# Printing the card

This guide is written for a Bambu Lab A1 mini with an AMS lite, using Bambu Studio. Other
multi-colour printers work too; the steps are much the same.

## What you need

- **A printer that prints several colours in one go**, such as a Bambu Lab printer with an AMS or
  AMS lite. The card changes colour about 30 times, which is too many to do by hand.
- **PLA in black, white and orange**, plus **grey** for a small detail on the back (optional: use
  white or orange instead).
- **A 0.2 mm or 0.4 mm nozzle.** See [Choose a nozzle](#choose-a-nozzle).
- **A 25 mm round NFC sticker** for each card. See [Buying NFC tags](#buying-nfc-tags).
- **A phone with NFC** and a free app to put your link on the sticker: Tilde (Android) or NFC
  Tools (iPhone and Android).
- **A textured PEI plate** (recommended). It gives the front a matte finish, which also stops the
  QR code reflecting light.

## Choose a nozzle

The card comes in two versions, one for each nozzle size. They look the same from arm's length;
the difference is in the small text and the print time.

| | 0.2 mm nozzle | 0.4 mm nozzle |
| --- | --- | --- |
| **Files** | `out/nozzle-0.2/` | `out/nozzle-0.4/` |
| **Small text** | Sharp. Every letter prints exactly as designed | The front is clean. Small letters on the back (`m`, `@`, `$`) can come out a little soft or partly filled in |
| **Tap label** | "tap to connect" | "tap" (the full phrase is too fine for this nozzle) |
| **Layers** | 16 layers of 0.1 mm | 8 layers of 0.2 mm |
| **Colour changes** | About 30 per plate | About half as many |
| **Print time** | About 4½ hours for one card | Shorter (time to be confirmed) |
| **Filament** | About 9 g in the card, plus about 12 g purged during colour changes | Similar in the card, less purge |
| **Best for** | The best-looking card, if you have a 0.2 mm nozzle | Most printers come with a 0.4 mm nozzle; the quicker option |

**The time is mostly colour changes, not the cards.** Colour changes happen once per layer for the
whole plate, so printing two or three cards at once takes only a little longer than printing one,
and wastes almost no extra filament. If you're printing a stack of cards, fill the plate.

The 0.2 mm time and filament figures are Bambu Studio's estimates for one card on an A1 mini
(5 October 2026). Your printer and settings may differ.

## Buying NFC tags

You need **25 mm round NFC stickers with an NTAG215 chip**, one per card. They're usually sold in
packs of 10 to 100.

- **Thickness matters.** The tag sits in a pocket 0.2 mm deep, so look for stickers no thicker
  than 0.2 mm. "Wet inlay" stickers (about 0.12 mm) are the safest. Many paper stickers are
  thicker; if a listing doesn't say, measure one before printing.
- **Avoid "coins", "anti-metal" tags and hard plastic discs.** They're 0.6 mm or thicker and won't
  fit.
- **NTAG215** holds 504 bytes, enough for a link or a contact card. NTAG216 (888 bytes) also
  works. NTAG213 (144 bytes) is enough for a link only.

Some options, with prices as listed on 5 October 2026:

| Where | What | Thickness | Price |
| --- | --- | --- | --- |
| [Seritag](https://seritag.com/nfc-tags/25mm-ntag215-wet) (UK, prices in £/€/$) | 25 mm NTAG215 wet inlay | 0.12 mm: fits | £0.42 each for 10–99, £0.36 for 100+ |
| [Tagstand](https://www.tagstand.com/products/ntag215-round-sticker-25mm-diameter/) (US) | 25 mm NTAG215 paper sticker | Not listed: measure | $0.62 each, $0.44 for 100+ |
| [GoToTags](https://store.gototags.com/nfc-sticker-ntag215-25-mm-circle/) (US) | 25 mm NTAG215 paper sticker | 0.35 mm: **too thick** for the standard pocket | $0.54 each in 10s |
| Amazon, AliExpress | 25 mm NTAG215 sticker multipacks | Rarely listed: measure | Often $0.25–0.40 each in packs of 50–100 |

**Expect to pay about $0.25 to $0.65 per tag**, or roughly $5–10 for a small pack.

## Set up the print in Bambu Studio

1. Fit the nozzle you chose. In Bambu Studio, pick your printer with that nozzle (for example
   **Bambu Lab A1 mini 0.2 nozzle**) and a process with the matching layer height: **0.10 mm** for
   the 0.2 mm nozzle, **0.20mm Standard** for the 0.4 mm nozzle.
2. Drag in all four files from that version's folder at once (`card-body.stl`, `card-light.stl`,
   `card-accent.stl`, `card-chrome.stl`). When asked whether to load them as **a single object with
   multiple parts**, choose **Yes**.
3. In the list of parts, set each one's filament: **body** → black, **light** → white,
   **accent** → orange, **chrome** → grey.
4. Change these settings (most are under **Quality** and **Strength**):

   | Setting | Set to | Why |
   | --- | --- | --- |
   | Initial layer height | Same as the layer height (0.10 or 0.20 mm) | The card is built from whole layers |
   | Sparse infill density | **100 %** | Makes the card solid all the way through |
   | Wall generator | **Arachne** | Fills thin letter strokes properly |
   | Bottom surface pattern | **Monotonic line** | Gives the front an even finish |
   | Top surface pattern | **Monotonic line** | Gives the back an even finish |
   | Elephant foot compensation | **0 mm** | Stops small gaps opening around the front's letters |
   | Brim | None | |

5. Leave room on the plate for the **prime tower** (the small block the printer purges into when
   it changes colour). Drag it onto an empty spot if it's off the plate.
6. Print one card first. For more, right-click the card, choose **Clone**, then **Arrange**. Two
   or three cards fit comfortably on the A1 mini's plate.

**The card prints face-down, and that's correct.** The side touching the plate comes out
smoothest, so the files are already turned over: you'll see the back facing up, upside down. Don't
flip them.

## Add the pause for the NFC tag

The printer needs to stop halfway so you can put the tag in.

1. Click **Slice plate**, then use the layer slider on the right of the preview.
2. Go to **layer 11** (0.2 mm nozzle) or **layer 6** (0.4 mm nozzle). The layer just below it
   should show an open round pocket; this layer should cover it.
3. Right-click the **+** on the slider and choose **Add pause**.

When the printer pauses:

1. Peel the backing off a sticker (with your link already on it; see below) and press it flat into
   the round pocket, sticky side down. Do this for every card on the plate.
2. Run a fingernail over it. Nothing may stick up above the pocket's edge, or the nozzle will
   catch it.
3. Keep your fingers away from the hot nozzle, then press **Resume** on the printer.

## Put your link on the tag

Do this **before** the sticker goes in the card, so a faulty sticker only costs you the sticker.
(You can also rewrite a tag through the finished card later.)

**On Android, with [Tilde](https://github.com/tbutman/tilde)** (free, the companion app):

1. Fill in your card in Tilde, then go to **Settings** → **Write a card**.
2. Choose what the card should open: your website, contact card, LinkedIn and so on.
3. Hold the sticker to the back of your phone until it buzzes. Hold the next one to write that too.

**On iPhone or Android, with NFC Tools** (free, by wakdev):

1. Open NFC Tools and go to **Write** → **Add a record** → **URL / URI**, and type your website
   address.
2. Tap **Write** and hold your phone against the sticker until it confirms.
3. To check: go to **Read** and hold the phone to the sticker. It should show your link.

**Locking is optional and permanent.** NFC Tools can lock a tag (Other → Lock tag) so nobody can
change it, but then you can't change it either, ever. If you lock it, only do it once the finished
card works.

## Check your first card

- The white square behind the QR code is white, not grey or speckled.
- The QR code's squares are crisp, and it scans with your phone's camera.
- Tapping the card on the "tap" marker opens your link. iPhones read NFC near the top edge, by the
  camera; Android phones usually in the middle or upper part of the back.
- The text is readable, including the small letters.
- The card is flat, with no bump over the tag and no curled corners.

## If something goes wrong

- **The white looks grey or has black specks:** increase the flushing volume from black to white
  (the **Flushing volumes** button next to the filament list).
- **Small letters on the front are missing or didn't stick:** wash the plate with dish soap and
  water (fingerprints stop small details sticking) and lower the initial layer speed, for example
  to 30 mm/s.
- **There's a bump over the tag:** the tag is too thick for the pocket. Use thinner stickers.
- **The phone doesn't react to a tap:** check NFC is on (Android), move the phone slowly over the
  marker, and check the tag works by tapping it before printing.

Details on how the model is built are in [docs/DESIGN.md](docs/DESIGN.md).
