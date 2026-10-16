# thl roscar

**基于 ROS1 Noetic 的差速移动机器人仿真与传感器可视化实践。**

从 URDF/Xacro 物理模型、Gazebo 差速驱动出发，逐步接入室内场景、激光雷达、TF、RGB-D 相机和低负载点云预览。项目保留实际操作、成功／失败日志、用户截图与可复用代码，便于复现、排错和后续扩展。最新整理：2026-10-16。

[运行手册](docs/RUNBOOK.md) · [系统架构](docs/ARCHITECTURE.md) · [实践复盘](docs/PRACTICE_LOG_2026-10-15_16.md) · [实验与证据](docs/EXPERIMENTS.md) · [资料下载](docs/RESOURCES.md) · [更新记录](CHANGELOG.md)

## 实际效果

<img src="evidence/screenshots/step9_rgb_depth_2026-10-16.png" alt="用户现场截图：RViz 显示机器人、激光扫描及 RGB/深度图" width="680" />

这是用户提供的真实运行截图，展示 RGB/深度图、模型与激光扫描；不是最新轻量点云的截图，后者目前只有数值检查和用户稳定性反馈。[更多截图与说明](evidence/screenshots/README.md)。

**新账号／新助手先读 [START_HERE.md](START_HERE.md)，再读 [当前状态](context/CURRENT_STATE.md) 和 [运行手册](docs/RUNBOOK.md)。不要从零重装或重新建包。**

## 项目能力与进度

- Ubuntu 20.04.6 LTS + ROS 1 Noetic + Gazebo Classic 11.15.1。
- 用户现有工作空间 `/home/thl/catkin_ws`，功能包 `/home/thl/catkin_ws/src/rcdp`。
- `rcdp` 已构建成功，模型 `lesson13_robot` 已在 Gazebo 显示。
- 差速插件订阅 `/cmd_vel`；用户运行测试脚本后明确反馈“向前移动且停止”。
- 这是用户现场截图、终端输出和反馈支持的结果，不是助手直接接入虚拟机测量；实际位移和速度未量化。
- 新增室内场景下的激光扫描、真实仿真关节状态、TF/RViz、RGB-D、CameraInfo 和轻量点云预览的逐阶段实践记录。
- 雷达约 5.495 Hz，RGB/深度约 10 Hz（ROS 仿真时间）；轻量点云 4800 点，约 1.712 Hz（墙钟）。这不是同一时间基准下的速率比较。
- 最新受控前进／停车与 Gazebo、RViz、扫描、预览的视觉联动，用户确认“正常 同步 稳定”。没有独立测量位移、制动时间或消息级同步误差。
- 原始全分辨率点云曾使 RViz 以 SIGBUS 退出。软件渲染＋低负载预览可用，但根因和偶发 TF 重复时间戳警告仍未解决。
- 后续键盘控制、建图、地图保存、定位、导航尚未验收；当前先暂停后续实践，整理项目资料。

**本次重点：[两天实践复盘](docs/PRACTICE_LOG_2026-10-15_16.md) · [当前启动与检查](docs/RUNBOOK.md) · [公开更新的边界](docs/PUBLIC_UPDATE_SCOPE.md)。**

| 模块 | 状态 | 验证依据 |
| --- | --- | --- |
| 双层机器人与差速驱动 | 已通过基础功能测试 | Gazebo 模型、话题订阅、低速前进／停车反馈 |
| 激光雷达与 TF/RViz | 已通过基础功能测试 | scan 数值／频率、TF 查询、现场截图 |
| RGB-D 与 CameraInfo | 已通过样本及显示检查 | 图像／深度截图、XYZ 和内参基本检查 |
| 低负载点云预览 | 已通过短时功能测试 | 4800 点消息、1.712 墙钟 Hz、稳定性反馈 |
| 原始完整点云显示／偶发 TF 警告 | 仍有已知问题 | SIGBUS 与 TF_REPEATED_DATA 日志保留 |
| 键盘控制、SLAM、AMCL、导航 | 待实施／待验收 | 仅有课程参考包和后续路线，不是完成项 |

“通过”均指当前课程仿真下的用户现场反馈；不代表实车测试、长期可靠性或精确轨迹／标定验收。

## 运行环境

| 项目 | 已验证环境 |
| --- | --- |
| Ubuntu / ROS | 20.04.6 LTS / ROS1 Noetic |
| Gazebo / RViz | Classic 11.15.1 / RViz 1.14.26 |
| 开发语言／配置 | Python3、XML/URDF/Xacro、ROS launch、YAML |
| 运行平台 | VMware；当前 RViz 采用逐命令软件渲染 |
| 工作空间 | `~/catkin_ws`，包 `rcdp`，模型 `lesson13_robot` |

## 仓库内容

| 目录 | 内容 |
| --- | --- |
| `courseware/` | Lesson1–15 原始 PDF，共 1682 页；其中最新提供的 Lesson11–15 为 352 页，已核对同版本 |
| `study/` | Lesson11–15 学习索引、既有笔试复习 PDF、可检索逐页文本和覆盖记录 |
| `catkin_ws/src/rcdp/` | 既有模型／驱动，加上 step7 雷达、step8 TF、step9 相机、step9a 预览的 12 个补充文件 |
| `reference/` | 用户提供的 Lesson13、14、15 原始代码 ZIP；只作原始参考，不能整包覆盖工作空间 |
| `archives/` | step4、6、7、8、9、9a 六份按阶段导入的增量 ZIP |
| `context/`、`docs/` | 当前状态、操作复盘、旧知识与排错、运行与接手步骤 |
| `history/` | 首次归档的旧对话快照，本次不追加内部会话或全量聊天 |
| `evidence/` | 实际截图、2 份用户文本附件、22 条终端消息、机器可读验收摘要 |
| `metadata/` | 文件清单、页数、校验值与来源边界 |
| `tests/`、`tools/` | 无 ROS 依赖的点云预览测试与归档完整性工具 |

## 快速继续（已有 Ubuntu 环境）

启动终端：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rospack find rcdp
```

先阅读运行手册。若仿真正在正常运行，保留现场，不要重复启动 Gazebo。所用室内 world 已随本次资料补齐，但仍需本机已有对应 ROS 插件；没有进行“全新系统一键安装”的验收。

运动前另开终端检查：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rostopic info /cmd_vel
```

先确认只有课程仿真接收速度、没有其他速度发布者、场地空旷且仿真未暂停，再按运行手册执行低速测试。不要在真实机器人上直接运行本仓库测试。

当前建议的重启组合为：step9 launch 关闭自动 RViz → 独立点云中继 → 软件渲染预览 RViz。具体终端 A/B/C、前置检查与停车命令见运行手册，不将三个命令不加检查地同时执行。

## 开发与验证

在仓库根目录运行（Windows 或 Linux，无需安装 ROS）：

```bash
python3 -m unittest discover -s tests -v
python3 tools/verify_archive.py
```

目前预览中继 9 项测试通过；文件 SHA256、XML/Python 语法及 ZIP CRC 通过。这是本地静态／合成数据检查，不冒充 Ubuntu 仿真测试。实际用户测试按实验文档逐条追溯。

## 必须知道的边界

1. 这是课程实践交接，不是整个虚拟机备份。已有 `robot_course_pkg` 的完整现场源码未取得；不捏造缺失文件。
2. 原始 ZIP 另有 `beginner_tutorials`、`ros_bilibili`、`tf2_roswiki`；不要把它们无差别复制到现有工作空间制造冲突。
3. 不运行 Arbotix、gazebo_ros_control 与当前直接差速插件同时控制同一轮关节。
4. 该差速插件没有本轮确认的指令超时停车机制。结束非零速度发布不等于停车，必须显式发零速度。
5. 历史对话里可能有不正确或过时的答题判断；原课件、当前文件与现场证据优先，不承诺考试满分。
6. 仓库按用户要求公开，本次还按新要求补齐所提供的课件索引、代码包、截图和日志。资料保留来源与权利归属，不为老师课件／原包授予统一开源许可证；日志中的历史用户名／路径不可当成当前部署配置。详见 [权利与隐私](RIGHTS_AND_PRIVACY.md)。

校验本地交接文件：`python3 tools/verify_archive.py`。完整来源与缺项见 [交接范围](context/COVERAGE_AND_LIMITS.md)。
