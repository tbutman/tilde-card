# NFC business card

A business card you print yourself. It has a QR code on the front and an NFC tag sealed inside, so
people can either scan it or tap it with their phone to open your website.

![The card](out/nozzle-0.2/preview.png)

| Front | Back |
| --- | --- |
| ![Front](out/nozzle-0.2/card-top-surface.png) | ![Back](out/nozzle-0.2/card-back-surface.png) |

- **Credit-card size** (85.6 × 54 mm), 1.6 mm thick (1.8 mm for thicker stickers), so it fits a
  wallet.
- **Four colours of PLA**, printed in one go on a printer with an AMS (or another multi-colour
  system). No painting or gluing.
- **The NFC tag goes in during the print.** The printer pauses halfway, you drop in a sticker, and
  the rest of the card prints over it, sealing it inside.
- **Works with most phones.** iPhones and Android phones with NFC open the link when tapped
  against the marked spot, and any phone camera can scan the QR code. No app needed.

This is Thomas Butman's own card. A version where you type in your own name, links and colours
is coming to MakerWorld; the page is drafted in [makerworld/](makerworld/listing.md).

## Print one

[PRINTING.md](PRINTING.md) walks through it step by step: which nozzle to use, which NFC stickers
to buy, the slicer settings, the pause for the tag and how to put your link on the tag.

## Share from your phone too

[Tilde](https://github.com/tbutman/tilde) is the companion Android app. It turns your phone into
the same thing as the card: people tap your phone, or scan the code on its screen, to get your
website or contact details.

## For developers

The model is written in [OpenSCAD](https://openscad.org): `card.scad` holds every size and every
line of text as a setting. [docs/DESIGN.md](docs/DESIGN.md) covers how it's built and checked,
the design decisions, and the print log.

## Licence

The fonts in `fonts/` are Inter and JetBrains Mono, under the SIL Open Font License (see the
licence files beside them).
