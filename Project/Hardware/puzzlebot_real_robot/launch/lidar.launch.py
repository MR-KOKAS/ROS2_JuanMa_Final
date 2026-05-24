from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # Driver del RPLiDAR A1
    rplidar_driver = Node(
       package='sllidar_ros2',
       executable='sllidar_node',
       name='sllidar_node',
       output='screen',
       parameters=[{
          'channel_type': 'serial',
          'serial_port': '/dev/ttyUSB1',
          'serial_baudrate': 115200,
          'frame_id': 'rplidar_link',
          'inverted': False,
          'angle_compensate': True,
          'scan_mode': 'Standard',
          }],
      )
  
     # TF estatica: laser_frame (URDF) -> rplidar_link (donde llegan los scans)
     # Corrige rotacion Z de 180 grados (3.14159 rad) por montaje fisico del LiDAR
    lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='lidar_static_tf',
        output='screen',
        arguments=[
           '--x', '0', '--y', '0', '--z', '0',
           '--yaw', '0', '--pitch', '0', '--roll', '0', # Valor original 3.14159 el primero
           '--frame-id', 'laser_frame',
           '--child-frame-id', 'rplidar_link',
           ],
        )
    
    return LaunchDescription([
        rplidar_driver,
        lidar_tf,
        ])
