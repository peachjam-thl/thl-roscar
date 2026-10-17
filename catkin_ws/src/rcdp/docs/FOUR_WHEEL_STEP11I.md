# Step11I — 四轮模型恢复激光雷达（本次只做文件预检）

## 上一步的实际验收

用户已在 Step11H 的当前四轮仿真中运行整棵 TF/关节只读检查，原日志：

```text
/home/thl/ros_course_logs/step11h_tf_audit_NkBzga/tf_audit.log
```

本次 40.047 秒墙钟窗口的结果：

- `status: WINDOW_OK`，窗口完整，`audit_exit=0 tee_exit=0`。
- `odom -> root_link` 动态 TF 3990 条，唯一来源 `/gazebo`。
- 六条活动关节 TF 各 1522 条，唯一来源 `/lesson14_4wd_robot_state_publisher`。
- 以上七条动态边的重复、同源/跨源重复、倒退、同时间戳载荷变化、零时间戳计数全部为零。
- 三条固定 TF 各收到一条，均来自同一个 robot_state_publisher，固定姿态未变化。
- `/joint_states` 1995 条，来源仅 `/gazebo`；六个关节各 1995 个有效样本，时间戳异常为空。
- `/odom` 3990 条，`/clock` 39911 条，来源均仅 `/gazebo`，异常计数为零。
- 无非法消息、额外边、异常例子或 issues。
- 模拟时间推进 39.914 秒，最大观测 clock 接收间隙 0.007611 秒。

这是**不移动、不加载实时雷达/相机时的一次观测窗口**。没有把它扩大为运动中、加传感器后或任意时长的保证。root 与关节 TF 消息数量不同并不自动意味着丢包；两个来源的发布与节流配置不同。

## 本步变化：只加回一台激光雷达

新的顶层 Xacro 包含：

```text
myrobot_4wd_laser_step11i.xacro
  -> myrobot_4wd_tf_step11h.xacro
     -> 原四轮 drive/base 与六关节状态发布
  -> gazebo_sensor/lesson14_laser_step7.xacro
     -> 原先两轮实验已经验证过的雷达传感器定义（不是两轮整车）
```

保留 10 links、9 joints、6 moving joints。驱动、质量/惯量、轮距/轮径、扭矩、摩擦、B/cone 世界、出生姿态、RSP 名称与参数均不改。不添加摄像头、光学帧、点云、RViz、额外控制器或 fake joint_state_publisher。

雷达复用旧传感器参数：`ray`，frame `laser_scan_link`，topic `/scan`，360 个采样，角度 -3 到 +3 rad（约 343.8 度，**不是整整 360 度**），距离 0.1–30 m，配置 5.5 Hz 模拟时间，噪声标准差 0.01 m。本步尚未证明四轮运行中的实际雷达频率、有效距离或传感器负载下 TF 稳定。

ZIP 只包含本步新增的 Xacro、launch、只读预检脚本和说明；已有 step7 传感器文件、step11A/C/H/F 及编译好的四轮驱动必须存在。原文件全部保留。新 launch 不会热更新当前已生成的 Gazebo 模型。

## 现在执行：导入和预检，保持当前 Step11H 运行

把 ZIP 复制到 Ubuntu `/home/thl/Lesson14_4wd_laser_step11i.zip`。在新终端逐条执行，任一报错就停下反馈，不继续：

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_4wd_laser_step11i.zip -d /home/thl/catkin_ws/src/rcdp

rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_4wd_tf_step11h.xacro -o /tmp/lesson14_step11i_baseline.urdf

rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_4wd_laser_step11i.xacro -o /tmp/lesson14_4wd_laser_step11i.urdf

python3 /home/thl/catkin_ws/src/rcdp/scripts/check_4wd_laser_step11i.py /tmp/lesson14_step11i_baseline.urdf /tmp/lesson14_4wd_laser_step11i.urdf
```

预期末尾 `PRECHECK_OK`。脚本只读文件及 `ldd` 激光库，不连接 ROS，不发送速度，不改参数，不关闭/启动 Gazebo；核对原关键文件 SHA256、原雷达配置、仅加一个 sensor/plugin、launch 的其他内容不变。

预检退出 2（PRECHECK_REVIEW）说明驱动库哈希不同；退出 1 表示文件、配置或依赖问题。都应先反馈，不直接启动。`catkin_make` 不需要为本次纯配置文件重复执行。

## 预检通过后的后续步骤（尚未执行）

后续再正常关闭当前 H launch，等旧服务器与端口完全退出，启动新 I launch（默认 cone_model）。仍不启动旧两轮 launch 或另一个 Gazebo。场景重启会回到出生位姿。

运行期依次验证 `/scan` 的发布来源、消息类型、header/frame、360 个样本、角度/距离元数据、有限有效距离和实测频率；检查到 `laser_scan_link` 的 TF；再运行上一步整棵 TF 诊断，确认雷达负载下没有新时间戳异常。

完成后才恢复轻量 RViz；再之后才恢复深度相机及降采样点云。不要直接启动旧相机顶层模型，也不要重新启用曾使 RViz 崩溃的满分辨率点云。

## 验证边界与回退

主机验证范围是 Xacro 展开、结构/配置差异、负例、已知基线哈希及 ZIP 完整性；未在主机运行 ROS/Gazebo，也未声称新雷达已原生加载。VM 预检仅进一步验证文件与库依赖，运行期仍待用户操作。

旧 H launch 保留；将来需要回退时先正常关闭 I，再重新启动 H。GitHub 上传保持暂停，没有提交或推送。
