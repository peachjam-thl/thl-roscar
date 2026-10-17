#!/usr/bin/env python3
"""Offline source-delta and command-math tests, NOT a Gazebo runtime test."""

import ast
import hashlib
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CLASS = "GazeboRosSkidSteerDriveStampFix"
OLD_CLASS = "GazeboRosSkidSteerDrive"
SOURCE_PATH = "src/gazebo_ros_skid_steer_stampfix.cpp"
HEADER_PATH = "include/rcdp_4wd_stampfix/gazebo_ros_skid_steer_stampfix.h"
RESET = '''  // Begin a new simulation-time epoch with no retained wheel command.
  void GazeboRosSkidSteerDriveStampFix::Reset() {
    if (!world) return;
    boost::mutex::scoped_lock scoped_lock(lock);
    last_update_time_ = world->SimTime();
    x_ = 0;
    rot_ = 0;
    for (int i = 0; i < 4; ++i) {
      wheel_speed_[i] = 0;
      if (joints[i]) {
        joints[i]->SetParam("fmax", 0, torque);
        joints[i]->SetParam("vel", 0, 0.0);
      }
    }
  }

'''
TIME_GUARD = '''    // Handle a backwards simulation-time jump; never fabricate timestamps.
    if (current_time < last_update_time_) {
      Reset();
      return;
    }
    // Physics reset can clear motor fmax after the plugin Reset callback.
    for (int i = 0; i < 4; ++i) {
      if (std::fabs(joints[i]->GetParam("fmax", 0) - torque) > 1e-6)
        joints[i]->SetParam("fmax", 0, torque);
    }
'''
STAMP = '''    // Stamp the Gazebo world state directly, not the asynchronously cached /clock.
    const common::Time sim_time = world->SimTime();
    const ros::Time current_time(sim_time.sec, sim_time.nsec);'''


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def replace_once(value, old, new):
    if value.count(old) != 1:
        raise AssertionError("Expected one upstream patch target: " + repr(old))
    return value.replace(old, new)


def command_math(v, w, separation=0.72, diameter=0.20):
    source = read(SOURCE_PATH)
    method = re.search(r"void " + CLASS + r"::getWheelVelocities\(\)\s*\{(.*?)\n  \}", source, re.S)
    if not method:
        raise AssertionError("Missing wheel mapping method.")
    expressions = dict(re.findall(r"wheel_speed_\[(\w+)\] = ([^;]+);", method.group(1)))
    if set(expressions) != {"LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR"}:
        raise AssertionError("Expected four actual wheel target assignments.")
    variables = {"vr": v, "va": w, "wheel_separation_": separation}
    allowed = (ast.Expression, ast.BinOp, ast.Name, ast.Load, ast.Constant, ast.Add, ast.Sub, ast.Mult, ast.Div)
    result = {}
    for name, expression in expressions.items():
        tree = ast.parse(expression, mode="eval")
        if any(not isinstance(node, allowed) for node in ast.walk(tree)):
            raise AssertionError("Unexpected expression syntax.")
        if any(node.id not in variables for node in ast.walk(tree) if isinstance(node, ast.Name)):
            raise AssertionError("Unexpected wheel expression variable.")
        linear = eval(compile(tree, "<wheel-command-math>", "eval"), {"__builtins__": {}}, variables)
        result[name] = linear / (diameter / 2.0)
    return result


class SourceTests(unittest.TestCase):
    def test_01_original_hashes_and_commit(self):
        metadata = json.loads(read("UPSTREAM.json"))
        self.assertEqual(metadata["tag"], "2.9.3")
        self.assertEqual(metadata["commit"], "cd9cc952402375be5f274f39b29399c4087aa839")
        for item in metadata["files"]:
            self.assertEqual(hashlib.sha256((ROOT / item["original"]).read_bytes()).hexdigest(), item["sha256"])

    def test_02_exact_cpp_patch_scope(self):
        expected = read("upstream/gazebo_ros_skid_steer_drive.cpp").replace(OLD_CLASS, CLASS)
        edits = [
            ("#include <gazebo_plugins/gazebo_ros_skid_steer_drive.h>", "#include <rcdp_4wd_stampfix/gazebo_ros_skid_steer_stampfix.h>"),
            ("#include <assert.h>\n", "#include <assert.h>\n#include <cmath>\n"),
            ("  " + CLASS + "::~" + CLASS + "() {\n", "  " + CLASS + "::~" + CLASS + "() {\n    FiniChild();\n"),
            ("  // Update the controller\n", RESET + "  // Update the controller\n"),
            ("  void " + CLASS + "::UpdateChild()\n  {\n", "  void " + CLASS + "::UpdateChild()\n  {\n    if (!alive_) return;\n"),
            ("#endif\n    double seconds_since_last_update =\n", "#endif\n" + TIME_GUARD + "    double seconds_since_last_update =\n"),
            ("    alive_ = false;\n    queue_.clear();\n    queue_.disable();\n    rosnode_->shutdown();\n    callback_queue_thread_.join();",
             "    alive_ = false;\n    update_connection_.reset();\n    queue_.clear();\n    queue_.disable();\n    if (rosnode_) rosnode_->shutdown();\n    if (callback_queue_thread_.joinable()) callback_queue_thread_.join();"),
            ("    ros::Time current_time = ros::Time::now();", STAMP),
            ("    odom_.pose.pose.position.y = pose.Pos().Y();\n", "    odom_.pose.pose.position.y = pose.Pos().Y();\n    odom_.pose.pose.position.z = pose.Pos().Z();\n"),
        ]
        for before, after in edits:
            expected = replace_once(expected, before, after)
        self.assertEqual(read(SOURCE_PATH), expected)

    def test_03_exact_header_patch_scope(self):
        expected = read("upstream/gazebo_ros_skid_steer_drive.h").replace(OLD_CLASS, CLASS).replace(
            "GAZEBO_ROS_SKID_STEER_DRIVE_H_", "RCDP_4WD_STAMPFIX_GAZEBO_ROS_SKID_STEER_H_"
        )
        for before, after in [
            ("#include <map>\n", "#include <map>\n#include <atomic>\n"),
            ("      void Load(physics::ModelPtr _parent, sdf::ElementPtr _sdf);\n", "      void Load(physics::ModelPtr _parent, sdf::ElementPtr _sdf);\n      void Reset() override;\n"),
            ("ros::NodeHandle* rosnode_;", "ros::NodeHandle* rosnode_ = nullptr;"),
            ("tf::TransformBroadcaster *transform_broadcaster_;", "tf::TransformBroadcaster *transform_broadcaster_ = nullptr;"),
            ("bool alive_;", "std::atomic<bool> alive_{false};"),
        ]:
            expected = replace_once(expected, before, after)
        self.assertEqual(read(HEADER_PATH), expected)

    def test_04_original_license_retained(self):
        for before, after in [("upstream/gazebo_ros_skid_steer_drive.cpp", SOURCE_PATH),
                              ("upstream/gazebo_ros_skid_steer_drive.h", HEADER_PATH)]:
            self.assertTrue(read(after).startswith(read(before).split("*/", 1)[0] + "*/"))

    def test_05_four_actual_joint_motor_targets(self):
        source, header = read(SOURCE_PATH), read(HEADER_PATH)
        for wheel in ("LEFT_FRONT", "RIGHT_FRONT", "LEFT_REAR", "RIGHT_REAR"):
            self.assertIn('joints[' + wheel + ']->SetParam("vel", 0, wheel_speed_[' + wheel + '] / (wheel_diameter_ / 2.0));', source)
        self.assertIn("double wheel_speed_[4];", header)
        self.assertIn("physics::JointPtr joints[4];", header)

    def test_06_forward_math_from_actual_source(self):
        for omega in command_math(0.1, 0).values():
            self.assertAlmostEqual(omega, 1.0)

    def test_07_reverse_math_from_actual_source(self):
        for omega in command_math(-0.1, 0).values():
            self.assertAlmostEqual(omega, -1.0)

    def test_08_positive_yaw_math_from_actual_source(self):
        values = command_math(0, 0.2)
        self.assertAlmostEqual(values["LEFT_FRONT"], -0.72)
        self.assertAlmostEqual(values["LEFT_REAR"], -0.72)
        self.assertAlmostEqual(values["RIGHT_FRONT"], 0.72)
        self.assertAlmostEqual(values["RIGHT_REAR"], 0.72)

    def test_09_curve_math_from_actual_source(self):
        values = command_math(0.1, 0.2)
        self.assertAlmostEqual(values["LEFT_FRONT"], 0.28)
        self.assertAlmostEqual(values["LEFT_REAR"], 0.28)
        self.assertAlmostEqual(values["RIGHT_FRONT"], 1.72)
        self.assertAlmostEqual(values["RIGHT_REAR"], 1.72)

    def test_10_time_and_pose_consistency_source(self):
        source = read(SOURCE_PATH)
        self.assertNotIn("ros::Time::now()", source)
        self.assertIn("const ros::Time current_time(sim_time.sec, sim_time.nsec);", source)
        self.assertIn("odom_.header.stamp = current_time;", source)
        self.assertIn("tf::StampedTransform(base_footprint_to_odom, current_time,", source)
        self.assertIn("odom_.pose.pose.position.z = pose.Pos().Z();", source)

    def test_11_manifest_and_build_identity(self):
        manifest = ET.fromstring(read("package.xml"))
        self.assertEqual(manifest.findtext("name"), "rcdp_4wd_stampfix")
        self.assertEqual(manifest.findtext("license"), "BSD-3-Clause")
        cmake = read("CMakeLists.txt")
        self.assertIn("add_library(rcdp_4wd_stampfix SHARED", cmake)
        self.assertIn("find_package(gazebo 11 REQUIRED)", cmake)
        self.assertIn("GZ_REGISTER_MODEL_PLUGIN(" + CLASS + ")", read(SOURCE_PATH))
        self.assertNotRegex(cmake, r"\bgazebo_ros_(diff_drive|skid_steer_drive)\b")

    def test_12_no_launch_model_or_binary_in_compile_package(self):
        for suffix in ("*.launch", "*.xacro", "*.so"):
            self.assertEqual(list(ROOT.rglob(suffix)), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
