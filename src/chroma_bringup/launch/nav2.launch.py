"""
nav2.launch.py
Launches the ROS 2 Navigation stack for a specific robot instance.
"""

import os
import sys
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

sys.path.insert(0, os.path.dirname(__file__))
from _yaml_utils import patch_and_write_yaml

def generate_launch_description():
    args = [
        DeclareLaunchArgument('robot_id', default_value='tb3_0'),
        DeclareLaunchArgument('map_yaml', default_value=''),
        DeclareLaunchArgument('nav2_params', default_value=''),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
    ]

    return LaunchDescription(args + [OpaqueFunction(function=launch_nav2)])

def launch_nav2(context, *args, **kwargs):
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    robot_id = context.launch_configurations['robot_id']
    map_yaml = context.launch_configurations['map_yaml']
    nav2_params = context.launch_configurations['nav2_params']
    use_sim_time = context.launch_configurations['use_sim_time']

    patched_params = patch_and_write_yaml(
        nav2_params, 
        [
            ('ROBOT_NAMESPACE/base_footprint', f'{robot_id}/base_footprint'),
            ('ROBOT_NAMESPACE/base_link', f'{robot_id}/base_link'),
            ('ROBOT_NAMESPACE/odom', f'{robot_id}/odom'),
            ('ROBOT_NAMESPACE/scan', f'/{robot_id}/scan'),
            ('ROBOT_NAMESPACE', robot_id),
        ],
        f'nav2_params_{robot_id}_'
    )

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'namespace': robot_id,
            'use_namespace': 'True',
            'use_sim_time': use_sim_time,
            'params_file': patched_params,
            'map': map_yaml,
            'autostart': 'True',
            'use_composition': 'False',
            'log_level': 'WARN',
        }.items()
    )

    return [TimerAction(period=6.0, actions=[nav2_launch])]