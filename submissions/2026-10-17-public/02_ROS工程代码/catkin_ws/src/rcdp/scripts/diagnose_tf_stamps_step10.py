#!/usr/bin/env python3
"""Passive ROS1 timestamp diagnostic. No TF/clock/velocity publishing or writes.

Reads raw /tf (root_link only), /odom and /clock for 40 wall-clock seconds.
The aggregation class can be tested offline without importing ROS.
"""
from collections import Counter
import json
import threading
import time


class StampBook:
    def __init__(self):
        self.lock = threading.Lock()
        self.stats = {
            name: {"received_records": 0, "publishers": Counter(),
                   "frame_pairs": Counter(), "repeated_stamps": 0,
                   "same_source_repeats": 0, "cross_source_repeats": 0,
                   "backwards_per_source": 0, "changed_pose_on_same_stamp": 0}
            for name in ("tf_root", "odom", "clock")
        }
        self.seen = {"tf_root": {}, "odom": {}}
        self.last = {}
        self.duplicates = {"tf_root": set(), "odom": set()}
        self.examples = []
        self.clock_first = None
        self.clock_last = None
        self.clock_last_wall = None
        self.clock_max_gap = 0.0

    def record(self, kind, source, parent, child, stamp_ns, pose=None, seq=None):
        with self.lock:
            state = self.stats[kind]
            state["received_records"] += 1
            state["publishers"][source] += 1
            if kind != "clock":
                state["frame_pairs"][parent + " -> " + child] += 1
            stream_key = (kind, source, parent, child)
            previous_ns = self.last.get(stream_key)
            if previous_ns is not None and stamp_ns < previous_ns:
                state["backwards_per_source"] += 1
            self.last[stream_key] = stamp_ns

            if kind == "clock":
                # Only consecutive equality per clock publisher is counted here.
                if previous_ns == stamp_ns:
                    state["repeated_stamps"] += 1
                    state["same_source_repeats"] += 1
                now = time.monotonic()
                if self.clock_last_wall is not None:
                    self.clock_max_gap = max(self.clock_max_gap, now - self.clock_last_wall)
                self.clock_first = stamp_ns if self.clock_first is None else self.clock_first
                self.clock_last, self.clock_last_wall = stamp_ns, now
                return

            key = (parent, child, stamp_ns)
            sources = self.seen[kind].setdefault(key, {})
            if sources:
                state["repeated_stamps"] += 1
                self.duplicates[kind].add(key)
                same_source = source in sources
                changed = same_source and pose != sources[source]
                state["same_source_repeats" if same_source else "cross_source_repeats"] += 1
                state["changed_pose_on_same_stamp"] += int(changed)
                if len(self.examples) < 12:
                    self.examples.append({
                        "stream": kind, "source": source,
                        "frame_pair": parent + " -> " + child,
                        "stamp_ns": stamp_ns, "seq": seq,
                        "same_source_seen_before": same_source,
                        "pose_changed": changed
                    })
            sources[source] = pose

    def snapshot(self):
        with self.lock:
            result = json.loads(json.dumps(self.stats))
            result["common_tf_odom_duplicate_stamp_count"] = len(
                self.duplicates["tf_root"] & self.duplicates["odom"]
            )
            result["duplicate_examples"] = list(self.examples)
            result["clock_sim_advance_seconds"] = (
                (self.clock_last - self.clock_first) / 1e9
                if self.clock_first is not None else None
            )
            result["clock_max_receive_gap_wall_seconds"] = round(self.clock_max_gap, 6)
            result["counting_scope"] = (
                "TF/Odom: repeated frame-pair+stamp in this window; "
                "clock: consecutive equal stamps per publisher. "
                "Receiver gaps are observations here, not Gazebo internal timing proof."
            )
            return result


def caller(message):
    return (getattr(message, "_connection_header", None) or {}).get("callerid", "unknown")


def main():
    import rospy
    from nav_msgs.msg import Odometry
    from rosgraph_msgs.msg import Clock
    from tf2_msgs.msg import TFMessage

    rospy.init_node("lesson14_tf_stamp_diagnostic", anonymous=True)
    book = StampBook()

    def tf_callback(message):
        source = caller(message)
        for transform in message.transforms:
            child = transform.child_frame_id.lstrip("/")
            if child != "root_link":
                continue
            p, q = transform.transform.translation, transform.transform.rotation
            book.record("tf_root", source, transform.header.frame_id.lstrip("/"),
                        child, transform.header.stamp.to_nsec(),
                        (p.x, p.y, p.z, q.x, q.y, q.z, q.w))

    def odom_callback(message):
        p, q = message.pose.pose.position, message.pose.pose.orientation
        book.record("odom", caller(message), message.header.frame_id.lstrip("/"),
                    message.child_frame_id.lstrip("/"), message.header.stamp.to_nsec(),
                    (p.x, p.y, p.z, q.x, q.y, q.z, q.w), message.header.seq)

    def clock_callback(message):
        book.record("clock", caller(message), "", "", message.clock.to_nsec())

    print("Read-only diagnostic: observing 40 WALL seconds; leave simulation running.", flush=True)
    started = time.monotonic()
    subscriptions = []
    completed = False
    try:
        for topic, msg_type, callback in (
            ("/tf", TFMessage, tf_callback),
            ("/odom", Odometry, odom_callback),
            ("/clock", Clock, clock_callback),
        ):
            subscriptions.append(rospy.Subscriber(
                topic, msg_type, callback, queue_size=2000, tcp_nodelay=True
            ))
        while not rospy.is_shutdown() and time.monotonic() - started < 40.0:
            time.sleep(0.1)
        completed = not rospy.is_shutdown()
    except KeyboardInterrupt:
        pass
    finally:
        for subscription in subscriptions:
            subscription.unregister()
        report = book.snapshot()
        report["observed_wall_seconds"] = round(time.monotonic() - started, 3)
        report["completed_window"] = completed
        report["all_three_streams_received"] = all(
            report[name]["received_records"] > 0 for name in ("tf_root", "odom", "clock")
        )
        print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
        rospy.signal_shutdown("diagnostic finished")


if __name__ == "__main__":
    main()
