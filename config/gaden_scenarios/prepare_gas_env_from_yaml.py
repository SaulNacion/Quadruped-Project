#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path
import yaml

"""
Uso:
  python3 prepare_gas_env_from_yaml.py <env_yaml> <target_env_dir>

Ejemplo:
  python3 prepare_gas_env_from_yaml.py \
    /workspace/Quadruped-Project/config/gas_envs/simple_tunnel_env.yaml \
    /workspace/Quadruped-Project/config/gas_envs/simple_tunnel_gas_env
"""

def main():
    if len(sys.argv) != 3:
        print("Uso: python3 prepare_gas_env_from_yaml.py <env_yaml> <target_env_dir>")
        sys.exit(1)

    env_yaml = Path(sys.argv[1]).expanduser().resolve()
    target_env_dir = Path(sys.argv[2]).expanduser().resolve()

    if not env_yaml.is_file():
        print(f"[ERROR] No se encontró env_yaml: {env_yaml}")
        sys.exit(1)

    with open(env_yaml, "r") as f:
        data = yaml.safe_load(f)

    env = data.get("environment", {})
    objects = env.get("objects", [])

    # Directorios de salida
    cad_models_dir = target_env_dir / "cad_models"
    cfg_dir = target_env_dir / "config"
    cad_models_dir.mkdir(parents=True, exist_ok=True)
    cfg_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Objetos en el entorno: {len(objects)}")
    exported_objects = []

    for obj in objects:
        obj_id = obj["id"]
        mesh_file = Path(obj["mesh_file"])
        pose = obj["pose_xyz_rpy"]

        if not mesh_file.is_file():
            print(f"[WARN] Mesh no encontrada: {mesh_file}")
            continue

        # nombre destino: <id>.<ext>  (para evitar choques de nombres)
        ext = mesh_file.suffix  # .dae, .stl, etc.
        dst_name = f"{obj_id}{ext}"
        dst_path = cad_models_dir / dst_name

        # copiar mesh
        shutil.copy2(mesh_file, dst_path)
        print(f"[INFO] Copiado {mesh_file} -> {dst_path}")

        exported_objects.append({
            "id": obj_id,
            # ruta relativa para que sea más portable
            "mesh_file": str(Path("cad_models") / dst_name),
            "pose_xyz_rpy": pose,
        })

    # Guardamos un YAML “limpio” solo con lo necesario para el simulador de gas
    gas_env_cfg = {
        "gas_environment": {
            "description": env.get("description", ""),
            "objects": exported_objects,
        }
    }

    out_cfg = cfg_dir / "gas_env_objects.yaml"
    with open(out_cfg, "w") as f:
        yaml.safe_dump(gas_env_cfg, f, sort_keys=False)

    print(f"[INFO] Config de entorno de gas escrita en: {out_cfg}")
    print(f"[INFO] Objetos exportados: {len(exported_objects)}")


if __name__ == "__main__":
    main()
