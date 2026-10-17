# 实验与验证记录

## 2026-10-17 四轮测试

| 场景／动作 | 平面净位移m | 航向变化度 | 停止样本 |
| --- | --- | --- | --- |
| A pyramid 前进 | 0.239226 | 近零 | 通过 |
| A pyramid 左转 | 0.073715 | +27.6363 | 通过，超过自设5cm参考而退出2 |
| B cone 前进 | 0.240039 | 近零 | 通过 |
| B cone 左转 | 0.012273 | +25.9996 | 通过 |
| B cone 右转 | 0.012240 | −25.9987 | 通过 |

单次A/B，不是路径长度、侧滑率或统计显著性；车体角速度仍低于命令。H/I两次约40秒全树检查无观测时间戳异常；I审计不订阅scan，雷达另做样本和频率检查。[原记录](../evidence/2026-10-17_4wd/README.md)。

下文保留旧阶段实验边界，不将两轮相机结果自动继承为四轮功能。

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
| E08 | step9/9a 期间运动回归 | 用户确认“正常 同步 稳定”；不是新插件部署后的运动回归 | [两天复盘第 9 节](PRACTICE_LOG_2026-10-15_16.md)、[当前状态](../context/CURRENT_STATE.md) |
| E09 | 原始重复戳诊断 | 根TF重复3、odom重复2；同源且同刻位姿改变 | [修复前 JSON](../evidence/timestamp_fix_step10/before_fix.json) |
| E10 | 新插件构建与加载 | VM 构建／依赖／URDF预检通过；进程 maps 确认新库 | [验收记录](TIMESTAMP_FIX_STEP10.md)、[部署记录](../evidence/logs/step10_deployment_user_reported.txt) |
| E11 | step10 未开 RViz 短测 | 40.079秒；TF3386／odom3387；重复倒退均0 | [首轮 JSON](../evidence/timestamp_fix_step10/after_no_rviz.json) |
| E12 | step10 恢复显示负载短测 | 40.048秒；TF3428／odom3429；均0，用户“稳定 没出现” | [第二轮 JSON](../evidence/timestamp_fix_step10/after_preview.json) |
| T01 | 离线预览测试 | 9 个测试方法通过 | [测试代码](../tests/test_cloud_preview.py) |
| T02 | 离线诊断／补丁／预检测试 | 原始戳聚合、允许修改范围、错误依赖／模型拒绝；不替代VM运行 | [测试目录](../tests/) |

## 怎样解读这些结果

- 截图显示哪个阶段，就只证明相应可见内容。没有最新轻量点云截图，不用 RGB-D 截图冒充。
- 样本全部有效不等于所有帧有效；数值格式正确不等于物理精度标定通过。
- 10 Hz ROS 仿真时间与约 1.7 Hz 墙钟不是同一计时标准；没有据此测出精确仿真倍率。
- 用户说“同步”是视觉联动验收，不是时间戳级同步误差测量。
- 0.1 m/s 持续 3 秒是脚本请求，不是测得严格前进 0.3 m。
- TF 的一个无重复窗口不能证明永久无故障。step10 两轮独立短测通过，不冒充连续80秒或长期运行；软件预览可用也不代表原始 SIGBUS 已修复。

## 待验证事项

键盘遥控、补丁后非零运动回归、转弯、轨迹／制动量化、长期显示／时序压测、reset／回放、完整大点云崩溃定位、SLAM／保存地图／AMCL／导航均未验收。未来实验记录完整环境与失败情况，不覆盖本轮原始记录。
