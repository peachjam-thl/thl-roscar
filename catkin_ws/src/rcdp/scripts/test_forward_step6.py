#!/usr/bin/env python3
"""Low-speed, finite-duration test for the Gazebo-only lesson13 robot.

Uses wall-clock waits so a paused /clock does not hang the test. Finally sends
zero velocity on normal completion and Ctrl+C. This is not a safety watchdog:
SIGKILL, power loss or an unresponsive transport can still prevent stopping.
"""
import time

import rospy
from geometry_msgs.msg import Twist


def stop_robot(publisher):
    zero = Twist()
    for _ in range(10):
        try:
            publisher.publish(zero)
        except rospy.ROSException:
            return
        time.sleep(0.05)


def main():
    # Keep Python's Ctrl+C handling: send zeros before shutting down ROS.
    rospy.init_node("lesson13_forward_test", anonymous=True, disable_signals=True)
    publisher = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
    try:
        deadline = time.monotonic() + 5.0
        while publisher.get_num_connections() == 0:
            if rospy.is_shutdown() or time.monotonic() >= deadline:
                raise RuntimeError("No /cmd_vel subscriber: check the Gazebo drive plugin.")
            time.sleep(0.05)

        command = Twist()
        command.linear.x = 0.1
        rospy.loginfo("Gazebo test: request forward 0.1 m/s for 3 wall-clock seconds.")
        deadline = time.monotonic() + 3.0
        while not rospy.is_shutdown() and time.monotonic() < deadline:
            publisher.publish(command)
            time.sleep(0.1)
    except KeyboardInterrupt:
        rospy.loginfo("Ctrl+C received; sending zero velocity.")
    except RuntimeError as exc:
        rospy.logerr(str(exc))
        return 1
    finally:
        stop_robot(publisher)
        rospy.loginfo("Zero velocity sent; verify that the robot has stopped.")
        rospy.signal_shutdown("test finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
