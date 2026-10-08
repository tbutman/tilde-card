# Bambu Studio process presets

Two process presets for the **Bambu Lab A1 mini**, one per nozzle. They build on the A1 mini's
standard processes and change only what the card needs:

| Preset | Builds on | Changes |
| --- | --- | --- |
| `Tilde card 0.4 mm` | 0.20mm Standard @BBL A1M | Sparse infill 100% with the Rectilinear pattern (`zig-zag` in the file), Arachne walls, Monotonic line bottom surface, and paint penetration layers top 2 / bottom 3 |
| `Tilde card 0.2 mm` | 0.10mm Standard @BBL A1M 0.2 nozzle | The same, with paint penetration layers top 4 / bottom 6 |

The paint penetration layers matter for a 3MF from MakerWorld's Customize: its colors are painted
onto one shape, and Bambu Studio paints each face this many layers deep. These values keep the
back's colors to its 0.4 mm inlays, above the black lid over the sticker, and the front's to
0.6 mm. With the defaults (top 5 on 0.4 mm, 7 on 0.2 mm) the back's letters go through the lid
and print onto the sticker. The STL parts in `out/` aren't painted, so they're not affected.

The 0.4 mm preset's infill, wall and surface settings are tested on a real print; its paint
penetration layers are new (from the print that showed the problem, which used Bambu's standard
process) and still to be confirmed on a print, as is the whole 0.2 mm preset. Before printing
a sticker card, check the lid in Preview (see [PRINTING.md](../PRINTING.md#set-up-the-print-in-bambu-studio), step 7).

**To use them:** in Bambu Studio, **File → Import → Import Configs**, choose
`Tilde card process presets.zip` (or one of the `.json` files), then pick **Tilde card 0.4 mm** or
**Tilde card 0.2 mm** under **Process**, with the A1 mini and the matching nozzle selected. The
pause for an NFC sticker is still added by hand (see [PRINTING.md](../PRINTING.md#add-the-pause-for-the-nfc-sticker)).

**Updating from an earlier version?** Delete the old Tilde card preset first, or check that Top
paint penetration layers shows 2 (0.4 mm) or 4 (0.2 mm) after importing. Bambu Studio may keep an
existing preset with the same name, and an older export doesn't set the paint layers.

On another printer, start from its own standard process and make the four changes by hand
(see [PRINTING.md](../PRINTING.md#set-up-the-print-in-bambu-studio)).
