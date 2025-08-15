# Base: Ubuntu 24.04 + ROS 2 Jazzy (orientada a simulación)
FROM osrf/ros:jazzy-simulation

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# Paquetes (incluye sudo) + GUI tools
RUN apt-get update && apt-get install -y \
    ros-jazzy-rviz2 \
    ros-jazzy-ros-gz \
    mesa-utils \
    sudo nano vim less \
 && rm -rf /var/lib/apt/lists/*

# --- UID/GID configurables (por defecto 1000, pero los puedes sobreescribir en build) ---
ARG USER=dev
ARG UID=1000
ARG GID=1000

# Crear o reutilizar grupo/usuario sin fallar si ya existen
RUN set -eux; \
  groupname="${USER}"; \
  if getent group "${GID}" >/dev/null; then \
    groupname="$(getent group "${GID}" | cut -d: -f1)"; \
    echo "Usando grupo existente ${groupname} (GID ${GID})"; \
  else \
    groupadd -g "${GID}" "${groupname}"; \
  fi; \
  if getent passwd "${UID}" >/dev/null; then \
    existing_user="$(getent passwd "${UID}" | cut -d: -f1)"; \
    echo "UID ${UID} ya existe (usuario ${existing_user}); renombrando a ${USER}"; \
    usermod -l "${USER}" -d "/home/${USER}" -m "${existing_user}" || true; \
    usermod -g "${GID}" "${USER}" || true; \
  else \
    useradd -m -s /bin/bash -u "${UID}" -g "${GID}" "${USER}"; \
  fi; \
  usermod -aG sudo "${USER}"; \
  echo "${USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/90-${USER}

USER ${USER}
WORKDIR /home/${USER}

# Fuente de ROS al abrir shell
RUN echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc

# Workspace
RUN mkdir -p ~/ros2_ws/src
WORKDIR /home/${USER}/ros2_ws

CMD ["bash"]


