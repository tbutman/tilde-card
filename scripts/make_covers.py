"""Build the MakerWorld cover options in makerworld/images/covers/, 1600 x 1200 PNGs:

- cover-card.png: the card on its own
- cover-card-app.png: the card and the app on a phone (the layout of makerworld/images/01-cover.png)
- cover-card-title.png, cover-card-app-title.png: the same with a title

From the repo's own assets: the sample card's render (out/makerworld-sample/preview.png, written
by build.sh), the app screenshot makerworld/images/05-app-share.png and the fonts in fonts/. The
phone is drawn here.

    .venv/bin/python scripts/make_covers.py
"""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "makerworld" / "images" / "covers"
W, H = 1600, 1200
BACKGROUND = (214, 211, 204)  # render_preview.py's background
INK = (22, 24, 27)            # #16181b, the card's black
SUBTLE = (72, 74, 79)         # the subtitle's dark grey
AMBER = (255, 159, 28)        # #ff9f1c
BRAND = "~/tilde card"
TITLE = ["Parametric NFC + QR", "Business Card"]
SUBTITLE = ["Your name, link and colours.", "Customize it in your browser. Free."]

# The phone, at scale 1: measured from the original cover (a 540 x 1200 screenshot shown at 0.8).
PHONE = (460, 988)            # outer size
PHONE_R = 56                  # outer corner radius
BEZEL = 14                    # frame to screen
SCREEN_R = 44
FRAME = (20, 21, 24)
SHADOW = (10, 18, 0.35)       # drop, blur radius, opacity
SS = 4                        # supersampling for the rounded corners


def font(name, size):
    return ImageFont.truetype(str(ROOT / "fonts" / name), size)


def card_render():
    """The render (1600 x 1100, on the cover's background) and the card's box in it."""
    image = Image.open(ROOT / "out" / "makerworld-sample" / "preview.png").convert("RGB")
    ink = np.abs(np.asarray(image).astype(int) - BACKGROUND).sum(axis=2) > 12
    ys, xs = np.nonzero(ink)
    return image, (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def rounded_mask(size, radius):
    w, h = size
    mask = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius * SS, fill=255)
    return mask.resize(size, Image.LANCZOS)


def place_phone(cover, x, y, scale=1.0):
    """The phone with the Share screen, outer top-left at (x, y), and its shadow."""
    w, h = round(PHONE[0] * scale), round(PHONE[1] * scale)
    bezel, drop, blur = round(BEZEL * scale), SHADOW[0] * scale, SHADOW[1] * scale
    shadow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle([x, y + drop, x + w - 1, y + h - 1 + drop], PHONE_R * scale, fill=255)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: round(v * SHADOW[2]))
    cover.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0), shadow)
    body = Image.new("RGB", (w, h), FRAME)
    sw, sh = w - 2 * bezel, h - 2 * bezel
    screen = Image.open(ROOT / "makerworld" / "images" / "05-app-share.png").convert("RGB").resize((sw, sh), Image.LANCZOS)
    body.paste(screen, (bezel, bezel), rounded_mask((sw, sh), SCREEN_R * scale))
    cover.paste(body, (x, y), rounded_mask((w, h), PHONE_R * scale))


def place_card(cover, render, box, x, y, card_width):
    """The card scaled so it is `card_width` wide, its top-left corner at (x, y). The whole render
    is scaled and pasted, background and all, so the card resamples as in the original cover."""
    scale = card_width / (box[2] - box[0])
    frame = render.resize((round(render.width * scale), round(render.height * scale)), Image.LANCZOS)
    cover.paste(frame, (round(x - box[0] * scale), round(y - box[1] * scale)))
    return round((box[3] - box[1]) * scale)


def draw_title(cover, x, y, title_size, subtitle_size, subtitle_lines):
    """Brand line, title and subtitle from (x, y); returns the bottom of the block."""
    draw = ImageDraw.Draw(cover)
    brand = font("JetBrainsMono-ExtraBold.ttf", round(title_size * 0.5))
    title = font("Inter-ExtraBold.ttf", title_size)
    subtitle = font("Inter-Bold.ttf", subtitle_size)
    draw.text((x, y), BRAND, font=brand, fill=AMBER)
    y += round(title_size * 0.85)
    for line in TITLE:
        draw.text((x, y), line, font=title, fill=INK)
        y += round(title_size * 1.1)
    y += round(title_size * 0.3)
    for line in subtitle_lines:
        draw.text((x, y), line, font=subtitle, fill=SUBTLE)
        y += round(subtitle_size * 1.3)
    return y


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    render, box = card_render()
    card_w, card_h = box[2] - box[0], box[3] - box[1]

    # 1. The card alone, as large as fits with an even margin.
    cover = Image.new("RGB", (W, H), BACKGROUND)
    width = 1440
    height = round(card_h * width / card_w)
    place_card(cover, render, box, (W - width) // 2, (H - height) // 2, width)
    cover.save(OUT / "cover-card.png", optimize=True)

    # 2. Card and app, as the original cover: the render at 1104 px wide (0.69), its frame's
    # top-left at (-22, 244); the phone at (1070, 106).
    cover = Image.new("RGB", (W, H), BACKGROUND)
    cover.paste(render.resize((1104, 759), Image.LANCZOS), (-22, 244))
    place_phone(cover, 1070, 106)
    cover.save(OUT / "cover-card-app.png", optimize=True)

    # 3. The card with the title above it.
    cover = Image.new("RGB", (W, H), BACKGROUND)
    width = 1300
    height = round(card_h * width / card_w)
    place_card(cover, render, box, (W - width) // 2, H - 70 - height, width)
    draw_title(cover, 96, 80, 92, 44, [" ".join(SUBTITLE)])
    cover.save(OUT / "cover-card-title.png", optimize=True)

    # 4. Card and app with the title top left, over the card; the phone keeps the right.
    cover = Image.new("RGB", (W, H), BACKGROUND)
    width = 930
    height = round(card_h * width / card_w)
    place_card(cover, render, box, 56, H - 96 - height, width)
    place_phone(cover, 1088, 112, 0.98)
    draw_title(cover, 72, 88, 80, 44, SUBTITLE)
    cover.save(OUT / "cover-card-app-title.png", optimize=True)
    for name in ["cover-card", "cover-card-app", "cover-card-title", "cover-card-app-title"]:
        print(f"wrote makerworld/images/covers/{name}.png")


if __name__ == "__main__":
    main()
