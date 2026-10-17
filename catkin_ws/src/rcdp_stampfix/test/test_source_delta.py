#!/usr/bin/env python3
"""Offline source/provenance checks; NOT a Gazebo build or runtime test."""

import hashlib
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
OLD_CLASS = "GazeboRosDiffDrive"
NEW_CLASS = "GazeboRosDiffDriveStampFix"
OLD_STAMP = "    ros::Time current_time = ros::Time::now();"
NEW_STAMP = (
    "    // Stamp the physics state directly, without the asynchronously cached /clock.\n"
    "    const common::Time sim_time = parent->GetWorld()->SimTime();\n"
    "    const ros::Time current_time(sim_time.sec, sim_time.nsec);"
)


def read(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


class SourceDeltaTests(unittest.TestCase):
    def test_01_upstream_hashes(self):
        metadata = json.loads(read("UPSTREAM.json"))
        self.assertEqual(metadata["tag"], "2.9.3")
        self.assertEqual(metadata["commit"], "cd9cc952402375be5f274f39b29399c4087aa839")
        for item in metadata["files"]:
            actual = hashlib.sha256((ROOT / item["vendored_original"]).read_bytes()).hexdigest()
            self.assertEqual(actual, item["sha256"], item["path"])

    def test_02_cpp_has_only_allowed_edits(self):
        original = read("upstream/gazebo_ros_diff_drive.cpp")
        self.assertEqual(original.count(OLD_STAMP), 3)
        expected = original.replace(OLD_CLASS, NEW_CLASS).replace(
            "#include <gazebo_plugins/gazebo_ros_diff_drive.h>",
            "#include <rcdp_stampfix/gazebo_ros_diff_drive_stampfix.h>",
        ).replace(OLD_STAMP, NEW_STAMP)
        self.assertEqual(read("src/gazebo_ros_diff_drive_stampfix.cpp"), expected)

    def test_03_header_has_only_allowed_edits(self):
        expected = read("upstream/gazebo_ros_diff_drive.h").replace(
            OLD_CLASS, NEW_CLASS
        ).replace("DIFFDRIVE_PLUGIN_HH", "RCDP_STAMPFIX_GAZEBO_ROS_DIFF_DRIVE_HH")
        self.assertEqual(read("include/rcdp_stampfix/gazebo_ros_diff_drive_stampfix.h"), expected)

    def test_04_three_physics_timestamps_no_ros_now(self):
        source = read("src/gazebo_ros_diff_drive_stampfix.cpp")
        self.assertNotIn("ros::Time::now()", source)
        self.assertEqual(source.count(NEW_STAMP), 3)
        self.assertIn("odom_.header.stamp = current_time;", source)
        for name in ("publishOdometry", "publishWheelTF", "publishWheelJointState"):
            pattern = (
                r"void " + NEW_CLASS + r"::" + name
                + r"\s*\([^)]*\)\s*\{\s*"
                + re.escape(NEW_STAMP.strip())
            )
            self.assertRegex(source, pattern)

    def test_05_unique_plugin_identity_and_explicit_utility_link(self):
        source = read("src/gazebo_ros_diff_drive_stampfix.cpp")
        self.assertIn("GZ_REGISTER_MODEL_PLUGIN ( " + NEW_CLASS + " )", source)
        self.assertIsNone(re.search(r"\b" + OLD_CLASS + r"\b", source))
        cmake = read("CMakeLists.txt")
        self.assertIn("add_library(rcdp_diff_drive_stampfix SHARED", cmake)
        self.assertIn("${GAZEBO_ROS_UTILS_LIBRARY}", cmake)
        self.assertNotRegex(cmake, r"\bgazebo_ros_diff_drive\b")
        self.assertIn("find_package(gazebo 11 REQUIRED)", cmake)

    def test_06_manifest_and_scope(self):
        manifest = ET.fromstring(read("package.xml"))
        self.assertEqual(manifest.findtext("name"), "rcdp_stampfix")
        self.assertEqual(manifest.findtext("buildtool_depend"), "catkin")
        self.assertEqual(manifest.findtext("license"), "BSD-3-Clause")
        dependencies = {node.text for node in manifest.findall("depend")}
        self.assertTrue({"gazebo_dev", "gazebo_plugins", "roscpp", "tf"} <= dependencies)
        self.assertEqual(
            manifest.find("export/gazebo_ros").get("plugin_path"), "${prefix}/../../lib"
        )
        self.assertEqual(list(ROOT.glob("**/*.launch")), [])
        self.assertEqual(list(ROOT.glob("**/*.xacro")), [])
        self.assertEqual(list(ROOT.glob("**/*.so")), [])

    def test_07_original_license_retained(self):
        for original, patched in (
            ("upstream/gazebo_ros_diff_drive.cpp", "src/gazebo_ros_diff_drive_stampfix.cpp"),
            ("upstream/gazebo_ros_diff_drive.h", "include/rcdp_stampfix/gazebo_ros_diff_drive_stampfix.h"),
        ):
            license_block = read(original).split("*/", 1)[0] + "*/"
            self.assertTrue(read(patched).startswith(license_block))


if __name__ == "__main__":
    unittest.main(verbosity=2)
