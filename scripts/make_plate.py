"""Build a full plate of cards for a batch (the Web Summit samples, for example): one STL per color,
each holding three cards in a column, so the four files load in Bambu Studio as one object that
fills an A1 mini's plate with room on the right for the prime tower.

    .venv/bin/python scripts/make_plate.py                 # the sample card, thin sticker, 0.4 mm
    .venv/bin/python scripts/make_plate.py --sticker none  # QR code only: no pause, no stickers

The thin- and thick-sticker cards come from out/nozzle-*/ (run build.sh first); a QR-only card is
built here with OpenSCAD in Docker, like build.sh does. The plate goes to out/plates/ (git-ignored).
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parent.parent
PARTS = ["body", "light", "accent", "chrome"]
BED = 180.0  # the A1 mini's plate, mm
GAP = 5.0    # between cards


def build_qr_only(nozzle, out_dir):
    """The QR-only card isn't in out/, so build its parts and check them the way build.sh does."""
    log = ""
    for part in PARTS:
        cmd = ["docker", "run", "--rm", "-v", f"{ROOT}:/w", "-w", "/w", "openscad/openscad:dev",
               "openscad", "--backend=manifold", "-D", f"nozzle={nozzle}", "-D", 'nfc_sticker="none"',
               "-D", f'part="{part}"', "--export-format", "binstl",
               "-o", f"/w/{out_dir.relative_to(ROOT)}/card-{part}.stl", "card.scad"]
        log += subprocess.run(cmd, check=True, capture_output=True, text=True).stderr
    limits = dict(re.findall(r"(\w+)=(\S+?)[ \"]", re.search(r"PRINTER .*", log).group(0) + " "))
    link = re.search(r'^qr_code_link = "(.*)";', (ROOT / "card.scad").read_text(), re.M).group(1)
    cmd = [sys.executable, str(ROOT / "scripts" / "verify.py"), "--dir", str(out_dir.relative_to(ROOT)),
           "--face-down", limits["face_down"], "--min-stroke", limits["min_stroke"], "--min-gap", limits["min_gap"]]
    if limits["strict_gaps"] == "false":
        cmd.append("--gaps-advisory")
    if subprocess.run(cmd + [link], cwd=ROOT, capture_output=True, text=True).returncode:
        sys.exit(f"verify.py failed on {out_dir.relative_to(ROOT)}: run it there to see why")


def pause_layer(nozzle, sticker):
    """The pause layer, as card.scad echoes it while rendering the (small) chrome part."""
    cmd = ["docker", "run", "--rm", "-v", f"{ROOT}:/w", "-w", "/w", "openscad/openscad:dev",
           "openscad", "--backend=manifold", "-D", f"nozzle={nozzle}", "-D", f'nfc_sticker="{sticker}"',
           "-D", 'part="chrome"', "--export-format", "binstl", "-o", "/dev/null", "card.scad"]
    log = subprocess.run(cmd, check=True, capture_output=True, text=True).stderr
    match = re.search(r"pause before layer (\d+)", log)
    return match and int(match.group(1))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nozzle", default="0.4", choices=["0.2", "0.4"])
    ap.add_argument("--sticker", default="thin", choices=["thin", "thick", "none"])
    ap.add_argument("--copies", type=int, default=3)
    args = ap.parse_args()

    name = f"nozzle-{args.nozzle}" + {"thin": "", "thick": "-thick-sticker", "none": "-qr-only"}[args.sticker]
    out = ROOT / "out" / "plates" / f"{name}-x{args.copies}"
    out.mkdir(parents=True, exist_ok=True)
    if args.sticker == "none":
        src = out / "card"
        src.mkdir(exist_ok=True)
        print(f"building the QR-only card ({args.nozzle} mm nozzle) ...")
        build_qr_only(args.nozzle, src)
    else:
        src = ROOT / "out" / name
    if not all((src / f"card-{p}.stl").exists() for p in PARTS):
        sys.exit(f"{src} has no card STLs: run ./build.sh {args.nozzle} first")

    meshes = {p: trimesh.load(src / f"card-{p}.stl") for p in PARTS}
    lo, hi = trimesh.util.concatenate(list(meshes.values())).bounds[:, :2]
    size = hi - lo
    column = args.copies * size[1] + (args.copies - 1) * GAP
    if column > BED or size[0] > BED / 2:
        sys.exit(f"{args.copies} cards make a column {column:.1f} mm tall: more than the {BED:.0f} mm plate")
    for p, mesh in meshes.items():
        copies = []
        for i in range(args.copies):
            copy = mesh.copy()
            copy.apply_translation([-lo[0], -lo[1] + i * (size[1] + GAP), 0])
            copies.append(copy)
        trimesh.util.concatenate(copies).export(out / f"card-{p}.stl")

    print(f"wrote {out.relative_to(ROOT)}/card-{{{','.join(PARTS)}}}.stl: {args.copies} cards, "
          f"{size[0]:.1f} x {column:.1f} mm")
    if args.sticker != "none":
        print(f"pause before layer {pause_layer(args.nozzle, args.sticker)} "
              f"({args.copies} stickers per plate)")
    else:
        print("no pause: QR code only")


if __name__ == "__main__":
    main()
