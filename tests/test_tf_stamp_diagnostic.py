"""Offline aggregation tests only; not an Ubuntu ROS runtime test."""
from pathlib import Path
import ast
import importlib.util
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "catkin_ws/src/rcdp/scripts/diagnose_tf_stamps_step10.py"
tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), feature_version=(3, 8))
spec = importlib.util.spec_from_file_location("stamp_diagnostic", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Tests(unittest.TestCase):
    def test_identifies_same_source_and_pose_change(self):
        book = module.StampBook()
        book.record("tf_root", "/gazebo", "odom", "root_link", 123, (0,) * 7)
        book.record("tf_root", "/gazebo", "odom", "root_link", 123, (1,) * 7)
        result = book.snapshot()["tf_root"]
        self.assertEqual(result["repeated_stamps"], 1)
        self.assertEqual(result["same_source_repeats"], 1)
        self.assertEqual(result["changed_pose_on_same_stamp"], 1)

    def test_cross_source_then_same_source(self):
        book = module.StampBook()
        for source in ("/a", "/b", "/b"):
            book.record("tf_root", source, "odom", "root_link", 1, (0,))
        result = book.snapshot()["tf_root"]
        self.assertEqual(result["cross_source_repeats"], 1)
        self.assertEqual(result["same_source_repeats"], 1)

    def test_common_tf_odom_duplicates(self):
        book = module.StampBook()
        for kind in ("tf_root", "odom"):
            for _ in range(2):
                book.record(kind, "/gazebo", "odom", "root_link", 1234, (0,))
        self.assertEqual(book.snapshot()["common_tf_odom_duplicate_stamp_count"], 1)

    def test_backward_and_non_adjacent_repeat(self):
        book = module.StampBook()
        for stamp in (10, 11, 9, 10):
            book.record("odom", "/gazebo", "odom", "root_link", stamp)
        result = book.snapshot()["odom"]
        self.assertEqual(result["backwards_per_source"], 1)
        self.assertEqual(result["repeated_stamps"], 1)

    def test_clock_counts_and_zero_stamp(self):
        book = module.StampBook()
        for stamp in (0, 0, 100, 90):
            book.record("clock", "/gazebo", "", "", stamp)
        result = book.snapshot()
        self.assertEqual(result["clock"]["same_source_repeats"], 1)
        self.assertEqual(result["clock"]["backwards_per_source"], 1)
        self.assertEqual(result["clock_sim_advance_seconds"], 90 / 1e9)

    def test_bounded_example_output_and_no_business_writes(self):
        book = module.StampBook()
        for _ in range(20):
            book.record("tf_root", "/gazebo", "odom", "root_link", 1)
        self.assertEqual(len(book.snapshot()["duplicate_examples"]), 12)
        calls = [node.func.attr for node in ast.walk(tree)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
        self.assertNotIn("Publisher", calls)
        self.assertNotIn("ServiceProxy", calls)
        self.assertNotIn("set_param", calls)


if __name__ == "__main__":
    unittest.main(verbosity=2)
