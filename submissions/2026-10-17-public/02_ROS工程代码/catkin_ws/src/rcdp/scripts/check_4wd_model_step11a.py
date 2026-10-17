#!/usr/bin/env python3
"""Read-only static URDF checks. No ROS imports or runtime/motion claims."""

import argparse
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


WHEELS = {
    "front_left": (0.20, 0.36, -0.10),
    "front_right": (0.20, -0.36, -0.10),
    "rear_left": (-0.20, 0.36, -0.10),
    "rear_right": (-0.20, -0.36, -0.10),
}
KEEP_LINKS = {"root_link", "base_link", "support_link", "platform_link", "laser_scan_link", "depth_camera_link"}
KEEP_JOINTS = {"base_link2root_link", "support_link2base_link", "platform_link2support_link", "laser_scan_link2platform_link", "depth_camera_link2base_link"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vector(value):
    require(value is not None, "Missing vector.")
    result = tuple(float(part) for part in value.split())
    require(len(result) == 3 and all(math.isfinite(v) for v in result), "Invalid three-vector.")
    return result


def close(actual, expected):
    return math.isclose(actual, expected, abs_tol=1e-9, rel_tol=1e-9)


def same_vector(actual, expected):
    return all(close(a, b) for a, b in zip(actual, expected))


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            tuple(canonical(child) for child in node))


def validate(robot, old):
    require(robot.tag == old.tag == "robot", "Inputs must be expanded URDF robot files.")
    require(robot.get("name") == old.get("name") == "lesson13_robot", "Unexpected robot name.")
    links = {node.get("name"): node for node in robot.findall("link")}
    joints = {node.get("name"): node for node in robot.findall("joint")}
    require(len(links) == len(robot.findall("link")) == 10, "Expected ten unique links.")
    require(len(joints) == len(robot.findall("joint")) == 9, "Expected nine unique joints.")
    require(len(robot.findall(".//plugin")) == 0, "Stage11A must not load a controller/sensor plugin.")
    wheel_links = {name + "_wheel_link" for name in WHEELS}
    wheel_joints = {name + "_wheel_joint" for name in WHEELS}
    require(set(links) == KEEP_LINKS | wheel_links, "Unexpected/missing links or old support wheels remain.")
    require(set(joints) == KEEP_JOINTS | wheel_joints, "Unexpected/missing joints or old drive joints remain.")

    parents = {}
    for name, joint in joints.items():
        parent, child = joint.find("parent"), joint.find("child")
        require(parent is not None and child is not None, "Missing joint endpoint: " + name)
        p, c = parent.get("link"), child.get("link")
        require(p in links and c in links and p != c and c not in parents,
                "Invalid/repeated joint endpoint: " + name)
        parents[c] = p
    require(set(links) - set(parents) == {"root_link"}, "Expected one root_link tree.")
    for name in links:
        seen, current = set(), name
        while current in parents:
            require(current not in seen, "Cycle in URDF tree.")
            seen.add(current)
            current = parents[current]
        require(current == "root_link", "Disconnected link: " + name)

    old_links = {node.get("name"): node for node in old.findall("link")}
    old_joints = {node.get("name"): node for node in old.findall("joint")}
    for name in KEEP_LINKS:
        require(name in old_links and canonical(links[name]) == canonical(old_links[name]),
                "Non-wheel link changed: " + name)
    for name in KEEP_JOINTS:
        require(name in old_joints and canonical(joints[name]) == canonical(old_joints[name]),
                "Non-wheel joint changed: " + name)

    total_mass = 0.0
    for name, link in links.items():
        if name == "root_link":
            require(link.find("inertial") is None, "root_link must remain a massless reference.")
            continue
        inertia = link.find("inertial/inertia")
        mass = link.find("inertial/mass")
        require(inertia is not None and mass is not None, "Missing inertia/mass: " + name)
        m = float(mass.get("value"))
        require(math.isfinite(m) and m > 0, "Invalid mass: " + name)
        total_mass += m
        xx, yy, zz, xy, xz, yz = (float(inertia.get(k)) for k in ("ixx", "iyy", "izz", "ixy", "ixz", "iyz"))
        determinant = xx * yy * zz + 2 * xy * xz * yz - xx * yz * yz - yy * xz * xz - zz * xy * xy
        require(all(math.isfinite(v) for v in (xx, yy, zz, xy, xz, yz))
                and xx > 0 and xx * yy - xy * xy > 0 and determinant > 0,
                "Inertia is not symmetric-positive-definite: " + name)

    base_z = vector(joints["base_link2root_link"].find("origin").get("xyz"))[2]
    bottoms = {}
    for name, expected in WHEELS.items():
        joint, link = joints[name + "_wheel_joint"], links[name + "_wheel_link"]
        require(joint.get("type") == "continuous", "Wheel must rotate continuously: " + name)
        require(joint.find("parent").get("link") == "base_link", "Wheel not attached to base: " + name)
        require(joint.find("child").get("link") == name + "_wheel_link", "Wheel child mismatch: " + name)
        require(same_vector(vector(joint.find("origin").get("xyz")), expected), "Wheel position mismatch: " + name)
        require(same_vector(vector(joint.find("origin").get("rpy")), (0, 0, 0)), "Wheel joint orientation mismatch.")
        require(same_vector(vector(joint.find("axis").get("xyz")), (0, 1, 0)), "Wheel joint axis mismatch: " + name)
        limit = joint.find("limit")
        require(limit is not None and float(limit.get("effort")) > 0 and float(limit.get("velocity")) > 0,
                "Wheel limits must be positive: " + name)
        for kind in ("visual", "collision"):
            cylinder = link.find(kind + "/geometry/cylinder")
            require(cylinder is not None and close(float(cylinder.get("radius")), 0.1)
                    and close(float(cylinder.get("length")), 0.08), "Wheel geometry mismatch: " + name)
            require(same_vector(vector(link.find(kind + "/origin").get("rpy")), (math.pi / 2, 0, 0)),
                    "Wheel cylinder axis must align with Y: " + name)
        wheel_inertia = link.find("inertial/inertia")
        require(close(float(link.find("inertial/mass").get("value")), 0.3), "Unexpected assumed wheel mass.")
        expected_inertia = {"ixx": 0.3 * (3 * 0.1**2 + 0.08**2) / 12,
                            "iyy": 0.3 * 0.1**2 / 2,
                            "izz": 0.3 * (3 * 0.1**2 + 0.08**2) / 12,
                            "ixy": 0.0, "ixz": 0.0, "iyz": 0.0}
        require(all(close(float(wheel_inertia.get(key)), value) for key, value in expected_inertia.items()),
                "Wheel Y-axis inertia mismatch: " + name)
        bottom = base_z + expected[2] - 0.1
        require(close(bottom, 0.0), "Nominal wheel contact height mismatch: " + name)
        bottoms[name] = round(bottom, 9)

    return {
        "model_only": True,
        "links": len(links), "joints": len(joints),
        "wheel_joints_prepared": len(wheel_joints),
        "old_support_wheels_remaining": 0,
        "plugins": 0,
        "wheel_diameter_m": 0.2,
        "wheelbase_m": 0.4,
        "track_width_m": 0.72,
        "nominal_wheel_bottom_z_m": bottoms,
        "nonwheel_links_and_joints_unchanged": True,
        "basic_inertia_checks_passed": True,
        "assumed_total_mass_kg": round(total_mass, 6),
        "gazebo_loaded_or_modified": False,
        "four_wheel_motion_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("new_urdf", type=Path)
    parser.add_argument("old_base_urdf", type=Path)
    args = parser.parse_args()
    try:
        result = validate(ET.parse(str(args.new_urdf)).getroot(), ET.parse(str(args.old_base_urdf)).getroot())
        print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
        print("MODEL_PRECHECK_OK: static four-wheel model only; no simulation/control changes.", flush=True)
        return 0
    except (OSError, ET.ParseError, ValueError, TypeError, AttributeError) as error:
        print("MODEL_PRECHECK_FAILED: " + str(error), file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
