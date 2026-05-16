import os
import xacro

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_share(pkg: str) -> str:
    """Devuelve el directorio share/ de un paquete instalado."""
    return get_package_share_directory(pkg)


def _robot_urdf(xacro_path: str) -> str:
    """Procesa un archivo xacro y devuelve el URDF como cadena XML."""
    return xacro.process_file(xacro_path).toxml()


# ---------------------------------------------------------------------------
# Generador principal
# ---------------------------------------------------------------------------

def generate_launch_description() -> LaunchDescription:

    # ── Rutas de paquetes ────────────────────────────────────────────────
    share_description = _resolve_share('puzzlebot_description')
    share_sim         = _resolve_share('puzzlebot_gazebo')
    share_gazebo_ros  = _resolve_share('gazebo_ros')

    xacro_path = os.path.join(share_description, 'urdf', 'puzzlebot.urdf.xacro')
    world_path = os.path.join(share_sim, 'worlds', 'maze_world.world')

    urdf_xml = _robot_urdf(xacro_path)

    # ── Argumentos declarados ────────────────────────────────────────────
    arg_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Sincronizar con /clock de Gazebo',
    )
    arg_x = DeclareLaunchArgument('x_pos', default_value='0.0',  description='Posición X de spawn')
    arg_y = DeclareLaunchArgument('y_pos', default_value='0.0',  description='Posición Y de spawn')
    arg_z = DeclareLaunchArgument('z_pos', default_value='0.05', description='Posición Z de spawn')
    arg_yaw = DeclareLaunchArgument('yaw',  default_value='0.0',  description='Orientación yaw de spawn')

    cfg_sim_time = LaunchConfiguration('use_sim_time')
    cfg_x   = LaunchConfiguration('x_pos')
    cfg_y   = LaunchConfiguration('y_pos')
    cfg_z   = LaunchConfiguration('z_pos')
    cfg_yaw = LaunchConfiguration('yaw')

    # ── Gazebo Classic ───────────────────────────────────────────────────
    gazebo_launcher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(share_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world':   world_path,
            'verbose': 'false',
            'pause':   'false',
        }.items(),
    )

    # ── robot_state_publisher ────────────────────────────────────────────
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': urdf_xml,
            'use_sim_time': cfg_sim_time,
        }],
    )

    # ── Spawn del Puzzlebot ──────────────────────────────────────────────
    spawn_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_puzzlebot',
        output='screen',
        arguments=[
            '-topic',  'robot_description',
            '-entity', 'puzzlebot',
            '-x', cfg_x,
            '-y', cfg_y,
            '-z', cfg_z,
            '-Y', cfg_yaw,
        ],
    )

    return LaunchDescription([
        arg_sim_time,
        arg_x,
        arg_y,
        arg_z,
        arg_yaw,
        gazebo_launcher,
        rsp_node,
        spawn_node,
    ])