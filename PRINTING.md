# Printing the card

Written for a Bambu Lab A1 mini with an AMS lite, a 0.4 mm nozzle and PLA. Other printers work
too: keep the 0.2 mm layer height and adapt the rest.

## Files

| File | Colour | AMS slot (suggested) |
| --- | --- | --- |
| `out/card-body.stl` | black: the card, the QR modules | 1 |
| `out/card-light.stl` | white: the QR field, the name and `tbutman` in the header mark | 2 |
| `out/card-accent.stl` | orange: `~/`, the rule, `tbutman.com` | 3 |

## Set up the plate in Bambu Studio

1. Choose the **Bambu Lab A1 mini 0.4 nozzle** printer, the **0.20mm Standard** process and your
   PLA profiles.
2. Drag all three STLs in at once, then answer **Yes** when asked whether to load them as a single
   object with multiple parts. They are already in position relative to each other.
3. In the object list, set each part's filament: body → black, light → white, accent → orange.
4. Print one card first (see the checklist below). For a batch, right-click the card, choose
   **Clone**, then click **Arrange**. Leave room for the prime tower. Two or three cards per plate
   is a comfortable fit on the 180 × 180 mm bed. The card count is up to you.

## Slicer settings

The geometry is built on 0.2 mm layers, so the height settings matter. The others are suggestions.

| Setting | Value | Why |
| --- | --- | --- |
| Layer height | **0.20 mm** | The pocket and the inlays are whole 0.2 mm layers |
| Initial layer height | **0.20 mm** | Same reason; this is Bambu's default for a 0.4 nozzle |
| Wall loops | 2 | |
| Top / bottom shell layers | 5 / 3 | With 8 layers in total, the card is solid all through |
| Sparse infill density | 100 % | Belt and braces: there is no room for real infill anyway |
| Top surface pattern | Monotonic line | An even sheen across the QR field |
| Ironing | Off for the first print | Try it later if the top looks rough |
| Brim | None | |
| Prime tower | On (the default with the AMS) | |
| Build plate | Textured PEI is fine | It gives the back of the card a fine texture |

If the white field looks grey or speckled, raise the black → white flushing volume (the
**Flushing volumes** button next to the filament list).

## What happens at each layer

The card is 1.6 mm thick: 8 layers of 0.2 mm.

| Layer | Height (top of layer) | Contents |
| --- | --- | --- |
| 1–2 | 0.20–0.40 mm | Black floor |
| 3 | 0.60 mm | Black, with the open NFC pocket (25.3 mm round, behind the name) |
| — | — | **Pause: drop in the NFC tag** |
| 4–5 | 0.80–1.00 mm | Black, printed over the tag |
| 6–8 | 1.20–1.60 mm | Black, white and orange inlays; the AMS swaps colours on each layer |

### The NFC pause: before layer 4 (0.80 mm)

1. In **Preview**, drag the layer slider to **layer 4 (0.80 mm)**. Check that layer 3 shows the
   open round pocket and that layer 4 covers it.
2. Right-click the **+** on the slider handle and choose **Add pause**. The printer finishes
   layer 3, parks and waits.
3. When it pauses: peel the backing off a (pre-written, see below) sticker and press it flat,
   adhesive side down, into the pocket of every card on the plate. Run a fingernail over it: nothing
   may stand proud of the pocket rim, or the nozzle will catch it. Keep your fingers off the hot
   nozzle.
4. Resume from the printer's screen.

The pocket is 0.2 mm deep, which assumes a tag no thicker than 0.2 mm. **Measure your tags with
calipers when they arrive.** If they are thicker, set `nfc_tag_t` in `card.scad` and run
`./build.sh`: the pocket deepens to whole layers, and the build output prints the new pause layer
(for a 0.2–0.4 mm tag it moves to layer 5).

## First-print checklist

Print one card, then check:

- [ ] Before the pause, the pocket is clean, round and free of strings.
- [ ] After the print, the area over the tag is flat: no bump under the name.
- [ ] The white field is white, not grey, with no black specks in it.
- [ ] The QR modules are crisp, with square corners and no colour bleeding between them.
- [ ] The text is legible: the `m`s in `tbutman.com` and `~/tbutman`, and the `~/` fully formed.
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
