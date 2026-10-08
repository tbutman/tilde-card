# Sticker test tile

`sticker-test.scad` is the card-sized tile used on 8 October 2026 to choose how a sticker card's
layers are stacked (see "Solid lid" in [docs/DESIGN.md](../docs/DESIGN.md)). It is 1.8 mm thick,
printed front down, with two thin-sticker pockets: **B** (0.2 mm of black in front of the sticker,
a 0.4 mm lid behind it) and **2** (0.4 mm and 0.2 mm), a white QR-like patch over each on the
front, 0.4 mm white letters over each on the back, and white squares 0.2, 0.4 and 0.6 mm deep.

    test/build-sticker-test.sh [folder]   # inlay-test-body.stl, inlay-test-light.stl, inlay-test.3mf

Load both STLs as one object with multiple parts (body black, light white), with the card's
settings (100% Rectilinear infill, Arachne, bottom Monotonic line). Pause before the layer that
starts at 1.0 mm (sticker in B) and the one that starts at 1.2 mm (sticker in 2):

| Nozzle and process | Pocket B | Pocket 2 |
| --- | --- | --- |
| 0.4 mm, 0.20mm Standard (9 layers) | layer 6 | layer 7 |
| 0.2 mm, 0.10mm Standard (18 layers) | layer 11 | layer 13 |

On the 0.2 mm nozzle, pocket 2's 0.2 mm lid is two layers, so its single-layer lid is only tested
on the 0.4 mm nozzle. Bambu Studio estimates about 2h45m on the 0.2 mm nozzle.
