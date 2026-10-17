# Step10：Gazebo 差速插件重复时间戳修复验收

记录日期：2026-10-16（当前任务日期）。证据来自用户在 Ubuntu VM 执行后的回传，
不是助手直接登录 VM 的结果。本文不改写先前静态检查报告的历史状态。

## 结论

**当前阶段修复验收通过。** 新插件实际加载、模型与依赖预检通过；
两个独立的约 40 秒观察窗口内，原始根 TF、里程计和时钟均未观测到重复或倒退。
第二个窗口按操作流程恢复了软件渲染 RViz 与轻量点云预览，用户反馈“稳定 没出现”。

两次是独立窗口，不是连续 80 秒测试。不将当前结果表述为长期运行、重置／回放等所有场景的永久保证。

可追溯原始数值见 [step10 证据索引](../evidence/timestamp_fix_step10/README.md)，
编译／动态库附件见 [日志索引](../evidence/logs/README.md)。本记录的“未覆盖”不因本地离线测试通过而取消。

## 现场环境与诊断依据

- Ubuntu 20.04.6 / ROS1 Noetic / Gazebo Classic 11.15.1，用户 `thl`。
- 工作空间 `/home/thl/catkin_ws`；模型包 `rcdp`；模型 `lesson13_robot`。
- 原始故障：`TF_REPEATED_DATA` 出现在 `odom -> root_link`。
- 原插件的一次 40 秒诊断：根 TF 重复 3 次，里程计重复 2 次，
  均为 `/gazebo` 同源、同一时间戳下位姿改变；TF 与 odom 共有 2 个重复时刻。
  该窗口内 `/clock` 未观测到重复或倒退。
- 原始诊断不证明具体内部线程调度时序，也不证明两个不同节点发布 `/tf` 就构成边冲突。

## 修复做法

基于官方 `gazebo_plugins` tag `2.9.3`，commit
`cd9cc952402375be5f274f39b29399c4087aa839`，复制并重命名类／头文件／库。
保留上游许可、原始副本与来源哈希，独立编译为：

```text
/home/thl/catkin_ws/devel/lib/librcdp_diff_drive_stampfix.so
```

将 `publishOdometry`、`publishWheelJointState`、`publishWheelTF` 的时间戳来源
从 `ros::Time::now()` 改为 Gazebo `World::SimTime()` 的整数秒／纳秒。
根 TF 与 odom 仍共享同一个发布函数中的时间戳；没有伪造微小递增量或过滤下游数据。
轮 TF 开关仍为 false，不额外与 RSP 争用模型内部 TF。

未替换 `/opt/ros` 中的系统库；未降低 100 Hz；未关闭 odom TF；未改变轮径、轮距、
速度／加速度／扭矩、里程计来源、传感器配置及现有坐标系。

## 编译与部署证据

- 用户完整编译日志显示新库链接成功，`Built target rcdp_diff_drive_stampfix`。
- 首次编译曾出现导入文件修改时间在未来的 GNU make 警告。
  已提供仅针对新包文件 `touch` 后重新构建的方法；没有收到完整重编译日志，
  不把该构建时间警告单独标为已复核消失。它与 ROS 仿真时间戳问题不同。
- VM 预检：新旧展开模型仅驱动库 filename 不同；11 links、10 joints、
  6 moving joints、4 plugins、1 diff-drive plugin、100 Hz、`odom -> root_link`。
- VM 完整动态依赖检查通过；插件 SHA256：
  `ad86bd0dc84e0b795ddc9d95e641a69ad59381e6ce4afed11ce9e1802623e10e`。
- 用户在当时实际 Gazebo PID `91801` 的 `/proc/91801/maps` 中确认新库的五个映射段；
  同一次针对新旧驱动库名的匹配输出没有旧驱动库。PID 只是当次证据，今后检查不能沿用。
- `91740 /bin/sh .../gzserver` 为启动包装脚本；不能将包装脚本与实际工作进程两条记录
  当成两份 Gazebo server。

## 两轮运行验收

| 项目 | 首轮：未恢复 RViz | 第二轮：恢复轻量显示负载 |
| --- | ---: | ---: |
| 墙钟观察时长（秒） | 40.079 | 40.048 |
| 仿真时间推进（秒） | 33.882 | 34.297 |
| 根 TF 收到条数 | 3386 | 3428 |
| odom 收到条数 | 3387 | 3429 |
| clock 收到条数 | 31405 | 32024 |
| 根 TF 重复／倒退／同刻位姿变化 | 0 / 0 / 0 | 0 / 0 / 0 |
| odom 重复／倒退／同刻位姿变化 | 0 / 0 / 0 | 0 / 0 / 0 |
| clock 重复／倒退 | 0 / 0 | 0 / 0 |
| TF 与 odom 共同重复时刻数 | 0 | 0 |
| completed_window | true | true |
| all_three_streams_received | true | true |

两轮三类流的发布者均为 `/gazebo`；根 TF 和 odom 的 frame-pair 均为 `odom -> root_link`。
TF 与 odom 接收条数相差 1，独立订阅窗口边界／传输可能导致差异，
不能单凭计数差声称某条消息丢失。这里没有执行逐条完整配对审计。

第二轮用户明确反馈：**“稳定 没出现”**。这是用户对窗口稳定和无警告的反馈，
不是助手直接监控的长期日志结论。两轮没有进行新的非零速度运动验收。

## 后续正常使用

默认启动文件改用 `myrobot_stampfix_step10.launch`，不要继续把旧 step9 当成默认入口。
**以下只供下次启动使用；当前仿真运行时不要再执行第二份 launch。**

终端 A：

```bash
source /home/thl/catkin_ws/devel/setup.bash
roslaunch rcdp myrobot_stampfix_step10.launch start_rviz:=false
```

终端 B，保持运行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
python3 /home/thl/catkin_ws/src/rcdp/scripts/cloud_preview_step9a.py
```

终端 C，保持运行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
LIBGL_ALWAYS_SOFTWARE=true rosrun rviz rviz -d /home/thl/catkin_ws/src/rcdp/config/lesson14_cloud_preview_step9a.rviz __name:=lesson14_rviz_preview
```

确认模型／红色扫描正常后，如未勾选，则开启 `Depth_Preview`。保持使用独立的轻量预览话题，
不重新默认开启原始大点云。旧 `myrobot_camera_step9.launch` 保留作回退，
但切回旧插件后不能继承本次新插件时间戳验收结论。

## 未覆盖与范围边界

- 尚未做长期连续运行、仿真 reset、暂停／恢复、rosbag 回放等完整时序测试。
- 尚未对新插件重复执行受控前进／停车运动回归；原控制逻辑和配置静态保持不变，
  不等同于已经做过运动实测。
- 原始完整点云导致 RViz SIGBUS 的根因仍未定位；轻量显示稳定不代表该问题已修复。
- 没有启动 SLAM、AMCL 或导航；没有安装新依赖、修改系统时钟或系统 ROS 库。
- 用户随后明确要求“上传github”；本记录随本轮修复源码归档，是否已远端同步以对应 Git 提交为准，不改变仓库可见性。
