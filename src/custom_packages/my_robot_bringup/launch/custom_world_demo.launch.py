"""
custom_world_demo.launch.py

Same structure as ROBOTIS's turtlebot3_world.launch.py (gzserver + gzclient +
robot_state_publisher + spawn_turtlebot3), but the world file is a launch
argument instead of hardcoded -- point it at any .world file you've placed
in this package's worlds/ folder (or anywhere else on disk).

Usage:

ros2 launch my_robot_bringup custom_world_demo.launch.py
  #default arguments
    #world:=/root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/worlds/warehouse_world.sdf
    #x_pose:=0.0   
    #y_pose:=0.0

# Specify everything example:
ros2 launch my_robot_bringup custom_world_demo.launch.py \
    world:=/root/turtlebot3_ws/src/turtlebot3_simulations/turtlebot3_gazebo/worlds/turtlebot3_world.world \
    x_pose:=-2.0 \
    y_pose:=-0.5


"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    tb3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    bringup_dir = get_package_share_directory('my_robot_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')

    # Default: a world file living inside this package's own worlds/ folder.
    # Drop any downloaded .world file there (and its models/ folder alongside
    # it, or on GAZEBO_MODEL_PATH) and this will pick it up with no edits.
    default_world = os.path.join(bringup_dir, 'worlds', 'warehouse_world.sdf')
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Full path to the .world file to load',
    )
    world = LaunchConfiguration('world')

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items(),
    )

    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # World-agnostic -- reused unmodified from turtlebot3_gazebo, exactly as
    # in the official launch file you attached.
    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo_dir, 'launch', 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    spawn_turtlebot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_gazebo_dir, 'launch', 'spawn_turtlebot3.launch.py')
        ),
        launch_arguments={'x_pose': x_pose, 'y_pose': y_pose}.items(),
    )

    return LaunchDescription([
        world_arg,
        gzserver_cmd,
        gzclient_cmd,
        robot_state_publisher_cmd,
        spawn_turtlebot_cmd,
    ])
