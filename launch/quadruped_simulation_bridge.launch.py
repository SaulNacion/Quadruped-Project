# quadruped_simulation_bridge.launch.py
import os
from ament_index_python import get_package_share_directory
import yaml
from yaml.loader import SafeLoader

from launch import LaunchDescription

from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, DeclareLaunchArgument, LogInfo, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, TextSubstitution, LaunchConfiguration, PythonExpression
from launch_ros.substitutions import FindPackageShare

from launch.actions import LogInfo
from launch.actions import TimerAction
from launch.substitutions import EnvironmentVariable
from launch.conditions import IfCondition

from ros_gz_bridge.actions import RosGzBridge  # si lo usas

def getNodeInfo(listofnode, nodename):
    node_info = listofnode.get(nodename, None)
    if node_info:
        node_ros = node_info.get('node', None)
        if node_ros:
            output = node_ros.get('output', None)
            if output == None or output == 'none':
                rosoutput = {}
            else:
                rosoutput = {f'{output}' }
            state = node_ros.get('state', True)
            param = node_ros.get('param', "None")
            package = node_ros.get('package', None)
            try:
                packagepath = get_package_share_directory(package)
            except Exception as e:
                print(f" == getNodeInfo error : {e}")
                return None, None , None, None , False
            return  param, rosoutput , package, packagepath, state
        else:
            return None, None , None, None , False
    else:
        return None, None , None, None , False

def generate_launch_description():
    # --- Declare argument to choose slam mode ---
    declare_slam_mode = DeclareLaunchArgument(
        'slam_mode',
        default_value='2d',
        description="Which SLAM to run: '2d' (slam_toolbox) or '3d' (rko_lio)"
    )

    # read config files
    conf_file = os.path.join(os.getenv('CONFIG_DIR'), 'simulation.config')
    if(not os.path.exists(conf_file)):
        print("ERROR File %s not found" % (conf_file))
        return LaunchDescription()

    print("Open config file : ", conf_file)
    yaml_config_file = open(conf_file)
    data_config_file = yaml.load(yaml_config_file, Loader=SafeLoader)

    # Build simulator indexed list (same logic que before)
    indexed_simulator_list = {}
    try:
        for simulator_name, simulator_config in data_config_file['simulator'].items():
            indexed_simulator_list[simulator_name] = {
                'node': simulator_config,
            }
    except KeyError as e:
        print(f"  - error reading parameters for {simulator_name}: {e}")

    # display node list with parameters, parameters will be added later 
    print('-' * 110 )
    print('-' * 50 + " Simulator " + '-' * 49)    
    print(f'+ {"Simulator":^10} + {"package path":^70} + {"world":^20} + {"model"}')

    allRosNode = []
    node_info = indexed_simulator_list.get('gazebo', None)

    if node_info:
        node_ros = node_info.get('node', None)
        if node_ros:
            if node_ros.get('state', False):
                output = node_ros.get('output', None)
                world = node_ros.get('world', 'none')
                package = node_ros.get('package', None)
                models_to_load = node_ros.get('models', [])
                try:
                    packagepath = get_package_share_directory(package)
                except Exception as e:
                    print(f" == getNodeInfo error : {e}")
                    return LaunchDescription()
            else:
                print('-' * 42 + "  Not simulator running  " + '-' * 43)
                return LaunchDescription()
    # Simulator Launch 
    if node_ros.get('state', False):
        world_runtime_name, _ = os.path.splitext(world)
        set_world_name = SetEnvironmentVariable(
            name='WORLD_NAME',
            value=world_runtime_name
        )
        gz_sim_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('ros_gz_sim'), 
                    'launch', 
                    'gz_sim.launch.py'
                ])
            ),
            launch_arguments={
                'gz_args': [
                    PathJoinSubstitution([
                        packagepath,
                        'worlds',
                        world
                    ]),
                    ' -r'
                ],
                'on_exit_shutdown': 'True'
            }.items()
        )

    allRosNode = [
        declare_slam_mode,
        set_world_name,
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            [
                PathJoinSubstitution([packagepath, 'models']),
                TextSubstitution(text=':'),
                PathJoinSubstitution([packagepath, 'worlds', 'models'])
            ]
        ),
        gz_sim_launch
    ]
    
    # Logging
    log_gz_resource_path = LogInfo(
        msg=['GZ_SIM_RESOURCE_PATH set to: ', EnvironmentVariable('GZ_SIM_RESOURCE_PATH')]
    )
    allRosNode.append(log_gz_resource_path)

    log_world_name = LogInfo(
        msg=['WORLD_NAME set to: ', EnvironmentVariable('WORLD_NAME')]
    )
    allRosNode.append(log_world_name)

    # ------ Spawning Models (make spawn conditional by slam_mode) ------
    for model_config in models_to_load:
        model_uri = model_config.get('uri')
        model_dir = os.path.join(packagepath, 'models', model_uri)
        sdf_path = os.path.join(model_dir, 'model.sdf')
        urdf_path = os.path.join(model_dir, 'model.urdf')

        if os.path.exists(sdf_path):
            model_path = sdf_path
        elif os.path.exists(urdf_path):
            model_path = urdf_path
        else:
            print(f"ERROR: urdf or sdf file not found for model {model_uri}")
            continue

        spawn_args = ['-file', model_path, '-world', world_runtime_name]
        model_name_instance = model_config.get('name')
        if model_name_instance:
            spawn_args.extend(['-name', model_name_instance])
        model_pose = model_config.get('pose')
        if model_pose and len(model_pose) == 6:
            spawn_args.extend([
                '-x', str(model_pose[0]),
                '-y', str(model_pose[1]),
                '-z', str(model_pose[2]),
                '-R', str(model_pose[3]),
                '-P', str(model_pose[4]),
                '-Y', str(model_pose[5])
            ])

        # decide condition for spawn:
        # if model uri contains 'lidar3D' -> only spawn when slam_mode == '3d'
        # if model uri contains 'lidar' (2D robot name) -> only spawn when slam_mode == '2d'
        # else spawn unconditionally (common models)
        condition = None
        if model_uri and 'lidar' in model_uri:
            condition = IfCondition(PythonExpression(["'", LaunchConfiguration('slam_mode'), "' == '3d'"]))
        elif model_uri and ('lidar' not in model_uri):
            # robot with 2D lidar (assuming name contains 'lidar' but not 'lidar3D')
            condition = IfCondition(PythonExpression(["'", LaunchConfiguration('slam_mode'), "' == '2d'"]))
        else:
            condition = None

        spawn_node = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=spawn_args,
            output='screen',
            condition=condition
        )
        allRosNode.append(spawn_node)

    # Bridge configs: use different yaml per SLAM mode (place these files in CONFIG_DIR)
    config_bridge_file_2d = os.path.join(os.getenv('CONFIG_DIR'), 'ros_bridge_2d.yaml')
    config_bridge_file_3d = os.path.join(os.getenv('CONFIG_DIR'), 'ros_bridge_3d.yaml')

    bridge_config_2d = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge_2d',
        output='screen',
        parameters=[{'config_file': config_bridge_file_2d}, {'use_sim_time': True}],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_mode'), "' == '2d'"]))
    )

    bridge_config_3d = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge_3d',
        output='screen',
        parameters=[{'config_file': config_bridge_file_3d}, {'use_sim_time': True}],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_mode'), "' == '3d'"]))
    )

    allRosNode.append(bridge_config_2d)
    allRosNode.append(bridge_config_3d)

    # static tf (leave always on or adapt if needed)
    config_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf',
        arguments=['0.8', '0', '0.5', '0', '0', '0',
                   'robot_diferencial_sensors/chassis', 'robot_diferencial_sensors/chassis/gpu_lidar'],
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    allRosNode.append(config_tf)

    # -- main nodes from config (same as before) --
    indexed_mainnodes_list = {}
    try:
        for mainnode_name, mainnode_config in data_config_file['features']['quadruped']['mainnodes'].items():
            indexed_mainnodes_list[mainnode_name] = {'node': mainnode_config}
    except KeyError as e:
        print(f"  - error reading parameters for {mainnode_name}: {e}")

    for app_name, app_info in indexed_mainnodes_list.items():
        ros_node = app_info.get('node', None)
        if ros_node and ros_node.get('state', False):
            try:
                rospackage = ros_node.get('package', None)
                rosnodepath = get_package_share_directory(rospackage)
                output = ros_node.get('output', None)
                if output == None or output == 'none':
                    rosoutput = {}
                else:
                    rosoutput = {f'{output}' }
                allRosNode.append(Node(
                    package=rospackage,
                    executable=ros_node.get('executable', None),
                    name=ros_node.get('name', app_name),
                    arguments=ros_node.get('arguments', None),
                    output=rosoutput
                ))
            except Exception as e:
                print(f" == config file error : {e}")
                continue
    
    # -- nodes  -
    print('-' * 110 )
    print('-' * 50 + "   Nodes   " + '-' * 49)  
    print(f'+ {"Node":^10} + {"package path":^70} + {"parameters"}')  

    # GAZEBO plugin path env (unchanged)
    gazebo_plugin_path = os.path.join(
        os.getenv('HOME'),
        'Personal/Quadruped-Project',
        'install',
        'quadruped_sim',
        'lib',
        'quadruped_sim'
    )
    set_gazebo_plugin_path = SetEnvironmentVariable(
        name='GAZEBO_PLUGIN_PATH',
        value=TextSubstitution(text=f"{gazebo_plugin_path}:${{GAZEBO_PLUGIN_PATH}}")
    )
    allRosNode = [set_gazebo_plugin_path] + allRosNode

    # SLAM launches (include but conditionally start only one)
    config_slam = os.path.join(os.getenv('CONFIG_DIR'), 'mapper_params_online_sync.yaml')
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ]),
        launch_arguments={
            'slam_params_file': config_slam,
            'use_sim_time': 'true'
        }.items(),
    )

    config_slam_3d = os.path.join(os.getenv('CONFIG_DIR'), 'rko_lio_config.yaml')
    slam_3d_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('rko_lio'), 'launch', 'odometry.launch.py')
        ]),
        launch_arguments={
            'config_file': config_slam_3d,
            'rviz': 'true',
            'lidar_topic': 'lidar_with_time',
            'imu_topic': 'imu',
            'base_frame': 'robot_diferencial_sensors/chassis',
            'use_sim_time': 'true'
        }.items(),
    )

    # lidar_timestamp: sólo si usas rko_lio (3D)
    lidar_timestamp_node = Node(
        package='common_utils',
        executable='lidar_timestamp.py',
        name='lidar_timestamp_node',
        output='screen',
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_mode'), "' == '3d'"])),
    )

    allRosNode.append(lidar_timestamp_node)

    # TimerActions con condición para que sólo uno de los SLAM se lance
    delayed_slam_launch_2d = TimerAction(
        period=20.0,
        actions=[slam_launch],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_mode'), "' == '2d'"]))
    )

    delayed_slam_3d_launch = TimerAction(
        period=20.0,
        actions=[slam_3d_launch],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_mode'), "' == '3d'"]))
    )

    allRosNode = [delayed_slam_launch_2d, delayed_slam_3d_launch] + allRosNode

    # RViz: carga distintos archivos segun modo (opcional)
    rviz_2d = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_slam2d',
        output='screen',
        arguments=['-d', os.path.join(os.getenv('CONFIG_DIR'), 'slam_toolbox_default.rviz')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(PythonExpression(["'", LaunchConfiguration('slam_mode'), "' == '2d'"]))
    )



    allRosNode.append(rviz_2d)
    

    return LaunchDescription(allRosNode)
