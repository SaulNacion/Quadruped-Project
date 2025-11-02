#!/usr/bin/env python3
"""
package_to_gzmodel.py — Reorganiza un paquete exportado (SolidWorks→URDF) a un **modelo** de Gazebo

Estructura generada:
  <dest>/<ModelName>/
    ├─ meshes/
    ├─ model.sdf
    └─ model.config

Novedades:
- Flag `--generate-convex` crea mallas convexas `col_<stem>.stl` (u opcionalmente sufijo) a partir
  de las mallas encontradas en `meshes/` usando `trimesh` (si está instalado). Si `trimesh` no está
  disponible, intenta ejecutar un script local `make_convex_collision.py` con interfaz flexible.
- `--use-convex-collision` reescribe URIs de <collision> a las mallas convexas generadas
  (prefijo `col_` o sufijo `_col`).

Uso típico:
  python package_to_gzmodel.py --src ./Pata_URDF \
    --add-position-plugins --generate-convex --use-convex-collision --verbose
"""

from pathlib import Path
import argparse
import shutil
import sys
import subprocess
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, List, Optional

SDF_VERSION = "1.11"
MESH_EXTS = {".stl", ".STL", ".dae", ".obj", ".OBJ"}

def eprint(*a, **k):
    print(*a, file=sys.stderr, **k)

def text_attr(el: Optional[ET.Element], name: str, default: str = "") -> str:
    if el is None:
        return default
    return el.attrib.get(name, default)

def join_pose(xyz: str, rpy: str) -> str:
    xyz = (xyz or "0 0 0").strip()
    rpy = (rpy or "0 0 0").strip()
    return f"{xyz} {rpy}"

def convert_uri_to_model(uri: str, model_name: str) -> str:
    if uri.startswith("package://"):
        rest = uri[len("package://"):]
        parts = rest.split("/", 1)
        if len(parts) == 2:
            _, tail = parts
            return f"model://{model_name}/{tail}"
        return f"model://{model_name}/{rest}"
    if uri.startswith("file://"):
        from pathlib import Path as _P
        return f"model://{model_name}/meshes/{_P(uri[len('file://'):]).name}"
    return f"model://{model_name}/{uri}"

def detect_urdf(src: Path) -> Optional[Path]:
    urdf_dir = src / "urdf"
    cands = []
    if urdf_dir.is_dir():
        cands.extend(sorted(urdf_dir.glob("*.urdf")))
    cands.extend(sorted(src.glob("*.urdf")))
    if not cands:
        return None
    for p in cands:
        if p.stem == src.name:
            return p
    return cands[0]

def gather_mesh_sources(src: Path) -> List[Path]:
    paths = []
    if (src / "materials" / "meshes").is_dir():
        paths.append(src / "materials" / "meshes")
    if (src / "meshes").is_dir():
        paths.append(src / "meshes")
    uniq, seen = [], set()
    for p in paths:
        q = p.resolve()
        if q not in seen:
            uniq.append(q); seen.add(q)
    return uniq

def copy_mesh_tree(src_dirs: List[Path], dest_mesh: Path) -> int:
    dest_mesh.mkdir(parents=True, exist_ok=True)
    count = 0
    for base in src_dirs:
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in MESH_EXTS:
                rel = p.relative_to(base)
                out = dest_mesh / rel
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, out); count += 1
    return count

# ---------- CONVEX GENERATION ----------

def _to_mesh(obj):
    try:
        import trimesh
    except Exception:
        return None
    if isinstance(obj, trimesh.Trimesh):
        return obj
    if isinstance(obj, trimesh.Scene):
        geos = [g for g in obj.dump() if isinstance(g, trimesh.Trimesh)]
        if not geos:
            return None
        return trimesh.util.concatenate(geos)
    return None


def generate_convex_meshes(mesh_root: Path, prefix: str = "col_", suffix: str = "", overwrite: bool = False, verbose: bool = False) -> int:
    """
    Genera mallas convexas en mesh_root como <prefix><stem><suffix>.<EXT> para cada malla soportada.
    - Detecta archivos con extensiones en MESH_EXTS (incluye .stl y .STL).
    - Mantiene la extensión **y su mayúsc/minúsc** del archivo original.
    Requiere 'trimesh'. Si no está, intenta make_convex_collision.py (si existe).
    """
    # Try internal via trimesh
    try:
        import trimesh
    except Exception as e:
        # Fallback: external script if exists
        script = Path(__file__).with_name("make_convex_collision.py")
        if script.exists():
            for flag in ("--dir", "--mesh-dir"):
                cmd = [sys.executable, str(script), flag, str(mesh_root), "--prefix", prefix]
                if overwrite: cmd.append("--overwrite")
                try:
                    if verbose: print("[convex] Ejecutando externo:", " ".join(map(str, cmd)))
                    subprocess.run(cmd, check=True)
                    return -1  # unknown count
                except subprocess.CalledProcessError:
                    continue
        eprint("[warn] No se pudo importar 'trimesh' ni ejecutar make_convex_collision.py. Omite generación convexa.")
        return 0

    # Build file list with all supported extensions
    files = []
    for ext in MESH_EXTS:
        files.extend(mesh_root.rglob(f"*{ext}"))

    count = 0
    for p in sorted(set(files)):
        name_low = p.name.lower()
        # Skip already convex
        if name_low.startswith("col_") or name_low.endswith("_col.stl") or name_low.endswith("_col.obj") or name_low.endswith("_col.dae"):
            continue
        stem = p.stem
        ext = p.suffix or ".stl"  # preserve original extension and its case
        outname = f"{prefix}{stem}{suffix}{ext}"
        out = p.with_name(outname)
        if out.exists() and not overwrite:
            if verbose: print("Existe, no sobrescribo:", out.name)
            continue
        try:
            m = trimesh.load(p, force="mesh")
            if isinstance(m, trimesh.Scene):
                geos = [g for g in m.dump() if isinstance(g, trimesh.Trimesh)]
                if not geos:
                    if verbose: print("[convex] No convertible:", p.name)
                    continue
                m = trimesh.util.concatenate(geos)
            elif not isinstance(m, trimesh.Trimesh):
                if verbose: print("[convex] No convertible:", p.name)
                continue
            # Limpieza mínima y hull
            m.remove_degenerate_faces()
            m.remove_unreferenced_vertices()
            hull = m.convex_hull
            hull.export(out)
            count += 1
            if verbose: print("OK →", out.name)
        except Exception as ex:
            eprint(f"[warn] Falló convex para {p.name}: {ex}")
    if verbose: print(f"[convex] Generadas: {count}")
    return count

# ---------- SDF BUILD / PLUGINS / REWRITE ----------

def build_sdf_from_urdf(urdf_path: Path, model_name: Optional[str], rewrite_uris: bool) -> ET.Element:
    tree = ET.parse(urdf_path); root = tree.getroot()
    if root.tag != "robot":
        raise RuntimeError("El archivo no parece ser URDF (<robot>).")
    mname = model_name or root.attrib.get("name") or urdf_path.stem

    sdf = ET.Element("sdf", {"version": SDF_VERSION})
    model = ET.SubElement(sdf, "model", {"name": mname})
    ET.SubElement(model, "pose").text = "0 0 0 0 0 0"
    ET.SubElement(model, "static").text = "false"

    for l in root.findall("link"):
        lname = l.attrib.get("name", "link")
        s_link = ET.SubElement(model, "link", {"name": lname})

        inert = l.find("inertial")
        if inert is not None:
            s_inert = ET.SubElement(s_link, "inertial")
            o = inert.find("origin")
            xyz = text_attr(o, "xyz", "0 0 0"); rpy = text_attr(o, "rpy", "0 0 0")
            ET.SubElement(s_inert, "pose").text = join_pose(xyz, rpy)
            mass = inert.find("mass")
            if mass is not None: ET.SubElement(s_inert, "mass").text = text_attr(mass, "value", "0")
            inertia = inert.find("inertia")
            if inertia is not None:
                s_inertia = ET.SubElement(s_inert, "inertia")
                for k in ["ixx","ixy","ixz","iyy","iyz","izz"]:
                    ET.SubElement(s_inertia, k).text = inertia.attrib.get(k, "0")

        for i, vis in enumerate(l.findall("visual")):
            s_vis = ET.SubElement(s_link, "visual", {"name": f"{lname}_visual_{i}"})
            o = vis.find("origin"); xyz = text_attr(o, "xyz", "0 0 0"); rpy = text_attr(o, "rpy", "0 0 0")
            ET.SubElement(s_vis, "pose").text = join_pose(xyz, rpy)
            geom = vis.find("geometry")
            if geom is not None:
                s_geom = ET.SubElement(s_vis, "geometry")
                mesh = geom.find("mesh")
                if mesh is not None:
                    uri = mesh.attrib.get("filename", "")
                    if rewrite_uris: uri = convert_uri_to_model(uri, mname)
                    s_mesh = ET.SubElement(s_geom, "mesh")
                    ET.SubElement(s_mesh, "uri").text = uri
                    if "scale" in mesh.attrib: ET.SubElement(s_mesh, "scale").text = mesh.attrib["scale"]
            mat = vis.find("material")
            if mat is not None:
                color = mat.find("color")
                if color is not None and color.attrib.get("rgba"):
                    rgba = color.attrib["rgba"]
                    s_mat = ET.SubElement(s_vis, "material")
                    ET.SubElement(s_mat, "ambient").text = rgba
                    ET.SubElement(s_mat, "diffuse").text = rgba
                    ET.SubElement(s_mat, "specular").text = "0 0 0 1"
                    ET.SubElement(s_mat, "emissive").text = "0 0 0 1"

        for i, col in enumerate(l.findall("collision")):
            s_col = ET.SubElement(s_link, "collision", {"name": f"{lname}_collision_{i}"})
            o = col.find("origin"); xyz = text_attr(o, "xyz", "0 0 0"); rpy = text_attr(o, "rpy", "0 0 0")
            ET.SubElement(s_col, "pose").text = join_pose(xyz, rpy)
            geom = col.find("geometry")
            if geom is not None:
                s_geom = ET.SubElement(s_col, "geometry")
                mesh = geom.find("mesh")
                if mesh is not None:
                    uri = mesh.attrib.get("filename", "")
                    if rewrite_uris: uri = convert_uri_to_model(uri, mname)
                    s_mesh = ET.SubElement(s_geom, "mesh")
                    ET.SubElement(s_mesh, "uri").text = uri
                    if "scale" in mesh.attrib: ET.SubElement(s_mesh, "scale").text = mesh.attrib["scale"]

    for j in root.findall("joint"):
        jname = j.attrib.get("name", "joint")
        jtype = j.attrib.get("type", "revolute")
        type_map = {"revolute":"revolute","continuous":"revolute","prismatic":"prismatic","fixed":"fixed","planar":"revolute","floating":"ball"}
        sdftype = type_map.get(jtype, "revolute")
        s_joint = ET.SubElement(model, "joint", {"name": jname, "type": sdftype})
        p = j.find("parent"); c = j.find("child")
        if p is not None and "link" in p.attrib: ET.SubElement(s_joint, "parent").text = p.attrib["link"]
        if c is not None and "link" in c.attrib: ET.SubElement(s_joint, "child").text = c.attrib["link"]
        o = j.find("origin"); xyz = text_attr(o, "xyz", "0 0 0"); rpy = text_attr(o, "rpy", "0 0 0")
        ET.SubElement(s_joint, "pose").text = join_pose(xyz, rpy)
        axis = j.find("axis")
        if axis is not None:
            s_axis = ET.SubElement(s_joint, "axis")
            ET.SubElement(s_axis, "xyz").text = axis.attrib.get("xyz", "0 0 1")
            lim = j.find("limit")
            if lim is not None:
                s_lim = ET.SubElement(s_axis, "limit")
                for k in ["lower","upper","effort","velocity"]:
                    if k in lim.attrib: ET.SubElement(s_lim, k).text = lim.attrib[k]
            dyn = j.find("dynamics")
            if dyn is not None:
                s_dyn = ET.SubElement(s_axis, "dynamics")
                if "damping" in dyn.attrib: ET.SubElement(s_dyn, "damping").text = dyn.attrib["damping"]
                if "friction" in dyn.attrib: ET.SubElement(s_dyn, "friction").text = dyn.attrib["friction"]

    return sdf

def inject_position_plugins(model_el: ET.Element, p_gain: str, i_gain: str, d_gain: str, include_fixed: bool):
    for j in model_el.findall("joint"):
        jname = j.attrib.get("name", "joint")
        jtype = j.attrib.get("type", "revolute")
        if jtype == "fixed" and not include_fixed:
            continue
        lower = upper = None
        lim = j.find("axis/limit")
        if lim is not None:
            lower = lim.findtext("lower")
            upper = lim.findtext("upper")
        plugin = ET.SubElement(model_el, "plugin", {
            "filename": "gz-sim-joint-position-controller-system",
            "name": "gz::sim::systems::JointPositionController"
        })
        ET.SubElement(plugin, "joint_name").text = jname
        ET.SubElement(plugin, "p_gain").text = p_gain
        ET.SubElement(plugin, "i_gain").text = i_gain
        ET.SubElement(plugin, "d_gain").text = d_gain
        if lower is not None: ET.SubElement(plugin, "cmd_min").text = lower
        if upper is not None: ET.SubElement(plugin, "cmd_max").text = upper

def rewrite_collision_to_convex(model_el: ET.Element, model_name: str, mesh_root: Path, verbose: bool=False):
    """
    Reescribe URIs de <collision> a mallas convexas si existen.
    - Acepta nombres con prefijo 'col_' o sufijo '_col'.
    - Conserva la subcarpeta original dentro de meshes/ si existe.
    - Conserva la extensión del archivo original.
    """
    def _find_existing(rel_path: Path) -> Path | None:
        candidates = [rel_path,
                      rel_path.with_suffix(rel_path.suffix.lower() or ".stl"),
                      rel_path.with_suffix(rel_path.suffix.upper() or ".STL")]
        for cand in candidates:
            path = (mesh_root / cand).resolve()
            if path.exists():
                return cand
        return None

    token_prefix = f"model://{model_name}/meshes/"
    changed = 0
    for uri_el in model_el.findall(".//collision/geometry/mesh/uri"):
        uri = (uri_el.text or "")
        if token_prefix not in uri:
            continue
        rel = Path(uri.split(token_prefix, 1)[1])
        subdir = rel.parent
        stem = rel.stem
        ext = rel.suffix if rel.suffix else ".stl"

        cands = [
            subdir / f"col_{stem}{ext}",
            subdir / f"{stem}_col{ext}",
            Path(f"col_{stem}{ext}"),
            Path(f"{stem}_col{ext}"),
        ]

        target = None
        for c in cands:
            found = _find_existing(c)
            if found is not None:
                target = found
                break

        if target is not None:
            uri_el.text = f"{token_prefix}{target.as_posix()}"
            changed += 1
            if verbose:
                print(f"[convex] {rel.as_posix()} -> {target.as_posix()}")
        else:
            if verbose:
                print(f"[convex] No hallado col_* para {rel.as_posix()}")

    if verbose:
        print(f"[convex] Reemplazos aplicados: {changed}")

def apply_relative_poses(model_el: ET.Element):
    """
    Ajusta frames para que coincidan con el SDF 'funcional':
    - En cada <joint>, el <pose> queda con attribute relative_to="<parent>".
    - En cada <link> (excepto el base), se añade <pose relative_to="<su_joint">0 0 0 0 0 0</pose> si no existe.
    """
    # Map child link -> joint name
    child_to_joint = {}
    joint_parent = {}
    for j in model_el.findall("joint"):
        name = j.attrib.get("name")
        child = j.findtext("child")
        parent = j.findtext("parent")
        if name and child:
            child_to_joint[child] = name
        if name and parent:
            joint_parent[name] = parent

        # Ensure joint pose exists and set relative_to to its parent link
        pose_el = j.find("pose")
        if pose_el is None:
            pose_el = ET.SubElement(j, "pose")
            pose_el.text = "0 0 0 0 0 0"
        if parent:
            pose_el.set("relative_to", parent)

    # Add link pose relative_to its joint (zero pose), except base (no joint points to it as child)
    for link in model_el.findall("link"):
        lname = link.attrib.get("name")
        if lname in child_to_joint:
            if link.find("pose") is None:
                lpose = ET.Element("pose", {"relative_to": child_to_joint[lname]})
                lpose.text = "0 0 0 0 0 0"
                # insert near top (after <self_collide> if present)
                # find first non-pose element position; if self_collide exists, insert after it
                inserted = False
                for i, child in enumerate(list(link)):
                    if child.tag == "self_collide":
                        link.insert(i + 1, lpose)
                        inserted = True
                        break
                if not inserted:
                    link.insert(0, lpose)

def write_model_config(outdir: Path, model_name: str):
    cfg = f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="{SDF_VERSION}">model.sdf</sdf>
  <author>
    <name>package_to_gzmodel.py</name>
    <email>n/a</email>
  </author>
  <description>Modelo generado a partir de un paquete URDF.</description>
</model>
"""
    (outdir / "model.config").write_text(cfg, encoding="utf-8")

def pretty_xml(elem: ET.Element) -> str:
    rough = ET.tostring(elem, encoding="utf-8")
    try:
        dom = minidom.parseString(rough)
        return dom.toprettyxml(indent="  ")
    except Exception:
        return rough.decode("utf-8")

def main():
    ap = argparse.ArgumentParser(description="Reorganiza paquete (SolidWorks→URDF) a modelo Gazebo (model.sdf + model.config + meshes).")
    ap.add_argument("--src", type=Path, required=True, help="Carpeta del paquete de origen (config/, launch/, materials/, urdf/, etc.)")
    ap.add_argument("--dest", type=Path, default=None, help="Carpeta destino (por defecto, la misma --src)")
    ap.add_argument("--urdf", type=Path, default=None, help="Ruta al URDF (si no se indica, se detecta en src/urdf)")
    ap.add_argument("--model-name", type=str, default=None, help="Nombre del modelo (por defecto: nombre del URDF o carpeta src)")
    ap.add_argument("--add-position-plugins", action="store_true", help="Añadir plugin JointPositionController por joint")
    ap.add_argument("--p-gain", default="10.0"); ap.add_argument("--i-gain", default="0.0"); ap.add_argument("--d-gain", default="0.5")
    ap.add_argument("--plugins-include-fixed", action="store_true", help="Incluir joints fijos")
    ap.add_argument("--use-convex-collision", action="store_true", help="Si existe meshes/col_*.stl o *_col.stl, usarlos en <collision>")
    ap.add_argument("--generate-convex", action="store_true", help="Generar mallas convexas col_*.stl a partir de las mallas existentes")
    ap.add_argument("--convex-overwrite", action="store_true", help="Sobrescribir col_*.stl si ya existen")
    ap.add_argument("--convex-prefix", default="col_", help="Prefijo para mallas convexas (por defecto: col_)")
    ap.add_argument("--convex-suffix", default="", help="Sufijo para mallas convexas (por defecto: vacío)")
    ap.add_argument("--verbose", action="store_true", help="Imprimir detalles de reemplazo y generación")
    args = ap.parse_args()

    src = args.src.resolve()
    if not src.is_dir():
        eprint(f"[error] No existe src: {src}"); sys.exit(2)
    urdf_path = args.urdf.resolve() if args.urdf else detect_urdf(src)
    if not urdf_path or not urdf_path.exists():
        eprint("[error] No encontré URDF. Usa --urdf o coloca uno en src/urdf/*.urdf"); sys.exit(2)

    # model name
    try:
        robot = ET.parse(urdf_path).getroot()
        model_name = args.model_name or robot.attrib.get("name") or src.name
    except Exception:
        model_name = args.model_name or src.name

    dest_root = (args.dest.resolve() if args.dest else src)
    outdir = dest_root / model_name
    outdir.mkdir(parents=True, exist_ok=True)

    # meshes
    mesh_srcs = gather_mesh_sources(src)
    if not mesh_srcs:
        eprint("[warn] No encontré materials/meshes ni meshes en src.")
    copied = copy_mesh_tree(mesh_srcs, outdir / "meshes")
    print(f"[ok] Copiadas {copied} malla(s) a {outdir/'meshes'}")

    # opcional: generar convex
    if args.generate_convex:
        nconv = generate_convex_meshes(outdir / "meshes", prefix=args.convex_prefix, suffix=args.convex_suffix,
                                       overwrite=args.convex_overwrite, verbose=args.verbose)
        if args.verbose:
            print(f"[convex] Generadas (interno o externo): {nconv if nconv>=0 else 'desconocido'}")

    # SDF
    sdf_el = build_sdf_from_urdf(urdf_path, model_name, rewrite_uris=True)
    model_el = sdf_el.find("model")

    # frames: usar poses relativas (como tu SDF funcional)
    apply_relative_poses(model_el)

    # plugins
    if args.add_position_plugins:
        inject_position_plugins(model_el, args.p_gain, args.i_gain, args.d_gain, args.plugins_include_fixed)

    # colisiones convexas
    if args.use_convex_collision:
        rewrite_collision_to_convex(model_el, model_name, outdir / "meshes", verbose=args.verbose)

    # write files
    (outdir / "model.sdf").write_text(pretty_xml(sdf_el), encoding="utf-8")
    write_model_config(outdir, model_name)

    print(f"[ok] Escrito {outdir/'model.sdf'}")
    print(f"[ok] Escrito {outdir/'model.config'}")
    print("\nEstructura final:")
    print(outdir)
    print("├─ meshes/")
    print("├─ model.sdf")
    print("└─ model.config")

if __name__ == "__main__":
    main()
