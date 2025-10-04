#!/bin/bash
# setup_x11_docker.sh
# Script para configurar el acceso X11 para contenedores Docker

XAUTH=/tmp/.docker.xauth

# Eliminar archivo anterior si existe
rm -f "$XAUTH"

# Crear archivo vacío
touch "$XAUTH"

# Exportar la cookie de autenticación X11 y guardarla en el archivo
xauth nlist "$DISPLAY" | sed -e 's/^..../ffff/' | xauth -f "$XAUTH" nmerge -

# Ajustar permisos
chmod 644 "$XAUTH"

# Permitir conexiones locales desde Docker
xhost +local:docker


# chmod +x setup_x11_docker.sh
# ./setup_x11_docker.sh
