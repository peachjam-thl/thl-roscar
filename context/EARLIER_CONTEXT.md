# 先前课程对话的知识与问题地图

这是便于接手的概要，不替代历史原话和原始 PDF。曾经的回答和考试判断可能有误；尤其教师隐藏评分键未知，不能承诺满分。当前 Gazebo 进度优先看 CURRENT_STATE。

## 1. Linux / Shell 基础

用户发过文件身份／权限、归档压缩、Shell变量与数据流、Ubuntu软件安装的习题截图。

- 文件三类访问身份：所有者 u、所属组 g、其他用户 o；权限 r/w/x，对应4/2/1。
- `chmod` 改权限，`chown` 改所有者（也可同时改组），`chgrp` 改组。
- `ls -l` 首字符是文件类型：d目录、-普通文件、l符号链接等；后九字符才是三组权限。
- `chmod 644 file` 通常写作 `chmod u=rw,go=r file`；`chmod a=rx path` 是所有三类设为r-x，不是简单追加x。
- 归档 tar 与压缩 gzip/bzip2/zip 区分；`.tar.gz`、`.tar.bz2` 的展开命令常见 `tar -xzvf`、`tar -xjvf`。
- stdin/stdout/stderr 对应文件描述符0/1/2；管道`|`把一端标准输出送入另一端标准输入。
- `$变量名`或`${变量名}`引用变量；PATH是可执行文件搜索路径，不是所有文件搜索路径。
- Shell脚本shebang指定解释器；`bash script.sh`、`./script.sh`、`source script.sh`作用域和权限要求不同。
- APT update更新索引，不等于升级软件；upgrade升级已装包。源码安装要按项目构建系统，不能把所有项目都说成`./configure; make; make install`。

用户曾输入 `mkdir-p~/catkin_ws/src` 报找不到文件：`mkdir`、`-p`、路径之间需要空格，正确如 `mkdir -p ~/catkin_ws/src`。之后命令应防止同类错误。

## 2. ROS 基础与课程复习

学过ROS目标／客户端库／工具／生态、Noetic与Ubuntu20.04、工作空间src/build/devel、包管理命令等。第一至十课共有1330页原始PDF，另有40页笔试复习PDF；复习文档不是覆盖课程每一幅截图和隐藏考点的标准答案。

ROS1 Master做发现与注册，不作为所有消息的数据中转；参数服务器存共享参数。topic发布订阅通常异步多对多，service是请求与响应，bag记录和回放话题。不要把ROS2无Master架构混入当前Noetic课程。

用户曾询问“Client Library支持哪些语言”并反馈考试错一道选择题。准确选项要读当题选项和课件范围，区分官方主要维护的roscpp/rospy与其他语言客户端库；不能在没有选项时保证某个多选组合满分。平台曾隐藏试卷／标准答案，旧记录里高置信判断不代表教师已经确认。

## 3. Catkin包、package.xml与自定义消息

用户最初用 `beginner_tutorials`，后来在 `/home/thl/catkin_ws/src/robot_course_pkg` 做消息／服务；当前 build 输出仍有 RobotTelemetry、SetRobotMode 目标。完整VM源码未导出，不擅自复原成“原文件”。

- 包最基本文件是`package.xml`和`CMakeLists.txt`；包里的文件与`src/CMakeLists.txt`工作空间顶层文件不是同一个。
- package.xml声明名字、版本、描述、维护者、许可证与依赖。format2常用buildtool_depend、build_depend、build_export_depend、exec_depend、test_depend、doc_depend；`depend`是部分依赖标签的合并写法，不能把所有标签当同义。
- `.msg`列出字段，`.srv`用`---`分请求和响应。字段类型与名字、常量与变量值要区分。
- 自定义消息：先在包的`msg/`创建真实文件，package.xml加入message_generation构建依赖和message_runtime运行依赖，再修改**包内**CMakeLists。
- CMake顺序通常为 find_package（含message_generation）→ add_message_files/add_service_files → generate_messages → catkin_package（含message_runtime）；必须在catkin_package之前调用generate_messages。
- 最后工作空间根目录catkin_make，再source devel/setup.bash，使用rosmsg show／rossrv show核对生成结果。

曾出现三个明确错误：

1. `junk after document element: line14`：XML根元素结束后又出现内容，检查是否把依赖写到了`</package>`外或重复根元素。
2. `msg/test.msg does not exist`：CMake声明的文件名与实际磁盘不一致（包括大小写、目录），先创建／核实文件，不靠反复编译解决。
3. `generate_messages() must be called before catkin_package()`：调整CMake调用顺序，而不是改工作空间顶层模板。

早期rospack抱怨python-catkin-pkg/python-empy/python-rospkg等，旧日志不足以证明当前根因；不能在Noetic中不核对版本就强装Python2老包或认为包的三项roscpp/rospy/std_msgs声明本身错了。

## 4. turtlesim、话题与服务

用户练过启动小乌龟、键盘操作、发布速度、清轨迹和mimic。典型命令：

```bash
roscore
# 另一个终端
rosrun turtlesim turtlesim_node
# 再开终端
rosrun turtlesim turtle_teleop_key
```

`rostopic echo /turtle1/cmd_vel`看实际消息，`rostopic type /turtle1/cmd_vel`看类型，`rosmsg info geometry_msgs/Twist`看结构。Twist含linear和angular两个Vector3；平面小龟主要用linear.x与angular.z。

`rosservice call /clear`清轨迹，`/reset`还会重置仿真；两者不能混淆。持续rostopic pub用Ctrl+C退出。当前Gazebo差速插件的停车行为不同，不能套用“小龟会停”的经验。

mimic重映射把input/pose接到领航龟pose，把output/cmd_vel接到跟随龟cmd_vel；目标命名必须对应实际生成的龟。话题重映射并不自动新建第二只龟。它复制运动速度关系，不承诺两只龟空间位置重合。

## 5. launch XML

用户希望理解文件、执行方式与笔试题。launch根为`<launch>`；node的重要属性包括pkg/type/name/args/output/respawn。`pkg`找包，`type`找可执行文件，`name`是运行节点名，不能混为同一个名字。

- `<param name="robot_description" textfile="..."/>`把文件内容存入参数，不是只把路径字符串存进去。
- `<remap from="..." to="..."/>`重映射名称，`<arg>`与`$(arg ...)`传launch参数，`$(find 包名)`定位包。
- `<include>`复用其他launch，`<rosparam>`常加载YAML参数，节点内param通常落入私有命名空间。
- `args="--test" respawn="true"`只是把--test传给程序，并在节点退出后按roslaunch规则重启；程序自身是否支持--test仍需检查，不能把示意行当保证可执行的完整程序。

执行格式 `roslaunch 包名 文件名.launch`。用户曾输入 `roslaunch turtle tf2 turtle tf2 demo cpp.launch`，因为下划线拆成空格导致参数错；课程对应 `roslaunch turtle_tf2 turtle_tf2_demo_cpp.launch`，需确保该包已安装且环境正确。

## 6. TF2、URDF、Xacro到Gazebo

用户了解过坐标变换图、Master注册、同步服务与异步话题。Lesson11–12进一步TF2工具和编程；Lesson13是URDF/Xacro/RViz/Arbotix；Lesson14进入Gazebo物理与驱动／传感器；Lesson15涉及传感器修正和导航流程。

URDF描述link/joint树；visual是显示，collision是碰撞，inertial是质量与惯性；revolute有角度限位、continuous可连续旋转、fixed固定；origin的xyz/rpy与axis坐标系必须核对。Xacro是生成URDF的宏语言，不能把展开前的宏文件不经处理当普通URDF。

用户此前发双层差速机器人实践截图：底层圆柱、立柱、顶层圆柱，前面摄像头绕Z±180°、顶层雷达绕Z连续旋转、左右驱动轮和前后支撑轮。这是当前rcdp模型来源的课程任务。实际本轮运行情况见OPERATION_LOG，不因旧课件截图存在就推断所有控制／传感器已经实现。

## 7. 下一步课程衔接

按用户选择，不自动全部实施：先键盘速度控制／停止，再补足关节状态与TF、真实传感器插件话题，最后导航。每阶段核对相关PDF原页及Noetic实际插件，不把导航截图中的残缺YAML当完整可用配置。
