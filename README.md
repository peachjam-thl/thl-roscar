# thl roscar

ROS 1 Noetic 课程与 Gazebo 小车实践的私有交接仓库。整理日期：2026-10-15（中国时间；本轮实践跨 10 月 14 日晚至 15 日凌晨）。

**新账号／新助手先读 [START_HERE.md](START_HERE.md)，再读 [当前状态](context/CURRENT_STATE.md) 和 [运行手册](docs/RUNBOOK.md)。不要从零重装或重新建包。**

## 现在已经做到哪里

- Ubuntu 20.04.6 LTS + ROS 1 Noetic + Gazebo Classic 11.15.1。
- 用户现有工作空间 `/home/thl/catkin_ws`，功能包 `/home/thl/catkin_ws/src/rcdp`。
- `rcdp` 已构建成功，模型 `lesson13_robot` 已在 Gazebo 显示。
- 差速插件订阅 `/cmd_vel`；用户运行测试脚本后明确反馈“向前移动且停止”。
- 这是用户现场截图、终端输出和反馈支持的结果，不是助手直接接入虚拟机测量；实际位移和速度未量化。
- 下一步可选键盘控制，之后才是完整 TF、真实雷达／相机数据、建图和导航。这些还没有验证，不能冒充完成。

## 仓库内容

| 目录 | 内容 |
| --- | --- |
| `courseware/` | Lesson1–15 原始 PDF，共 1682 页；不是原生 PPTX |
| `study/` | Lesson11–15 学习索引、既有笔试复习 PDF、可检索逐页文本和覆盖记录 |
| `catkin_ws/src/rcdp/` | 原始 rcdp 源码 + 第四步物理模型和第六步差速驱动新增文件 |
| `reference/` | 用户提供的 Lesson13 原始 ZIP（含四个包，仅作原始参考） |
| `archives/` | 当时给用户导入的两份增量 ZIP |
| `context/`、`docs/` | 当前状态、操作复盘、旧知识与排错、运行与接手步骤 |
| `history/` | 可恢复的用户／助手公开对话导出、用户图片和覆盖说明 |
| `evidence/` | 用户现场反馈、Gazebo 截图及本地静态检查报告 |
| `metadata/` | 文件清单、页数、校验值与来源边界 |

## 快速继续（已有 Ubuntu 环境）

启动终端：

```bash
source /home/thl/catkin_ws/devel/setup.bash
roslaunch rcdp myrobot_drive_step6.launch
```

另开终端先检查：

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
6. 本仓库含个人学习记录与课程材料，应保持私有。课件与原始课程代码的权利仍归原作者，未授予公开再分发许可。

校验本地交接文件：`python3 tools/verify_archive.py`。完整来源与缺项见 [交接范围](context/COVERAGE_AND_LIMITS.md)。
