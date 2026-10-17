#!/usr/bin/env python3
"""Read-only expanded-URDF, launch and dependency checks; no ROS connections."""

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


DRIVE_LIBRARY = Path("/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so")
JSP_LIBRARY = Path("/opt/ros/noetic/lib/libgazebo_ros_joint_state_publisher.so")
RSP_EXECUTABLE = Path("/opt/ros/noetic/lib/robot_state_publisher/robot_state_publisher")
LAST_DRIVE_SHA = "1265cba90fa07463d7f8af80decdf33bbf47a916a113fe7fdb51599699a9424c"
SOURCE_HASHES = {
    "urdf/gazebo/myrobot_4wd_base_step11a.xacro":
        "6f949506ac146fd7f8b0657e44bab30eed4f80fc87c58283e25c4075001fb106",
    "urdf/gazebo/myrobot_4wd_drive_step11c.xacro":
        "2e3b940f4a95b3a174723afac4796b9f4aadffc990cd00cb2ed4b5029bc863ae",
    "worlds/lesson14_4wd_cone_model_step11f.world":
        "2daf5b3e22a547d6cbc005db65038d8fd5421fb3f4a1235084b06e0519892172",
}
JOINTS = (
    "front_left_wheel_joint", "front_right_wheel_joint",
    "rear_left_wheel_joint", "rear_right_wheel_joint",
    "depth_camera_link2base_link", "laser_scan_link2platform_link",
)
MODEL = "urdf/gazebo/myrobot_4wd_tf_step11h.xacro"
LAUNCH = "launch/myrobot_4wd_tf_step11h.launch"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            (node.tail or "").strip(), tuple(canonical(c) for c in node))


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def validate_models(baseline, measured):
    require(baseline.tag == measured.tag == "robot", "Expected two expanded URDF robots.")
    old_plugins = baseline.findall(".//plugin")
    require(len(old_plugins) == 1, "Baseline must have exactly one drive plugin.")
    drive = old_plugins[0]
    require(drive.attrib == {"name": "lesson14_four_wheel_drive", "filename": DRIVE_LIBRARY.as_posix()},
            "Unexpected baseline drive library/name.")
    require((drive.findtext("broadcastTF") or "").strip() == "true"
            and (drive.findtext("robotBaseFrame") or "").strip() == "root_link"
            and (drive.findtext("odometryFrame") or "").strip() == "odom",
            "Baseline must retain drive-owned odom -> root_link TF.")
    require(len(measured.findall(".//plugin")) == 2, "Expected exactly one drive and one joint-state plugin.")
    candidates = measured.findall(".//plugin[@name='lesson14_four_wheel_joint_states']")
    require(len(candidates) == 1, "Expected one uniquely named joint-state plugin.")
    jsp = candidates[0]
    require(jsp.attrib == {"name": "lesson14_four_wheel_joint_states",
                           "filename": JSP_LIBRARY.name}, "Wrong joint-state plugin library/name.")
    tags = [c.tag for c in jsp]
    require(len(tags) == 3 and set(tags) == {"robotNamespace", "updateRate", "jointName"}
            and all(not c.attrib and len(c) == 0 for c in jsp),
            "Unexpected, duplicate or unsupported joint-state plugin settings.")
    require((jsp.findtext("robotNamespace") or "").strip() == "/",
            "Joint states must resolve to global /joint_states, not the model namespace.")
    rate = float(jsp.findtext("updateRate"))
    require(math.isfinite(rate) and rate == 50.0, "Expected joint-state updateRate=50.")
    names = tuple(n.strip() for n in (jsp.findtext("jointName") or "").split(","))
    require(len(names) == len(set(names)) == 6 and set(names) == set(JOINTS),
            "Joint list must contain all four new wheels and the two sensor joints exactly once.")
    joints = measured.findall("joint")
    links = measured.findall("link")
    require(len(joints) == len({j.get("name") for j in joints}) == 9
            and len(links) == len({l.get("name") for l in links}) == 10,
            "Expected the unchanged 10-link, 9-joint physical model.")
    moving = {j.get("name") for j in joints if j.get("type") != "fixed"}
    require(moving == set(names), "Published joint names do not match actual moving URDF joints.")
    require(not any(j.find("child").get("link") == "root_link" for j in joints),
            "root_link must remain the URDF root, not have an added parent joint.")
    stripped = copy.deepcopy(measured)
    wrappers = [g for g in stripped.findall("gazebo")
                if g.find("plugin[@name='lesson14_four_wheel_joint_states']") is not None]
    require(len(wrappers) == 1 and not wrappers[0].attrib and len(wrappers[0]) == 1,
            "Added joint-state plugin must be in its own model-level gazebo wrapper.")
    stripped.remove(wrappers[0])
    require(canonical(stripped) == canonical(baseline),
            "Robot changed outside the one added joint-state plugin.")
    return {"robot_geometry_joints_and_drive_unchanged": True,
            "links": len(links), "joints": len(joints), "moving_joints": len(moving),
            "drive_plugin_count": 1, "joint_state_plugin_count": 1,
            "measured_joint_names": list(names), "joint_state_rate_hz": rate,
            "joint_state_topic": "/joint_states", "root_tf_owner": "existing four-wheel drive",
            "root_tf": "odom -> root_link", "live_sensor_plugins": 0}


def validate_launch(old, new):
    require(old.tag == new.tag == "launch", "Expected ROS1 launch XML.")
    normalized = copy.deepcopy(new)
    rsps = normalized.findall("node[@pkg='robot_state_publisher']")
    require(len(rsps) == 1 and len(normalized.findall(".//node")) == 2,
            "Only one spawn node and one robot_state_publisher may be added; no RViz/fake states.")
    rsp = rsps[0]
    require(rsp.attrib == {"pkg": "robot_state_publisher", "type": "robot_state_publisher",
                          "name": "lesson14_4wd_robot_state_publisher", "output": "screen"},
            "Unexpected robot_state_publisher configuration.")
    expected = {"publish_frequency": "50.0", "listener_queue_size": "100", "use_tf_static": "true"}
    require(len(rsp) == 3 and all(p.tag == "param" and p.attrib == {
        "name": p.get("name"), "value": expected.get(p.get("name"))} for p in rsp)
        and {p.get("name") for p in rsp} == set(expected), "Unexpected RSP parameters.")
    normalized.remove(rsp)
    mode = normalized.findall("arg[@name='friction_model']")
    require(len(mode) == 1 and mode[0].attrib == {"name": "friction_model", "default": "cone_model"},
            "New launch must continue the tested B/cone world by default.")
    mode[0].set("default", "pyramid_model")
    loaders = normalized.findall("param[@name='robot_description']")
    require(len(loaders) == 1 and loaders[0].get("command") ==
            "$(find xacro)/xacro '$(find rcdp)/" + MODEL + "'", "Wrong new Xacro loader.")
    loaders[0].set("command", old.find("param[@name='robot_description']").get("command"))
    spawns = normalized.findall("node")
    require(len(spawns) == 1 and spawns[0].get("name") == "spawn_four_wheel_tf_step11h",
            "Wrong spawn node.")
    spawns[0].set("name", "spawn_four_wheel_friction_step11f")
    require(canonical(normalized) == canonical(old),
            "Launch changed outside the description, new RSP, spawn node name and B default.")
    return {"spawn_pose_and_gazebo_settings_unchanged": True,
            "default_friction_model": "cone_model", "robot_state_publisher_nodes": 1,
            "fake_joint_state_publisher_nodes": 0, "rviz_started_by_launch": False}


def inspect_dependencies(drive=DRIVE_LIBRARY, jsp=JSP_LIBRARY, rsp=RSP_EXECUTABLE,
                         runner=subprocess.run):
    for path in (drive, jsp):
        require(path.is_file(), "Required library missing: " + str(path))
        with path.open("rb") as stream:
            header = stream.read(20)
        require(len(header) == 20 and header[:6] == b"\x7fELF\x02\x01"
                and int.from_bytes(header[16:18], "little") == 3
                and int.from_bytes(header[18:20], "little") == 62,
                "Expected an x86-64 Linux ELF shared library: " + str(path))
    require(rsp.is_file(), "robot_state_publisher executable missing: " + str(rsp))
    result = runner(["ldd", str(jsp)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, timeout=25, check=False)
    require(result.returncode == 0 and (result.stdout or "").strip(), "Joint-state library ldd failed.")
    require(not re.search(r"\bnot found\b", result.stdout, re.IGNORECASE),
            "Joint-state library has unresolved dependencies:\n" + result.stdout)
    actual = digest(drive)
    return {"existing_drive_library_sha256": actual,
            "drive_library_matches_last_user_report": actual == LAST_DRIVE_SHA,
            "gazebo_joint_state_library_found": True, "joint_state_library_dependencies_resolved": True,
            "robot_state_publisher_executable_found": True}


def inspect_preserved_files(package):
    actual = {}
    for relative, expected in SOURCE_HASHES.items():
        path = package / relative
        require(path.is_file(), "Required existing file missing: " + str(path))
        actual[relative] = digest(path)
        require(actual[relative] == expected, "Existing baseline file hash changed: " + relative)
    return {"existing_base_drive_and_cone_world_sha256": actual,
            "existing_base_drive_and_cone_world_match_prior_checkpoint": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_urdf", type=Path, help="Expanded existing step11C URDF")
    parser.add_argument("measured_urdf", type=Path, help="Expanded new step11H URDF")
    args = parser.parse_args()
    try:
        package = Path(__file__).resolve().parents[1]
        report = validate_models(ET.parse(args.baseline_urdf).getroot(), ET.parse(args.measured_urdf).getroot())
        report.update(validate_launch(ET.parse(package / "launch/myrobot_4wd_friction_step11f.launch").getroot(),
                                      ET.parse(package / LAUNCH).getroot()))
        report.update(inspect_preserved_files(package))
        report.update(inspect_dependencies())
        report.update({"check_is_read_only": True, "gazebo_started_stopped_or_modified": False,
                       "native_gazebo_plugin_loading_verified": False,
                       "runtime_joint_states_and_link_tf_verified": False,
                       "timestamp_regression_with_joint_states_verified": False})
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if not report["drive_library_matches_last_user_report"]:
            print("PRECHECK_REVIEW: drive library hash changed; send the output before switching Gazebo.")
            return 2
        print("PRECHECK_OK: files/dependencies only; current Gazebo is unchanged. Do NOT switch yet.")
        return 0
    except (OSError, ValueError, TypeError, AttributeError, KeyError,
            ET.ParseError, subprocess.SubprocessError) as error:
        print("PRECHECK_FAILED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
