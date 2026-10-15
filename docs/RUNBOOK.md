# 运行手册：保留现有成功环境

适用：用户 VMware 中的 Ubuntu 20.04.6、ROS1 Noetic、Gazebo Classic 11.15.1。命令块内没有提示符 `$`，可以逐行复制。不要把中文注释或终端输出当成命令。

## A. 已有包，重新启动

先关闭不再使用的旧仿真：在它原来的 roslaunch 终端按 **Ctrl+C**，等其正常退出。不要同时开启两份 Gazebo server。

终端 A：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rospack find rcdp
ss -ltnp 'sport = :11345'
```

包路径应为 `/home/thl/catkin_ws/src/rcdp`。若准备启动新的 Gazebo，11345 应没有旧 `gzserver` 的 LISTEN；如有，先按故障排查节识别，不直接强杀。

```bash
roslaunch rcdp myrobot_drive_step6.launch
```

保持终端 A 运行。roslaunch 会在需要时启动 ROS master；通常无需额外再开 roscore。应出现本地平地和双层机器人，且没有 gzserver 退出或 spawn 无限等待。启动本身不应让小车前进。

终端 B（新开终端）：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rostopic info /cmd_vel
rosservice call /gazebo/get_model_properties "model_name: 'lesson13_robot'"
```

期望 `/cmd_vel` 类型 `geometry_msgs/Twist`、订阅者 `/gazebo`；服务 `success: True`、`is_static: False`。如果输出不同先回传，不继续运动。

## B. 已跑通的低速测试

仅在课程仿真中使用。先看 `rostopic info /cmd_vel`，确认无其他键盘／导航发布者，Gazebo 未暂停且周围空旷。随后终端 B：

```bash
python3 /home/thl/catkin_ws/src/rcdp/scripts/test_forward_step6.py
```

脚本等待订阅者，约以 10 Hz 请求 0.1 m/s 前进三秒墙上时间，最后连续发送零速度。实际轨迹受加速度、摩擦、仿真倍率影响，不能等同严格位移 0.3 m。

用户已经通过这个流程确认“向前移动且停止”。再次执行仍需要现场观察是否真的停车，不仅看程序打印。

显式停车（在已 source 的终端 B）：

```bash
rostopic pub -1 /cmd_vel geometry_msgs/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'
```

注意：该版本直接差速插件保留最后速度指令，本轮没有命令超时停车机制。停止非零 `rostopic pub` 或关闭发布者不等于可靠停车。脚本正常结束／Ctrl+C 路径会尝试停车，但不覆盖强杀、断电、通信故障等情况，不是现实机器人安全控制器。

## C. 只看模型、不加载差速驱动

停止当前 drive launch 后，终端 A：

```bash
roslaunch rcdp myrobot_gazebo_step4.launch
```

它只加载物理模型与本地 world，没有驱动插件，不能指望 `/cmd_vel` 使其移动。不要同时开启 stage4 和 stage6 两份 launch。

## D. 从交接仓库恢复源文件（仅在确实需要时）

现有 VM 已成功时不用执行本节，不要为了“重新来一遍”覆盖文件。仓库内 `catkin_ws/src/rcdp/` 包含原始 14 文件与六个阶段新增文件。原始课件中的另外三个包只在 reference ZIP 内，不是当前有效工作空间的一部分。

若 VM 文件丢失或迁移到另一个同版本环境，先将本仓库下载到 Ubuntu，确认实际下载位置。以下用**示例路径** `/home/thl/thl-roscar`；只有实际存在且内容核对后才能照用：

```bash
test -f /home/thl/thl-roscar/catkin_ws/src/rcdp/package.xml
```

若目标包已存在，不覆盖，先检查差异／备份并让助手解释。若目标包完全不存在，可只复制 rcdp：

```bash
mkdir -p /home/thl/catkin_ws/src
cp -a /home/thl/thl-roscar/catkin_ws/src/rcdp /home/thl/catkin_ws/src/
source /opt/ros/noetic/setup.bash
cd /home/thl/catkin_ws
catkin_make
source /home/thl/catkin_ws/devel/setup.bash
rospack find rcdp
```

这不是新系统完整安装教程。包依赖在 `package.xml` / `CMakeLists.txt` 中，若缺依赖需先核对实际缺项与网络，不盲目重装全部 ROS。原包声明 gazebo_ros_control 作为课程依赖，不代表当前 direct diff-drive 路线同时运行它。

## E. 常见故障与最小检查

### Gazebo exit 255 / spawn 一直等服务

exit255 本身不是唯一原因。先取得完整 server 错误，隔离 GUI：

```bash
roslaunch gazebo_ros empty_world.launch world_name:=/home/thl/catkin_ws/src/rcdp/worlds/lesson13_flat_step4.world gui:=false verbose:=true
```

此命令只用于旧仿真已停止后的诊断；它不会额外 spawn 机器人。如果明确出现 `Address already in use`：

```bash
pgrep -a gzserver
ss -ltnp 'sport = :11345'
```

先在对应旧启动终端 Ctrl+C。若确认为遗留孤立课程进程，重新核对当前 PID 后才考虑 `kill -INT 当前PID`。81082 是历史 PID，不可照抄。别用 killall 清掉其他工作。

### APT 暂时不能解析域名

本轮 `cn.archive.ubuntu.com` 解析失败，未完成 `liburdfdom-tools` 安装。`apt update` / `--fix-missing` 不保证能修复 DNS；先检查 VM 网络和 DNS，未经确认不改软件源／DNS。可跳过可选 check_urdf，使用已完成的 Xacro 展开和实际 Gazebo 加载证据。

### 空白窗口或图形告警

旧日志包含 fuel 域名解析失败、127.0.0.1 推断和 svga context mismatch。它们不等于已证明的根因。本轮已证明的启动故障是旧进程占端口；解决后机器人显示。不要只看到图形字样就永久改显卡配置。

### 包找不到 / 找到旧副本

每个新终端先 source 当前 overlay，再 `rospack find rcdp`；不要 source 原解压包附带的旧 build/devel。下划线不是空格：`cmd_vel`、`gazebo_ros`、`myrobot_drive_step6.launch` 都必须完整。

### 模型在，但不动

先区分 stage4（没有驱动）还是 stage6；检查 `/cmd_vel` 的类型、订阅者、发布者、是否暂停和 wheel joint 名称。不要重复加两个控制器。完整问题输出比无依据改参数有效。

## F. 正常结束

先明确发送零速度、观察停止，再在终端 A Ctrl+C 正常关闭整组仿真。若有异常残留，重新识别当前进程和端口后处理。
