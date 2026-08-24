
# ROS2 TurtleBot3 — Warehouse Simulation Project

A simulated TurtleBot3 Burger operating in a custom warehouse environment —
reactive obstacle avoidance, SLAM mapping, and autonomous Nav2 waypoint
navigation — built on ROS2 Humble and Gazebo Classic, in Docker on WSL2.

## Contents

| Folder | Covers |
|---|---|
| [`01-introduction`](01-introduction/) | Environment, Docker/WSL2 setup, world source, prerequisites |
| `02-turtlebot3_nodes` | TurtleBot3's built-in teleop, Cartographer, Nav2 |
| `03-slam and navigation` | This project's SLAM/Nav2 launch files, saving/using maps|
| `04-custom_nodes` | `obstacle_avoider` and `waypoint_follower`, explained and usable|

## Quick start

See [`01-introduction/README.md`](01-introduction/README.md) for full setup
instructions.
## Repository Layout

```
ROS2_Turtlebot3/
├── 01-introduction/
├── 02-turtlebot3_nodes/
├── 03-slam and navigation/
├── 04-custom_nodes/
├── docker/
│   ├── Dockerfile              # ROBOTIS's official Dockerfile (unmodified)
│   └── docker-compose.yml
└── src/
    └── custom_packages/
        ├── my_robot_control/    # obstacle_avoider, waypoint_follower
        └── my_robot_bringup/    # launch files, config, worlds, maps
```

## Stack

| Component | Choice |
|---|---|
| OS | Windows 10/11 + WSL2 (Ubuntu) |
| ROS2 distro | Humble |
| Simulator | Gazebo Classic |
| Robot | TurtleBot3 Burger (simulated) |
| Container | `robotis/turtlebot3:humble-latest`, via Docker Compose |
