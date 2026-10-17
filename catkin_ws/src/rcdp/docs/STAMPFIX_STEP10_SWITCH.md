# Step10：独立切换文件——先预检，不启动

> 此文保留交付时的分阶段步骤。用户随后已完成预检、切换、实际新库加载及两轮约40秒诊断；
> 最新记录见 [修复验收](../../../../docs/TIMESTAMP_FIX_STEP10.md)。以下“本轮不要执行／尚未切换”等
> 指最初交付阶段，不应当作当前状态。原交付 ZIP 保持原字节；源码目录说明加了此更新。

固定现场：`/home/thl/catkin_ws`、`rcdp`、模型 `lesson13_robot`、ROS1 Noetic、Gazebo11。
这是已编译的 `rcdp_stampfix` 插件的模型／launch 增量包，不是替换整个课程包。
ZIP 条目统一使用 2020-01-01 固定时间，避免导入时再次出现未来文件时间；
这是打包元数据，不代表文件原始创建时间。

## 证据边界

- 用户上一份完整编译日志已经显示新 `.so` 链接成功、目标构建成功。
- 导入源码存在“文件修改时间在未来”警告，已建议只用 touch 规范新包文件时间，再构建。
  后续未收到完整重编译输出，不能假定该警告已经复核消失。
- 最新 `ldd` 附件是后半段，其中所有显示的库均已解析；没有完整前半段，
  不能仅据此宣布全部依赖通过。下方脚本对指定新库重新执行完整 `ldd`，仅输出检查摘要。
- 本机 Windows 的 Xacro/XML 离线比较与测试不等于 VM 实际加载成功。
- 当前运行的仿真尚未切换插件；不宣称 TF_REPEATED_DATA 已消失。

## 新文件与改动

1. `urdf/gazebo/myrobot_drive_stampfix_step10.xacro`：保留 step6 全部参数和物理模型引用，
   仅把差速插件 filename 改为 `/home/thl/catkin_ws/devel/lib/librcdp_diff_drive_stampfix.so`。
2. `urdf/gazebo/myrobot_stampfix_step10.xacro`：组合新驱动、原 step7 激光、原 step8 四个辅助关节、
   原 step9 相机。展开后的整个 robot XML 除驱动库 filename 外必须与原 step9 一致。
3. `launch/myrobot_stampfix_step10.launch`：同一个原 world、同名模型、同一 RSP 配置。
   `start_rviz` 默认 false；如日后主动开启，则用原 step9a 轻量配置和软件渲染。
4. `scripts/check_stampfix_switch_step10.py`：只读取两份展开 URDF 和新库，运行 ldd 并校验。
   不连接 ROS、不写参数、不发速度／TF、不生成或启动仿真。
5. 本文档。没有覆盖任何 step4–9a 原文件，不含导航、键盘或运动节点。

使用绝对插件路径是针对当前现场路径的明确选择，避免依赖插件搜索路径是否包含 devel/lib。
迁移工作空间时需要重新核对路径；不要把此包当成适用于任意目录的一键部署。
加载路径机制可参看 [Gazebo11 Plugin.hh](https://github.com/gazebosim/gazebo-classic/blob/gazebo11/gazebo/common/Plugin.hh)。

## 当前只做导入和预检

把 `Lesson14_stampfix_switch_step10.zip` 放到 VM `/home/thl/`。
保持原仿真、RViz 运行，另开终端输入：

```bash
source /home/thl/catkin_ws/devel/setup.bash
unzip -n /home/thl/Lesson14_stampfix_switch_step10.zip -d /home/thl/catkin_ws/src/rcdp
```

这次 ZIP 是 rcdp 内的增量文件，所以解压目标是 `src/rcdp`；
上一次独立插件包的目标是 `src`。不要混淆。

分别展开旧模型和新模型，只写 `/tmp/` 文件，不改变运行中的 robot_description：

```bash
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_camera_step9.xacro -o /tmp/lesson14_step10_baseline.urdf
rosrun xacro xacro /home/thl/catkin_ws/src/rcdp/urdf/gazebo/myrobot_stampfix_step10.xacro -o /tmp/lesson14_stampfix_step10.urdf
```

若任一命令报错，停止并回传，不继续使用旧的 /tmp 文件做验收。
两条均正常退出后运行：

```bash
python3 /home/thl/catkin_ws/src/rcdp/scripts/check_stampfix_switch_step10.py /tmp/lesson14_step10_baseline.urdf /tmp/lesson14_stampfix_step10.urdf
```

必须看到 `urdf_equal_except_drive_library: true`、`dynamic_dependencies_resolved: true`、
11 links、10 joints、6 moving joints、4 plugins、1 diff-drive plugin、100 Hz，
以及结尾 `PRECHECK_OK`。回传这份短输出后再继续。

不需要为这些 XML／Python 文件重新 catkin_make；新插件二进制须已在上一阶段编译生成。
预检不会确认 gazebo 当前加载哪个库，也不验证 TF 时间戳。

## 后续切换／验收计划（本轮不要执行）

1. 现场检查 `/cmd_vel` 的发布者，停止其他运动命令源，显式发零并观察停车。
2. 在各自终端正常停止旧 RViz、轻量预览中继、旧 launch。保留文件，不 killall。
3. 当前检查 Gazebo 进程和 11345 端口，若仍有旧 server，先辨明原因，不叠加新 launch。
4. 只启动 `myrobot_stampfix_step10.launch`；默认不启动 RViz。
5. 从当前实际 gzserver 进程的 `/proc/<PID>/maps` 核实新库已加载；不能只看参数文件或构建成功。
6. 重新运行 40 秒 TF／odom／clock 原始诊断，不跨 reset／重启边界，保存完整结果。
7. 再按原方案恢复一个中继、一个软件渲染 RViz，验收扫描／RGB-D／轻量点云和受控停车。

本阶段不修改 `/clock`、不降低 100Hz、不添加第二个 odom TF、不屏蔽 TF 警告、不动 `/opt/ros`。
短窗口重复为零只能证明该窗口未观察到重复，不能自动表述为永久根治。

## 回退

仅导入／展开／预检时不需回退，旧仿真仍在运行。
未来切换若失败，正常停止新 launch，在确认旧 server 已退出后，用保留的
`myrobot_camera_step9.launch start_rviz:=false` 恢复，再分别恢复原中继与软件 RViz。
