# 课件、源码包与实践资料

## 2026-10-17 新增材料

- [公开提交材料](../submissions/2026-10-17-public/README.md)：报告DOCX/PDF、源码、五张PNG、运行说明和日志。
- [今日复盘](PRACTICE_LOG_2026-10-17.md)、[证据索引](../evidence/2026-10-17_4wd/README.md)。
- [阶段ZIP目录](../archives/2026-10-17_4wd/)：10份四轮原交付增量，以及公开脱敏提交包。
- [更新范围](../metadata/PROJECT_UPDATE_2026-10-17.json)。课件和Lesson13–15原始代码包已在仓库，不重复拷贝同版文件。

以下是既有资料索引，作为历史来源保留。

## 课件

最新提供的 Lesson11–15 已与本地原件逐份核对 SHA256 和页数，均为仓库已有的同版文件，因此不重复保存第二份。它们是 PDF，不是原生可编辑 PPTX。

| 课件 | 页数 | 项目衔接 |
| --- | ---: | --- |
| [Lesson11](../courseware/Lesson11.pdf) | 71 | ROS 实践基础，按既有索引查具体主题 |
| [Lesson12](../courseware/Lesson12.pdf) | 123 | TF 等后续实践基础，按既有索引查原页 |
| [Lesson13](../courseware/Lesson13.pdf) | 73 | URDF/Xacro 模型与展示基础 |
| [Lesson14](../courseware/Lesson14.pdf) | 48 | Gazebo 模型、驱动、传感器与 RViz 衔接 |
| [Lesson15](../courseware/Lesson15.pdf) | 37 | 建图／导航参考，当前尚未实际验收 |

共 352 页。完整 Lesson1–15 共 1682 页，见 [课件目录](../courseware/README.md)。具体参数仍须回原页核对，不以本项目简介代替课程内容。

## 原始课程代码

| 包 | 用途 | 当前使用方式 |
| --- | --- | --- |
| [Lesson13 原包](../reference/Lesson13_code_original.zip) | 课程模型／展示参考 | 原 rcdp 为当前模型基础 |
| [Lesson14 原包](../reference/Lesson14_code_original.zip) | Gazebo 场景、驱动与传感器参考 | 分析后逐阶段适配，未整包覆盖 |
| [Lesson15 原包](../reference/Lesson15_code_original.zip) | 另一套 rs_gazebo 及 rs_nav | 保留参考；导航未导入验收 |

Lesson14/15 共有包内容重复；不要把两个 catkin_ws 整体解压到现有 src，也不要将 rs_gazebo 与当前模型同时绑定根命名空间 /cmd_vel。

## 已使用的阶段增量

见 [阶段包索引](../archives/README.md)。这些是逐次交付的增量，不是独立完整工作空间；恢复需要先有原模型／前置阶段。当前有效合并源码在 `catkin_ws/src/rcdp/`，所用室内 world 也已补入。

step10 新增独立 [rcdp_stampfix 包](../catkin_ws/src/rcdp_stampfix/README.md)，不覆盖系统驱动库；
[插件源码 ZIP](../archives/Lesson14_stampfix_step10.zip) 与 [切换 ZIP](../archives/Lesson14_stampfix_switch_step10.zip) 的解压目标不同，见索引。GitHub 不含用户编译的 `.so`，来源和 BSD 许可随源码保留。

## 截图与日志

- [截图索引](../evidence/screenshots/README.md)：基础模型旧图＋本次新增的 TF/RViz、RGB-D 两图；逐张标出能证明和不能证明的内容。
- [日志索引](../evidence/logs/README.md)：2 份原始用户文本附件，22 条用户终端消息。保留报错、警告、数值和来源时间，不冒充完整 VM 日志目录。
- [实验矩阵](EXPERIMENTS.md)：将能力与对应证据连接。
- [资源元数据](../metadata/RESOURCE_INDEX_2026-10-16.json)：原件／阶段包 SHA256、页数、CRC、来源类别。
- [时间戳修复证据](../evidence/timestamp_fix_step10/README.md)：修复前与两轮修复后完整诊断 JSON、构建与部署记录；不包含新截图或未提供的 VM 日志。

## 权利与复现边界

按用户新要求在现有公开项目集中保存所提供的学习材料。课件和原始代码保持来源／权利归属，没有全仓统一开源许可；请勿据仓库可访问就推断另有转载授权。截图和日志含课程 VM 用户名／路径，由用户本次明确要求上传；不包含凭据或内部会话内容。

本仓库不是 VM 镜像，也没有取得全部其他包的现场文件。详情见 [权利与隐私](../RIGHTS_AND_PRIVACY.md) 及 [当前范围](PUBLIC_UPDATE_SCOPE.md)。
