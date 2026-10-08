# Bambu Studio process presets

Two process presets for the **Bambu Lab A1 mini**, one per nozzle. They build on the A1 mini's
standard processes and change only what the card needs:

| Preset | Builds on | Changes |
| --- | --- | --- |
| `Tilde card 0.4 mm` | 0.20mm Standard @BBL A1M | Sparse infill 100% with the Rectilinear pattern (`zig-zag` in the file), Arachne walls, Monotonic line bottom surface |
| `Tilde card 0.2 mm` | 0.10mm Standard @BBL A1M 0.2 nozzle | The same |

The 0.4 mm preset is tested on a real print; the 0.2 mm one has the same changes and is still to
be confirmed on a print.

**To use them:** in Bambu Studio, **File → Import → Import Configs**, choose
`Tilde card process presets.zip` (or one of the `.json` files), then pick **Tilde card 0.4 mm** or
**Tilde card 0.2 mm** under **Process**, with the A1 mini and the matching nozzle selected. The
pause for an NFC sticker is still added by hand (see [PRINTING.md](../PRINTING.md#add-the-pause-for-the-nfc-sticker)).

On another printer, start from its own standard process and make the three changes by hand
(see [PRINTING.md](../PRINTING.md#set-up-the-print-in-bambu-studio)).
