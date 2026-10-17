#!/usr/bin/env python3
"""Passive 40-wall-second audit of step11H joints, TF, odometry and clock.

No publishers, service calls, parameter writes, motion or simulation restarts.
ROS imports are inside main so the aggregation logic can be tested offline.
"""

from collections import Counter
import json
import math
import sys
import threading
import time


RSP = "/lesson14_4wd_robot_state_publisher"
GAZEBO = "/gazebo"
JOINT_CHILDREN = {
    "front_left_wheel_joint": "front_left_wheel_link",
    "front_right_wheel_joint": "front_right_wheel_link",
    "rear_left_wheel_joint": "rear_left_wheel_link",
    "rear_right_wheel_joint": "rear_right_wheel_link",
    "depth_camera_link2base_link": "depth_camera_link",
    "laser_scan_link2platform_link": "laser_scan_link",
}
ROOT_EDGE = "odom -> root_link"
DYNAMIC = {ROOT_EDGE: GAZEBO}
DYNAMIC.update({("platform_link" if child == "laser_scan_link" else "base_link")
                + " -> " + child: RSP for child in JOINT_CHILDREN.values()})
STATIC = {edge: RSP for edge in (
    "root_link -> base_link", "base_link -> support_link", "support_link -> platform_link")}
BAD_FIELDS = ("repeated_stamps", "same_source_repeats", "cross_source_repeats",
              "backwards_per_source", "changed_payload_on_same_stamp", "zero_stamps")


def caller(msg):
    return (getattr(msg, "_connection_header", None) or {}).get("callerid", "unknown")


def edge(parent, child):
    return parent.lstrip("/") + " -> " + child.lstrip("/")


def pose_values(p, q):
    values = (p.x, p.y, p.z, q.x, q.y, q.z, q.w)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Non-finite pose")
    if not math.isclose(sum(v * v for v in values[3:]), 1.0, rel_tol=0, abs_tol=1e-3):
        raise ValueError("Quaternion not approximately unit length")
    return values


def new_stats():
    result = {"records": 0, "publishers": Counter()}
    result.update({key: 0 for key in BAD_FIELDS})
    return result


class Audit:
    def __init__(self):
        self.lock = threading.RLock()
        self.stats = {"dynamic_tf": {}, "odom": {}, "joints": {}, "clock": {}}
        self.seen = {}
        self.last = {}
        self.static = {}
        self.static_pose = {}
        self.invalid = Counter()
        self.unexpected = Counter()
        self.examples = []
        self.joint_messages = 0
        self.joint_publishers = Counter()
        self.clock_first = self.clock_last = self.clock_wall = None
        self.clock_max_receive_gap = 0.0

    def example(self, **values):
        if len(self.examples) < 12:
            self.examples.append(values)

    def record(self, kind, key, source, stamp, payload=None):
        with self.lock:
            state = self.stats[kind].setdefault(key, new_stats())
            state["records"] += 1
            state["publishers"][source] += 1
            state["zero_stamps"] += int(stamp == 0)
            stream = (kind, key, source)
            previous = self.last.get(stream)
            if previous is not None and stamp < previous:
                state["backwards_per_source"] += 1
                self.example(stream=kind, key=key, source=source, event="backwards", stamp_ns=stamp)
            self.last[stream] = stamp
            if kind == "clock":
                if previous == stamp:
                    state["repeated_stamps"] += 1
                    state["same_source_repeats"] += 1
                now = time.monotonic()
                if self.clock_wall is not None:
                    self.clock_max_receive_gap = max(self.clock_max_receive_gap, now - self.clock_wall)
                if self.clock_first is None:
                    self.clock_first = stamp
                self.clock_last, self.clock_wall = stamp, now
                return
            sources = self.seen.setdefault((kind, key, stamp), {})
            if sources:
                same_source = source in sources
                changed = same_source and sources[source] != payload
                state["repeated_stamps"] += 1
                state["same_source_repeats" if same_source else "cross_source_repeats"] += 1
                state["changed_payload_on_same_stamp"] += int(changed)
                self.example(stream=kind, key=key, source=source, event="repeated",
                             stamp_ns=stamp, same_source=same_source, payload_changed=changed)
            sources[source] = payload

    def tf(self, msg, is_static=False):
        with self.lock:
            source = caller(msg)
            for item in msg.transforms:
                pair = edge(item.header.frame_id, item.child_frame_id)
                expected = STATIC if is_static else DYNAMIC
                if pair not in expected:
                    self.unexpected[("/tf_static: " if is_static else "/tf: ") + pair] += 1
                try:
                    payload = pose_values(item.transform.translation, item.transform.rotation)
                    if is_static:
                        state = self.static.setdefault(pair, {"records": 0, "publishers": Counter(),
                                                              "changed_static_pose": 0})
                        state["records"] += 1
                        state["publishers"][source] += 1
                        key = (pair, source)
                        if key in self.static_pose and self.static_pose[key] != payload:
                            state["changed_static_pose"] += 1
                        self.static_pose[key] = payload
                    else:
                        self.record("dynamic_tf", pair, source, item.header.stamp.to_nsec(), payload)
                except (ValueError, TypeError, AttributeError, OverflowError):
                    self.invalid["static_tf_payload" if is_static else "dynamic_tf_payload"] += 1

    def joints(self, msg):
        with self.lock:
            self.joint_messages += 1
            self.joint_publishers[caller(msg)] += 1
            try:
                names = list(msg.name)
                count = len(names)
                # This installed Gazebo plugin supplies position AND velocity.
                # Empty effort and empty header.frame_id are deliberately accepted.
                if count != 6 or len(set(names)) != 6 or set(names) != set(JOINT_CHILDREN):
                    raise ValueError("Missing, unexpected or duplicate joint names")
                if len(msg.position) != count or len(msg.velocity) != count or len(msg.effort) not in (0, count):
                    raise ValueError("Unexpected joint array lengths")
                if not all(math.isfinite(v) for values in (msg.position, msg.velocity, msg.effort) for v in values):
                    raise ValueError("Non-finite joint values")
                for index, name in enumerate(names):
                    payload = (msg.position[index], msg.velocity[index])
                    self.record("joints", name, caller(msg), msg.header.stamp.to_nsec(), payload)
            except (ValueError, TypeError, AttributeError, OverflowError):
                self.invalid["joint_state_layout_or_values"] += 1

    def odom(self, msg):
        with self.lock:
            pair = edge(msg.header.frame_id, msg.child_frame_id)
            if pair != ROOT_EDGE:
                self.unexpected["/odom: " + pair] += 1
            try:
                payload = pose_values(msg.pose.pose.position, msg.pose.pose.orientation)
                self.record("odom", pair, caller(msg), msg.header.stamp.to_nsec(), payload)
            except (ValueError, TypeError, AttributeError, OverflowError):
                self.invalid["odom_payload"] += 1

    def clock(self, msg):
        self.record("clock", "/clock", caller(msg), msg.clock.to_nsec())

    def snapshot(self, completed, wall_seconds):
        with self.lock:
            issues = []
            expected_streams = (("dynamic_tf", DYNAMIC), ("odom", {ROOT_EDGE: GAZEBO}),
                                ("joints", {key: GAZEBO for key in JOINT_CHILDREN}),
                                ("clock", {"/clock": GAZEBO}))
            for kind, expected in expected_streams:
                for key, owner in expected.items():
                    state = self.stats[kind].get(key)
                    if not state:
                        issues.append(kind + ": missing " + key)
                        continue
                    if set(state["publishers"]) != {owner}:
                        issues.append(kind + ": unexpected publisher(s) for " + key)
                    # /clock=0 can be valid at simulation start; still report it.
                    for metric in BAD_FIELDS:
                        if metric == "zero_stamps" and kind == "clock":
                            continue
                        if state[metric]:
                            issues.append(kind + ": " + key + ": " + metric + "=" + str(state[metric]))
            for key, owner in STATIC.items():
                state = self.static.get(key)
                if not state:
                    issues.append("static_tf: missing " + key)
                elif set(state["publishers"]) != {owner} or state["changed_static_pose"]:
                    issues.append("static_tf: unexpected owner or changing fixed pose: " + key)
            advance = ((self.clock_last - self.clock_first) / 1e9 if self.clock_first is not None else None)
            if advance is None or advance <= 0:
                issues.append("No positive simulation-clock advance observed")
            if not completed:
                issues.append("Observation window not completed")
            if self.invalid:
                issues.append("Invalid message layout or non-finite/non-unit pose observed")
            if self.unexpected:
                issues.append("Unexpected TF/odometry edges observed; review scene/node scope")
            if set(self.joint_publishers) != {GAZEBO}:
                issues.append("Unexpected /joint_states publisher(s) or no messages")
            joint_anomalies = {key: {metric: s[metric] for metric in BAD_FIELDS if s[metric]}
                               for key, s in self.stats["joints"].items() if any(s[m] for m in BAD_FIELDS)}
            report = {
                "status": "WINDOW_OK" if not issues else "REVIEW_REQUIRED",
                "completed_window": bool(completed), "observed_wall_seconds": round(wall_seconds, 3),
                "dynamic_tf": self.stats["dynamic_tf"], "static_tf": self.static,
                "joint_states": {"messages": self.joint_messages, "publishers": self.joint_publishers,
                                 "valid_samples_per_joint": {key: s["records"] for key, s in self.stats["joints"].items()},
                                 "joint_timestamp_anomalies": joint_anomalies},
                "odom": self.stats["odom"], "clock": self.stats["clock"],
                "invalid_message_counts": self.invalid, "unexpected_edge_counts": self.unexpected,
                "anomaly_examples": self.examples, "issues": issues,
                "clock_sim_advance_seconds": advance,
                "clock_max_receive_gap_wall_seconds": round(self.clock_max_receive_gap, 6),
                "scope": "Passive received-data window only. Static latched replay is not a dynamic timestamp duplicate. No motion, live-sensor or long-duration validation.",
                "gazebo_or_robot_configuration_changed": False,
                "long_term_or_sensor_loaded_stability_verified": False,
            }
            return json.loads(json.dumps(report))


def main():
    import rospy
    from nav_msgs.msg import Odometry
    from rosgraph_msgs.msg import Clock
    from sensor_msgs.msg import JointState
    from tf2_msgs.msg import TFMessage

    rospy.init_node("lesson14_4wd_tf_audit_step11h", anonymous=True, disable_signals=True)
    book = Audit()
    subscriptions = []
    started = time.monotonic()
    completed = False
    print("Read-only audit: observing 40 WALL seconds. Leave Gazebo running; do not move/reset the robot.", flush=True)
    try:
        for topic, kind, callback in (("/tf", TFMessage, book.tf),
                                      ("/tf_static", TFMessage, lambda msg: book.tf(msg, True)),
                                      ("/joint_states", JointState, book.joints),
                                      ("/odom", Odometry, book.odom), ("/clock", Clock, book.clock)):
            subscriptions.append(rospy.Subscriber(topic, kind, callback, queue_size=2000, tcp_nodelay=True))
        while not rospy.is_shutdown() and time.monotonic() - started < 40.0:
            time.sleep(0.1)
        completed = not rospy.is_shutdown() and time.monotonic() - started >= 40.0
    except KeyboardInterrupt:
        pass
    finally:
        for subscription in subscriptions:
            subscription.unregister()
        report = book.snapshot(completed, time.monotonic() - started)
        print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
        rospy.signal_shutdown("read-only audit finished")
    return 0 if report["status"] == "WINDOW_OK" else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print("AUDIT_FAILED: " + str(error), file=sys.stderr, flush=True)
        sys.exit(1)
