# 本轮实践操作复盘（10 月 14 日晚至 15 日凌晨）

本日志总结真实对话记录；“已做”以现场反馈为依据。“补充代码”指助手为连接 Lesson13 模型与 Lesson14 Gazebo 流程新增的文件，不冒充老师原文件。

## 1. 原始材料和环境确认

用户提供 Lesson11–15 PDF 和 `Lesson13_code(1).zip`，要求逐阶段给终端命令，最后在 Gazebo 运行。确认 Ubuntu 20.04.6、Noetic、Gazebo 11.15.1；`rospack find gazebo_ros` 返回 `/opt/ros/noetic/share/gazebo_ros`。现有 catkin_ws 存在，但最初没有 rcdp。

用户把 ZIP 解压进 `/home/thl`，查得：

```text
/home/thl/Lesson13_code/catkin_ws/src/rcdp/package.xml
```

只把 `rcdp` 导入现有 `/home/thl/catkin_ws/src`，保留已有工程，未无差别导入 ZIP 内的另外三个包。成功 `catkin_make` 后 source 当前 devel，`rospack find rcdp` 返回正确 active 路径。

## 2. 原代码为何不直接当 Gazebo 动力学模型

原始课程 rcdp 主要是 Lesson13 的 URDF/Xacro/RViz/Arbotix 展示：10 links、9 joints，有视觉几何，但不能把可显示外形当成完整物理仿真、驱动和传感器功能。先检查原链接／关节／尺寸，再按阶段新增，不覆盖原始文件。

### 第四步新增

- `urdf/gazebo/myrobot_gazebo_step4.xacro`
- `launch/myrobot_gazebo_step4.launch`
- `worlds/lesson13_flat_step4.world`

物理模型补齐 collision 和合理的质量／惯性，保留链接、关节命名和双层几何。本地平地＋光照 world 不依赖外部在线模型下载。加入的质量是教学仿真假设，不是实物称重：总质量约 7.2 kg。支撑轮用低摩擦近似，不宣称逼真万向轮接触。

原代码底盘长 0.2 m、立柱长 0.4 m，与课件截图某些 0.3/0.8 参数不同；本轮按实际原代码建立连续方案。摄像头 Z 轴限位改为 ±π 对应练习所要求 ±180°，不是将 ±1.57 当作 ±180°。

## 3. 增量包导入与可选检查器问题

用户把 `Lesson13_Gazebo_step4.zip` 放 Ubuntu 桌面，执行：

```bash
unzip -n "$HOME/桌面/Lesson13_Gazebo_step4.zip" -d /home/thl/catkin_ws/src/rcdp
source /home/thl/catkin_ws/devel/setup.bash
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_gazebo_step4.xacro > /tmp/lesson13_step4.urdf
check_urdf /tmp/lesson13_step4.urdf
```

展开命令无错误；`check_urdf` 未安装。尝试安装 `liburdfdom-tools` 时 cn.archive.ubuntu.com 域名解析失败。因此 checker 安装没有完成。未为此重装 ROS、改软件源或把失败说成通过；后续跳过可选工具继续真实加载。

## 4. Gazebo 启动失败的根因定位

第一次 launch 中 gzserver exit255，spawn 等 `/gazebo/spawn_urdf_model`。同时有 fuel DNS 与 svga 警告，不能仅凭它们定位。

通过 `gui:=false verbose:=true` 隔离，明确错误：

```text
Unable to start server[bind: Address already in use].
There is probably another Gazebo process running.
```

当前进程＋端口交叉查证：

```text
pgrep -a gzserver
81082 gzserver

ss -ltnp 'sport = :11345'
LISTEN ... users:(("gzserver",pid=81082,fd=7))
```

停止当时的旧 gzserver，释放端口后重新启动成功。**81082 只对那次记录有效。** 新问题要重新查当前 PID。

## 5. 第四步通过：显示＋动态实体

用户截图显示双层圆柱小车。服务返回 `lesson13_robot`、`success: True`、`is_static: False`；6 个非固定关节存在，包括两个驱动轮。Gazebo 将固定关节 lump 到 root_link，所以单独 body_names 少于 URDF links 不代表零件消失，geom_names 中仍有 base/support/platform collision。

完整用户原输出见对话导出及 `evidence`。

## 6. 第六步：直接差速插件

确认 `/opt/ros/noetic/lib/libgazebo_ros_diff_drive.so` 已安装后，新增：

- `urdf/gazebo/myrobot_drive_step6.xacro`
- `launch/myrobot_drive_step6.launch`
- `scripts/test_forward_step6.py`

drive Xacro 相对包含 stage4 模型，追加一个插件；不叠加 Arbotix 或 ros_control。参数对照 Noetic 官方源码，未照抄不被当前版本读取的 `legacyMode` 等字段。

轮关节 `base_l_wheel_joint` / `base_r_wheel_joint`、轮距 0.8、轮径 0.2、更新率100Hz、轮加速度0.3、扭矩5；速度 `/cmd_vel`、里程计 `/odom`、world 真值里程计、`odom → root_link`。没有顺带完成所有传感器和完整 TF。

用户启动 drive launch 后：

```text
rostopic info /cmd_vel
Type: geometry_msgs/Twist
Publishers: None
Subscribers:
 * /gazebo (http://ubuntu:40241/)
```

说明订阅接口已存在，测试前无发布者正常。

## 7. 最终运动验收

用户执行：

```bash
python3 /home/thl/catkin_ws/src/rcdp/scripts/test_forward_step6.py
```

现场日志：

```text
[INFO] [1791994044.814923, 182.107000]: Gazebo test: request forward 0.1 m/s for 3 wall-clock seconds.
[INFO] [1791994048.332462, 185.597000]: Zero velocity sent; verify that the robot has stopped.
```

用户原反馈：**向前移动且停止**。

结论：模型显示、驱动订阅、低速前进和结束停车已被用户现场确认。没有测得精确距离、实际速度或刹车时间，不能拿理论 v×t 充当实测。

## 8. 下一步与移交

用户要求把课件、所学内容、本轮操作和历史上下文上传自己的 GitHub，标题“thl roscar”，方便次日换 GPT 账号继承。整理为私有 `thl-roscar`，不导出密码／令牌／内部推理／系统指令。接手助手从当前成功状态继续，而不是重复整个安装流程。
