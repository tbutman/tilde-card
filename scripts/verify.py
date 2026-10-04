"""Check the exported STLs, not the source: the QR code decodes and the text strokes are printable.

Every colour body must be manifold (each edge shared by exactly two triangles), or the slicer
will flag it for repair. Then it rasterises the top-facing triangles of each colour body at the card's top surface into a
top-down image in its print colour, then:

- decodes the QR code with OpenCV at full resolution, at a low resolution and blurred (closer
  to what a phone camera sees), and requires exactly the expected URL each time;
- opens the text masks with a 0.5 mm disk and fails if any stroke thinner than that is lost.
  Sharp glyph corners always lose a sliver, so fragments under 0.06 mm^2 are ignored.

    .venv/bin/python scripts/verify.py [expected-url]
"""

import sys
from pathlib import Path

import cv2
import numpy as np
import trimesh
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
EXPECTED = sys.argv[1] if len(sys.argv) > 1 else "https://tbutman.com/hello"
PX_PER_MM = 20
MIN_STROKE_MM = 0.5
CORNER_SLIVER_MM2 = 0.06
PARTS = {  # print colours: black PLA, white PLA, orange PLA
    "body": (22, 24, 27),
    "light": (241, 239, 232),
    "accent": (255, 159, 28),
}


def top_surface_image(px_per_mm=PX_PER_MM):
    meshes = {name: trimesh.load(ROOT / "out" / f"card-{name}.stl") for name in PARTS}
    top_z = max(mesh.bounds[1][2] for mesh in meshes.values())
    width_mm, height_mm = meshes["body"].extents[:2]
    size = (round(width_mm * px_per_mm), round(height_mm * px_per_mm))
    image = Image.new("RGB", size, (128, 128, 128))  # matches no print colour
    draw = ImageDraw.Draw(image)
    for name, colour in PARTS.items():
        mesh = meshes[name]
        up = (mesh.face_normals[:, 2] > 0.99) & (np.abs(mesh.triangles[:, :, 2] - top_z).max(axis=1) < 1e-3)
        for triangle in mesh.triangles[up]:
            # Image rows run top to bottom; model y runs bottom to top.
            points = [(x * px_per_mm, (height_mm - y) * px_per_mm) for x, y, _ in triangle]
            draw.polygon(points, fill=colour)
    return image


def decode(image_rgb):
    gray = cv2.cvtColor(np.asarray(image_rgb), cv2.COLOR_RGB2GRAY)
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(gray)
    return text


failed = False
for name in PARTS:
    mesh = trimesh.load(ROOT / "out" / f"card-{name}.stl")
    _, counts = np.unique(np.sort(mesh.edges, axis=1), axis=0, return_counts=True)
    bad = int((counts != 2).sum())
    failed |= bad > 0
    print(f"{'PASS' if not bad else 'FAIL'}  card-{name}.stl manifold" + (f": {bad} bad edges" if bad else ""))

image = top_surface_image()
out = ROOT / "out" / "card-top-surface.png"
image.save(out)

checks = {
    "top surface, 20 px/mm": image,
    "top surface, 4 px/mm": image.resize((image.width // 5, image.height // 5), Image.LANCZOS),
    "top surface, blurred": Image.fromarray(cv2.GaussianBlur(np.asarray(image), (0, 0), 6)),
}
def thin_strokes(image, colour, max_x_mm=None, px_per_mm=PX_PER_MM):
    """Places where `colour` is thinner than MIN_STROKE_MM, as (x, y, area) in mm."""
    rgb = np.asarray(image).astype(int)
    mask = (np.abs(rgb - colour).max(axis=2) < 40).astype(np.uint8)
    if max_x_mm is not None:
        mask[:, round(max_x_mm * px_per_mm):] = 0
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


for label, img in checks.items():
    text = decode(img)
    ok = text == EXPECTED
    failed |= not ok
    print(f"{'PASS' if ok else 'FAIL'}  {label}: decoded {text!r}")
# The name is the light colour left of the QR field; the accent colour is all text.
field_x_mm = 38.0
for label, colour, max_x in [("name", PARTS["light"], field_x_mm), ("accent text", PARTS["accent"], None)]:
    thin = thin_strokes(image, colour, max_x)
    failed |= bool(thin)
    print(f"{'PASS' if not thin else 'FAIL'}  {label} strokes >= {MIN_STROKE_MM} mm" + (f": thin at {thin}" if thin else ""))
print(f"wrote {out.relative_to(ROOT)}")
sys.exit(1 if failed else 0)
