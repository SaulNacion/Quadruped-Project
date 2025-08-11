from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch import LaunchDescription


from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    #~~~~~~~~~~~~~~~~~~~~~~ PACKAGEs ~~~~~~~~~~~~~~~~~
    package_name = 'test_package'

    #~~~~~~~~~~~~~~~~~~~~~~~~ PATHS ~~~~~~~~~~~~~~~~~~~~~~~~~~~+
    package_share = get_package_share_directory(package_name)

    rviz_file = PathJoinSubstitution([package_share,'rviz','camera.rviz'])

    #~~~~~~~~~~~~~~~~~~~~~~~~ ARGUMENTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~+

    arg_device = DeclareLaunchArgument(
        name='device',
        default_value= '1',
        description='Dipositivo para capturar el video, esto aparece haciendo --ls //dev-- el dispositivo aparece como videoX, donde x es un número'
    )


    arg_fps = DeclareLaunchArgument(
        name='fps',
        default_value= '30',
        description='frames por segundo'
    )


    config_device = LaunchConfiguration('device')
    config_fps = LaunchConfiguration('fps')

    #~~~~~~~~~~~~~~~~~~~~~~~~ Node ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    publisher_camera = Node(
        name='publisher_camera',
        package='test_package',
        executable='publisher_camera',
        parameters=[{'device': config_device, 
                     'fps': config_fps }],
        output='screen',
        emulate_tty=True
    )

    rviz = Node(
        name='rviz2',
        package='rviz2',
        executable='rviz2',
        output='screen',
        emulate_tty=True,
        arguments=['-d', rviz_file],
    )


    return LaunchDescription([
        arg_device,
        arg_fps,   
        rviz, 
        publisher_camera
    ])