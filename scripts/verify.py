"""Check the exported STLs, not the source: the QR code decodes and the text strokes are printable.

Every color body must be manifold (each edge shared by exactly two triangles), or the slicer
will flag it for repair. Then it rasterizes each face of the card from the STLs, in print
colors: the front from the top-facing triangles at the top surface, the back from the
bottom-facing triangles at z = 0, flipped so it reads as it will when the card is turned over.

- The QR code on the front must decode with ZXing (the decoder behind many phone scanners) to
  exactly the expected URL, at full resolution, at a low resolution and blurred (closer to what a
  phone camera sees). OpenCV's decoder is reported too, as a second opinion: it misses some valid
  codes (masks 5 and 6 on some data), so it doesn't fail the build.
- Opening each text mask with a `min_stroke` disk (from card.scad) must lose nothing: no stroke is
  thinner than that. Closing it with a `min_gap` disk must fill nothing: no gap inside or between
  letters is narrower than one nozzle line. Acute inner corners (the middle of a "w") always
  fill a sliver; fragments under 0.06 mm^2 are ignored, as for strokes.
  Sharp glyph corners always lose a sliver, so fragments under 0.06 mm^2 are ignored, and
  reviewed pointed tips are listed in KNOWN_THIN_TIPS.

    .venv/bin/python scripts/verify.py --dir out/nozzle-0.2 --min-stroke 0.3 --min-gap 0.22 [expected-url]

build.sh passes the limits card.scad uses for that nozzle.
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import trimesh
import zxingcpp
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument("url", nargs="?", default="https://tbutman.com/hello")
parser.add_argument("--dir", default="out/nozzle-0.2", help="folder holding card-*.stl, relative to the repo")
parser.add_argument("--face-down", choices=["front", "back"], default="front", help="which face the STLs print against the plate")
parser.add_argument("--min-stroke", type=float, default=0.3)
parser.add_argument("--min-gap", type=float, default=0.22)
parser.add_argument("--gaps-advisory", action="store_true", help="report narrow gaps as WARN instead of failing")
args = parser.parse_args()
EXPECTED = args.url
OUT = ROOT / args.dir
PX_PER_MM = 20
# The narrowest printable stroke and gap for this nozzle, as card.scad sets them.
MIN_STROKE_MM = args.min_stroke
MIN_GAP_MM = args.min_gap
CORNER_SLIVER_MM2 = 0.06
OFF_CARD = (255, 0, 255)  # matches no print color
QR_FIELD_X_MM = (38.5, 78.6)  # the QR field's light area; light text sits on either side of it
# Acute inner corners always fill a little when "closed", whatever their size: the gap check
# cannot tell them from a real narrow gap. Each reviewed corner is listed here as (face, x, y) in
# mm; a change to the text moves them and brings the check back. Reviewed 5 October 2026:
KNOWN_ACUTE_CORNERS = [
    ("back", 13.5, 37.8),  # the middle V of the mono "w" in "whoami"; it rounds slightly, still reads as a w
    # The same V with the back tap mark on, which moves the back's text 2.69 mm right (back_shift:
    # qr_right_margin + text_gap - back_x). Shifted, it rasterizes as its two inner corners.
    # Reviewed 7 October 2026:
    ("back", 16.2, 37.8),
    ("back", 16.7, 37.8),
]
# Pointed stroke ends can lose more than a sliver to the stroke check's opening, though the stroke
# itself is wide enough. Each reviewed tip is listed here the same way, matched by position.
# Reviewed 7 October 2026, the Jane Doe sample on the 0.4 mm nozzle (0.5 mm opening):
KNOWN_THIN_TIPS = [
    # The four outer arm tips of the mono "x" in "jane@example.com" on the back: each loses
    # 0.072 mm^2 and prints slightly blunt; the x still reads as an x.
    ("back", 24.3, 20.2),
    ("back", 26.7, 20.2),
    ("back", 24.2, 17.5),
    ("back", 26.8, 17.5),
    # The same tips with the back tap mark on, 2.69 mm right. Reviewed 7 October 2026:
    ("back", 27.0, 20.2),
    ("back", 29.4, 20.2),
    ("back", 26.9, 17.5),
    ("back", 29.5, 17.5),
]
PARTS = {  # print colors: black PLA, white PLA, orange PLA
    "body": (22, 24, 27),
    "light": (241, 239, 232),
    "accent": (255, 159, 28),
    "chrome": (142, 144, 137),  # gray PLA: the back's window bar
}


def surface_raster(meshes, face, px_per_mm=PX_PER_MM):
    """The STLs' "top" or "bottom" face in print colors, drawn as seen from above."""
    lo = min(mesh.bounds[0][2] for mesh in meshes.values())
    hi = max(mesh.bounds[1][2] for mesh in meshes.values())
    z, sign = (hi, 1) if face == "top" else (lo, -1)
    width_mm, height_mm = meshes["body"].extents[:2]
    image = Image.new("RGB", (round(width_mm * px_per_mm), round(height_mm * px_per_mm)), OFF_CARD)
    draw = ImageDraw.Draw(image)
    for name, colour in PARTS.items():
        if name not in meshes:
            continue
        mesh = meshes[name]
        facing = (sign * mesh.face_normals[:, 2] > 0.99) & (np.abs(mesh.triangles[:, :, 2] - z).max(axis=1) < 1e-3)
        for triangle in mesh.triangles[facing]:
            # Image rows run top to bottom; model y runs bottom to top.
            draw.polygon([(x * px_per_mm, (height_mm - y) * px_per_mm) for x, y, _ in triangle], fill=colour)
    return image


def faces(meshes, face_down):
    """(front, back) as a person holds the card: the back as seen after turning it over sideways.

    Printed back-down, the STLs are the model as designed. Printed front-down, they are turned over
    about the card's long axis, so the front is the bottom face upside down.
    """
    top, bottom = surface_raster(meshes, "top"), surface_raster(meshes, "bottom")
    if face_down == "back":
        return top, ImageOps.mirror(bottom)
    return ImageOps.flip(bottom), ImageOps.flip(ImageOps.mirror(top))


def decode(image_rgb):
    gray = cv2.cvtColor(np.asarray(image_rgb), cv2.COLOR_RGB2GRAY)
    found = zxingcpp.read_barcodes(gray, formats=zxingcpp.BarcodeFormat.QRCode)
    return found[0].text if found else ""


def decode_opencv(image_rgb):
    gray = cv2.cvtColor(np.asarray(image_rgb), cv2.COLOR_RGB2GRAY)
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(gray)
    return text


def thin_strokes(image, colour, skip_x_mm=None, gaps=False, px_per_mm=PX_PER_MM):
    """Places where `colour` is thinner than MIN_STROKE_MM, as (x, y, area) in mm. With `gaps`, the
    places where the black between parts of `colour` (inside an "e", between waves) is."""
    rgb = np.asarray(image).astype(int)
    mask = (np.abs(rgb - colour).max(axis=2) < 40).astype(np.uint8)
    if skip_x_mm is not None:
        mask[:, round(skip_x_mm[0] * px_per_mm) : round(skip_x_mm[1] * px_per_mm)] = 0
    r = round((MIN_GAP_MM if gaps else MIN_STROKE_MM) * px_per_mm / 2)
    disk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    if gaps:
        lost = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, disk) & (1 - mask)
    else:
        lost = mask & (1 - cv2.morphologyEx(mask, cv2.MORPH_OPEN, disk))
    _, _, stats, centres = cv2.connectedComponentsWithStats(lost)
    height = mask.shape[0]
    return [
        (round(cx / px_per_mm, 1), round((height - cy) / px_per_mm, 1), round(area / px_per_mm**2, 3))
        for (*_, area), (cx, cy) in zip(stats[1:], centres[1:])
        if area / px_per_mm**2 >= CORNER_SLIVER_MM2
    ]


def report(ok, label, detail="", advisory=False):
    print(f"{'PASS' if ok else 'WARN' if advisory else 'FAIL'}  {label}" + (f": {detail}" if detail else ""))
    return not ok and not advisory


# A part with nothing in it (no window bar on a plain or blank back) has no file.
meshes = {name: trimesh.load(OUT / f"card-{name}.stl") for name in PARTS if (OUT / f"card-{name}.stl").exists()}
failed = False
for name, mesh in meshes.items():
    _, counts = np.unique(np.sort(mesh.edges, axis=1), axis=0, return_counts=True)
    bad = int((counts != 2).sum())
    failed |= report(not bad, f"card-{name}.stl manifold", f"{bad} bad edges" if bad else "")

front, back = faces(meshes, args.face_down)
def save(image, name):
    """Saves with the off-card background transparent, so the rounded corners show cleanly."""
    rgba = np.dstack([np.asarray(image), np.full(image.size[::-1], 255, np.uint8)])
    rgba[(rgba[:, :, :3] == OFF_CARD).all(axis=2), 3] = 0
    Image.fromarray(rgba).save(OUT / name)


save(front, "card-top-surface.png")
save(back, "card-back-surface.png")

for label, img in {
    "front QR, 20 px/mm": front,
    "front QR, 4 px/mm": front.resize((front.width // 5, front.height // 5), Image.LANCZOS),
    "front QR, blurred": Image.fromarray(cv2.GaussianBlur(np.asarray(front), (0, 0), 6)),
}.items():
    text = decode(img)
    failed |= report(text == EXPECTED, label, f"decoded {text!r}")
    second = decode_opencv(img)
    report(second == EXPECTED, f"{label} (OpenCV, second opinion)", f"decoded {second!r}", advisory=True)

def unreviewed(spots, face, reviewed):
    return [s for s in spots if not any(f == face and abs(s[0] - x) < 0.3 and abs(s[1] - y) < 0.3 for f, x, y in reviewed)]


for label, img, colour, skip_x in [
    ("front light text", front, PARTS["light"], QR_FIELD_X_MM),
    ("front accent text", front, PARTS["accent"], None),
    ("front chrome", front, PARTS["chrome"], None),  # only the tap mark, when it takes the window bar color
    ("back light text", back, PARTS["light"], None),
    ("back accent text", back, PARTS["accent"], None),
    ("back window bar", back, PARTS["chrome"], None),
]:
    thin = unreviewed(thin_strokes(img, colour, skip_x), label.split()[0], KNOWN_THIN_TIPS)
    failed |= report(not thin, f"{label} strokes >= {MIN_STROKE_MM} mm", f"thin at {thin}" if thin else "")
    narrow = unreviewed(thin_strokes(img, colour, skip_x, gaps=True), label.split()[0], KNOWN_ACUTE_CORNERS)
    detail = f"{len(narrow)} narrow spots, e.g. {narrow[:3]}" if narrow else ""
    failed |= report(not narrow, f"{label} gaps >= {MIN_GAP_MM} mm", detail, advisory=args.gaps_advisory)

print(f"wrote {args.dir}/card-top-surface.png, {args.dir}/card-back-surface.png")
sys.exit(1 if failed else 0)
