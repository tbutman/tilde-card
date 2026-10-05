# Printing the card

Written for a Bambu Lab A1 mini with an AMS lite, a **0.2 mm nozzle** and PLA. Other printers work
too: keep the 0.1 mm layer height and adapt the rest.

The model is tuned for the 0.2 mm nozzle: 0.1 mm layers, strokes of at least 0.3 mm, gaps of at
least 0.22 mm, and a 2.6 mm "tap to connect" label. For a 0.4 mm nozzle, set the `[Printer]`
parameters in `card.scad` back (`layer_h = 0.2`, `min_stroke = 0.5`, `min_cap = 3`) and rebuild;
the checks then say what to enlarge.

## Files

| File | Colour | AMS slot (suggested) |
| --- | --- | --- |
| `out/card-body.stl` | black: the card, the QR modules | 1 |
| `out/card-light.stl` | white: front QR field, name, `tbutman` and the "tap" label; back terminal text | 2 |
| `out/card-accent.stl` | orange: front `~/`, rule, tap waves and `tbutman.com`; back `$` prompts and cursor | 3 |
| `out/card-chrome.stl` | gray: the back's terminal window bar (three dots and a rule) | 4 |

No gray loaded? Assign `card-chrome` to white or orange instead; nothing in the model changes.

The front prints facing up. The back prints against the plate, so in Bambu Studio its text looks
mirrored: that is correct, and it reads normally when you turn the finished card over.

## Set up the plate in Bambu Studio

1. Fit the 0.2 mm hotend. Choose the **Bambu Lab A1 mini 0.2 nozzle** printer, a **0.10 mm**
   process (Bambu's 0.10mm Standard profile for that printer) and your PLA profiles.
2. Drag all four STLs in at once, then answer **Yes** when asked whether to load them as a single
   object with multiple parts. They are already in position relative to each other.
3. In the object list, set each part's filament: body → black, light → white, accent → orange,
   chrome → gray.
4. Print one card first (see the checklist below). For a batch, right-click the card, choose
   **Clone**, then click **Arrange**. Leave room for the prime tower. Two or three cards per plate
   is a comfortable fit on the 180 × 180 mm bed. The card count is up to you.

## Slicer settings

The geometry is built on 0.1 mm layers, so the height settings matter. The others are suggestions.

| Setting | Value | Why |
| --- | --- | --- |
| Layer height | **0.10 mm** | The pocket and the inlays are whole 0.1 mm layers |
| Initial layer height | **0.10 mm** | Same reason |
| Line widths | Profile defaults (about 0.22 mm) | The model's minimum gap is one such line |
| Wall loops | 2 | |
| Top / bottom shell layers | 8 / 8 | With 16 layers in total, the card is solid all through |
| Sparse infill density | 100 % | Belt and braces: there is no room for real infill anyway |
| Top surface pattern | Monotonic line | An even sheen across the QR field |
| Ironing | Off for the first print | Try it later if the top looks rough |
| Brim | None | |
| Elephant foot compensation | **0 mm** | It shrinks first-layer outlines, which can open hairline gaps around the back lettering |
| Prime tower | On (the default with the AMS) | |
| Build plate | Textured PEI is fine | It gives the back a fine, matte texture; wipe it clean of fingerprints so the small first-layer letters stick |

If the white field looks grey or speckled, raise the black → white flushing volume (the
**Flushing volumes** button next to the filament list).

Expect a much longer print than with a 0.4 mm nozzle: half-width lines on half-height layers, and
twice as many colour layers (12 instead of 6), so twice the AMS swaps and purge per plate.

## What happens at each layer

The card is 1.6 mm thick: 16 layers of 0.1 mm.

| Layer | Height (top of layer) | Contents |
| --- | --- | --- |
| 1–6 | 0.10–0.60 mm | The back: black, white, orange and gray inlays; the AMS swaps colours on each layer |
| 7–8 | 0.70–0.80 mm | Black, with the open NFC pocket (25.3 mm round, against the right edge, under the QR code) |
| — | — | **Pause: drop in the NFC tag** |
| 9–10 | 0.90–1.00 mm | Black, printed over the tag |
| 11–16 | 1.10–1.60 mm | The front: black, white and orange inlays |

### The NFC pause: before layer 9 (0.90 mm)

1. In **Preview**, drag the layer slider to **layer 9 (0.90 mm)**. Check that layer 8 shows the
   open round pocket and that layer 9 covers it.
2. Right-click the **+** on the slider handle and choose **Add pause**. The printer finishes
   layer 8, parks and waits.
3. When it pauses: peel the backing off a (pre-written, see below) sticker and press it flat,
   adhesive side down, into the pocket of every card on the plate. Run a fingernail over it: nothing
   may stand proud of the pocket rim, or the nozzle will catch it. Keep your fingers off the hot
   nozzle.
4. Resume from the printer's screen.

The pocket is 0.2 mm deep, which assumes a tag no thicker than 0.2 mm. **Measure your tags with
calipers when they arrive.** If they are thicker, set `nfc_tag_t` in `card.scad` and run
`./build.sh`: the pocket deepens to whole 0.1 mm layers, and the build output prints the new pause
layer (each extra 0.1 mm moves it one layer later, so a 0.3 mm tag pauses before layer 10).

## First-print checklist

Print one card, then check:

- [ ] Before the pause, the pocket is clean, round and free of strings.
- [ ] After the print, the area over the tag is flat: no bump in the QR field's right half.
- [ ] The white field is white, not grey, with no black specks in it.
- [ ] The QR modules are crisp, with square corners and no colour bleeding between them.
- [ ] The text is legible: the `m`s in `tbutman.com` and `~/tbutman`, the `~/` fully formed, and
      the `c`s and `e`s in "tap to connect" still open.
- [ ] The back reads correctly (not mirrored), and its first-layer letters are complete, with no
      lifted or missing pieces and no gaps around them.
- [ ] The tap marker is clear, and tapping there opens the page.
- [ ] The QR face is flat over the tag (lay a ruler across it), and the QR code still scans.
- [ ] The QR code opens `https://tbutman.com/hello` from the camera app on an **iPhone** and on
      an **Android** phone, at arm's length and close up, and in dim light.
- [ ] Tapping the card opens the same URL on the iPhone (top edge of the phone, near the camera)
      and on the Android phone (the reader is usually mid or upper back;
      it varies by model).
- [ ] The card is flat, with no warped corners, and fits a wallet card slot.
- [ ] The thickness measures about 1.6 mm.

Note the results in `README.md` under "Print log".

## Writing the NFC tag

Use **NFC Tools** (free, by wakdev, on iOS and Android). Write each sticker **before** it goes in
the card. A dud tag then costs one sticker, not a whole card. Writing through 1 mm of plastic also
works if a tag needs fixing later.

1. Open NFC Tools → **Write** → **Add a record** → **URL / URI**.
2. Enter `https://tbutman.com/hello` and confirm.
3. Tap **Write**, then hold the phone against the sticker until it confirms.
4. Check it: go to **Read**, hold the phone to the tag and confirm it shows the URL. Also test with
   the phone's own reader: with the phone unlocked, tapping the tag should offer to open the link.

An NTAG215 holds 504 bytes, and this URL record uses about 20.

### Locking (optional and irreversible)

NFC Tools → **Other** → **Lock tag** makes the tag permanently read-only, so nobody can overwrite
it. **There is no undo.** A locked tag can never be rewritten, even if the URL changes. Only lock
after the finished card has opened the page on both an iPhone and an Android phone. Leaving it
unlocked is also fine.

## Which tags to buy

**25 mm round NTAG215 stickers**, usually sold in packs of 10–50. Check the listing says 25 mm and NTAG215. Avoid "anti-metal" tags and hard PVC
coins: they are 0.6–1 mm thick and need a different pocket (`nfc_tag_t`, and probably a thicker
card).
