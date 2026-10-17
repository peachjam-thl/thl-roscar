# Step 10：差速插件仿真时间戳修复（先编译，不切换）

目标环境：Ubuntu 20.04 / ROS 1 Noetic / Gazebo Classic 11.15.1 / gazebo_plugins 2.9.3。

## 当前状态（2026-10-16 上传更新）

本说明最初随“先编译、不切换”源码包交付。随后用户已完成实际编译、依赖与模型预检、
新库加载和两轮独立约40秒诊断；第二轮恢复软件 RViz 与轻量点云后反馈“稳定 没出现”。
最新事实见 [验收记录](../../../docs/TIMESTAMP_FIX_STEP10.md)。下面的分阶段操作供复现，
不能把旧 ZIP 中的“尚待执行”当成当前状态。GitHub 只保存源码，不含用户编译的 `.so`。

## 为什么做这个包

用户的 40 秒只读诊断已捕获：`odom -> root_link` 的 TF 出现 3 次重复时间戳，
`/odom` 出现 2 次，均来自 `/gazebo` 且相同时间戳下位姿改变；两类消息共有 2 个重复时刻。
该窗口内 `/clock` 未观测到重复或倒退。不能据此证明所有内部回调／缓存更新都及时，
也不能把重复时间戳简单归因于两个节点同时发布 `/tf`。

官方 2.9.3 差速插件按 `World::SimTime()` 调度更新，但三个发布函数通过
`ros::Time::now()` 获取 ROS 时间。在 `/use_sim_time=true` 时，后者来自异步更新的 ROS 仿真时钟缓存。
缓存延迟是与现场证据一致的机制解释，具体线程调度延迟没有被此次外部诊断直接测量。

本包直接使用读取物理状态所在更新回调中的 Gazebo 仿真时间，按整数秒／纳秒构造 ROS 时间戳。
不使用墙上时间、不加微小偏移伪造时间、不在下游过滤重复消息，也不关闭必需的里程计 TF。

## 实际改动

- 官方源文件和头文件来自 tag `2.9.3`，commit 见 `UPSTREAM.json`，原始字节副本位于 `upstream/`。
- 重命名插件类、头文件、头文件保护宏、共享库，避免与系统版本冲突。
- `publishOdometry()`、`publishWheelJointState()`、`publishWheelTF()` 共三处改为：

```cpp
const common::Time sim_time = parent->GetWorld()->SimTime();
const ros::Time current_time(sim_time.sec, sim_time.nsec);
```

- 其余 C++ 逻辑保持上游版本。保留全部原有 SDF 参数及默认值。
- 新库为 `librcdp_diff_drive_stampfix.so`，复用已安装的 `libgazebo_ros_utils.so`。
- 原模型不变，原插件 `libgazebo_ros_diff_drive.so` 不变，原 launch 不变。
- 当前包不包含切换模型或自动启动 Gazebo 的脚本；编译不会将运行中的插件替换掉。

本阶段没有提供新的驱动参数：现有模型的 `updateRate=100`、`/cmd_vel`、`/odom`、
`odom -> root_link`、轮距／轮径、加速度／扭矩都应在后续切换阶段原样保留。
`publishWheelTF=false` 仍应保留，模型内部 TF 仍由现有 robot_state_publisher 发布。

## 现在只执行这些步骤

将 ZIP 复制到 VM 的 `/home/thl/Lesson14_stampfix_step10.zip`。
保持现有仿真与 RViz 原样，另开一个终端。

先确认新包目录尚不存在：

```bash
test ! -e /home/thl/catkin_ws/src/rcdp_stampfix && echo "new_package_path_ok"
```

必须看到 `new_package_path_ok`。若无输出，先停止，不覆盖已有目录。

解压并编译（第二组命令只在前一组成功后执行）：

```bash
unzip -n /home/thl/Lesson14_stampfix_step10.zip -d /home/thl/catkin_ws/src
source /home/thl/catkin_ws/devel/setup.bash
python3 /home/thl/catkin_ws/src/rcdp_stampfix/test/test_source_delta.py
```

应显示 `Ran 7 tests` 和 `OK`。这些测试核验源码／元数据，不代表插件已编译或已修复运行问题。

```bash
cd /home/thl/catkin_ws
catkin_make -j2
```

应出现 `[100%] Built target rcdp_diff_drive_stampfix`（百分比可能不同），且编译命令正常结束。
若失败，先停在这里，回传第一处错误及末尾输出，不删除 build/devel、不 sudo make install。

编译成功后检查产物和动态依赖：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rospack find rcdp_stampfix
ls -lh /home/thl/catkin_ws/devel/lib/librcdp_diff_drive_stampfix.so
ldd /home/thl/catkin_ws/devel/lib/librcdp_diff_drive_stampfix.so
```

`rospack find` 应指向 `/home/thl/catkin_ws/src/rcdp_stampfix`；库应存在，`ldd` 中不应出现 `not found`。
本阶段停止于此：把结果发回，确认通过后再制作／检查模型切换文件。

## 后续验收计划（现在不执行）

1. 新增独立 xacro／launch，仅替换插件库引用，核验模型与全部控制参数仍与 stage9 一致。
2. 确认停车，正常关闭旧仿真，再启动新阶段；不允许同时启动第二个 Gazebo server。
3. 确认实际 Gazebo 进程加载了新库，而不是仅看编译成功或 ROS 参数。
4. 复跑 40 秒原始 TF／odom／clock 诊断，检查同源重复、倒退、同刻位姿变化。
5. 检查速度控制、停车、雷达、TF 和轻量点云显示。短窗口无重复不等于长期／重置场景均已证明。

仿真时钟重置会开始新的时间纪元；本补丁不伪造单调跨纪元时间。验收不应跨越 reset／重启，
重启仿真时应重新启动诊断和 RViz，避免用旧缓存评估新的仿真时间。

## 验证边界和回退

本包不含预编译二进制。Windows 的源码检查不等于 Ubuntu 编译；用户随后提供了 Ubuntu 编译、
加载和两轮短测证据，但长期／reset／补丁后非零运动尚未覆盖。源码使用的是官方 2.9.3 tag，
不是从当前已安装的 Debian 二进制反向还原出来的源码。

只解压／编译本包时，旧仿真仍运行旧插件，不需要回退操作。以后新增的 launch 若未通过，
正常停止新仿真并用原来的 `roslaunch rcdp myrobot_camera_step9.launch` 启动即可；
前提仍是没有另一台 Gazebo server 占用同一端口，且旧配置文件未被改动。

上游来源及许可：
[gazebo_ros_diff_drive.cpp at 2.9.3](https://github.com/ros-simulation/gazebo_ros_pkgs/blob/2.9.3/gazebo_plugins/src/gazebo_ros_diff_drive.cpp)。
原 BSD 许可保留于源文件、头文件和 `LICENSE`。
