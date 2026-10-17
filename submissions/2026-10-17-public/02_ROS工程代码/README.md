# 四轮四驱机器人源码与复现说明

## 1 环境和验证范围

原运行环境：Ubuntu 20.04.6 LTS、ROS Noetic、Gazebo Classic 11.15.1、RViz 1.14.26。

源码工作空间在 `catkin_ws/`，包含 `rcdp` 和 `rcdp_4wd_stampfix` 两个包。前者保存模型、世界和启动配置，后者编译C++14四电机滑移转向插件。

这是依据已分发阶段源码整理的副本，不是直接从VM导出的全部磁盘镜像。核心已验证源文件逐字节复制，并在 `verification/source_manifest.json` 记录来源、SHA256和用途。`evidence/user_pasted_logs/` 保存用户回传终端文本，不伪装为从VM完整导出的日志。

## 2 原工作空间的已用启动方式

以下流程有原Ubuntu阶段记录，适用于已准备好的原 `/home/thl/catkin_ws`。不要将副本直接覆盖进去。

```bash
cd /home/thl/catkin_ws
source /opt/ros/noetic/setup.bash
catkin_make -j2
source /home/thl/catkin_ws/devel/setup.bash
roslaunch rcdp myrobot_4wd_laser_step11i.launch friction_model:=cone_model
```

原 `myrobot_4wd_drive_step11c.xacro` 第9行保留实际使用的绝对库路径 `/home/thl/catkin_ws/devel/lib/librcdp_4wd_stampfix.so`。因此不能不改说明就声称原入口适合任意用户名或目录。

## 3 在独立工作空间复现提交副本

先把本目录的 `catkin_ws` 文件夹复制到Ubuntu的一个**尚不存在**的新目录，例如 `/home/thl/ros_submission_20261017`。该目录内部应直接是 `src/rcdp` 和 `src/rcdp_4wd_stampfix`，不要多套一层 `catkin_ws`。复制时选择新目录，勿替换已有工作空间。

依赖包括 catkin、CMake、g++、Gazebo 11开发库、Boost thread、roscpp、tf、geometry_msgs、nav_msgs、gazebo_ros、gazebo_plugins、xacro、robot_state_publisher、rviz、rospy、sensor_msgs、tf2_msgs和rosgraph_msgs。原Ubuntu已有主要依赖；本次未执行安装或系统升级。若新机器缺依赖，先报告缺项再补装。

终端A：仅编译和启动一次Gazebo。

```bash
source /opt/ros/noetic/setup.bash
cd /home/thl/ros_submission_20261017
catkin_make -j2
source /home/thl/ros_submission_20261017/devel/setup.bash
rospack find rcdp
ls -l /home/thl/ros_submission_20261017/devel/lib/librcdp_4wd_stampfix.so
roslaunch rcdp submission_4wd_laser.launch friction_model:=cone_model
```

新增 `submission_4wd_laser.launch` 及 `scripts/submission_description.py` 仅解决提交目录变化：展开未修改的当前Xacro后，只替换四驱插件的一个filename属性，指向本工作空间 `devel/lib`。其余模型、关节、参数、World、出生位置和RSP设置保持一致。此入口已做离线等价检查，但**尚未在Ubuntu原生重新运行**。它面向catkin devel布局，不声称适用于install空间。未改变原已验证Launch。

终端B：打开RViz，避免同时开启多个同名窗口。

```bash
source /opt/ros/noetic/setup.bash
source /home/thl/ros_submission_20261017/devel/setup.bash
LIBGL_ALWAYS_SOFTWARE=true rosrun rviz rviz -d /home/thl/ros_submission_20261017/src/rcdp/config/lesson14_scan_step8.rviz __name:=lesson14_4wd_rviz
```

RViz固定坐标为odom，RobotModel读robot_description，LaserScan读/scan。旧step8配置名不表示加载旧两轮模型。

## 4 非运动检查

终端C应source与终端A完全相同的新工作空间。

```bash
source /home/thl/ros_submission_20261017/devel/setup.bash
rosservice call /gazebo/get_world_properties
rosservice call /gazebo/get_model_properties "model_name: 'box_house'"
rosservice call /gazebo/get_model_properties "model_name: 'lesson13_robot'"
rostopic info /cmd_vel
rostopic info /joint_states
rostopic info /scan
timeout 12s rostopic echo -n 1 /scan/header
timeout -s INT 8s rostopic hz /scan
timeout -s INT 7s rosrun tf tf_echo odom laser_scan_link
timeout -s INT 55s python3 -u /home/thl/ros_submission_20261017/src/rcdp/scripts/diagnose_4wd_tf_step11h.py
```

应有9个场景模型（8个World模型加机器人）、4面墙的碰撞几何、4个轮子及6个活动关节。URDF为10 Link/9 Joint；Gazebo固定关节合并后返回7个body属于正常现象。tf_echo初始化时可能先提示缓存未建立；持续错误才进一步排查。

诊断脚本观察40秒墙钟时间；它不是控制脚本，不订阅/scan，也不能证明长期或压力稳定性。按Ctrl+C退出连续检查不会关闭Gazebo。

## 5 有限运动测试

只在仿真中、车旁有足够空间、没有其他/cmd_vel发布者时单独运行。不要同时开键盘控制。依次执行并观察每次停止，再进行下一次。

```bash
python3 -u /home/thl/ros_submission_20261017/src/rcdp/scripts/test_4wd_forward_step11d.py
python3 -u /home/thl/ros_submission_20261017/src/rcdp/scripts/test_4wd_turn_step11e.py
python3 -u /home/thl/ros_submission_20261017/src/rcdp/scripts/test_4wd_right_step11g.py
```

脚本分别发送0.08m/s或±0.20rad/s约3秒墙钟指令，之后约2秒零速度并检查样本。它们不是实车安全控制器，插件本身还没有命令超时看门狗。需要紧急停止时，在另一个已source的终端持续发送零指令，并停止其他发布者：

```bash
rostopic pub -r 10 /cmd_vel geometry_msgs/Twist '{linear: {x: 0, y: 0, z: 0}, angular: {x: 0, y: 0, z: 0}}'
```

确认车停后Ctrl+C退出零指令。关闭仿真请在启动终端Ctrl+C，随后用 `pgrep -a -x gzserver` 和 `ss -ltnp 'sport = :11345'` 检查残留；不要直接重复启动，也不要无差别kill全部进程。

## 6 典型问题

- `libRayPlugin.so => not found`：先在子shell加载 `$(pkg-config --variable=prefix gazebo)/share/gazebo/setup.sh`，再ldd检查激光库；原问题是搜索环境，不是缺文件。不要仅凭这一行重装Gazebo。
- RViz退出：当前用软件渲染和扫描配置，不加载历史高密度点云。
- 节点列表有名字但ping拒绝连接：可能是注册残留；先确认对应进程和当前订阅，不把旧名称当作活节点。
- 不见墙体：先看box_house四个Wall和Collision，再比对World哈希。界面删除而未保存不等于源文件损坏。
- A组左转脚本退出2：记录显示运动和停止成功，但超过自设5cm净位移参考，不是插件崩溃或课程评分标准。

## 7 检验与来源

`verification/host_checks.json`：本次主机检查范围；`plugin_source_tests.txt`：12项源码/指令数学测试；`current_4wd_expanded.urdf`：主机展开结果，只用于检验，不替代Xacro源码。历史checker的哈希、/home/thl路径和.so比较针对原工作空间，移植后可能需要人工审阅，不能将其机械当成新副本的原生验收通过。

`docs/PACKAGING_CHANGES.md` 说明整理副本的有限变更。课程场景版权未明确，rcdp许可证保留原TODO状态；只作课程材料整理，不授予额外开源许可。插件上游BSD来源位于 `rcdp_4wd_stampfix/UPSTREAM.json` 和LICENSE。
