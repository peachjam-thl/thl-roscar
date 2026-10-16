"""Offline synthetic/mock tests. No ROS, Gazebo or VMware runtime is claimed."""
from pathlib import Path
import ast
import copy
import importlib.util
import struct
from types import SimpleNamespace as NS
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "catkin_ws/src/rcdp/scripts/cloud_preview_step9a.py"
ast.parse(SCRIPT.read_text(encoding="utf-8"), feature_version=(3, 8))
spec = importlib.util.spec_from_file_location("cloud_preview_under_test", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def example_cloud(width=19, height=11, padding=16, bigendian=False):
    step, row = 32, width * 32 + padding
    data = bytearray([0xA5]) * (height * row)
    fmt = (">" if bigendian else "<") + "8f"
    for v in range(height):
        for u in range(width):
            struct.pack_into(fmt, data, v * row + u * step,
                             float(u), float(v), 1.0 + u / 10.0,
                             0.0, float(u + v), 0.0, 0.0, 1.0)
    return NS(
        width=width, height=height, point_step=step, row_step=row,
        data=bytes(data), is_bigendian=bigendian, is_dense=True,
        header=NS(seq=7, stamp=NS(secs=123, nsecs=456), frame_id=module.EXPECTED_FRAME),
        fields=[NS(name=name, offset=offset, datatype=7, count=1)
                for name, offset in (("x", 0), ("y", 4), ("z", 8), ("rgb", 16))]
    )


class FakeROS:
    ROSException = RuntimeError

    def __init__(self):
        self.shutdown = False
        self.warnings = []
        self.subscription_events = []
        self.pub = NS(connections=0, messages=[])
        self.pub.get_num_connections = lambda: self.pub.connections
        self.pub.publish = lambda msg: self.pub.messages.append(msg)

    def Publisher(self, topic, cloud_type, **kwargs):
        self.published_topic, self.publisher_options = topic, kwargs
        return self.pub

    def Subscriber(self, topic, cloud_type, callback, **kwargs):
        self.subscription_events.append(("subscribe", topic, kwargs))
        self.callback = callback
        return NS(unregister=lambda: self.subscription_events.append(("unsubscribe", topic)))

    def is_shutdown(self):
        return self.shutdown

    def loginfo(self, *args):
        pass

    def logwarn_throttle(self, *args):
        self.warnings.append(args)


class PreviewTests(unittest.TestCase):
    def test_exact_point_bytes_both_endians_and_padded_rows(self):
        for big in (False, True):
            with self.subTest(bigendian=big):
                source = example_cloud(bigendian=big)
                out = module.make_preview(source, NS, 8)
                self.assertEqual((out.width, out.height), (3, 2))
                self.assertEqual(out.row_step, 96)
                expected = b"".join(
                    source.data[v * source.row_step + u * 32:v * source.row_step + (u + 1) * 32]
                    for v in (0, 8) for u in (0, 8, 16)
                )
                self.assertEqual(out.data, expected)
                self.assertEqual(out.is_bigendian, big)

    def test_real_resolution_preview_size(self):
        source = example_cloud(width=640, height=480, padding=0)
        out = module.make_preview(source, NS, 8)
        self.assertEqual((out.width, out.height), (80, 60))
        self.assertEqual(out.width * out.height, 4800)
        self.assertEqual(len(out.data), 153600)
        self.assertEqual(len(source.data), 9830400)

    def test_header_fields_and_source_are_not_modified(self):
        source = example_cloud()
        before = copy.deepcopy(source)
        out = module.make_preview(source, NS, 8)
        self.assertEqual(source, before)
        self.assertEqual(out.header.frame_id, source.header.frame_id)
        self.assertEqual(out.header.stamp, source.header.stamp)
        self.assertIsNot(out.header, source.header)
        self.assertEqual(out.fields, source.fields)
        self.assertIsNot(out.fields, source.fields)
        out.header.seq = 999
        out.fields[0].offset = 1
        self.assertEqual(source.header.seq, 7)
        self.assertEqual(source.fields[0].offset, 0)

    def test_nan_bytes_and_dense_flag_are_preserved(self):
        source = example_cloud(width=1, height=1, padding=0)
        raw = bytearray(source.data)
        struct.pack_into("<I", raw, 0, 0x7FC01234)
        source.data, source.is_dense = bytes(raw), False
        out = module.make_preview(source, NS, 8)
        self.assertEqual(out.data, source.data)
        self.assertFalse(out.is_dense)

    def test_invalid_layouts_are_rejected(self):
        for args in ((0, 1, 32, 32, bytes(32), 8), (1, 1, 32, 31, bytes(31), 8),
                     (1, 1, 32, 32, bytes(31), 8), (1, 1, 32, 32, bytes(33), 8),
                     (1, 1, 32, 32, bytes(32), 0)):
            with self.subTest(layout=args[:4]), self.assertRaises(ValueError):
                module.decimate_bytes(*args)

    def test_invalid_fields_are_rejected(self):
        for change in ("missing", "duplicate", "overrun", "bad_type", "overlap"):
            source = example_cloud()
            if change == "missing":
                source.fields.pop(2)
            elif change == "duplicate":
                source.fields[1].name = "x"
            elif change == "overrun":
                source.fields[2].offset = 31
            elif change == "bad_type":
                source.fields[2].datatype = 99
            else:
                source.fields[1].offset = 2
            with self.subTest(change=change), self.assertRaises(ValueError):
                module.make_preview(source, NS, 8)

    def test_rate_bound_and_duplicate_stamp_gate(self):
        gate = module.PublishGate(2.0)
        self.assertTrue(gate.allow(0.0, (100, 0)))
        self.assertFalse(gate.allow(0.1, (100, 1)))
        self.assertFalse(gate.allow(0.499, (100, 2)))
        self.assertTrue(gate.allow(0.5, (100, 3)))
        self.assertFalse(gate.allow(1.0, (100, 3)))
        self.assertTrue(gate.allow(1.0, (100, 4)))
        self.assertTrue(gate.allow(1.5, (0, 1)))

    def test_parameter_safety_bounds(self):
        self.assertEqual(module.validate_parameters(8, 2), (8, 2.0))
        self.assertEqual(module.validate_parameters(4, 0.5), (4, 0.5))
        for stride, hz in ((3, 2), (True, 2), (8.0, 2), (8, 0), (8, 3),
                           (8, float("nan")), (8, float("inf")), (8, True)):
            with self.subTest(stride=stride, hz=hz), self.assertRaises(ValueError):
                module.validate_parameters(stride, hz)

    def test_on_demand_source_subscription_and_cleanup(self):
        ros = FakeROS()
        relay = module.PreviewRelay(ros, NS, 8, 2.0)
        turns = []

        def step(_duration):
            turns.append(1)
            if len(turns) == 1:
                self.assertEqual(ros.subscription_events, [])
                ros.pub.connections = 1
            elif len(turns) == 2:
                ros.callback(example_cloud())
                ros.pub.connections = 0
            elif len(turns) == 3:
                ros.shutdown = True
            else:
                raise AssertionError("unexpected polling loop")

        with mock.patch.object(module.time, "sleep", side_effect=step):
            relay.run()
        self.assertEqual(ros.published_topic, module.PREVIEW_TOPIC)
        self.assertEqual(ros.publisher_options, {"queue_size": 1, "latch": False})
        self.assertEqual([event[0] for event in ros.subscription_events], ["subscribe", "unsubscribe"])
        self.assertEqual(ros.subscription_events[0][1], module.RAW_TOPIC)
        self.assertEqual(ros.subscription_events[0][2]["queue_size"], 1)
        self.assertEqual(len(ros.pub.messages), 1)
        self.assertEqual(ros.pub.messages[0].header.stamp, NS(secs=123, nsecs=456))
        self.assertEqual(ros.warnings, [])
        self.assertTrue(relay.stopping)


if __name__ == "__main__":
    unittest.main(verbosity=2)
