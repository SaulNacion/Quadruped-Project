# `package_to_gzmodel.py` — turn a SolidWorks→URDF export into a clean Gazebo model

This script takes a SolidWorks **URDF package** (the typical export with `urdf/`, `materials/meshes/`, etc.) and produces a **self‑contained Gazebo model** you can drop into your model path.

## What it does (at a glance)
- **Discovers the URDF** in `src/urdf/*.urdf` (you can also pass `--urdf`).
- **Converts URDF → SDF** in pure Python (no `gz/ign` calls) while **preserving numeric strings** (e.g., scientific notation) from the URDF.
- **Rewrites mesh URIs** to `model://<ModelName>/...` so the model is portable.
- **Copies meshes** from `materials/meshes/` (or `meshes/`) to `<dest>/<ModelName>/meshes/`.
- **Optionally generates convex collision meshes** (e.g., `col_Link_1.stl`) and **uses them for `<collision>`**.
- **Optionally injects per‑joint position‑controller plugins** (GZ Sim JointPositionController).
- Writes **`model.sdf` (SDF 1.11)** and **`model.config`** in the new model folder.
- Sets **relative frames** like this:
  - each `joint` has `<pose relative_to='<parent link>'>…</pose>`
  - each non‑base `link` has `<pose relative_to='<its joint>'>0 0 0 0 0 0</pose>`  
  This mirrors a common “functional” frame layout and fixes frequent misalignment issues.

---

## Why simplified / convex STL for collisions?
Physics engines are **much faster and more stable** when collision geometry is **simple and convex**. Using the original CAD STL for collisions often yields:
- excessive contact points / slow collision checks,
- tunneling or instability due to thin features,
- long load times.

Best practice: **keep rich meshes for `<visual>`**, and use **simplified, convex meshes for `<collision>`** (e.g., `col_*`). The script can generate these convex meshes for you and switch the `<collision>` URIs to the convex versions.

---

## Requirements
- **Python 3.8+**
- **`trimesh`** (and a recent `scipy`) if you want the script to **generate** convex meshes:
  ```bash
  # conda
  conda install -c conda-forge trimesh scipy

  # or pip
  pip install trimesh scipy
  ```
- (Optional fallback) If `trimesh` is unavailable, the script tries to run a local **`make_convex_collision.py`** placed next to `package_to_gzmodel.py`.

> You do **not** need Gazebo/GZ tools for the conversion—the script writes SDF directly.

---

## Input → Output

**Input** (your export folder, passed via `--src`):
```
Pata_URDF/
├─ urdf/               # SolidWorks exporter
├─ materials/meshes/   # or meshes/
└─ ... (other folders from the export)
```

**Output** (final model folder):
```
<dest>/<ModelName>/
├─ meshes/             # copied from the source
├─ model.sdf           # SDF 1.11, portable URIs, relative frames
└─ model.config
```

- The script picks `<ModelName>` from the URDF’s `<robot name="...">` (or `--model-name`), and writes all URIs as `model://<ModelName>/...`.
- SDF uses **relative frames** (`relative_to`) to match a working layout out‑of‑the‑box.

> **Units:** the script **preserves** any `<scale>` already in your URDF meshes. It does **not** auto‑scale from mm to m. If your STL units are mm, export in meters or add `<scale>0.001 0.001 0.001</scale>` in URDF/visual/collision—or extend the script to inject a scale of your choice.

---

## Quick start

Minimal pack:
```bash
python package_to_gzmodel.py --src ./Pata_URDF
```

Generate convex meshes **and** use them for collisions, plus the joint controller plugins:
```bash
python package_to_gzmodel.py --src ./Pata_URDF   --generate-convex --use-convex-collision   --add-position-plugins --verbose
```

Send the model to a different destination (e.g., your model path):
```bash
python package_to_gzmodel.py --src ./Pata_URDF   --dest ~/gazebo_models
```

Pass an explicit URDF path and custom model name:
```bash
python package_to_gzmodel.py --src ./Pata_URDF   --urdf ./Pata_URDF/urdf/Pata_URDF.urdf   --model-name Pata_URDF
```

Tune controller gains for all joints:
```bash
python package_to_gzmodel.py --src ./Pata_URDF   --add-position-plugins   --p-gain 12.0 --i-gain 0.1 --d-gain 0.4
```

Overwrite existing convex meshes and set a different naming pattern:
```bash
python package_to_gzmodel.py --src ./Pata_URDF   --generate-convex --convex-overwrite   --convex-prefix col_ --convex-suffix ""
```

---

## Options (most used)

- `--src DIR`  
  Source folder (your SolidWorks→URDF export). **Required**.

- `--dest DIR`  
  Destination root for the final model folder. Default: `--src`.

- `--urdf FILE`  
  URDF file to convert (auto‑discovered in `src/urdf/*.urdf` if omitted).

- `--model-name NAME`  
  Name of the model folder and SDF `<model name>`. Default: robot name or `src` folder name.

- `--generate-convex`  
  Build convex meshes for each STL in `meshes/`. Produces `col_<stem>.stl` (same extension casing as the source). Uses `trimesh` when available.

- `--convex-overwrite`  
  Overwrite already existing `col_*` files.

- `--convex-prefix/--convex-suffix`  
  Customize the naming for convex meshes. Defaults: `col_` prefix, empty suffix.

- `--use-convex-collision`  
  Switch `<collision>` URIs to the convex meshes. Looks for `col_<stem>.stl` or `<stem>_col.stl`, prioritizing the same subfolder as the original.

- `--add-position-plugins`  
  Add one **JointPositionController** plugin per (non‑fixed) joint. Gains via `--p-gain`, `--i-gain`, `--d-gain`.

- `--plugins-include-fixed`  
  Also add a controller plugin for fixed joints (off by default).

- `--verbose`  
  Print extra details (convex generation and replacements).

---

## How the frames are set
- **Joints** get `<pose relative_to='<parent link>'> … </pose>` copied from the URDF origin (rpy/xyz).  
- **Links** (except the base link) get `<pose relative_to='<their joint>'>0 0 0 0 0 0</pose>`.  
This makes the tree easy to reason about and typically **fixes misalignment** issues found when all poses were interpreted in the model frame.

> If your joint axes differ (e.g., `-1 0 0` vs `0 0 -1`), that affects rotation, not placement. You can change axes in URDF or extend the script to normalize axes systematically.

---

## Troubleshooting

- **`[warn] Could not import 'trimesh'...`**  
  Install `trimesh` (and `scipy`), or place a `make_convex_collision.py` next to the script. Then re‑run with `--generate-convex`.

- **“Generated: 0” when using `--generate-convex`**  
  Check that your files are really `*.stl`/`*.STL` under the copied `meshes/` folder. The script preserves extension case (e.g., `Link_1.STL` → `col_Link_1.STL`).

- **No replacements applied with `--use-convex-collision`**  
  Ensure the convex files exist (`col_*` or `*_col`) in the **same subfolder** as the original mesh (or at the mesh root). Use `--verbose` to see attempts.

- **Wrong scale or units**  
  Export meshes in meters or add `<scale>` in URDF. The script preserves pre‑existing scales; it does not auto‑convert from mm to m.

---

## Limitations & ideas
- No automatic mm→m scaling (can be added as a flag if needed).
- Axis normalization (e.g., force `0 0 1`) is not automatic—left to the URDF source.
- Material/texture nuances are kept simple (ambient/diffuse from URDF color).


