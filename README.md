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

- Docker
- Visual Studio Code
- Dev Containers extension for easier development integration

For installation instructions, please visit the official tutorials:

- [Install Docker Engine](https://docs.docker.com/engine/install/)
- [Install Visual Studio Code](https://code.visualstudio.com/)
- [Install Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

## Getting Started / Primeros pasos

1. **Clone the `docker-nvidia-graphics` branch** (This is your development branch):

```bash
   git clone -b docker-nvidia-graphics https://github.com/SaulNacion/Quadruped-Project.git
   cd Quadruped-Project
```

2. **Pull the latest changes from the `main` branch** (or from another development branch, such as `quadruped_sim`, `quadruped_nav`, `quadruped_control`, etc.)

```bash
git pull origin main
```

* This will pull the latest changes from the `main` branch (or any other development branch you specify) while respecting the `.gitignore` rules of the development branch (i.e., files like documentation will not be downloaded or updated based on the `.gitignore`).

---

## Verify NVIDIA Container Toolkit

The **NVIDIA Container Toolkit** is required for Docker to access your GPU. Follow these steps on your Ubuntu host:

### Confirm Toolkit installation

```bash
nvidia-container-runtime --version
```

and:

```bash
dpkg -l | grep nvidia-container
```

If the toolkit is correctly installed, you should see details about the version and installed packages. If not, you will need to install it.

### Install the Toolkit (if missing)

Official guide: [NVIDIA Container Toolkit Installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

---

## Preparing X11 Access for GUI Applications

Before running the container, execute the `setup_x11_docker.sh` script to prepare your system to allow Docker containers to display graphical applications:

```bash
chmod +x setup_x11_docker.sh
./setup_x11_docker.sh
```

After running the script, open the container with Visual Studio Code by using the **Command Palette** (`Ctrl+Shift+P`) and selecting **"Dev Container: Rebuild and Reopen in Container"**.

To exit the container, simply choose **"Dev Container: Reopen Folder Locally"**.

---

## Running the Container

To run the container for the first time, follow these steps:

1. Execute `./setup_x11_docker.sh`.
2. Open Visual Studio Code and select **"Dev Container: Rebuild and Reopen in Container"**.

For subsequent use, use **"Dev Container: Reopen in Container"** from the Command Palette.

---

## Test GPU Access Inside the Container

Once inside the container, test GPU access:

```bash
nvidia-smi
glxinfo -B
```

* **`nvidia-smi`** → Displays NVIDIA driver stack information.
* **`glxinfo -B`** → Look for `OpenGL vendor string: NVIDIA Corporation`.

If successful, you can try running:

```bash
gazebo
gz sim -v 4 shapes.sdf   # or: gz gui
```

---

## How `setup_x11_docker.sh` Works

This script sets up the X11 environment for Docker containers, ensuring that graphical applications can be displayed on your host system.

1. **Define the X11 authentication file**:

   ```bash
   XAUTH=/tmp/.docker.xauth
   ```

2. **Clean and create the file**:

   ```bash
   rm -f "$XAUTH"
   touch "$XAUTH"
   ```

3. **Export your X11 cookie**:

   ```bash
   xauth nlist "$DISPLAY" | sed -e 's/^..../ffff/' | \
     xauth -f "$XAUTH" nmerge -
   ```

4. **Set permissions**:

   ```bash
   chmod 644 "$XAUTH"
   ```

5. **Allow Docker to connect locally**:

   ```bash
   xhost +local:docker
   ```

> 📄 **Summary**: This script copies your X11 cookie to a location accessible by Docker, adjusts permissions, and grants access so containers can open GUI windows on your desktop.

---

## Contact / Contacto

For questions or contributions, please contact:

* **GitHub Username**: SaulNacion
* **Email**: [saul.nacion.d@uni.pe](mailto:saul.nacion.d@uni.pe)

---

