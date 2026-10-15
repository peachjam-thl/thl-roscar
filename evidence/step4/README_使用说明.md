# Lesson13 模型进入 Gazebo：第四步补充文件

目标环境：用户已确认 Ubuntu 20.04.6、ROS Noetic、Gazebo Classic 11.15.1；原始 `rcdp` 已放到 `/home/thl/catkin_ws/src/rcdp` 并成功执行 `catkin_make`，`rospack find rcdp` 返回该目录。

这不是老师提供的 Lesson14 源码，而是以用户的 `Lesson13_code(1).zip` 为基础，按 Lesson14 第 8–12、21–24 页流程补全的文件。原包里的 URDF、Xacro、RViz 和 Arbotix launch 不改动。

新增三个文件，相对 `/home/thl/catkin_ws/src/rcdp/`：

- `urdf/gazebo/myrobot_gazebo_step4.xacro`
- `launch/myrobot_gazebo_step4.launch`
- `worlds/lesson13_flat_step4.world`

## 与原代码的关系

几何尺寸以压缩包 `myrobot_v2.xacro` 为准：base 高 0.2 m，support 高 0.4 m，而不是前面 PPT 示例截图的其他尺寸。保留全部 10 个 link 的名称及 9 个 joint 的名称和连接关系。

新增：每个实际刚体的碰撞、正质量和按几何公式计算的惯性；Gazebo 材质；关节阻尼；接触参数。`root_link` 改成无几何、无质量的参考 link，不创建极小的真实物体；它通过固定关节连接有正常惯性的底盘。

质量是教学仿真假设，不是来自 PPT 的实测数据：base=5 kg、support=0.3 kg、platform=1 kg、每个驱动轮=0.3 kg、每个支撑球=0.05 kg、相机/雷达外观件各 0.1 kg，总计 7.2 kg。惯性公式由这些质量和原始几何尺寸计算，未声称质量经过实物标定。

驱动轮圆柱轴沿 Y，visual/collision 都旋转 90°，惯性主轴也按 Y 计算。原支撑球单轴关节方向 (1,1,1) 归一化，仍是原课件的教学简化；使用较低接触摩擦，而不声称它是真实万向脚轮。

相机限位由原代码 ±1.57 改为 ±π，对应课件实践文字的 ±180°。透明色改为不透明，便于在 Gazebo 中观察。此阶段相机、雷达只有外观，尚未加入传感器插件。

世界文件自行定义地面和光照，不依赖老师未附带的 `box_house.world`，也不引用 `model://` 在线资源。launch 采用课件的 `robot_description` → `empty_world.launch` → `spawn_model` 流程。

不启动 Arbotix、假关节状态发布器、差速控制器或 RViz。先验证模型生成和落地；下一阶段再添加 Gazebo 驱动、真实仿真关节状态、TF 和传感器，避免不同阶段混杂。

## 当前应执行的阶段

把 `Lesson13_Gazebo_step4.zip` 放到 Ubuntu 桌面，再执行：

```bash
unzip -n "$HOME/桌面/Lesson13_Gazebo_step4.zip" -d /home/thl/catkin_ws/src/rcdp
source /home/thl/catkin_ws/devel/setup.bash
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_gazebo_step4.xacro > /tmp/lesson13_step4.urdf
check_urdf /tmp/lesson13_step4.urdf
```

`-n` 不覆盖任何同名文件；如果之前已安装同名补充文件，需要单独确认版本，不能假定本次替换成功。任何一条报错都先停下，将第一处报错及上下文发来。`check_urdf` 如果不存在，说明校验工具尚未安装，不等于模型有错。

当前只要求完成导入与 URDF 校验。校验成功后，后续启动命令是：

```bash
roslaunch rcdp myrobot_gazebo_step4.launch
```

启动前关闭此前由自己启动、仍在运行的 Gazebo/冲突 launch，优先在对应终端 Ctrl+C；不要默认批量杀掉系统进程。`roslaunch` 在没有 ROS Master 时会自行启动，因此通常不必再单独开 roscore。此阶段没有 `/cmd_vel` 驱动接口，机器人不响应键盘是预期行为。

## 验证边界

已进行的本地静态检查以随附工作区验证结果为准，包括 Xacro 展开、XML、关节树、质量/惯性和几何关系检查。未连接用户 Ubuntu；未完成 Gazebo 运行、接触稳定性、TF 或控制闭环验证。不能把“静态检查通过”说成“Gazebo 已跑通”。

技术依据：[Gazebo Classic 官方 URDF 教程](https://classic.gazebosim.org/tutorials?cat=connect_ros&tut=ros_urdf)。课程版本固定为 ROS1 Noetic/Gazebo11，不迁移到 ROS2 或新版 Gazebo。
