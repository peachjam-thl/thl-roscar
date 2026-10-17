# 提交副本整理记录

1. 核心阶段Xacro、原Launch、World、配置、检查及运动脚本均从原分发目录逐字节复制，未回写源文件。这里只打包当前四轮工程及所需旧依赖，不混入其他课程包或旧两轮控制Launch。
2. 原rcdp的CMakeLists/package.xml完整保留在original_metadata目录。副本使用仅安装资源的CMake，并补充真实运行依赖；维护者为提交者，邮箱使用不可投递example.invalid占位以免伪造个人邮箱。课程许可证原TODO保持不变，不虚构版权授权。
3. 新增submission_4wd_laser.launch与submission_description.py，适配独立catkin devel目录。只替换展开URDF中的一个驱动库filename，保留原阶段入口；已做主机结构等价检查，未声称已原生运行。
4. 完整保留自建插件源、原上游文件、BSD许可证、来源版本及12项测试；不复制Ubuntu构建出的平台相关.so，不复制build/devel，需在目标Ubuntu重新编译。
5. 日志为用户粘贴文本，另存解析JSON与对话摘录；不是VM完整日志导出。截图保持字节不变，仅编号重命名。
6. 未恢复四轮版相机、点云或导航，未修改原GitHub仓库，未录制视频。
