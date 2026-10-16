# ROS 小车实践复盘：2026-10-15—16

本文回答：这两天做了什么、怎样做、遇到什么问题、怎样恢复、还没做什么。日期按中国时间整理，虚拟机显示时间可能不同，不拿文件时间推断运行先后。公开版本不包含个人截图、原始日志、用户名／主机地址、课程原包或新增课件。

证据分两类：**用户现场反馈**是用户在 Ubuntu 执行并回传的输出／观察；**本地静态检查**是助手侧 XML/Xacro/YAML、Python 与合成数据测试。后者不等于在 Ubuntu 或 VMware 运行。

## 1. 总体成果

| 阶段 | 做了什么 | 用户现场验收 |
| --- | --- | --- |
| 原有 step4/6 | 双层差速车物理模型、驱动、短时低速前进并停车 | 此前已通过，保留作为后续基础 |
| 准备 | 分析 Lesson14/15 代码，隔离参考材料，备份现有 rcdp | 参考 package.xml 和备份文件存在 |
| step7 | 加入室内场景、激光雷达 | 小车／房间正常，scan 类型、frame、频率及单帧数据通过 |
| step8 | 仿真真实关节状态、RSP、TF、RViz | 模型与红色扫描显示，运动视觉联动通过 |
| step9 | RGB-D 插件、光学 frame、图像、深度、点云、CameraInfo | 数据基本检查通过；原始完整点云的 RViz 显示曾崩溃 |
| step9a | 软件渲染＋独立轻量点云预览 | 4800 点预览稳定；最终前进／停车、视觉联动和稳定性通过 |

本轮没有完成键盘遥控、SLAM、保存地图、AMCL 或 move_base。最新用户要求先暂停进一步实践，整理 GitHub。

## 2. 起点与路线选择

环境是 Ubuntu 20.04.6、ROS1 Noetic、Gazebo Classic 11.15.1，运行在 VMware。已有工作空间 `~/catkin_ws`，已有包 `rcdp`。模型名 `lesson13_robot`，速度 `/cmd_vel`，里程计 `/odom`。

之前已用 `test_forward_step6.py` 完成请求 0.1 m/s、持续 3 秒墙钟、最后发送零速度的测试，用户观察到前进并停止。不是实测走了 0.3 m。

分析课程代码后，选择：**保留已跑通的模型和单个差速插件，逐步加传感器／TF／显示，再考虑导航。** 不整包覆盖当前 rcdp，也不在当前根命名空间再起 rs_gazebo。

原因：另一套 rs_gazebo 的尺寸、轮关节名、雷达 frame 均不同。悄悄换模型会使已验证的物理和控制条件失效。

## 3. 准备：分离参考材料，先备份

用户把 Lesson14、Lesson15 原始 ZIP 放入 Ubuntu 主文件夹，并将参考材料解压到 `~/ros_course_reference/`，不放入当前工作空间 src 来制造同名包冲突。随后确认 Lesson14 的 rcdp 和 Lesson15 的 rs_nav 的 package.xml 存在。

现有 rcdp 的备份放在 `~/ros_course_backups/`，用户已列出压缩文件；没有做恢复演练，因此只确认备份文件存在，不宣称完成了可恢复性测试。该备份早于后续 step7–9a，继续改工程前应再备份当前成功版本。

检查结果：robot_state_publisher、joint_state_publisher、RViz 和 Gazebo 雷达／深度相机／关节状态插件可找到；teleop_twist_keyboard 未找到。**软件存在不等于整个功能运行成功。** 此时没有为一个缺包盲目安装全部 ROS，也未确认早前 DNS 故障恢复。

## 4. step7：室内场景与雷达

### 改动

- `urdf/gazebo/myrobot_laser_step7.xacro`：包含既有 step6，只追加雷达。
- `urdf/gazebo/gazebo_sensor/lesson14_laser_step7.xacro`：ray 传感器和 `libgazebo_ros_laser.so` 配置。
- `launch/myrobot_laser_step7.launch`：加载场景、模型，spawn 一台车。
- 用户本地的 `worlds/lesson14_box_house_step7.world`：课程室内场景；本次公开更新不新增分发该文件。

雷达挂在 `laser_scan_link`，输出 `/scan`，360 个角度采样，角范围 -3 到 +3 rad（约 343.8°，不是正好 360°）；配置 5.5 Hz、距离 0.1–30 m。

### 当时的操作顺序

在阶段文件已经导入、之前的仿真已正常停止后，用户展开 Xacro，然后启动并检查。下列使用 HOME 代替个人路径：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
rosrun xacro xacro "$HOME/catkin_ws/src/rcdp/urdf/gazebo/myrobot_laser_step7.xacro" -o /tmp/lesson14_laser_step7.urdf
roslaunch rcdp myrobot_laser_step7.launch
```

另开终端：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
rostopic info /scan
rostopic echo -n 1 /scan/header
rostopic hz /scan
```

不要现在为了回看流程重复启动以上旧阶段；当前用的是 step9。

### 验收

- 用户确认小车和房间开启。
- `/scan` 类型 sensor_msgs/LaserScan，发布节点 `/gazebo`，frame `laser_scan_link`。
- 短时频率约 5.495 Hz。
- 一帧 360 样本全部有效，最近有效距离约 1.749193 m；配置上下限读回约 0.1 与 30 m。

这证明数据链路和该帧数值有效，不是激光精度标定，也不代表所有后续帧都有效。

## 5. step8：真实关节状态、TF 与 RViz

### 为什么还要做这一步

能在 Gazebo 看见车，不等于 RViz 知道每个零件相对 odom 的位置。需要机器人描述、关节状态及 TF 一致。

既有差速插件只提供两个驱动轮位置；新增 `libgazebo_ros_joint_state_publisher.so` 只负责其他四个活动关节，避免与驱动轮重复。单个 robot_state_publisher 读取这些状态并发布模型变换，不再运行会伪造同名位置的 joint_state_publisher 节点。

新增文件：`myrobot_tf_step8.xacro`、`myrobot_tf_step8.launch`、`lesson14_scan_step8.rviz`，均位于 rcdp 对应 urdf/gazebo、launch、config 目录。

职责为：Gazebo 驱动发布 `odom → root_link`，RSP 发布模型内部的固定／活动关节 TF。**有两个 /tf 发布节点不自动等于重复同一条边。**

### 排查过程

```bash
rosnode list
rostopic info /tf
rostopic info /clock
rostopic info /joint_states
rostopic info /cmd_vel
rosrun tf tf_echo odom laser_scan_link
```

- tf_echo 刚开始提示找不到 frame，随后连续返回变换；需区分监听器刚接入还没收齐动态 TF，和一直不连通。
- `/joint_states` 的发布节点为 Gazebo，订阅者为 RSP；`/clock` 的发布节点只有 Gazebo。
- 旧 `/sim`、`/teleop` 记录属于 turtlesim 的 turtle1/2 话题，且节点无法通信。没有证据证明它们是当前小车 TF 或 cmd_vel 的冲突源，未据此强杀进程。
- 运动前 `/cmd_vel` 无发布者、Gazebo 为订阅者：这是等待控制指令的正常状态。

### 验收与未解决警告

RViz 固定 frame 为 odom，模型、红色扫描与场景轮廓可见；用户确认低速运动及停车时显示联动正常。

一次约 30 秒墙钟采样收到 odom→root_link 数据 2997 条，重复时间戳为 0，来源为 Gazebo。但后续 step9 又出现 `TF_REPEATED_DATA`，所以这是“这个样本没有复现”，不是“警告已根治”。未逐条保存六个活动关节实时消息的完整清单，不用静态关节数冒充现场清单。

## 6. step9：RGB-D 与光学坐标系

### 新增内容

- `myrobot_camera_step9.xacro` 包含 step8，并追加相机配置。
- `gazebo_sensor/lesson14_camera_step9.xacro` 在现有相机外形前方放置 depth 传感器、配置 OpenNI 插件，同时加无质量的光学参考 frame。
- `myrobot_camera_step9.launch` 让 Gazebo 与单个 RSP 使用同一 robot_description。
- `lesson14_camera_step9.rviz` 用于图像／深度检查；完整原始点云默认关闭。

基础模型的尺寸、质量、驱动、雷达及 6 个活动关节保持不变。模型由原来 10 links/9 joints 变为 11 links/10 joints，只增加一个光学 link 与固定 joint。

`rotate_depth_camera_link` 遵循光学轴约定：Z 朝前、X 向右、Y 向下。相机物理 frame 朝向与消息光学 frame 不能混为一谈；这里在 URDF 内统一，不靠再启动一份互相竞争的静态 TF。

### 话题和参数

| 数据 | 话题 |
| --- | --- |
| RGB | `/kinect/rgb/image_raw` |
| RGB 内参 | `/kinect/rgb/camera_info` |
| 深度 | `/kinect/depth/image_raw` |
| 深度内参 | `/kinect/depth/camera_info` |
| 原始点云 | `/kinect/depth/points` |

图像 640×480；为 VMware 初始负载将传感器和插件都设置 10 Hz；水平视场约 60°；有效深度截止设置 0.4–8 m。深度编码 32FC1 是光学 Z 方向的米，不是所有像素都必为有效数，也不是到相机的欧式距离。

### 实际检查结果

| 检查 | 用户输出摘要 |
| --- | --- |
| RGB | sensor_msgs/Image，Gazebo 发布，frame 正确；图像中可见墙／地面 |
| 深度单帧 | 640×480、32FC1，307200/307200 像素有限且正数 |
| 深度范围 | 约 0.783238–3.837840 m，中心约 3.806936 m |
| 原始点云单帧 | 字段 x/y/z/rgb，point_step 32，9830400 字节 |
| XYZ 数值 | 307200/307200 点有限且 Z>0，Z 约 0.783225–3.452346 m |
| 光学 TF | 初始两次未连通，随后连续查询成功 |
| RGB/Depth CameraInfo | frame 正确、640×480、K 基本检查均为 True |
| 内参 | fx=fy≈554.254691，cx=320.5、cy=240.5 |

两次深度／点云范围来自不同消息，不要求它们数值严格相等。上述均为基本数据／元信息检查，不是传感器物理标定、重投影精度或所有帧同步的证明。

## 7. RViz 完整点云闪退：如何判断与恢复

### 发生了什么

用户启用原始完整点云显示后 RViz 卡死退出，roslaunch 报退出码 **-7**。在 x86 Linux 上对应 SIGBUS。没有崩溃堆栈，不能把它直接说成 OOM、显卡坏、TF 警告导致或点云坏。

### 安全排查

先保留 Gazebo，不重启整套工程。用户检查到 `/scan` 仍有新数据，说明 RViz 崩溃不等于仿真也死了；Gazebo 包装脚本与实际 gzserver 的两行进程记录也不等于开了两套仿真。

崩溃后内存约 4.4 GiB 可用，/dev/shm 未用满，/tmp 所在盘也未满。这只说明采样时没有当前耗尽，不能排除崩溃瞬间压力。尝试查 roslaunch 提示的 RViz 日志没有找到匹配文件，因此未取得可定位 SIGBUS 的堆栈。

### 第一次恢复：只有模型和雷达

在 Gazebo 继续运行的前提下，只重启一个 RViz：

```bash
LIBGL_ALWAYS_SOFTWARE=true rosrun rviz rviz -d "$HOME/catkin_ws/src/rcdp/config/lesson14_scan_step8.rviz" __name:=lesson14_rviz_recovery
```

实际日志确认 llvmpipe（LLVM 12.0.0）和 OpenGL 3.1；用户确认窗口稳定。`Stereo is NOT SUPPORTED` 是普通信息，不是这次退出原因。

这不是完整点云恢复验收，因为当时没有显示点云。没有永久修改 VMware 显卡设置、重装驱动或重装 ROS，也没有禁用必要的 odom TF 来压掉警告。

## 8. step9a：独立低负载点云预览

### 设计

补充两个文件：

- `scripts/cloud_preview_step9a.py`：只做显示数据中继。
- `config/lesson14_cloud_preview_step9a.rviz`：模型、红色扫描、青色轻量预览，10 FPS。

原始点云保持 `/kinect/depth/points`，中继另发 `/lesson14/depth_points_preview`。每 8 行／列选一个完整点记录：640×480 → 80×60，307200 → 4800 点，9830400 → 153600 字节。

保留采集 stamp、frame、字段、字节序及所选点完整字节，不重算 XYZ，不把时间改为 now；ROS 发布 seq 可由新发布端管理，不以 seq 对齐输入。墙钟节流上限 2 Hz、队列 1；无预览订阅者时解除原始订阅。

它不发布 TF、不发 cmd_vel、不改 Gazebo 相机、不重写参数。原始活跃输入仍是 640×480，不能说中继降低了 Gazebo 生成相机数据本身的开销。抽稀预览仅用于显示，不代替原始 CameraInfo／点云用于标定或导航。

### 当时实际运行顺序

保持 step9 Gazebo/RSP 运行。新终端启动中继：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
python3 "$HOME/catkin_ws/src/rcdp/scripts/cloud_preview_step9a.py"
```

先用订阅脚本收到预期的 80×60、4800 点、point_step 32、153600 字节消息。然后关闭单独的旧 recovery RViz，保留 Gazebo 和中继，再启动唯一的预览窗口：

```bash
LIBGL_ALWAYS_SOFTWARE=true rosrun rviz rviz -d "$HOME/catkin_ws/src/rcdp/config/lesson14_cloud_preview_step9a.rviz" __name:=lesson14_rviz_preview
```

默认 Depth_Preview 关闭，确认模型／雷达正常后再勾选，订阅新预览话题，不勾选旧原始大点云。用户确认显示及窗口稳定。

### 本地代码验证

9 个单元测试覆盖大小端、行填充、完整点字节、stamp/frame/source 不变、NaN 与 RGB 字节保留、非法布局拒绝、节流／重复 stamp、参数边界、模拟按需连接生命周期。另有 Python3.8 语法、RViz YAML 和 ZIP 校验。

公开仓库提供不依赖 ROS 的复用测试：

```bash
python3 -m unittest discover -s tests -v
```

这些是合成数据及模拟接口测试，不是本地直接运行 Gazebo 的证据。

## 9. 最后的速率与运动回归

依次测试，各窗口请求约 8 秒：

```bash
timeout -s INT 8s rostopic hz /kinect/rgb/image_raw
timeout -s INT 8s rostopic hz /kinect/depth/image_raw
timeout -s INT 8s rostopic hz --wall-time /lesson14/depth_points_preview
```

最后平均值分别为 **10.051 Hz、9.960 Hz、1.712 Hz**。前两者用 ROS 仿真时间，第三者显式墙钟；不能以二者之比宣称精确仿真倍率。预览符合最多 2 Hz，不保证精确 2 Hz。

保持 Gazebo、中继和轻量 RViz，要求先确认无其他 `/cmd_vel` 发布者、车前方至少约 0.5 m 空旷，再重用已有短时测试：

```bash
source "$HOME/catkin_ws/devel/setup.bash"
rostopic info /cmd_vel
# 只有确认没有竞争发布者、仿真未暂停且前方空旷后，才执行下一条。
python3 "$HOME/catkin_ws/src/rcdp/scripts/test_forward_step6.py"
```

用户对前进／停车、视觉联动、预览稳定三项反馈：**正常 同步 稳定**。没有新收集精确轨迹、停止时间或消息级同步数据。

停车命令保留：

```bash
rostopic pub -1 /cmd_vel geometry_msgs/Twist '{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}'
```

该差速插件没有本轮确认的命令超时停车机制；结束发布者不自动等于停车。脚本的正常结束／Ctrl+C 会尝试发零，但不是强杀、断电或网络故障的安全保障。

## 10. 问题与处理结论

| 问题 | 处理／证据 | 结论 |
| --- | --- | --- |
| 新旧课程包重名 | 隔离解压，保留当前 rcdp，分阶段增量 | 避免覆盖，不更换成功底盘 |
| 键盘包找不到 | 记录缺项，不盲目安装 | 未解决，留给后续依赖阶段 |
| TF 刚开始查不到 | 继续观察后续连续变换／图形状态 | 本次链路后来连通，不等于长期断树 |
| TF_REPEATED_DATA | 查发布者、clock、joint_states；短采样未复现，后来又出现 | 未根治，不能用无重复样本宣称修复 |
| 原始点云 RViz SIGBUS | 保留 Gazebo，检查数据／资源，软件渲染基线，再低负载预览 | 当前预览可用，原完整显示根因未明 |
| 大点云负载 | 80×60、最多 2 墙钟 Hz、单队列、按需订阅 | 减少中继输出／绘制负载，不改原始相机 |
| 速率解读混淆 | 明确 ROS 仿真时间 vs 墙钟 | 记录各自速率，不混为同一标准 |

更早的 Gazebo 端口占用与 APT DNS 失败详见历史操作日志。端口占用曾通过识别并停止当时旧仿真恢复；DNS／check_urdf 安装没有确认修好，不复制旧 PID、不 killall、不把重装当默认解法。

## 11. 学到的关键关系

1. URDF 外形、Gazebo 物理／插件、ROS 话题、TF、RViz 是不同层：看见模型不能代替数据和变换验收。
2. 同一模型、frame、时间基准和唯一控制责任比“多开几个 launch”重要。
3. Gazebo 真值 odom 不等于实物编码器估计；相机光学轴不等于外壳坐标轴。
4. 有数据、单帧数值有效、短时显示稳定、长期运行和物理精度是不同验收层级。
5. 窗口崩溃不必重启一切，先确认后端存活再隔离恢复；可用绕过不等于根因修复。
6. SLAM 前先稳住运动、scan、TF；导航时不能让 Gmapping 与 AMCL 同时竞争 map→odom。

## 12. 下一步仅作为待办

恢复实践后先检查 teleop、gmapping、map_server、amcl、move_base 等依赖；做当前工程新备份，再适配 rs_nav 到 `laser_scan_link`、当前模型和新地图。老师地图含旧机器绝对路径，参考图也不保证对应当前 world。先建图保存，再停 Gmapping 开 AMCL，最后 move_base；不把老师完整导航 launch 与现有 RSP 叠加。

**本次只归档，不执行这些待办。** 公开上传边界及缺失的课程 world 见 [PUBLIC_UPDATE_SCOPE.md](PUBLIC_UPDATE_SCOPE.md)。
