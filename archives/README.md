# 按阶段使用的增量代码包

这些 ZIP 是本项目逐阶段交付的文件，保留原字节及 CRC。不含独立 ROS 安装环境，不要当成六套需要同时运行的程序。

| 包 | 内容 | 前置 |
| --- | --- | --- |
| [step4](Lesson13_Gazebo_step4.zip) | 物理模型、平地、launch | 原 rcdp／同版本 ROS 环境 |
| [step6](Lesson13_Gazebo_step6_drive.zip) | 单个直接差速插件、launch、短时测试 | step4 |
| [step7](Lesson14_laser_step7.zip) | 激光、室内场景、launch | step6 |
| [step8](Lesson14_tf_rviz_step8.zip) | 辅助真实关节状态、RSP、TF/RViz | step7 |
| [step9](Lesson14_camera_step9.zip) | RGB-D、光学 frame、launch、显示配置 | step8 |
| [step9a](Lesson14_cloud_preview_step9a.zip) | 独立轻量预览中继及 RViz 配置 | step9 数据流 |

现有 VM 已导入时无需再次全部解压。恢复前先备份和比较文件；`unzip -n` 会跳过同名文件，不证明旧内容就是新内容。当前合并后的可阅读源码在 `catkin_ws/src/rcdp`。

不要同时启动各阶段 launch：只选当前需要的最新入口。用户现场使用的是 step9 Gazebo＋step9a 中继与软件 RViz，运行方法和安全检查见 [RUNBOOK](../docs/RUNBOOK.md)。

课程原包另放 `reference`，不是这些增量的替代命名。校验值见 metadata 的资源索引与总 manifest。
