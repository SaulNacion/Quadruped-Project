# Proyecto Cuadrúpedo

## Descripción del Proyecto

El proyecto consiste en el desarrollo de un robot cuadrúpedo destinado a mejorar la seguridad en la industria minera al explorar áreas peligrosas e inaccesibles para los trabajadores humanos, como túneles estrechos, zonas con gases tóxicos o riesgo de colapso. La implementación en hardware implicará la construcción de un chasis ligero capaz de soportar las condiciones ambientales propias de la mina y que tenga un grado de protección IP ante polvo y agua, pero lo suficientemente ligero para no impedir movimientos ágiles del robot por su entorno. Este robot estará equipado con una suite de sensores exteroceptivos y propioceptivos que le permitirá estimar de manera robusta su estado actual y el de su entorno en tiempo real. Para este fin, se desarrollará el software de la plataforma utilizando un enfoque modular inalámbrico basado en ROS2, con simulaciones en Gazebo y Rviz para validar el sistema antes de desplegarlo y permitir desarrollo continuo de sus subcomponentes. Posteriormente, será desplegado en la supercomputadora de Inteligencia Artificial llamada Jetson Orin Nano de Nvidia. En cuanto a la gestión energética, se diseñarán baterías eficientes, con buena durabilidad y factor de forma optimizado para asegurar lograr un mayor tiempo de uso sin recargar y extender el tiempo de vida de las baterías durante el momento de operación.

Se abordarán cuatro aspectos clave durante el desarrollo del software: percepción, planificación, comunicación y control. Los algoritmos avanzados de percepción permitirán al robot interpretar la transmisión de video y detectar en tiempo real elementos usando sus sensores exteroceptivos, proporcionando información acerca de los cambios topográficos y anomalías geológicas en áreas que presenten grietas o fisuras. Se desarrollarán algoritmos de planificación de trayectorias para garantizar un movimiento seguro y eficiente, evitando colisiones y obstáculos en la mayoría de los casos. Se establecerán sistemas resilientes de comunicación para la interacción con operadores humanos a distancia de manera segura en entornos denegados, facilitando la supervisión remota y la transmisión de datos en tiempo real. Además, se implementarán algoritmos de control modernos para garantizar una locomoción fluida y estable del robot en diversos terrenos y condiciones operativas. Cabe resaltar que, en estas condiciones, los robots a ruedas y drones tienen una operatividad limitada, por lo que este proyecto ofrece una prueba de concepto que pretende ser validada en los entornos competentes y, en el futuro, poder ser incluido durante las actividades diarias en una operación minera. Es decir, se espera que el robot sea programado para realizar inspecciones regulares de manera autónoma de la infraestructura minera, permitiendo la detección temprana de problemas de seguridad o mantenimiento y contribuyendo así a una actividad minera más tecnológica y segura en el Perú. 

## Conocimientos Previos Software
### GIT y GitHub Desktop
GIT es un software de control de versiones. Los proyectos generalmente tienen múltiples desarrolladores trabajando en paralelo. Así que necesitan un sistema de control de versiones para asegurarse de que no hay conflictos de código entre ellos.
El sistema de ramas en Git permite a los desarrolladores trabajar individualmente en una tarea (Por ejemplo: una rama -> una tarea O una Rama -> un desarrollador). Básicamente, se puede pensar en Git como una aplicación de software pequeña que controla tu código base, si eres un desarrollador.
En un nivel más alto, GitHub es un servicio en la nube que ayuda a los desarrolladores a almacenar, administrar su código y crear repositorios basados en GIT, al igual que llevar un registro y control de cualquier cambio sobre este código.
#### Flujo de Git
  * Git fetch: Descarga archivos de un repositorio remoto a tu repositorio local. Este comando descarga el contenido remoto, pero no actualiza el estado de trabajo del repositorio local, por lo que el trabajo actual no se verá afectado.
  * Git pull: El comando git pull se emplea para extraer y descargar contenido desde un repositorio remoto y actualizar al instante el repositorio local para reflejar ese contenido.
  * Git push: Se usa para cargar contenido del repositorio local a un repositorio remoto.
  * Git merge: Se usa para fusionar una rama con otra rama activa.
  * Git add: Se usa para agregar archivos al área de preparación.
  * Git commit: Captura una instantánea de los archivos del área de preparación y las guarda en el repositorio local. Las instantáneas confirmadas pueden considerarse como versiones "seguras" de un proyecto.
  
<p align="center">
  <img src="_static/images/guide/git_workflow.png" alt="rviz" width="400"/>  
</p>

Cuando se trabaja en Git se pueden usar una variedad de estrategias de ramificación y flujos de trabajo. Cuando se habla de una rama se refiere a una línea de desarrollo independiente, generalmente existe una rama principal llamada “master” o “main” del cual pueden salir ramificaciones para trabajar en el desarrollo de nuevo código aislando el trabajo con respecto a otras ramas y al trabajo de los demás miembros del equipo.
Para el proyecto usaremos el método de ramificación llamado “GitHub Flow”, a diferencia de otros flujos, es simple y ligero. Como característica clave se tiene a la existencia de una rama principal que se encontrará siempre lista para “producción”, a partir de la rama principal se pueden crear nuevas ramas que tendrán la finalidad de trabajar y agregar nuevas funcionalidades, una vez el código de dichas ramas halla sido validado y aprobado, se fusionarán con la rama principal.

<p align="center">
  <img src="_static/images/guide/git.png" alt="rviz" width="500"/>  
</p>

#### Instalación
Visitar el enlace GitHub Desktop | Simple collaboration from your desktop , dar Click en Download for Windows (64bit) y hacer doble click en el ejecutable descargado. Además, descargar mediante el siguiente enlace <https://git-scm.com/downloads> 

<p align="center">
  <img src="_static/images/guide/git_desktop.png" alt="rviz" width="600"/>  
</p>


En el siguiente enlace pueden ver un pequeño tutorial de como usar la aplicación de GitHub Desktop: <https://www.youtube.com/watch?v=PvUexC0-D2s>
### Docker
Docker es un software utilizado para desplegar aplicaciones dentro de contenedores virtuales. La principal diferencia con respecto a las máquinas virtuales es que los contenedores Docker comparten el sistema operativo del anfitrión, mientras que las máquinas virtuales también tienen un sistema operativo invitado que se ejecuta sobre el sistema anfitrión.
#### Instalación

En el siguiente enlace se muestra un tutorial para la instalación de Docker y WSL: Docker, Instlación en Windows (más WSL, Window Subsystem for Linux) <https://www.youtube.com/watch?v=ZO4KWQfUBBc>
#### Comandos básicos para ejecutar en el terminal

Para poder practicar los siguientes comandos comandos usar <image_name> = ubuntu
  * Docker pull <image_name>: Descargar una imagen desde el hub de Docker
  * Docker images: Muestra la lista de imágenes descargadas
  * Docker rmi <image_name>: Borra una imagen descargada
  * Docker run --name <container_name> <image_name>: Crear y correr un contenedor a partir de una imagen
  * Docker start|stop <container_name>: Inicia o detiene un contenedor
  * Docker rm <container_name>: Borra un contenedor
  * Docker ps: Muestra los contenedores corriendo en el sistema
  * Docker ps -a: Muestra todos los contenedores
  * Docker exec -it <container_name> /bin/bash: Abre un terminal bash de un contenedor corriendo.

En el siguiente documento pueden ver más comandos útiles para usar en Docker <https://docs.docker.com/get-started/docker_cheatsheet.pdf>
#### Comandos básicos de Linux 
  
En el siguiente enlace se encuentran enlistados algunos comandos básicos de Linux: Los 60 comandos básicos de Linux que todo usuario debe saber <https://www.hostinger.com/es/tutoriales/linux-comandos>

### Instalacion de ROS
**Nota: Todo este proceso que se detallará a continuacación esta grabado en este [video](https://unipe-my.sharepoint.com/shared?id=%2Fpersonal%2Fsaul%5Fnacion%5Fd%5Funi%5Fpe%2FDocuments%2FProyecto%20Cuadr%C3%BApedo%2FInstalacion%20Ubuntu%20y%20ROS&listurl=%2Fpersonal%2Fsaul%5Fnacion%5Fd%5Funi%5Fpe%2FDocuments).** 
#### Instalacion de ROS
La versión de ROS que usaremos será Humble y gazebo classic, para esto necesitamos tener   instalado la versión 22.04 de Ubuntu que se llama Jammy.

<img src="_static/images/install_ros/Humble.png" alt="Descripción de la imagen" width="200"/>  

Instalar ubuntu se puede hacer de varias maneras, la más sencilla es atravez de [wsl2](https://learn.microsoft.com/es-es/windows/wsl/install), las otras son dual boot y a travez de una máquina virtual.
1. wsl (instalación fácil, recomendado)
2. dual boot (instalación tediosa, recomendado)
3. máquina virtual (no recomendado)

#### Instalar wsl en windows 
    Para esto se puede seguir la guía oficial de windows [link](https://learn.microsoft.com/es-es/windows/wsl/) o sino siga estos pasos:
##### Abrir un terminal de windows PowerShell o Windows Command en modo administrador.

###### Image
<img src="_static/images/install_ros/power_shell.png" alt="Descripción de la imagen" width="600"/>   

##### Ejecutar

```bash
wsl --install -d Ubuntu-22.04
```
###### Output (en el caso de ustedes se procedera con la instalación)
<img src="_static/images/install_ros/output_terminal.png" alt="Descripción de la imagen" width="600"/>   

##### Descargar visual estudio code

```bash
wsl --install -d Ubuntu-22.04
```

#### Instalar Ubuntu en dual boot
    Para instalar rn dual boot se encuentran varios videos de youtube, [video](https://www.youtube.com/watch?v=FId4-IO-yj4) 

#### Instalar ROS2 Humble
    Para instalar Ros2 Humble solo seguir el siguiente [documento](https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html) o en tal caso ejecutar las siguientes lineas de codigo en el terminal. 

##### Configuración regional o local
```bash
locale  # check for UTF-8

sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

locale  # verify settings
```
##### Setup resources

```bash
sudo apt install software-properties-common
sudo add-apt-repository universe

sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

```
##### Install ros2

```bash
sudo apt update
sudo apt upgrade
sudo apt install ros-humble-desktop
```
##### Configuración de entorno 

Cada vez que se abre una nueva terminal, es necesario configurarla utilizando el siguiente comando:
```bash
source /opt/ros/humble/setup.bash
```
Si no desea realizar esta acción manualmente cada vez, puede agregar esta línea al archivo .bashrc, el cual se ejecuta automáticamente cada vez que se abre una nueva terminal. Para hacerlo, utilice el siguiente comando:
```bash
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
```
Después de modificar el archivo .bashrc, es necesario reiniciar la terminal actual para que los cambios surtan efecto. Esto solo es necesario si continúa trabajando en la misma terminal, ya que el archivo .bashrc se ejecuta automáticamente al abrir una nueva terminal. Para aplicar los cambios en la terminal actual, ejecute:
```bash
source ~/.bashrc
```
##### Probar un ejemplo básico

Abrir un terminal y ejecutar 
###### Terminal 1
```bash
source /opt/ros/humble/setup.bash 
ros2 run demo_nodes_cpp talker
```
###### Terminal 2
```bash
source /opt/ros/humble/setup.bash
ros2 run demo_nodes_py listener
```
Ejecutar source **/opt/ros/humble/setup.bash** solo es necesario si no se agrego la línea source **/opt/ros/humble/setup.bash** al archivo **.bashrc.**

###### Output terminal 1
<img src="_static/images/install_ros/simple_publish_example.png" alt="Output terminal 1" width="400"/>  

###### Output terminal 2
<img src="_static/images/install_ros/simple_subscri_example.png" alt="Output terminal 2" width="340"/>


## Configuración de entorno
```bash
source ~/quadruped_robot_ws/install/setup.bash
```
### Lanzamiento     
```bash
ros2 launch quadruped_description rviz_fake_joints.launch.xml
```
#### Output 

<p align=center>     
<img src="_static/images/quadruped_description/rviz.png" alt="rviz" width="400"/> 
</p>

## Requerimientos del Sistema
- Control
  * Actuadores: Control de cada como que permite el movimiento del robot.
  * Estabilidad y movimiento: Control para mantener el equilibrio estático y en movimiento (dinámica).
  * Marcha: Patrón de movimiento de las patas del robot.
- Percepción
  * Reconocimiento de terreno: Identificación de superficies, detección de irregularidades.
  * Detectar obstáculos: Detección de obstáculos que impidan el movimiento en la trayectoria planificada.
  * Detección de objetos: Detección de objetos en específico.
- Navegación
  * Planificación de rutas: Generación de trayectoria que evite obstáculos y que minimice el uso de recursos.
  * Localización: Localización del robot dentro del entorno.
o	Orientación: Orientación del robot dentro del entorno.
o	Mapeo: Construcción del mapa del entorno.
- Sensorización
  * Temperatura: Monitoreo de condiciones ambientales.
  * Humedad: Monitoreo de condiciones ambientales.
  * Malformaciones: Detectar malformaciones del entorno que si bien no afectan en la trayectoria serían importantes para reportes del terreno.
- Comunicación
  * Protocolos inalámbricos: Comunicación que permita la transmisión de video y datos.
  * Antenas: Diseño que asegure la comunicación en todo momento.

<p align="center">
  <img src="_static/images/system_requirements/schema.png" alt="rviz" width="600"/>  
</p>

## Funcionalidades Necesarias del robot Prototipo Software
A. Que pueda hacer movimientos de roll pitch yaw sin desplazarse->Control

B. Detección de rango de desplazamiento -> Percepción (C)

C. Detección de obstáculos -> Percepción 

D. Tenga funcionamiento de Marcha o caminata -> Control (A)

E. Mapeo del terreno (Utilización de SLAM). -> Navegación, Percepción (B)

F. El robot tenga la capacidad de desplazarse de un punto a otro solo con un mapa 2D. ->Navegación (E)

G. Funcionamiento de seguimiento a una persona -> Navegación y Percepción (B, F)

H. Que tenga funcionalidad de levantarse en caso se caiga, equilibrio. -> Control (A)
 
## Descripcion de paquetes


1. ### Quadruped Description: 
    Este paquete de ROS almacena los archivos de modelado del robot en formato URDF y XACRO, así como los archivos .stl y .obj del robot. También contiene archivos de lanzamiento (launch) para visualizar el robot en RViz. [video](https://www.youtube.com/watch?v=CwdbsvcpOHM/"video")

2. ### Quadruped Bringup: 
    Este paquete de ROS incluye los controladores (drivers) para el hardware real, como cámaras y LiDAR. También contiene archivos de lanzamiento que permiten iniciar el robot tanto en simulación como en su versión física, integrando todas sus características en un entorno ROS.

3. ### Quadruped Control: 
    Este paquete de ROS gestiona los controladores de alto nivel (high-level control), que permiten controlar el movimiento del robot (como marcha y giro), así como hacerlo permanecer de pie. Además, incluye archivos de configuración y lanzamiento de los controladores.

4. ### Quadruped Interfaces: 
    ...
5. ### Quadruped Nav: 
 
    1. #### Localization:
        Este paquete contiene los algoritmos de localización (AMCL) y sus archivos de configuración, permitiendo que el robot se localice en su entorno.
    2. #### Planning:
        Paquete que contiene los algoritmos para la generación y seguimiento de trayectorias.
    3. #### Slam:
        Paquete que contiene los algoritmos de SLAM (Simultaneous Localization and Mapping), los mapas generados y los archivos de configuración. Permite navegar y generar mapas del entorno.

6. ### Quadruped Perception
    Este paquete agrupa todas las funcionalidades relacionadas con la visión, como la detección de obstáculos y el reconocimiento del entorno, utilizando herramientas como TensorFlow y YOLO.

7. ### Test
    Este paquete agrupa todos los códigos para su testeo.
