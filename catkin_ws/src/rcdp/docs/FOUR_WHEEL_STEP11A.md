# 四驱左右差速改造：step11A 实体模型预检

日期：2026-10-17（用户客户端日期）。用户已选择四轮驱动＋左右差速，继续使用 `/cmd_vel`，
不改成阿克曼转向。本轮暂停 GitHub 上传；此前本地整理保留，不提交／推送四轮内容。

## 分阶段做什么

1. **现在：导入并静态检查四轮实体模型**，不关闭原 step10，不改运行中的参数。
2. 预检通过后再单独启动 model-only launch，验收四轮、落地、稳定性。
3. 再接入**单个四轮驱动控制器**，所有四个关节实际参与驱动；保留 SimTime 时间戳修复。
4. 最后恢复单一关节状态／TF链、原激光和 RGB-D、轻量 RViz，验收前进／停车／转向与时间戳。

原差速插件的实现只操作两个轮关节，增加轮子外观不等于完成四驱。
本阶段没有加载驱动或传感器插件，不能用 `/cmd_vel` 运动验收，也不声称已有四驱实测。
不通过并排启动两个两轮插件解决四驱，避免重复 `/odom` 和根 TF。

## 本阶段几何

保留原双层圆盘、立柱、摄像头与雷达几何、质量假设及五个非车轮关节。
移除两个小球支撑轮和旧左右轮，新增四个等尺寸车轮：

| 车轮 | 关节 | 相对 base_link 的中心位置 (m) |
| --- | --- | --- |
| 左前 | front_left_wheel_joint | +0.20, +0.36, -0.10 |
| 右前 | front_right_wheel_joint | +0.20, -0.36, -0.10 |
| 左后 | rear_left_wheel_joint | -0.20, +0.36, -0.10 |
| 右后 | rear_right_wheel_joint | -0.20, -0.36, -0.10 |

X向前、Y向左、Z向上。所有关节轴为 `0 1 0`，圆柱 visual／collision 轴与之对齐。
轮径0.20m、轮宽0.08m沿用原驱动轮；初版轴距0.40m、轮距0.72m是本次教学起调尺寸，
不是实车尺寸或实验测量。原两轮驱动的轮距0.80m不能原样复制给新控制器。
以后若改尺寸，必须同步修改几何、控制器、预检和验收说明。

物理模型10links／9joints，含4个车轮活动关节和2个原传感器活动关节。
没有光学参考link或真实传感器插件；这些将在传感器集成阶段恢复。
总质量7.7kg是沿用原教学假设的计算值，不是测量值。
轮接触摩擦先沿用原0.8，侧滑／转向性能要在接驱动后依据实际仿真调试，不宣称此时已通过。

## 文件

- `urdf/gazebo/myrobot_4wd_base_step11a.xacro`：独立完整物理模型，不覆盖旧 step4或step10。
- `launch/myrobot_4wd_model_step11a.launch`：供下一步 model-only Gazebo验收，使用原室内world，不自动启动RViz/RSP/驱动。
- `scripts/check_4wd_model_step11a.py`：只读取新旧展开URDF，核验结构、轮位置、轴、惯量与保留部件。
- 本说明。

## 当前输入（原仿真保持运行）

将ZIP放在 `/home/thl/Lesson14_4wd_model_step11a.zip`，另开终端：

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_model_step11a.zip -d /home/thl/catkin_ws/src/rcdp
```

依次展开，任何一条报错就停止，不使用旧的/tmp文件继续验收：

```bash
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_gazebo_step4.xacro -o /tmp/lesson14_step11a_old_base.urdf
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_4wd_base_step11a.xacro -o /tmp/lesson14_4wd_step11a.urdf
python3 /home/thl/catkin_ws/src/rcdp/scripts/check_4wd_model_step11a.py /tmp/lesson14_4wd_step11a.urdf /tmp/lesson14_step11a_old_base.urdf
```

应输出 `wheel_joints_prepared:4`、`old_support_wheels_remaining:0`、`plugins:0`、
`nonwheel_links_and_joints_unchanged:true`、`basic_inertia_checks_passed:true`，结尾 `MODEL_PRECHECK_OK`。
这里 plugins 为0是故意的；既不是运行中的 step10 插件丢失，也不是已经四驱可动。

**回传预检后再继续。现在不启动新launch、不关闭旧仿真、不发运动命令、不重新安装ROS或Gazebo。**
这些模型文件不需要重新编译C++；后续真正四轮控制器需要单独编译和加载验证。

## 验证边界

本地 Xacro／XML／数学检查不能证明 Gazebo实际加载、四轮受力均匀或转弯成功。
接触高度是相对root的名义几何值，launch会额外在z=0.02m生成后落地；实际姿态需现场验收。
不改变已通过的step10插件，不覆盖系统库，保留回退入口。
ZIP条目固定2020-01-01以避免导入未来mtime，非文件创作时间。
