# Step11E：四轮滑移转向的单次原地左转测试

客户端日期：2026-10-17。仅适用于 thl 当前 ROS Noetic / Gazebo 仿真，不用于真实硬件。

## 上一步的实际证据

用户提供的 Step11D 完整日志显示：

- 前进指令 0.08 m/s、3 秒墙钟时间，实际发布循环 3.0001 秒；60 条前进指令、40 条零速度。
- 4 次运动窗口快照中，四轮速度中位数均约 +0.80003 rad/s，接近目标 +0.8 rad/s。
- 净前进位移 0.2392256 m，侧偏 3.45e-7 m，偏航变化 -1.39e-7 rad。
- 发零后，四轮约 2.66e-5 rad/s，车体平面速度约 2.68e-6 m/s；本次停车采样判据通过，errors 为空。

以上支持这次低速直行及停车的数值检查通过；目视结果须由用户确认，不能据此声称转向、重置、长期稳定性或四轮时间戳复验已通过。

## 本阶段只测试一次左转

保持 Step11C Gazebo 运行，无需重编译或重启；不修改模型、轮距、摩擦、扭矩、插件或旧脚本，也不上传 GitHub。
四轮左右差速属于滑移转向，不增加转向舵机。

指令为 linear.x=0、angular.z=+0.20 rad/s，持续约 3 秒墙钟时间，随后连续发送 2 秒全零速度。
在车体 Z 向上约定下，正向偏航目标是从上方看逆时针左转。

按当前插件公式和 0.72 m 轮距、0.10 m 半径，理想轮速目标为：

| 轮子 | 关节 | 理想目标 rad/s |
|---|---|---:|
| 左前 | front_left_wheel_joint | -0.72 |
| 左后 | rear_left_wheel_joint | -0.72 |
| 右前 | front_right_wheel_joint | +0.72 |
| 右后 | rear_right_wheel_joint | +0.72 |

这是关节速度目标，不是保证的车体转速；轮胎与地面侧向滑动会影响实际偏航。不要要求实际角度恰好 0.6 rad/34.4°，墙钟与仿真时间也不一定一致。
轮子反向正确但车体不转、转得少或明显平移，都属于待核对的接触/驱动表现，先发回数据，不要提高速度、扭矩或自行修改摩擦。

## 导入与执行

先确认 Step11D 的目视结果也是正常前进并停止；如不一致，先反馈，不执行左转。
确认车周围至少约半米净空、Gazebo 未暂停，无其他键盘遥控或 /cmd_vel 发布程序。

将 ZIP 复制为 `/home/thl/Lesson14_4wd_turn_step11e.zip`，新终端逐条运行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_turn_step11e.zip -d /home/thl/catkin_ws/src/rcdp
rostopic info /cmd_vel
```

测试前 Publishers 应为 None，Subscribers 应包含 /gazebo；否则停止并反馈。确认符合后只运行一次：

```bash
python3 -u /home/thl/catkin_ws/src/rcdp/scripts/test_4wd_turn_step11e.py
```

测试代码从已经实际运行的 Step11D 脚本派生，保留启动检查、独立查询线程、墙钟计时、显式零速度以及一般异常/Ctrl+C 发零路径；修改了命令、轮速方向判据和偏航/净平移统计。
本包是独立脚本，不依赖你覆盖或手工编辑 Step11D。

## 发回哪些结果

发回完整输出，以及目视是否左转、是否有明显横移/抖动、最后是否停止。

- wheel_directions_match_left_turn：左轮负、右轮正，四轮中位数绝对值大于 0.1 rad/s。
- body_yaw_rate_median_radps：运动快照中的实际车体偏航速度中位数，期望正值，不要求等于指令。
- yaw_change_rad / yaw_change_deg：从初始朝向到停车后的净偏航；本次短脉冲以正向变化为核对重点。
- positive_yaw_change_observed：净正向偏航大于 0.02 rad，是本次诊断阈值，不是课程或硬件标准。
- planar_displacement_m：起止净平移，诊断时以小于 0.05 m 为初步参考；不是全程轨迹/轮胎滑移测量。
- after_zero_stationary_sample：沿用 Step11D 的停车采样判据。
- TEST_RECORDED：表示输出已记录，不代表整体转向功能验收通过。errors、错误方向、不转、停车失败均需反馈。

关节是顺序查询，并非严格同时采样；不从轮速推断电机力矩或各轮载荷。只测一次左转，不自动测右转、回到初始朝向、恢复传感器、清理节点或重置仿真。

## 异常处理

异常时按一次 Ctrl+C，让脚本发零；不要连按、关闭终端或强制杀 Python。
如车仍不停，立即点击 Gazebo 暂停按钮，保持暂停并反馈，不要直接恢复仿真。
发零是尽力操作，无法保证断网、系统崩溃、强制杀进程或其他速度源竞争时停车；新驱动本身仍没有命令超时自动停车功能。
