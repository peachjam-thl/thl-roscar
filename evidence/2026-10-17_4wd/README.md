# 2026-10-17 四轮实践证据

## 五张真实截图

1. [模型Xacro源码与部分结构树](screenshots/01_URDF_Xacro四轮机器人模型结构.png)
2. [RViz模型和激光扫描](screenshots/02_RViz机器人模型可视化.png)
3. [Gazebo房间与障碍物](screenshots/03_Gazebo仿真场景.png)
4. [Gazebo模型加载](screenshots/04_Gazebo机器人加载结果.png)
5. [Gazebo运行状态](screenshots/05_Gazebo机器人运行验证.png)

来自用户本次提供的PNG，内容及像素不改，只统一编号。图1终端只展示结构树下部，完整10 Link／9 Joint关系另据源码解析。Gazebo蓝线为雷达射线，RViz红点为激光观测；不是SLAM地图。静态截图不单独证明前进、转角或停车。

## 终端证据

`user_pasted_logs/` 中7份用户粘贴终端文本：A_forward、A_left_turn、B_forward、B_left_turn、B_right_turn、H_full_tf_audit、I_full_tf_audit。不是从VM直接完整导出的.ros日志。

[parsed_metrics.json](parsed_metrics.json)保留其JSON数据；[conversation_excerpt.md](conversation_excerpt.md)为用户直接消息的补充摘录，包含雷达、场景、哈希和库环境核查，不伪装成原始完整日志。

A/B均是一次主要记录，净平移不是轨迹长度或侧滑率。A左转脚本退出2是超过自设5cm参考，运动和停车样本仍有记录；保留失败参考不只展示“全绿”。H/I审计不订阅/scan，不冒充联合传感器40秒压力测试。

## 来源和隐私

原始截图无姓名／班级／学号可见项，终端保留课程VM用户名、路径和历史服务地址。本次公开报告移除个人身份字段，但并非对旧仓库历史的全量隐私清理。现场结果由用户提供，本地Windows只做源码、文档和归档检查。
