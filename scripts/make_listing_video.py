"""Build the Tilde Card video (v4.1): about 26 seconds, 30 fps, silent with captions, so it
autoplays muted and loops. Four formats, each laid out for its own frame (not cropped from
another), each with a .jpg poster (the end card):

- makerworld/video/tilde-card.mp4: 1440 x 1080 (4:3) for MakerWorld, whose end card adds "Click
  Customize to make yours". The only output kept in the repo.
- In the exports folder (out/video/exports/, git-ignored, or --exports DIR):
  - tilde-card-4x3.mp4: the same 4:3 with the general end card
  - tilde-card-16x9.mp4 and .webm: 1920 x 1080, for tbutman.com/tilde
  - tilde-card-1x1.mp4 and .webm: 1080 x 1080, for X and LinkedIn feeds
  - tilde-card-9x16.mp4: 1080 x 1920, for Reels, Shorts and Stories

The scenes (tilde-media/video/card-v4-storyboard.md):

1. Tap: a phone comes down onto the card's tap mark, in the card's own 3D view, and the card
   pulses; then the phone straight on, where the link opens.
2. One print, four colors: the card, then it turns over to show the back.
3. Make it yours: four color sets in place.
4. Anyone can scan it: the phone's camera finds the QR code, the link chip appears, the page opens.
5. NFC: the card at the pause on the plate, the sticker drops in, the last four layers seal it, and
   a see-through moment shows the sticker inside.
6. The end card: ~/tilde card, taptilde.com, "Free · Open source", "by Thomas Butman". The last
   frame matches the first, so the video loops.

Everything about the card is the model's own geometry: makerworld/tilde-card.scad with its
committed sample defaults (Jane Doe, https://taptilde.com, 0.4 mm nozzle, thin sticker), cut at
each layer for the print scene (OpenSCAD in Docker). The layer height, the pause and the pocket
come from the model's own echo. The phones, screens, plate and sticker are drawn.

Each pose of the card is rendered once with transparency, a contact shadow, a gentle light
falloff and, on its printed top face, the 45-degree lines of the top layer; every format then
places those poses with its own framing. Renders are cached in out/video/v4/, so a second run
only lays out and encodes the frames.

The phones show a mock of tbutman.com/tilde (where taptilde.com redirects) with its "Scanned a
Tilde Card? Make your own" strip. Put a 1080 x 2400 (or 540 x 1200) screenshot at makerworld/video/taptilde-page.png and the
phones show it instead.

Colors and sizes follow tilde-media/brand/BRAND.md: Tilde orange #ffb547 for drawn accents,
#a85f00 for orange text on the beige backdrop, captions 72 / 42 px on a 1080 px short side.

    .venv/bin/python scripts/make_listing_video.py [--exports DIR]
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
from collections import OrderedDict
from multiprocessing import Pool
from pathlib import Path

import cv2
import imageio_ffmpeg
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_covers import BACKGROUND, INK, SUBTLE, font  # noqa: E402
from make_listing_images import COLOR_SETS, STICKER, phone, sticker  # noqa: E402
from render_preview import LIGHT, PARTS, SUPERSAMPLE as SS, TILT_DEG, TURN_DEG, render, rotation  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCAD = "makerworld/tilde-card.scad"
CACHE = ROOT / "out" / "video" / "v4"
CARD_DIR = CACHE / "card"
LAYER_DIR = CACHE / "layers"
POSES = CACHE / "poses"
VIDEO = ROOT / "makerworld" / "video"
PAGE_SHOT = VIDEO / "taptilde-page.png"
FPS = 30
FADE = 10  # frames of crossfade between scenes

ORANGE = (255, 181, 71)     # Tilde orange, #ffb547
ORANGE_DEEP = (168, 95, 0)  # Tilde orange on light grounds, #a85f00
SITE_BG, SITE_PANEL, SITE_LINE = (11, 13, 16), (17, 21, 26), (31, 38, 46)
SITE_TEXT, SITE_MUTED = (231, 234, 238), (162, 171, 182)
SHADOW_INK = (64, 57, 48)   # warm, so shadows on the beige don't look gray
PHONE_BODY = (28, 30, 34)
PLATE = (70, 70, 72)        # a textured PEI plate, dark gray, lighter than the card

POSE_SIZE = (2000, 1600)    # a pose's canvas, output pixels; the card's centre is in the middle
POSE_SCALE = 16.0           # output pixels per mm in a pose
PHONE_CANVAS = ((2000, 1800), (800, 700), 8.0)  # phone poses: size, the card's centre, pixels per mm
FLIP_STEPS = 40
DROP_STEPS = 14
PHONE_STEPS = 16
LINE_PITCH = 0.42           # mm between the top layer's lines

EXPORTS = ROOT / "out" / "video" / "exports"  # git-ignored; --exports DIR writes them elsewhere
# Each output: its layout, size, file (None: in the exports folder, under this name), encoder quality
# and, for MakerWorld, the end card that says to click Customize. Only the MakerWorld file lives in
# the repo.
FORMATS = {
    "4x3-makerworld": {"layout": "4x3", "size": (1440, 1080), "path": VIDEO / "tilde-card.mp4", "crf": 20,
                       "makerworld": True},
    "4x3": {"layout": "4x3", "size": (1440, 1080), "name": "tilde-card-4x3.mp4", "crf": 20},
    "16x9": {"layout": "16x9", "size": (1920, 1080), "name": "tilde-card-16x9.mp4", "crf": 25, "webm": True},
    "1x1": {"layout": "1x1", "size": (1080, 1080), "name": "tilde-card-1x1.mp4", "crf": 23, "webm": True},
    "9x16": {"layout": "9x16", "size": (1080, 1920), "name": "tilde-card-9x16.mp4", "crf": 23},
}


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))


def lerp(a, b, t):
    return a + (b - a) * t


# --- the model ------------------------------------------------------------------------------------

def openscad(*args, entry=None):
    cmd = ["docker", "run", "--rm", "-v", f"{ROOT}:/w", "-w", "/w", "-e", "OPENSCAD_FONT_PATH=/w/fonts"]
    if entry:
        cmd += ["--entrypoint", "sh", "openscad/openscad:dev", "-c", entry]
    else:
        cmd += ["openscad/openscad:dev", "openscad", "--backend=manifold", *args]
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def model_facts():
    """Layer height, layer count, the pause and the pocket, from the model's own echo."""
    path = CACHE / "facts.json"
    if path.exists():
        return json.loads(path.read_text())
    CARD_DIR.mkdir(parents=True, exist_ok=True)
    log = openscad("-D", 'part="chrome"', "--export-format", "binstl", "-o", "out/video/v4/echo.stl", SCAD).stderr
    facts = {
        "layer_h": float(re.search(r"layer_h=([0-9.]+)", log).group(1)),
        "layers": int(re.search(r"([0-9]+) layers\"", log).group(1)),
        "pause": int(re.search(r"pause before layer ([0-9]+)", log).group(1)),
        "pocket_top": float(re.search(r"pocket_top=([0-9.]+)", log).group(1)),
        "pocket_d": float(re.search(r"NFC pocket: d=([0-9.]+)", log).group(1)),
    }
    path.write_text(json.dumps(facts))
    return facts


def build_card(facts):
    """The card's color bodies (as printed, front down) and the cuts through each layer from the
    pause on, from the MakerWorld file with its own defaults."""
    for part in PARTS:
        out = CARD_DIR / f"card-{part}.stl"
        if not out.exists():
            openscad("-D", f'part="{part}"', "--export-format", "binstl", "-o", f"out/video/v4/card/{out.name}", SCAD)
    LAYER_DIR.mkdir(parents=True, exist_ok=True)
    (LAYER_DIR / "cut.scad").write_text(
        'file = "";\ntop = 1;\nintersection() { import(file); translate([-1, -1, -1]) cube([200, 200, top + 1]); }\n')
    lines = []
    for n in range(facts["pause"] - 1, facts["layers"]):
        top = round(n * facts["layer_h"] - 0.005, 3)  # just under the layer's top: no skin over the pocket
        for part in PARTS:
            src, out = CARD_DIR / f"card-{part}.stl", LAYER_DIR / f"{n:02d}-{part}.stl"
            if out.exists() or not src.exists() or trimesh.load(src).bounds[0][2] >= top:
                continue
            lines.append(f"openscad --backend=manifold -D 'file=\"/w/{src.relative_to(ROOT)}\"' -D top={top} "
                         f"--export-format binstl -o out/video/v4/layers/{out.name} out/video/v4/layers/cut.scad")
    if lines:
        openscad(entry=" && ".join(lines))


_parts = {}


def card_parts(layer=None):
    """The card's parts as printed (front down on the plate), through `layer` (None: finished)."""
    key = layer
    if key not in _parts:
        facts = model_facts()
        if layer is None or layer >= facts["layers"]:
            files = {p: CARD_DIR / f"card-{p}.stl" for p in PARTS}
        else:
            files = {p: LAYER_DIR / f"{layer:02d}-{p}.stl" for p in PARTS}
        _parts[key] = {p: trimesh.load(f) for p, f in files.items() if f.exists()}
    return {k: v.copy() for k, v in _parts[key].items()}


def centre():
    return card_parts()["body"].bounds.mean(axis=0)


def about(matrix, point):
    return trimesh.transformations.translation_matrix(point) @ matrix @ trimesh.transformations.translation_matrix(-point)


def rot(angle, axis):
    return trimesh.transformations.rotation_matrix(angle, axis)


def front_up():
    return about(rot(math.pi, [1, 0, 0]), centre())


def back_up():
    """Back up and reading the right way: the print turned a half turn on the plate."""
    return about(rot(math.pi, [0, 0, 1]), centre())


def flip(degrees):
    """From front up to back up about the card's short axis, like turning a page; lifted a little
    on the way."""
    lift = 8 * math.sin(math.radians(degrees))
    turn = about(rot(math.radians(degrees), [0, 1, 0]) @ rot(math.pi, [1, 0, 0]), centre())
    return trimesh.transformations.translation_matrix([0, 0, lift]) @ turn


def pocket(facts):
    """The open pocket at the pause, in the print's frame: floor height and centre."""
    body = card_parts(facts["pause"] - 1)["body"]
    tris, normals = body.triangles, body.face_normals
    top = facts["pocket_top"]
    floor_z = max(z for z in np.unique(tris[:, :, 2].round(4)) if z < top - 0.02)
    floor = tris[(np.abs(tris[:, :, 2] - floor_z).max(axis=1) < 1e-4) & (normals[:, 2] > 0.99)].reshape(-1, 3)
    c = (floor.min(axis=0) + floor.max(axis=0)) / 2
    return float(floor_z), [float(c[0]), float(c[1])]


def plate():
    c = centre()
    box = trimesh.creation.box(extents=[104, 74, 1.2])
    box.apply_translation([c[0], c[1], -0.6])
    return box


def phone_mesh():
    """A phone, 72 x 150 x 8 mm, screen up (+z), its top end at +y, as a rounded slab."""
    def ring(w, length, r, z):
        pts = []
        for cx, cy, a0 in [(w / 2 - r, length / 2 - r, 0), (-w / 2 + r, length / 2 - r, 90),
                           (-w / 2 + r, -length / 2 + r, 180), (w / 2 - r, -length / 2 + r, 270)]:
            for a in np.linspace(a0, a0 + 90, 10):
                pts.append([cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), z])
        return pts
    rings = [ring(70.6, 148.6, 9.3, 0), ring(72, 150, 10, 1.2), ring(72, 150, 10, 6.8), ring(70.6, 148.6, 9.3, 8)]
    n = len(rings[0])
    verts = np.array([p for r in rings for p in r] + [[0, 0, 0], [0, 0, 8]])
    faces = []
    for k in range(len(rings) - 1):  # the sides: a quad between each pair of rings
        for i in range(n):
            a0, a1 = k * n + i, k * n + (i + 1) % n
            b0, b1 = a0 + n, a1 + n
            faces += [[a0, a1, b1], [a0, b1, b0]]
    bottom, top = len(verts) - 2, len(verts) - 1
    last = (len(rings) - 1) * n
    for i in range(n):  # the caps: fans from the middle
        faces += [[bottom, (i + 1) % n, i], [top, last + i, last + (i + 1) % n]]
    return trimesh.Trimesh(verts, faces, process=False)  # wound outward: the rings run counterclockwise


PHONE_SCREEN = np.array([[-32.5, 71, 8.02], [32.5, 71, 8.02], [-32.5, -71, 8.02]])  # top-left, top-right, bottom-left
PHONE_TILT = 10  # degrees: the end nearest the camera is higher, as in a hand


def phone_pose(t, tap):
    """The phone's placement for descent t (0: up and back, 1: touching the tap mark): held the way
    someone at the camera would hold it, its top end (where the NFC antenna is) over the tap mark and
    its body toward the camera, so its screen reads upright in the shot."""
    a = math.radians(PHONE_TILT + 8 * (1 - t))
    m = rot(-a, [1, 0, 0])  # the near end (-y) up
    end = m @ np.array([0, 75, 0, 1])  # the top end's bottom edge
    target = np.array([tap[0] + 26, tap[1] + 22 - 25 * (1 - t), tap[2] + 0.4 + 46 * (1 - t)])
    return trimesh.transformations.translation_matrix(target - end[:3]) @ m


# --- poses ----------------------------------------------------------------------------------------

def view(centre_point, scale, size, anchor=None, tilt=TILT_DEG, turn=TURN_DEG):
    """An orthographic view like render_preview's, at a fixed scale (output pixels per mm), with
    `centre_point` at `anchor` (output pixels; the canvas's middle by default)."""
    r = rotation(-tilt, turn)
    ax, ay = anchor if anchor else (size[0] / 2, size[1] / 2)

    def project(points):
        p = (np.asarray(points, float) - centre_point) @ r.T
        return np.column_stack([p[:, 0] * scale * SS + ax * SS, ay * SS - p[:, 1] * scale * SS, p[:, 2]])

    return project, r


def light_world(r):
    lv = LIGHT / np.linalg.norm(LIGHT)
    return r.T @ lv


def surface(name, points, normal):
    """The printed look: the top layer's 45-degree lines on every face that was printed facing up,
    a speckle on the plate; the front (printed against the plate) stays smooth and matte."""
    if name == "plate":
        cell = np.floor(points[:, :2] * 4)
        n = np.modf(np.sin(cell[:, 0] * 12.9898 + cell[:, 1] * 78.233) * 43758.5453)[0]
        return 1 + 0.07 * (np.abs(n) - 0.5)
    if normal[2] > 0.9:
        u = (points[:, 0] + points[:, 1]) / math.sqrt(2)
        return 1 + 0.035 * np.sin(2 * math.pi * u / LINE_PITCH)
    return 1.0


def falloff(image, covered):
    """Light a little stronger at the top left of the canvas than at the bottom right (+-4%)."""
    h, w = covered.shape
    gy, gx = np.mgrid[0:h, 0:w]
    g = 1.04 - 0.08 * (0.6 * gx / w + 0.4 * gy / h)
    image[covered] *= g[covered, None]
    return image


def to_rgba(image, covered, size):
    """Downsample with straight alpha (color premultiplied by coverage, then divided back out)."""
    alpha = Image.fromarray((covered * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    pre = np.where(covered[..., None], image, 0).clip(0, 255).astype(np.uint8)
    rgb = np.asarray(Image.fromarray(pre).resize(size, Image.LANCZOS)).astype(float)
    a = np.asarray(alpha).astype(float)
    rgb = np.where(a[..., None] > 0, rgb * 255 / np.maximum(a[..., None], 1), 0)
    return Image.fromarray(np.dstack([rgb.clip(0, 255), a]).astype(np.uint8), "RGBA")


def shadow_mask(meshes, project, r, size, table_z, key=0.5, ambient=0.26):
    """A soft shadow on the table (z = table_z) under `meshes`: the key light's shadow, sharper
    the closer the object is, plus a wide ambient one. Output pixels, 0-255."""
    pts = np.vstack([m.vertices for m in meshes])
    lw = light_world(r)
    h = np.maximum(pts[:, 2] - table_z, 0)
    cast = pts.copy()
    cast[:, :2] -= h[:, None] * lw[:2] / lw[2]
    cast[:, 2] = table_z
    flat = pts.copy()
    flat[:, 2] = table_z
    out = np.zeros((size[1], size[0]), float)
    lift = float(h.mean())
    for points, strength, blur in [(cast, key, 3 + 1.6 * lift), (flat, ambient, 26 + 1.0 * lift)]:
        xy = (project(points)[:, :2] / SS).astype(np.float32)
        hull = cv2.convexHull(xy).astype(np.int32)
        layer = np.zeros((size[1], size[0]), np.uint8)
        cv2.fillPoly(layer, [hull], 255)
        layer = cv2.GaussianBlur(layer.astype(float), (0, 0), blur)
        fade = 1 / (1 + lift / 25)
        out = np.maximum(out, layer * strength * fade)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "L")


def pose_specs(facts, flips):
    """Every pose to render: name -> (kind, args)."""
    specs = {f"front-{k}": ("front", k) for k in range(len(COLOR_SETS))}
    specs.update({f"flip-{a:06.2f}": ("flip", a) for a in flips})
    for n in range(facts["pause"] - 1, facts["layers"] + 1):
        specs[f"layer-{n:02d}"] = ("layer", n, None)
    floor_z, _ = pocket(facts)
    for i in range(DROP_STEPS):
        specs[f"drop-{i:02d}"] = ("layer", facts["pause"] - 1, floor_z + 9 * (1 - ease(i / (DROP_STEPS - 1))))
    for i in range(PHONE_STEPS):
        specs[f"phone-{i:02d}"] = ("phone", i / (PHONE_STEPS - 1), "lock")
    specs["phone-tap"] = ("phone", 1.0, "banner")
    specs["camera"] = ("camera",)
    return specs


def tap_point():
    """The front's tap mark, on the card's top face, with the card front up."""
    acc = card_parts()["accent"]
    v = acc.vertices[acc.vertices[:, 0] > acc.vertices[:, 0].max() - 6]
    p = np.append((v.min(axis=0) + v.max(axis=0)) / 2, 1)
    p = front_up() @ p
    top = front_up() @ np.append(centre(), 1)
    return np.array([p[0], p[1], top[2] + 0.9])


def qr_field():
    """The QR code's light field with the card front up: its centre and corners."""
    light = card_parts()["light"]
    v = light.vertices
    v = v[(v[:, 0] > 37) & (v[:, 0] < v[:, 0].max() - 5)]
    v = trimesh.transform_points(v, front_up())
    lo, hi = v.min(axis=0), v.max(axis=0)
    return (lo + hi) / 2, lo, hi


def render_pose(item):
    """One pose: an RGBA PNG, its shadow and a JSON of where the card's centre sits."""
    name, spec = item
    out = POSES / f"{name}.png"
    if out.exists():
        return name
    kind = spec[0]
    c = centre()
    size, anchor = POSE_SIZE, None
    colors = dict(PARTS)
    shadow = None
    if kind == "camera":
        # The phone held over the card: the whole card in view, 86% of the screen's width.
        mid, lo, hi = qr_field()
        size = (1080, 2400)
        body = card_parts()["body"].copy().apply_transform(front_up())
        scale = 0.86 * size[0] / np.ptp(body.vertices[:, 0])
        project, r = view(body.bounds.mean(axis=0), scale, size, tilt=10, turn=2)
        meshes = {k: v.apply_transform(front_up()) for k, v in card_parts().items()}
        image, covered = render(meshes, colors, size, (project, r))
        image = falloff(image, covered)
        Image.fromarray(image.clip(0, 255).astype(np.uint8)).resize(size, Image.LANCZOS).save(out)
        corners = project(np.array([[lo[0], lo[1], hi[2]], [hi[0], hi[1], hi[2]], [lo[0], hi[1], hi[2]], [hi[0], lo[1], hi[2]]]))
        xy = corners[:, :2] / SS
        out.with_suffix(".json").write_text(json.dumps({"qr": [*xy.min(axis=0).tolist(), *xy.max(axis=0).tolist()]}))
        return name
    if kind == "phone":
        size, anchor, scale = PHONE_CANVAS
        project, r = view(c, scale, size, anchor)
        m = phone_pose(spec[1], tap_point())
        body = phone_mesh().apply_transform(m)
        image, covered = render({"phone": body}, {"phone": PHONE_BODY}, size, (project, r))
        rgba = to_rgba(image, covered, size)
        # The screen: an affine map of the screen image onto the top face.
        scr = Image.open(CACHE / f"screen-{spec[2]}.png").convert("RGB")
        corners = project(trimesh.transform_points(PHONE_SCREEN, m))[:, :2] / SS
        (x0, y0), (x1, y1), (x2, y2) = corners
        sw, sh = scr.size
        a = np.array([[x1 - x0, x2 - x0], [y1 - y0, y2 - y0]]) / np.array([sw, sh])
        inv = np.linalg.inv(a)
        data = (inv[0, 0], inv[0, 1], -(inv[0, 0] * x0 + inv[0, 1] * y0),
                inv[1, 0], inv[1, 1], -(inv[1, 0] * x0 + inv[1, 1] * y0))
        warped = scr.transform(size, Image.AFFINE, data, Image.BICUBIC)
        mask = Image.new("L", scr.size, 255).transform(size, Image.AFFINE, data, Image.BICUBIC)
        mask = mask.filter(ImageFilter.MinFilter(3))
        rgba.paste(warped, (0, 0), mask)
        rgba.save(out)
        top = tap_point()[2]
        shadow_mask([body], project, r, size, top, key=0.42, ambient=0.0).save(out.with_name(f"{name}-shadow.png"))
        out.with_suffix(".json").write_text(json.dumps({"anchor": list(anchor), "scale": scale}))
        return name
    local = {}
    if kind == "front":
        m, colors = front_up(), dict(COLOR_SETS[spec[1]])
        local = card_parts()
        table = 0.0
    elif kind == "flip":
        m = flip(spec[1])
        local = card_parts()
        table = 0.0
    else:  # a layer of the print, on the plate, with the sticker at height spec[2]
        m = back_up()
        local = card_parts(spec[1])
        local["plate"] = plate()
        colors["plate"] = PLATE
        table = -1.2
    project, r = view(c, POSE_SCALE, size)
    meshes = {k: v.copy().apply_transform(m) for k, v in local.items()}
    extra = {}
    if kind == "layer" and spec[2] is not None:
        floor_z, pc = pocket(model_facts())
        extra = {k: v.apply_transform(m) for k, v in sticker(np.array(pc), spec[2]).items()}
        colors.update(STICKER)
    image, covered = render({**meshes, **extra}, colors, size, (project, r), local=local, texture=surface)
    image = falloff(image, covered)
    to_rgba(image, covered, size).save(out)
    shadow = shadow_mask(list(meshes.values()), project, r, size, table)
    shadow.save(out.with_name(f"{name}-shadow.png"))
    out.with_suffix(".json").write_text(json.dumps({"anchor": [size[0] / 2, size[1] / 2]}))
    return name


# --- screens (1080 x 2400, a phone's screen at 2x) -------------------------------------------------

SW, SH = 1080, 2400


def status_bar(d, color):
    d.text((60, 46), "9:41", font=font("Inter-Bold.ttf", 34), fill=color, anchor="lm")
    for i in range(4):  # signal bars and a battery
        d.rounded_rectangle([880 + i * 16, 58 - 8 * i, 890 + i * 16, 62], 2, fill=color)
    d.rounded_rectangle([960, 34, 1018, 60], 6, outline=color, width=3)
    d.rounded_rectangle([965, 39, 1004, 55], 3, fill=color)


def lock_screen():
    s = Image.new("RGB", (SW, SH))
    d = ImageDraw.Draw(s)
    for y in range(SH):
        t = y / SH
        d.line([(0, y), (SW, y)], fill=(round(20 + 16 * t), round(23 + 14 * t), round(30 + 18 * t)))
    status_bar(d, (236, 236, 236))
    d.text((SW / 2, 470), "9:41", font=font("Inter-ExtraBold.ttf", 230), fill=(240, 240, 240), anchor="mm")
    return s


def banner(s, t=1.0):
    """The link notification sliding down from the top (t: 0 hidden, 1 in place)."""
    s = s.copy()
    y = round(-260 + 400 * ease(t))
    layer = Image.new("RGBA", s.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([40, y, SW - 40, y + 220], 48, fill=(246, 246, 244, 245))
    d.ellipse([84, y + 54, 196, y + 166], fill=(222, 226, 232))
    cx, cy = 140, y + 110  # a globe
    d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], outline=(70, 76, 86), width=5)
    d.ellipse([cx - 14, cy - 32, cx + 14, cy + 32], outline=(70, 76, 86), width=4)
    d.line([(cx - 32, cy), (cx + 32, cy)], fill=(70, 76, 86), width=4)
    d.text((230, y + 82), "taptilde.com", font=font("Inter-ExtraBold.ttf", 46), fill=INK, anchor="lm")
    d.text((230, y + 142), "Open in browser", font=font("Inter-Bold.ttf", 36), fill=(90, 94, 100), anchor="lm")
    s.paste(layer, (0, 0), layer)
    return s


def wordmark(d, x, y, size, name, anchor="lm", dark=False):
    """~/name in JetBrains Mono ExtraBold: ~/ in Tilde orange, the name in the text color."""
    f = font("JetBrainsMono-ExtraBold.ttf", size)
    w = f.getlength("~/" + name)
    if anchor == "mm":
        x -= w / 2
    d.text((x, y), "~/", font=f, fill=ORANGE if dark else ORANGE_DEEP, anchor="lm")
    d.text((x + f.getlength("~/"), y), name, font=f, fill=SITE_TEXT if dark else INK, anchor="lm")
    return w


def wrap(text, f, width):
    """Lines of `text` no wider than `width`, as even as they can be (no one-word last line)."""
    lines = greedy(text, f, width)
    while len(lines) > 1 and width > 50:
        narrower = greedy(text, f, width - 10)
        if len(narrower) > len(lines):
            break
        lines, width = narrower, width - 10
    return lines


def greedy(text, f, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if f.getlength(trial) <= width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line]


def page_screen(card_still):
    """The page a tap or scan opens: tbutman.com/tilde (where taptilde.com redirects), with its
    sample-card strip. A screenshot replaces it when there is one."""
    if PAGE_SHOT.exists():
        shot = Image.open(PAGE_SHOT).convert("RGB")
        k = max(SW / shot.width, SH / shot.height)
        return shot.resize((round(shot.width * k), round(shot.height * k)), Image.LANCZOS).crop((0, 0, SW, SH))
    s = Image.new("RGB", (SW, SH), SITE_BG)
    d = ImageDraw.Draw(s)
    status_bar(d, SITE_TEXT)
    d.rectangle([0, 90, SW, 240], fill=SITE_PANEL)
    d.rounded_rectangle([40, 112, SW - 40, 218], 53, fill=SITE_LINE)
    lx, ly = 100, 165  # a padlock
    d.rounded_rectangle([lx - 14, ly - 4, lx + 14, ly + 20], 4, fill=SITE_MUTED)
    d.arc([lx - 10, ly - 24, lx + 10, ly + 4], 180, 360, fill=SITE_MUTED, width=5)
    d.text((136, ly), "tbutman.com/tilde", font=font("Inter-Bold.ttf", 42), fill=SITE_TEXT, anchor="lm")
    d.rectangle([0, 240, SW, 384], fill=ORANGE)
    d.text((60, 290), "Scanned a Tilde Card?", font=font("Inter-Bold.ttf", 38), fill=INK, anchor="lm")
    d.text((60, 342), "Make your own →", font=font("Inter-ExtraBold.ttf", 38), fill=INK, anchor="lm")
    wordmark(d, 60, 470, 46, "tbutman", dark=True)
    for i in range(3):
        d.rounded_rectangle([SW - 112, 452 + i * 16, SW - 60, 458 + i * 16], 3, fill=SITE_MUTED)
    d.line([(0, 540), (SW, 540)], fill=SITE_LINE, width=2)
    d.text((60, 620), "free · open source · no account · android", font=font("JetBrainsMono-ExtraBold.ttf", 30),
           fill=ORANGE, anchor="lm")
    y = 700
    for line in ["Your business card,", "on your phone."]:
        d.text((60, y), line, font=font("Inter-ExtraBold.ttf", 92), fill=SITE_TEXT, anchor="la")
        y += 108
    body = font("Inter-Bold.ttf", 38)
    y += 40
    for line in wrap("Tap phones to share your contact card, your website or your WhatsApp, or let them scan "
                     "the code on your screen.", body, SW - 120):
        d.text((60, y), line, font=body, fill=SITE_MUTED, anchor="la")
        y += 54
    y += 46
    d.rounded_rectangle([60, y, 600, y + 104], 52, fill=ORANGE)
    d.text((330, y + 52), "download for android", font=font("Inter-ExtraBold.ttf", 36), fill=SITE_BG, anchor="mm")
    d.rounded_rectangle([630, y, SW - 60, y + 104], 52, outline=SITE_LINE, width=3)
    d.text(((630 + SW - 60) / 2, y + 52), "print a card", font=font("Inter-ExtraBold.ttf", 36), fill=SITE_TEXT, anchor="mm")
    y += 170
    panel = (60, y, SW - 60, y + 640)
    d.rounded_rectangle(panel, 32, fill=tuple(BACKGROUND))
    still = card_still.copy()
    still.thumbnail((panel[2] - panel[0] - 60, panel[3] - panel[1] - 60), Image.LANCZOS)
    s.paste(still, (round((SW - still.width) / 2), round(y + (640 - still.height) / 2)), still)
    return s


def camera_screen(view_img, qr_box, t, found=0.0, press=0.0):
    """What the scanning phone shows: the camera's view of the whole card, drifting a little in the
    hand, brackets closing on the QR code (t: 0 wide, 1 locked), the link chip rising (found) and a
    tap on it (press)."""
    dx, dy = 6 * math.sin(t * 5.1), 5 * math.cos(t * 3.7)
    s = view_img.transform(view_img.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), Image.BICUBIC)
    s = Image.composite(s, Image.new("RGB", s.size, (0, 0, 0)), vignette(s.size))
    layer = Image.new("RGBA", s.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    status_bar(d, INK)
    # The shutter button, white with a soft dark ring so it reads on the table.
    d.ellipse([SW / 2 - 86, 2134, SW / 2 + 86, 2306], outline=(0, 0, 0, 60), width=6)
    d.ellipse([SW / 2 - 80, 2140, SW / 2 + 80, 2300], outline=(255, 255, 255, 255), width=10)
    x0, y0, x1, y1 = qr_box
    pad = 24 + 120 * (1 - ease(t))
    x0, y0, x1, y1 = x0 - pad + dx, y0 - pad + dy, x1 + pad + dx, y1 + pad + dy
    L = 70
    for color, width in [((0, 0, 0, 70), 18), ((255, 255, 255, 255), 10)]:
        for cx, cy, sx, sy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line([(cx, cy), (cx + sx * L, cy)], fill=color, width=width)
            d.line([(cx, cy), (cx, cy + sy * L)], fill=color, width=width)
    if found > 0:
        e = ease(found)
        y = round(1880 - 60 * e)
        a = round(255 * e)
        grow = 1 - 0.05 * math.sin(math.pi * min(press, 1))
        w2, h2 = 300 * grow, 62 * grow
        d.rounded_rectangle([SW / 2 - w2, y - h2 + 8, SW / 2 + w2, y + h2 + 8], h2, fill=(0, 0, 0, round(40 * e)))
        d.rounded_rectangle([SW / 2 - w2, y - h2, SW / 2 + w2, y + h2], h2, fill=(250, 250, 248, a))
        gx, gy = SW / 2 - w2 + 70, y
        d.ellipse([gx - 22, gy - 22, gx + 22, gy + 22], outline=(70, 76, 86, a), width=5)
        d.line([(gx - 22, gy), (gx + 22, gy)], fill=(70, 76, 86, a), width=4)
        d.text((gx + 50, y), "taptilde.com", font=font("Inter-ExtraBold.ttf", 46), fill=(*INK, a), anchor="lm")
        if 0 < press < 1:
            r = 40 + 90 * press
            d.ellipse([SW / 2 - r, y - r, SW / 2 + r, y + r], fill=(255, 255, 255, round(110 * (1 - press))))
    s.paste(layer, (0, 0), layer)
    return s


_vignette = {}


def vignette(size):
    """A soft darkening toward the edges, as a phone camera's view has: a mask, 255 in the middle."""
    if size not in _vignette:
        w, h = size
        gy, gx = np.mgrid[0:h, 0:w]
        r = np.sqrt(((gx - w / 2) / (w * 0.75)) ** 2 + ((gy - h / 2) / (h * 0.75)) ** 2)
        _vignette[size] = Image.fromarray((255 * (1 - 0.16 * np.clip(r, 0, 1) ** 2)).astype(np.uint8), "L")
    return _vignette[size]


def slide_up(base, page, t):
    """`page` sliding up over `base` (t: 0 hidden, 1 in place)."""
    s = base.copy()
    y = round(SH * (1 - ease(t)))
    if y < SH:
        s.paste(page.crop((0, 0, SW, SH - y)), (0, y))
    return s


# --- the timeline -----------------------------------------------------------------------------------
# A frame is a dict: {"card": [(pose, weight)], "place": placement, "phone3d": pose, "rings": phase,
# "screen": screen spec, "caption": (headline, second line, alpha), "end": alpha of the end card's
# lines}. Placements are resolved per format in Layout.

def caption_alpha(i, n, lead=8, tail=FADE):
    return min(1, max(0, (i - lead) / 8)) * min(1, max(0, (n - 1 - i) / tail))


def timeline(flips):
    frames = []
    scenes = []

    def scene(fs):
        scenes.append(fs)

    # 1a. The tap, in the card's view: from the end card's framing into the tap mark.
    fs = []
    n = 76
    for i in range(n):
        t = ease(i / 44)
        d = ease((i - 8) / 40)
        f = {"card": [("front-0", 1)], "place": ("mix", "end", "tap", t, 0.02 * max(0, i - 44) / 32),
             "caption": ("Share your details with a tap", None, caption_alpha(i, n, lead=14))}
        if i >= 8:
            f["phone3d"] = "phone-tap" if i >= 48 else f"phone-{round(d * (PHONE_STEPS - 1)):02d}"
            f["phone_t"] = d
            f["phone_a"] = ease((i - 8) / 8)
        if i >= 48:
            f["rings"] = (i - 48) / 24
        fs.append(f)
    # 1b. The phone straight on: the notification is there, then the page slides up.
    for i in range(64):
        fs.append({"screen": ("tap", (i - 14) / 16), "phone_zoom": 0.02 * i / 63})
    scene(fs)

    # 2a. One print, four colors.
    n = 76
    scene([{"card": [("front-0", 1)], "place": ("at", "home", 0.03 * i / (n - 1)),
            "caption": ("One print, four colors", None, caption_alpha(i, n))} for i in range(n)])

    # 2b. It turns over: the back.
    fs = []
    seq = [flips[0]] * 6 + flips + [flips[-1]] * 60
    for i, a in enumerate(seq):
        hold = max(0, i - 6 - len(flips))
        # The caption waits for the turn: mid-turn the card needs the whole frame.
        fs.append({"card": [(f"flip-{a:06.2f}", 1)], "place": ("at", "home", 0.03 * hold / 60), "fit": True,
                   "caption": ("Your details on the back", None, caption_alpha(i, len(seq), lead=6 + len(flips)))})
    scene(fs)

    # 3. Make it yours: the other color sets, then back to the sample's.
    order = [1, 2, 3, 0]
    fs = []
    n = len(order) * 22 + (len(order) - 1) * 8
    i = 0
    for k, s in enumerate(order):
        for _ in range(22):
            fs.append({"card": [(f"front-{s}", 1)], "place": ("at", "home", 0.03 * i / (n - 1))})
            i += 1
        if k + 1 < len(order):
            for j in range(8):
                w = ease((j + 1) / 9)
                fs.append({"card": [(f"front-{s}", 1 - w), (f"front-{order[k + 1]}", w)],
                           "place": ("at", "home", 0.03 * i / (n - 1))})
                i += 1
    for i, f in enumerate(fs):
        f["caption"] = ("Make it yours", "Your name, your link, your colors", caption_alpha(i, n))
    scene(fs)

    # 4. Anyone can scan it: the phone's view.
    n = 120
    scene([{"screen": ("scan", i), "phone_zoom": 0.02 * i / (n - 1),
            "caption": ("Anyone can scan it", "Any phone camera opens your link", caption_alpha(i, n))} for i in range(n)])

    # 5a. The pause: the half-printed card on the plate, the sticker drops in.
    fs = []
    n = 72
    for i in range(n):
        pose = "layer-05" if i < 20 else f"drop-{min(DROP_STEPS - 1, round((i - 20) / 22 * (DROP_STEPS - 1))):02d}"
        fs.append({"card": [(pose, 1)], "place": ("mix", "home", "pocket", ease(i / 34), 0),
                   "pocket": ease((i - 6) / 10) * (1 - ease((i - 36) / 8)),
                   "caption": ("Add NFC to tap", "An optional sticker goes in at a pause", caption_alpha(i, n))})
    scene(fs)

    # 5b. The last layers seal it; a see-through moment shows the sticker inside.
    fs = []
    n = 110
    last = f"drop-{DROP_STEPS - 1:02d}"
    for i in range(n):
        if i < 36:
            layer = min(9, 6 + i // 9)
            card = [(f"layer-{layer:02d}", 1)]
        else:
            x = ease((i - 40) / 10) * (1 - ease((i - 62) / 12))
            card = [("layer-09", 1 - 0.65 * x), (last, 0.65 * x)]
        fs.append({"card": card, "pocket": x if i >= 36 else 0, "place": ("mix", "pocket", "home", ease((i - 24) / 50), 0),
                   "caption": ("Sealed inside", "Write it with the free Tilde app (Android) or NFC Tools",
                               caption_alpha(i, n, lead=36))})
    scene(fs)

    # 6. The end card: the card turns front up, settles into the end framing, the lines fade in
    # and, at the very end, out again, so the last frame is the first.
    fs = []
    back = list(reversed(flips))[:: max(1, len(flips) // 20)]
    n = 130
    for i in range(n):
        a = back[min(i, len(back) - 1)] if i < len(back) else flips[0]
        name = f"flip-{a:06.2f}" if i < len(back) else "front-0"
        fs.append({"card": [(name, 1)], "place": ("mix", "home", "end", ease((i - 18) / 28), 0), "fit": i < len(back),
                   "end": (i - 40, max(0, 1 - (i - 116) / 13) if i >= 116 else 1)})
    scene(fs)

    # Crossfade each scene's last FADE frames into the next one's first; from the phone's view to
    # the print (scene 5a), dip through the background instead, so the plate never lies over the
    # phone.
    dips = {5}
    for k, fs in enumerate(scenes):
        if k == 0:
            frames.extend(fs)
            continue
        tail = frames[-FADE:]
        del frames[-FADE:]
        for t in range(FADE):
            kind = "dip" if k in dips else "mix"
            frames.append({kind: (tail[t], fs[t], (t + 1) / (FADE + 1))})
        frames.extend(fs[FADE:])
    return frames


# --- layout per format ------------------------------------------------------------------------------

class Layout:
    """Places and draws frames for one format."""

    def __init__(self, fmt, facts):
        self.fmt = FORMATS[fmt]["layout"]
        self.makerworld = FORMATS[fmt].get("makerworld", False)
        self.W, self.H = FORMATS[fmt]["size"]
        self.tall = self.fmt == "9x16"
        fmt = self.fmt
        self.cache = OrderedDict()
        self.meta = {}
        self.screens = {}
        W, H = self.W, self.H
        # The card's area above the captions (or below them, in 9:16), and its home width.
        if self.tall:
            self.area = (40, 600, W - 40, 1420)
            home = 0.78 * W
        else:
            self.area = (0.04 * W, 0.05 * H, 0.96 * W, 0.66 * H)
            home = 0.62 * W if fmt in ("16x9", "4x3") else 0.78 * W
        box = self.bbox("front-0")
        self.pose_w = box[2] - box[0]
        self.aspect = (box[3] - box[1]) / self.pose_w
        area_h = self.area[3] - self.area[1]
        self.home_w = min(home, 0.94 * area_h / self.aspect)
        self.sizes = {"head": 76 if self.tall else 72, "sub": 44 if self.tall else 42}

    # poses
    def pose(self, name, half=False):
        key = (name, half)
        if key not in self.cache:
            im = Image.open(POSES / f"{name}.png").convert("RGBA")
            sh_path = POSES / f"{name}-shadow.png"
            sh = Image.open(sh_path).convert("L") if sh_path.exists() else None
            meta = json.loads((POSES / f"{name}.json").read_text())
            if half:
                im = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
                sh = sh.resize((sh.width // 2, sh.height // 2), Image.LANCZOS) if sh else None
            self.cache[key] = (im.convert("RGBa"), sh, meta)
            while len(self.cache) > 14:
                self.cache.popitem(last=False)
        return self.cache[key]

    def bbox(self, name):
        if name not in self.meta:
            im = Image.open(POSES / f"{name}.png")
            anchor = json.loads((POSES / f"{name}.json").read_text())["anchor"]
            x0, y0, x1, y1 = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
            self.meta[name] = (x0 - anchor[0], y0 - anchor[1], x1 - anchor[0], y1 - anchor[1])
        return self.meta[name]

    # placements: (centre x, centre y, card width) of the card's centre in the frame
    def placement(self, name):
        W, H = self.W, self.H
        x0, y0, x1, y1 = self.area
        box = self.bbox("front-0")
        if name == "home":
            k = self.home_w / self.pose_w
            # Centre the card's outline, not its middle point (the edge shows below it).
            return ((x0 + x1) / 2 - (box[0] + box[2]) / 2 * k, (y0 + y1) / 2 - (box[1] + box[3]) / 2 * k, self.home_w)
        if name == "end":
            w = self.home_w * (0.6 if not self.tall else 0.72)
            k = w / self.pose_w
            block = self.end_block_height()
            card_h = self.aspect * w
            top = (H - (card_h + 70 + block)) / 2 if not self.tall else 560
            return (W / 2 - (box[0] + box[2]) / 2 * k, top + card_h / 2 - (box[1] + box[3]) / 2 * k, w)
        if name == "tap":
            # The card and the phone touching it, together as large as fits the card area, so the
            # phone (which reaches toward the camera) stays clear of the caption.
            card = self.bbox("front-0")
            k_phone = POSE_SCALE / json.loads((POSES / "phone-tap.json").read_text())["scale"]
            ph = [v * k_phone for v in self.bbox("phone-tap")]
            u = (min(card[0], ph[0]), min(card[1], ph[1]), max(card[2], ph[2]), max(card[3], ph[3]))
            ax0, ay0, ax1, ay1 = self.area
            k = 0.96 * min((ax1 - ax0) / (u[2] - u[0]), (ay1 - ay0) / (u[3] - u[1]))
            return ((ax0 + ax1) / 2 - (u[0] + u[2]) / 2 * k, (ay0 + ay1) / 2 - (u[1] + u[3]) / 2 * k, k * self.pose_w)
        if name == "pocket":
            # The home framing, pushed in 12% toward the pocket, so the card stays in frame.
            cx, cy, w = self.placement("home")
            k = w / self.pose_w
            px, py = self.pocket_px
            fx, fy = cx + px * k, cy + py * k
            z = 1.12
            return (fx + (cx - fx) * z, fy + (cy - fy) * z, w * z)
        raise ValueError(name)

    def resolve(self, place, fit=1.0):
        if place[0] == "at":
            cx, cy, w = self.placement(place[1])
            zoom = 1 + place[2]
        else:
            a, b = self.placement(place[1]), self.placement(place[2])
            cx, cy, w = (lerp(a[i], b[i], place[3]) for i in range(3))
            zoom = 1 + place[4]
        # Zoom about the frame's card area centre.
        ax = (self.area[0] + self.area[2]) / 2
        ay = (self.area[1] + self.area[3]) / 2
        if fit < 1:  # a turning card: smaller, and toward the frame's middle, where there's room
            shift = min(1.0, (1 - fit) / 0.1)
            ax, ay = lerp(ax, self.W / 2, shift), lerp(ay, self.H / 2, shift)
            cx, cy = lerp(cx, self.W / 2, shift), lerp(cy, self.H / 2, shift)
        zoom *= fit
        return ax + (cx - ax) * zoom, ay + (cy - ay) * zoom, w * zoom

    def fit_curve(self, frames):
        """For turning frames, how far to pull back so the card stays in its area: smoothed."""
        need = np.ones(len(frames))
        for i, f in enumerate(frames):
            f = (f.get("mix") or f.get("dip"))[1] if ("mix" in f or "dip" in f) else f
            if f.get("fit"):
                name = f["card"][0][0]
                b = self.bbox(name)
                k = self.home_w / self.pose_w
                h = (b[3] - b[1]) * k
                need[i] = min(1.0, 0.92 * self.H / h)  # no caption mid-turn: the whole frame
        smooth = np.array([need[max(0, i - 10): i + 11].min() for i in range(len(need))])
        kernel = np.ones(9) / 9
        return np.convolve(np.pad(smooth, 4, mode="edge"), kernel, mode="valid")

    # drawing
    def draw_card(self, frame, name, cx, cy, w):
        """The pose `name` with its shadow, its card centre at (cx, cy) and the card `w` wide."""
        k = w / self.pose_w
        half = k < 0.62  # from a half-size copy, so the QR code doesn't alias
        im, sh, meta = self.pose(name, half)
        kk = k * (2 if half else 1)
        ax, ay = meta["anchor"]
        if half:
            ax, ay = ax / 2, ay / 2
        data = (1 / kk, 0, ax - cx / kk, 0, 1 / kk, ay - cy / kk)
        layer = frame.copy()
        if sh is not None:
            s = sh.transform(layer.size, Image.AFFINE, data, Image.BILINEAR)
            layer.paste(Image.new("RGBA", layer.size, (*SHADOW_INK, 255)), (0, 0), s)
        card = im.transform(layer.size, Image.AFFINE, data, Image.BICUBIC).convert("RGBA")
        return Image.alpha_composite(layer, card)

    def frame(self, f, fit=1.0):
        if "mix" in f:
            a, b, t = f["mix"]
            fa, fb = self.frame(a, fit), self.frame(b, fit)
            return Image.blend(fa, fb, ease(t))
        if "dip" in f:
            a, b, t = f["dip"]
            bg = Image.new("RGB", (self.W, self.H), tuple(BACKGROUND))
            if t < 0.5:
                return Image.blend(self.frame(a, fit), bg, ease(2 * t))
            return Image.blend(bg, self.frame(b, fit), ease(2 * t - 1))
        W, H = self.W, self.H
        frame = Image.new("RGBA", (W, H), (*BACKGROUND, 255))
        if "card" in f:
            poses = [(n, wt) for n, wt in f["card"] if wt > 0.002]
            cx, cy, w = self.resolve(f["place"], fit)
            if len(poses) == 2:  # a crossfade between two poses in place
                a = self.draw_card(frame, poses[0][0], cx, cy, w)
                b = self.draw_card(frame, poses[1][0], cx, cy, w)
                frame = Image.blend(a, b, poses[1][1] / (poses[0][1] + poses[1][1]))
            else:
                frame = self.draw_card(frame, poses[0][0], cx, cy, w)
            k = w / self.pose_w
            if "rings" in f:
                self.draw_rings(frame, f["rings"], cx, cy, k)
            if f.get("pocket", 0) > 0:
                self.draw_pocket(frame, f["pocket"], cx, cy, k)
            if "phone3d" in f:
                self.draw_phone3d(frame, f["phone3d"], cx, cy, k, f.get("phone_t", 1), f.get("phone_a", 1))
            caption_mode = "top" if self.tall else "bottom"
        else:
            self.draw_phone_screen(frame, f)
            caption_mode = "top" if self.tall else "side"
        if f.get("caption") and f["caption"][2] > 0:
            self.draw_caption(frame, *f["caption"], caption_mode)
        if "end" in f:
            self.draw_end(frame, *f["end"])
        return frame.convert("RGB")

    def draw_rings(self, frame, phase, cx, cy, k):
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for n in range(3):
            p = phase * 1.4 - n * 0.28
            if not 0 < p < 1:
                continue
            pts = [(cx + x * k, cy + y * k) for x, y in self.ring(12 + 30 * p)]
            d.line(pts + pts[:1], fill=(*ORANGE, round(235 * (1 - p))), width=max(3, round(9 * k)))
        frame.alpha_composite(layer)

    def draw_pocket(self, frame, alpha, cx, cy, k):
        """A thin rim round the open pocket, which is too shallow to see black on black."""
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        pts = [(cx + x * k, cy + y * k) for x, y in self.pocket_rim]
        ImageDraw.Draw(layer).line(pts + pts[:1], fill=(*ORANGE, round(230 * alpha)), width=max(3, round(6 * k)))
        frame.alpha_composite(layer)

    def draw_phone3d(self, frame, name, cx, cy, k, t, alpha):
        im, sh, meta = self.pose(name)
        k = k * POSE_SCALE / meta["scale"]
        ax, ay = meta["anchor"]
        data = (1 / k, 0, ax - cx / k, 0, 1 / k, ay - cy / k)
        s = sh.transform(frame.size, Image.AFFINE, data, Image.BILINEAR).point(lambda v: round(v * (0.4 + 0.6 * t) * alpha))
        frame.paste(Image.new("RGBA", frame.size, (*SHADOW_INK, 255)), (0, 0), s)
        body = im.transform(frame.size, Image.AFFINE, data, Image.BICUBIC).convert("RGBA")
        if alpha < 1:
            body.putalpha(body.getchannel("A").point(lambda v: round(v * alpha)))
        frame.alpha_composite(body)

    def phone_box(self):
        """Where the straight-on phone goes: scale and top-left."""
        W, H = self.W, self.H
        if self.tall:
            ph = 1140
            x = W / 2
            y = 640
        else:
            ph = 0.84 * H if self.fmt != "1x1" else 0.8 * H
            x = {"16x9": 0.68, "4x3": 0.7, "1x1": 0.72}[self.fmt] * W
            y = (H - ph) / 2
        return ph / 988, x, y

    def draw_phone_screen(self, frame, f):
        kind, arg = f["screen"]
        scr = self.screen(kind, arg)
        scale, x, y = self.phone_box()
        mid = y + 988 * scale / 2
        scale *= 1 + f.get("phone_zoom", 0)
        if kind == "tap":
            x = self.W / 2  # no caption beside it: centered
        rgb = frame.convert("RGB")
        phone(rgb, scr, round(x - 230 * scale), round(mid - 494 * scale), scale)
        frame.paste(rgb)

    def screen(self, kind, arg):
        if "page" not in self.screens:
            front = Image.open(POSES / "front-0.png")
            box = front.getbbox()
            still = front.crop(box)
            self.screens["page"] = page_screen(still)
            self.screens["lock"] = Image.open(CACHE / "screen-lock.png").convert("RGB")
            self.screens["banner"] = Image.open(CACHE / "screen-banner.png").convert("RGB")
            self.screens["camera"] = Image.open(POSES / "camera.png").convert("RGB")
            self.qr_box = json.loads((POSES / "camera.json").read_text())["qr"]
        if kind == "tap":
            return slide_up(self.screens["banner"], self.screens["page"], arg)
        i = arg  # the scan: brackets 6-24, chip 30-42, press 56-66, page 64-82
        cam = camera_screen(self.screens["camera"], self.qr_box, (i - 6) / 18, (i - 30) / 12, (i - 56) / 10)
        return slide_up(cam, self.screens["page"], (i - 64) / 18)

    def draw_caption(self, frame, head, sub, alpha, mode):
        W, H = self.W, self.H
        hs, ss = self.sizes["head"], self.sizes["sub"]
        hf, sf = font("Inter-ExtraBold.ttf", hs), font("Inter-Bold.ttf", ss)
        if mode == "top":
            x, width = 70, W - 70 - 140 - 34
        elif mode == "side":
            scale, px, _ = self.phone_box()
            x = 0.07 * W
            width = px - 230 * scale - 0.05 * W - x - 34
        else:
            x, width = 0.07 * W, W - 0.14 * W - 34
        hl = wrap(head, hf, width)
        sl = wrap(sub, sf, width) if sub else []
        block = len(hl) * round(hs * 1.12) + (round(hs * 0.3) + len(sl) * round(ss * 1.3) if sl else 0)
        if mode == "top":
            y = 270
        elif mode == "side":
            y = (H - block) / 2
        else:
            y = 0.88 * H - block
        a = round(255 * alpha)
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle([x, y + 0.08 * hs, x + 12, y + block - 0.12 * ss], 6, fill=(*ORANGE, a))
        ty = y
        for line in hl:
            d.text((x + 34, ty), line, font=hf, fill=(*INK, a), anchor="la")
            ty += round(hs * 1.12)
        if sl:
            ty += round(hs * 0.3) - round(hs * 0.12)
            for line in sl:
                d.text((x + 34, ty), line, font=sf, fill=(*SUBTLE, a), anchor="la")
                ty += round(ss * 1.3)
        frame.alpha_composite(layer)

    END_LINES = [("mark", 96), ("taptilde.com", 64), ("Free · Open source", 40), ("by Thomas Butman", 30)]
    END_MAKERWORLD = [("mark", 96), ("Click Customize to make yours", 64),
                      ("Free · Open source · taptilde.com", 40), ("by Thomas Butman", 30)]

    def end_lines(self):
        return self.END_MAKERWORLD if self.makerworld else self.END_LINES
    END_GAPS = [0, 34, 22, 26]

    def end_block_height(self):
        return sum(s * 1.15 for _, s in self.end_lines()) + sum(self.END_GAPS)

    def draw_end(self, frame, i, out):
        cx, cy, w = self.placement("end")
        k = w / self.pose_w
        box = self.bbox("front-0")
        y = cy + box[3] * k + 70
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for n, ((text, size), gap) in enumerate(zip(self.end_lines(), self.END_GAPS)):
            y += gap
            a = ease((i - 6 * n) / 14) * out
            if a > 0:
                lift = round(14 * (1 - ease((i - 6 * n) / 14)))
                yy = y + size * 0.575 + lift
                if text == "mark":
                    f = font("JetBrainsMono-ExtraBold.ttf", size)
                    x = self.W / 2 - f.getlength("~/tilde card") / 2
                    d.text((x, yy), "~/", font=f, fill=(*ORANGE_DEEP, round(255 * a)), anchor="lm")
                    d.text((x + f.getlength("~/"), yy), "tilde card", font=f, fill=(*INK, round(255 * a)), anchor="lm")
                else:
                    face = "Inter-ExtraBold.ttf" if size == 64 else "Inter-Bold.ttf"
                    color = INK if size == 64 else SUBTLE
                    d.text((self.W / 2, yy), text, font=font(face, size), fill=(*color, round(255 * a)), anchor="mm")
            y += size * 1.15
        frame.alpha_composite(layer)


def encode(args):
    fmt, frames, geo, path = args
    facts = model_facts()
    lay = Layout(fmt, facts)
    lay.tap_px, lay.pocket_px, ring = geo["tap"], geo["pocket"], geo["ring"]
    lay.pocket_rim = geo["rim"]
    tx, ty = lay.tap_px
    lay.ring = lambda r: [(tx + x * r / 10, ty + y * r / 10) for x, y in ring]
    fits = lay.fit_curve(frames)
    spec = dict(FORMATS[fmt], path=path)
    spec["path"].parent.mkdir(parents=True, exist_ok=True)
    w = imageio_ffmpeg.write_frames(str(spec["path"]), spec["size"], fps=FPS, codec="libx264", pix_fmt_out="yuv420p",
                                    quality=None, macro_block_size=8,
                                    output_params=["-preset", "slow", "-movflags", "+faststart", "-crf", str(spec["crf"])])
    w.send(None)
    poster = None
    for i, f in enumerate(frames):
        im = lay.frame(f, fits[i])
        if i == geo["poster"]:
            poster = im
        w.send(np.asarray(im, dtype=np.uint8).tobytes())
    w.close()
    poster.save(spec["path"].with_suffix(".jpg"), quality=88)
    if spec.get("webm"):
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", str(spec["path"]), "-c:v", "libvpx-vp9", "-b:v", "0",
                        "-crf", "38", "-row-mt", "1", "-an", str(spec["path"].with_suffix(".webm"))], check=True)
    return fmt


def check_qr():
    """The sample's QR code must open taptilde.com: decode it from the front render."""
    im = Image.open(POSES / "camera.png").convert("L")
    text = ""
    for k in (1, 0.6, 0.4):  # OpenCV's detector misses large codes; try smaller copies too
        small = np.asarray(im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS))
        text = cv2.QRCodeDetector().detectAndDecode(small)[0]
        if text:
            break
    if text != "https://taptilde.com":
        raise SystemExit(f"QR check failed: decoded {text!r}")
    print(f"QR decodes to {text}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--exports", type=Path, default=EXPORTS,
                        help="folder for the web and social files (default: out/video/exports, git-ignored)")
    exports = parser.parse_args().exports.expanduser().resolve()
    paths = {fmt: spec.get("path") or exports / spec["name"] for fmt, spec in FORMATS.items()}
    CACHE.mkdir(parents=True, exist_ok=True)
    POSES.mkdir(parents=True, exist_ok=True)
    facts = model_facts()
    print(f"model: {facts['layers']} layers of {facts['layer_h']} mm, pause before layer {facts['pause']}")
    build_card(facts)
    flips = sorted({round(180 * ease(i / (FLIP_STEPS - 1)), 2) for i in range(FLIP_STEPS)})
    lock_screen().save(CACHE / "screen-lock.png")
    banner(lock_screen()).save(CACHE / "screen-banner.png")
    specs = pose_specs(facts, flips)
    todo = [(k, v) for k, v in specs.items() if not (POSES / f"{k}.png").exists()]
    print(f"{len(specs)} poses, {len(todo)} to render")
    # Big canvases first (the phone poses), so the pool stays busy at the end.
    todo.sort(key=lambda kv: kv[1][0] != "phone")
    with Pool(max(1, min(6, (os.cpu_count() or 2) - 2))) as pool:
        for n, _ in enumerate(pool.imap_unordered(render_pose, todo), 1):
            if n % 10 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)}")
    check_qr()

    # Points the layout needs, in pose pixels from the card's centre.
    c = centre()
    project, r = view(c, POSE_SCALE, POSE_SIZE)
    mid = np.array(POSE_SIZE) / 2
    tap = tap_point()
    tap_px = project(tap[None])[0, :2] / SS - mid
    floor_z, pc = pocket(facts)
    p = trimesh.transform_points(np.array([[pc[0], pc[1], floor_z]]), back_up())
    pocket_px = project(p)[0, :2] / SS - mid
    t = np.linspace(0, 2 * np.pi, 72, endpoint=False)
    circle = np.column_stack([tap[0] + 10 * np.cos(t), tap[1] + 10 * np.sin(t), np.full_like(t, tap[2] + 0.05)])
    ring = (project(circle)[:, :2] / SS - mid - tap_px).tolist()  # a 10 mm circle round the tap mark
    rim_r = facts["pocket_d"] / 2
    rim = np.column_stack([pc[0] + rim_r * np.cos(t), pc[1] + rim_r * np.sin(t), np.full_like(t, facts["pocket_top"])])
    rim = (project(trimesh.transform_points(rim, back_up()))[:, :2] / SS - mid).tolist()
    frames = timeline(flips)
    poster = len(frames) - 30
    geo = {"tap": tap_px.tolist(), "pocket": pocket_px.tolist(), "ring": ring, "rim": rim, "poster": poster}
    print(f"{len(frames)} frames, {len(frames) / FPS:.1f} s; encoding {len(FORMATS)} files")
    with Pool(len(FORMATS)) as pool:
        for fmt in pool.imap_unordered(encode, [(fmt, frames, geo, paths[fmt]) for fmt in FORMATS]):
            print(f"  {fmt} done")
    for path in paths.values():
        for p in [path, path.with_suffix(".webm"), path.with_suffix(".jpg")]:
            if p.exists():
                print(f"  {p}  {p.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
