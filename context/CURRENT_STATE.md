# 当前状态：先读此文件

截止 2026-10-15，本轮 ROS 实践已达成“原始 Lesson13 模型在 Gazebo 显示，并能通过差速插件低速前进、停止”。

## 现场环境（用户逐项提供）

| 项目 | 已知值 |
| --- | --- |
| 用户 / 主机提示符 | `thl@ubuntu` |
| 系统 | Ubuntu 20.04.6 LTS |
| ROS | ROS 1 Noetic；运行日志 roslaunch/rosversion 为 1.17.4 |
| 仿真 | Gazebo Classic 11.15.1，VMware 虚拟机 |
| ROS 安装 | `/opt/ros/noetic` |
| 现有工作空间 | `/home/thl/catkin_ws` |
| 当前功能包 | `/home/thl/catkin_ws/src/rcdp` |
| 原始解压位置 | `/home/thl/Lesson13_code/catkin_ws/src/rcdp`（不是当前 active 包） |
| 模型名 | `lesson13_robot` |
| 当前驱动 launch | `myrobot_drive_step6.launch` |
| 当前驱动 Xacro | `urdf/gazebo/myrobot_drive_step6.xacro`，相对包含第四步模型 |
| 本地 world | `worlds/lesson13_flat_step4.world` |
| 速度 / 里程计 | `/cmd_vel` / `/odom` |

## 已验证证据

1. 用户 `catkin_make` 成功，输出包含 `rcdp_xacro_generated_to_devel_space_`；已有 `robot_course_pkg` 消息目标也成功。
2. `rospack find rcdp` → `/home/thl/catkin_ws/src/rcdp`。
3. Gazebo 截图显示双层圆柱小车；`get_model_properties` 返回 `success: True`、`is_static: False`。
4. 左右驱动轮关节 `base_l_wheel_joint`、`base_r_wheel_joint` 确认存在。
5. 插件库 `/opt/ros/noetic/lib/libgazebo_ros_diff_drive.so` 确认存在。
6. `/cmd_vel` 类型是 `geometry_msgs/Twist`，订阅者包含 `/gazebo`。测试前 `Publishers: None` 正常，不代表插件未加载。
7. 用户执行 `python3 /home/thl/catkin_ws/src/rcdp/scripts/test_forward_step6.py`，日志显示请求前进、发送零速度；明确反馈“向前移动且停止”。

以上是用户现场证据，不是助手直接访问 VM。速度／位移／制动时间未独立量化，不能说严格走了 0.3 m。Windows 静态 XML/Xacro/Python 检查另存 `evidence/step4`、`evidence/step6`。

## 当前模型与控制配置

- 10 links、9 joints 的 URDF 树；Gazebo 固定关节合并后 `body_names` 为 7 项是正常现象。
- `root_link` 是参考根；底盘、立柱、二层平台通过固定关节连接，碰撞几何仍存在。
- 驱动轮半径 0.1 m、轮宽 0.08 m；轮距 0.8 m。
- 仅一个 `libgazebo_ros_diff_drive.so` 插件，100 Hz，轮加速度上限 0.3 m/s²，轮扭矩 5 Nm。
- odometrySource 为 `world`（仿真真值，不是已验证的真实轮编码器）。TF 配置为 `odom → root_link`。
- `publishWheelJointState=true` 只涉及两个驱动轮；完整关节状态和整棵 TF 树尚未形成已验收链路。
- `publishWheelTF=false`，未来加入 robot_state_publisher 时要避免重复 TF 发布者。
- 摄像头／雷达目前是模型中的几何零件，不能仅凭外形断言会发布图像、深度或 scan。

## 尚未完成／不允许写成已完成

- 键盘遥控验收，旋转／转弯测试，速度／距离量化。
- 相机／深度／激光传感器插件、话题与数据验证。
- 完整 robot_state_publisher、全部关节状态、RViz 联动与 TF 验证。
- SLAM、地图保存、AMCL、move_base 导航。
- APT/DNS 修复和 `check_urdf` 安装（当时下载失败，检查器不是跑 Gazebo 的硬性前提）。
- VM 全工程备份；`robot_course_pkg` 的现场完整源文件未读回。

## 下一次不要误判

当前机器人仿真是否还在运行未知，需按需检查，不能根据旧日志推断仍在线。Gazebo 端口占用的 PID 必须重新确认。先保留成功配置，按用户选择继续一个阶段。
