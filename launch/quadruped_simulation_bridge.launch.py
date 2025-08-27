import os
from ament_index_python import get_package_share_directory
import yaml
from yaml.loader import SafeLoader

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

from launch.actions import LogInfo
from launch.substitutions import EnvironmentVariable

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
    print(f'+ {"Simulator":^10} + {"package path":^70} + {"world:":^70} + {"model"}')
    
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
                models_to_load = node_ros.get('models', []) # Obtiene la lista de modelos, por defecto vacía
                try:
                    packagepath = get_package_share_directory(package)
                except Exception as e:
                    print(f" == getNodeInfo error : {e}")
                    return None, None , None, None , False
                print(f"+ {'gazebo':<10} | {packagepath:<70} | {world:<70} | {models_to_load}") 
            else:
                print('-' * 42 + "  Not simulator running  " + '-' * 43)  

    # Simulator Launch 
    if node_ros.get('state', False):
        gz_sim_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([
                    FindPackageShare('ros_gz_sim'), 
                    'launch', 
                    'gz_sim.launch.py'
                ])
            ),
            launch_arguments={
                'gz_args': PathJoinSubstitution([
                    packagepath,
                    'worlds',
                    world
                ]),
                # 'extra_gz_args': extra_gz_args_string, # Models not working, service for creation very slow
                'on_exit_shutdown': 'True'
            }.items()
        )

        allRosNode = [
            SetEnvironmentVariable(
                'GZ_SIM_RESOURCE_PATH',
                PathJoinSubstitution([packagepath, 'models'])
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

         # Spawning Models
        for model_config in models_to_load:
            model_uri = model_config.get('uri')
            if not model_uri:
                print(f"WARNING: Model configuration in YAML missing 'uri' key: {model_config}")
                continue
            model_path = os.path.join(packagepath, 'models', model_uri, 'model.sdf') # Ajusta 'model.sdf' si el archivo principal tiene otro nombre

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
        bridge_name = "ros_gz_bridge"
        config_bridge_file = os.path.join(os.getenv('CONFIG_DIR'), 'ros_bridge.yaml')

        bridge_config = RosGzBridge(
                bridge_name=bridge_name,
                config_file=config_bridge_file,
            )
        
        allRosNode.append(bridge_config)

        config_tf = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_tf_green',
            arguments=['0.8', '0', '0.5', '0', '0', '0',
                       'robot_diferencial/chassis', 'robot_diferencial/chassis/gpu_lidar'],
            output='screen'
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
                except Exception as e:
                    print(f" == config file error : {e}")
                    continue
    print('-' * 110 )
       
    print(" ------ starting ros2 nodes ------ ")   
     
    return LaunchDescription(allRosNode)