#!/usr/bin/env python3
"""ROS1 display-only point-cloud preview; never changes TF or robot controls.

Raw data stays on /kinect/depth/points. The separate preview keeps each selected
point's complete byte record, acquisition stamp, and original coordinate frame.
No ROS imports are needed when importing this module for offline unit tests.
"""
import copy
import math
import sys
import threading
import time

RAW_TOPIC = "/kinect/depth/points"
PREVIEW_TOPIC = "/lesson14/depth_points_preview"
EXPECTED_FRAME = "rotate_depth_camera_link"
# sensor_msgs/PointField datatype enum -> number of bytes per component.
FIELD_BYTES = {1: 1, 2: 1, 3: 2, 4: 2, 5: 4, 6: 4, 7: 4, 8: 8}


def validate_parameters(stride, rate_hz):
    if isinstance(stride, bool) or not isinstance(stride, int) or stride < 4:
        raise ValueError("stride must be an integer >= 4 (default 8)")
    if isinstance(rate_hz, bool):
        raise ValueError("rate_hz must be a number in (0, 2]")
    rate_hz = float(rate_hz)
    if not math.isfinite(rate_hz) or not 0.0 < rate_hz <= 2.0:
        raise ValueError("rate_hz must be in (0, 2] wall-clock Hz")
    return stride, rate_hz


def decimate_bytes(width, height, point_step, row_step, data, stride):
    """Keep rows/columns 0, stride, 2*stride, ... without decoding XYZ/RGB."""
    if any(isinstance(v, bool) or not isinstance(v, int) or v <= 0
           for v in (width, height, point_step, row_step, stride)):
        raise ValueError("cloud layout and stride must be positive integers")
    if row_step < width * point_step:
        raise ValueError("row_step is shorter than a complete point row")
    source = memoryview(data).cast("B")
    if source.nbytes != row_step * height:
        raise ValueError("data byte count does not match row_step * height")
    out_width = (width + stride - 1) // stride
    out_height = (height + stride - 1) // stride
    target = bytearray(out_width * out_height * point_step)
    cursor = 0
    for v in range(0, height, stride):
        row_start = v * row_step
        for u in range(0, width, stride):
            start = row_start + u * point_step
            target[cursor:cursor + point_step] = source[start:start + point_step]
            cursor += point_step
    return out_width, out_height, bytes(target)


def make_preview(cloud, cloud_type, stride):
    fields = {field.name: field for field in cloud.fields}
    if len(fields) != len(cloud.fields) or not {"x", "y", "z"}.issubset(fields):
        raise ValueError("expected distinct fields including x, y, z")
    for field in cloud.fields:
        size = FIELD_BYTES.get(field.datatype)
        if (size is None or field.count <= 0 or field.offset < 0
                or field.offset + size * field.count > cloud.point_step):
            raise ValueError("invalid field layout: " + field.name)
    if any(fields[name].datatype != 7 or fields[name].count != 1
           for name in ("x", "y", "z")):
        raise ValueError("this lesson preview expects FLOAT32 XYZ fields")
    xyz_offsets = [fields[name].offset for name in ("x", "y", "z")]
    if any(abs(a - b) < 4 for i, a in enumerate(xyz_offsets)
           for b in xyz_offsets[i + 1:]):
        raise ValueError("XYZ fields overlap")
    width, height, data = decimate_bytes(
        cloud.width, cloud.height, cloud.point_step,
        cloud.row_step, cloud.data, stride
    )
    result = cloud_type()
    result.header = copy.copy(cloud.header)
    result.width, result.height = width, height
    result.fields = copy.deepcopy(cloud.fields)
    result.is_bigendian = cloud.is_bigendian
    result.point_step = cloud.point_step
    result.row_step = width * cloud.point_step
    result.data = data
    result.is_dense = cloud.is_dense
    return result


class PublishGate:
    """Wall-clock upper rate bound; never fabricate a sensor timestamp."""
    def __init__(self, rate_hz):
        self.period = 1.0 / rate_hz
        self.next_wall_time = float("-inf")
        self.last_stamp = None

    def allow(self, now, stamp):
        if now < self.next_wall_time or stamp == self.last_stamp:
            return False
        self.next_wall_time = now + self.period
        self.last_stamp = stamp
        return True


class PreviewRelay:
    def __init__(self, ros, cloud_type, stride, rate_hz):
        self.ros, self.cloud_type = ros, cloud_type
        self.stride, self.rate_hz = stride, rate_hz
        self.gate = PublishGate(rate_hz)
        self.lock = threading.Lock()
        self.stopping = False
        self.first_reported = False
        self.subscriber = None
        self.publisher = ros.Publisher(
            PREVIEW_TOPIC, cloud_type, queue_size=1, latch=False
        )

    def callback(self, message):
        if self.stopping or self.ros.is_shutdown():
            return
        if self.publisher.get_num_connections() == 0:
            return
        stamp = (message.header.stamp.secs, message.header.stamp.nsecs)
        with self.lock:
            if not self.gate.allow(time.monotonic(), stamp):
                return
            try:
                if message.header.frame_id.lstrip("/") != EXPECTED_FRAME:
                    raise ValueError("unexpected source frame: " + message.header.frame_id)
                preview = make_preview(message, self.cloud_type, self.stride)
                if self.stopping or self.ros.is_shutdown():
                    return
                self.publisher.publish(preview)
                if not self.first_reported:
                    self.ros.loginfo(
                        "Preview: %dx%d -> %dx%d (%d points); stamp/frame unchanged.",
                        message.width, message.height, preview.width, preview.height,
                        preview.width * preview.height
                    )
                    self.first_reported = True
            except (ValueError, TypeError, BufferError, self.ros.ROSException) as exc:
                if not self.stopping and not self.ros.is_shutdown():
                    self.ros.logwarn_throttle(5.0, "Preview dropped a frame: %s", str(exc))

    def run(self):
        self.ros.loginfo(
            "Display-only preview ready: %s -> %s; stride=%d; at most %.1f wall Hz.",
            RAW_TOPIC, PREVIEW_TOPIC, self.stride, self.rate_hz
        )
        self.ros.loginfo("Waiting for a preview subscriber; robot controls/TF are untouched.")
        try:
            while not self.ros.is_shutdown():
                wanted = self.publisher.get_num_connections() > 0
                if wanted and self.subscriber is None:
                    self.subscriber = self.ros.Subscriber(
                        RAW_TOPIC, self.cloud_type, self.callback,
                        queue_size=1, buff_size=16 * 1024 * 1024
                    )
                elif not wanted and self.subscriber is not None:
                    self.subscriber.unregister()
                    self.subscriber = None
                time.sleep(0.2)
        finally:
            self.stopping = True
            if self.subscriber is not None:
                self.subscriber.unregister()


def main():
    import rospy
    from sensor_msgs.msg import PointCloud2

    rospy.init_node("lesson14_cloud_preview", anonymous=False)
    try:
        stride, rate_hz = validate_parameters(
            rospy.get_param("~stride", 8), rospy.get_param("~rate_hz", 2.0)
        )
    except (TypeError, ValueError) as exc:
        rospy.logerr("Invalid preview parameters: %s", str(exc))
        return 2
    try:
        PreviewRelay(rospy, PointCloud2, stride, rate_hz).run()
    except (rospy.ROSInterruptException, KeyboardInterrupt):
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
