# Design and build notes

The technical side of the card: how the model is built, checked and generated. To print one, see
[PRINTING.md](../PRINTING.md).

## Specifications

- **Size:** ID-1 (85.60 × 53.98 mm, 3.2 mm corners), 1.6 mm thick; 1.8 mm for thick stickers.
- **QR code:** generated in `card.scad` from `qr_code_link`: byte mode, version 1–3 with error
  correction M (or L when M can't hold the link), up to 53 characters. The modules scale to fill a
  fixed 39.6 mm white field that includes the full 4-module quiet zone: 1.37 mm (version 1),
  1.2 mm (version 2, as for `https://tbutman.com/hello`) or 1.07 mm (version 3). Black modules on
  white; the white is a 0.6 mm inlay, flush with the face.
- **NFC (optional):** `nfc_sticker = "none"` leaves out the pocket and the tap marker, for a QR
  card with no pause; the QR code keeps its place. Otherwise, a 25 mm NTAG215 sticker in a 25.3 mm pocket against the right edge, under the QR code,
  with 0.8 mm of plastic between it and the front face (the 0.6 mm inlay and 0.2 mm of black, so
  the tag can't show through the white field). The pocket is 0.2 mm deep for stickers 0.10–0.20 mm
  thick, or 0.4 mm deep with `nfc_sticker = "thick"`, which makes the card 1.8 mm thick. A tap marker (NFC waves, not the EMVCo payment symbol, and
  `tap_label`, "tap" by default), turned to read upwards, sits in the strip right of the QR code,
  over the tag. The waves and the label each take one of the card's colors (`tap_waves_color`,
  `tap_label_color`: `accent`, `light` or `chrome`; by default amber waves and a light label), on
  both sides; each goes into that color's inlay part, flush with the face. A longer label shrinks to fit the QR code's height, down to the
  nozzle's smallest text (about 14 characters on 0.4 mm, 17 on 0.2 mm); an empty one leaves just
  the waves. `back_tap_mark` (`waves` or `label`) repeats the marker on the back: the waves, plus
  `tap_label` for `label`, turned like the front's, in the same strip seen from behind, so it sits
  over the tag. With the mark on, the back's lines (and the terminal window) start 2.69 mm further
  right, a `text_gap` past the strip, on all three styles; with it off, nothing moves.
  The back's mark uses the same two colors. On a None back the mark brings back the back's inlay
  layers (about one more color change per layer: 6 layers on 0.2 mm, 3 on 0.4 mm), and with the
  window bar color the gray filament too; the window bar color on the front adds it to the front's
  layers the same way.
  `verify.py` lists the sample's reviewed spots at both positions.
- **Back:** `back_style` is `terminal`, `plain` or `none` (plain black). Both designs print the
  same three lines, `back_line_1` to `back_line_3`; an empty one is skipped. The terminal style is
  a window: a gray title bar (three dots and a rule), then a session (`$ ` and `terminal_command`,
  `whoami` by default, the three lines, a cursor) anchored under it, inlaid 0.6 mm. The plain style
  prints the lines in Inter, centered vertically: the first larger, the second in amber. Both shrink
  to fit like the front. The back reads correctly when the card is turned over sideways.
- **Print orientation:** the front prints face-down (`face_down = "front"`), because the plate
  side came out flat and matte on the first sample and the top side came out ridged. The STLs
  are exported already lying that way: the model turned over about its long axis, a rotation
  rather than a mirror. `verify.py` turns each face back the right way round before checking it.
- **Type:** Inter (ExtraBold; Bold for "tap" on the 0.2 mm version) and JetBrains Mono ExtraBold, the site's
  own typefaces, unaltered. Tuned for a 0.2 mm nozzle on 0.1 mm layers: cap heights of 2.6 mm or
  more, every stroke at least 0.3 mm and every gap at least 0.22 mm, on both faces.

Two versions are built from the same model, `out/nozzle-0.2/` and `out/nozzle-0.4/`; see
[Choose a nozzle](../PRINTING.md#choose-a-nozzle).

## Files

| Path | What |
| --- | --- |
| `card.scad` | The parametric model, one self-contained file. The Customizer sections at the top are the settings people change, one help line each (MakerWorld shows only one); `[Hidden]` holds the layout. The defaults are the sample card, Jane Doe. |
| `card.local.example.scad` | A template for `card.local.scad` (git-ignored): your own settings, one `setting = value;` per line, which `build.sh` passes to OpenSCAD as `-D` flags. |
| `makerworld/tilde-card.scad` | The copy uploaded to MakerWorld's customizer, written by `scripts/make_makerworld.py`: no font file lines, and the example person Jane Doe as the defaults. Never edited by hand. |
| `out/makerworld-sample/`, `out/makerworld-sample-qr-only-plain/` | Cards built from the MakerWorld copy, to check it renders and passes the checks: the default, and one with no NFC sticker and the plain back (its first line typed as "Jane Doe"). |
| `out/nozzle-{0.2,0.4}/card-{body,light,accent,chrome}.stl` | The sample card (Jane Doe): one STL per color (black, white, orange, gray), per nozzle, for stickers up to 0.2 mm. |
| `out/nozzle-{0.2,0.4}-thick-sticker/` | The same for stickers up to 0.4 mm: a 1.8 mm card with a deeper pocket. |
| `out/nozzle-*/card-{top,back}-surface.png` | Each face as printed, rasterized from the STLs (the back as seen from behind); the QR check decodes the front. |
| `out/nozzle-*/preview.png` | A 3/4 render of the front, from the color STLs. |
| `out/local/` | Your own card, built from `card.local.scad` when it exists, in the same layout as `out/`. Git-ignored. |
| `fonts/` | Static instances of the site's variable fonts (SIL Open Font License; see the license files). |
| `scripts/` | Checks (`verify.py`, `test_qr.py`), the preview render, the MakerWorld copy and the MakerWorld cover options (`make_covers.py`, into `makerworld/images/covers/`, and the chosen one to `makerworld/images/01-cover.png`). |

## Build

Needs Docker (OpenSCAD runs in the official `openscad/openscad:dev` image, so nothing needs
installing) and Python 3.10 or newer (Homebrew's `python3.13` here):

```bash
python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt
./build.sh
.venv/bin/python scripts/test_qr.py
```

For each nozzle (`./build.sh 0.2` builds just one) and sticker thickness, `build.sh` exports the
four STLs, runs the checks below and re-renders the preview: the sample card into `out/`, and, if
`card.local.scad` exists, your own card into `out/local/` (copy `card.local.example.scad` to start). Then it writes the MakerWorld copy
and builds and checks a sample card from it, with the fonts found by name as MakerWorld finds
them. To try settings interactively, open `card.scad` in any recent OpenSCAD and use the
Customizer.

`card.scad` refuses to render, with a message saying what to change, if the link is over 53
characters, if a name, handle, website or line on the back won't fit at the nozzle's smallest
printable size (`min_cap`), if a module is under 1 mm, if the inlay is under 0.4 mm, if text is under `min_cap`, if a thickness is not a whole
number of layers, or if the NFC pocket has fewer than two layers over it or less than 2 mm of wall
to any edge. The `nozzle` parameter (0.2 or 0.4) sets those limits (`layer_h`,
`min_stroke`, `min_gap`, `min_cap`) and the few design differences; `build.sh` passes the same
limits to `verify.py`.

## Checks

`scripts/verify.py` checks the exported STLs, not the source:

- every color body is manifold (each edge shared by exactly two triangles);
- the front, rasterized from the STLs in print colors, decodes with ZXing to exactly the link:
  at 20 px/mm, at 4 px/mm, and with a heavy blur. OpenCV's decoder runs too, as a warning only:
  it misses some valid symbols (for `https://tbutman.com/hello`, masks 5 and 6 at full
  resolution, including segno's own), which ZXing reads;
- on both faces, opening each text mask with a `min_stroke` disk (0.3 mm / 0.5 mm) loses nothing
  larger than a glyph-corner sliver (0.06 mm²): no stroke is thinner than that. Pointed stroke
  ends can lose a little more though the stroke is wide enough, so each reviewed one is listed in
  `KNOWN_THIN_TIPS`, matched by position so a change to the text brings the check back (currently
  the four arm tips of the `x` in the sample's `jane@example.com` on the 0.4 mm back, 0.072 mm²
  each: they print slightly blunt);
- closing it with a `min_gap` disk (0.22 mm, one 0.2 mm line / 0.34 mm, the slicer's narrowest
  wall for a 0.4 mm nozzle) fills nothing: no gap inside or between letters is narrower. Acute
  inner corners always fill a little, so each reviewed one is listed in `KNOWN_ACUTE_CORNERS`
  (currently the middle of the back's `w`).

Result on the current files: the 0.2 mm version passes everything. The 0.4 mm version passes
everything except the gap check, which it reports as warnings rather than failures: about 6 spots
on the front and 40 on the back, mostly inside the back's monospace letters. That is the 0.4 mm
nozzle's limit, and the reason for the 0.2 mm version. These checks are on the digital model;
see the print log for real prints.

## What happens at each layer

The card is 1.6 mm thick. With the 0.2 mm nozzle that is 16 layers of 0.1 mm:

| Layer | Height (top of layer) | Contents |
| --- | --- | --- |
| 1–6 | 0.10–0.60 mm | The front, face-down: black, white and orange inlays; the AMS swaps colors on each layer |
| 7–8 | 0.70–0.80 mm | Black |
| 9–10 | 0.90–1.00 mm | Black, with the open NFC pocket (25.3 mm round, under the QR code, against the card's right edge as seen from the front) |
| — | — | **Pause: drop in the NFC tag** |
| 11–16 | 1.10–1.60 mm | The back, printed over the tag: black, white, orange and gray inlays |

With the 0.4 mm nozzle it is 8 layers of 0.2 mm:

| Layer | Height (top of layer) | Contents |
| --- | --- | --- |
| 1–3 | 0.20–0.60 mm | The front, face-down: black, white and orange inlays |
| 4 | 0.80 mm | Black |
| 5 | 1.00 mm | Black, with the open NFC pocket |
| — | — | **Pause: drop in the NFC tag** |
| 6–8 | 1.20–1.60 mm | The back, printed over the tag: black, white, orange and gray inlays |

### Thick stickers

These tables are for the standard card. With `nfc_sticker = "thick"`, the card gains 0.2 mm of
black in the middle: the pocket is 0.4 mm deep (0.8–1.2 mm above the plate), and the pause moves
to layer 13 (0.2 mm nozzle) or layer 7 (0.4 mm nozzle). `build.sh` prints the pocket and pause for
every version. The model refuses to build if the tag would have fewer than two layers over it, or
less than 0.2 mm of black between it and the front inlays.

## Design notes

- The QR encoder is OpenSCAD functions in `card.scad`, so MakerWorld's customizer (one file, no
  local includes) can make a code for each person's link. It covers only what fits the card:
  byte mode, versions 1–3, levels M and L, single blocks. `scripts/test_qr.py` checks every
  version and mask: ZXing must decode each symbol, and symbols whose text fills them exactly must
  match segno module for module. (With shorter text, segno adds a `0x00` byte after the
  terminator that ISO/IEC 18004 7.4.10 doesn't call for, so those differ while both decode.) The
  mask is the one with the lowest penalty score; the scores match segno's scorer.
- Long text shrinks to fit rather than running into the QR code: the model sums each string's
  advance widths (a table read from Inter ExtraBold; JetBrains Mono is 0.822 per mm of size) and
  scales the size down to the column, never below the nozzle's `min_cap`. Measured against
  OpenSCAD's rendered ink, the estimate is within 2%, and the 1.5 mm gap before the QR field
  covers the difference. Two names shrink together, as do all the back's lines.

- The QR modules are the black body showing through the white field, so the code has no
  separate dark part. Dark modules are grown by 0.02 mm (`qr_overlap`), so diagonal neighbors
  overlap instead of meeting at a zero-width edge. That edge would make both STLs non-manifold.
- `JetBrains Mono` set the domain at first, but its narrow `m` has stems under 0.5 mm at this
  size. Inter's `m` is wider. The mono face stays for the `~/tbutman` mark, which matches the
  site header: amber `~/`, light `tbutman`. It is set as one string and split by color, so the
  spacing is the font's own.
- With a 0.4 mm nozzle, several glyphs need thickening to reach 0.5 mm strokes (the mono `a`
  joint, the `$` bar). The `*_bolden` parameters do that for the 0.4 version; for the 0.2 version
  they are all 0, so the letters print exactly as drawn.
- The tap label was "tap to connect" in white. It printed cleanly on the 0.2 mm sample, but the
  short "tap" in amber, matching the waves, reads better at a glance. The 0.2 mm version keeps that
  sample's lighter Inter Bold at 2.6 mm (Thomas preferred it); the 0.4 mm version uses ExtraBold at
  3 mm, since Bold's strokes are too fine for that nozzle. (Earlier note: at 2.6 mm, ExtraBold's
  `c` and `e` openings were about 0.15 mm and would have printed closed.)
- The tap marker sits right of the QR code, where the NFC tag now is. The tag first sat behind
  the name, under a non-QR area as the original brief asked; it moved so the marker could go
  in that strip and still point at the tag. Phones read NFC from only 1–3 cm away, so a marker
  away from the tag would send people to a dead spot. The trade-off: the tag is under the QR
  code, so check on the first print that the QR face stays flat over it.
- In OpenSCAD 2026.09, `text(size = s)` gives a cap height of about `s` mm for both fonts
  (measured: an `H` at size 10 is 10.1 mm), so the sizes above are cap heights.

## Counting scans

The site promises 0 cookies and 0 trackers, so there are no analytics scripts. Visits are counted
from nginx's own access log instead: since 5 October 2026 the site's server keeps that log (four
weeks) and builds a private GoAccess report from it every 15 minutes, with `/hello` among the
pages and referring sites (see the site repository's `deploy/README.md`). For a quick count on the
server, in the site's Docker Compose directory:

```bash
sudo docker compose logs --no-log-prefix website | grep -c '"GET /hello'
```

This counts requests, not people. The QR code, the NFC tag and Tilde on Thomas's phone all open
the same URL, so they can't be told apart. Link-preview bots and reloads count too. The Docker
log only goes back to when the container was last recreated; the report keeps longer history.

## Print log

| Date | Cards | Result |
| --- | --- | --- |
| 2026-10-05 | 1, 0.4 mm nozzle, no tag, front face-down (design as of a1a15f1) | 75 minutes. Front: smooth and matte, crisp QR code, name and domain; the "tap" label and waves too small to read, and concentric first-layer rings in the black (fix: bottom surface pattern). Back, printed on top: legible but ridged and a little soft; `@`, `m` and `$` slightly blobby, as the 0.4 mm gap check predicted. Led to making front-down the default orientation and to the 0.2 mm version. QR and tap not yet tested on phones. |
| 2026-10-05 | 1, 0.2 mm nozzle, front face-down, white "tap to connect" label | Significantly better than the 0.4 mm sample (Thomas, comparing photos): the back's small mono text is crisp, where the 0.4 mm sample's `@`, `m` and `$` were soft. He preferred this version's lighter label weight and asked for a shorter "tap" label in amber, now the design. Tag and phone tests still to come. |
