# Step11D：四轮低速直行、轮速回读与显式停车

客户端日期：2026-10-17。仅适用于用户当前 Ubuntu/Noetic/Gazebo 四轮仿真，不用于真实硬件。

## 当前已确认

用户的 Step11C 预检通过；运行进程映射中出现 `/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so`；已收到 `/odom/header`，frame_id 为 odom。
用户反馈没有明显抖动/倾倒。本次仍未证明四轮运动、停车和转向。

本 ZIP 只增加测试脚本和本文档，不改变模型、launch、插件源码/库、物理参数，也不上传 GitHub。

## 执行前

1. 保持 `roslaunch rcdp myrobot_4wd_drive_step11c.launch` 运行，不再启动另一套 Gazebo。
2. 确认是仿真，不连接真实机器人；车前方至少留出 0.5 m 空间，Gazebo 处于播放状态。
3. 停止键盘遥控、旧运动脚本和 `rostopic pub /cmd_vel`，不要在测试中途启动其他速度源。
4. 执行 `rostopic info /cmd_vel`：测试前 Publishers 应为 None，Subscribers 应包含 /gazebo。不同则先反馈。

## 导入并运行一次

将 ZIP 放入虚拟机 `/home/thl/Lesson14_4wd_forward_step11d.zip`，新终端逐条执行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_forward_step11d.zip -d /home/thl/catkin_ws/src/rcdp
rostopic info /cmd_vel
```

确认无其他速度发布者后：

```bash
python3 -u /home/thl/catkin_ws/src/rcdp/scripts/test_4wd_forward_step11d.py
```

不用重新编译，不用重启 Gazebo。脚本会真的发送速度：前进 0.08 m/s，约 3 秒墙钟时间后连续发 2 秒零速度。
理论每轮目标角速度为 0.08/0.10 = 0.8 rad/s。实际距离取决于仿真时间进度、接触与响应，不要求恰好 0.24 m。

## 脚本做了什么

- 预先检查速度源、目标模型、四个轮关节、仿真未暂停，以及模型/轮子基本静止。
- 只向 `/cmd_vel` 发布直行和零速度；不转向、不改参数、不施力、不重置模型/仿真。
- 用墙钟计时，不使用会受仿真暂停影响的 rospy.sleep/Rate 控制测试时长。
- 在独立线程回读四个关节的实际速度和车体位姿，主发布循环不等待这些服务。每次只读 RPC 等待设墙钟上限。
- 测试末尾及一般异常/Ctrl+C 路径尝试连续发布零速度；这不等于断网、强制杀进程或系统崩溃时保证停车。
- 启动前及观察线程会检查其他速度发布者；这是采样检查，不是原子独占或硬件安全锁。
- 停车后再次读取实际轮速/模型速度；连续发零与实际停车是两件事，以回读及目视共同核对。

四个关节的查询使用 `lesson13_robot::关节名`，避免无模型前缀时与其他模型重名。查询是顺序读取，并非同一仿真时刻的同步测量。

Gazebo 官方 `GetJointProperties` 返回 rate；API 实现使用关节 GetVelocity(0)，本次轮关节为转动关节，因此单位 rad/s：

- https://github.com/ros-simulation/gazebo_ros_pkgs/blob/2.9.3/gazebo_msgs/srv/GetJointProperties.srv
- https://github.com/ros-simulation/gazebo_ros_pkgs/blob/2.9.3/gazebo_ros/src/gazebo_ros_api_plugin.cpp
- https://github.com/gazebosim/gazebo-classic/blob/gazebo11/gazebo/physics/Model.cc

## 怎么看结果

- `moving_sample_count`：运动窗口内成功完成的快照数量，通常会有多个；为 0 时不能认定四轮已回读通过。
- `wheel_rate_medians_radps`：四轮运动阶段的速度中位数，期望均为正且大致接近 0.8。
- `all_four_wheels_positive_in_samples`：四轮采样速度中位数均大于 0.1 rad/s；不是四轮扭矩或接地力证明。
- `forward_displacement_m`：相对初始车头方向的净前进位移，应为正。
- `lateral_displacement_m` / `yaw_change_rad`：供核对侧偏、偏航，不自动等同转向已验收。
- `zero_messages_sent`：零速度发送次数；大于 0 只能证明尝试发布，不单独证明车已停车。
- `after_zero_stationary_sample`：本次回读四轮绝对转速均小于 0.15 rad/s、平面速度小于 0.01 m/s、偏航速度绝对值小于 0.05 rad/s。属于这次采样的判据，不代表长期无漂移。
- `TEST_RECORDED` 不是总体验收通过；仍须发回完整输出和目视结果。有 error、运动采样缺失、轮子反向/不转、不能停车时，不要自行重试或提速。

轮子在代码中分别受到电机目标控制，加上四轮速度回读，可比单独观察车身移动提供更充分证据；仍不能从转速推导各轮实际输出扭矩或接地载荷。

## 异常处理

若运动异常，按一次 Ctrl+C，让脚本执行发零流程；不要连按、关闭该终端或强制终止 Python。
若车没有停止，立即用 Gazebo 窗口底部的暂停按钮暂停仿真，保持暂停并反馈；不要直接恢复运行。
可在另一终端明确发送一次全零指令（可能被其他速度源覆盖，因此不是独占安全机制）：

```bash
rostopic pub -1 /cmd_vel geometry_msgs/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'
```

任何服务/数据检查失败都会提示反馈，先保持现状，不删 build/devel、不改轮胎摩擦、不提高速度/扭矩。

本阶段不测试转向、相机/雷达、RViz、长时间稳定性、重置或四轮插件的运行时间戳；完成直行/停车验收后逐项继续。
