"""Build the MakerWorld model video, makerworld/video/tilde-card.mp4: about 22 seconds, 1440 x 1080
(4:3, like the pictures), 30 fps, silent with captions, so it works muted and loops.

1. The card turns over: the front, then the back.
2. Customize: the name changes (Jane Doe to Ana Ribeiro), then the colors.
3. The print, from the plate up: the layers to the pause, the NFC sticker dropping into its pocket,
   the rest of the layers sealing it in.
4. A phone taps the card and the website opens.
5. The titled cover.

Everything on the card is the model's own geometry: the sample card (out/makerworld-sample), a
second one built here with another name, and the sample cut at each layer height (OpenSCAD in
Docker). The phone, its screens and the sticker are drawn. The renders are cached in out/video/,
so a second run only reassembles the frames.

    .venv/bin/python scripts/make_listing_video.py
"""

import math
import os
import subprocess
import sys
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_covers import AMBER, BACKGROUND, INK, SUBTLE, font  # noqa: E402
from make_listing_images import COLOR_SETS, STICKER, STICKER_D, outline, pause_cut, phone, sticker, upright  # noqa: E402
from render_preview import PARTS, SUPERSAMPLE, load_parts, projector, render  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "out" / "makerworld-sample"
CACHE = ROOT / "out" / "video"
OUT = ROOT / "makerworld" / "video" / "tilde-card.mp4"
W, H, FPS = 1440, 1080, 30
STAGE = (W, H - 170)  # the render area; the caption goes below it
FILL = 0.74
FADE = 10  # frames of crossfade between scenes and stills

# The second card: an example person from the app's screenshots.
ANA = {"first_name": "Ana", "last_name": "Ribeiro", "handle": "anaribeiro", "qr_code_link": "https://ana.example.com",
       "website_on_card": "ana.example.com", "back_line_1": "ana ribeiro", "back_line_2": "product lead",
       "back_line_3": "ana@example.com"}
CUSTOMIZE = [("sample", 0), ("ana", 0), ("ana", 1), ("ana", 2), ("ana", 3)]  # (card, color set)
FLIP_STEPS = 46  # the turn, eased; one render each
LAYERS = 18      # the sample: 1.8 mm at 0.1 mm layers
PAUSE = 11       # the sample's pause: before layer 11
DROP_STEPS = 14


def docker(*args, env=()):
    cmd = ["docker", "run", "--rm", "-v", f"{ROOT}:/w", "-w", "/w"]
    for e in env:
        cmd += ["-e", e]
    subprocess.run(cmd + ["openscad/openscad:dev", *args], check=True, capture_output=True)


def build_ana():
    """The second card's color bodies, from the MakerWorld file with Ana's details."""
    folder = CACHE / "ana"
    folder.mkdir(parents=True, exist_ok=True)
    defines = []
    for key, value in ANA.items():
        defines += ["-D", f'{key}="{value}"']
    for part in PARTS:
        out = folder / f"card-{part}.stl"
        if not out.exists():
            docker("openscad", "--backend=manifold", "-D", f'part="{part}"', *defines, "--export-format", "binstl",
                   "-o", f"out/video/ana/{out.name}", "makerworld/tilde-card.scad", env=["OPENSCAD_FONT_PATH=/w/fonts"])
    return folder


def build_layers():
    """The sample as printed up to each layer (just under its top, so a pocket ceiling there
    leaves no skin), as out/video/layers/<n>-<part>.stl."""
    folder = CACHE / "layers"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "cut.scad").write_text(
        'file = "";\ntop = 1;\nintersection() { import(file); translate([-1, -1, -1]) cube([200, 200, top + 1]); }\n')
    lines = []
    for n in range(1, LAYERS):
        top = round(n * 0.1 - 0.005, 3)
        for part in PARTS:
            src = SAMPLE / f"card-{part}.stl"
            out = folder / f"{n:02d}-{part}.stl"
            if out.exists() or not src.exists() or trimesh.load(src).bounds[0][2] >= top:
                continue
            lines.append(f'openscad --backend=manifold -D \'file="/w/{src.relative_to(ROOT)}"\' -D top={top} '
                         f"--export-format binstl -o out/video/layers/{out.name} out/video/layers/cut.scad")
    if lines:
        subprocess.run(["docker", "run", "--rm", "-v", f"{ROOT}:/w", "-w", "/w", "--entrypoint", "sh",
                        "openscad/openscad:dev", "-c", " && ".join(lines)], check=True, capture_output=True)
    return folder


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))


# --- renders (run in worker processes; each writes a PNG and returns its path) -------------------

def front_meshes(folder):
    return load_parts(Path(folder), show="front")


def turned(meshes, degrees):
    """Turn the card over about its short axis, so the back comes up the right way round."""
    centre = meshes["body"].bounds.mean(axis=0)
    m = trimesh.transformations.rotation_matrix(math.radians(degrees), [0, 1, 0], centre)
    return {k: v.copy().apply_transform(m) for k, v in meshes.items()}


def save(rgb, path, size=STAGE):
    Image.fromarray(rgb.clip(0, 255).astype(np.uint8)).resize(size, Image.LANCZOS).save(path)
    return str(path)


def job(spec):
    kind, path = spec[0], Path(spec[1])
    if path.exists():
        return str(path)
    if kind == "flip":
        base = front_meshes(SAMPLE)
        view = projector(base, STAGE, fill=FILL)
        rgb, _ = render(turned(base, spec[2]), PARTS, STAGE, view)
        return save(rgb, path)
    if kind == "still":
        meshes = front_meshes(spec[2])
        rgb, _ = render(meshes, COLOR_SETS[spec[3]], STAGE, projector(meshes, STAGE, fill=FILL))
        return save(rgb, path)
    # Print stages: the card as it lies on the plate, turned so the back reads upright.
    layer, sticker_z, info = spec[2], spec[3], spec[4]
    full = {k: upright(v) for k, v in load_parts(SAMPLE, show="back").items()}
    view = projector(full, STAGE, fill=FILL)
    if layer >= LAYERS:
        meshes = dict(full)
    else:
        meshes = {}
        for part in PARTS:
            f = CACHE / "layers" / f"{layer:02d}-{part}.stl"
            if f.exists():
                meshes[part] = upright(trimesh.load(f))
    if sticker_z is not None:
        meshes.update(sticker(np.array(info["centre"]), sticker_z))
    rgb, _ = render(meshes, {**PARTS, **STICKER}, STAGE, view)
    if len(spec) > 5:  # a dashed ring: (diameter, height)
        big = Image.fromarray(rgb.clip(0, 255).astype(np.uint8))
        outline(ImageDraw.Draw(big), view[0], info["centre"], spec[5][0], spec[5][1])
        big.resize(STAGE, Image.LANCZOS).save(path)
        return str(path)
    return save(rgb, path)


# --- frames ----------------------------------------------------------------------------------------

def stage_frame(still, caption=None, caption_alpha=1.0):
    frame = Image.new("RGB", (W, H), BACKGROUND)
    frame.paste(still, (0, 10))
    if caption and caption_alpha > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        a = round(255 * caption_alpha)
        draw.rounded_rectangle([80, H - 122, 92, H - 62], 6, fill=(*AMBER, a))
        draw.text((116, H - 92), caption, font=font("Inter-ExtraBold.ttf", 52), fill=(*INK, a), anchor="lm")
        frame.paste(layer, (0, 0), layer)
    return frame


def blend(a, b, t):
    return Image.blend(a, b, ease(t))


def phone_screens():
    """The tapping phone's two screens, 540 x 1200: its home screen, and the card's website."""
    home = Image.new("RGB", (540, 1200), (24, 27, 33))
    d = ImageDraw.Draw(home)
    for y in range(1200):
        c = 24 + round(18 * y / 1200)
        d.line([(0, y), (540, y)], fill=(c, c + 4, c + 12))
    d.text((270, 260), "9:41", font=font("Inter-Bold.ttf", 120), fill=(236, 236, 236), anchor="mm")
    d.text((270, 350), "Thursday, October 8", font=font("Inter-Bold.ttf", 30), fill=(170, 172, 178), anchor="mm")

    page = Image.new("RGB", (540, 1200), (246, 245, 241))
    d = ImageDraw.Draw(page)
    d.rectangle([0, 0, 540, 150], fill=(232, 231, 226))
    d.rounded_rectangle([30, 70, 510, 130], 30, fill=(255, 255, 255))
    d.text((270, 100), "example.com", font=font("Inter-Bold.ttf", 28), fill=(60, 62, 66), anchor="mm")
    d.ellipse([195, 230, 345, 380], fill=(22, 24, 27))
    d.text((270, 305), "JD", font=font("Inter-ExtraBold.ttf", 56), fill=AMBER, anchor="mm")
    d.text((270, 450), "Jane Doe", font=font("Inter-ExtraBold.ttf", 58), fill=INK, anchor="mm")
    d.text((270, 515), "Product designer", font=font("Inter-Bold.ttf", 32), fill=SUBTLE, anchor="mm")
    for i, w in enumerate([400, 360, 380, 300]):
        d.rounded_rectangle([270 - w // 2, 600 + i * 46, 270 + w // 2, 622 + i * 46], 11, fill=(218, 216, 210))
    d.rounded_rectangle([130, 830, 410, 910], 40, fill=AMBER)
    d.text((270, 870), "Say hello", font=font("Inter-ExtraBold.ttf", 34), fill=INK, anchor="mm")
    CACHE.mkdir(parents=True, exist_ok=True)
    home.save(CACHE / "screen-home.png")
    page.save(CACHE / "screen-page.png")
    return CACHE / "screen-home.png", CACHE / "screen-page.png"


def tap_point():
    """Where the front's tap mark is in the stage: the centre of the accent color right of the QR
    field, projected as the sample's front still is."""
    meshes = front_meshes(SAMPLE)
    project, _ = projector(meshes, STAGE, fill=FILL)
    accent = meshes["accent"].vertices
    right = accent[accent[:, 0] > accent[:, 0].max() - 6]
    p = project(right.mean(axis=0, keepdims=True))[0]
    return p[0] / SUPERSAMPLE, p[1] / SUPERSAMPLE + 10


def tap_scene(card, screens):
    """The card smaller and to the left; a phone slides in beside its tap mark, waves pass
    between them, and the phone opens the website."""
    k, ox, oy = 0.8, 20, 90
    small = card.resize((round(card.width * k), round(card.height * k)), Image.LANCZOS)
    stage = Image.new("RGB", card.size, BACKGROUND)
    stage.paste(small, (ox, oy - 10))
    tx, ty = tap_point()
    tx, ty = tx * k + ox, (ty - 10) * k + oy
    scale = 0.7
    ph = round(988 * scale)
    end_x, y = round(tx + 70), round(ty - ph / 2)
    caption = "Tap it or scan it: no app needed"
    for i in range(110):
        f = stage_frame(stage, caption, min(1, i / 8))
        x = round(W + 40 + (end_x - W - 40) * ease(i / 22))
        if i >= 24:  # in reach: waves from the tap mark toward the phone
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            for n in range(3):
                phase = ((i - 24) / 18 + n / 3) % 1
                r = 24 + 60 * phase
                d.arc([tx - r, ty - r, tx + r, ty + r], -50, 50, fill=(*AMBER, round(230 * (1 - phase))), width=7)
            f.paste(layer, (0, 0), layer)
        phone(f, screens[1] if i >= 44 else screens[0], x, y, scale)
        yield f


def hold(frames, caption):
    """Stage frames for a list of stills, the caption fading in; repeated stills share one frame."""
    made = {}
    for i, im in enumerate(frames):
        alpha = min(1, i / 8)
        key = (id(im), alpha)
        if key not in made:
            made[key] = stage_frame(im, caption, alpha)
        yield made[key]


def renders(floor_z, top, pocket_d, full_top, info, ana):
    flips = [round(180 * ease(i / (FLIP_STEPS - 1)), 2) for i in range(FLIP_STEPS)]
    drops = [floor_z + 9 * (1 - ease(i / (DROP_STEPS - 1))) for i in range(DROP_STEPS)]
    jobs = [("flip", CACHE / f"flip-{a:06.2f}.png", a) for a in sorted(set(flips))]
    jobs += [("still", CACHE / f"still-{c}-{p}.png", str(SAMPLE if c == "sample" else ana), p) for c, p in CUSTOMIZE]
    jobs += [("print", CACHE / f"layer-{n:02d}.png", n, floor_z if n >= PAUSE else None, info) for n in range(1, LAYERS + 1)]
    jobs += [("print", CACHE / "pause-ring.png", PAUSE - 1, None, info, (pocket_d, top))]
    jobs += [("print", CACHE / f"drop-{i:02d}.png", PAUSE - 1, z, info) for i, z in enumerate(drops)]
    jobs += [("print", CACHE / "sealed-ring.png", LAYERS, floor_z, info, (STICKER_D, full_top))]
    todo = [j for j in jobs if not Path(j[1]).exists()]
    print(f"{len(jobs)} renders, {len(todo)} to do")
    with Pool(max(1, (os.cpu_count() or 2) - 1)) as pool:
        for n, _ in enumerate(pool.imap_unordered(job, todo), 1):
            if n % 10 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)}")
    return flips


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    ana = build_ana()
    build_layers()
    _, top, floor_z, centre, pocket_d = pause_cut()  # centre: in the upright print frame
    full_top = float(trimesh.load(SAMPLE / "card-body.stl").bounds[1][2])
    info = {"centre": [float(c) for c in centre]}
    flips = renders(floor_z, top, pocket_d, full_top, info, ana)

    cache = {}

    def img(name):
        if name not in cache:
            cache[name] = Image.open(CACHE / name).convert("RGB")
        return cache[name]

    def turn():
        frames = [img(f"flip-{a:06.2f}.png") for a in [flips[0]] * 28 + flips + [flips[-1]] * 40]
        yield from hold(frames[:50], "A business card you print in one go")
        yield from hold(frames[50:], "Your details on the back")

    def customize():
        stills = [img(f"still-{c}-{p}.png") for c, p in CUSTOMIZE]
        made = {}
        for k, im in enumerate(stills):
            for _ in range(26):
                yield made.setdefault(id(im), stage_frame(im, "Type your name. Pick your colors."))
            if k + 1 < len(stills):
                for t in range(FADE):
                    yield stage_frame(blend(im, stills[k + 1], (t + 1) / (FADE + 1)), "Type your name. Pick your colors.")

    def print_scene():
        layers = [img(f"layer-{n:02d}.png") for n in range(1, LAYERS + 1)]
        yield from hold([im for im in layers[: PAUSE - 1] for _ in range(4)], "Printed face down, layer by layer")
        drop = [img(f"drop-{i:02d}.png") for i in range(DROP_STEPS)]
        yield from hold([img("pause-ring.png")] * 26 + drop + [drop[-1]] * 12, "At the pause, drop in an NFC sticker")
        yield from hold([im for im in layers[PAUSE - 1:] for _ in range(5)] + [img("sealed-ring.png")] * 34,
                        "The print seals it in, out of sight")

    def ending():
        cover = Image.open(ROOT / "makerworld" / "images" / "covers" / "cover-card-title.png").convert("RGB")
        cover = cover.resize((W, H), Image.LANCZOS)
        for _ in range(84):
            yield cover

    screens = phone_screens()
    scenes = [turn(), customize(), print_scene(), tap_scene(img("still-sample-0.png"), screens), ending()]

    writer = imageio_ffmpeg.write_frames(str(OUT), (W, H), fps=FPS, codec="libx264", pix_fmt_out="yuv420p", quality=None,
                                         output_params=["-crf", "18", "-preset", "slow", "-movflags", "+faststart"],
                                         macro_block_size=8)
    writer.send(None)
    count = 0

    def send(frame):
        nonlocal count
        writer.send(np.asarray(frame, dtype=np.uint8).tobytes())
        count += 1

    # Stream the scenes, crossfading each one's last FADE frames into the next one's first.
    tail = []
    for scene in scenes:
        head = [next(scene) for _ in range(FADE)] if tail else []
        for t, (a, b) in enumerate(zip(tail, head)):
            send(blend(a, b, (t + 1) / (FADE + 1)))
        buffer = deque()
        for frame in scene:
            buffer.append(frame)
            if len(buffer) > FADE:
                send(buffer.popleft())
        tail = list(buffer)
    for frame in tail:
        send(frame)
    writer.close()
    print(f"wrote {OUT.relative_to(ROOT)}: {count} frames, {count / FPS:.1f} s")


if __name__ == "__main__":
    main()
