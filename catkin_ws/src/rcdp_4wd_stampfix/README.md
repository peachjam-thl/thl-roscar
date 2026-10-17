# 四轮左右差速插件：step11B（先编译，不切换）

日期：2026-10-17。用户已在 Gazebo 建立四轮实体模型，get_model_properties 确认四个轮关节存在且模型为动态实体。
未提供四轮接触力、长时间静置或转向运动验收，不能将“模型建立成功”扩展成“四驱运动已通过”。

## 本包做什么

这是独立包 `rcdp_4wd_stampfix`，基于官方 gazebo_plugins 2.9.3 的四轮 skid-steer 源码，
不是继续让两轮插件假装控制四个轮子。新共享库是：

```text
/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so
```

不覆盖旧 `rcdp_stampfix` 包、两轮库、step11A模型或 `/opt/ros`。本包没有 launch／Xacro，
只解压、检查和编译，不会替换正在运行的四轮实体模型，不发送速度、不上传 GitHub。

同侧前后轮使用同一侧线速度，四个实际关节分别设定角速度：

```text
v_left  = linear.x - angular.z * wheelSeparation / 2
v_right = linear.x + angular.z * wheelSeparation / 2
omega   = v_side / (wheelDiameter / 2)
```

这是理想差速指令换算，不是对实际滑移、转弯角度或里程计精度的实测保证。

## 相对上游的明确修改

- 独立库／类／头文件，保留 BSD 许可、原始源码、提交及 SHA256。
- odom 与根 TF 统一直接使用 Gazebo `World::SimTime()`，不回退到异步 ROS 时钟缓存。
- 补上 odom 的 Z 位置，与同次发布的完整世界位姿 TF 一致。
- 初始化 ROS 指针，工作线程标志改为 atomic；退出时先断开更新回调并正常停止／join线程，再释放 ROS 对象。
- 增加 Reset：清零本插件保留的命令及四轮目标，重置更新基准；若时间倒退触发同样处理。
- 物理重置可能清除电机 fmax，因此更新时恢复四个轮子的扭矩上限。

这些是源码层改动；未做 VM 编译／运行／reset 验收，不能把 Reset 实现当作已验证的安全停车机制。
插件仍没有命令超时停车，停止发布者不等于保证车停；后续运动必须显式发零并观察。

## 后续接入所需的参数（现在不启动）

| 标签 | 后续设定 |
| --- | --- |
| leftFrontJoint | front_left_wheel_joint |
| rightFrontJoint | front_right_wheel_joint |
| leftRearJoint | rear_left_wheel_joint |
| rightRearJoint | rear_right_wheel_joint |
| wheelSeparation | 0.72，左右轮距；不是前后轴距0.40 |
| wheelDiameter | 0.20 |
| torque | 5.0，每个驱动轮；不是原两轮插件的 wheelTorque 标签 |
| updateRate | 100 |
| commandTopic / odometryTopic | /cmd_vel / /odom |
| odometryFrame / robotBaseFrame | odom / root_link |
| broadcastTF | true，唯一 odom→root_link 发布者 |

本四轮插件**不读取**旧两轮插件的 wheelAcceleration、wheelTorque、publishOdomTF 或 publishWheelTF 标签。
它没有旧0.3m/s²斜坡；后续只从低速受控测试起步，不能说旧加速度限制已自动继承。
不发布轮关节状态；后续要用一个真实 Gazebo joint-state 插件覆盖四轮和两个传感器关节，再接一个 RSP。
不能包含旧 step8 的两个球支撑轮关节，也不能并行启动旧两轮驱动。

## 当前只导入、检查、编译

把 ZIP 放到 `/home/thl/Lesson14_4wd_plugin_step11b.zip`。
现有四轮模型的 Gazebo 保持运行，另开终端。先检查新目录不存在：

```bash
test ! -e /home/thl/catkin_ws/src/rcdp_4wd_stampfix && echo "new_4wd_package_path_ok"
```

看到该行再继续；无输出就先停，不覆盖目录。

```bash
unzip -n /home/thl/Lesson14_4wd_plugin_step11b.zip -d /home/thl/catkin_ws/src
source /home/thl/catkin_ws/devel/setup.bash
python3 /home/thl/catkin_ws/src/rcdp_4wd_stampfix/test/test_source_step11b.py
```

源码检查显示 `OK` 后才执行：

```bash
cd /home/thl/catkin_ws
catkin_make -j2
```

应看到 `Built target rcdp_4wd_stampfix`，构建正常结束。出现错误就回传第一处及末尾，不删 build/devel、不 sudo make install。

成功后检查：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rospack find rcdp_4wd_stampfix
ls -lh /home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so
```

回传后再继续制作驱动接入 Xacro／launch，完整依赖检查和实际加载检查也在下一阶段完成。
现在不关闭 Gazebo、不尝试 /cmd_vel、不额外安装软件，不推送 GitHub。

## 验证与来源

当前工具链与 Gazebo 开发库已在此前两轮插件编译中由用户确认存在，故不重复重装。
本地检查仅覆盖原始哈希、允许修改范围、四轮指令公式及包元数据，不替代 Ubuntu 实际编译或运动。
ZIP条目固定2020-01-01是打包元数据，避免再次导入未来mtime，不是创作日期。

上游：[gazebo_ros_skid_steer_drive.cpp at 2.9.3](https://github.com/ros-simulation/gazebo_ros_pkgs/blob/2.9.3/gazebo_plugins/src/gazebo_ros_skid_steer_drive.cpp)。
版权及 BSD 条款保留在所有源文件和 LICENSE，未为整个课程资料另行授予许可证。
