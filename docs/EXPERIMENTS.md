# 实验与验证记录

所有现场结果由用户在 VMware Ubuntu 中操作并提供；本地测试不替代现场验收。保留失败日志，避免只展示成功截图。

## 验证矩阵

| ID | 实验 | 主要结果 | 证据 |
| --- | --- | --- | --- |
| E01 | 物理模型与差速控制 | 模型为动态实体；低速前进后发送零速度并停止 | [早期复盘](../context/OPERATION_LOG_2026-10-14_15.md)、[模型截图](../evidence/gazebo_model_user_screenshot_2026-10-14.png) |
| E02 | 室内 world 与激光 | 5.495 Hz，360/360 样本有效；最近约 1.749 m | [启动附件](../evidence/logs/step7_launch_user_supplied.txt)、[终端记录](../evidence/logs/README.md) |
| E03 | Gazebo joint states 与 RSP/TF | 激光 TF 后续连通，RViz 模型／扫描正常 | [启动与警告附件](../evidence/logs/step8_launch_user_supplied.txt)、[TF/RViz 截图](../evidence/screenshots/step8_rviz_laser_2026-10-15.png) |
| E04 | RGB-D 基本数据 | 640×480；深度、XYZ 一帧各 307200 个有效值 | [RGB/Depth 截图](../evidence/screenshots/step9_rgb_depth_2026-10-16.png)、[数值摘要](../evidence/practice_2026-10-15_16.json) |
| E05 | CameraInfo 与短时频率 | 两类内参基本检查 True；RGB 10.051 / Depth 9.960 ROS Hz | [终端日志索引](../evidence/logs/README.md) |
| E06 | 大点云显示故障与恢复 | RViz -7/SIGBUS；Gazebo 存活；llvmpipe 基线稳定 | [问题复盘](PRACTICE_LOG_2026-10-15_16.md)、[终端日志索引](../evidence/logs/README.md) |
| E07 | 低负载预览 | 4800 点、153600 字节、约 1.712 墙钟 Hz；用户反馈稳定 | [验收摘要](../evidence/practice_2026-10-15_16.json)、[预览代码](../catkin_ws/src/rcdp/scripts/cloud_preview_step9a.py) |
| E08 | 最新运动回归 | 用户确认“正常 同步 稳定” | [两天复盘第 9 节](PRACTICE_LOG_2026-10-15_16.md)、[当前状态](../context/CURRENT_STATE.md) |
| T01 | 离线预览测试 | 9 个测试方法通过 | [测试代码](../tests/test_cloud_preview.py) |

## 怎样解读这些结果

- 截图显示哪个阶段，就只证明相应可见内容。没有最新轻量点云截图，不用 RGB-D 截图冒充。
- 样本全部有效不等于所有帧有效；数值格式正确不等于物理精度标定通过。
- 10 Hz ROS 仿真时间与约 1.7 Hz 墙钟不是同一计时标准；没有据此测出精确仿真倍率。
- 用户说“同步”是视觉联动验收，不是时间戳级同步误差测量。
- 0.1 m/s 持续 3 秒是脚本请求，不是测得严格前进 0.3 m。
- TF 的一段无重复样本不能否认之后重现的警告；软件预览可用也不代表原始 SIGBUS 根因已修复。

## 待验证事项

键盘遥控、转弯、实际轨迹／制动、长期显示压测、完整大点云显示故障定位、TF 重复戳定位、SLAM／保存地图／AMCL／导航均未验收。未来新增实验应记录环境、输入、输出、通过标准及失败情况，不覆盖本轮原始记录。
