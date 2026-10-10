"""Render a 3/4 preview of the three color bodies from the exported STLs.

A small z-buffer rasterizer (orthographic camera, one directional light), because OpenSCAD's
PNG export needs an OpenGL context that the headless Docker image does not have.

    .venv/bin/python scripts/render_preview.py --dir out/nozzle-0.2   # writes <dir>/preview.png
"""

import argparse
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PARTS = {"body": (22, 24, 27), "light": (241, 239, 232), "accent": (255, 159, 28), "chrome": (142, 144, 137)}
BACKGROUND = np.array([214, 211, 204])
WIDTH, HEIGHT, SUPERSAMPLE = 1600, 1100, 2
TILT_DEG, TURN_DEG = 52, -18
LIGHT = np.array([-0.35, 0.45, 0.82])


def rotation(tilt, turn):
    t, z = np.radians(tilt), np.radians(turn)
    turn_m = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])
    tilt_m = np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])
    return tilt_m @ turn_m


def load_parts(folder, face_down="front", show="front"):
    """The card's color bodies from `folder`'s card-*.stl, turned so `show` faces the camera."""
    # A part with nothing in it (no window bar on a plain or blank back) has no file.
    meshes = {name: trimesh.load(folder / f"card-{name}.stl") for name in PARTS if (folder / f"card-{name}.stl").exists()}
    if face_down == show:
        # The STLs lie with that face down for printing; turn them over (about the long axis).
        for mesh in meshes.values():
            mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))  # the view centers itself
    return meshes


def projector(meshes, size=(WIDTH, HEIGHT), centre=None, fill=0.86):
    """The view `render` uses: a function from model points (n x 3) to supersampled pixels
    (n x 3: x, y and depth), plus the rotation it applies. By default the view centers on the
    body and fills 86% of the frame."""
    if centre is None:
        centre = meshes["body"].bounds.mean(axis=0)
    rot = rotation(-TILT_DEG, TURN_DEG)
    w, h = size[0] * SUPERSAMPLE, size[1] * SUPERSAMPLE
    all_xy = np.vstack([(m.vertices - centre) @ rot.T for m in meshes.values()])[:, :2]
    scale = fill * min(w / np.ptp(all_xy[:, 0]), h / np.ptp(all_xy[:, 1]))

    def project(points):
        p = (np.asarray(points, float) - centre) @ rot.T
        return np.column_stack([p[:, 0] * scale + w / 2, h / 2 - p[:, 1] * scale, p[:, 2]])

    return project, rot


def render(meshes, colors=PARTS, size=(WIDTH, HEIGHT), view=None, background=BACKGROUND, local=None, texture=None):
    """Shade `meshes` ({part: mesh}, drawn in `colors`, which may name extra parts). Returns the
    image and the coverage (True where the card is), both at supersampled size. `view` is a
    projector(); by default, projector(meshes, size).

    Optional surface texture: `local` holds the same meshes before they were moved (same
    triangles, same order), and texture(part, points, normal) returns a brightness factor for
    each of the points (n x 3, in `local`'s frame) on a face with that local normal."""
    project, rot = view or projector(meshes, size)
    light = LIGHT / np.linalg.norm(LIGHT)
    w, h = size[0] * SUPERSAMPLE, size[1] * SUPERSAMPLE

    depth = np.full((h, w), -np.inf)
    image = np.tile(np.asarray(background), (h, w, 1)).astype(float)

    for name, mesh in meshes.items():
        color = colors[name]
        tris = project(mesh.triangles.reshape(-1, 3)).reshape(-1, 3, 3)
        normals = mesh.face_normals @ rot.T
        shade = 0.35 + 0.65 * np.clip(normals @ light, 0, 1)
        textured = texture is not None and local is not None and name in local
        local_tris = local[name].triangles if textured else [None] * len(tris)
        local_normals = local[name].face_normals if textured else [None] * len(tris)
        for tri, normal, s, ltri, lnormal in zip(tris, normals, shade, local_tris, local_normals):
            if normal[2] <= 0:
                continue  # back face
            sx, sy = tri[:, 0], tri[:, 1]
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
            if textured and nearer.any():
                points = w0[nearer, None] * ltri[0] + w1[nearer, None] * ltri[1] + w2[nearer, None] * ltri[2]
                factor = texture(name, points, lnormal)
                image[y0 : y1 + 1, x0 : x1 + 1][nearer] = np.array(color) * s * np.asarray(factor).reshape(-1, 1)
            else:
                image[y0 : y1 + 1, x0 : x1 + 1][nearer] = np.array(color) * s
    return image, depth > -np.inf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="out/nozzle-0.2", help="folder holding card-*.stl, relative to the repo")
    parser.add_argument("--face-down", choices=["front", "back"], default="front", help="which face the STLs print against the plate")
    parser.add_argument("--transparent", metavar="PNG", help="also write a copy with a transparent background, for web pages")
    args = parser.parse_args()
    image, covered = render(load_parts(ROOT / args.dir, args.face_down))
    out = ROOT / args.dir / "preview.png"
    Image.fromarray(image.clip(0, 255).astype(np.uint8)).resize((WIDTH, HEIGHT), Image.LANCZOS).save(out)
    print(f"wrote {out.relative_to(ROOT)}")

    if args.transparent:
        # Scale color premultiplied by coverage, then divide it back out, so the edges carry no
        # trace of the background color.
        alpha = Image.fromarray((covered * 255).astype(np.uint8)).resize((WIDTH, HEIGHT), Image.LANCZOS)
        premultiplied = np.where(covered[..., None], image, 0).clip(0, 255).astype(np.uint8)
        rgb = np.asarray(Image.fromarray(premultiplied).resize((WIDTH, HEIGHT), Image.LANCZOS)).astype(float)
        a = np.asarray(alpha).astype(float)
        rgb = np.where(a[..., None] > 0, rgb * 255 / np.maximum(a[..., None], 1), 0)
        rgba = np.dstack([rgb.clip(0, 255), a]).astype(np.uint8)
        Image.fromarray(rgba).save(args.transparent)
        print(f"wrote {args.transparent}")


if __name__ == "__main__":
    main()
