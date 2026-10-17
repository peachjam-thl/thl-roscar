# Step11F：转向侧偏的单变量摩擦模型对照，先做文件预检

客户端日期：2026-10-17。当前仅新增独立实验文件，不上传 GitHub、不改旧模型/驱动/世界，不切换运行中的 Gazebo。

## 事实、假设和未完成项

用户已确认四轮低速直行、左转和发零后停车；左转日志测得：净偏航 +27.7185°，起止净平移 0.0738416 m，主要向初始车体侧向偏移。四轮方向正确，停车采样通过，但净平移超过此前设定的 0.05 m 初步诊断参考，并非严格原地旋转。0.05 m 是本项目的初步参考，不是课程或硬件标准。

实际 ROS 物理查询：步长 0.001 s、max_update_rate=1000、未暂停、重力 -9.8、PGS 迭代 50、SOR=1.3、CFM=0、ERP=0.2、contact_surface_layer=0.001 m、全局 contact_max_correcting_vel=100。

这些数值不单独证明配置错误。尤其全局 contact_max_correcting_vel 是接触穿透修正速度上限，不是小车指令速度；当前轮子还显式设置了 maxVel=0.1，不能把全局 100 直接认定为侧偏原因。

本地现有模型中四轮 mu1=mu2=0.8，未显式设置 fdir1。原世界也没有显式指定 friction_model。Gazebo 官方资料说明默认 pyramid 摩擦模型的默认摩擦方向依赖世界 X/Y 轴，可能带来方向相关的表现；cone 模型采用不同的耦合摩擦求解方式。

因此提出可检验假设：接触摩擦模型的方向相关性可能参与了侧偏。**尚未确认主因，也不保证切到 cone 后偏移减小。** ROS get_physics_properties 不返回 friction_model，不能声称该服务已经确认当前活动的摩擦模型。

资料依据：

- [Gazebo Classic Physics Parameters](https://classic.gazebosim.org/tutorials?tut=physics_params)：摩擦方向、pyramid/cone，以及局部/全局接触修正上限。
- [Gazebo Classic Friction](https://classic.gazebosim.org/tutorials?tut=friction)：mu/mu2 含义、接触双方取较小值。
- [Gazebo 11.15.1 官方 ODE 实现](https://github.com/gazebosim/gazebo-classic/blob/gazebo11_11.15.1/gazebo/physics/ode/ODEPhysics.cc)：支持 pyramid_model、cone_model、box_model。

cone 只使用 mu，而不是与 pyramid 完全相同的两个独立方向约束。这是此次实验被改变的求解语义，不能说两个引擎设置物理上完全等价；当前四轮两方向系数均为 0.8，为此对照提供了简单基线。

## 新增文件

```text
worlds/lesson14_4wd_pyramid_model_step11f.world
worlds/lesson14_4wd_cone_model_step11f.world
launch/myrobot_4wd_friction_step11f.launch
scripts/check_4wd_friction_step11f.py
docs/FOUR_WHEEL_STEP11F.md
```

两个 world 都复制自现有 lesson14_box_house_step7.world，只显式增加 physics/ode/solver/friction_model；A 为 pyramid_model，B 为 cone_model。房间/障碍物/保存状态、地面材料及摩擦、步长/更新率全部保留。不额外设置求解器迭代、SOR、CFM、ERP、接触修正值，不增加插件。

新 launch 沿用 Step11C 的原机器人 Xacro、同一驱动库和同一出生位姿；只新增对照世界选择参数，默认选择 A。没有新增加速斜坡、命令超时保护、传感器或 RViz。

## 当前只导入和预检

将压缩包复制到虚拟机 `/home/thl/Lesson14_4wd_friction_step11f.zip`，当前 Gazebo 保持运行。在新终端逐条执行，报错则停止：

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_friction_step11f.zip -d /home/thl/catkin_ws/src/rcdp
python3 /home/thl/catkin_ws/src/rcdp/scripts/check_4wd_friction_step11f.py
```

成功末行应为 PRECHECK_OK，drive_library_matches_last_user_report 应为 true。
脚本只读 XML/文件/哈希，不连接 ROS、不改参数、不启动/关闭 Gazebo、不发运动指令。不需要重新编译，也不覆盖旧文件。

若驱动库哈希与用户此前提供的 1265cba9... 不同，提示 PRECHECK_REVIEW；不自动恢复库，不据此认定库损坏，请先反馈。
XML 预检不能代替 Gazebo 原生 SDF 解析和运行验收；摩擦设置的实际效果尚待后续运行核对。

先把完整预检结果发回，**现在不要运行新 launch**。

## 后续实验设计（尚未执行）

预检通过后分开指导，每一步正常停止旧 Gazebo，确认端口释放，禁止同时启动两套。

1. 从新启动的 A/pyramid 世界开始，等待车体静止；保持当前 100 Hz 驱动、5 N·m 每轮扭矩、相同轮距和轮径。
2. 顺序运行现有 Step11D 直行脚本、Step11E 左转脚本，保留完整日志及初始/结束位姿、轮速、实测墙钟时长和停车结果。
3. 正常退出 A，启动 B/cone，从同一出生位姿/初始朝向开始，重复相同的静置和 D→E 顺序。不要在已经转过的姿态上直接当作另一组公平对照。
4. 比较净平移、净偏航、实际车体转速、直行表现、轮速和停车；不只比较绝对平移，也看转角是否变小，避免把“转得更少”误认为转向改善。
5. 单次差异只能说明初步现象；如 B 有改善，再重复核对并测试右转、四轮 TF/odom 时间戳，然后才决定保留哪种配置并恢复传感器。

如果没有改善，保持旧文件可回退，不把假设写成已确诊，不同时修改摩擦系数、接触方向、扭矩与迭代次数。
现有 7.38 cm 左转记录保留为历史观察；正式 A/B 需要各自重新从一致状态采集，不能混用不同起点或轮子相位后声称严格因果。

控制命令仍由现有测试脚本限时发送并显式发零；驱动本身仍无命令超时自动停车。异常时按一次 Ctrl+C 等脚本发零；如仍不停，立即暂停 Gazebo 并反馈，不直接恢复运行。
