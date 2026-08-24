# 01 — Introduction & Environment Setup

Prerequisites, Docker setup, and a clean build for reproducing this
project's environment.

## What this project is

A simulated TurtleBot3 Burger operating in a custom warehouse environment —
reactive obstacle avoidance, SLAM mapping, and autonomous Nav2 waypoint
navigation — built on ROS2 Humble and Gazebo Classic, in a Docker container
on WSL2.

## Stack

| Component | Choice |
|---|---|
| OS | Windows 10/11 + WSL2 (Ubuntu) |
| ROS2 distro | Humble |
| Simulator | Gazebo Classic (`gazebo-ros-pkgs`) |
| Robot | TurtleBot3 Burger (simulated) |
| Container | built from `docker/Dockerfile` (ROBOTIS's official Humble image) |
| Custom world | `warehouse_world.sdf`|

---

## Prerequisites

1. **WSL2** with an Ubuntu distro installed:
   ```powershell
   wsl --install
   ```

2. **Docker**, working inside WSL2 — Docker Desktop with WSL integration enabled, or Docker Engine installed directly inside WSL.

3.  Then in PowerShell:
   ```powershell
   wsl --shutdown
   ```
   Wait ~10 seconds before reopening WSL.

   > If GUI windows later show only a taskbar entry with no content
   > (sometimes titled `[WARN:COPY MODE]`) when opening Gazebo/RViz — known
   > WSLg rendering bug, unrelated to ROS2:
   > ```powershell
   > wsl --update
   > wsl --shutdown
   > ```
   > If it persists, run this once on the WSL host (not in the container):
   > ```bash
   > sudo mount -t tmpfs tmpfs /mnt/shared_memory
   > ```

---

## 1. Clone this repository

```bash
cd ~
git clone git@github.com:mahdi-yousef/ROS2_Turtlebot3.git
cd ROS2_Turtlebot3
```

## 2. Build the base image

`docker/Dockerfile` is ROBOTIS's official TurtleBot3 Humble Dockerfile
(source: [`github.com/ROBOTIS-GIT/turtlebot3/tree/humble/docker/humble`](https://github.com/ROBOTIS-GIT/turtlebot3/tree/humble/docker/humble)),
included in this repo unmodified. It clones and builds the `turtlebot3`
package itself at build time — no separate clone of that repo is needed.

Build the image:
```bash
cd docker
docker build -t robotis/turtlebot3:humble-latest .
```

This installs ROS2 Humble desktop, Cartographer, Nav2, and hardware driver
packages, and takes several minutes. It does **not** include any Gazebo or
simulation packages — those are added in step 6.

## 3. Set up persistent storage

The container only keeps what's explicitly bind-mounted from the host —
anything built only *inside* the container is lost if the container is
destroyed (`docker compose down`).

```bash
mkdir -p ~/tb3_extra/turtlebot3_simulations
```

> If this fails with "Permission denied" (Docker may have auto-created the
> parent folder as root on an earlier run):
> ```bash
> sudo chown -R $USER:$USER ~/tb3_extra
> mkdir -p ~/tb3_extra/turtlebot3_simulations
> ```

## 4. docker-compose.yml

You can see in `docker/` the following yaml file:
```yaml
services:
  turtlebot3:
    container_name: turtlebot3
    image: robotis/turtlebot3:humble-latest
    tty: true
    restart: unless-stopped
    cap_add:
      - SYS_NICE
    ulimits:
      rtprio: 99
      rttime: -1
      memlock: 8428281856
    network_mode: host
    ipc: host
    pid: host
    environment:
     - DISPLAY=${DISPLAY}
     - QT_X11_NO_MITSHM=1
    volumes:
      - /dev:/dev
      - /dev/shm:/dev/shm
      - /run/udev:/run/udev
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      - /tmp/.docker.xauth:/tmp/.docker.xauth:rw
      - ~/tb3_extra/turtlebot3_simulations:/root/turtlebot3_ws/src/turtlebot3_simulations
      - ../src/custom_packages:/root/turtlebot3_ws/src/custom_packages
    privileged: true
    command: bash
```

Two mounts matter:
- `~/tb3_extra/turtlebot3_simulations` (host, outside the repo) →
  `turtlebot3_simulations`, ROBOTIS's Gazebo simulation packages, added in
  step 6.
- `../src/custom_packages` (this repo's own `src/custom_packages/`, sibling
  to `docker/`) → my project's own packages created by me using turtle nest (`my_robot_control`,
  `my_robot_bringup`). No separate setup needed for this one — it's part of
  the repo and mounts automatically on clone.

Start the container then open a terminal in it as follows:
```bash
docker compose up -d
docker exec -it turtlebot3 bash
```

> In WSL use `docker stop turtlebot3` to stop the container. Avoid using `docker compose down` so you don't destroy the container and lose built progress.

## 5. Confirm the environment

```bash
export TURTLEBOT3_MODEL=burger
echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
echo $ROS_DISTRO
```
Should print `humble`.

## 6. Add Gazebo simulation support

```bash
cd ~/turtlebot3_ws/src
git clone -b humble https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git turtlebot3_simulations
```

```bash
colcon list | grep turtlebot3_gazebo
```
> Should print exactly one line. Two means a folder got cloned inside
> another already-mounted directory tree by mistake — move the persistent
> folder outside any other mounted path and re-clone.

## 7. Install dependencies and build

```bash
apt-get update
```
> Always run this before `rosdep install` in this container — its apt
> package index is stale/cleared by default, causing misleading
> `E: Unable to locate package ros-humble-<pkg>` errors for packages that
> genuinely exist, including `gazebo-ros-pkgs`. Skipping this surfaces
> later as `CMake Error ... Could not find a package configuration file
> provided by "gazebo"` during the build below.

```bash
cd ~/turtlebot3_ws
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

```bash
MAKEFLAGS="-j2" colcon build --symlink-install --parallel-workers 1
source install/setup.bash
```
> `c++: fatal error: Killed signal terminated program cc1plus` — the Linux
> OOM killer; WSL2 ran out of memory mid-compile. Confirm the `.wslconfig`
> fix from Prerequisites is applied (`wsl --shutdown` fully restarts WSL),
> and keep `--parallel-workers 1`/`MAKEFLAGS="-j2"` even with more memory
> allocated.
>
> `1 package failed: turtlebot3_simulations` with everything else
> succeeding — it's an empty metapackage referencing
> `turtlebot3_manipulation_gazebo` (arm variant, not built here). Safe to
> ignore.
>
> `my_robot_bringup` fails with `Check that the following packages have
> been built: - my_robot_control` — dependency ordering; this one-shot
> full build already handles it correctly. If rebuilding a single package
> later, use `colcon build --packages-up-to my_robot_bringup` instead of
> `--packages-select`.

## 8. Verify

```bash
ros2 launch my_robot_bringup custom_world_demo.launch.py \
  world:=/root/turtlebot3_ws/src/custom_packages/my_robot_bringup/worlds/warehouse_world.sdf
```
> Robot not visible in Gazebo — confirm `echo $TURTLEBOT3_MODEL`, then
> check Gazebo's Models panel and right-click the robot entry → Follow.
>
> `gzserver` dies immediately with `Entity [burger] already exists`, exit
> code 255 — an orphaned process from a previous crashed/interrupted
> launch:
> ```bash
> pkill -9 gzserver gzclient
> ```
> If that doesn't resolve it, `docker restart turtlebot3` and relaunch.

Gazebo should open (via WSLg, no extra X server setup needed) showing the
warehouse with TurtleBot3 spawned inside it. See folders `02` through `04`
for the rest of the project once this is confirmed working.

---

## World & Model Sources

`warehouse_world.sdf` (in `src/custom_packages/my_robot_bringup/worlds/`)
was downloaded from: **[fill in the exact source URL/site you downloaded it
from here]**. It contains no external model references (self-contained
world file, no separate `models/` folder needed).

> Before publishing: confirm the original source's license permits
> redistribution, and credit it here explicitly. If unclear or restrictive,
> link to the source instead of committing the file directly, and add a
> download step here in its place.

---

## Repository Layout Reference

```
this-repo/
├── 01-introduction/          (this folder)
├── 02-existing-nodes/
├── 03-slam-and-navigation/
├── 04-custom-nodes/
├── docker/
│   ├── Dockerfile              # ROBOTIS's official Dockerfile (unmodified)
│   ├── docker-compose.yml
│   └── docker-compose.checkpoint.yml
└── src/
    └── custom_packages/
        ├── my_robot_control/
        └── my_robot_bringup/
```
