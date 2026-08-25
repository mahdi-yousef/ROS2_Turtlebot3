# 02 - TurtleBot3 Nodes

What ships in the base image out of the box, before any custom code is
introduced from `docker/Dockerfile`, this container installs `turtlebot3`,
`turtlebot3-cartographer`, `turtlebot3-navigation2`, `nav2-bringup`, plus
hardware driver packages, and clones/builds `ROBOTIS-GIT/turtlebot3` itself
at image-build time.

## Discovering packages and nodes yourself

```bash
ros2 pkg list | grep turtlebot3        # every turtlebot3-related package installed
ros2 pkg executables <package_name>    # every ros2 run-able node in a given package
```

## Summary

| Package | Contains | Used in this project's simulation? |
|---|---|---|
| `turtlebot3_teleop` | `teleop_keyboard` node | **Yes** |
| `turtlebot3_cartographer` | SLAM launch file | **Yes** |
| `turtlebot3_navigation2` | Nav2 launch file | **Yes** |
| `turtlebot3_example` | Demo nodes | **Yes** |
| `turtlebot3_description` | URDF/robot model | Used indirectly (Gazebo spawns from it), not something run directly |
| `turtlebot3_node` | Low-level hardware driver | No real hardware only |
| `turtlebot3_bringup` | Real hardware bringup launch files | No real hardware only |

---

## Used in simulation
Before running and trying differenet nodes, first make sure to open the container from the image downloaded in section 01 as follows:
```bash
cd ~/ROS2_Turtlebot3/docker
docker compose up -d                 #run the container
docker exec -it turtlebot3 bash      #open a new terminal in the container
```
### `turtlebot3_teleop`

Manual keyboard control. One node:
```bash
ros2 pkg executables turtlebot3_teleop
# -> turtlebot3_teleop teleop_keyboard
```
Run the simulation as described in section [`01-8`](../01-introduction/) then open new WSL terminal and open a new terminal in the container using `docker exec -it turtlebot3 bash`:
```bash
ros2 run turtlebot3_teleop teleop_keyboard
```
Now try moving the robot using the keyboard (make sure to click on the teleop terminal before)

It publishes `geometry_msgs/msg/Twist` to `/cmd_vel` based on keypresses.
Confirm it's working by watching the topic directly in a new terminal:
```bash
ros2 topic echo /cmd_vel
```

### `turtlebot3_cartographer`

SLAM (mapping):
```bash
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=true
```
driving to build a map, saving it, and the tuned config used
for the warehouse environment is covered in
[`03-slam and navigation`](../03-slam%20and%20navigation/).

### `turtlebot3_navigation2`

Autonomous navigation (Nav2) against a previously-saved map:
```bash
ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=<path-to-map.yaml>
```
Also covered fully in `03-slam and navigation`, including a real issue hit
integrating this into a custom launch file and its fix.

### `turtlebot3_example`

Small demo nodes ROBOTIS ships for learning purposes:
```bash
ros2 pkg executables turtlebot3_example
```
A useful reference for node structure/style, see `04-custom_nodes` for
this project's own custom nodes (`obstacle_avoider`, `waypoint_follower`),
written from scratch in a similar shape.

---

## Not used in simulation (real hardware only)

- **`turtlebot3_node`** — the low-level driver that talks to the real
  robot's microcontroller over serial (motor commands, IMU, battery
  status). Gazebo simulates all of this instead.
- **`turtlebot3_bringup`** — launch files for bringing up the real robot
  (starts `turtlebot3_node`, LiDAR driver, etc.). This project's
  equivalent is `custom_world_demo.launch.py` in `my_robot_bringup`, which
  spawns the robot in Gazebo instead.

---

## Quick sanity check

With the simulation running (see `01-introduction`, step 8):
```bash
ros2 node list
ros2 run rqt_graph rqt_graph
```
