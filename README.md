# thl roscar

ROS 1 Noetic 课程与 Gazebo 小车实践记录。最新整理：2026-10-16（中国时间）。用户本次明确选择保持公开，因此这次更新只增加脱敏总结和可分享的实践补充代码；不是对历史材料的公开授权或全仓隐私清理。

**新账号／新助手先读 [START_HERE.md](START_HERE.md)，再读 [当前状态](context/CURRENT_STATE.md) 和 [运行手册](docs/RUNBOOK.md)。不要从零重装或重新建包。**

## 现在已经做到哪里

- Ubuntu 20.04.6 LTS + ROS 1 Noetic + Gazebo Classic 11.15.1。
- 用户现有工作空间 `/home/thl/catkin_ws`，功能包 `/home/thl/catkin_ws/src/rcdp`。
- `rcdp` 已构建成功，模型 `lesson13_robot` 已在 Gazebo 显示。
- 差速插件订阅 `/cmd_vel`；用户运行测试脚本后明确反馈“向前移动且停止”。
- 这是用户现场截图、终端输出和反馈支持的结果，不是助手直接接入虚拟机测量；实际位移和速度未量化。
- 新增室内场景下的激光扫描、真实仿真关节状态、TF/RViz、RGB-D、CameraInfo 和轻量点云预览的逐阶段实践记录。
- 雷达约 5.495 Hz，RGB/深度约 10 Hz（ROS 仿真时间）；轻量点云 4800 点，约 1.712 Hz（墙钟）。这不是同一时间基准下的速率比较。
- 最新受控前进／停车与 Gazebo、RViz、扫描、预览的视觉联动，用户确认“正常 同步 稳定”。没有独立测量位移、制动时间或消息级同步误差。
- 原始全分辨率点云曾使 RViz 以 SIGBUS 退出。软件渲染＋低负载预览可用，但根因和偶发 TF 重复时间戳警告仍未解决。
- 后续键盘控制、建图、地图保存、定位、导航尚未验收；用户已暂停后续实践，先整理 GitHub。

**本次重点：[两天实践复盘](docs/PRACTICE_LOG_2026-10-15_16.md) · [当前启动与检查](docs/RUNBOOK.md) · [公开更新的边界](docs/PUBLIC_UPDATE_SCOPE.md)。**

## 仓库内容

| 目录 | 内容 |
| --- | --- |
| `courseware/` | Lesson1–15 原始 PDF，共 1682 页；不是原生 PPTX |
| `study/` | Lesson11–15 学习索引、既有笔试复习 PDF、可检索逐页文本和覆盖记录 |
| `catkin_ws/src/rcdp/` | 既有模型／驱动，加上 step7 雷达、step8 TF、step9 相机、step9a 预览的 12 个补充文件 |
| `reference/` | 用户提供的 Lesson13 原始 ZIP（含四个包，仅作原始参考） |
| `archives/` | 首次归档的两份增量 ZIP；本次不新增包含课程场景的 ZIP |
| `context/`、`docs/` | 当前状态、操作复盘、旧知识与排错、运行与接手步骤 |
| `history/` | 首次归档的历史对话／图片；本次不追加原始聊天或截图，以脱敏复盘衔接 |
| `evidence/` | 首次归档证据，以及本次脱敏验收摘要（不是新上传的原始日志／截图） |
| `metadata/` | 文件清单、页数、校验值与来源边界 |

## 快速继续（已有 Ubuntu 环境）

启动终端：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rospack find rcdp
```

先阅读运行手册。若仿真正在正常运行，保留现场，不要重复启动 Gazebo；若需要重新启动 step9，必须已有课程场景文件。本次公开更新不新增分发该文件。

运动前另开终端检查：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rostopic info /cmd_vel
```

先确认只有课程仿真接收速度、没有其他速度发布者、场地空旷且仿真未暂停，再按运行手册执行低速测试。不要在真实机器人上直接运行本仓库测试。

## 必须知道的边界

1. 这是课程实践交接，不是整个虚拟机备份。已有 `robot_course_pkg` 的完整现场源码未取得；不捏造缺失文件。
2. 原始 ZIP 另有 `beginner_tutorials`、`ros_bilibili`、`tf2_roswiki`；不要把它们无差别复制到现有工作空间制造冲突。
3. 不运行 Arbotix、gazebo_ros_control 与当前直接差速插件同时控制同一轮关节。
4. 该差速插件没有本轮确认的指令超时停车机制。结束非零速度发布不等于停车，必须显式发零速度。
5. 历史对话里可能有不正确或过时的答题判断；原课件、当前文件与现场证据优先，不承诺考试满分。
6. 仓库现为公开，首次归档中的课程和个人材料仍在，未做全历史清理。公开可访问不等于取得公开再分发许可；风险见 [权利与隐私](RIGHTS_AND_PRIVACY.md)。

校验本地交接文件：`python3 tools/verify_archive.py`。完整来源与缺项见 [交接范围](context/COVERAGE_AND_LIMITS.md)。
