"""
nav_demo.launch.py

Launches TurtleBot3 in the warehouse world, brings up turtlebot3_navigation2
against a previously-saved map, and optionally starts the waypoint_follower
node.

Usage:
    # full mission:
    ros2 launch my_robot_bringup nav_demo.launch.py \
        map:=/root/turtlebot3_ws/src/custom_packages/my_robot_bringup/maps/warehouse_map.yaml

    # nav2 only, no autonomous mission:
    ros2 launch my_robot_bringup nav_demo.launch.py \
        map:=/root/turtlebot3_ws/src/custom_packages/my_robot_bringup/maps/warehouse_map.yaml \
        run_waypoint_follower:=false
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('my_robot_bringup')
    tb3_nav_dir = get_package_share_directory('turtlebot3_navigation2')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(bringup_dir, 'maps', 'warehouse_map.yaml'),
        description='Full path to the map YAML file saved from slam_demo.launch.py',
    )

    run_waypoint_follower_arg = DeclareLaunchArgument(
        'run_waypoint_follower',
        default_value='true',
        description='Whether to start the autonomous waypoint_follower node',
    )

    world_file = os.path.join(bringup_dir, 'worlds', 'warehouse_world.sdf')

    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'custom_world_demo.launch.py')
        ),
        launch_arguments={'world': world_file}.items(),
    )

    # Computed explicitly (mirroring turtlebot3_navigation2's own logic)
    # rather than relying on navigation2.launch.py's internal self-referential
    # LaunchConfiguration('params_file', default=...) trick, which breaks
    # when navigation2.launch.py is nested inside another launch file.
    turtlebot3_model = os.environ['TURTLEBOT3_MODEL']
    ros_distro = os.environ.get('ROS_DISTRO')
    param_file_name = turtlebot3_model + '.yaml'
    if ros_distro == 'humble':
        params_file = os.path.join(tb3_nav_dir, 'param', ros_distro, param_file_name)
    else:
        params_file = os.path.join(tb3_nav_dir, 'param', param_file_name)

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(tb3_nav_dir, 'launch', 'navigation2.launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': 'true',
            'params_file': params_file,
        }.items(),
    )

    waypoint_follower_node = Node(
        package='my_robot_control',
        executable='waypoint_follower',
        name='waypoint_follower',
        output='screen',
        parameters=[os.path.join(bringup_dir, 'config', 'waypoints.yaml')],
        condition=IfCondition(LaunchConfiguration('run_waypoint_follower')),
    )

    return LaunchDescription([
        map_arg,
        run_waypoint_follower_arg,
        world_launch,
        nav2_launch,
        waypoint_follower_node,
    ])
