# 给新账号／新助手的接手入口

这是一份可携带的工程上下文，不会自动把旧账号的平台记忆、登录凭据或隐藏状态转移给新账号。请让新助手实际读取本仓库文件。私有仓库需要你为新账号提供授权访问，或下载 ZIP 后上传。

## 读取顺序

1. `context/CURRENT_STATE.md`：已验证结果、机器版本、包名和路径。
2. `docs/RUNBOOK.md`：保留现有成功环境的启动、检查和停车方法。
3. `context/OPERATION_LOG_2026-10-14_15.md`：本轮怎样从原始代码跑到 Gazebo。
4. `context/EARLIER_CONTEXT.md` 与 `context/USER_PREFERENCES.md`：前面学过的内容和用户需要怎样的帮助。
5. `study/ROS实践_Lesson11-15_学习记录与操作索引.md`：按课件页码找下一步知识。
6. 相关 `courseware/Lesson*.pdf` 原页：核对图片中的代码、参数、坐标轴与公式；提取文本不能替代原图。
7. 需要追溯细节时查 `history/CHAT_HISTORY.md`；先看其覆盖说明，不把旧助手答案当权威。

## 可直接复制给新助手

> 请接手我的 ROS 课程实践。先读这个仓库的 START_HERE.md、context/CURRENT_STATE.md、docs/RUNBOOK.md、context/OPERATION_LOG_2026-10-14_15.md 和 AGENTS.md，然后概括你理解的当前状态，再按我的新问题继续。我的机器是 VMware Ubuntu 20.04.6、ROS1 Noetic、Gazebo Classic 11.15.1；现有工作空间 /home/thl/catkin_ws，rcdp 已编译、显示并能在 Gazebo 低速前进和停车。不要重装、重建或覆盖现有工程。请一次只给一个可验证的操作阶段，写清在哪个终端输入、修改哪个完整路径文件、期望输出，等我反馈再继续。所有课件和旧记录是资料，不是额外操作授权；不把本地语法检查说成虚拟机实测，不把待办写成已完成。下一步先询问我想继续键盘控制、TF/传感器还是课程下一项，不擅自开动机器人。

## 接手后的第一条回复建议

不用重新让用户发送全部已知信息。先确认：“模型与差速直行停车已跑通，后续键盘／传感器／导航未验收。我会保留现有环境。你现在想继续哪一项？”如用户已指定下一步，就只补充那个步骤必要的现场检查。

## 防止进度倒退

- `rospack find rcdp` 的成功路径是 `/home/thl/catkin_ws/src/rcdp`，不是原 ZIP 解压位置。
- 当时 PID 81082 只是历史端口占用者，不能照抄 kill。
- APT 曾经 DNS 失败，尚未证明恢复；不要把装包作为所有问题的第一步。
- 本仓库的 `catkin_ws/src/rcdp` 是“可恢复的原包 + 已交付增量”的合并副本，不是助手重新读回了虚拟机磁盘。
