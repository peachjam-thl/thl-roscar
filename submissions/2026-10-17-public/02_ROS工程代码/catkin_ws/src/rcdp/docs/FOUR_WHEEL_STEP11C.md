# 四轮车 Step11C：将已编译的四电机插件接入模型

客户端记录日期：2026-10-17。目标：Ubuntu 20.04 / ROS Noetic / Gazebo Classic 11，用户 thl。

## 已确认与尚未确认

- Step11A：用户已成功加载四个普通轮子的物理模型，Gazebo 查询列出了四个新轮关节。
- Step11B：用户已成功编译链接 `rcdp_4wd_stampfix`，目标库为 `/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so`。
- 本包：只增加驱动顶层 Xacro、独立 launch、只读预检脚本和本文档；不覆盖旧文件或系统库。
- 尚未确认：新库在 Gazebo 中实际加载、四轮都受驱动、直行/转向/停车、运行中的时间戳、重置行为。
- GitHub 上传暂停。本阶段不提交或上传任何内容。

## 文件与依赖

将 ZIP 解压到 `/home/thl/catkin_ws/src/rcdp`，不是 `/home/thl/catkin_ws/src`。

```text
urdf/gazebo/myrobot_4wd_drive_step11c.xacro
launch/myrobot_4wd_drive_step11c.launch
scripts/check_4wd_drive_step11c.py
docs/FOUR_WHEEL_STEP11C.md
```

必须保留已导入的以下文件：

- `/home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_4wd_base_step11a.xacro`
- `/home/thl/catkin_ws/src/rcdp/worlds/lesson14_box_house_step7.world`
- `/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so`

插件库路径按用户现有工作空间明确指定；移植到其他用户/目录时，须同步修改 Xacro 和预检脚本中的路径。
ZIP 内时间设为 2020-01-01，只是避免宿主机/虚拟机时差造成未来文件时间警告，不代表代码编写时间。

## 当前只做预检：不关闭、不切换当前 Gazebo

先将 ZIP 下载并复制到虚拟机 `/home/thl/Lesson14_4wd_drive_step11c.zip`。在新终端逐条运行；任何命令报错就停下并反馈。

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_drive_step11c.zip -d /home/thl/catkin_ws/src/rcdp
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_4wd_base_step11a.xacro -o /tmp/lesson14_step11c_base.urdf
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_4wd_drive_step11c.xacro -o /tmp/lesson14_4wd_drive_step11c.urdf
python3 /home/thl/catkin_ws/src/rcdp/scripts/check_4wd_drive_step11c.py /tmp/lesson14_step11c_base.urdf /tmp/lesson14_4wd_drive_step11c.urdf
```

预期末行：`PRECHECK_OK: files/dependencies only; Gazebo has NOT been switched.`

脚本只解析文件、读取库文件并对用户刚编译的库调用 `ldd` 检查依赖；不连接 ROS、不修改参数、不启动/关闭 Gazebo、不发送速度。
`dynamic_dependencies_resolved: true` 不等于已在 Gazebo 中加载成功。
本包不修改 C++ 源码；这里只展开 Xacro、检查文件，无需为本包重新编译。

## 本次控制配置

四个轮关节分别绑定 `leftFrontJoint`、`rightFrontJoint`、`leftRearJoint`、`rightRearJoint`。
不通过齿轮或 mimic 间接拖动后轮，而是由插件对四个关节分别设置速度目标。

| 项目 | 设置 |
|---|---|
| 左前 / 右前 | `front_left_wheel_joint` / `front_right_wheel_joint` |
| 左后 / 右后 | `rear_left_wheel_joint` / `rear_right_wheel_joint` |
| 左右轮距 `wheelSeparation` | 0.72 m，左右轮中心距离 |
| 前后轴距 | 0.40 m，在物理模型里定义，不是 wheelSeparation |
| 轮径 `wheelDiameter` | 0.20 m，不能写成半径 0.10 m |
| 每轮力矩上限 `torque` | 5 N·m，初始教学配置，未做转向调参 |
| 控制更新 `updateRate` | 100 Hz 仿真时间；实测墙钟频率可能更低 |
| 输入 / 输出 | `/cmd_vel` / `/odom` |
| TF | `broadcastTF=true`，`odom -> root_link` |
| 命名空间 | 不写 robotNamespace，使用插件默认空命名空间；本 launch 无命名空间 |

不复制原两轮插件的 `leftJoint`、`rightJoint`、`wheelTorque`、`wheelAcceleration`、`publishOdomTF`、`publishWheelTF` 或 `odometrySource`，因为这个四轮插件不读取这些参数。

X 向前、Y 向左、Z 向上，四个轮关节轴均为 +Y。理想目标关系为：

```text
左前 = 左后 = (linear.x - angular.z * 0.72 / 2) / 0.10  [rad/s]
右前 = 右后 = (linear.x + angular.z * 0.72 / 2) / 0.10  [rad/s]
```

这是目标角速度，不是对实际接触/转向效果的证明。四轮滑移转向受轮胎摩擦与地面接触影响；验证直行后，再根据实际表现调整。

## 重要边界

- 本阶段仍然没有 `/scan`、RGB、深度/点云插件，也不启动 RViz 或 robot_state_publisher；这是有意隔离驱动测试，不是传感器丢失。
- 本插件发布根 TF 和里程计，不发布轮子 `/joint_states`；后续恢复传感器时需要额外接入正确的六关节状态发布。
- `/odom` 使用 Gazebo 世界位姿真值，不是轮编码器积分，不应当描述为已验证的编码器里程计。
- 插件没有速度加速斜坡，也没有命令超时自动停车；最后一条速度会持续保留。后续测试必须低速、限定时长，最后显式发送零速度并观察停车。
- 新插件保留从仿真时刻直接生成 TF/里程计时间戳的修复，但新四轮版本仍需重新做运行验收；两轮版本通过不等于四轮已经通过。
- 预检通过后再正常关闭当前模型版 launch，确认旧 Gazebo 退出，然后单独启动本包 launch；不能同时启动两套 Gazebo。
- 本文不让你现在执行 launch 或运动命令。先把完整预检输出发回，再进行下一步切换。

## 后续验收顺序

文件预检 → 正常切换 Gazebo → 核对实际加载的新库与四关节 → 低速直行/显式停车 → 四轮速度证据与转向 → 时间戳复验 → 恢复关节状态、TF、雷达、相机和轻量 RViz。

当前只能确认用户报告的模型载入和插件编译；其余保持待验收。
