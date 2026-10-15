# ROS 实践：Lesson11–15 学习记录与操作索引

整理日期：2026-10-14。用途：后续按本课程提供具体 ROS 指令、完整代码文件及排错步骤。

## 1. 本次范围与完成边界

| 原文件 | PDF 页数 | 主要内容 |
| --- | ---: | --- |
| D:/Personal/Desktop/实践PPT/Lesson11.pdf | 71 | rqt、rosbag、ROS API、TF2 基础、旋转表示、RViz |
| D:/Personal/Desktop/实践PPT/Lesson12.pdf | 123 | 静态/动态 TF2、坐标点变换、多坐标系、小乌龟跟随、时间查询 |
| D:/Personal/Desktop/实践PPT/Lesson13.pdf | 73 | URDF、双层差速机器人、RViz、Xacro、Arbotix |
| D:/Personal/Desktop/实践PPT/Lesson14.pdf | 48 | Gazebo、碰撞/惯性、世界文件、差速插件、激光雷达和深度相机 |
| D:/Personal/Desktop/实践PPT/Lesson15.pdf | 37 | Gazebo 模型稳定性、传感器、导航框架、Gmapping/AMCL/move_base |
| 合计 | 352 | 五份文件均纳入 |

本次完成：352 页文字逐页读取；352 页全部渲染；通过 32 张带页码总览图查看全部页面；28 页关键截图、公式和参数另行放大复核。低文本页 105 页，不能将其误当作空白页。五份 PDF 均没有内嵌的源码附件。

单独放大复核页：Lesson11：22、23、24、27、51、52、56、64、65；Lesson13：28、29、33、34、45、46、47、48、49、59、60；Lesson14：35、37、39；Lesson15：8、9、16、17、19。Lesson12 大量代码可从文字层提取，文字已全部阅读，图示均做了总览核对。

“读过课件”不等于“已在用户 Ubuntu 中运行通过”。本次未连接或修改 Ubuntu，未安装 ROS 依赖，未编译、启动这些实践程序。截图裁切外的代码、外链视频、未附带的 `.world`、`.rviz`、导航 YAML 等，不能说成已经拿到完整原始文件。后续实际使用截图代码时，仍需回到对应原页逐行核对。

页码均指 PDF 从封面开始的实际页码，不以幻灯片中的章节号代替。

## 2. 与之前实践的衔接

沿用历史谈话中已知的学习环境作为初始假设：ROS 1 Noetic、Ubuntu 20.04 风格环境、用户名 `thl`、工作空间 `/home/thl/catkin_ws`。这些是历史上下文，不代表本次现场检查了虚拟机状态；下次动手前先确认是否仍然一致。

此前做过：catkin 工作空间、`beginner_tutorials` / `robot_course_pkg`、自定义消息、`package.xml` 与 `CMakeLists.txt`、turtlesim、话题/服务、launch、TF2 演示。

需要继续遵守的具体约定：

1. 命令、参数之间必须有空格，如 `mkdir -p ~/catkin_ws/src`；包名和文件名中的下划线不能改成空格。
2. 工作空间顶层 `/home/thl/catkin_ws/src/CMakeLists.txt` 与功能包自己的 `CMakeLists.txt` 不同；功能配置改功能包内的文件。
3. `package.xml` 只有一个根元素 `<package>...</package>`；不能把依赖标签加到根元素之后。
4. 自定义消息构建顺序为：`find_package(... message_generation ...)` → `add_message_files(...)` → `generate_messages(...)` → `catkin_package(...)`；实际 `.msg` 必须存在。
5. 构建在工作空间根目录进行：`cd /home/thl/catkin_ws` 后执行 `catkin_make`，成功后加载 `devel/setup.bash`。
6. 之前的 URDF 截图实现请求被用户叫停，本次只是研读新课件，不自动恢复那次实现或替用户修改系统。

课程中的 `rcdp`、`ros_bilibili`、`tf2_roswiki`、`rs_urdf`、`rs_gazebo`、`rs_nav` 是示例/自建包名，不能假设安装 ROS 后自动存在，也不能在同一套文件里随意混用。后续若沿用 `rcdp`，launch 路径、`$(find rcdp)`、包名和实际目录都要一致。使用现有 `robot_course_pkg` 则应明确统一替换，而不是改一处漏几处。

## 3. 整体实践顺序

```text
已有 ROS 基础与 catkin 工作空间
  → Lesson11：观察节点、话题、日志、数据记录和 RViz
  → Lesson12：理解并实现 TF2 坐标系关系
  → Lesson13：URDF 模型 → RViz → Xacro 参数化
  → Lesson14：添加碰撞和惯性 → Gazebo → 驱动及传感器
  → Lesson15：修正稳定性 → 检查传感器/里程计/TF → 建图 → 定位导航
```

前一阶段通过检查再进入后一阶段：模型在 RViz 显示成功，不等于 Gazebo 物理模型正确；Gazebo 能运动，不等于已具备正确里程计和导航 TF；出现 `/scan`，也不等于扫描 frame、时间和地图链路都正确。

## 4. Lesson11：调试工具、TF2 基础与 RViz

### 4.1 页码索引

| 页码 | 学习内容 | 后续实践产物/检查 |
| --- | --- | --- |
| 1–5 | 封面、课堂回顾/评价和预习题 | 课程背景，不是自动执行任务 |
| 6–24 | rqt、graph、publisher、service caller、console、plot、bag | 节点连接图、日志、曲线、bag 文件 |
| 25–34 | ROS API 及常用消息/工具包 | 按实际需要查对应 API，不是全部包都要安装 |
| 35–45 | TF2、坐标系、turtle_tf2 演示 | 观察 world 与两只乌龟之间的 TF |
| 46–58 | RPY、欧拉角、轴角、万向节锁、四元数 | 正确设置方向和旋转顺序 |
| 59–69 | RViz 安装、界面、显示类型、TF 演示 | 设置 Fixed Frame、添加显示项 |
| 70–71 | 小结/练习 | 对照前述知识检查理解 |

### 4.2 核心操作

课件涉及的常用入口如下；只是命令参考，本次未执行安装或启动：

```bash
rosrun rqt_gui rqt_gui
rosrun rqt_graph rqt_graph
rosrun rqt_publisher rqt_publisher
rosrun rqt_service_caller rqt_service_caller
rosrun rqt_console rqt_console
rosrun rqt_plot rqt_plot
rosrun rqt_bag rqt_bag
rosrun rviz rviz
roslaunch turtle_tf2 turtle_tf2_demo_cpp.launch
```

rqt_graph 查看连接关系；rqt_publisher 发布消息；service caller 调用服务；console 看日志；plot 看数值随时间变化；bag 记录/回放话题。日志等级包括 DEBUG、INFO、WARN、ERROR、FATAL；DEBUG 是否可见取决于日志配置，FATAL 日志本身不等价于自动退出程序。

第 22–24 页截图中的 rosbag 用法，需要保留空格和参数位置：

```bash
rosbag record -a
rosbag record -O practice.bag /turtle1/cmd_vel /turtle1/pose
rosbag info practice.bag
rosbag play --pause practice.bag
rosbag play -r 0.5 practice.bag
```

记录和回放要明确是否仍有原发布节点运行；不能一边原程序发布，一边不加区分地回放到相同控制话题。

### 4.3 方向与可视化

- 坐标轴通常红 X、绿 Y、蓝 Z；采用右手系。
- 固定轴 RPY：roll 绕 X、pitch 绕 Y、yaw 绕 Z，ROS API 参数通常用弧度。
- `tf2::Quaternion q; q.setRPY(roll, pitch, yaw);` 比手抄易错公式更可靠。
- 四元数数学表达可能把 `w` 写在最前，但 ROS 消息字段和 TF2 四标量构造通常为 `x,y,z,w`；不能按截图排版直接当赋值顺序。
- RViz 的 Fixed Frame 必须在当前 TF 树中可用；RobotModel 需要正确的 `robot_description` 和模型各 link 的 TF。
- RViz 中 Image、Camera、LaserScan、PointCloud2、Map、Path、Odometry 等显示项，要和发布的消息类型对应，不能仅凭话题名添加错误显示类型。

## 5. Lesson12：TF2 编程实践

### 5.1 页码与程序对应

| 页码 | 内容 | 课件程序/文件 |
| --- | --- | --- |
| 1–20 | 回顾、TF2 消息类型、时间与持续时间 | `TransformStamped`、`PointStamped` |
| 21–37 | 静态坐标变换发布/订阅 | `tf_static_pub.cpp`、`tf_static_sub.cpp` |
| 38–46 | ROS Wiki 风格静态广播及命令行工具 | `static_turtle_tf2_broadcaster.cpp`、静态发布 launch |
| 47–49 | 复习/练习 | 静态 TF 与点变换 |
| 50–70 | 动态 TF，乌龟位姿转 TF | `tf_dynamic_pub.cpp`、`tf_dynamic_sub.cpp` |
| 71–76 | 参数、通用乌龟广播程序 | `turtle_tf2_broadcaster.cpp` |
| 77–101 | 多坐标系转换、代码复用和 launch | `tf_multi_*` 示例 |
| 102–111 | 创建 turtle2、两只乌龟跟随 | spawn 客户端、广播节点、跟随节点、launch |
| 112–121 | 新增 carrot 坐标系、动态 frame、历史时间查询 | frame 广播、listener、TF 树检查 |
| 122–123 | 小结/练习 | 复盘完整数据链路 |

### 5.2 必须掌握的字段和方向

`geometry_msgs::TransformStamped` 包括父坐标系 `header.frame_id`、子坐标系 `child_frame_id`、时间戳、平移和四元数。其内容描述子坐标系相对父坐标系的位姿；不要把坐标系位姿与“把点从哪变到哪”混为一谈。

```cpp
buffer.lookupTransform("target_frame", "source_frame", ros::Time(0));
buffer.transform(source_point, "target_frame");
```

第一条返回可将 source 中坐标表示转换到 target 的变换。第二条的输入点必须声明真实 `header.frame_id`。`ros::Time(0)` 请求最新可用关系，不是所有真实传感器消息都可以随意改成时间 0；实际融合应关注原始采样时间。

静态 TF 通过 `StaticTransformBroadcaster` 发布到 `/tf_static`，动态 TF 通过 `TransformBroadcaster` 发布到 `/tf`。Buffer 与 Listener 要有足够长的生命周期，不能在每次查询前临时创建就立即期待已有缓存。

课件静态示例：laser 相对 baselink 平移 `(0.1,0,0.2)`、无旋转，laser 中点 `(2,3,5)` 转到 baselink 为 `(2.1,3,5.2)`。示例里 `baselink` 与后文 `base_link` 不完全一致，实际程序必须统一。

Noetic 的 TF2 静态发布命令示例：

```bash
rosrun tf2_ros static_transform_publisher 0.1 0 0.2 0 0 0 base_link laser
```

此工具欧拉角参数次序是 `x y z yaw pitch roll parent child`，不同于 C++ `setRPY(roll,pitch,yaw)`。不要把 ROS 2 命令格式或旧 `tf` 工具的周期参数混入此命令。frame 名不加开头 `/`。

### 5.3 时间、多坐标系与小乌龟

- Time 表示时刻，Duration 表示时间长度；Time − Time 得 Duration，Time ± Duration 得 Time。
- 课件 `ros::Time(5,20000000)` 为 5.02 秒，不是 5.2 秒。
- 多坐标系例：local1 在 world 的原点为 `(1,2,3)`，local2 为 `(4,5,6)`，均无旋转；local1 原点在 local2 中为 `(-3,-3,-3)`。local1 中点 `(2,3,5)` 在 local2 中为 `(-1,0,2)`。第 82 页另处点值不同，计算时必须明确用的是哪组点。
- 动态例：订阅 `/turtle1/pose`，用 `x,y,theta` 广播 `world → turtle1`，其中 `q.setRPY(0,0,theta)`。
- 跟随例：生成 turtle2；分别广播 `world → turtle1`、`world → turtle2`；查询 turtle1 在 turtle2 中的位置；向 `/turtle2/cmd_vel` 发布速度。
- 原示例控制律为 `v = 2*sqrt(dx*dx+dy*dy)`、`w = 2*atan2(dy,dx)`；真实实践需设置速度上限，并在 TF 丢失时停止，而不是沿用无限制控制量。
- 两只乌龟跟随是根据相对位置闭环控制，不应简单解释成永远复制 turtle1 的前进/后退键。
- carrot 示例分为固定偏移 frame 和随时间变化的 frame；时间穿越通常应表达“现在的跟随者追踪目标过去的位置”，目标/源时间与固定参考 frame 都要明确。

### 5.4 后续交付需要的文件与检查

TF2 C++ 实践会给：`src/*.cpp`、包级 `CMakeLists.txt`、`package.xml`、必要的 `launch/*.launch`，而不只给一段 main。

依赖按用途选择 `roscpp rospy std_msgs geometry_msgs tf2 tf2_ros tf2_geometry_msgs turtlesim`；只有实际用到的才添加。C++ 目标要配置 `add_executable`、`target_link_libraries(... ${catkin_LIBRARIES})` 等。

检查至少包括：`/tf` 或 `/tf_static` 是否存在；frame 名/父子关系；查询的 target/source 是否反了；TF 时间；编译目标名是否与 launch `type` 一致；参数数量判断失败后是否真正退出。第 91 页 `atoi` 不适合带小数的平移参数，第 107 页缺参数只打印错误仍继续访问 argv 的写法需要修正。

## 6. Lesson13：URDF、Xacro、RViz 与 Arbotix

### 6.1 页码索引

| 页码 | 内容 | 后续产物 |
| --- | --- | --- |
| 1–10 | 回顾、URDF/RViz/Gazebo 关系与安装背景 | 明确显示和物理仿真不同 |
| 11–21 | URDF robot/link/joint、几何和属性 | URDF 结构与关节树 |
| 22–26 | 创建功能包、目录、加载模型、保存 RViz | package、launch、rviz 配置 |
| 27–34 | 双层差速机器人、TF 缺失与状态发布 | 机器人 URDF 与显示 launch |
| 35–49 | Xacro 前置讨论及机器人截图源码 | link、joint 和尺寸对应关系 |
| 50–63 | Xacro 属性、表达式、宏、包含及加载 | `.xacro` 及展开后的 URDF |
| 64–71 | Arbotix 模拟控制与键盘控制 | YAML、模拟里程计和启动文件 |
| 72–73 | 小结/练习 | 模型和控制流程复盘 |

### 6.2 建模规则与显示链路

- `<robot>` 是根元素；`link` 表示刚体，`joint` 定义父子 link 的连接关系。
- `visual` 管显示，`collision` 管碰撞，`inertial` 管质量/惯性；只做 RViz 外观时可以先只完成 visual，做物理仿真再补完整物理属性。
- `visual/origin` 相对 link 坐标系；`joint/origin` 相对父 link 坐标系；`joint/axis` 按关节坐标系解释。
- 连续旋转用 `continuous`；有限角度旋转用 `revolute` 并给 limit；固定连接用 `fixed`。
- URDF 只能描述运动学树，不等价于电机控制程序或导航程序。

```text
URDF/Xacro → robot_description
                    ↓
关节状态来源 → /joint_states → robot_state_publisher → /tf、/tf_static → RViz
```

纯显示时可用 `joint_state_publisher` / GUI 提供关节值；Gazebo 中若驱动插件已发布真实仿真关节状态，就不能再不加区分地启动另一套假关节值来源。

课件实践目录可按下列关系组织，最终文件名以实际交付为准：

```text
/home/thl/catkin_ws/src/rcdp/
├── package.xml
├── CMakeLists.txt
├── urdf/
│   ├── urdf/2-1/myrobot.urdf
│   └── xacro/3-1/...
├── meshes/
├── config/                 # .rviz 与控制器 YAML
└── launch/                 # 显示/控制启动文件
```

`<param name="robot_description" textfile="..."/>` 是读取 URDF 文件内容存入参数，不是把路径字符串当模型；原始 Xacro 应通过 `xacro` 处理后加载。保存 RViz 配置之后，再给 RViz 节点加 `args="-d 配置路径"`，不要先引用不存在的 `.rviz` 文件。

### 6.3 双层机器人截图参数记录

以下为第 43–49 页截图读取的原模型，不是已经完成运行验证的最终物理模型。长度单位米，角度弧度。

| link 名 | 外形/尺寸 |
| --- | --- |
| `root_link` | 极小圆柱：半径、长度均 0.0001，用作参考根 link |
| `base_link` | 下层圆柱：半径 0.4、长 0.3 |
| `front_support_wheel_link`、`back_support_wheel_link` | 球形支撑轮：半径 0.05 |
| `left_wheel_link`、`right_wheel_link` | 驱动轮圆柱：半径 0.1、宽 0.08；visual 绕 X 约 1.57 |
| `support_link` | 中间立柱：半径 0.1、长 0.8 |
| `platform_link` | 上层平台圆柱：半径 0.25、长 0.15 |
| `laser_scan_link` | 雷达外观 box：0.05 × 0.06 × 0.08 |
| `depth_camera_link` | 相机外观 box：0.05 × 0.08 × 0.08 |

| joint | 类型 | 父 → 子 | 原点 xyz | 轴/限制 |
| --- | --- | --- | --- | --- |
| `base_link2root_link` | fixed | root → base | 0,0,0.25 | 固定 |
| `front_support_wheel_link2base_link` | continuous | base → front_support | 0.32,0,-0.2 | 原示例 axis=1,1,1 |
| `back_support_wheel_link2base_link` | continuous | base → back_support | -0.32,0,-0.2 | 原示例 axis=1,1,1 |
| `base_l_wheel_joint` | continuous | base → left_wheel | 0,0.4,-0.15 | 0,1,0 |
| `base_r_wheel_joint` | continuous | base → right_wheel | 0,-0.4,-0.15 | 0,1,0 |
| `support_link2base_link` | fixed | base → support | 0,0,0.55 | 固定 |
| `platform_link2support_link` | fixed | support → platform | 0,0,0.475 | 固定 |
| `depth_camera_link2base_link` | revolute | base → depth_camera | 0.32,0,0.19 | 0,0,1；截图 ±1.57 |
| `laser_scan_link2platform_link` | continuous | platform → laser_scan | 0.2,0,0.115 | 0,0,1 |

共 10 个 link、9 个 joint。表中 root/base 等缩写仅为方便阅读，代码应使用完整 link 名。相机实践文字要求 -180° 至 180°，截图却是 ±1.57（约 ±90°）；若按文字要求实现，限位应改为约 ±3.141593，并明确这是对原截图的修正。雷达无角度限位的连续旋转用 continuous，而不是只允许一次 0–360° 的有限关节。

支撑轮的单轴球形建模是课件简化，不应直接当作任意方向自由滚动的真实万向轮。Lesson15 还会调整底盘高度和支撑位置，因此不要把 Lesson13 的外观几何直接认定为最终稳定物理结构。

### 6.4 Xacro 和 Arbotix

Xacro 重点：`xacro:property` 定义参数，`${...}` 引用/计算，`xacro:macro` 复用结构，`xacro:include` 组织文件；标准命名空间使用 `http://wiki.ros.org/xacro`。

```bash
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/xacro/3-1/myrobot_v2.xacro > /tmp/myrobot_expanded.urdf
check_urdf /tmp/myrobot_expanded.urdf
```

此处输出到临时文件的命令是后续检查示例；源文件需先实际创建，且没有与用户已有文件重名覆盖。

Arbotix 是本课 RViz 中模拟差速底盘的一条练习路线，不等于 Gazebo 物理仿真。第 66–68 页 YAML 重点：`diff_controller`、`base_frame_id: root_link`、`base_width: 0.8`、`ticks_meter: 2000`、Kp/Kd/Ki/Ko 和加速度限制；具体配置须与实际模型和驱动版本匹配。

## 7. Lesson14：Gazebo、差速控制与传感器

### 7.1 页码索引

| 页码 | 内容 | 后续产物 |
| --- | --- | --- |
| 1–5 | 回顾与 Gazebo 引入 | 明确仿真目标 |
| 6–13 | 模型依赖、collision、质量惯性、Gazebo 材质 | 可物理仿真的 Xacro |
| 14–20 | Gazebo 进程、启动问题和模型资源 | 按实际报错排查，不盲目批量杀进程 |
| 21–24 | 加载 world、生成机器人 | world 与 spawn_model launch |
| 25–30 | 场景/建筑编辑、保存 world 和模型 | `.world`、模型资源 |
| 31–35 | 控制概念、transmission、差速插件截图 | `move.xacro` |
| 36–37 | 激光雷达 | `laser.xacro` |
| 38–39 | 深度相机 | `kinect.xacro` |
| 40–43 | 文件包含、Gazebo/RViz launch 和启动 | 传感器组合模型和启动文件 |
| 44–48 | 结果图、小结与练习 | 检查话题、TF、显示和运动 |

### 7.2 物理属性

球体：三个主轴惯量均为 `2*m*r*r/5`。

圆柱轴沿 Z：`Ixx = Iyy = m*(3*r*r+h*h)/12`，`Izz = m*r*r/2`。

长方体约定尺寸为 X=l、Y=w、Z=h：`Ixx=m*(w*w+h*h)/12`，`Iyy=m*(l*l+h*h)/12`，`Izz=m*(l*l+w*w)/12`。第 12 页宏的变量组合不符合这一轴约定，后续必须先统一几何轴与惯性轴，不能照抄变量排列。

轮子圆柱若从 Z 轴旋到 Y 轴，碰撞形状与惯性方向也需要匹配；不能仅旋转 visual。URDF 惯性相对质心表达，惯性矩阵必须合理，不能用负质量或随意的零惯性糊弄错误。

RViz 材质颜色与 Gazebo 材质不是一回事；课件用 `<gazebo reference="link名"><material>Gazebo/...</material></gazebo>` 设置仿真显示颜色。

### 7.3 世界加载与模型生成

课件路线：展开 Xacro → 设置 `robot_description` → include `gazebo_ros/launch/empty_world.launch` 并指定 world → 运行 `gazebo_ros/spawn_model` 的 `-urdf -model ... -param robot_description`。

第 21–24 页与后续截图的模型路径不完全一致；第 40 页组合文件又引入传感器。未来交付需确保 Gazebo 生成和 RViz 状态发布使用同一份一致的模型，不能各自加载不同关节树。

课件出现的 `box_house.world` 和场景模型并未以原文件附在 PDF 内。若用户没有老师的资源，需明确补建简化世界，不能假称已取得相同原场景。

### 7.4 控制与传感器的具体参数

第 35 页实际展示的驱动插件为 `libgazebo_ros_diff_drive.so`。这条直接差速驱动路线和 `gazebo_ros_control` + 控制器管理器是不同接法；不能因为前一页介绍了 ros_control 就混搭两套驱动同一轮关节。

截图涉及 `base_l_wheel_joint`、`base_r_wheel_joint`、轮距 `2*base_radius`、轮径 `2*move_wheel_radius`、更新率 100 Hz、发布轮关节状态及 TF 等设置。截图没有完整展示所有配置尾部；完整可运行文件需要补齐并按实际插件版本核对。

| 传感器 | Lesson14 原参数 | 后续检查 |
| --- | --- | --- |
| 激光雷达 | link=`laser_scan_link`，ray，360 samples，5.5 Hz，角度 -3 到 3 rad，距离 0.10–30 m，噪声标准差 0.01 | 插件 `libgazebo_ros_laser.so`，话题 `/scan`，frame 要与模型一致；6 rad 不是精确 360° |
| 深度相机 | link=`depth_camera_link`，depth，640×480，60° 水平视场，0.05–8 m | 插件 `libgazebo_ros_openni_kinect.so`；图像、深度、点云、CameraInfo 的话题和 frame |

深度插件截图使用 `cameraName=kinect`、`rgb/image_raw`、`depth/image_raw`、`depth/points`、`rgb/camera_info`、`depth/camera_info` 和 `rotate_depth_camera_link`；最终解析后的话题名应在仿真启动后查看，不能只凭字符串猜。

第 42 页的静态相机坐标旋转需要与光学坐标约定核对。若使用 optical frame，须保证轴含义正确。若驱动插件已发布轮关节 TF，再由 robot_state_publisher 发布同一边，会造成多发布者冲突，应选择一致的 TF 发布责任。

## 8. Lesson15：模型修正、传感器与导航

### 8.1 页码索引

| 页码 | 内容 | 后续产物 |
| --- | --- | --- |
| 1–3 | 回顾 | 与上一课接续 |
| 4–10 | 底盘倾斜、驱动轮方向、质量/惯性和支撑轮修正 | 稳定的仿真模型 |
| 11–14 | 键盘控制与 RViz | 实际话题和模型显示检查 |
| 15–20 | 雷达、RGB 相机、深度点云插件 | 传感器模型、话题、TF |
| 21–34 | 导航结构、SLAM、地图、AMCL、规划、odom/map | 导航数据关系和 TF 链 |
| 35–36 | 安装/创建包及启动命令框架 | 后续仍需补齐 launch/YAML/地图 |
| 37 | 结束页 | 无新增实践源码 |

### 8.2 模型稳定性修正

课件将底盘中心高度设置为 `base_height/2 + move_wheel_radius`；驱动轮关节的 Z 为 `-base_height/2`，左右 Y 为 `±base_radius`，转轴 `0 1 0`。

支撑球的 Z 为 `-(base_height/2 + support_wheel_radius)`，前后 X 为 `±0.8*base_radius`。依此两组几何关系计算，车轮和支撑球的最低点可对齐地面。第 8 页还展示支撑轮碰撞/惯性宏；第 9 页强调驱动轮关节方向和质量/根 link 处理。

这些是课件修正方案，不代表所有任意尺寸与质量组合都已保证稳定。后续需检查落地高度、接触碰撞、质心、惯性、摩擦、速度和仿真步长，而非仅看“窗口里出现机器人”。

### 8.3 传感器文件存在跨课差异

- 第 16 页雷达 reference 是 `laser_camera`，上一课为 `laser_scan_link`，不能直接拼接两页文件。
- 第 17 页 RGB 相机为 camera sensor、30 Hz、1280×720、水平视场约 80°，使用 `libgazebo_ros_camera.so`；有 `depth_camera` 等命名。
- 第 19 页深度传感器挂在 `support_link`，但插件 frame 写 `camera_link`；这与上一课相机安装 link 不一致。模型位置与消息 frame 不匹配时，RViz 点云会出现在错误位置或报 TF 错误。
- `rs_gazebo`、`rs_nav` 是本课另一套例子包名，不说明原先 `rcdp` 应被删除或替换。

### 8.4 导航完整链路

```text
/scan + 里程计 + 机器人 TF
  ├─ 建图阶段：Gmapping → /map → 保存地图
  └─ 导航阶段：map_server → 已知地图
                         + AMCL → map→odom
                         + move_base → 全局/局部规划 → /cmd_vel
                                                        ↓
                                                  差速驱动与机器人
```

TF 的基本连接应为 `map → odom → base_link`，允许插入 `root_link`、`base_footprint` 等有明确含义的中间 frame，但必须连通且每个子 frame 只有一个父 frame。课件中的 `doom` 为 `odom` 的笔误。odom 连续但会漂移；map 提供长期全局参考，定位修正可能产生跳变。

AMCL 用于已知地图定位，不是建图算法。Gmapping 用于 SLAM。`move_base` 将目标、地图、障碍和机器人状态结合，产生控制速度。课件提到 A*/Dijkstra 与 DWA，不表示整个 ROS 导航框架只支持这几种规划器。

第 35–36 页给出 gmapping、map_server、navigation、amcl、move_base 的依赖/启动思路，但没有给出一套完整的导航包源码：costmap、机器人 footprint、全局/局部规划器、AMCL、激光配置、地图加载和保存文件均需结合实际机器人补齐。

课件中的启动示例：`roslaunch rs_nav gazebo_control.launch`、`roslaunch rs_nav gmapping.launch`、`roslaunch rs_nav move_base.launch`。这些只有在对应包和文件实际存在时才可用，不是安装系统导航包后就自动拥有的命令。

## 9. 重要勘误和使用边界

下表区分明确拼写/接口错误、课件内部冲突以及实际部署时需补充的工程条件。主要接口已对照官方 Noetic 消息定义、TF2 源码、joint_state_publisher 源码及 REP；未将所有截图中的程序称为运行通过。

| 来源 | 问题 | 后续处理 |
| --- | --- | --- |
| L11 p57–58 | 四元数公式与固定轴 RPY API 不能混用 | 采用 `setRPY(roll,pitch,yaw)`，弧度，明确 xyzw |
| L11 p64 | `sensor_msgs/JointStates` 拼写 | 正确为 `sensor_msgs/JointState` |
| L11 p65 | RViz Polygon 显示消息类型需注意带 header | 核对实际 RViz 显示项，通常用 `geometry_msgs/PolygonStamped` |
| L11 p68 | 建议删除 `/usr/bin/python` 再链接到 python3.8 | 不照做；Noetic 使用 Python3，先查脚本 shebang、安装方式和依赖 |
| L12 p17 | Time 与 Duration 字段类型概括不准确 | ROS1 Time 的 sec/nsec 为无符号，Duration 为有符号；按 API 定义使用 |
| L12 p19 | `(5,20000000)` 被写成 5.2 秒 | 实际为 5.02 秒 |
| L12 p41–44 | world/baselink/base_link 混用，frame 带 `/` | 实际图与代码统一命名；TF2 frame 不以 `/` 开头 |
| L12 p43 | 命令行角度次序容易与 API 搞反 | CLI 为 yaw,pitch,roll；setRPY 为 roll,pitch,yaw |
| L12 p71 | node 内 param 的命名空间描述 | node 内通常为私有命名空间，结合 `NodeHandle("~")` 理解 |
| L12 p82、p95–96 | 同一转换例的点值前后不同 | 先明确坐标值再算，不混用结果 |
| L12 p91、p107 | 整数转换导致小数截断，参数不足未退出 | 补参数检查与浮点解析；错误路径 return |
| L12 p120–121 | 时间穿越只有启动/结果说明，缺完整 listener 源码 | 未来补充实现时明确标“补全”，不是原文完整源码 |
| L13 p17 | RGBA 中文颜色说明写成红黄蓝 | 应为红、绿、蓝、透明度 |
| L13 p20 | `planer` 关节名 | 正确类型为 `planar` |
| L13 p24–25 | rs_urdf 与 rcdp 混用 | 按实际创建的包统一 `$(find ...)` |
| L13 p31 | `/joint_state`、包含加速度的表述 | 话题通常 `/joint_states`；消息字段为 name/position/velocity/effort，无 acceleration |
| L13 p32 | `/tf2` 被当作变换话题 | 正确为 `/tf` 和 `/tf_static`；TF2 是库/系统名称 |
| L13 p34 | 笼统建议删除 URDF 全部注释 | 合法 XML 注释允许存在；应按具体语法报错修正 |
| L13 p27 与 p49 | 摄像头文字要求 ±180°，截图 limit ±1.57 | 按实践要求取 ±π，注明修正 |
| L14 p12 | box 惯性公式轴与变量组合 | 先固定 XYZ 尺寸定义再写正确公式 |
| L14 p21–24、p40–42 | 多个模型路径及组合层级 | 一个实际存在且一致的模型作为加载来源 |
| L14 p32–35 | ros_control 概念与 diff_drive 插件路线混在一起 | 不让两套驱动同时控制同一组关节 |
| L14 p37/L15 p16 | -3 到 3 rad 被容易理解为 360° | 实际约 343.8°；需要全周时使用 ±π 并核对端点采样 |
| L14 p42 | 假关节状态与插件关节状态/重复 TF | 明确每个话题和 TF 边由谁负责，避免冲突 |
| L15 p16–19 | 传感器挂载 link 与 frame 跨页不一致 | 对照最终 URDF 和插件参数逐项统一 |
| L15 p32–34 | `doom` | 改为 `odom` |
| L15 p35–36 | 只有导航安装/启动框架 | 未来需补齐模型相关导航参数，不声称原 PDF 已含全套代码 |

## 10. 后续实质性实践的交付方式

用户指定某课某实践后，按以下顺序交付，不只解释概念：

1. 确认使用的 ROS 版本、现有包名和当前目录；必要时先让用户运行少量只读检查，不重复重装整个环境。
2. 给完整目标目录树，以及每个文件的准确绝对路径。
3. 逐文件给完整代码：C++/Python、URDF/Xacro、launch、YAML、`package.xml`、包级 `CMakeLists.txt` 等；不存在的文件先创建，已有文件按实际内容修改，避免覆盖用户无关工作。
4. 明确“课件原文”“必要修正”“为可运行而补全”三类内容；原截图裁切处不伪称原作者代码。
5. 给依赖安装、编译、加载环境、启动的顺序；区分终端 1/2/3，说明长驻程序、新开终端、是否需要单独 roscore。
6. 每阶段给验收指令和预期现象：节点/话题、TF、模型、运动、传感器、地图或导航结果。
7. 给退出方式 `Ctrl+C`、保存文件位置和常见报错；不把删除 build/devel、修改系统 Python 或批量杀进程当作默认解决办法。
8. 明确验证等级：静态检查、用户现场编译、实际启动、端到端成功；没有完成的级别不宣称通过。

可以直接这样提出后续请求：

- “按 Lesson12 静态 TF 示例，从建包到运行给我全部代码。”
- “按 Lesson13 双层机器人实践，使用 rcdp 包，给我 URDF 和 launch。”
- “在我已有模型上继续 Lesson14，补 Gazebo 惯性、雷达和相机。”
- “按 Lesson15 做建图和导航，先检查我的话题和 TF，再给配置。”

## 11. 可追溯材料

本工作区的中间材料保存在 `C:/Users/cris/Documents/Codex/2026-09-02/xu/work/practice_pdf_study/`：

- `inventory.json`：原文件路径、字节数、SHA256、页数、低文本页。
- `pages.json`、`page_index.tsv`：逐页文字与索引。
- `Lesson11.read.txt` 至 `Lesson15.read.txt`：带 PDF 页码的可读文本。
- `renders/Lesson11/` 至 `renders/Lesson15/`：全部页面图片与总览图。
- `coverage.json`：本次覆盖与未验证边界。

下列官方来源用于核对易错接口，不取代课程原页：

- [Noetic TF2 静态发布工具源码](https://raw.githubusercontent.com/ros/geometry2/noetic-devel/tf2_ros/src/static_transform_broadcaster_program.cpp)：参数次序和发布方式。
- [Noetic TF2 Quaternion 源码](https://raw.githubusercontent.com/ros/geometry2/noetic-devel/tf2/include/tf2/LinearMath/Quaternion.h)：setRPY 和 xyzw 顺序。
- [Noetic JointState 消息定义](https://github.com/ros/common_msgs/blob/noetic-devel/sensor_msgs/msg/JointState.msg)：实际字段与类型名。
- [Noetic joint_state_publisher 源码](https://raw.githubusercontent.com/ros/joint_state_publisher/noetic-devel/joint_state_publisher/src/joint_state_publisher/__init__.py)：joint_states 发布接口。
- [robot_state_publisher 的 ROS Index](https://index.ros.org/p/robot_state_publisher/)：使用时切到 Noetic 条目，不把页面默认 ROS2 文档当作 ROS1 API。
- [REP-105 坐标系约定](https://github.com/ros-infrastructure/rep/blob/master/rep-0105.rst)：map/odom/base_link 的关系和连续性。
- [REP-151 Python3](https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-0151.rst)：Noetic 的 Python3 与脚本处理。

本记录是可查阅的课程学习依据，不是对未来每台机器的运行保证。后续具体实践应回到原 PDF 对应页，并以用户机器的真实编译输出、话题与 TF 作为最终验证证据。
