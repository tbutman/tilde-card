"""Build the MakerWorld model pictures in makerworld/images/: 1600 x 1200 (4:3, the ratio MakerWorld
recommends, so its thumbnails show them whole) on the covers' background.

- 02-both-sides.png: the sample card's front and back, the four colors
- 03-front.png, 04-back.png: the flat front and back drawings, padded to 4:3 (from
  out/makerworld-sample/card-top-surface.png and card-back-surface.png)
- 05-sticker.png: the NFC sticker going in at the pause, from the sample's own geometry cut at the
  pause height
- 06-colors.png: the sample card in four color sets (the card's color settings)
- 07-tilde-app.png: the three app screenshots (makerworld/images/app/) on phones

From the sample card build.sh writes (out/makerworld-sample), the fonts in fonts/ and OpenSCAD in
Docker (for the cut at the pause). The sticker is drawn here: a 25 mm disc with a coil.

    .venv/bin/python scripts/make_listing_images.py
"""

import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_covers import AMBER, BACKGROUND, BEZEL, FRAME, INK, PHONE, PHONE_R, SCREEN_R, SHADOW, SUBTLE, font, rounded_mask  # noqa: E402
from render_preview import PARTS, SUPERSAMPLE, load_parts, projector, render  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "makerworld" / "images"
SAMPLE = ROOT / "out" / "makerworld-sample"
WORK = ROOT / "out" / "listing"
W, H = 1600, 1200

# Color sets for 06-colors.png: (card, light, accent, window bar). The QR code needs a dark card and
# a light color, so every set keeps that.
COLOR_SETS = [
    PARTS,
    {"body": (27, 42, 74), "light": (241, 239, 232), "accent": (245, 197, 24), "chrome": (120, 130, 150)},
    {"body": (22, 24, 27), "light": (241, 239, 232), "accent": (0, 174, 66), "chrome": (142, 144, 137)},
    {"body": (96, 20, 30), "light": (241, 232, 214), "accent": (240, 170, 60), "chrome": (150, 120, 110)},
]
STICKER = {"paper": (236, 234, 226), "coil": (196, 124, 60)}
STICKER_D = 25.0  # the round NTAG215 stickers the listing recommends
APP = [("05-app-share.png", "Your card on your phone"), ("06-app-picker.png", "Choose what a tap shares"),
       ("07-app-met.png", "Remember who you met")]


def to_image(rgb, size):
    return Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).resize(size, Image.LANCZOS)


def card(meshes, colors=PARTS, size=(W, H), fill=0.86):
    rgb, _ = render(meshes, colors, size, projector(meshes, size, fill=fill))
    return to_image(rgb, size)


def pad(src, out, margin=100):
    """A flat drawing on the background with `margin` around it, padded (not scaled) to 4:3."""
    im = Image.open(src).convert("RGBA")
    w = max(im.width + 2 * margin, round((im.height + 2 * margin) * 4 / 3))
    h = round(w * 3 / 4)
    canvas = Image.new("RGB", (w, h), BACKGROUND)
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2), im)
    canvas.save(out, optimize=True)


def upright(mesh):
    """Turn a part as printed (front down) a half turn on the bed, so the back reads upright."""
    return mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 0, 1]))


def back_parts():
    return {name: upright(mesh) for name, mesh in load_parts(SAMPLE, show="back").items()}


def openscad(scad, out, *defines):
    subprocess.run(["docker", "run", "--rm", "-v", f"{ROOT}:/w", "-w", "/w", "openscad/openscad:dev", "openscad",
                    "--backend=manifold", *defines, "--export-format", "binstl", "-o", out, scad],
                   check=True, capture_output=True)


def pause_cut():
    """The sample's parts as printed up to the pause, the pocket's floor height and its centre.
    The pause height comes from the model's own PRINTER echo; the pocket is found as the round
    floor below it."""
    log = subprocess.run(["docker", "run", "--rm", "-v", f"{ROOT}:/w", "-w", "/w", "-e", "OPENSCAD_FONT_PATH=/w/fonts",
                          "openscad/openscad:dev", "openscad", "--backend=manifold", "-D", 'part="chrome"',
                          "--export-format", "binstl", "-o", "out/listing/echo.stl", "makerworld/tilde-card.scad"],
                         capture_output=True, text=True).stderr
    top = float(re.search(r"pocket_top=([0-9.]+)", log).group(1))
    (WORK / "cut.scad").write_text(
        'file = "";\ntop = 1;\nintersection() { import(file); translate([-1, -1, -1]) cube([200, 200, top + 1]); }\n')
    parts = {}
    for name in PARTS:
        src = SAMPLE / f"card-{name}.stl"
        if not src.exists() or trimesh.load(src).bounds[0][2] >= top - 1e-6:
            continue  # nothing of it is printed yet (the window bar is all above the pause)
        out = WORK / f"pause-{name}.stl"
        # Just under the pocket's ceiling: a cut exactly on it leaves a skin over the pocket.
        openscad("out/listing/cut.scad", f"out/listing/{out.name}", "-D", f'file="/w/{src.relative_to(ROOT)}"', "-D", f"top={top - 0.01}")
        parts[name] = upright(trimesh.load(out))
    body = parts["body"]
    tris, normals = body.triangles, body.face_normals
    floor_z = max(z for z in np.unique(tris[:, :, 2].round(4)) if z < top - 0.02)
    floor = tris[(np.abs(tris[:, :, 2] - floor_z).max(axis=1) < 1e-4) & (normals[:, 2] > 0.99)].reshape(-1, 3)
    centre = (floor.min(axis=0) + floor.max(axis=0)) / 2
    return parts, top, floor_z, centre[:2], np.ptp(floor[:, 0])


def sticker(centre, z):
    """A round sticker lying in the pocket: a paper disc and a coil of three rings on it."""
    paper = trimesh.creation.cylinder(radius=STICKER_D / 2, height=0.12, sections=128)
    paper.apply_translation([centre[0], centre[1], z + 0.06])
    rings = [trimesh.creation.annulus(r_min=r - 0.45, r_max=r, height=0.02, sections=128) for r in (10.6, 9.6, 8.6)]
    coil = trimesh.util.concatenate(rings + [trimesh.creation.box([2.6, 2.6, 0.02])])
    coil.apply_translation([centre[0], centre[1], z + 0.13])
    return {"paper": paper, "coil": coil}


def outline(draw, project, centre, d, z, dash=True):
    """A dashed amber circle of diameter `d` at height z, in a render's supersampled pixels."""
    t = np.linspace(0, 2 * np.pi, 121)
    pts = project(np.column_stack([centre[0] + d / 2 * np.cos(t), centre[1] + d / 2 * np.sin(t), np.full_like(t, z)]))
    width = 4 * SUPERSAMPLE
    for i in range(0, len(t) - 1, 2 if dash else 1):
        draw.line([tuple(pts[i, :2]), tuple(pts[i + 1, :2])], fill=AMBER, width=width)


def step_label(tile, number, text):
    draw = ImageDraw.Draw(tile)
    r = 30
    draw.ellipse([40, 36, 40 + 2 * r, 36 + 2 * r], fill=AMBER)
    digit = font("Inter-ExtraBold.ttf", 36)
    draw.text((40 + r, 36 + r), str(number), font=digit, fill=INK, anchor="mm")
    draw.text((40 + 2 * r + 20, 36 + r), text, font=font("Inter-Bold.ttf", 38), fill=INK, anchor="lm")


def sticker_steps():
    parts, top, floor_z, centre, pocket_d = pause_cut()
    tile = (W // 2, H // 2)
    full_back = back_parts()
    front = load_parts(SAMPLE, show="front")
    # Steps 1-3 share one view, so the card stays put while it is printed.
    view = projector(full_back, tile, fill=0.84)
    colors = {**PARTS, **STICKER}
    tiles = []

    rgb, _ = render(parts, colors, tile, view)
    big = Image.fromarray(rgb.clip(0, 255).astype(np.uint8))
    outline(ImageDraw.Draw(big), view[0], centre, pocket_d, top)
    tiles.append((big.resize(tile, Image.LANCZOS), "Print to the pause"))

    rgb, _ = render({**parts, **sticker(centre, floor_z)}, colors, tile, view)
    tiles.append((to_image(rgb, tile), "Drop the sticker in"))

    rgb, _ = render(full_back, colors, tile, view)
    big = Image.fromarray(rgb.clip(0, 255).astype(np.uint8))
    outline(ImageDraw.Draw(big), view[0], centre, STICKER_D, full_back["body"].bounds[1][2])
    tiles.append((big.resize(tile, Image.LANCZOS), "Resume: it's sealed in"))

    tiles.append((card(front, size=tile, fill=0.84), "Flip it: the front"))

    canvas = Image.new("RGB", (W, H), BACKGROUND)
    for i, (im, text) in enumerate(tiles):
        step_label(im, i + 1, text)
        canvas.paste(im, ((i % 2) * tile[0], (i // 2) * tile[1]))
    canvas.save(IMAGES / "05-sticker.png", optimize=True)


def both_sides():
    canvas = Image.new("RGB", (W, H), BACKGROUND)
    size = (1100, 756)
    for show, (x, y) in [("front", (-30, 40)), ("back", (530, 420))]:
        meshes = back_parts() if show == "back" else load_parts(SAMPLE, show=show)
        rgb, covered = render(meshes, PARTS, size, projector(meshes, size, fill=0.9))
        im = to_image(rgb, size)
        mask = Image.fromarray((covered * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
        canvas.paste(im, (x, y), mask)
    canvas.save(IMAGES / "02-both-sides.png", optimize=True)


def colors():
    meshes = load_parts(SAMPLE, show="front")
    tile = (W // 2, H // 2)
    canvas = Image.new("RGB", (W, H), BACKGROUND)
    for i, palette in enumerate(COLOR_SETS):
        canvas.paste(card(meshes, palette, tile, fill=0.82), ((i % 2) * tile[0], (i // 2) * tile[1]))
    canvas.save(IMAGES / "06-colors.png", optimize=True)


def phone(canvas, screen, x, y, scale):
    w, h = round(PHONE[0] * scale), round(PHONE[1] * scale)
    bezel = round(BEZEL * scale)
    shadow = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(shadow).rounded_rectangle([x, y + SHADOW[0] * scale, x + w - 1, y + h - 1 + SHADOW[0] * scale],
                                             PHONE_R * scale, fill=255)
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW[1] * scale)).point(lambda v: round(v * SHADOW[2]))
    canvas.paste(Image.new("RGB", canvas.size, (0, 0, 0)), (0, 0), shadow)
    body = Image.new("RGB", (w, h), FRAME)
    sw, sh = w - 2 * bezel, h - 2 * bezel
    shot = Image.open(screen).convert("RGB").resize((sw, sh), Image.LANCZOS)
    body.paste(shot, (bezel, bezel), rounded_mask((sw, sh), SCREEN_R * scale))
    canvas.paste(body, (x, y), rounded_mask((w, h), PHONE_R * scale))
    return w, h


def tilde_app():
    canvas = Image.new("RGB", (W, H), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    scale = 0.92
    pw, ph = round(PHONE[0] * scale), round(PHONE[1] * scale)
    gap = (W - 3 * pw) // 4
    label = font("Inter-Bold.ttf", 36)
    for i, (name, text) in enumerate(APP):
        x = gap + i * (pw + gap)
        phone(canvas, IMAGES / "app" / name, x, 50, scale)
        draw.text((x + pw // 2, 50 + ph + 60), text, font=label, fill=SUBTLE, anchor="mm")
    canvas.save(IMAGES / "07-tilde-app.png", optimize=True)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    pad(SAMPLE / "card-top-surface.png", IMAGES / "03-front.png")
    pad(SAMPLE / "card-back-surface.png", IMAGES / "04-back.png")
    both_sides()
    colors()
    tilde_app()
    sticker_steps()
    for name in ["02-both-sides", "03-front", "04-back", "05-sticker", "06-colors", "07-tilde-app"]:
        print(f"wrote makerworld/images/{name}.png")


if __name__ == "__main__":
    main()
