#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import yaml

"""
Uso:
    python3 export_world_to_env.py <world_file> <models_root> <output_yaml>

Ejemplo:
    python3 export_world_to_env.py \
        empty_world.world \
        /workspace/Quadruped-Project/src/quadruped_sim/worlds/models \
        cave_env.yaml
"""

def parse_pose(text):
    """
    Convierte 'x y z roll pitch yaw' -> [x, y, z, roll, pitch, yaw] (floats).
    Si no hay pose, devuelve [0,0,0,0,0,0].
    """
    if text is None:
        return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    parts = text.strip().split()
    parts += ["0.0"] * (6 - len(parts))
    return [float(p) for p in parts[:6]]


def find_mesh_uris_in_model(model_sdf_path: Path):
    """
    Abre model.sdf y devuelve una lista de URIs de meshes encontradas.
    Ignora duplicados (ej. collision y visual usando la misma mesh).
    """
    tree = ET.parse(model_sdf_path)
    root = tree.getroot()

    mesh_uris = []
    seen = set()

    for mesh in root.iter("mesh"):
        uri_el = mesh.find("uri")
        if uri_el is not None and uri_el.text:
            uri = uri_el.text.strip()
            if uri not in seen:
                seen.add(uri)
                mesh_uris.append(uri)
    return mesh_uris


def resolve_mesh_path(mesh_uri: str, model_dir: Path):
    """
    Convierte una URI de mesh a una ruta de archivo.
    Casos típicos:
      - 'meshes/cavecorner01.dae'
      - 'model://Cave Corner 01/meshes/cavecorner01.dae'
    """
    if mesh_uri.startswith("model://"):
        # model://Cave Corner 01/meshes/cavecorner01.dae
        parts = mesh_uri.split("://", 1)[1]  # 'Cave Corner 01/meshes/...'
        subparts = parts.split("/", 1)
        if len(subparts) == 2:
            rel_path = subparts[1]          # 'meshes/cavecorner01.dae'
        else:
            rel_path = ""                   # caso raro
        return (model_dir / rel_path).resolve()
    else:
        # Asumimos ruta relativa al directorio del modelo
        return (model_dir / mesh_uri).resolve()


def main():
    if len(sys.argv) != 4:
        print("Uso: python3 export_world_to_env.py <world_file> <models_root> <output_yaml>")
        sys.exit(1)

    world_file = Path(sys.argv[1]).expanduser().resolve()
    models_root = Path(sys.argv[2]).expanduser().resolve()
    output_yaml = Path(sys.argv[3]).expanduser().resolve()

    if not world_file.is_file():
        print(f"[ERROR] No se encontró world_file: {world_file}")
        sys.exit(1)
    if not models_root.is_dir():
        print(f"[ERROR] No se encontró models_root: {models_root}")
        sys.exit(1)

    print(f"[INFO] Leyendo mundo: {world_file}")
    tree = ET.parse(world_file)
    root = tree.getroot()

    # Buscamos todos los <include> en el world
    includes = list(root.iter("include"))
    print(f"[INFO] Includes encontrados: {len(includes)}")

    env_models = []

    for idx, inc in enumerate(includes):
        uri_el = inc.find("uri")
        if uri_el is None or not uri_el.text:
            continue

        uri_text = uri_el.text.strip()
        if not uri_text.startswith("model://"):
            # ignoramos cosas que no sean modelos
            continue

        # Nombre del modelo tal como está en el uri
        # e.g. model://Cave Corner 01
        model_name = uri_text.replace("model://", "")
        include_pose = parse_pose(inc.findtext("pose"))

        # Directorio del modelo en la carpeta de modelos
        model_dir = models_root / model_name
        model_sdf = model_dir / "model.sdf"

        if not model_sdf.is_file():
            print(f"[WARN] No se encontró model.sdf para modelo '{model_name}' en {model_sdf}")
            continue

        mesh_uris = find_mesh_uris_in_model(model_sdf)
        if not mesh_uris:
            print(f"[WARN] No se encontraron meshes en {model_sdf}")
            continue

        for m_idx, mesh_uri in enumerate(mesh_uris):
            mesh_path = resolve_mesh_path(mesh_uri, model_dir)
            if not mesh_path.is_file():
                print(f"[WARN] Mesh no encontrada en disco: {mesh_path} (uri: {mesh_uri})")
                continue

            env_models.append({
                "id": f"{model_name}_{idx}_{m_idx}",
                "model_name": model_name,
                "mesh_file": str(mesh_path),
                "pose_xyz_rpy": include_pose,  # [x,y,z,roll,pitch,yaw]
            })

    env_data = {
        "environment": {
            "description": "Exported from Gazebo world",
            "world_file": str(world_file),
            "models_root": str(models_root),
            "objects": env_models,
        }
    }

    output_yaml.parent.mkdir(parents=True, exist_ok=True)
    with open(output_yaml, "w") as f:
        yaml.safe_dump(env_data, f, sort_keys=False)

    print(f"[INFO] Entorno exportado a: {output_yaml}")
    print(f"[INFO] Objetos exportados: {len(env_models)}")


if __name__ == "__main__":
    main()
