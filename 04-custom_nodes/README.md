# 04 - Custom Nodes

The two nodes I wrote for this project, both in `src/custom_packages/my_robot_control/my_robot_control/`.

## obstacle_avoider

Reactive, LiDAR-based obstacle avoidance. Looks at a forward cone of the `/scan` topic, drives forward if nothing's within `stop_distance`, otherwise stops and turns toward whichever side has more open space.

Configured via a parameter YAML rather than hardcoded values. Default parameter file `obstacle_avoider_params.yaml` values:

| Parameter | Default | Meaning |
|---|---|---|
| `stop_distance` | 0.45 m | Start turning when something is closer than this |
| `forward_speed` | 0.15 m/s | Straight-line driving speed |
| `turn_speed` | 0.6 rad/s | Turning speed when avoiding |
| `forward_cone_deg` | 40.0° | +/- degrees around straight-ahead counted as "front" |

**The node should be initiated while gazebo is launched and the turtlebot is spawned inside a world, then a launch file `avoid_demo.launch.py` is created for this purpose. Run it:**
```bash
ros2 launch my_robot_bringup avoid_demo.launch.py
```
The default arguments are:

- `world:=/root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/worlds/warehouse_world.sdf`
- `x_pose:=0.0`
- `y_pose:=0.0`
- `params_file:=/root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/config/obstacle_avoider_params.yaml`

Gazebo opens with the robot driving itself around the warehouse, stopping and turning away from shelves and walls.

![obstacle_avoider driving around the warehouse](screenshots/obstacle_avoider.png)

**Override the tuning**, either edit `config/obstacle_avoider_params.yaml` directly, or point at a different YAML entirely:
```bash
ros2 launch my_robot_bringup avoid_demo.launch.py \
  params_file:=/path/to/your_own_params.yaml
```
or override a single value on the command line:
```bash
ros2 launch my_robot_bringup avoid_demo.launch.py --ros-args -p stop_distance:=0.6
```
Finally, you can specify your arguments to any world and parameter file as follows:
```bash
ros2 launch my_robot_bringup avoid_demo.launch.py \
  world:=/root/turtlebot3_ws/src/turtlebot3_simulations/turtlebot3_gazebo/worlds/turtlebot3_world.world \
  params_file:=/root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/config/custom_avoid_param.yaml \
  x_pose:=-2.0 \
  y_pose:=-0.5
```
![obstacle_avoider driving around the warehouse](screenshots/obstacle_avoider2.png)

---

## waypoint_follower

Sends a sequence of `(x, y, yaw)` goals to Nav2's `NavigateToPose` action, one at a time, waiting for each to finish before sending the next. Waits for AMCL to publish a localized pose before sending anything, so it's safe to start even before you've given a 2D Pose Estimate, it just sits and waits.

Waypoints come from `config/waypoints.yaml`, same YAML-parameter pattern as `obstacle_avoider`.

**Getting real `(x, y)` values off the map**, instead of eyeballing coordinates, use RViz's **Publish Point** tool:

1. With `nav_demo.launch.py` running and the map loaded in RViz, click the **Publish Point** button in the RViz toolbar.
2. Click anywhere on the map at the location you want as a waypoint. Each click publishes a `geometry_msgs/PointStamped` to the `/clicked_point` topic.
3. In a spare terminal, echo that topic to read off the coordinates as you click:
   ```bash
   ros2 topic echo /clicked_point
   ```
4. Copy the `x` and `y` values from the echoed output into `config/waypoints.yaml` for that waypoint. Repeat per point, picking your own `yaw` for each (the tool only gives you position, not heading).

### Yaw tolerance

Since `/clicked_point` doesn't carry a heading, hitting the exact yaw for every waypoint isn't realistic. Rather than fighting that, `yaw_goal_tolerance` in `nav2_params_override.yaml` is set to `2π` (`6.28`). With the tolerance that wide, Nav2's goal check accepts any final heading, so the yaw value in a waypoint stops mattering, the robot just needs to reach the `(x, y)` and it counts as arrived. One config value instead of changing how `waypoint_follower.py` builds or checks goals.

**Note:** this override currently lives in the *install* copy:
```
/root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/config/nav2_params_override.yaml
```
not in `src/`. That's intentional, not an oversight: `nav2_params_override.yaml` in `src/` is the generic Nav2 config used by other navigation setups in this workspace, where a real `yaw_goal_tolerance` still matters, so it can't be loosened there. The tradeoff is that **any `colcon build` will overwrite the install copy from `src/` and silently undo this**, `yaw_goal_tolerance` will go back to its normal value and yaw will matter again for waypoint missions. After any rebuild, re-apply the `2π` edit to the install file before running `waypoint_follower`.

**`nav_demo.launch.py` no longer starts this automatically** (removed to keep Nav2 usable on its own while tuning localization, without a mission firing off goals in the background). Run it yourself in a second terminal instead:

**Terminal 1:**
```bash
ros2 launch my_robot_bringup nav_demo.launch.py
```
Give a 2D Pose Estimate in RViz once it's up.

**Terminal 2:**
```bash
ros2 run my_robot_control waypoint_follower --ros-args \
  --params-file /root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/config/waypoints.yaml
```

Watch the terminal, it logs one line per waypoint sent and one per result:
```
[waypoint_follower]: waypoint_follower waiting for AMCL localization (give a "2D Pose Estimate" in RViz)...
[waypoint_follower]: AMCL pose received -- starting waypoint mission.
[waypoint_follower]: Sending waypoint 1/3: x=1.00, y=0.00, yaw=0.00
[waypoint_follower]: Waypoint 1 reached.
```

![waypoint_follower driving the robot through a saved mission](screenshots/waypoint_follower.png)

---

## Both together

Nothing stops you running `obstacle_avoider` for casual driving and `waypoint_follower` for scripted missions in the same session, just not at the same time, both publish to `/cmd_vel` and would fight each other.
