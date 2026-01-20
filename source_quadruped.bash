QUADRUPEP_PROJECT_FOLDER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export QUADRUPEP_PROJECT_FOLDER

echo "Project folder: $QUADRUPEP_PROJECT_FOLDER"

export CONFIG_DIR="${QUADRUPEP_PROJECT_FOLDER}/config"

echo "Config folder: $CONFIG_DIR"

echo "========================"
echo "==== Menú de Aliases Quadruped ===="
echo "sws       -> Fuente del workspace (source install/setup.bash)"
echo "quad      -> Cargar workspace y lanzar simulación con bridge_ros"
echo "build     -> Construir el workspace"
echo "rebuild   -> Borrar build/, install/, log/ y reconstruir"
echo "========================"

alias quad="ros2 launch $QUADRUPEP_PROJECT_FOLDER/launch/quadruped_simulation_bridge.launch.py"
alias sws="source $QUADRUPEP_PROJECT_FOLDER/install/setup.bash"

# Construcción normal
alias build="cd $QUADRUPEP_PROJECT_FOLDER && colcon build"

# Reconstrucción limpia
alias rebuild='cd $QUADRUPEP_PROJECT_FOLDER && rm -rf build install log && colcon build'
