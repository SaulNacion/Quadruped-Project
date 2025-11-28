import os
from ament_index_python.packages import get_package_share_directory
import yaml
from yaml.loader import SafeLoader

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, TextSubstitution
from launch_ros.substitutions import FindPackageShare

from launch.actions import LogInfo
from launch.actions import TimerAction
from launch.substitutions import EnvironmentVariable, Command
from launch_ros.parameter_descriptions import ParameterValue

from ros_gz_bridge.actions import RosGzBridge

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
    conf_file = os.path.join(os.getenv('CONFIG_DIR'), 'simulation.config')
    if(not os.path.exists(conf_file)):
        print("ERROR File %s not found" % (conf_file))
        return LaunchDescription()

    # Opening config file
    print("Open config file : ", conf_file)
    
    yaml_config_file = open(conf_file)
    data_config_file = yaml.load(yaml_config_file, Loader=SafeLoader)
    
    # Get gazebo list from config file     
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
                if output == None or output == 'none':
                    rosoutput = {}
                else:
                    rosoutput = {f'{output}' }
                world = node_ros.get('world', 'none')
                package = node_ros.get('package', None)
                models_to_load = node_ros.get('models', [])
                try:
                    packagepath = get_package_share_directory(package)
                except Exception as e:
                    print(f" == getNodeInfo error : {e}")
                    return None, None , None, None , False
                for model_config in models_to_load:
                    local_model = model_config.get('uri')
                    print(f"+ {'gazebo':<10} | {packagepath:<70} | {world:<20} | {local_model}") 
            else:
                print('-' * 42 + "  Not simulator running  " + '-' * 43)  

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

        # Printing GZ_SIM_RESOURCE_PATH to check
        log_gz_resource_path = LogInfo(
            msg=[
                'GZ_SIM_RESOURCE_PATH set to: ',
                EnvironmentVariable('GZ_SIM_RESOURCE_PATH')
            ]
        )
        allRosNode.append(log_gz_resource_path)  

        # Printing WORLD_NAME to check
        log_world_name = LogInfo(
            msg=[
                'WORLD_NAME set to: ',
                EnvironmentVariable('WORLD_NAME')
            ]
        )
        allRosNode.append(log_world_name)     

        entire_robot_project = False
         # Spawning Models
        for model_config in models_to_load:
            if model_config.get('name') == "unitree_go2":
                entire_robot_project = True
            model_uri = model_config.get('uri')
            if not model_uri:
                print(f"WARNING: Model configuration in YAML missing 'uri' key: {model_config}")
                continue
            model_dir = os.path.join(packagepath, 'models', model_uri)
            sdf_path = os.path.join(model_dir, 'model.sdf')
            urdf_path = os.path.join(model_dir, 'model.urdf')

            if os.path.exists(sdf_path):
                model_path = sdf_path
            elif os.path.exists(urdf_path):
                model_path = urdf_path
            else:
                print(f"ERROR: urdf or sdf file not founded {model_uri}")
                continue

            world_runtime_name, _ = os.path.splitext(world)
            spawn_args = [
                '-file', model_path,
                '-world', world_runtime_name
            ]
            
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

            # Service to create node, service called world/name_world/create must be active otherwise model will not appear
            spawn_node = Node(
                package='ros_gz_sim',
                executable='create',
                arguments=spawn_args,
                output='screen'
            )
            allRosNode.append(spawn_node)

        #   Bridge Launch 
        if entire_robot_project == False:
            bridge_name = "ros_gz_bridge"
            config_bridge_file = os.path.join(os.getenv('CONFIG_DIR'), 'ros_bridge.yaml')

            bridge_config = Node(
                package='ros_gz_bridge',
                executable='parameter_bridge',
                name=bridge_name,
                output='screen',
                parameters=[
                    {'config_file': config_bridge_file}, 
                    {'use_sim_time': True}             
                ]
            )
            allRosNode.append(bridge_config)

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
    else:
        allRosNode = []

    # get mainnodes list from config file
    indexed_mainnodes_list = {}
    try:
        for mainnode_name, mainnode_config in data_config_file['features']['quadruped']['mainnodes'].items():
            indexed_mainnodes_list[mainnode_name] = {
                'node': mainnode_config,
            }           
    except KeyError as e:
        print(f"  - error reading parameters for {mainnode_name}: {e}") 

    # -- nodes  -
    print('-' * 110 )
    print('-' * 50 + "   Nodes   " + '-' * 49)  
    print(f'+ {"Node":^10} + {"package path":^70} + {"parameters"}')

    plotjuggler_started = False  

    config_dir = os.getenv('CONFIG_DIR', '/workspace/Quadruped-Project/config')
    plotjuggler_layouts_dir = os.path.join(config_dir, 'plotjuggler_layouts')

    for app_name, app_info in indexed_mainnodes_list.items():
        ros_node = app_info.get('node', None)
        if ros_node:
            if ros_node.get('state', False):
                try:
                    rospackage = ros_node.get('package', None)
                    rosnodepath = get_package_share_directory(rospackage)
                    output = ros_node.get('output', None)
                    if output == None or output == 'none':
                        rosoutput = {}
                    else:
                        rosoutput = {f'{output}' }
                    param = ros_node.get('param', "None")
                    if param == None or param == "None":    
                        pmsg = "*local param not defined*"
                    else:
                        pmsg = f"*missing* {param}"
                    print(f"+ {app_name:<10} | {rosnodepath:<70} | {pmsg}")  
                    # print(f"- {app_name:<15} - package {rospackage:<30} - path : {rosnodepath}") 
                    allRosNode.append(Node(
                        package=rospackage,
                        executable=ros_node.get('executable', None),
                        name=ros_node.get('name', app_name),
                        arguments=ros_node.get('arguments', None),
                        output=rosoutput
                    ))

                    # ========== PlotJuggler ==========
                    pj_flag = ros_node.get('plotjuggler', False)

                    if pj_flag and not plotjuggler_started:
                        # Nombre de archivo de layout desde simulation.config
                        layout_file = ros_node.get('plotjuggler_layout', None)
                        pj_arguments = []

                        if layout_file:
                            layout_path = os.path.join(
                                plotjuggler_layouts_dir,
                                layout_file
                            )
                            print(f"  [PlotJuggler] Using layout: {layout_path}")
                            # Argumentos para el nodo
                            pj_arguments = ['--layout', layout_path]
                        else:
                            # Sin layout → se abre solo PlotJuggler vacío
                            print("  [PlotJuggler] Launching WITHOUT layout (no 'plotjuggler_layout' in config)")
                        
                        plotjuggler_node = Node(
                            package='plotjuggler',
                            executable='plotjuggler',
                            name='plotjuggler',
                            arguments=pj_arguments,
                            output='screen'
                        )
                        
                        allRosNode.append(plotjuggler_node)
                        plotjuggler_started = True  
                    # ===========================================================                 
                except Exception as e:
                    print(f" == config file error : {e}")
                    continue
    print('-' * 110 )
       
    print(" ------ starting ros2 nodes ------ ")   
    
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
        value=TextSubstitution(
            text=f"{gazebo_plugin_path}:${{GAZEBO_PLUGIN_PATH}}"
        )
    )

    allRosNode = [set_gazebo_plugin_path] + allRosNode

    config_slam = os.path.join(os.getenv('CONFIG_DIR'), 'mapper_params_online_sync.yaml')
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('slam_toolbox'),
                'launch',
                'online_async_launch.py'
            )
        ]),
        launch_arguments={
            'slam_params_file': config_slam,
            'use_sim_time': 'true'
        }.items(),
    )

    config_slam_3d = os.path.join(os.getenv('CONFIG_DIR'), 'rko_lio_config.yaml')
    slam_3d_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('rko_lio'),
                'launch',
                'odometry.launch.py'
            )
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

    lidar_timestamp = Node(
            package='common_utils',
            executable='lidar_timestamp.py',
            name='lidar_timestamp_node',
            output='screen',
            parameters=[{'use_sim_time': True}]
        )
    
    # allRosNode.append(lidar_timestamp)

    # Retrasar 10 segundos el lanzamiento del SLAM
    delayed_slam_launch = TimerAction(period=20.0, actions=[slam_launch])

    delayed_slam_3d_launch = TimerAction(period=5.0, actions=[slam_3d_launch])

    # allRosNode = [delayed_slam_launch] + [delayed_slam_3d_launch] + allRosNode
    # allRosNode = [delayed_slam_3d_launch] + allRosNode

    if entire_robot_project == False:
        rviz_config_file = os.path.join(os.getenv('CONFIG_DIR'), 'slam_toolbox_default.rviz')
        # Nodo de RViz2
        rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file], # El argumento -d carga la configuración
            parameters=[{'use_sim_time': True}] 
        )
        allRosNode.append(rviz_node)
    
    #---------------------#
    ### Unitree Project ###
    #---------------------# 
    for model_config in models_to_load:
        if model_config.get('name') == "unitree_go2":
            model_pose = model_config.get('pose')
            str(model_pose[0])

            unitree_launch_path = PathJoinSubstitution([
                FindPackageShare("unitree_go2_sim"),
                "launch",
                "unitree_go2_launch.py"
            ])

            unitree_launch = IncludeLaunchDescription(
                PythonLaunchDescriptionSource(unitree_launch_path),
                launch_arguments={
                    "world_init_x": str(model_pose[0]),
                    "world_init_y": str(model_pose[1]),
                    "world_init_z": str(model_pose[2]),
                    "world_init_heading" : str(model_pose[3])
                }.items()
            )
            allRosNode.append(unitree_launch)

    return LaunchDescription(allRosNode)