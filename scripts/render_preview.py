"""Render a 3/4 preview of the three colour bodies from the exported STLs.

A small z-buffer rasteriser (orthographic camera, one directional light), because OpenSCAD's
PNG export needs an OpenGL context that the headless Docker image does not have.

    .venv/bin/python scripts/render_preview.py
"""

from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PARTS = {"body": (22, 24, 27), "light": (241, 239, 232), "accent": (255, 159, 28)}
BACKGROUND = np.array([214, 211, 204])
WIDTH, HEIGHT, SUPERSAMPLE = 1600, 1100, 2
TILT_DEG, TURN_DEG = 52, -18
LIGHT = np.array([-0.35, 0.45, 0.82])


def rotation(tilt, turn):
    t, z = np.radians(tilt), np.radians(turn)
    turn_m = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])
    tilt_m = np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])
    return tilt_m @ turn_m


meshes = {name: trimesh.load(ROOT / "out" / f"card-{name}.stl") for name in PARTS}
centre = meshes["body"].bounds.mean(axis=0)
rot = rotation(-TILT_DEG, TURN_DEG)
light = LIGHT / np.linalg.norm(LIGHT)

w, h = WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE
all_xy = np.vstack([(m.vertices - centre) @ rot.T for m in meshes.values()])[:, :2]
scale = 0.86 * min(w / np.ptp(all_xy[:, 0]), h / np.ptp(all_xy[:, 1]))

depth = np.full((h, w), -np.inf)
image = np.tile(BACKGROUND, (h, w, 1)).astype(float)

for name, colour in PARTS.items():
    mesh = meshes[name]
    tris = (mesh.triangles - centre) @ rot.T
    normals = mesh.face_normals @ rot.T
    shade = 0.35 + 0.65 * np.clip(normals @ light, 0, 1)
    for tri, normal, s in zip(tris, normals, shade):
        if normal[2] <= 0:
            continue  # back face
        sx = tri[:, 0] * scale + w / 2
        sy = h / 2 - tri[:, 1] * scale
        x0, x1 = int(max(np.floor(sx.min()), 0)), int(min(np.ceil(sx.max()), w - 1))
        y0, y1 = int(max(np.floor(sy.min()), 0)), int(min(np.ceil(sy.max()), h - 1))
        if x0 > x1 or y0 > y1:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, bx, cx), (ay, by, cy) = sx, sy
        area = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
        if abs(area) < 1e-9:
            continue
        w0 = ((bx - gx) * (cy - gy) - (cx - gx) * (by - gy)) / area
        w1 = ((cx - gx) * (ay - gy) - (ax - gx) * (cy - gy)) / area
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        z = w0 * tri[0, 2] + w1 * tri[1, 2] + w2 * tri[2, 2]
        region = depth[y0 : y1 + 1, x0 : x1 + 1]
        nearer = inside & (z > region + 1e-4)
        region[nearer] = z[nearer]
        image[y0 : y1 + 1, x0 : x1 + 1][nearer] = np.array(colour) * s

out = ROOT / "preview.png"
Image.fromarray(image.clip(0, 255).astype(np.uint8)).resize((WIDTH, HEIGHT), Image.LANCZOS).save(out)
print(f"wrote {out.relative_to(ROOT)}")
