#!/usr/bin/env python3
"""Read-only step11I file/dependency precheck; no ROS calls or scene changes."""

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


MODEL = "urdf/gazebo/myrobot_4wd_laser_step11i.xacro"
LAUNCH = "launch/myrobot_4wd_laser_step11i.launch"
LASER_LIBRARY = Path("/opt/ros/noetic/lib/libgazebo_ros_laser.so")
DRIVE_LIBRARY = Path("/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so")
LAST_DRIVE_SHA = "1265cba90fa07463d7f8af80decdf33bbf47a916a113fe7fdb51599699a9424c"
PRESERVED_HASHES = {
    "urdf/gazebo/myrobot_4wd_base_step11a.xacro":
        "6f949506ac146fd7f8b0657e44bab30eed4f80fc87c58283e25c4075001fb106",
    "urdf/gazebo/myrobot_4wd_drive_step11c.xacro":
        "2e3b940f4a95b3a174723afac4796b9f4aadffc990cd00cb2ed4b5029bc863ae",
    "urdf/gazebo/myrobot_4wd_tf_step11h.xacro":
        "31ec875b4d28532280dc3ba73bd80fd06639e9e460b070924a6f4ea16b4ab3e5",
    "launch/myrobot_4wd_tf_step11h.launch":
        "24db1147aafba50058d7352a82dbccabb7fdd43e1789fcf94d10dfd14e94d8c4",
    "worlds/lesson14_4wd_cone_model_step11f.world":
        "2daf5b3e22a547d6cbc005db65038d8fd5421fb3f4a1235084b06e0519892172",
}
# Exact sensor structure from the previously used step7 include. No new tuning.
SENSOR_XML = """<gazebo reference="laser_scan_link">
  <sensor type="ray" name="lesson14_rplidar">
    <pose>0 0 0 0 0 0</pose><always_on>true</always_on><visualize>true</visualize>
    <update_rate>5.5</update_rate>
    <ray><scan><horizontal><samples>360</samples><resolution>1</resolution>
      <min_angle>-3</min_angle><max_angle>3</max_angle></horizontal></scan>
      <range><min>0.10</min><max>30.0</max><resolution>0.01</resolution></range>
      <noise><type>gaussian</type><mean>0.0</mean><stddev>0.01</stddev></noise>
    </ray>
    <plugin name="lesson14_laser_ros" filename="libgazebo_ros_laser.so">
      <robotNamespace>/</robotNamespace><topicName>/scan</topicName><frameName>laser_scan_link</frameName>
    </plugin>
  </sensor>
</gazebo>"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            (node.tail or "").strip(), tuple(canonical(child) for child in node))


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def validate_models(baseline, scanned):
    require(baseline.tag == scanned.tag == "robot", "Expected expanded URDF robots.")
    require(not baseline.findall(".//sensor"), "Baseline step11H must not contain live sensors.")
    old_plugins = baseline.findall(".//plugin")
    require(len(old_plugins) == 2 and {p.get("name") for p in old_plugins} == {
        "lesson14_four_wheel_drive", "lesson14_four_wheel_joint_states"},
        "Baseline must contain the accepted drive and measured-joint plugin only.")
    require(len(scanned.findall(".//plugin")) == 3 and len(scanned.findall(".//sensor")) == 1,
            "Expected exactly three plugins and one laser sensor, no camera/second controller.")
    stripped = copy.deepcopy(scanned)
    sensor_wrappers = [g for g in stripped.findall("gazebo") if g.find("sensor") is not None]
    require(len(sensor_wrappers) == 1, "Expected one link-level lidar wrapper.")
    require(canonical(sensor_wrappers[0]) == canonical(ET.fromstring(SENSOR_XML)),
            "Lidar configuration differs from the previously validated step7 sensor.")
    stripped.remove(sensor_wrappers[0])
    require(canonical(stripped) == canonical(baseline),
            "Model changed outside the added lidar: geometry, drive or joint-state settings changed.")
    links, joints = scanned.findall("link"), scanned.findall("joint")
    require(len(links) == len({p.get("name") for p in links}) == 10
            and len(joints) == len({p.get("name") for p in joints}) == 9,
            "Expected unchanged 10-link/9-joint model.")
    moving = [joint for joint in joints if joint.get("type") != "fixed"]
    require(len(moving) == 6, "Expected six existing moving joints.")
    require(any(link.get("name") == "laser_scan_link" for link in links), "Laser link missing.")
    return {"geometry_drive_and_joint_state_configuration_unchanged": True,
            "links": len(links), "joints": len(joints), "moving_joints": len(moving),
            "drive_plugin_count": 1, "joint_state_plugin_count": 1, "laser_plugin_count": 1,
            "depth_camera_plugins": 0, "laser_topic": "/scan", "laser_frame": "laser_scan_link",
            "laser_samples": 360, "laser_angle_limits_rad": [-3.0, 3.0],
            "laser_range_limits_m": [0.1, 30.0], "configured_laser_update_rate_sim_hz": 5.5,
            "sensor_parameters_match_previous_step7": True}


def validate_launch(old, new):
    require(old.tag == new.tag == "launch", "Expected ROS1 launch XML.")
    result = copy.deepcopy(new)
    loaders = result.findall("param[@name='robot_description']")
    require(len(loaders) == 1 and loaders[0].get("command") ==
            "$(find xacro)/xacro '$(find rcdp)/" + MODEL + "'", "Unexpected new Xacro loader.")
    loaders[0].set("command", old.find("param[@name='robot_description']").get("command"))
    spawn = result.findall("node[@pkg='gazebo_ros']")
    require(len(spawn) == 1 and spawn[0].get("name") == "spawn_four_wheel_laser_step11i",
            "Unexpected spawn node.")
    spawn[0].set("name", "spawn_four_wheel_tf_step11h")
    require(canonical(result) == canonical(old),
            "Launch changed outside robot description and spawn node name.")
    require(len(new.findall(".//node")) == 2
            and new.find("arg[@name='friction_model']").get("default") == "cone_model",
            "Expected one spawn, one existing RSP and B/cone default; no RViz or extra node.")
    return {"spawn_world_physics_and_rsp_launch_preserved": True,
            "default_friction_model": "cone_model", "rviz_started_by_launch": False}


def inspect_files(package, drive=DRIVE_LIBRARY, laser=LASER_LIBRARY, runner=subprocess.run):
    source_hashes = {}
    for relative, expected in PRESERVED_HASHES.items():
        source_hashes[relative] = digest(package / relative)
        require(source_hashes[relative] == expected, "Preserved file hash changed: " + relative)
    sensor_source = package / "urdf/gazebo/gazebo_sensor/lesson14_laser_step7.xacro"
    sensor = ET.parse(sensor_source).getroot()
    require(len(sensor) == 1 and canonical(sensor[0]) == canonical(ET.fromstring(SENSOR_XML)),
            "Existing step7 sensor include changed; send the output before switching.")
    for path in (drive, laser):
        with path.open("rb") as stream:
            header = stream.read(20)
        require(len(header) == 20 and header[:6] == b"\x7fELF\x02\x01"
                and int.from_bytes(header[16:18], "little") == 3
                and int.from_bytes(header[18:20], "little") == 62,
                "Expected an existing x86-64 Linux ELF library: " + str(path))
    result = runner(["ldd", str(laser)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, timeout=25, check=False)
    require(result.returncode == 0 and (result.stdout or "").strip(), "Laser library ldd failed.")
    require(not re.search(r"\bnot found\b", result.stdout, re.IGNORECASE),
            "Unresolved laser library dependency:\n" + result.stdout)
    drive_sha = digest(drive)
    return {"preserved_sources_sha256": source_hashes,
            "step7_sensor_include_sha256": digest(sensor_source),
            "existing_drive_library_sha256": drive_sha,
            "drive_library_matches_last_user_report": drive_sha == LAST_DRIVE_SHA,
            "laser_library_found": True, "laser_library_dependencies_resolved": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_urdf", type=Path, help="Expanded accepted step11H URDF")
    parser.add_argument("laser_urdf", type=Path, help="Expanded new step11I URDF")
    args = parser.parse_args()
    try:
        package = Path(__file__).resolve().parents[1]
        report = validate_models(ET.parse(args.baseline_urdf).getroot(), ET.parse(args.laser_urdf).getroot())
        report.update(validate_launch(ET.parse(package / "launch/myrobot_4wd_tf_step11h.launch").getroot(),
                                      ET.parse(package / LAUNCH).getroot()))
        report.update(inspect_files(package))
        report.update({"gazebo_started_stopped_or_modified": False,
                       "native_gazebo_sensor_loading_verified": False,
                       "four_wheel_laser_data_and_loaded_tf_stability_verified": False})
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if not report["drive_library_matches_last_user_report"]:
            print("PRECHECK_REVIEW: drive hash differs; send output before switching Gazebo.")
            return 2
        print("PRECHECK_OK: lidar files/dependencies only; current Gazebo is unchanged. Do NOT switch yet.")
        return 0
    except (OSError, ValueError, TypeError, AttributeError, KeyError, ET.ParseError,
            subprocess.SubprocessError) as error:
        print("PRECHECK_FAILED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
