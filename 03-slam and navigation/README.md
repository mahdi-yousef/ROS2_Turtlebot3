# 03 - SLAM and Navigation

This folder covers the SLAM and Nav2 workflow, using the launch files I built in `my_robot_bringup`.

## Launch files

Location: `src/custom_packages/my_robot_bringup/launch/`

- **`custom_world_demo.launch.py`**: spawns TurtleBot3 in the warehouse world. This is the building block the other two include.
- **`slam_demo.launch.py`**: includes `custom_world_demo.launch.py`, then adds `turtlebot3_cartographer` for mapping. Uses a tuned Cartographer config at `config/warehouse_cartographer.lua`, since the stock config is built for a small demo room, not a warehouse.
- **`nav_demo.launch.py`**: includes `custom_world_demo.launch.py`, then adds `turtlebot3_navigation2` against a saved map, plus the `waypoint_follower` node (optional, toggle with `run_waypoint_follower:=false`).

I built them this way, one launch file including smaller ones, so the world spawn logic isn't duplicated across SLAM and navigation.

---

## Running SLAM

You need two terminals into the same container.

**Terminal 1:**
```bash
docker exec -it turtlebot3 bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger

ros2 launch my_robot_bringup slam_demo.launch.py
```
Gazebo and RViz should open, with the map building live in RViz as you drive.

**Terminal 2** (open a new WSL terminal, same command to enter the same running container):
```bash
docker exec -it turtlebot3 bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash

ros2 run turtlebot3_teleop teleop_keyboard
```
Drive slowly, especially through turns, and try to loop back to your start point so Cartographer gets a clean loop closure.

![SLAM session: Gazebo, RViz, and teleop terminal open together](screenshots/slam_session.png)

Once the map looks good, save it:
```bash
mkdir -p ~/turtlebot3_ws/src/custom_packages/my_robot_bringup/maps
ros2 run nav2_map_server map_saver_cli -f ~/turtlebot3_ws/src/custom_packages/my_robot_bringup/maps/warehouse_map
```

---

## Running Navigation

**Terminal 1:**
```bash
docker exec -it turtlebot3 bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash
export TURTLEBOT3_MODEL=burger

ros2 launch my_robot_bringup nav_demo.launch.py \
  map:=/root/turtlebot3_ws/src/custom_packages/my_robot_bringup/maps/warehouse_map.yaml
```

**Terminal 2**, if RViz didn't open on its own or you want a separate window:
```bash
docker exec -it turtlebot3 bash
source /opt/ros/humble/setup.bash
source ~/turtlebot3_ws/install/setup.bash

ros2 run rviz2 rviz2
```
In RViz, click "2D Pose Estimate" and click-drag on the robot's real position and heading. The waypoint follower waits for this before it starts sending goals.

![Navigation session: Gazebo, RViz, and terminal running Nav2](screenshots/nav_session.png)

---

## More on this project's own nodes

`waypoint_follower` and `obstacle_avoider` are covered in `04-custom_nodes`.
