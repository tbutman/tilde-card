# Tilde card

A business card you print yourself, made to go with [Tilde](https://github.com/tbutman/tilde), the
Android app that turns your phone into an NFC business card. The card has a QR code on the front and
an NFC tag sealed inside, so people can scan it or tap it with their phone to open your website,
even when your phone isn't out.

It works on its own too: phones read it without any app, and any NFC app can write the tag.

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

The files in `out/` are Thomas Butman's own card. To make yours, type in your name, links and
colours on MakerWorld (the page is drafted in [makerworld/](makerworld/listing.md)) or in
OpenSCAD's Customizer: see [Make it yours](PRINTING.md#make-it-yours).

## Print one

[PRINTING.md](PRINTING.md) walks through it step by step: which nozzle to use, which NFC stickers
to buy, the slicer settings, the pause for the tag and how to put your link on the tag.

## Tilde, the app it goes with

[Tilde](https://github.com/tbutman/tilde) is a free, open-source Android app that does what the card
does, from your phone: people tap your phone, or scan the code on its screen, to get your website,
contact card, WhatsApp or LinkedIn. It also writes your link onto the card's tag
(**Settings → Write a card**).

## For developers

The model is written in [OpenSCAD](https://openscad.org): `card.scad` holds every size and every
line of text as a setting. [docs/DESIGN.md](docs/DESIGN.md) covers how it's built and checked,
the design decisions, and the print log.

## Licence

The model and scripts are [MIT](LICENSE) © Thomas Butman. The printable files on MakerWorld are
shared under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/): print, remix and sell
cards freely, with credit. The fonts in `fonts/` are Inter and JetBrains Mono, under the SIL Open
Font License (see the licence files beside them).
