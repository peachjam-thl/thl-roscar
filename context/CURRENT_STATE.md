# 当前状态 2026-10-17 四轮版

目前已到step11I：四轮四驱＋实测关节状态＋TF＋激光雷达，cone_model场景，软件渲染RViz。用户确认重启后车与墙体恢复、RViz正常，并补交5张当前四轮版截图。本次最后任务是公开脱敏归档上传，不自动进入相机或导航阶段。

## 环境与实际文件

- 用户VMware：Ubuntu20.04.6、ROS1 Noetic、Gazebo Classic11.15.1、RViz1.14.26。
- 原工作空间/home/thl/catkin_ws，模型包rcdp，当前驱动包rcdp_4wd_stampfix。
- 当前原入口：myrobot_4wd_laser_step11i.launch friction_model:=cone_model；它不自动开RViz。
- RViz：LIBGL_ALWAYS_SOFTWARE=true，lesson14_scan_step8.rviz，节点lesson14_4wd_rviz，Fixed Frame=odom。
- 当前World：lesson14_4wd_cone_model_step11f.world；模型lesson13_robot。
- /cmd_vel、/odom、/joint_states、/scan；没有已恢复的四轮相机图像或点云。

## 实体和控制

- 四个同尺寸独立驱动轮，无旧小支撑轮；10 Link、9 Joint，6活动关节。
- 轮径0.20m、宽0.08m，轴距0.40m、轮距0.72m；每轮质量0.3kg，模型总设定质量7.7kg，不是实物测量。
- 四个continuous轮关节轴均0 1 0；相机安装revolute范围±π，雷达安装continuous；转台尚未主动控制。
- 四电机插件源自官方gazebo_ros_pkgs2.9.3，保留BSD；100Hz配置、每轮5Nm，轮速分配v±w×0.72/2再除0.10。
- /odom为Gazebo世界真值；驱动独占odom→root_link并用SimTime秒／纳秒；六个关节由Gazebo50Hz配置实测，经一个RSP发布内部TF。
- 已加载库用户报告SHA256：1265cba90fa07463d7f8af80decdf33bbf47a916a113fe7fdb51599699a9424c。仓库无该编译.so，需目标机重新编译。

## 已有运行证据

1. 实体、四驱库、/cmd_vel订阅与模型关节映射已逐阶段检查。
2. A/pyramid前进0.239226m；左转净平移0.073715m、+27.6363度，停车样本通过。脚本退出2因为超过自设5cm参考，不是崩溃或老师标准。
3. B/cone前进0.240039m；左转净平移0.012273m、+25.9996度；右转0.012240m、−25.9987度，停车样本通过。单次A/B减少约83.35%，不是重复试验统计。
4. H全树40.047秒：根TF3990、关节状态1995；I全树40.049秒：根TF3984、odom3984、关节状态1992、clock39844。7条动态边无观察到重复／倒退，3条静态关系不变。该脚本不订阅/scan，不把它写成联合传感器压力测试。
5. 激光独立检查约5.495Hz，frame=laser_scan_link，360有效样本、NaN/正无穷均0，角度−3..3rad，距离0.1..30m，最近1.6867m、最远8.9694m。
6. 重启前3份World哈希匹配；重启后9个运行模型，box_house四面墙与四碰撞几何完整。未覆盖World源文件。
7. 五张最新截图已交；15页六章报告和可复现工程副本已生成。公开版移除姓名、班级、学号；视频未处理。

所有现场结果来自用户终端与截图，不是助手直接连入VM。完整记录见[evidence](../evidence/2026-10-17_4wd/README.md)和[今日复盘](../docs/PRACTICE_LOG_2026-10-17.md)。

## 排错和边界

- libRayPlugin.so预检缺失是动态库搜索环境，加载Gazebo官方setup.sh后通过；不写成重装Gazebo。
- 初次tf_echo可能短暂1ms缓存外推，随后持续正常；不凭初始化报错添加多余静态TF。
- 旧lesson14_rviz有注册残留／拒绝连接；新四轮RViz显示正常，未记录执行全局cleanup。
- 原始307200点点云SIGBUS仍未定位；历史两轮RGB-D／轻量预览可用不等于四轮已恢复。
- 长时、reset、实物标定、精确轨迹跟踪、四轮相机、SLAM与导航均未完成。
- 原工作空间入口含/home/thl固定库路径；提交副本新增路径适配入口只做离线等价检查，不能当作干净Ubuntu端到端通过。

## 继续工作规则

按用户新请求一次一步；先当前只读检查，不拿旧PID／topic输出当实时状态。不重启正常仿真，不叠加两驱动，不修改/opt/ros，不整包覆盖旧包。非零运动前看/cmd_vel，结束显式发零。新账号不继承登录，GitHub只保存工程上下文，不导出内部会话或凭据。

历史两轮状态已保存在[step10快照](history/CURRENT_STATE_STEP10_2026-10-16.md)，不作为当前默认配置。
