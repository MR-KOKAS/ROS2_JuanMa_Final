import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_real = get_package_share_directory('puzzlebot_real_robot')

    urdf_path = os.path.join(pkg_real, 'urdf', 'puzzlebot.urdf')
    config_path = os.path.join(pkg_real, 'config', 'puzzlebot_params.yaml')

    with open(urdf_path, 'r') as urdf_file:
        robot_description_content = urdf_file.read()

    # 1) micro-ROS agent: puente entre Hackerboard y ROS 2
    micro_ros_agent = Node(
        package='micro_ros_agent',
        executable='micro_ros_agent',
        name='micro_ros_agent',
        arguments=['serial', '-D', '/dev/ttyUSB1'],
        output='screen',
    )

    # 2) LiDAR (driver + TF estatica laser_frame->rplidar_link)
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_real, 'launch', 'lidar.launch.py')
        )
    )

    # 3) robot_state_publisher: lee URDF y publica TF del robot
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        emulate_tty=True,  # Añadir esto
        respawn=True,      # Añadir esto - reinicia si falla
        respawn_delay=2.0, # Esperar 2 segundos antes de reiniciar

        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': False,
            'publish_frequency': 50.0, #Frequency agregué
            'ignore_timestamp': False #Delete timestamp agregué
            
        }],
    )

    # 4) puzzlebot_localization (Manchester): encoders -> /odom
    puzzlebot_localization = Node(
        package='puzzlebot_real_robot',
        executable='puzzlebot_localization',
        name='puzzlebot_localization_node',
        output='screen',
        parameters=[config_path],
    )

    # 5) puzzlebot_joint_state_publisher (Manchester):
    #    /odom -> /joint_states + TF odom->base_footprint
    puzzlebot_jsp = Node(
        package='puzzlebot_real_robot',
        executable='puzzlebot_joint_state_publisher',
        name='puzzlebot_joint_state_publisher_node',
        output='screen',
        parameters=[config_path],
    )

    return LaunchDescription([
        micro_ros_agent,
        lidar_launch,
        robot_state_publisher,
        puzzlebot_localization,
        puzzlebot_jsp,
    ])
