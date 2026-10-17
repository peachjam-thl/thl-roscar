#!/usr/bin/env python3
"""Read-only file/dependency precheck. Does not connect to ROS or start Gazebo."""

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


LIBRARY = "/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so"
JOINT_TAGS = {
    "leftFrontJoint": "front_left_wheel_joint",
    "rightFrontJoint": "front_right_wheel_joint",
    "leftRearJoint": "rear_left_wheel_joint",
    "rightRearJoint": "rear_right_wheel_joint",
}
POSITIONS = {
    "front_left_wheel_joint": (0.20, 0.36, -0.10),
    "front_right_wheel_joint": (0.20, -0.36, -0.10),
    "rear_left_wheel_joint": (-0.20, 0.36, -0.10),
    "rear_right_wheel_joint": (-0.20, -0.36, -0.10),
}
STRINGS = dict(JOINT_TAGS, commandTopic="/cmd_vel", odometryTopic="/odom",
               odometryFrame="odom", robotBaseFrame="root_link", broadcastTF="true")
NUMBERS = {
    "wheelSeparation": 0.72, "wheelDiameter": 0.20, "torque": 5.0,
    "updateRate": 100.0, "covariance_x": 0.0001,
    "covariance_y": 0.0001, "covariance_yaw": 0.01,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(node):
    """Ignore formatting/comments, but compare all elements, attributes and text."""
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            (node.tail or "").strip(), tuple(canonical(child) for child in node))


def vector(text, expected, description):
    values = tuple(float(part) for part in text.split())
    require(len(values) == len(expected) and all(
        math.isfinite(a) and math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
        for a, b in zip(values, expected)), description)


def validate_model(base, driven):
    require(base.tag == driven.tag == "robot", "Both input files must be URDF robots.")
    require(not base.findall(".//plugin"), "Baseline must be the plugin-free step11A model.")
    plugins = driven.findall(".//plugin")
    require(len(plugins) == 1, "Driven model must contain exactly one plugin.")
    plugin = plugins[0]
    wrappers = [g for g in driven.findall("gazebo") if plugin in list(g)]
    require(len(wrappers) == 1 and not wrappers[0].attrib
            and len(wrappers[0]) == 1, "Drive plugin must have its own model-level gazebo wrapper.")
    physical = copy.deepcopy(driven)
    for wrapper in physical.findall("gazebo"):
        if wrapper.find("plugin") is not None:
            physical.remove(wrapper)
    require(canonical(physical) == canonical(base),
            "Physical model changed: expected only one added controller, no geometry/joint edits.")
    require(plugin.attrib == {"name": "lesson14_four_wheel_drive", "filename": LIBRARY},
            "Unexpected drive plugin name or library path.")
    tags = [child.tag for child in plugin]
    expected = set(STRINGS) | set(NUMBERS)
    require(len(tags) == len(expected) and set(tags) == expected,
            "Missing, duplicate or unsupported plugin tag (do not copy two-wheel plugin tags).")
    require(all(not child.attrib and len(child) == 0 for child in plugin),
            "Drive settings must be simple scalar elements.")
    for key, value in STRINGS.items():
        require((plugin.findtext(key) or "").strip() == value,
                "Incorrect controller setting: " + key)
    for key, value in NUMBERS.items():
        actual = float(plugin.findtext(key))
        require(math.isfinite(actual) and math.isclose(actual, value, rel_tol=1e-9),
                "Incorrect controller setting: " + key)

    links = {link.get("name"): link for link in base.findall("link")}
    joints = {joint.get("name"): joint for joint in base.findall("joint")}
    require(len(links) == len(base.findall("link")) == 10, "Expected 10 unique links.")
    require(len(joints) == len(base.findall("joint")) == 9, "Expected 9 unique joints.")
    moving = [j for j in joints.values() if j.get("type") != "fixed"]
    require(len(moving) == 6, "Expected four wheel and two sensor-mount moving joints.")
    for joint_name, xyz in POSITIONS.items():
        require(joint_name in joints, "Missing wheel joint: " + joint_name)
        joint = joints[joint_name]
        require(joint.get("type") == "continuous", "Wheel joint must be continuous.")
        require(joint.find("parent").get("link") == "base_link", "Wrong wheel parent.")
        wheel_link = joint_name.replace("_joint", "_link")
        require(joint.find("child").get("link") == wheel_link, "Wrong wheel child.")
        vector(joint.find("axis").get("xyz"), (0, 1, 0), "Wheel axis must be +Y.")
        vector(joint.find("origin").get("xyz"), xyz, "Wrong wheel center: " + joint_name)
        vector(joint.find("origin").get("rpy", "0 0 0"), (0, 0, 0), "Wrong wheel joint RPY.")
        effort = float(joint.find("limit").get("effort"))
        require(math.isfinite(effort) and effort >= NUMBERS["torque"], "Motor torque exceeds joint effort.")
        for kind in ("visual", "collision"):
            body = links[wheel_link].find(kind)
            cylinder = body.find("geometry/cylinder")
            require(cylinder is not None, "Wheel must have cylinder geometry.")
            vector(cylinder.get("radius"), (0.10,), "Wheel radius mismatch.")
            vector(cylinder.get("length"), (0.08,), "Wheel width mismatch.")
            vector(body.find("origin").get("rpy"), (math.pi / 2, 0, 0), "Wheel cylinder must align with Y.")

    return {
        "model_geometry_and_joints_unchanged": True,
        "links": len(links), "joints": len(joints), "moving_joints": len(moving),
        "drive_plugin_count": 1, "four_wheel_joint_mapping_ok": True,
        "wheel_joint_mapping": dict(JOINT_TAGS),
        "wheel_diameter_m": 0.20, "track_width_m": 0.72, "wheelbase_m": 0.40,
        "torque_per_wheel_nm": 5.0, "drive_update_rate_hz": 100.0,
        "odom_tf": "odom -> root_link", "command_topic": "/cmd_vel",
        "live_sensor_plugins": 0,
    }


def inspect_library(path, runner=subprocess.run):
    require(path.is_file(), "Compiled plugin not found: " + str(path))
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        header = stream.read(20)
        require(len(header) == 20 and header[:6] == b"\x7fELF\x02\x01",
                "Expected a 64-bit little-endian Linux ELF shared library.")
        require(int.from_bytes(header[16:18], "little") == 3
                and int.from_bytes(header[18:20], "little") == 62,
                "Expected an x86-64 ELF shared object.")
        digest.update(header)
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    result = runner(["ldd", str(path)], stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, timeout=25, check=False)
    output = result.stdout or ""
    require(result.returncode == 0 and output.strip(), "ldd failed:\n" + output)
    require(not re.search(r"\bnot found\b", output, re.IGNORECASE),
            "Unresolved dynamic dependency:\n" + output)
    old = r"lib(?:gazebo_ros_(?:diff_drive|skid_steer_drive)|rcdp_diff_drive_stampfix)\.so"
    require(not re.search(old, output), "Unexpected dependency on another drive plugin:\n" + output)
    return {"new_library": path.as_posix(), "plugin_sha256": digest.hexdigest(),
            "dynamic_dependencies_resolved": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_urdf", type=Path, help="Expanded plugin-free step11A URDF")
    parser.add_argument("driven_urdf", type=Path, help="Expanded step11C URDF")
    args = parser.parse_args()
    try:
        report = validate_model(ET.parse(args.base_urdf).getroot(),
                                ET.parse(args.driven_urdf).getroot())
        package = Path(__file__).resolve().parents[1]
        world = package / "worlds/lesson14_box_house_step7.world"
        require(world.is_file(), "Required existing world file not found: " + str(world))
        require(ET.parse(world).getroot().tag == "sdf", "World file is not SDF XML.")
        report.update(inspect_library(Path(LIBRARY)))
        report.update({"existing_world_file_found": True,
                       "gazebo_loaded_or_modified": False,
                       "four_wheel_motion_verified": False})
        print(json.dumps(report, indent=2, ensure_ascii=False))
        print("PRECHECK_OK: files/dependencies only; Gazebo has NOT been switched.")
    except (OSError, ValueError, TypeError, AttributeError, KeyError,
            ET.ParseError, subprocess.SubprocessError) as error:
        print("PRECHECK_FAILED: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
