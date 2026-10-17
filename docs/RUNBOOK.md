# 运行手册 当前四轮四驱版

适用用户已有Ubuntu20.04.6 / Noetic / Gazebo11环境，命令在Ubuntu执行，不在Windows执行。当前step11I四轮＋TF＋激光，旧两轮相机／点云流程仅见[历史手册](history/RUNBOOK_STEP10_2026-10-16.md)。

## 1 保留正常运行现场

若Gazebo和RViz正常，不重复启动Launch。只读检查可另开终端：

```bash
source /home/thl/catkin_ws/devel/setup.bash
rospack find rcdp
rostopic info /cmd_vel
rostopic info /joint_states
rostopic info /scan
```

当前正常模型名lesson13_robot，四轮关节名front_left_wheel_joint、front_right_wheel_joint、rear_left_wheel_joint、rear_right_wheel_joint。不要将这些名称直接输入shell当命令。

## 2 确实要重新启动时

先在旧Launch终端Ctrl+C正常退出，并核查当前进程、11345端口。看不懂占用者就停，不killall、不照抄历史PID。

```bash
pgrep -a -x gzserver
pgrep -a -x gzclient
ss -ltnp 'sport = :11345'
```

确认旧仿真停止后，终端A：

```bash
source /home/thl/catkin_ws/devel/setup.bash
roslaunch rcdp myrobot_4wd_laser_step11i.launch friction_model:=cone_model
```

已有VM阶段不需要重复覆盖文件。若库缺失，则先检查依赖，在工作空间catkin_make -j2后source；GitHub不上传编译.so。原Launch保留/home/thl固定路径。若新用户名／新目录复现，请用[独立提交副本说明](../submissions/2026-10-17-public/02_ROS工程代码/README.md)，不要直接把旧绝对路径当成可移植入口。

## 3 单独打开RViz

终端B，保持运行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
LIBGL_ALWAYS_SOFTWARE=true rosrun rviz rviz -d /home/thl/catkin_ws/src/rcdp/config/lesson14_scan_step8.rviz __name:=lesson14_4wd_rviz
```

应显示当前四轮模型、红色扫描和LaserScan Status Ok。Gazebo蓝色线束是射线显示。没有已恢复的四轮相机／点云，不启动旧预览中继，不勾选历史大点云。

## 4 非运动验收

```bash
rosservice call /gazebo/get_world_properties
rosservice call /gazebo/get_model_properties "model_name: 'box_house'"
rosservice call /gazebo/get_model_properties "model_name: 'lesson13_robot'"
timeout 12s rostopic echo -n 1 /scan/header
timeout -s INT 8s rostopic hz /scan
timeout -s INT 7s rosrun tf tf_echo odom laser_scan_link
timeout -s INT 55s python3 -u /home/thl/catkin_ws/src/rcdp/scripts/diagnose_4wd_tf_step11h.py
```

World运行9模型，box_house应有4墙与4碰撞；机器人6活动关节。Gazebo固定合并后7body不等于URDF10Link缺失。雷达360样本、约5.495Hz。TF初始化可能短暂缺缓存，后续应持续正常；不能凭初始化异常添加静态TF。审计观察40秒墙钟，不订阅scan，不是长期压力证明。

## 5 有限运动与停车

先确认/cmd_vel没有键盘或导航竞争发布者、仅课程仿真接收、未暂停且周围空旷。每次只跑一项，观察确实停止后再下一项：

```bash
python3 -u /home/thl/catkin_ws/src/rcdp/scripts/test_4wd_forward_step11d.py
python3 -u /home/thl/catkin_ws/src/rcdp/scripts/test_4wd_turn_step11e.py
python3 -u /home/thl/catkin_ws/src/rcdp/scripts/test_4wd_right_step11g.py
```

命令0.08m/s或±0.20rad/s约3秒墙钟，后约2秒零指令。插件无完善命令超时看门狗，停止发布者不保证停车。必要时另开已source终端持续发零，并停止其他非零发布者：

```bash
rostopic pub -r 10 /cmd_vel geometry_msgs/Twist '{linear: {x: 0, y: 0, z: 0}, angular: {x: 0, y: 0, z: 0}}'
```

确认停后Ctrl+C退出零指令，再正常关闭整组仿真。不在实车使用这些脚本。

## 6 已知排错

- 雷达ldd提示libRayPlugin.so找不到：先在子shell加载Gazebo官方setup.sh再检查，不据此重装Gazebo。
- RViz列表有旧名字而ping拒绝连接：可能注册残留；当前四轮节点需另查，未执行的cleanup不写成已完成。
- 怀疑误删墙：先查World哈希和box_house几何，再决定是否需要恢复，不覆盖正常文件。
- 原始点云SIGBUS未根治，当前只用软件渲染扫描配置。APT/DNS未确认修复。

历史完整手册已单独保留，不丢失旧两轮学习记录；其“默认入口”仅适用于历史阶段。
