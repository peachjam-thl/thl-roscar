# Lesson13 Gazebo：第六步，差速驱动

## 已有现场证据

用户环境：Ubuntu 20.04.6、ROS1 Noetic、Gazebo Classic 11.15.1。`rcdp` 已成功构建。用户截图显示第四步模型出现在 Gazebo 中；随后 `/gazebo/get_model_properties` 返回模型 `lesson13_robot`、`success: True`、`is_static: False`，并确认 `base_l_wheel_joint` 和 `base_r_wheel_joint` 存在。

返回 `body_names` 中没有单独的 base/support/platform，是 Gazebo 将其固定关节合并进 `root_link`；`geom_names` 仍含相应 collision。不能将此结果当作零件丢失。

曾遇到 Gazebo 启动失败 `bind: Address already in use`：经 `pgrep` 和 `ss` 确認 PID 81082 占用 11345，用户停止该进程后模型成功显示。81082 是当时的历史 PID，不可在新一轮排障中直接重复使用。新启动若端口占用，须重新识别当前占用者。

本机 APT 下载曾因 `cn.archive.ubuntu.com` 域名解析失败而无法安装 `liburdfdom-tools`。因此不把新依赖安装当作本阶段默认前置操作；先检查已安装插件库。

## 本次文件

`Lesson13_Gazebo_step6_drive.zip` 仅包含三个新增文件，相对 `/home/thl/catkin_ws/src/rcdp/`：

- `urdf/gazebo/myrobot_drive_step6.xacro`
- `launch/myrobot_drive_step6.launch`
- `scripts/test_forward_step6.py`

它依赖已导入的第四步 Xacro 与 world，不能单独替代第四步补充包。第六步 Xacro 使用相对 include 复用第四步模型，不覆盖几何、质量或原代码。

## 控制方式与参数依据

对应 Lesson14 第 35 页 `libgazebo_ros_diff_drive.so` 路线；这是直接 Gazebo 差速插件，不再叠加 Arbotix 或 gazebo_ros_control 控制同一组轮关节。它不需要为此插件添加 transmission。

关键配置：左右关节为用户已确认的 `base_l_wheel_joint`、`base_r_wheel_joint`；轮距 0.8 m，轮径 0.2 m；100 Hz 更新；轮切向加速度限制 0.3 m/s²，轮扭矩上限 5 Nm。速度话题 `/cmd_vel`，里程计 `/odom`；TF 为 `odom → root_link`。

使用 `odometrySource=world` 读取仿真世界位姿，便于本阶段检验，不声称它是真实轮式编码器里程计。`publishTf=true`、`publishOdomTF=true`；`publishWheelJointState=true` 只发布两个驱动轮的关节位置。轮 TF 发布暂关闭，后续若增加 robot_state_publisher，避免重复发布同一 TF 边。本阶段不包含整棵机器人 TF 树、RViz 联动或传感器插件。

课件截图中的 `legacyMode`、`alwaysOn` 等不是当前 Noetic 源码实际读取的差速参数，因此没有盲目复制。实际参数与速度计算已对照 [Noetic 官方插件源码](https://raw.githubusercontent.com/ros-simulation/gazebo_ros_pkgs/noetic-devel/gazebo_plugins/src/gazebo_ros_diff_drive.cpp)。

重要：此版本的插件保存最后一条速度命令，没有在该源码中实现命令超时停车。仅关闭发布端不等于车辆停车。因此不要把停止非零 `rostopic pub` 误认为停止底盘。本包测试脚本在正常结束与 Ctrl+C 路径发送零速度；它不是覆盖进程被强杀等故障的安全控制器。

## 当前执行顺序：先加载，不发送移动命令

在 Ubuntu 检查插件库：

```bash
ls -l /opt/ros/noetic/lib/libgazebo_ros_diff_drive.so
```

若不存在先反馈，不在 DNS 故障状态下盲目重装 ROS。

把补充包复制到 Ubuntu 桌面，执行：

```bash
unzip -n "$HOME/桌面/Lesson13_Gazebo_step6_drive.zip" -d /home/thl/catkin_ws/src/rcdp
```

在原第四步 roslaunch 终端 Ctrl+C 停止旧仿真。确认端口释放：

```bash
ss -ltnp 'sport = :11345'
```

正常应只有表头，无 LISTEN 条目。若还有占用者，先反馈当前进程，不继续叠加仿真。

在启动终端执行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
roslaunch rcdp myrobot_drive_step6.launch
```

保持该终端运行。另开终端，执行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rostopic info /cmd_vel
```

预期类型 `geometry_msgs/Twist`，Subscribers 包含 `/gazebo`。模型不自动前进是正常的，启动后初始指令为零。先反馈以上结果确认插件加载。

## 下一阶段才执行：低速直行和停车验证

先确认当前只有课程仿真接收 `/cmd_vel`、Gazebo 未暂停、机器人周围有空地，且没有别的键盘/导航节点同时发布速度。通过第六步后，执行：

```bash
python3 /home/thl/catkin_ws/src/rcdp/scripts/test_forward_step6.py
```

它请求 0.1 m/s 前进，发布约三秒后发送零速度；车轮加速度、摩擦与仿真实时倍率会影响实际距离，不能将其说成严格走 0.3 m。发布和等待使用墙上时间，避免仿真暂停时脚本因 Rate 而无限等待。请观察是否真的停车，并记录截图或仿真位姿。

需要手动停车时，在已加载 ROS 环境的新终端执行：

```bash
rostopic pub -1 /cmd_vel geometry_msgs/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'
```

该停车指令也需要有效连接与正常仿真；不对通信断开、强杀进程或现实机器人安全作保证。

## 验证边界

第六步补充文件的本地 Xacro/XML/脚本语法和参数检查，与用户 Ubuntu 上的实际插件加载、直行及停车分别验证。生成代码不等于已运行通过；本阶段最终结果以用户的 `/cmd_vel` 订阅者、运动现象和停止状态为准。

### 2026-10-15 用户现场验证结果

用户确认插件库存在，`rostopic info /cmd_vel` 返回 `geometry_msgs/Twist`，订阅者包含 `/gazebo`。随后运行本包测试脚本，日志显示发送前进指令和零速度指令，用户明确反馈“向前移动且停止”。因此模型显示、差速接口、低速直行和测试结束后停车已由用户现场反馈确认。

这不是代理直接操作虚拟机或测量轨迹所得的独立验证；实际速度、距离、制动性能未量化。键盘控制、雷达/相机数据、完整 TF/RViz 联动、建图导航均尚未验证。原始反馈摘要保存在 `runtime_user_reported.json`，可与本地静态检查分开追溯。
