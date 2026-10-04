"""Check the exported STLs, not the source: the QR code decodes and the text strokes are printable.

Every colour body must be manifold (each edge shared by exactly two triangles), or the slicer
will flag it for repair. Then it rasterises each face of the card from the STLs, in print
colours: the front from the top-facing triangles at the top surface, the back from the
bottom-facing triangles at z = 0, flipped so it reads as it will when the card is turned over.

- The QR code on the front must decode with OpenCV to exactly the expected URL, at full
  resolution, at a low resolution and blurred (closer to what a phone camera sees).
- Opening each text mask with a 0.5 mm disk must lose nothing: no stroke is thinner than that.
  Sharp glyph corners always lose a sliver, so fragments under 0.06 mm^2 are ignored.

    .venv/bin/python scripts/verify.py [expected-url]
"""

import sys
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = sys.argv[1] if len(sys.argv) > 1 else "https://tbutman.com/hello"
PX_PER_MM = 20
MIN_STROKE_MM = 0.5
CORNER_SLIVER_MM2 = 0.06
OFF_CARD = (255, 0, 255)  # matches no print colour
QR_FIELD_X_MM = 38.0  # the front's light text is left of the QR field
PARTS = {  # print colours: black PLA, white PLA, orange PLA
    "body": (22, 24, 27),
    "light": (241, 239, 232),
    "accent": (255, 159, 28),
    "chrome": (142, 144, 137),  # gray PLA: the back's window bar
}


def surface_image(meshes, face, px_per_mm=PX_PER_MM):
    """The card's front ("top") or back ("bottom", as seen from behind) in print colours."""
    lo = min(mesh.bounds[0][2] for mesh in meshes.values())
    hi = max(mesh.bounds[1][2] for mesh in meshes.values())
    z, sign = (hi, 1) if face == "top" else (lo, -1)
    width_mm, height_mm = meshes["body"].extents[:2]
    image = Image.new("RGB", (round(width_mm * px_per_mm), round(height_mm * px_per_mm)), OFF_CARD)
    draw = ImageDraw.Draw(image)
    for name, colour in PARTS.items():
        mesh = meshes[name]
        facing = (sign * mesh.face_normals[:, 2] > 0.99) & (np.abs(mesh.triangles[:, :, 2] - z).max(axis=1) < 1e-3)
        for triangle in mesh.triangles[facing]:
            # Image rows run top to bottom; model y runs bottom to top.
            draw.polygon([(x * px_per_mm, (height_mm - y) * px_per_mm) for x, y, _ in triangle], fill=colour)
    return image if face == "top" else ImageOps.mirror(image)


def decode(image_rgb):
    gray = cv2.cvtColor(np.asarray(image_rgb), cv2.COLOR_RGB2GRAY)
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(gray)
    return text


def thin_strokes(image, colour, max_x_mm=None, px_per_mm=PX_PER_MM):
    """Places where `colour` is thinner than MIN_STROKE_MM, as (x, y, area) in mm."""
    rgb = np.asarray(image).astype(int)
    mask = (np.abs(rgb - colour).max(axis=2) < 40).astype(np.uint8)
    if max_x_mm is not None:
        mask[:, round(max_x_mm * px_per_mm) :] = 0
    r = round(MIN_STROKE_MM * px_per_mm / 2)
    disk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
    lost = mask & (1 - cv2.morphologyEx(mask, cv2.MORPH_OPEN, disk))
    _, _, stats, centres = cv2.connectedComponentsWithStats(lost)
    height = mask.shape[0]
    return [
        (round(cx / px_per_mm, 1), round((height - cy) / px_per_mm, 1), round(area / px_per_mm**2, 3))
        for (*_, area), (cx, cy) in zip(stats[1:], centres[1:])
        if area / px_per_mm**2 >= CORNER_SLIVER_MM2
    ]


def report(ok, label, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {label}" + (f": {detail}" if detail else ""))
    return not ok


meshes = {name: trimesh.load(ROOT / "out" / f"card-{name}.stl") for name in PARTS}
failed = False
for name, mesh in meshes.items():
    _, counts = np.unique(np.sort(mesh.edges, axis=1), axis=0, return_counts=True)
    bad = int((counts != 2).sum())
    failed |= report(not bad, f"card-{name}.stl manifold", f"{bad} bad edges" if bad else "")

front = surface_image(meshes, "top")
back = surface_image(meshes, "bottom")
def save(image, name):
    """Saves with the off-card background transparent, so the rounded corners show cleanly."""
    rgba = np.dstack([np.asarray(image), np.full(image.size[::-1], 255, np.uint8)])
    rgba[(rgba[:, :, :3] == OFF_CARD).all(axis=2), 3] = 0
    Image.fromarray(rgba).save(ROOT / "out" / name)


save(front, "card-top-surface.png")
save(back, "card-back-surface.png")

for label, img in {
    "front QR, 20 px/mm": front,
    "front QR, 4 px/mm": front.resize((front.width // 5, front.height // 5), Image.LANCZOS),
    "front QR, blurred": Image.fromarray(cv2.GaussianBlur(np.asarray(front), (0, 0), 6)),
}.items():
    text = decode(img)
    failed |= report(text == EXPECTED, label, f"decoded {text!r}")

for label, img, colour, max_x in [
    ("front light text", front, PARTS["light"], QR_FIELD_X_MM),
    ("front accent text", front, PARTS["accent"], None),
    ("back light text", back, PARTS["light"], None),
    ("back accent text", back, PARTS["accent"], None),
    ("back window bar", back, PARTS["chrome"], None),
]:
    thin = thin_strokes(img, colour, max_x)
    failed |= report(not thin, f"{label} strokes >= {MIN_STROKE_MM} mm", f"thin at {thin}" if thin else "")

print("wrote out/card-top-surface.png, out/card-back-surface.png")
sys.exit(1 if failed else 0)
