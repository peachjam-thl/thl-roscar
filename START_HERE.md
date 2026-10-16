# 给新助手的接手入口（2026-10-16）

这是工程上下文，不会自动迁移旧账号记忆、登录或隐藏状态。读取仓库后再继续，不凭旧快照判断当前虚拟机仍在线。

## 读取顺序

1. [当前状态](context/CURRENT_STATE.md)：最新通过项、未解决项和暂停点。
2. [10 月 15–16 日实践复盘](docs/PRACTICE_LOG_2026-10-15_16.md)：做了什么、怎么做、问题与处理。
3. [运行手册](docs/RUNBOOK.md)：保留已成功配置的启动／检查／停车方法。
4. [公开更新范围](docs/PUBLIC_UPDATE_SCOPE.md) 和 [AGENTS.md](AGENTS.md)：用户授权及执行边界。
5. `context/OPERATION_LOG_2026-10-14_15.md`：更早的模型、端口排错及初次差速测试。
6. `study/`：课件索引和历史复习资料；具体运行进度以 CURRENT_STATE 为准。
7. `history/README.md`：旧聊天导出的截点。后续两天只以本次脱敏文档衔接，不伪称已全量追加聊天。

## 可直接复制给新助手

> 请接手我的 ROS1 Noetic / Ubuntu 20.04.6 / Gazebo Classic 11.15.1 课程实践。先读 START_HERE.md、context/CURRENT_STATE.md、docs/PRACTICE_LOG_2026-10-15_16.md、docs/RUNBOOK.md 和 AGENTS.md。现有工作空间是 ~/catkin_ws，包为 rcdp，模型 lesson13_robot，控制 /cmd_vel，雷达 /scan。step9 RGB-D 数据和光学 TF、step9a 软件渲染轻量点云、受控前进／停车视觉联动已经由我反馈通过。原始完整点云曾使 RViz SIGBUS 退出，偶发 odom→root_link 重复时间戳警告还没定位，不能说彻底解决。当前先暂停后续实践，不擅自安装或启动键盘、建图、定位、导航。之后按我的新请求一次给一个可验证阶段，写清终端、文件路径、预期输出，等我反馈。保留现有工程，不整包覆盖课程代码，不混入 rs_gazebo。仓库按我的新要求补齐课件、所用代码包、截图和用户终端记录；资源索引在 docs/RESOURCES.md，不能上传凭据、内部会话、隐藏推理或未提供的 VM 文件。

## 防止进度倒退

- step4 是物理模型；step6 是驱动；step7 雷达；step8 真实关节状态与 TF；step9 RGB-D；step9a 独立轻量点云预览。
- 只有一个 Gazebo、一个差速插件、一份 robot_description、一份 robot_state_publisher；不要叠加旧 launch。
- 正常情况下 `/tf` 有 Gazebo 和 RSP 两个发布节点可以合理：它们应拥有不同的 TF 边，不是按发布节点数量直接判冲突。
- 当前使用软件渲染的低负载预览，不要重新默认勾选原始 307200 点大点云。
- 重新启动时可用 `start_rviz:=false`，再单独开预览；这是现有开关的整理用法，完整冷启动组合尚未单独复测。
- APT/DNS 故障未确认恢复；teleop_twist_keyboard 之前缺失，不能把未来检查写成已经安装。
- 重新遇到端口占用，重新查 PID，不照抄旧记录或 killall。
- 室内课程 world、所用阶段 ZIP 和 Lesson14/15 原包已按新要求补齐；课件 Lesson11–15 与已有副本一致。参看 docs/RESOURCES.md，不整包覆盖旧工程，不把参考导航包说成已跑通。
- 代码是“原包＋已交付补充文件”的合并，不是从 VM 逐字读回的镜像。精确位移、长时稳定性、真实相机标定均未完成。
