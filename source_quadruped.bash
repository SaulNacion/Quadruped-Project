
QUADRUPEP_PROJECT_FOLDER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export QUADRUPEP_PROJECT_FOLDER

echo "Project folder: $QUADRUPEP_PROJECT_FOLDER"

export CONFIG_DIR="${QUADRUPEP_PROJECT_FOLDER}/config"

echo "Config dolfer: $CONFIG_DIR"

echo "========================"
echo "==== Menú de Aliases Quadruped ===="
echo "sws   -> Fuente del workspace (source install/setup.bash)"
echo "quad  -> Cargar workspace y lanzar simulación"
echo "========================"

alias quad="ros2 launch  $QUADRUPEP_PROJECT_FOLDER/launch/quadruped_simulation.launch.py"
alias sws="source  $QUADRUPEP_PROJECT_FOLDER/install/setup.bash"