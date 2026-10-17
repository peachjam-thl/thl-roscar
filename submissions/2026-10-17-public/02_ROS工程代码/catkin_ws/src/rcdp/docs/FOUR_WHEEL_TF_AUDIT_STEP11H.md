# Step11H 运行期只读验收：六个关节与整棵 TF

## 用户已经证实的内容

- `/joint_states` 的实际发布者为 `/gazebo`，订阅者包含 `/lesson14_4wd_robot_state_publisher`。
- 单条消息含四个新车轮关节和两个传感器转轴关节，position 与 velocity 各六项，数值有限；effort 为空被允许，header.frame_id 为空不影响本检查。
- `tf_echo odom laser_scan_link` 首次查询出现缓存时间范围不足（43.309 s 请求，缓存最早仅 43.310 s），随后 44.290–49.309 s 连续返回变换。
- 这与查询工具刚建立自己的 TF 缓冲时数据尚不足的表现相符，不是 `TF_REPEATED_DATA`，也不是持续断树的证据。若运行中持续出现或反复复现，仍需另查时序。
- 雷达座平移约 `[0.200, 0, 0.889]`，是当前车体与雷达座 TF 的结果；不表示 `/scan` 已恢复。

## 为什么不是直接运行旧诊断

旧 `diagnose_tf_stamps_step10.py` 只检查 `odom -> root_link`，不覆盖新出现的六条活动关节 TF。本脚本在同一个 40 秒墙钟窗口被动订阅 `/tf`、`/tf_static`、`/joint_states`、`/odom`、`/clock`。

预期动态边共七条：

```text
/gazebo: odom -> root_link

/lesson14_4wd_robot_state_publisher:
  base_link -> front_left_wheel_link
  base_link -> front_right_wheel_link
  base_link -> rear_left_wheel_link
  base_link -> rear_right_wheel_link
  base_link -> depth_camera_link
  platform_link -> laser_scan_link
```

预期三条 `/tf_static` 固定边均由同一个 robot_state_publisher 产生：

```text
root_link -> base_link
base_link -> support_link
support_link -> platform_link
```

脚本按“每条边、每个关节、每个来源”统计，避免将不同关节共享同一个合法时间戳误判为重复。会核对来源与边、关节数组布局、有限数值、近似单位四元数、同一动态流的重复/倒退、同来源同时间戳载荷变化；固定 TF 的正常锁存重放不按动态时间戳重复处理。

`effort` 可为空；当前已安装的 Gazebo 插件确实提供速度，所以这个特定验收要求 position、velocity 均为六项。它不是针对所有 ROS JointState 发布器的通用协议校验器。

## 操作

ZIP 只新增脚本和本说明，不覆盖当前启动文件。复制到 Ubuntu `/home/thl/Lesson14_4wd_tf_audit_step11h.zip` 后执行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_tf_audit_step11h.zip -d /home/thl/catkin_ws/src/rcdp
```

在新终端创建独立日志目录，然后执行下列条件块。当前 step11H Gazebo 保持运行，期间不移动车辆、不重置世界、不另起 launch。不需要编译。

```bash
step11h_audit_dir=$(mktemp -d /home/thl/ros_course_logs/step11h_tf_audit_XXXXXX)
printf '本次检查目录：%s\n' "$step11h_audit_dir"

if [ ! -d "$step11h_audit_dir" ]; then
    printf '日志目录创建失败，未执行检查。\n'
elif [ ! -f /home/thl/catkin_ws/src/rcdp/scripts/diagnose_4wd_tf_step11h.py ]; then
    printf '检查脚本不存在，未执行检查。\n'
elif [ -e "$step11h_audit_dir/tf_audit.log" ]; then
    printf '日志已存在，不覆盖，请反馈现有结果。\n'
else
    timeout -s INT 55s python3 -u /home/thl/catkin_ws/src/rcdp/scripts/diagnose_4wd_tf_step11h.py 2>&1 | tee -i "$step11h_audit_dir/tf_audit.log"
    step11h_audit_status=("${PIPESTATUS[@]}")
    printf 'audit_exit=%s tee_exit=%s\n' "${step11h_audit_status[0]}" "${step11h_audit_status[1]}"
fi
```

## 解释结果

`WINDOW_OK`、`completed_window: true`、`issues: []`、`audit_exit=0 tee_exit=0` 是本次被动接收窗口的合格结果。必须看完整结果，不能仅看 tee 退出码。

退出 2 / REVIEW_REQUIRED：收集到了需审查的问题或窗口未完成，发送完整输出，不自行改参数屏蔽警告。退出 1：脚本运行错误。timeout 退出 124 说明超过外部时间上限，并不是合格结果。

本检查不发送速度，不提供电机控制、加速限制或超时停车保护；运行时仅新增临时 ROS 订阅节点，不修改机器人参数/驱动/仿真场景。没有证明持续任意时长、运动中、传感器负载下无异常；没有检验所有查询时刻均可进行 TF 插值，也没有证明 ROS 传输从不丢包。接收间隙只表示本观察者所见，不能当 Gazebo 内部调度证据。

如果新增的关节时间戳有重复，先定位到具体关节、具体 TF 边及发布源。标准 Gazebo 关节状态插件的消息时间来源与自定义四轮驱动不同，根 TF 通过不等于其他边通过；没有在本步预先修改它。

原始驱动、模型、world 和旧诊断脚本均保留；GitHub 上传仍暂停。

## 官方定义核对

- [Noetic JointState 消息定义](https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/msg/JointState.msg)：状态数组允许为空，非空时长度应一致。
- [Noetic TF2 时间缓存实现](https://github.com/ros/geometry2/blob/noetic-devel/tf2/src/cache.cpp)：仅缓存一个采样且查询时间不同，会产生这里看到的 only-time-in-buffer 外推异常；同时间戳重复插入是另一种独立诊断。
