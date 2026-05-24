#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Loads the robot URDF/Xacro, starts robot_state_publisher and opens RViz.
Useful for verifying the robot model and TF tree in isolation.
"""

import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Generate and return the launch description for standalone URDF visualization."""

    # Package directory
    package_share_dir = get_package_share_directory('puzzlebot_description')

    # File paths
    urdf_xacro_path = os.path.join(package_share_dir, 'urdf', 'puzzlebot.xacro')
    rviz_config_path = os.path.join(package_share_dir, 'rviz', 'puzzlebot_description.rviz')

    # Generate URDF string from Xacro file
    robot_description_urdf = xacro.process_file(urdf_xacro_path).toxml()

    # Launch configuration
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    # ========== 1. Launch arguments ==========
    sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time (/clock) from Gazebo when true'
    )

    # ========== 2. Robot state publisher ==========
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description_urdf,
            'use_sim_time': use_sim_time,
        }]
    )

    # ========== 3. RViz2 visualization ==========
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        sim_time_arg,
        robot_state_publisher_node,
        rviz_node,
    ])
