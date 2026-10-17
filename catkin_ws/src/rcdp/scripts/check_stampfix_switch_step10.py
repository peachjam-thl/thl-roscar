#!/usr/bin/env python3
"""Read-only file/dependency precheck. Never contacts ROS or starts a simulator."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


LIBRARY = Path("/home/thl/catkin_ws/devel/lib/librcdp_diff_drive_stampfix.so")
ORIGINAL_LIBRARY = "libgazebo_ros_diff_drive.so"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(node):
    return (
        node.tag,
        tuple(sorted(node.attrib.items())),
        (node.text or "").strip(),
        tuple(canonical(child) for child in node),
    )


def compare_models(old, new):
    """Allow exactly one filename change; reject all other expanded XML changes."""
    require(old.tag == new.tag == "robot", "Both input files must be expanded URDF robots.")
    old_plugins = old.findall(".//plugin")
    new_plugins = new.findall(".//plugin")
    old_drives = [p for p in old_plugins if p.get("filename") == ORIGINAL_LIBRARY]
    new_drives = [p for p in new_plugins if p.get("filename") == LIBRARY.as_posix()]
    require(len(old_drives) == 1, "Baseline must contain exactly one original diff-drive plugin.")
    require(len(new_drives) == 1, "New URDF must contain exactly one stampfix plugin at the expected path.")
    require(len(old_plugins) == len(new_plugins) == 4, "Expected four plugins in each stage-9/10 robot.")
    require(not any(p.get("filename") == ORIGINAL_LIBRARY for p in new_plugins),
            "New model still contains the original diff-drive plugin.")

    normalized = copy.deepcopy(new)
    normalized_drive = next(p for p in normalized.findall(".//plugin")
                            if p.get("filename") == LIBRARY.as_posix())
    normalized_drive.set("filename", ORIGINAL_LIBRARY)
    require(canonical(old) == canonical(normalized),
            "Expanded models differ beyond the drive library filename. Do not switch.")

    require(len(new.findall("link")) == 11, "Expected eleven links.")
    require(len(new.findall("joint")) == 10, "Expected ten joints.")
    moving = [j for j in new.findall("joint") if j.get("type") != "fixed"]
    require(len(moving) == 6, "Expected six moving joints.")
    expected = {
        "updateRate": "100",
        "leftJoint": "base_l_wheel_joint",
        "rightJoint": "base_r_wheel_joint",
        "wheelSeparation": "0.8",
        "wheelDiameter": "0.2",
        "wheelAcceleration": "0.3",
        "wheelTorque": "5.0",
        "commandTopic": "/cmd_vel",
        "odometryTopic": "/odom",
        "odometryFrame": "odom",
        "robotBaseFrame": "root_link",
        "odometrySource": "world",
        "publishTf": "true",
        "publishOdomTF": "true",
        "publishWheelTF": "false",
        "publishWheelJointState": "true",
    }
    drive = new_drives[0]
    for key, value in expected.items():
        require(drive.findtext(key) == value,
                "Unexpected drive setting: " + key + "=" + str(drive.findtext(key)))
    return {
        "urdf_equal_except_drive_library": True,
        "links": len(new.findall("link")),
        "joints": len(new.findall("joint")),
        "moving_joints": len(moving),
        "plugins": len(new_plugins),
        "diff_drive_plugin_count": len(new_drives),
        "drive_update_rate_hz": drive.findtext("updateRate"),
        "odom_tf": drive.findtext("odometryFrame") + " -> " + drive.findtext("robotBaseFrame"),
        "new_library": drive.get("filename"),
    }


def check_dependencies(ldd_output, returncode):
    require(returncode == 0, "ldd failed: " + ldd_output[:1200])
    missing = [line.strip() for line in ldd_output.splitlines()
               if re.search(r"\bnot found\b", line, re.I)]
    require(not missing, "Missing dependencies: " + "; ".join(missing))
    require("libgazebo_ros_utils.so" in ldd_output,
            "Expected installed libgazebo_ros_utils.so dependency is absent.")
    require(ORIGINAL_LIBRARY not in ldd_output,
            "New library unexpectedly depends on the original diff-drive library.")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old_urdf", type=Path)
    parser.add_argument("new_urdf", type=Path)
    args = parser.parse_args()
    try:
        result = compare_models(
            ET.parse(str(args.old_urdf)).getroot(),
            ET.parse(str(args.new_urdf)).getroot(),
        )
        require(LIBRARY.is_file(), "Compiled plugin file is missing: " + LIBRARY.as_posix())
        with LIBRARY.open("rb") as stream:
            require(stream.read(4) == b"\x7fELF", "The plugin is not an ELF file.")
        completed = subprocess.run(
            ["ldd", LIBRARY.as_posix()], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=25, check=False,
        )
        result["dynamic_dependencies_resolved"] = check_dependencies(
            completed.stdout + completed.stderr, completed.returncode
        )
        result["plugin_sha256"] = hashlib.sha256(LIBRARY.read_bytes()).hexdigest()
        result["gazebo_started_or_modified"] = False
        result["runtime_fix_verified"] = False
        print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
        print("PRECHECK_OK: files/dependencies only; Gazebo has NOT been switched.", flush=True)
        return 0
    except (OSError, ET.ParseError, ValueError, subprocess.TimeoutExpired) as error:
        print("PRECHECK_FAILED: " + str(error), file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
