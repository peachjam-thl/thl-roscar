# 原始参考文件

`Lesson13_code_original.zip` 是用户提供的 Lesson13_code(1).zip，保留原字节。包含 beginner_tutorials、rcdp、ros_bilibili、tf2_roswiki 四个包。本轮只导入 rcdp；另外三个不要直接覆盖现有工作空间。ZIP里的旧构建配置不代表当前机器环境。

2026-10-16 按用户新要求补齐 `Lesson14_code_original.zip`、`Lesson15_code_original.zip`。两份原件字节保持不变、CRC 通过。Lesson14 有四个包；Lesson15 还有另一版 rs_gazebo 和 rs_nav。它们不是两套必须全部复制进当前工作空间的程序。已用功能通过增量适配接入 rcdp；rs_nav 和参考地图尚未完成现场导航验收。

ZIP 内可能包含老师机器的绝对路径、旧配置、地图和占位许可证；保留原文件以便追溯，不将旧路径当作当前部署值，不授予全包统一开放许可。详见 [资料导航](../docs/RESOURCES.md) 和 [阶段包](../archives/README.md)。

`legacy/` 是早期Shell练习交付包，保留用于历史任务衔接，含个人课程信息，勿公开。

课件在 courseware，当前有效的 rcdp 源副本在 catkin_ws/src/rcdp。原始ZIP和阶段增量包均保留，不把补充文件伪称老师原代码。
