#!/usr/bin/env python3
"""Gazebo-only short RIGHT turn with explicit zeros and measured wheel rates.

Run only in the current step11F B/cone trial, with clear space around the car and no
other /cmd_vel source. This script DOES command motion. It is not a hardware
safety controller, an obstacle detector or an automatic command-timeout fix.
"""

import json
import math
import queue
import statistics
import sys
import threading
import time


MODEL = "lesson13_robot"
WHEELS = ("front_left_wheel_joint", "front_right_wheel_joint",
          "rear_left_wheel_joint", "rear_right_wheel_joint")
TURN_RADPS = -0.20
TURN_WALL_SECONDS = 3.0
ZERO_WALL_SECONDS = 2.0
WHEEL_RADIUS_M = 0.10
TRACK_WIDTH_M = 0.72
IDEAL_TARGETS = {
    "front_left_wheel_joint": -TURN_RADPS * TRACK_WIDTH_M / (2 * WHEEL_RADIUS_M),
    "front_right_wheel_joint": TURN_RADPS * TRACK_WIDTH_M / (2 * WHEEL_RADIUS_M),
    "rear_left_wheel_joint": -TURN_RADPS * TRACK_WIDTH_M / (2 * WHEEL_RADIUS_M),
    "rear_right_wheel_joint": TURN_RADPS * TRACK_WIDTH_M / (2 * WHEEL_RADIUS_M),
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def call_wall(label, function, *args, timeout=1.0):
    """Bound a read-only ROS RPC by wall time; a stuck RPC cannot hold driving open."""
    result = queue.Queue(maxsize=1)

    def work():
        try:
            result.put((True, function(*args)))
        except Exception as error:
            result.put((False, error))

    threading.Thread(target=work, daemon=True).start()
    try:
        ok, value = result.get(timeout=timeout)
    except queue.Empty:
        raise RuntimeError(label + " timed out (wall time).")
    if not ok:
        raise RuntimeError(label + ": " + str(value))
    return value


def graph_guard(master, own_name):
    publishers, subscribers, _ = call_wall("ROS graph", master.getSystemState)
    others = set(dict(publishers).get("/cmd_vel", [])) - {own_name}
    require(not others, "Other /cmd_vel publishers: " + str(sorted(others)))
    require("/gazebo" in dict(subscribers).get("/cmd_vel", []),
            "Gazebo is not registered as a /cmd_vel subscriber.")


def joint_rates(proxy):
    rates = {}
    for name in WHEELS:
        response = call_wall(name, proxy, MODEL + "::" + name)
        require(response.success and len(response.rate) == 1,
                name + ": " + response.status_message)
        value = float(response.rate[0])
        require(math.isfinite(value), "Non-finite wheel rate: " + name)
        rates[name] = value
    return rates


def model_state(proxy):
    response = call_wall("model state", proxy, MODEL, "world")
    require(response.success, response.status_message)
    p, q, v, w = (response.pose.position, response.pose.orientation,
                  response.twist.linear, response.twist.angular)
    values = (p.x, p.y, p.z, q.x, q.y, q.z, q.w, v.x, v.y, v.z, w.x, w.y, w.z)
    require(all(math.isfinite(x) for x in values), "Non-finite model state.")
    require(abs(q.x*q.x + q.y*q.y + q.z*q.z + q.w*q.w - 1) < 0.01,
            "Invalid model orientation quaternion.")
    yaw = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
    return {"world_xyz_m": [p.x, p.y, p.z], "yaw_rad": yaw,
            "planar_speed_mps": math.hypot(v.x, v.y), "yaw_rate_radps": w.z}


def stationary(snapshot):
    return (set(snapshot["wheel_rates_radps"]) == set(WHEELS)
            and all(abs(v) < 0.15 for v in snapshot["wheel_rates_radps"].values())
            and snapshot["model"]["planar_speed_mps"] < 0.01
            and abs(snapshot["model"]["yaw_rate_radps"]) < 0.05)


def run_pulse(publisher, twist_type, shutdown, read_snapshot, guard,
              duration=TURN_WALL_SECONDS, zero_seconds=ZERO_WALL_SECONDS,
              wall=time.monotonic, sleep=time.sleep):
    """Main thread only publishes; all service/graph reads stay in a daemon worker."""
    cancel, abort = threading.Event(), threading.Event()
    samples, errors = [], []
    started = wall()
    deadline = started + duration
    turn, zero = twist_type(), twist_type()
    turn.angular.z = TURN_RADPS
    sent, zero_sent = 0, 0

    def observe():
        while not cancel.wait(0.7):
            try:
                guard()
                begin = wall()
                snapshot = read_snapshot()
                end = wall()
                if end >= deadline or cancel.is_set():
                    return
                samples.append({"wall_start_s": begin-started, "wall_end_s": end-started,
                                **snapshot})
            except Exception as error:
                errors.append("Observation aborted: " + str(error))
                abort.set()
                return

    observer = threading.Thread(target=observe, daemon=True)
    try:
        observer.start()
        while wall() < deadline and not abort.is_set() and not shutdown():
            publisher.publish(turn)
            sent += 1
            sleep(min(0.05, max(0, deadline-wall())))
    except KeyboardInterrupt:
        errors.append("Ctrl+C: turn pulse interrupted; sending zero velocity.")
    except Exception as error:
        errors.append("Publishing aborted: " + str(error))
    finally:
        turn_ended = wall()
        cancel.set()
        stop_until = wall() + zero_seconds
        while wall() < stop_until:
            try:
                publisher.publish(zero)
                zero_sent += 1
            except Exception as error:
                if not errors or not errors[-1].startswith("Zero publish failed"):
                    errors.append("Zero publish failed: " + str(error))
            sleep(min(0.05, max(0, stop_until-wall())))
        if observer.ident is not None:
            observer.join(timeout=0.05)
    return {"turn_wall_seconds_observed": round(turn_ended-started, 4),
            "turn_messages_sent": sent, "zero_messages_sent": zero_sent,
            "moving_samples": list(samples), "errors": list(errors)}


def summarize(before, after, pulse):
    samples = pulse["moving_samples"]
    medians = {name: (statistics.median(s["wheel_rates_radps"][name] for s in samples)
                      if samples else None) for name in WHEELS}
    dx, dy = (after["model"]["world_xyz_m"][i] - before["model"]["world_xyz_m"][i]
              for i in (0, 1))
    yaw = before["model"]["yaw_rad"]
    heading_change = after["model"]["yaw_rad"] - yaw
    heading_change = math.atan2(math.sin(heading_change), math.cos(heading_change))
    signs_ok = bool(samples) and all(
        medians[name] * (1 if target > 0 else -1) > 0.1
        for name, target in IDEAL_TARGETS.items())
    return {"moving_sample_count": len(samples), "wheel_rate_medians_radps": medians,
            "wheel_directions_match_right_turn": signs_ok,
            "planar_displacement_m": math.hypot(dx, dy),
            "forward_displacement_m": math.cos(yaw)*dx + math.sin(yaw)*dy,
            "lateral_displacement_m": -math.sin(yaw)*dx + math.cos(yaw)*dy,
            "yaw_change_rad": heading_change,
            "yaw_change_deg": math.degrees(heading_change),
            "negative_yaw_change_observed": heading_change < -0.02,
            "body_yaw_rate_median_radps": (statistics.median(
                s["model"]["yaw_rate_radps"] for s in samples) if samples else None),
            "after_zero_stationary_sample": stationary(after),
            "threshold_note": "Stationary sample: each wheel |rate|<0.15 rad/s, planar speed<0.01 m/s, |yaw rate|<0.05 rad/s. Not long-term stability proof.",
            "simultaneous_joint_measurement": False,
            "scope_note": "One right-turn command in the current B configuration only; not a new controlled A/B pair and not a return-to-start controller. Actual yaw depends on skid/contact physics.",
            "repeatability_or_reset_verified": False}


def main():
    # Runtime-only imports keep offline helper tests independent of ROS installation.
    import rospy
    import rosgraph
    from geometry_msgs.msg import Twist
    from gazebo_msgs.srv import (GetJointProperties, GetModelState,
                                 GetModelProperties, GetPhysicsProperties)

    # Leave Python SIGINT handling enabled so Ctrl+C reaches run_pulse's finally
    # before unregistering the publisher. Do not press Ctrl+C repeatedly.
    rospy.init_node("lesson14_4wd_right_step11g", anonymous=True, disable_signals=True)
    master = rosgraph.Master(rospy.get_name())
    publisher, pulse = None, None
    report = {"model": MODEL, "command_topic": "/cmd_vel", "requested_linear_mps": 0.0,
              "requested_angular_radps": TURN_RADPS, "requested_turn_wall_seconds": TURN_WALL_SECONDS,
              "ideal_wheel_targets_radps": dict(IDEAL_TARGETS), "motion_attempted": False}
    try:
        graph_guard(master, rospy.get_name())
        props = call_wall("model properties", rospy.ServiceProxy(
            "/gazebo/get_model_properties", GetModelProperties), MODEL)
        require(props.success and not props.is_static, "Target model missing or static.")
        require(set(WHEELS).issubset(set(props.joint_names)), "Four target wheel joints not found.")
        physics = call_wall("physics properties", rospy.ServiceProxy(
            "/gazebo/get_physics_properties", GetPhysicsProperties))
        require(physics.success and not physics.pause, "Gazebo physics is paused or unavailable.")
        def snapshot():
            # Separate proxies per snapshot also isolate any timed-out read
            # that might still be finishing in its daemon thread.
            return {"wheel_rates_radps": joint_rates(rospy.ServiceProxy(
                        "/gazebo/get_joint_properties", GetJointProperties)),
                    "model": model_state(rospy.ServiceProxy(
                        "/gazebo/get_model_state", GetModelState))}

        before = snapshot()
        require(stationary(before), "Model is not stationary before test; no motion command sent.")
        publisher = rospy.Publisher("/cmd_vel", Twist, queue_size=1, latch=False)
        connection_deadline = time.monotonic() + 5.0
        while publisher.get_num_connections() == 0 and time.monotonic() < connection_deadline:
            time.sleep(0.05)
        require(publisher.get_num_connections() > 0, "No velocity subscriber connection.")
        graph_guard(master, rospy.get_name())
        print("RIGHT TURN TEST: linear=0, angular.z=-0.20 rad/s for about 3 WALL seconds, then 2 seconds of zeros. Watch Gazebo.", flush=True)
        report["motion_attempted"] = True
        pulse = run_pulse(publisher, Twist, rospy.is_shutdown, snapshot,
                          lambda: graph_guard(master, rospy.get_name()))
        report.update(pulse)
        after = snapshot()
        report.update({"before": before, "after_zero": after})
        report.update(summarize(before, after, pulse))
        graph_guard(master, rospy.get_name())
        print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
        print("TEST_RECORDED: confirm visually that the car turned right and stopped; send output even if it did NOT turn.", flush=True)
        good = (not pulse["errors"] and pulse["zero_messages_sent"] > 0
                and report["wheel_directions_match_right_turn"]
                and report["negative_yaw_change_observed"]
                and report["planar_displacement_m"] < 0.05
                and report["after_zero_stationary_sample"])
        return 0 if good else 2
    except (Exception, KeyboardInterrupt) as error:
        report["error"] = str(error) or type(error).__name__
        if pulse is not None:
            report.update(pulse)
        print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)
        print("TEST_INCOMPLETE: do not repeat or increase speed; check whether the car is stopped.", flush=True)
        return 1
    finally:
        if publisher is not None:
            publisher.unregister()


if __name__ == "__main__":
    sys.exit(main())
