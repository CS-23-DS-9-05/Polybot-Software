# Copyright (c) 2021 Juan Miguel Jimeno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition
from ament_index_python import get_package_share_directory
from nav2_common.launch import RewrittenYaml


def generate_launch_description():

    robot_ns = os.getenv('ROBOT_NAMESPACE')
    if robot_ns is None:
        robot_ns = "polybot01"

    sensors_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'sensors.launch.py']
    )

    joy_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_bringup'), 'launch', 'joy_teleop.launch.py']
    )

    description_launch_path = PathJoinSubstitution(
        [FindPackageShare('linorobot2_description'), 'launch', 'description.launch.py']
    )

    ekf_config_path = PathJoinSubstitution(
        [FindPackageShare("linorobot2_base"), "config", "ekf.yaml"]
    )

    # ekf namespace configuration
    if robot_ns != "":
        ekf_config = RewrittenYaml(
            source_file=ekf_config_path,
            root_key=robot_ns,
            param_rewrites={},
            convert_types=True
        )
    else:
        ekf_config = ekf_config_path

    return LaunchDescription([
        DeclareLaunchArgument(
            name='base_serial_port',
            default_value='/dev/ttyACM0',
            description='Linorobot Base Serial Port'
        ),

       DeclareLaunchArgument(
            name='joy',
            default_value='false',
            description='Use Joystick'
        ),

        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            output='screen',
            arguments=['serial', '--dev', LaunchConfiguration("base_serial_port")]
        ),

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                ekf_config
            ],
            remappings=[
                ("odometry/filtered", "odom"),
                ('/tf', 'tf'),
                ('/tf_static', 'tf_static')
            ]
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(description_launch_path)
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sensors_launch_path),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(joy_launch_path),
            condition=IfCondition(LaunchConfiguration("joy")),
        )
    ])
