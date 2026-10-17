# Step11G：在 B/cone 候选配置下验证一次右转

客户端日期：2026-10-17。只增加独立测试脚本和本文档，不修改模型、世界、驱动、摩擦参数或旧脚本，不上传 GitHub。

## 单次 A/B 结果

数据来自用户提供的实际 Gazebo 日志；每组都从重新启动的世界开始，依次运行相同的 Step11D 直行和 Step11E 左转。两组左转均为 +0.20 rad/s、约 3 秒墙钟时间，然后连续发 2 秒零速度。

| 左转观测 | A/pyramid | B/cone |
|---|---:|---:|
| 净转角 | +27.6363° | +25.9996° |
| 起止净平移 | 0.0737147 m | 0.0122729 m |
| 净平移/净转角 | 0.152826 m/rad | 0.0270461 m/rad |
| 实际车体偏航速度中位数 | +0.157647 rad/s | +0.151298 rad/s |
| 发零后停车采样 | 通过 | 通过 |
| 测试退出码 / 日志退出码 | 2 / 0 | 0 / 0 |

本次 B 的净平移减少约 83.35%，转角减少约 5.92%；按每弧度转角归一后，净偏移减少约 82.30%。因此这次观测的改善并不只是转角变小。

限制：每组仅一次，观察到的是起止净平移，不是全程轨迹长度或严格滑移率；尚不能证明唯一根因、统计显著性、长期稳定性或所有姿态/负载下均改善。
实际偏航速度仍低于指令 0.20 rad/s，不能把此次通过描述为精确角速度跟踪通过。本阶段不同时标定轮距/速度增益或增加扭矩。
先保留 B 作为候选，原 A、Step11C 及两轮文件均保留，不覆盖。后续仍需重复验证、右转、四轮 TF/odom 时间戳复验，再恢复传感器。

已保存的虚拟机日志：

```text
/home/thl/ros_course_logs/step11f_A_tests_hyYQmn/A_forward.log
/home/thl/ros_course_logs/step11f_A_tests_hyYQmn/A_left_turn.log
/home/thl/ros_course_logs/step11f_B_tests_mMb7nY/B_forward.log
/home/thl/ros_course_logs/step11f_B_tests_mMb7nY/B_left_turn.log
```

## 右转测试边界

在当前仍运行的 B/cone 世界进行一次基本右转功能测试，无需重新编译、重启或手工复位。它不是另一个严格匹配起点的 A/B 对照，也不是闭环回到初始位置/朝向的控制器。
保持周围约半米净空、仿真未暂停，没有其他 /cmd_vel 发布者。若刚才 B 左转的目视表现与日志不符，或没有停稳，先反馈，不运行右转。

固定指令：linear.x=0，angular.z=-0.20 rad/s，约 3 秒墙钟时间，再连续发 2 秒全零速度。理想四轮目标：左前/左后 +0.72 rad/s，右前/右后 -0.72 rad/s。
从上方看应顺时针右转；实际转角受接触滑移和仿真时间进度影响，不要求恰好 -0.6 rad，也不保证抵消上一轮左转角。

## 导入

将 ZIP 放到 `/home/thl/Lesson14_4wd_right_step11g.zip`，在新终端运行：

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_right_step11g.zip -d /home/thl/catkin_ws/src/rcdp
```

## 执行一次并保存到 B 组目录

```bash
b_trial_dir=/home/thl/ros_course_logs/step11f_B_tests_mMb7nY
if [ ! -d "$b_trial_dir" ]; then
    printf '日志目录不存在，未执行测试。\n'
elif [ -e "$b_trial_dir/B_right_turn.log" ]; then
    printf '右转日志已存在，未重复执行。请反馈现有结果。\n'
else
    python3 -u /home/thl/catkin_ws/src/rcdp/scripts/test_4wd_right_step11g.py 2>&1 | tee -i "$b_trial_dir/B_right_turn.log"
    b_right_status=("${PIPESTATUS[@]}")
    printf 'python_exit=%s tee_exit=%s\n' "${b_right_status[0]}" "${b_right_status[1]}"
fi
```

脚本来自已运行的 Step11E 框架，改为负角速度、右转轮速方向和负偏航判据，其余启动检查、只读服务超时、独立采样线程、墙钟计时、一般异常/Ctrl+C 发零逻辑均保留。
它会真实发送运动指令，不是只读诊断；尽力发零不等于断网/强制杀进程/系统崩溃时保证停车。驱动仍无命令超时自动停车。

## 看哪些结果

- wheel_directions_match_right_turn 应为 true。
- negative_yaw_change_observed 应为 true，净偏航需小于 -0.02 rad（本项目诊断阈值，不是课程标准）。
- planar_displacement_m 仍以 <0.05 m 作为初步参考；不能从单次净位移推断完整路径和滑移。
- after_zero_stationary_sample 应为 true，需同时目视确认停止。
- errors 应为空；python_exit=0 表示脚本本次数值判据通过，不等于整个四轮项目验收完毕。
- python_exit=2 表示数值判据未全部满足，先保留结果，不提速、不重复执行。

把完整输出和目视结果发回。异常时按一次 Ctrl+C 让脚本发零；仍不停则立即暂停 Gazebo，保持暂停并反馈。
