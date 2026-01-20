# Autonomous Quadruped Robot for Underground Mining Exploration and Hazard Detection  
# Robot cuadrúpedo autónomo para exploración minera subterránea y detección de peligros

## Description (English)  
The Quadruped Project aims to develop a quadruped robot capable of operating in underground mining environments. Its primary functions include:  
- Mine exploration and monitoring (3D scanning, mapping unexplored or unstable areas).  
- Surveillance for toxic gas detection.  
- Search and rescue operations for trapped or unconscious miners in case of collapses.

Additional potential applications include:  
- Search and localization of objects.  
- Structural evaluation (detecting cracks or deformations).  
- Routine maintenance or inspection tasks.

These tasks are highly complex due to the extreme and unpredictable conditions of underground environments, such as collapsed terrain, zero lighting, limited connectivity, and the presence of hazardous gases or temperatures.

This project is developed by students and supervisors from the National University of Engineering (UNI), Lima, Peru.

## Descripción (Español)  
El Proyecto Cuadrúpedo busca desarrollar un robot cuadrúpedo capaz de operar en entornos mineros subterráneos. Sus funciones principales incluyen:  
- Exploración y monitoreo de minas (escaneo 3D, mapeo de zonas inexploradas o inestables).  
- Vigilancia para la detección de gases tóxicos.  
- Búsqueda y rescate de personas atrapadas, como mineros inconscientes en caso de derrumbe.

Además, se contempla su posible aplicación en tareas adicionales como:  
- Búsqueda y localización de objetos.  
- Evaluación estructural (detección de grietas o deformaciones).  
- Tareas de mantenimiento o reconocimiento rutinario.

Estas tareas presentan un alto nivel de complejidad debido a las condiciones extremas e impredecibles propias de los entornos subterráneos, tales como terrenos colapsados, iluminación nula, conectividad limitada y presencia de gases o temperaturas peligrosas.

Este proyecto es desarrollado por alumnos y supervisores de la Universidad Nacional de Ingeniería (UNI), Lima, Perú.

---

## Requirements / Requisitos

Este proyecto está diseñado para funcionar en un entorno ROS 2 Jazzy Jalisco (Ubuntu 24.04). A continuación se detallan las dependencias necesarias para la simulación, navegación y control.

Dependencias del Sistema
Asegúrate de tener instaladas las siguientes herramientas y librerías base:

- libunwind-dev

- libgoogle-glog-dev

> Agregar en CMakeLists.txt ubicado en quadruped_slam_3d/rko_lio la línea `find_package(glog REQUIRED)`

### Paquetes de ROS 2

| Categoría | Paquetes | Descripción |
| --- | --- | --- |
| **Navegación & SLAM** | `navigation2`, `nav2-bringup`, `slam-toolbox` | Stack de navegación y mapeo. |
| **Simulación** | `ros-gz-sim`, `ros-gz-bridge` | Gazebo Sim (Harmonic) y el puente con ROS 2. |
| **Control** | `ros2-control`, `ros2-controllers`, `gz-ros2-control` | Control de hardware y simulación de actuadores. |
| **Sensores** | `velodyne`, `pointcloud-to-laserscan`, `rko-lio` | Drivers de LiDAR y odometría inercial (LIO). |
| **Visualización** | `rviz2`, `plotjuggler-ros` | Visualización de datos y robótica. |
| **Utilidades** | `xacro`, `robot-localization`, `joint-state-publisher-gui` | Descripción de robots y estimación de estado. |

### Instalación

Para instalar todas las dependencias necesarias en tu sistema, ejecuta el siguiente comando en tu terminal:

```bash
sudo apt-get update && sudo apt-get install -y \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-nav2-minimal-tb* \
    ros-jazzy-slam-toolbox \
    ros-jazzy-pointcloud-to-laserscan \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-rviz2 \
    ros-jazzy-rko-lio \
    ros-jazzy-plotjuggler-ros \
    ros-jazzy-gz-ros2-control \
    ros-jazzy-xacro \
    ros-jazzy-robot-localization \
    ros-jazzy-ros2-controllers \
    ros-jazzy-ros2-control \
    ros-jazzy-velodyne \
    ros-jazzy-velodyne-description \
    ros-jazzy-joint-state-publisher-gui \
    libunwind-dev \
    libgoogle-glog-dev \

```
---

For installation instructions, please visit the official tutorials:

[Ubuntu 24.04 installation guide](https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview)  

[Gazebo installation guide](https://gazebosim.org/docs/latest/ros_installation/) 

### ⚠️ Observación de la instalaciôn de Gazebo

> **Importante:** Para que el archivo de lanzamiento (`launch file`) funcione correctamente, es necesario instalar Gazebo usando su integración oficial con ROS. No utilices otros métodos de instalación (como paquetes independientes o Flatpak), ya que podrían causar errores al lanzar el entorno simulado.
>  
> Esto se debe a que el launch file configura automáticamente algunas rutas (`paths`) y espera que los paquetes de Gazebo estén disponibles en ubicaciones específicas, lo cual solo se garantiza al instalarlo con el siguiente comando:

```bash
sudo apt-get install ros-${ROS_DISTRO}-ros-gz
```

- [Jazzy installation guide](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)  

---

### ⚠️ Datos externos

La carpeta `worlds/models` no está incluida en el repositorio por su tamaño.  
Para descargarla, este es el link del drive: [models](https://drive.google.com/drive/folders/1tynZ0zJsusemuihCU3QADJCJNjwpdFcR?usp=sharing)

Esta carpeta debe estar dentro de `src/quadruped_sim/worlds`
---

## Getting Started / Primeros pasos

1. Clone this repository  
2. Follow the official installation guides linked above to set up your environment  
3. Build the project workspace according to your platform  (TODO)
4. Launch simulations and control nodes as needed  (TODO)

📚 [Read the full project documentation here](https://hosting-quadruped-documentation.readthedocs.io/es/latest/index.html)  

---

## Contact / Contacto

For questions or contributions, please contact the project team.