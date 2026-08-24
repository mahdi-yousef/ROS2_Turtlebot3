# 02 — TurtleBot3 Nodes

Before any custom code is introduced, this covers what ships in the base
image out of the box — from `docker/Dockerfile`, this container installs
`turtlebot3`, `turtlebot3-msgs`, `turtlebot3-cartographer`,
`turtlebot3-navigation2`, `nav2-bringup`, `nav2-route`, plus hardware driver
packages (`dynamixel-sdk`, `hls-lfcd-lds-driver`, `ld08-driver`,
`camera-ros`), and clones/builds `ROBOTIS-GIT/turtlebot3` itself at
image-build time.

That last repo (`turtlebot3`) is a meta-repo bundling several packages
together — this page walks through what each one actually contains, since
`ls install/` alone doesn't tell you that.

## Discovering packages and nodes yourself

Two commands cover almost everything:
```bash
ros2 pkg list | grep turtlebot3        # every turtlebot3-related package installed
ros2 pkg executables <package_name>    # every ros2 run-able node in a given package
```
Everything below was found this way — worth running yourself rather than
taking this page as the only source of truth, since packages get added
between ROBOTIS releases.

---

## `turtlebot3_description`

URDF/xacro robot model — links, joints, sensor frames. No runnable nodes;
`robot_state_publisher` (a generic ROS2 package, not TurtleBot3-specific)
reads this to publish TF. Worth a look directly:
```bash
find $(ros2 pkg prefix turtlebot3_description)/share/turtlebot3_description/urdf -name "*.xacro"
```

## `turtlebot3_node`

The low-level driver that talks to the real robot's microcontroller over
serial (motor commands, IMU, battery status). **Not used in this project**
— Gazebo simulates all of this instead, so this package is only relevant
if/when deploying to real hardware (see the note in `01-introduction` about
transitioning from simulation to a physical robot).

## `turtlebot3_bringup`

Launch files for bringing up the **real** robot (starts `turtlebot3_node`,
LiDAR driver, etc.). Also not used here for the same reason — this
project's equivalent "bringup" is `custom_world_demo.launch.py` in
`my_robot_bringup`, which spawns the robot in Gazebo instead of talking to
real hardware.

## `turtlebot3_teleop`

Manual keyboard control. One node:
```bash
ros2 pkg executables turtlebot3_teleop
# -> turtlebot3_teleop teleop_keyboard
```
Run it (needs the simulation already running in another terminal):
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```
It publishes `geometry_msgs/msg/Twist` messages to `/cmd_vel` based on
keypresses — nothing more complex than that. Confirm it's working by
watching the topic directly instead of trusting the robot's motion alone:
```bash
ros2 topic echo /cmd_vel
```

## `turtlebot3_cartographer`

SLAM (mapping). One launch file that matters:
```bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=true
```
Full usage — driving to build a map, saving it, and the tuned config used
for the warehouse environment in this project — is covered in
[`03-slam and navigation`](../03-slam%20and%20navigation/).

## `turtlebot3_navigation2`

Autonomous navigation (Nav2) against a previously-saved map:
```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=<path-to-map.yaml>
```
Also covered fully in `03-slam and navigation` — including a real issue
hit integrating this into a custom launch file (an internal
`params_file` default that only resolves correctly when this launch file
is run standalone, not nested inside another one) and its fix.

## `turtlebot3_example`

A grab-bag of small demo nodes ROBOTIS ships for learning purposes — worth
exploring directly rather than listing exhaustively here, since exact
contents vary by release:
```bash
ros2 pkg executables turtlebot3_example
```
These are a good reference for node structure/style before writing your
own — see `04-custom_nodes` for this project's actual custom nodes
(`obstacle_avoider`, `waypoint_follower`), which follow a similar shape but
are written from scratch for this project rather than reused from here.

## `turtlebot3_msgs`

Custom message/service definitions used by the other packages (e.g. sensor
state messages specific to TurtleBot3 hardware). Inspect any of them with:
```bash
ros2 interface list | grep turtlebot3
ros2 interface show turtlebot3_msgs/msg/<MessageName>
```

---

## Quick sanity check across all of the above

With the simulation running (see `01-introduction`, step 8), this should
show every node from whichever of the packages above is currently running:
```bash
ros2 node list
```
And this shows the full live communication graph — useful for visually
confirming, e.g., that `teleop_keyboard`'s `/cmd_vel` output is actually
reaching the simulated robot:
```bash
ros2 run rqt_graph rqt_graph
```
