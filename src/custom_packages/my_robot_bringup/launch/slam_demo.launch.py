"""
slam_demo.launch.py

Launches TurtleBot3 in the selected Gazebo world via
custom_world_demo.launch.py, plus turtlebot3_cartographer for SLAM.

The world defaults to warehouse_world.sdf, but a different world
can be supplied through the 'world' launch argument.

ros2 launch my_robot_bringup slam_demo.launch.py
  #default arguments
    #world:=/root/turtlebot3_ws/install/my_robot_bringup/share/my_robot_bringup/worlds/warehouse_world.sdf
    #x_pose:=0.0   
    #y_pose:=0.0

# Specify everything example:
ros2 launch my_robot_bringup slam_demo.launch.py \
  world:=/root/turtlebot3_ws/src/turtlebot3_simulations/turtlebot3_gazebo/worlds/turtlebot3_world.world \
  x_pose:=-2.0 \
  y_pose:=-0.5

    # When you're happy with map coverage, save it:
    ros2 run nav2_map_server map_saver_cli \
        -f ~/turtlebot3_ws/src/custom_packages/my_robot_bringup/maps/map_name
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_dir = get_package_share_directory('my_robot_bringup')
    cartographer_dir = get_package_share_directory('turtlebot3_cartographer')

    # Default world
    default_world = os.path.join(
        bringup_dir,
        'worlds',
        'warehouse_world.sdf'
    )

    # Allow the world to be overridden from the command line
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Full path to the world file to load'
    )

    world = LaunchConfiguration('world')

    # Launch Gazebo with the selected world
    world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                bringup_dir,
                'launch',
                'custom_world_demo.launch.py'
            )
        ),
        launch_arguments={'world': world}.items()
    )
    x_pose = LaunchConfiguration('x_pose', default='0.0')
    y_pose = LaunchConfiguration('y_pose', default='0.0')
    # Launch Cartographer
    cartographer_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                cartographer_dir,
                'launch',
                'cartographer.launch.py'
            )
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    return LaunchDescription([
        world_arg,
        world_launch,
        cartographer_launch,
    ])
