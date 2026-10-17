# Step 11H — 四轮真实关节状态与连杆 TF（先做文件预检）

## 当前依据与边界

用户提供的 B/cone 四轮检查：40.048 秒墙钟窗口，根 TF 3995 条、odom 3995 条、clock 39953 条；均仅由 `/gazebo` 发布，重复、倒退、同时间戳位姿变化计数全部为零。模拟时间推进 39.958 秒，最大观测 clock 接收间隙 0.0075 秒；诊断与 tee 均退出 0。

这证明**该次静止窗口没有观察到根 TF/odom 时间戳异常**，不是任意时长、运动状态或传感器负载下的全面证明。四轮前进、左右转向及停车的既有记录保留；本步不再发送运动指令。

## 这一步做什么

只新增四个文件，不覆盖旧文件、不重编译驱动、不改轮距/轮径/质量/惯量/摩擦/扭矩：

- `urdf/gazebo/myrobot_4wd_tf_step11h.xacro`：包含原 step11C，新增一个 Gazebo 真实关节状态插件。
- `launch/myrobot_4wd_tf_step11h.launch`：同一机器人、原出生姿态及 B/cone 世界，新增一个 `robot_state_publisher`。
- `scripts/check_4wd_tf_step11h.py`：离线、只读的 URDF/launch/已有文件哈希/库依赖检查。
- 本说明。

本 ZIP 不是完整机器人包；依赖已经安装到 `rcdp` 的 step11A、11C、11F 和已编译的 `rcdp_4wd_stampfix`，不要解压到 `src` 根目录或额外创建嵌套 rcdp。

## 为什么需要这一步

当前四轮驱动负责四个电机、`/odom` 和 `odom -> root_link`，**不发布关节状态**。`robot_state_publisher` 需要真实关节角度，才能产生轮子、摄像头座、雷达座等相对于车体的坐标变换。只读的 Gazebo 关节状态插件不会驱动电机或锁住两个传感器转轴。

数据链：

```text
Gazebo 六个实际关节
    -> /joint_states（一个 Gazebo 插件，配置 50 Hz 模拟时间）
    -> 一个 robot_state_publisher
    -> /tf（六个活动关节）及 /tf_static（三个固定关节）

原四轮驱动 -> /odom + odom -> root_link（仍然只有它负责根变换）
```

六个名称必须是：

```text
front_left_wheel_joint
front_right_wheel_joint
rear_left_wheel_joint
rear_right_wheel_joint
depth_camera_link2base_link
laser_scan_link2platform_link
```

不能复制旧 step8 中已删除的 `front_support_wheel_link2_base_link`、`back_support_wheel_link2_base_link`。本步不运行用于虚拟关节角度的 `joint_state_publisher`/GUI 节点，也不额外广播根 TF。

插件参数与真实测量行为已对照 [gazebo_ros_pkgs 2.9.3 官方源文件](https://github.com/ros-simulation/gazebo_ros_pkgs/blob/2.9.3/gazebo_plugins/src/gazebo_ros_joint_state_publisher.cpp) 核对。`jointName` 是逗号分隔的实际 Gazebo 关节名；`robotNamespace` 显式为 `/`，用于全局 `/joint_states`，避免默认进入模型命名空间。插件配置 50 Hz 不是已测频率：实际墙钟频率随实时率变化。

注意：这个标准插件仍使用 `ros::Time::now()` 给关节消息打时间戳，不能假定新增关节 TF 已自动获得自定义驱动的时间戳修复。后续必须单独检查 `/joint_states` 与各条连杆 TF；根 TF 的既有检查不覆盖这些新边。

## 当前只做：导入、展开、预检

把 ZIP 复制到 Ubuntu `/home/thl/Lesson14_4wd_tf_step11h.zip`，在**新终端**执行，每条成功后再做下一条。当前 B 组 Gazebo 保持运行。

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_tf_step11h.zip -d /home/thl/catkin_ws/src/rcdp

rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_4wd_drive_step11c.xacro -o /tmp/lesson14_step11h_baseline.urdf

rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_4wd_tf_step11h.xacro -o /tmp/lesson14_4wd_tf_step11h.urdf

python3 /home/thl/catkin_ws/src/rcdp/scripts/check_4wd_tf_step11h.py /tmp/lesson14_step11h_baseline.urdf /tmp/lesson14_4wd_tf_step11h.urdf
```

若任一步报错立即停下，发送完整输出。预期最后 `PRECHECK_OK`。脚本校验已知的 Linux 工作区路径、原模型/世界 SHA256、两种插件数量、六个关节名称，以及新增库的 `ldd`；会读已有文件，但不会连接 ROS、发速度或重启 Gazebo。驱动库哈希与上一检查点不同会返回 2，请先反馈，不直接启动。

**现在不要启动新 launch，也不要关闭当前 Gazebo。** 文件预检不等于原生 Gazebo 装载成功或运行期 TF 合格。

## 预检通过后的下一阶段（尚未执行）

在后续指导下正常 Ctrl+C 关闭现有 Gazebo launch，等其退出，核对没有残留服务器和端口占用后，再启动新 launch。启动会重建场景，不保留本次已经移动后的位姿。新文件默认 B/cone，旧 11F 默认值与文件完全不变。

启动后需要验证：

1. `/joint_states` 只有 `/gazebo` 一个实际发布者，六个关节各出现一次，position/velocity 有限且长度正确。
2. `lesson14_4wd_robot_state_publisher` 订阅 `/joint_states`；固定与活动 TF 形成一棵树，可查询 `odom -> laser_scan_link` 和所有轮子。
3. `odom -> root_link` 仍只有驱动负责，并复测时间戳；新活动关节 TF 也检查重复/倒退/发布归属。
4. 此后再分步恢复激光、深度相机及轻量 RViz。

本步没有 `/scan`、图像、点云、光学帧 `rotate_depth_camera_link` 或 RViz，属于刻意分步恢复，不是遗漏。先不加载曾造成崩溃的 640×480 原始点云。

## 回退与验证边界

旧 11A/11C/11F、两个世界及驱动源码/二进制都不改。将来回退也应先正常结束新 launch，再使用原 11F 并显式指定 `friction_model:=cone_model`；不要两个 Gazebo 同时启动。

主机离线检查只覆盖 Xacro 展开、XML 差异约束、负例和 ZIP 完整性。主机没有 ROS/Gazebo，未声称在 VM 编译或加载成功。GitHub 上传保持暂停，本步没有提交或推送。
