# 补充对话记录摘录

来源：本任务中用户粘贴的 Ubuntu 终端输出和运行反馈。以下为整理摘录，不是从虚拟机导出的完整日志。

## 雷达数据检查
frame: laser_scan_link；samples: 360；angle_limits_rad: -3.0, 3.0；angle_increment_rad: 0.016713092103600502。
range_limits_m: 0.10000000149011612, 30.0；valid_samples: 360；positive_inf_samples: 0；nan_samples: 0。
nearest_valid_m: 1.6867303848266602；farthest_valid_m: 8.969403266906738；8秒频率检查约5.495Hz（仿真时间）。

## 场景重新加载检查
关闭后检查 gzserver/gzclient/rviz 无进程、11345 无监听；三个 World 的 sha256sum -c 均成功。
get_world_properties 返回 ground_plane、box_house、unit_box、unit_cylinder、unit_box_0、unit_box_1、unit_cylinder_0、unit_cylinder_1、lesson13_robot。
box_house：Wall_1..Wall_4，Wall_1_Collision..Wall_4_Collision，is_static=True，success=True。
lesson13_robot：root_link、depth_camera_link、四个 wheel_link、laser_scan_link，共7个 Gazebo body；6个活动关节；is_static=False；success=True。
用户确认：车和墙壁都像之前一样，Gazebo 正常；RViz 一切正常。

## 雷达库预检环境
初次 ldd 提示 libRayPlugin.so => not found；加载 pkg-config 提供的 Gazebo 官方 setup.sh 后，解析到 /usr/lib/x86_64-linux-gnu/gazebo-11/plugins/libRayPlugin.so；precheck_exit=0。
这是检查进程的动态库搜索环境问题，未进行 Gazebo 重装。

## 原两轮版时间戳诊断背景
40秒窗口：root TF 3932条、重复3次；odom 3931条、重复2次；两者同源均为 /gazebo；clock 38754条、无重复，未观察到回退。
该记录用于说明先前问题和采用 SimTime 的理由，不冒充本次四轮结果。

## RViz 注册残留
旧 /lesson14_rviz XMLRPC 连接拒绝；新 /lesson14_4wd_rviz 已订阅 /scan 且用户确认显示正常。未记录执行 rosnode cleanup。
