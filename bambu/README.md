# Bambu Studio process presets

Two process presets for the **Bambu Lab A1 mini**, one per nozzle. They build on the A1 mini's
standard processes and change only what the card needs:

| Preset | Builds on | Changes |
| --- | --- | --- |
| `Tilde card 0.4 mm` | 0.20mm Standard @BBL A1M | Sparse infill 100% with the Rectilinear pattern (`zig-zag` in the file), Arachne walls, Monotonic line bottom surface, and paint penetration layers top 2 / bottom 2 |
| `Tilde card 0.2 mm` | 0.10mm Standard @BBL A1M 0.2 nozzle | The same, with paint penetration layers top 4 / bottom 4 |

The paint penetration layers matter for a 3MF from MakerWorld's Customize: its colors are painted
onto one shape, and Bambu Studio paints each face this many layers deep. These values keep the
back's colors to its 0.4 mm inlays, above the black lid over the sticker. Bambu also paints the
pocket's ceiling black upward as a bottom face, so the bottom value is 2 (4): more would fill the
letters over the pocket with black. The front's white is then 0.4 mm with black behind it, which
hides the sticker. With the defaults (top 5 on 0.4 mm, 7 on 0.2 mm) the back's letters go through
the lid and print onto the sticker. The STL parts in `out/` aren't painted, so they're not affected.

Both presets are tested on real prints of a sticker card from a Customize 3MF, paint penetration
layers included (October 8, 2026): the 0.4 mm one fully, the 0.2 mm one through to the last layer,
where the 0.2 mm nozzle clogged, so its back's white came out one layer short. A tap test and
photos of the 0.2 mm card are still to come. Before printing
a sticker card, check the lid in Preview (see [PRINTING.md](../PRINTING.md#set-up-the-print-in-bambu-studio), step 7).

**To use them:** in Bambu Studio, **File → Import → Import Configs**, choose
`tilde_card_bambu_printer_settings.zip` (or one of the `.json` files), then pick **Tilde card 0.4 mm** or
**Tilde card 0.2 mm** under **Process**, with the A1 mini and the matching nozzle selected. The
pause for an NFC sticker is still added by hand (see [PRINTING.md](../PRINTING.md#add-the-pause-for-the-nfc-sticker)).

**Updating from an earlier version?** Delete the old Tilde card preset first, or check that Top
paint penetration layers shows 2 (0.4 mm) or 4 (0.2 mm) after importing. Bambu Studio may keep an
existing preset with the same name, and an older export doesn't set the paint layers.

**After opening the 3MF, choose the process again** (Tilde card 0.4 mm or 0.2 mm, or your adjusted
standard process): the 3MF from Customize is a Bambu project file and brings Bambu's standard
process with it. If the name shows an asterisk, re-select it and discard the changes. Then check
Top paint penetration layers shows 2 (0.4 mm) or 4 (0.2 mm).

On another printer, start from its own standard process and make the four changes by hand
(see [PRINTING.md](../PRINTING.md#set-up-the-print-in-bambu-studio)).
