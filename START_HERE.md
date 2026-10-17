# 新助手接手入口 2026-10-17

先读[当前状态](context/CURRENT_STATE.md)、[今日复盘](docs/PRACTICE_LOG_2026-10-17.md)、[运行手册](docs/RUNBOOK.md)、[原记录](evidence/2026-10-17_4wd/README.md)、[AGENTS约定](AGENTS.md)。旧step10、相机和点云文档均为历史背景，不覆盖当前四轮阶段。

## 可复制给新助手

> 请接手我的ROS1 Noetic / Ubuntu20.04.6 / Gazebo Classic11.15.1项目。已改成四个独立驱动轮，10 Link、9 Joint，轮径0.20m、轴距0.40m、轮距0.72m。独立rcdp_4wd_stampfix已在VM编译加载；原工作空间/home/thl/catkin_ws，当前myrobot_4wd_laser_step11i.launch friction_model:=cone_model，再单独软件渲染打开lesson14_scan_step8.rviz，节点lesson14_4wd_rviz。/cmd_vel、/odom、/scan不变，驱动独占odom→root_link，六关节Gazebo实测再由RSP生成内部TF。前进和左右转／停止已记录，摩擦A/B仅为单次比较；H/I全树约40秒审计无观测时间戳异常，雷达约5.495Hz、360有效样本。四轮相机和点云尚未恢复，SLAM导航未开始。先读CURRENT_STATE和RUNBOOK，确认VM现场，不用旧PID、不叠加旧Launch、一次一步等我反馈。源码保留上游BSD，不覆盖/opt/ros。GitHub有五张实拍、日志和15页脱敏报告，没有姓名／班级／学号新报告，也不含.so或VM镜像。独立提交副本入口仅离线验证，不能冒充干净Ubuntu端到端通过。

## 防止误判

- 根TF由四驱插件拥有，内部关节边由RSP拥有；/tf两个发布者本身正常。
- step11A仅实体，C驱动，D/E/G有限运动，F摩擦A/B，H关节/TF，I雷达；不要把A当作完整运行配置。
- 配置文件沿用step8名字但读取当前robot_description，不表示恢复旧两轮模型。
- 四轮没有相机光学link；历史rotate_depth_camera_link和点云恢复步骤暂不适用。
- 本次用户选择公开脱敏上传；本地原件不上传，不重写既有Git历史。旧历史未全量脱敏。
- 视频用户自行处理；不伪造演示。下一阶段由用户决定，不自行导航或驱动车辆。
