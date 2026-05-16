#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Starts SLAM Toolbox in online‑async mapping mode together with Gazebo and RViz.

Launch order:
  1. Gazebo + PuzzleBot          (from puzzlebot_gazebo)
  2. SLAM Toolbox                (async_slam_toolbox_node with slam_toolbox.yaml)
  3. RViz2                       (pre‑configured display)

Usage:
    ros2 launch puzzlebot_navigation2 slam.launch.py
    ros2 launch puzzlebot_navigation2 slam.launch.py use_sim_time:=true
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Generate and return the launch description for SLAM mapping."""

    # Package directories
    nav2_pkg = get_package_share_directory('puzzlebot_navigation2')
    gazebo_pkg = get_package_share_directory('puzzlebot_gazebo')

    # File paths
    slam_config_file = os.path.join(nav2_pkg, 'config', 'slam_toolbox.yaml')
    rviz_config_file = os.path.join(nav2_pkg, 'rviz', 'slam.rviz')

    # Launch configuration
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # ========== 1. Launch arguments ==========
    sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time (/clock) from Gazebo'
    )

    # ========== 2. Gazebo simulation with PuzzleBot ==========
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_pkg, 'launch', 'puzzlebot_gazebo.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # ========== 3. SLAM Toolbox (online asynchronous mapping) ==========
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_config_file,
            {'use_sim_time': use_sim_time}
        ],
    )

    # ========== 4. RViz2 visualization ==========
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        sim_time_arg,
        gazebo_launch,
        slam_node,
        rviz_node,
    ])
