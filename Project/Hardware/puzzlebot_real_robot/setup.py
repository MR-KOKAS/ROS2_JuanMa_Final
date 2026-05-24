import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'puzzlebot_real_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*.urdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='itzelh',
    maintainer_email='itzelh@todo.todo',
    description='TODO: Package real Puzzlebot',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'puzzlebot_localization = puzzlebot_real_robot.puzzlebot_localization:main',
            'puzzlebot_joint_state_publisher = puzzlebot_real_robot.puzzlebot_joint_state_publisher:main',
        ],
    },
)