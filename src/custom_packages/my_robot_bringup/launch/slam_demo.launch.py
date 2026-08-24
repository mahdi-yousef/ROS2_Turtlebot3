"""
slam_demo.launch.py

Launches TurtleBot3 in the warehouse world plus turtlebot3_cartographer for
SLAM. Drive around (teleop or obstacle_avoider), then save the map:
    ros2 run nav2_map_server map_saver_cli -f \
        ~/turtlebot3_ws/src/custom_packages/my_robot_bringup/maps/warehouse_map
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    bringup_dir = get_package_share_directory('my_robot_bringup')
    cartographer_dir = get_package_share_directory('turtlebot3_cartographer')

    world_file = os.path.join(bringup_dir, 'worlds', 'warehouse_world.sdf')

    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'custom_world_demo.launch.py')
        ),
        launch_arguments={'world': world_file}.items(),
    )

    cartographer_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(cartographer_dir, 'launch', 'cartographer.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    return LaunchDescription([
        world_launch,
        cartographer_launch,
    ])
