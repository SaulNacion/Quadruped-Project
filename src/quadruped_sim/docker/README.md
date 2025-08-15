# Setting Up a Docker Container with GPU Access for Simulation (NVIDIA Graphics Card)

Before starting, make sure you have a working Docker setup:

* [Docker](https://docs.docker.com/get-docker/)

---

## 1. Verify NVIDIA Container Toolkit

The **NVIDIA Container Toolkit** is required for Docker to access your GPU. Follow these steps on your Ubuntu host:

### 1.1 Check if Docker detects the GPU

```bash
docker run --rm --gpus all nvidia/cuda:12.0.0-base-ubuntu24.04 nvidia-smi
```

> This image version matches the one used inside the container.

* If you see the **`nvidia-smi`** table with your GPU details → The runtime is installed and working.
* If you get errors like `Unknown runtime` or `could not select device driver` → The toolkit is missing or misconfigured.

---

### 1.2 Check Docker runtime configuration

```bash
cat /etc/docker/daemon.json
```

You should see something similar to:

```json
{
  "runtimes": {
    "nvidia": {
      "path": "nvidia-container-runtime",
      "runtimeArgs": []
    }
  }
}
```

---

### 1.3 Confirm Toolkit installation

```bash
nvidia-container-runtime --version
```

and:

```bash
dpkg -l | grep nvidia-container
```

---

### 1.4 Install the Toolkit (if missing)

Official guide: [NVIDIA Container Toolkit Installation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
Quick install commands for Ubuntu:

```bash
# 1. Add NVIDIA repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

distribution=$(. /etc/os-release;echo $ID$VERSION_ID)

curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 2. Install the toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# 3. Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker

# 4. Restart Docker
sudo systemctl restart docker
```

---

## 2. Container Build Files

* `Dockerfile`
* `docker-compose.yml`

### 2.1 Build the image

```bash
docker build -t ros-jazzy-simulation .
```

Check the image:

```bash
docker images
```

Expected output example:

```bash
REPOSITORY             TAG        IMAGE ID       CREATED        SIZE
ros-jazzy-simulation   latest     fedc908ad24e   12 hours ago   3.5GB
```

---

## 3. Preparing X11 Access for GUI Applications

Before running the container, execute the `setup_x11_docker.sh` script.
This prepares your system so a Docker container can display graphical applications.

>  📌 **Important**: You must be running an X11 graphical session.


> ⚠️ **Warning**
> 
> In the `docker-compose.yml` file, you must update **line 16** to match the path where you want the workspace to be stored.
>
> Example:
>
> ```yaml
> ${HOME}/docker/simulation_qdp/ros2_ws:/home/dev/ros2_ws
> ```
>
> Replace `${HOME}/docker/simulation_qdp/ros2_ws` with your desired local directory path.

```bash
chmod +x setup_x11_docker.sh
./setup_x11_docker.sh
docker compose up
```

Then, in a new terminal:

```bash
docker compose exec -it ros_jazzy_sim bash
```

Inside the container, test GPU access:

```bash
nvidia-smi
glxinfo -B
```

* **`nvidia-smi`** → Displays NVIDIA driver stack information.
* **`glxinfo -B`** → Look for `OpenGL vendor string: NVIDIA Corporation`.

If successful, try running:

```bash
gazebo
gz sim -v 4 shapes.sdf   # or: gz gui
```

---

## 4. How `setup_x11_docker.sh` Works

**Define the X11 authentication file:**

```bash
XAUTH=/tmp/.docker.xauth
```

Stores a temporary copy of your X11 authentication cookie.

**Clean and create the file:**

```bash
rm -f "$XAUTH"
touch "$XAUTH"
```

**Export your X11 cookie:**

```bash
xauth nlist "$DISPLAY" | sed -e 's/^..../ffff/' | \
  xauth -f "$XAUTH" nmerge -
```

**Set permissions:**

```bash
chmod 644 "$XAUTH"
```

**Allow Docker to connect locally:**

```bash
xhost +local:docker
```

> 📄 **Summary**: This script copies your X11 cookie to a location accessible by Docker, adjusts permissions, and grants access so containers can open GUI windows on your desktop.

---
>ℹ️ **Info**
>
>Visual Studio Code Integration
>
>For easier container development, you can use the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
