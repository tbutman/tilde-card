# MakerWorld page (draft)

The text below the line is the model page, ready to paste into MakerWorld. Images are in
[images/](images/), in the order they should appear.

**Before publishing:**

- [ ] Make the model customisable in MakerWorld's Parametric Model Maker (name, title, email,
      link, handle, colours), with the QR code generated in OpenSCAD.
- [ ] Decide what to do about tag thickness: keep the 0.2 mm pocket and recommend wet inlays, or
      add a setting for thicker paper stickers (0.3–0.4 mm).
- [ ] Print and photograph real cards for both nozzles (shot list below), and fill in the 0.4 mm
      print time.
- [ ] Make a 3MF print profile for each nozzle with the pause and settings already in.
- [ ] Choose the licence (MakerWorld offers Creative Commons options, such as CC BY 4.0).
- [ ] Publish Tilde on GitHub first, and this repo too (or drop its link), so the links below work.

**Photo shot list:** the card in a hand; front and back on a desk; a phone tapping the card with
the website opening; the 0.2 mm and 0.4 mm cards side by side, close up on the small text; the
open pocket at the pause, with a tag going in; a stack of cards on the plate.

**Images:**

| File | Caption |
| --- | --- |
| `01-cover.png` | Print your own NFC business card, and share from your phone with the free Tilde app |
| `02-card-3d.png` | Four colours, printed in one go |
| `03-front.png` | The front: your name, your link and a QR code |
| `04-back.png` | The back: a terminal window with your details |
| `05-app-share.png` | Tilde: your card on your phone |
| `06-app-picker.png` | Choose what a tap shares |
| `07-app-met.png` | Remember who you met |

---

## Title

NFC Business Card: tap or scan, with a free companion app

## Summary

A credit-card-sized business card with a QR code on the front and an NFC tag sealed inside. Tap it
with a phone or scan it to open your website. Type in your own details and print it in one go.

## Description

Hand someone this card and they can **tap it with their phone** or **scan the QR code** to open
your website. No app needed on their side: iPhones and Android phones with NFC read it straight
away.

**Make it yours.** Click **Customize** to type in your name, job title, email, website and colours.
The QR code is made for your link automatically.

**The tag goes in while it prints.** The printer pauses halfway, you press in an NFC sticker, and
the rest of the card prints over it. The tag ends up sealed inside, invisible and protected.

### What you need

- A multi-colour printer (AMS, AMS lite or similar). The card changes colour about 30 times.
- PLA in black, white and orange (and grey for a small detail on the back, optional).
- A 0.2 mm or 0.4 mm nozzle.
- 25 mm round NTAG215 NFC stickers, **no thicker than 0.2 mm** (see below).
- A phone with NFC and a free app to put your link on the sticker: Tilde (Android) or NFC Tools
  (iPhone and Android).

### 0.2 mm or 0.4 mm nozzle?

There's a print profile for each.

- **0.2 mm nozzle:** the sharpest card. Every letter prints exactly as designed, and the tap
  marker reads "tap to connect". About 4½ hours for one card.
- **0.4 mm nozzle:** quicker, and it's the nozzle most printers come with. The front looks clean;
  the smallest letters on the back can come out slightly soft. The tap marker reads "tap".

Most of the time goes on colour changes, which happen once per layer for the whole plate. So
**two or three cards take barely longer than one**: fill the plate.

### NFC stickers

Buy **25 mm round NTAG215 stickers**, about $0.25–0.65 each ($5–10 for a small pack).

- **Thin is important:** the pocket is 0.2 mm deep. "Wet inlay" stickers (about 0.12 mm) fit
  best. Many paper stickers are thicker, so measure one if the listing doesn't say.
- **Don't use** NFC coins, anti-metal tags or hard plastic discs. They're too thick.
- A good option: [Seritag 25 mm NTAG215 wet inlay](https://seritag.com/nfc-tags/25mm-ntag215-wet),
  0.12 mm thick.

### How to print

1. Open the print profile for your nozzle. The settings and the pause are already set.
2. Before printing, put your link on a sticker. With Tilde: Settings → Write a card, then hold the
   sticker to your phone. With NFC Tools: Write → Add a record → URL, then hold it to your phone.
3. When the printer pauses, peel the sticker and press it flat into the round pocket, then resume.
4. Done. Tap it with your phone to try it.

The card prints face-down, so you'll see the back on top in the slicer. That's on purpose: the
side on the plate comes out smoothest, so that's the front.

Full instructions, troubleshooting and the source files:
[github.com/tbutman/business-card](https://github.com/tbutman/business-card)

### Share from your phone too: Tilde

[Tilde](https://github.com/tbutman/tilde) is a free, open-source Android app that does the same
thing as the card. People tap their phone against yours, or scan the code on your screen, to get
your website, contact card, WhatsApp or LinkedIn. It works offline, has no ads and no account, and
keeps a list of who you've shared with. It can also write your link onto the card's NFC tag.

### Print settings

- Layer height: 0.10 mm (0.2 mm nozzle) or 0.20 mm (0.4 mm nozzle), first layer the same
- Infill: 100 %
- Wall generator: Arachne
- Top and bottom surface pattern: Monotonic line
- Elephant foot compensation: 0
- Plate: textured PEI recommended (matte front, no glare on the QR code)

## Tags

business card, NFC, QR code, NTAG215, multicolor, AMS, customizable, wallet card, contact card,
networking
