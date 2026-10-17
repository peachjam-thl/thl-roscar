# 按阶段使用的增量代码包

## 今日四轮归档 2026-10-17

`2026-10-17_4wd/` 保存step11A模型、B插件、C驱动、D前进、E左转、F摩擦、G右转、H关节TF、H全树审计、I雷达等10份原交付ZIP，以及公开脱敏提交包。插件ZIP解压目标src，其他增量一般为src/rcdp；先读包内说明，不无差别覆盖现有成功工程。

公开提交包报告已移除姓名、班级、学号，原私人版不上传。所有二进制都只是资料压缩包／文档图片，不含VM编译.so。

这些 ZIP 是本项目逐阶段交付的文件，保留原字节及 CRC。不含独立 ROS 安装环境，不要把各阶段当成需要同时启动的程序。

| 包 | 内容 | 前置 |
| --- | --- | --- |
| [step4](Lesson13_Gazebo_step4.zip) | 物理模型、平地、launch | 原 rcdp／同版本 ROS 环境 |
| [step6](Lesson13_Gazebo_step6_drive.zip) | 单个直接差速插件、launch、短时测试 | step4 |
| [step7](Lesson14_laser_step7.zip) | 激光、室内场景、launch | step6 |
| [step8](Lesson14_tf_rviz_step8.zip) | 辅助真实关节状态、RSP、TF/RViz | step7 |
| [step9](Lesson14_camera_step9.zip) | RGB-D、光学 frame、launch、显示配置 | step8 |
| [step9a](Lesson14_cloud_preview_step9a.zip) | 独立轻量预览中继及 RViz 配置 | step9 数据流 |
| [step10 插件](Lesson14_stampfix_step10.zip) | 独立 rcdp_stampfix 源码、原始上游／许可、7项源差异测试 | Noetic、Gazebo11开发环境；解压到 catkin_ws/src 后编译 |
| [step10 切换](Lesson14_stampfix_switch_step10.zip) | 两份Xacro、launch、模型／依赖预检、当时操作说明 | step9/9a 与编译好的新库；解压到 src/rcdp |

现有 VM 已导入时无需再次全部解压。恢复前先备份和比较文件；`unzip -n` 会跳过同名文件，不证明旧内容就是新内容。当前合并后的可阅读源码在 `catkin_ws/src/rcdp`。

不要同时启动各阶段 launch：只选当前入口。最新用户现场为 step10 Gazebo＋step9a 中继与软件 RViz，见 [RUNBOOK](../docs/RUNBOOK.md)。两份 step10 ZIP 保留交付时字节，所以包内“待编译／待切换”是当时阶段说明；最新验收见 [step10 记录](../docs/TIMESTAMP_FIX_STEP10.md)。源码目录 README 已同步新状态，归档 ZIP 未重打包。

课程原包另放 `reference`，不是这些增量的替代命名。校验值见 metadata 的资源索引与总 manifest。
