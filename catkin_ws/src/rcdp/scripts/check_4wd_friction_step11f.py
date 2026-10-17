#!/usr/bin/env python3
"""Read-only file precheck for a friction-model A/B experiment. No ROS calls."""

import copy
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


WORLD_FILES = {
    "pyramid_model": "worlds/lesson14_4wd_pyramid_model_step11f.world",
    "cone_model": "worlds/lesson14_4wd_cone_model_step11f.world",
}
WORLD_PATTERN = "$(find rcdp)/worlds/lesson14_4wd_$(arg friction_model)_step11f.world"
LIBRARY = Path("/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so")
LAST_REPORTED_LIBRARY_SHA256 = "1265cba90fa07463d7f8af80decdf33bbf47a916a113fe7fdb51599699a9424c"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or "").strip(),
            (node.tail or "").strip(), tuple(canonical(c) for c in node))


def strip_friction_mode(root, expected):
    """Only remove the one scalar setting and its otherwise-empty wrappers."""
    result = copy.deepcopy(root)
    require(result.tag == "sdf" and len(result.findall("world")) == 1,
            "Expected one SDF world.")
    world = result.find("world")
    require(len(world.findall("physics")) == 1, "Expected one global physics element.")
    physics = world.find("physics")
    require(physics.get("type") == "ode", "Expected ODE physics.")
    require(len(physics.findall("ode")) == 1, "Expected one global ODE configuration.")
    ode = physics.find("ode")
    require(len(ode.findall("solver")) == 1, "Expected one global solver configuration.")
    solver = ode.find("solver")
    settings = result.findall(".//friction_model")
    require(len(settings) == 1 and settings[0] in list(solver),
            "Expected exactly one friction_model under physics/ode/solver.")
    setting = settings[0]
    require(not setting.attrib and len(setting) == 0
            and (setting.text or "").strip() == expected,
            "Unexpected friction model; expected " + expected)
    solver.remove(setting)
    if len(solver) == 0 and not solver.attrib and not (solver.text or "").strip():
        ode.remove(solver)
    if len(ode) == 0 and not ode.attrib and not (ode.text or "").strip():
        physics.remove(ode)
    return result


def validate_worlds(original, pyramid, cone):
    require(not original.findall(".//friction_model"),
            "Original world now has an explicit friction model; re-evaluate the baseline.")
    for mode, trial in (("pyramid_model", pyramid), ("cone_model", cone)):
        stripped = strip_friction_mode(trial, mode)
        require(canonical(stripped) == canonical(original),
                mode + ": world changed outside the friction-model setting.")
    return {
        "control_world_friction_model": "pyramid_model",
        "trial_world_friction_model": "cone_model",
        "worlds_equal_except_one_friction_model_setting": True,
        "original_world_geometry_and_surfaces_preserved": True,
        "step_size_update_rate_and_iteration_settings_preserved": True,
        "explicitly_changed_global_physics_fields": ["ode/solver/friction_model"],
    }


def validate_launch(original, trial):
    require(original.tag == trial.tag == "launch", "Expected ROS1 launch XML.")
    result = copy.deepcopy(trial)
    arg = result.findall("arg[@name='friction_model']")
    require(len(arg) == 1 and arg[0].attrib == {"name": "friction_model", "default": "pyramid_model"},
            "Launch must default to the explicit pyramid control world.")
    result.remove(arg[0])
    world_args = result.findall("include/arg[@name='world_name']")
    require(len(world_args) == 1 and world_args[0].get("value") == WORLD_PATTERN,
            "Unexpected A/B world routing.")
    old_world = original.find("include/arg[@name='world_name']")
    require(old_world is not None, "Original step11C launch world argument missing.")
    world_args[0].set("value", old_world.get("value"))
    nodes, old_nodes = result.findall("node"), original.findall("node")
    require(len(nodes) == len(old_nodes) == 1, "Only the original spawn node is allowed.")
    require(nodes[0].get("name") == "spawn_four_wheel_friction_step11f", "Unexpected spawn node.")
    nodes[0].set("name", old_nodes[0].get("name"))
    require(canonical(result) == canonical(original),
            "Launch changed robot loading, spawn pose, arguments or Gazebo settings.")
    return {"robot_loader_and_spawn_pose_unchanged": True,
            "extra_robot_or_sensor_plugins_added": False}


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def precheck(package, library=LIBRARY):
    original = package / "worlds/lesson14_box_house_step7.world"
    a, b = (package / WORLD_FILES[mode] for mode in ("pyramid_model", "cone_model"))
    report = validate_worlds(ET.parse(original).getroot(), ET.parse(a).getroot(), ET.parse(b).getroot())
    report.update(validate_launch(
        ET.parse(package / "launch/myrobot_4wd_drive_step11c.launch").getroot(),
        ET.parse(package / "launch/myrobot_4wd_friction_step11f.launch").getroot()))
    model_files = [package / "urdf/gazebo/myrobot_4wd_base_step11a.xacro",
                   package / "urdf/gazebo/myrobot_4wd_drive_step11c.xacro"]
    for path in model_files:
        require(path.is_file(), "Existing robot Xacro not found: " + str(path))
        ET.parse(path)
    require(library.is_file(), "Existing compiled drive library not found: " + str(library))
    with library.open("rb") as stream:
        require(stream.read(4) == b"\x7fELF", "Expected an existing Linux ELF drive library.")
    library_sha = digest(library)
    report.update({
        "original_world_sha256": digest(original),
        "world_sha256": {mode: digest(package / name) for mode, name in WORLD_FILES.items()},
        "existing_robot_sources_sha256": {path.name: digest(path) for path in model_files},
        "existing_drive_library": library.as_posix(), "existing_drive_library_sha256": library_sha,
        "drive_library_matches_last_user_report": library_sha == LAST_REPORTED_LIBRARY_SHA256,
        "robot_source_or_binary_modified_by_this_check": False,
        "gazebo_started_stopped_or_modified": False,
        "native_gazebo_sdf_parser_or_runtime_verified": False,
        "lateral_drift_cause_confirmed": False, "cone_model_improvement_verified": False,
    })
    return report


def main():
    try:
        package = Path(__file__).resolve().parents[1]
        report = precheck(package)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if not report["drive_library_matches_last_user_report"]:
            print("PRECHECK_REVIEW: drive-library hash differs; report this before switching Gazebo.")
            return 2
        print("PRECHECK_OK: A/B files only; current Gazebo is unchanged. Do NOT switch worlds yet.")
        return 0
    except (OSError, ValueError, TypeError, AttributeError, ET.ParseError) as error:
        print("PRECHECK_FAILED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
