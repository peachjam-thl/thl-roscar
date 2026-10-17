# 当前状态：先读此文件

更新至 2026-10-16 step10。最新用户反馈 **“稳定 没出现”**：新时间戳修复插件已加载；恢复软件 RViz 和轻量点云后，第二轮独立约40秒原始消息测试无重复／倒退。当前用户要求将这次修复上传 GitHub，不自动进入下一课程阶段。

## 现场环境（用户逐项提供）

| 项目 | 已知值 |
| --- | --- |
| 工作方式 | 用户在 VMware 中执行，助手根据回传验收 |
| 系统 | Ubuntu 20.04.6 LTS |
| ROS | ROS 1 Noetic；运行日志 roslaunch/rosversion 为 1.17.4 |
| 仿真 | Gazebo Classic 11.15.1，VMware 虚拟机 |
| ROS 安装 | `/opt/ros/noetic` |
| 现有工作空间 | `~/catkin_ws` |
| 当前功能包 | `~/catkin_ws/src/rcdp`；新增独立插件包 `~/catkin_ws/src/rcdp_stampfix` |
| 原始参考材料 | 工作空间外隔离保存，不整包覆盖当前 rcdp |
| 模型名 | `lesson13_robot` |
| 最新仿真 launch | `myrobot_stampfix_step10.launch start_rviz:=false`；旧 step9 保留作回退 |
| 预览脚本 | `scripts/cloud_preview_step9a.py` |
| 当前 RViz | `lesson14_cloud_preview_step9a.rviz`，Fixed Frame=odom，Depth_Preview 开启 |
| 软件渲染 | 每次 RViz 命令前 `LIBGL_ALWAYS_SOFTWARE=true`；日志确认 llvmpipe |
| 本地 world | `worlds/lesson14_box_house_step7.world`，本次资料补齐已纳入仓库 |
| 速度 / 里程计 | `/cmd_vel` / `/odom` |

## 已验证证据

1. 既有模型与驱动：构建成功，Gazebo 动态模型存在，差速订阅和低速前进／停车通过。
2. step7 雷达：房间和小车正常；LaserScan 约 5.495 Hz；单帧 360 个样本有效，最近约 1.749 m，frame=laser_scan_link。
3. step8 TF/RViz：使用 Gazebo 关节位置与单个 RSP；odom→laser_scan_link 后续连续可查；模型、红色扫描及运动视觉联动通过。
4. step9 RGB-D：RGB、深度图显示；深度 640×480、32FC1；单帧 307200 像素有限且正数；原始 XYZ 点云一次检查同样 307200 点有效。
5. 光学 TF / CameraInfo：odom 到 rotate_depth_camera_link 后续连续连通；RGB/Depth CameraInfo 的 frame、分辨率和 K 矩阵基本检查通过，不是物理标定验收。
6. step9a：80×60=4800 点、153600 字节；保持采集时间／frame／所选点字节；最多 2 Hz 墙钟，短测约 1.712 Hz。用户确认静态稳定和运动视觉联动。
7. 实测短窗口频率：RGB 10.051 Hz、Depth 9.960 Hz（ROS 仿真时间），预览 1.712 Hz（墙钟）；时间基准不同，不直接比较。
8. step10：VM 构建和完整依赖预检通过，新旧展开 URDF 仅差速插件库路径不同；11 links、10 joints、4 plugins、100Hz 保持。实际进程 maps 已确认新库加载，不是仅看参数文件。
9. 两轮时间戳窗口：未开 RViz 时 TF3386／odom3387；恢复预览后 TF3428／odom3429；重复、倒退、同刻位姿变化均0，两轮均完整。用户确认第二轮显示稳定、无警告。原始数据见 [step10 证据](../evidence/timestamp_fix_step10/README.md)。

以上来自用户现场输出、此前截图和明确反馈，不是助手直接访问 VM。速度／位移／制动时间未独立量化，不能说严格走了 0.3 m；“同步”是视觉反馈，不是消息级同步误差测量。本地静态检查与现场证据分开。详见 [脱敏复盘](../docs/PRACTICE_LOG_2026-10-15_16.md) 和 [验收摘要](../evidence/practice_2026-10-15_16.json)。

## 当前模型与控制配置

- 基础物理模型 10 links、9 joints；step9 只新增无质量光学参考 link＋fixed joint，成为 11 links、10 joints，6 个活动关节不变。
- `root_link` 是参考根；底盘、立柱、二层平台通过固定关节连接，碰撞几何仍存在。
- 驱动轮半径 0.1 m、轮宽 0.08 m；轮距 0.8 m。
- 仅一个 `/home/thl/catkin_ws/devel/lib/librcdp_diff_drive_stampfix.so` 驱动插件，100 Hz，轮加速度上限 0.3 m/s²，轮扭矩 5 Nm。独立包基于官方2.9.3，三处状态发布改用 Gazebo SimTime；原系统库未替换。
- odometrySource 为 `world`（仿真真值，不是已验证的真实轮编码器）。TF 配置为 `odom → root_link`。
- `publishWheelJointState=true` 提供两个驱动轮位置；新增 Gazebo joint-state 插件只提供其他四个活动关节，RSP 转换为模型 TF，不启动伪造位置的 JSP。
- `publishWheelTF=false`，RSP 负责模型边，Gazebo 驱动负责 odom→root_link；两个 /tf 发布节点不自动等于边冲突。
- 雷达及 RGB-D 已追加实际插件并通过话题／样本验证，不再只是几何外形。预览中继只用于显示，不控制车、不发布 TF。

## 当前阶段修复与剩余问题

- 原始完整点云在 RViz 触发退出码 -7（x86 Linux SIGBUS），没有崩溃堆栈；未定位根因，未重新通过完整点云显示。
- `odom→root_link` 的同源重复已在旧插件诊断中捕获；step10 两轮短测通过，标为**当前阶段修复通过**，不是所有 TF／长期／reset／回放均已证明。详见 [验收记录](../docs/TIMESTAMP_FIX_STEP10.md)。
- 软件渲染＋低负载显示是可用恢复方案，不能证明故障一定源于显卡、内存、TF 或数据。

## 尚未完成／不允许写成已完成

- 键盘遥控验收，旋转／转弯测试，速度／距离量化。
- 新插件部署后的非零速度运动回归、暂停／恢复、reset 和长时间连续运行；首次导入源码的未来文件时间构建警告也没有取得完整重编译日志复核。
- 长时稳定性、消息级同步误差、真实相机／激光精度标定。
- 六个活动关节的逐条实时完整消息清单；当前只有静态覆盖、插件日志及相关功能证据。
- SLAM、地图保存、AMCL、move_base 导航。
- APT/DNS 修复和 `check_urdf` 安装（当时下载失败，检查器不是跑 Gazebo 的硬性前提）。
- VM 全工程备份；`robot_course_pkg` 的现场完整源文件未读回。

## 下一次不要误判

最后反馈时 step10＋低负载显示稳定，但下次接手仍需按需检查，不能根据旧 PID 或日志推断进程仍在线。以新 launch 为默认，旧 step9 只回退。用户要求继续后，先按实际请求做新插件运动回归或后续课程依赖只读检查，再逐阶段进入 Lesson15。不混用 rs_gazebo；不让 Gmapping 和 AMCL 同时发布 map→odom。

历史资料已补齐 Lesson14/15 原 ZIP、step7–9a 增量、world、截图和用户日志。本次再按“上传github”授权加入 step10 独立插件、切换与诊断源代码、两份原交付 ZIP、编译／ldd 附件及三次诊断 JSON。课件不重复上传；不上传 VM 二进制、凭据或内部会话，不改变公开可见性、不清理旧历史。资料和验收证据保留来源边界，见 docs/RESOURCES.md。
