# 运行手册：保留现有成功环境

适用：用户 VMware 中的 Ubuntu 20.04.6、ROS1 Noetic、Gazebo Classic 11.15.1。命令块内没有提示符 `$`，可以逐行复制。不要把中文注释或终端输出当成命令。

> 2026-10-16 step10：当前默认是时间戳修复 launch＋step9a 轻量预览。原 A–F 为历史模型／驱动手册，不是默认入口。两轮短测通过，长期／reset／补丁后运动未验收。命令中的 HOME 指当前 Ubuntu 用户主目录，不是在 Windows 执行。若仿真正运行，不再启动第二份。

## 0. 当前成功方案：相机仿真＋轻量点云

### 已经在正常运行时

保留一个 step10 Gazebo/RSP、一个预览中继和一个软件渲染 RViz。不要重复执行另一个 stage 的 launch，不重新勾选原始大点云。旧 step9 使用系统原驱动，只作回退。

只读检查可另开终端执行：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
rospack find rcdp
rostopic info /cmd_vel
rostopic info /scan
rostopic info /lesson14/depth_points_preview
```

`/cmd_vel` 是否无发布者需当场检查，不凭昨日输出推断。任何非零运动仍需先确认只有课程仿真接收、无竞争控制者、仿真未暂停且前方空旷。

### 确实要重新启动时

先在旧启动终端正常退出旧仿真；检查端口，没有辨清占用者就不再起新 Gazebo。确保以下课程场景文件存在（现已按用户新要求补入仓库，但当前 VM 不必重复覆盖）：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
test -f "$HOME/catkin_ws/src/rcdp/worlds/lesson14_box_house_step7.world" && echo "world exists"
test -f "$HOME/catkin_ws/devel/lib/librcdp_diff_drive_stampfix.so" && echo "stampfix library exists"
ss -ltnp 'sport = :11345'
rosrun xacro xacro "$HOME/catkin_ws/src/rcdp/urdf/gazebo/myrobot_stampfix_step10.xacro" -o /tmp/lesson14_stampfix_step10.urdf
```

文件缺失／Xacro 报错／旧端口仍占用就停在这里。不要直接运行后面的命令。

GitHub 保存的是源码，不含用户 VM 编译产物。若刚从仓库恢复且新库不存在，先按
[`rcdp_stampfix` 说明](../catkin_ws/src/rcdp_stampfix/README.md) 核对已安装开发依赖、构建工作空间和预检。
独立插件包 ZIP 解压到 `src`；切换包 ZIP 解压到 `src/rcdp`，两者目标不同。

终端 A：

```bash
roslaunch rcdp myrobot_stampfix_step10.launch start_rviz:=false
```

新 launch 保留原 world、模型和 RSP，只改驱动库引用，默认关闭自动 RViz。
用户已启动此组合，确认新库实际加载并完成两轮时间戳短测；这不等于全新系统安装或长期可靠性已通过。

终端 B，保持运行：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
python3 "$HOME/catkin_ws/src/rcdp/scripts/cloud_preview_step9a.py"
```

等确认仿真和中继没有报错，终端 C 启动唯一一个 RViz：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
LIBGL_ALWAYS_SOFTWARE=true rosrun rviz rviz -d "$HOME/catkin_ws/src/rcdp/config/lesson14_cloud_preview_step9a.rviz" __name:=lesson14_rviz_preview
```

先看模型和红色雷达正常，再勾选 Depth_Preview。预期 80×60、4800 点的青色预览，不是原始 307200 点。中继无订阅者时等待是正常状态；RViz 开启预览后才按需订阅原始点云。

### 读数检查

终端 D：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
timeout 7s rosrun tf tf_echo odom laser_scan_link
timeout 7s rosrun tf tf_echo odom rotate_depth_camera_link
timeout -s INT 8s rostopic hz /scan
timeout -s INT 8s rostopic hz /kinect/rgb/image_raw
timeout -s INT 8s rostopic hz /kinect/depth/image_raw
timeout -s INT 8s rostopic hz --wall-time /lesson14/depth_points_preview
```

timeout 到期终止持续观察是预期行为；个别程序退出码非零不能脱离输出直接判仿真崩溃。TF 刚接入可短暂未收齐，后续应持续成功；一直失败就回传，不叠加静态 TF。图像／CameraInfo 是按需数据流，预览开启时相关深度数据链路活跃；没有消费者时需区分“未激活”与“插件坏了”。

预览最多 2 Hz 墙钟，历史短测约 1.712；RGB/Depth 约 10 Hz 指 ROS 仿真时间。此手册不自动运行会发非零速度的程序；短时运动必须再走 B 节前置安全检查。

### 正常退出与故障边界

如曾发非零速度，先按 B 节发零并观察停车，再正常关闭 RViz、中继和 Gazebo。中继本身没有机器人控制输出。不要把退出发布者当作插件保证停车。

完整原始点云 SIGBUS 根因仍未定位。step10 已通过两轮根 TF／odom／clock 短测，但不能称为长期或 reset 场景均根治。显示再卡死时不要反复开启大点云，先保留后端并报告新错误；不要永久改 VM 显卡／软件源、重复启动 Gazebo 或强杀所有进程。

### 时间戳修复的复查

源码和单次数据诊断见 [step10 验收](TIMESTAMP_FIX_STEP10.md)。在新仿真稳定运行、没有暂停或 reset 时，另开终端：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
timeout 55s python3 -u "$HOME/catkin_ws/src/rcdp/scripts/diagnose_tf_stamps_step10.py"
```

该脚本被动观察 40 秒墙钟，不发布速度／TF／clock，不写业务参数。
需要完整窗口、三类流均收到，再判断重复、倒退、同刻位姿变化是否为0。
重新确认库加载时先查当前真实 gzserver PID；包装 `/bin/sh` 和实际 gzserver 两行本身不代表两份 server。
不能复制证据中的历史 PID。新插件部署后尚未重新验收非零速度运动，后面的 B 节是原阶段测试方法。

## A. 历史 step6：仅模型与驱动

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

## B. 历史已跑通的低速测试（step6–9a）

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

现有 VM 已成功时不用执行本节，不要为了“重新来一遍”覆盖文件。仓库内代码是原始 rcdp、早前 step4/6、12 个补充文件及本次补齐的室内 world，不是 VM 回读备份。源文件齐备仍不等于新系统的 ROS 依赖已经安装或已验收完整冷启动。原始参考 ZIP 里的其他包也不是当前应默认导入的内容。

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
