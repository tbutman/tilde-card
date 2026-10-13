"""Check a 3MF against the Tilde card's print settings: a Customize download from MakerWorld, a
print profile's file, or a project saved from Bambu Studio.

    .venv/bin/python scripts/check_3mf.py ~/Downloads/tilde-card.3mf
    .venv/bin/python scripts/check_3mf.py --nozzle 0.2 card.3mf   # if the 3MF doesn't say

It reads the 3MF (a zip) without extracting it, and reports PASS, WARN or FAIL per setting:
- the wanted values: the presets in bambu/ (paint penetration, infill, Arachne, bottom surface)
  plus the settings that are already right in Bambu's standard processes (PRINTING.md, step 4);
- what applies: an object's own setting (Metadata/model_settings.config; the Parametric Model
  Maker's settings dialog writes there) wins over the project's (Metadata/project_settings.config);
- the pause: the card's thickness says which sticker it was made for, card.scad's nfc_sticker help
  line says which layer (check_pause_docs.py keeps that in line with the model), and
  Metadata/custom_gcode_per_layer.xml must pause there.

Exit status 1 if anything fails. A 3MF without Bambu's settings files (OpenSCAD's own export, for
example) has nothing to check but the pause and the thickness.
"""

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THICKNESS = {1.6: "none", 1.8: "thin", 2.0: "thick"}  # mm, as DESIGN.md gives them
LAYER = {"0.4": 0.2, "0.2": 0.1}
FROM_PRESET = ["top_color_penetration_layers", "bottom_color_penetration_layers", "sparse_infill_density",
               "sparse_infill_pattern", "wall_generator", "bottom_surface_pattern"]
NAMES = {"zig-zag": "Rectilinear", "monotonicline": "Monotonic line", "monotonic": "Monotonic",
         "arachne": "Arachne", "classic": "Classic", "no_brim": "none", "auto_brim": "auto"}


def wanted(nozzle):
    preset = json.loads((ROOT / "bambu" / f"Tilde card {nozzle} mm.json").read_text())
    want = {key: [preset[key]] for key in FROM_PRESET}
    layer = f"{LAYER[nozzle]:g}"
    want.update({
        "layer_height": [layer],
        "initial_layer_print_height": [layer],
        "elefant_foot_compensation": ["0"],
        "top_surface_pattern": ["monotonicline"],
        "enable_support": ["0"],
        "brim_type": ["no_brim", "auto_brim"],  # auto adds no brim to a flat card; none is surer
    })
    return want


def pause_layers():
    """{(nozzle, sticker): layer} from card.scad's nfc_sticker help line."""
    help_line = next(l for l in (ROOT / "card.scad").read_text().splitlines() if l.startswith("// An NFC sticker"))
    m = re.search(r"layer (\d+) \(thin\) or (\d+) \(thick\) on a 0\.4 mm nozzle, (\d+) or (\d+) on 0\.2 mm", help_line)
    return {("0.4", "thin"): int(m[1]), ("0.4", "thick"): int(m[2]), ("0.2", "thin"): int(m[3]), ("0.2", "thick"): int(m[4])}


def first(value):
    return value[0] if isinstance(value, list) else value


def plain(value):
    return value.rstrip("%") if isinstance(value, str) else value


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--nozzle", choices=["0.2", "0.4"], help="if the 3MF doesn't name one")
    args = ap.parse_args()

    results = []  # (status, setting, found, wanted)

    def report(status, setting, found, want=""):
        results.append((status, setting, found, want))

    with zipfile.ZipFile(args.path) as z:
        names = z.namelist()
        project = json.loads(z.read("Metadata/project_settings.config")) if "Metadata/project_settings.config" in names else {}
        objects = {}  # name -> {setting: value}, the object's own settings
        if "Metadata/model_settings.config" in names:
            for obj in ET.fromstring(z.read("Metadata/model_settings.config")).findall("object"):
                meta = {m.get("key"): m.get("value") for m in obj.findall("metadata")}
                objects[meta.get("name", obj.get("id"))] = meta
        models = [z.read(n) for n in names if n.startswith("3D/") and n.endswith(".model")]
        pauses = []
        if "Metadata/custom_gcode_per_layer.xml" in names:
            for layer in ET.fromstring(z.read("Metadata/custom_gcode_per_layer.xml")).iter("layer"):
                if layer.get("type") == "1":  # Bambu's "Pause" (type 1); color changes are type 0
                    pauses.append(float(layer.get("top_z")))

    nozzle = args.nozzle or (f"{float(first(project['nozzle_diameter'])):g}" if "nozzle_diameter" in project else None)
    if nozzle not in LAYER:
        sys.exit(f"Can't tell the nozzle from the 3MF ({nozzle}): pass --nozzle 0.2 or 0.4")
    painted = sum(len(re.findall(rb'paint_color="', m)) for m in models)
    # The z range, not the top: Bambu Studio can store a mesh centered on its origin, with the
    # placement in the build's transform.
    zs = [float(z_) for m in models for z_ in re.findall(rb'<vertex [^>]*z="([-0-9.eE]+)"', m)]
    top = max(zs) - min(zs) if zs else 0
    sticker = THICKNESS.get(round(top, 1))

    print(f"{args.path}")
    print(f"  nozzle {nozzle} mm; card {top:.2f} mm thick ({sticker or 'not a Tilde card thickness'}); "
          f"{painted} painted triangles; process {first(project.get('print_settings_id', '-'))}")
    if objects:
        print(f"  objects: {', '.join(objects)}")

    if project:
        for key, want in wanted(nozzle).items():
            for name, own in (objects or {"": {}}).items():
                value = own.get(key, project.get(key))
                where = "object" if key in own else "project"
                value = first(value) if value is not None else None
                label = f"{key}" + (f" ({name})" if len(objects) > 1 else "")
                found = f"{NAMES.get(value, value)} ({where})" if value is not None else "missing"
                shown = " or ".join(NAMES.get(w, w) for w in want)
                if key.endswith("color_penetration_layers") and not painted:
                    report("PASS", label, f"{found}; no painted colors, so it doesn't apply", shown)
                elif value is not None and plain(value) in [plain(w) for w in want]:
                    status = "WARN" if key == "brim_type" and value != want[0] else "PASS"
                    report(status, label, found, shown)
                else:
                    report("FAIL", label, found, shown)
    else:
        report("WARN", "settings", "no project settings in the 3MF (not saved by Bambu Studio)",
               "pick the Tilde card process after opening it")

    layer_h = LAYER[nozzle]
    if sticker in ("thin", "thick"):
        layer = pause_layers()[(nozzle, sticker)]
        want = f"layer {layer} (top_z {layer * layer_h:.1f} mm)"
        found = ", ".join(f"layer {round(z_ / layer_h)} (top_z {z_:g})" for z_ in pauses) or "none"
        ok = len(pauses) == 1 and abs(pauses[0] - layer * layer_h) < layer_h / 2
        report("PASS" if ok else ("WARN" if not pauses else "FAIL"), "pause", found, want)
    elif sticker == "none":
        report("PASS" if not pauses else "FAIL", "pause", ", ".join(f"top_z {z_:g}" for z_ in pauses) or "none",
               "none (QR code only)")
    else:
        report("WARN", "pause", f"{len(pauses)} pause(s)", "can't tell the sticker from the thickness")

    width = max(len(r[1]) for r in results)
    for status, setting, found, want in results:
        print(f"{status:5} {setting:{width}}  {found}" + (f"  (wanted {want})" if status != "PASS" else ""))
    failed = sum(r[0] == "FAIL" for r in results)
    print(f"{failed} failed, {sum(r[0] == 'WARN' for r in results)} to check" if failed or any(
        r[0] == "WARN" for r in results) else "all right")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
