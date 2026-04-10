#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import launch.logging

def generate_launch_description():
    # Config paths
    nav2_config = os.path.join(
        get_package_share_directory('pirc_navigation'),
        'config', 'nav2_params.yaml')
    
    bt_config = os.path.join(
        get_package_share_directory('pirc_navigation'),
        'config', 'bt_config.yaml')
    
    # Nodes
    nav2_bringup = Node(
        package='nav2_bringup',
        executable='bringup_launch.py',
        parameters=[nav2_config],
        output='screen'
    )
    
    mpc_controller = Node(
        package='pirc_navigation',
        executable='casadi_mpc',
        name='mpc_controller',
        parameters=[{'robot_model': 'diff_drive'}],
        output='screen'
    )
    
    bt_navigator = Node(
        package='pirc_navigation',
        executable='bt_navigator',
        name='bt_navigator',
        parameters=[bt_config],
        output='screen'
    )
    
    rplidar = Node(
        package='rplidar_ros',
        executable='rplidar_composition',
        name='rplidar_node',
        parameters=[{'serial_port': '/dev/ttyUSB0', 'frame_id': 'laser'}],
        output='screen'
    )
    
    realsense = Node(
        package='realsense2_camera',
        executable='rs_launch.py',
        name='realsense',
        output='screen'
    )
    
    return LaunchDescription([
        nav2_bringup,
        mpc_controller,
        bt_navigator,
        rplidar,
        realsense,
    ])
