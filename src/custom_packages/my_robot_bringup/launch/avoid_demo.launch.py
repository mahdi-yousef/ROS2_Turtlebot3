"""
avoid_demo.launch.py

Launches TurtleBot3 in the selected Gazebo world via
custom_world_demo.launch.py, then starts obstacle_avoider, configured from
a ROS2 parameter YAML file rather than individual command-line overrides.

The node's own declared defaults (stop_distance=0.45, forward_speed=0.15,
turn_speed=0.6, forward_cone_deg=40.0) match config/obstacle_avoider_params.yaml
exactly, so both stay in sync with no extra effort: the YAML is what actually
gets loaded at runtime, the in-code declare_parameter() defaults are only a
fallback if the node is ever run without any parameter file at all (e.g.
`ros2 run my_robot_control obstacle_avoider` directly).

Usage:
    # Use all defaults:
    ros2 launch my_robot_bringup avoid_demo.launch.py
        #default arguments
        #world:=/root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/worlds/warehouse_world.sdf
        #x_pose:=0.0
        #y_pose:=0.0
        #params_file:=/root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/config/obstacle_avoider_params.yaml

    # Override with your own tuned YAML instead of editing the shipped one:
    ros2 launch my_robot_bringup avoid_demo.launch.py \
        params_file:=/root/turtlebot3_ws/src/custom_packages/my_robot_bringup/config/my_tuned_params.yaml

    # Or override individual values on the command line, no YAML edit needed:
    ros2 launch my_robot_bringup avoid_demo.launch.py \
        --ros-args -p stop_distance:=0.6
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('my_robot_bringup')

    default_world = os.path.join(bringup_dir, 'worlds', 'warehouse_world.sdf')
    default_params_file = os.path.join(
        bringup_dir, 'config', 'obstacle_avoider_params.yaml'
    )

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Full path to the Gazebo world file',
    )
    x_pose_arg = DeclareLaunchArgument(
        'x_pose',
        default_value='0.0',
        description='Initial X position of the robot',
    )
    y_pose_arg = DeclareLaunchArgument(
        'y_pose',
        default_value='0.0',
        description='Initial Y position of the robot',
    )
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value=default_params_file,
        description='Full path to the obstacle_avoider parameter YAML file',
    )

    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    params_file = LaunchConfiguration('params_file')

    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'custom_world_demo.launch.py')
        ),
        launch_arguments={
            'world': world,
            'x_pose': x_pose,
            'y_pose': y_pose,
        }.items(),
    )

    obstacle_avoider_node = Node(
        package='my_robot_control',
        executable='obstacle_avoider',
        name='obstacle_avoider',
        output='screen',
        parameters=[params_file],
    )

    return LaunchDescription([
        world_arg,
        x_pose_arg,
        y_pose_arg,
        params_file_arg,
        world_launch,
        obstacle_avoider_node,
    ])
