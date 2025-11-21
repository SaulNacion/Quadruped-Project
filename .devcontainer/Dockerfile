# Imagen base oficial ROS 2 Jazzy con todas las herramientas desktop
FROM osrf/ros:jazzy-desktop-full

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# Paquetes extra útiles (sudo, editores, utilidades gráficas)
RUN apt-get update && apt-get install -y \
    mesa-utils \
    sudo nano vim less \
 && rm -rf /var/lib/apt/lists/*

# Instalación de Nav2, SLAM Toolbox, TurtleBot y utilidades para Gazebo Modern en ROS 2 Jazzy
RUN apt-get update && apt-get install -y \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-nav2-minimal-tb* \
    ros-jazzy-slam-toolbox \
    ros-jazzy-pointcloud-to-laserscan \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-rviz2 \
 && rm -rf /var/lib/apt/lists/*


# --- Configuración de usuario (para que coincida con el host y evitar problemas con permisos) ---
ARG USER=dev
ARG UID=1000
ARG GID=1000

RUN set -eux; \
  groupname="${USER}"; \
  if getent group "${GID}" >/dev/null; then \
    groupname="$(getent group "${GID}" | cut -d: -f1)"; \
  else \
    groupadd -g "${GID}" "${groupname}"; \
  fi; \
  if getent passwd "${UID}" >/dev/null; then \
    existing_user="$(getent passwd "${UID}" | cut -d: -f1)"; \
    usermod -l "${USER}" -d "/home/${USER}" -m "${existing_user}" || true; \
    usermod -g "${GID}" "${USER}" || true; \
  else \
    useradd -m -s /bin/bash -u "${UID}" -g "${GID}" "${USER}"; \
  fi; \
  usermod -aG sudo "${USER}"; \
  echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-${USER}

USER ${USER}
WORKDIR /workspace/Quadruped-Project

# Fuente de ROS siempre que abras shell
RUN echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc

CMD ["bash"]
