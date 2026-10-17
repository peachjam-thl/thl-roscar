# step10 时间戳修复证据

来源：用户在本对话中亲自执行 Ubuntu VM 命令后贴出的数据。JSON 是对其消息中完整诊断对象的忠实转录，
不含助手的内部会话、工具结果或推理。未提供精确消息 UTC，故不补造采样日期／开始时刻。
日志中的秒数属于 ROS 仿真时间或明确标注的墙钟观测，不与 Windows 文件时间混用。

| 文件 | 含义与边界 |
| --- | --- |
| [before_fix.json](before_fix.json) | 旧插件40秒窗口：根TF重复3、odom重复2，均同源且位姿改变；clock无重复／倒退 |
| [after_no_rviz.json](after_no_rviz.json) | 实际加载新库后的首轮40.079秒窗口，未恢复 RViz，全部重复／倒退计数0 |
| [after_preview.json](after_preview.json) | 恢复轻量预览与软件 RViz 后40.048秒窗口，全部计数0；用户反馈“稳定 没出现” |
| [构建附件](../logs/step10_build_user_supplied.txt) | 用户原始文本附件，字节保留；含构建成功和未来文件时间警告 |
| [ldd 后半段附件](../logs/step10_ldd_tail_user_supplied.txt) | 仅后半段，不冒充完整依赖检查；后续预检给出了完整依赖通过摘要 |
| [部署消息整理](../logs/step10_deployment_user_reported.txt) | 用户预检输出、新启动／订阅信息、maps 新库映射；不是整个 VM 日志目录 |

前后观察的负载条件不完全相同，不将它们当作严格受控性能对照。
新旧展开模型仅库路径不同、实际新库已加载、原始消息短测与用户视觉反馈共同支持本阶段通过。
两次修复后窗口彼此独立，不冒充连续80秒压测；没有新增运动、长期、reset或回放验收。

[完整修复说明](../../docs/TIMESTAMP_FIX_STEP10.md) · [当前状态](../../context/CURRENT_STATE.md)
