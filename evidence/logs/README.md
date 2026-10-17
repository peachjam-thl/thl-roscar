# 运行日志与用户终端记录

这些是用户在本次 ROS 实践中提供的文本，不是助手直接从虚拟机采集的完整系统日志。保留成功和失败输出；日志中的历史 PID、端口、绝对路径和时间不应直接当作当前环境。

用户本次明确要求随项目上传。日志包含其课程 VM 用户名／本机路径；已检查已知凭据格式，未改写数值或删除黄色警告。内部会话、助手推理、系统／开发者消息、工具输出未导出。

## 原始文本附件

| 文件 | 来源与用途 |
| --- | --- |
| [step7_launch_user_supplied.txt](step7_launch_user_supplied.txt) | 用户原始附件，雷达仿真启动；字节保持不变 |
| [step8_launch_user_supplied.txt](step8_launch_user_supplied.txt) | 用户原始附件，TF/RViz 启动及警告；字节保持不变 |

## 终端消息

每条只抽取用户可见消息文字，规范换行；截图另存。时间为消息提交 UTC，不冒充日志内部仿真时间。

| 编号 | 消息时间 UTC | 第一行预览 |
| --- | --- | --- |
| [001](user_terminal_001.txt) | 2026-10-15T12:38:19.499Z | thl@ubuntu:~/桌面$ ls -lh /home/thl/Lesson14_code.zip /home/thl/Lesson15_code.zip |
| [002](user_terminal_002.txt) | 2026-10-15T12:41:10.954Z | thl@ubuntu:~/桌面$ ls -l /home/thl/ros_course_reference/Lesson14_code/catkin_ws/src/rcdp/package.xml |
| [003](user_terminal_003.txt) | 2026-10-15T12:44:08.911Z | ls -lh /home/thl/ros_course_backups/rcdp_before_lesson14_15_*.tar.gz |
| [004](user_terminal_004.txt) | 2026-10-15T12:46:00.868Z | thl@ubuntu:~/桌面$ rospack find teleop_twist_keyboard |
| [005](user_terminal_005.txt) | 2026-10-15T12:46:44.910Z | thl@ubuntu:~/桌面$ rospack find robot_state_publisher |
| [006](user_terminal_006.txt) | 2026-10-15T12:52:48.870Z | thl@ubuntu:~/桌面$ unzip -n /home/thl/Lesson14_laser_step7.zip -d /home/thl/catkin_ws/src/rcdp |
| [007](user_terminal_007.txt) | 2026-10-15T13:01:28.506Z | thl@ubuntu:~/桌面$ source /home/thl/catkin_ws/devel/setup.bash |
| [008](user_terminal_008.txt) | 2026-10-15T13:04:07.034Z | frame: laser_scan_link |
| [009](user_terminal_009.txt) | 2026-10-15T13:14:11.785Z | thl@ubuntu:~/桌面$ source /home/thl/catkin_ws/devel/setup.bash |
| [010](user_terminal_010.txt) | 2026-10-15T13:20:30.852Z | thl@ubuntu:~/桌面$ rosrun tf tf_echo odom laser_scan_link |
| [011](user_terminal_011.txt) | 2026-10-15T13:25:54.437Z | 这是黄色报错。以下是后续完整输出thl@ubuntu:~/桌面$ source /home/thl/catkin_ws/devel/setup.bash |
| [012](user_terminal_012.txt) | 2026-10-15T13:33:01.744Z | thl@ubuntu:~/桌面$ rosnode info /sim |
| [013](user_terminal_013.txt) | 2026-10-15T13:36:54.411Z | received: 2997 |
| [014](user_terminal_014.txt) | 2026-10-16T04:36:25.414Z | thl@ubuntu:~/桌面$ unzip -n /home/thl/Lesson14_camera_step9.zip -d /home/thl/catkin_ws/src/rcdp |
| [015](user_terminal_015.txt) | 2026-10-16T04:43:20.326Z | thl@ubuntu:~/桌面$ source /home/thl/catkin_ws/devel/setup.bash |
| [016](user_terminal_016.txt) | 2026-10-16T04:54:34.667Z | thl@ubuntu:~/桌面$ source /home/thl/catkin_ws/devel/setup.bash |
| [017](user_terminal_017.txt) | 2026-10-16T05:00:58.869Z | [WARN] [1792126743.722288295, 844.271000000]: TF_REPEATED_DATA ignoring data with redundant timestam |
| [018](user_terminal_018.txt) | 2026-10-16T05:06:04.454Z | hl@ubuntu:~/桌面$ source /home/thl/catkin_ws/devel/setup.bash |
| [019](user_terminal_019.txt) | 2026-10-16T05:10:33.918Z | thl@ubuntu:~/桌面$ LIBGL_ALWAYS_SOFTWARE=true rosrun rviz rviz -d /home/thl/catkin_ws/src/rcdp/config/ |
| [020](user_terminal_020.txt) | 2026-10-16T05:16:12.122Z | hl@ubuntu:~/桌面$ timeout 25s python3 -u - <<'PY' |
| [021](user_terminal_021.txt) | 2026-10-16T05:27:33.052Z | thl@ubuntu:~/桌面$ timeout 15s python3 -u - <<'PY' |
| [022](user_terminal_022.txt) | 2026-10-16T05:40:07.260Z | thl@ubuntu:~/桌面$ source /home/thl/catkin_ws/devel/setup.bash |

不包含从未提供的崩溃 core、完整 ~/.ros 日志目录或新截图；未取得的内容不伪造。最终“正常 同步 稳定”属于用户功能反馈，见上层验收摘要和实验报告。

## step10 后续修复记录

- [编译原附件](step10_build_user_supplied.txt)：用户提供，原字节保留；成功构建和未来文件时间警告都在。
- [ldd 后半段原附件](step10_ldd_tail_user_supplied.txt)：原字节保留，不冒充完整 ldd；完整依赖通过见后续预检摘要。
- [部署消息转录](step10_deployment_user_reported.txt)：用户预检、启动订阅、实际进程映射和“稳定 没出现”反馈；未补造时间。
- [完整诊断 JSON 索引](../timestamp_fix_step10/README.md)：旧插件一次及新插件两次，各约40秒；保留完整统计与计数范围。

本次没有新增用户截图、core 或完整 VM 日志目录，不上传源码构建的 `.so`；其现场 SHA256 只作来源证据。
