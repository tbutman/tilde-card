# Printing the Tilde card

This guide is written for a Bambu Lab A1 mini with an AMS lite, using Bambu Studio. Other
multi-color printers work too; the steps are much the same.

The model is free and open source (MIT; CC BY 4.0 on MakerWorld): no account, sign-up or payment,
and the card links straight to your own website. The NFC sticker is optional. Without one you get a
QR card, and you can skip everything about stickers and the pause.

## What you need

- **A printer that prints several colors in one go**, such as a Bambu Lab printer with an AMS or
  AMS lite. The card changes color about 30 times (roughly half that with no back design), which
  is too many to do by hand.
- **PLA in black, white and orange**, plus **gray** for the window bar on the terminal-style back
  (optional: use white or orange instead).
- **A 0.2 mm or 0.4 mm nozzle.** See [Choose a nozzle](#choose-a-nozzle).
- **Optional, for a card people can tap:** a 25 mm round NFC sticker for each card (see [Buying NFC
  stickers](#buying-nfc-stickers)), and a phone with NFC plus a free app to put your link on the
  sticker: Tilde (Android) or NFC Tools (iPhone and Android).
- **A textured PEI plate** (recommended). It gives the front a matte finish, which also stops the
  QR code reflecting light.

## Make it yours

The files in `out/` are a sample card for Jane Doe, an example person. To print yours, put in your
details first:

- **On MakerWorld (coming soon; the easiest):** open the model page, click **Customize**, and fill
  in your name, link, website, the back of the card and the colors. Under **Printing**, choose your
  nozzle and whether to add an NFC sticker. The preview updates as you type; then open the result in
  Bambu Studio.
- **In OpenSCAD (free, [openscad.org](https://openscad.org)):** open `card.scad`, show the
  Customizer (**Window → Customizer**), change the settings in the first sections and export a
  3MF. Use a recent development snapshot of OpenSCAD: it keeps the four colors in the 3MF.

The choices that change the print:

| Setting | Options |
| --- | --- |
| **NFC sticker** | **None:** a QR card, with no pocket, no "tap" marker and no pause. **Thin** or **thick stickers:** a card people can tap too; see [Buying NFC stickers](#buying-nfc-stickers). |
| **Back of the card** | Three lines of your choice, such as your name, title and email. **Terminal window:** a command such as `$ whoami`, then your lines. **Plain:** just your lines. **None:** plain black, the quickest to print, with roughly half the color changes. Choose None to add your own text or logo in Bambu Studio: the back is the top face as it prints, so the text and color-painting tools work there, and the sticker's pause layer doesn't change. |
| **Nozzle** | **0.2 mm** or **0.4 mm**; see [Choose a nozzle](#choose-a-nozzle). |
| **Tap label** and **back tap mark** | With NFC: the word by the tap waves ("tap", or your own, such as "tap to connect"; empty for just the waves), and whether to repeat the waves and label on the back, over the sticker. |

**What fits:** a link of up to 53 characters (shorter is better: the QR code gets bigger squares).
Long names, handles and websites shrink to fit; if something is too long even at the smallest
printable size, the preview stops with a message saying what to change, such as splitting a long
name between **first name** and **last name**. The 0.2 mm nozzle prints smaller text, so more fits.

## Choose a nozzle

The card comes in two versions, one for each nozzle size. They look the same from arm's length;
the difference is in the small text and the print time.

| | 0.2 mm nozzle | 0.4 mm nozzle |
| --- | --- | --- |
| **Files** | `out/nozzle-0.2/` | `out/nozzle-0.4/` |
| **Files for thick stickers** | `out/nozzle-0.2-thick-sticker/` | `out/nozzle-0.4-thick-sticker/` |
| **Small text** | Sharp. Every letter prints exactly as designed | The front is clean. Small letters on the back (`m`, `@`, `$`) can come out a little soft or partly filled in |
| **Tap label** ("tap" by default) | Inter Bold, 2.6 mm | Inter ExtraBold, 3 mm (the lighter weight is too fine for this nozzle) |
| **Layers** | 16 layers of 0.1 mm | 8 layers of 0.2 mm |
| **Color changes** | About 30 per plate | About half as many |
| **Print time** | About 4½ hours for one card | About 75 minutes for one card |
| **Filament** | About 9 g in the card, plus about 12 g purged during color changes | Similar in the card, less purge |
| **Best for** | The best-looking card, if you have a 0.2 mm nozzle and the time | Most printers come with a 0.4 mm nozzle, and it's over three times faster |

**The time is mostly color changes, not the cards.** Color changes happen once per layer for the
whole plate, so printing two or three cards at once takes only a little longer than printing one,
and wastes almost no extra filament. If you're printing a stack of cards, fill the plate.

The 0.2 mm figures are Bambu Studio's estimate for one card on an A1 mini (5 October 2026); the
0.4 mm time is a real print of one card on the same printer (an early sample, without the pause
for a sticker). Your printer and settings may differ,
and the thick-sticker versions take a little longer (two extra layers on the 0.2 mm nozzle, one on
the 0.4 mm).

## Buying NFC stickers

*Only for a card with NFC. Printing a QR card? Skip to [Set up the print](#set-up-the-print-in-bambu-studio).*

You need **25 mm round NFC stickers with an NTAG215 chip**, one per card. They're usually sold in
packs of 10 to 100, for about **$0.25 to $0.65 per sticker** ($5–10 for a small pack).

**Check the thickness, because it decides which files you print:**

| Sticker thickness | Print | The card |
| --- | --- | --- |
| **0.10–0.20 mm** (wet inlays, thin paper stickers) | The standard files, `out/nozzle-0.2/` or `out/nozzle-0.4/` | 1.6 mm thick |
| **0.20–0.40 mm** (most thicker paper stickers) | The thick-sticker files, `out/nozzle-0.2-thick-sticker/` or `out/nozzle-0.4-thick-sticker/` | 1.8 mm thick |
| Over 0.40 mm ("coins", "anti-metal" tags, hard plastic discs) | Not supported | |

If the listing doesn't say, measure one sticker with its backing peeled off, using calipers. If
you can't measure, print the thick-sticker version: thin stickers work in it too.

**About the chip:** NTAG215 holds 504 bytes, enough for a link or a contact card. NTAG216 (888
bytes) also works. NTAG213 (144 bytes) is enough for a link only.

Some options, with prices as listed on 5 October 2026:

| Where | What | Thickness | Files | Price |
| --- | --- | --- | --- | --- |
| [Seritag](https://seritag.com/nfc-tags/25mm-ntag215-wet) (UK, prices in £/€/$) | 25 mm NTAG215 wet inlay | 0.12 mm | Standard | £0.42 each for 10–99, £0.36 for 100+ |
| [GoToTags](https://store.gototags.com/nfc-sticker-ntag215-25-mm-circle/) (US) | 25 mm NTAG215 paper sticker | 0.35 mm | Thick sticker | $0.54 each in 10s |
| [Tagstand](https://www.tagstand.com/products/ntag215-round-sticker-25mm-diameter/) (US) | 25 mm NTAG215 paper sticker | Not listed: measure | | $0.62 each, $0.44 for 100+ |
| [Amazon](https://www.amazon.com/clp/B091FCQW7N) (K LAKEY, 100 pack) | 25 mm NTAG215 stickers | Not listed: measure | | Varies |
| [eBay](https://www.ebay.com/itm/307182392836) (100 pack) | 25 mm NTAG215 stickers | Not listed: measure | | About $0.37 each |

Listings and prices change; check the thickness and the "25 mm" and "NTAG215" in the listing
before you buy.

## Set up the print in Bambu Studio

New to it? Print a QR card first (**NFC sticker: none**): no pause, nothing to buy.

1. Fit the nozzle you chose. In Bambu Studio, pick your printer with that nozzle (for example
   **Bambu Lab A1 mini 0.2 nozzle**) and its standard process: **0.10mm Standard @BBL A1M 0.2
   nozzle** for the 0.2 mm nozzle, **0.20mm Standard @BBL A1M** for the 0.4 mm nozzle. Other
   printers have their own Standard processes with the same layer heights.
2. Open your card:
   - **Your own card (a 3MF from MakerWorld or OpenSCAD):** open it, then check the four colors
     are assigned to the right filaments (black, white, orange, gray) in the **Filament** list.
   - **The sample card (the STLs in `out/`):** drag in all four files from one version's folder at
     once (`card-body.stl`, `card-light.stl`, `card-accent.stl`, `card-chrome.stl`). When asked
     whether to load them as **a single object with multiple parts**, choose **Yes**.
3. If you loaded the STLs, set each part's filament: **body** → black, **light** → white,
   **accent** → orange, **chrome** → gray.
4. Change these three settings (the same for both nozzles):

   | Setting | Where | Change to | Why |
   | --- | --- | --- | --- |
   | Sparse infill density | Strength | **100 %** (from 15 %) | Makes the card solid all the way through |
   | Wall generator | Quality | **Arachne** (from Classic) | Fills thin letter strokes properly |
   | Bottom surface pattern | Strength | **Monotonic line** (from Monotonic) | Gives the front an even finish |

   Already right in Bambu's standard profiles; check them if you've changed your defaults or use
   another printer:

   | Setting | Should be | Why |
   | --- | --- | --- |
   | Initial layer height | Same as the layer height (0.10 or 0.20 mm) | The card is built from whole layers |
   | Elephant foot compensation | 0 mm | Stops small gaps opening around the front's letters |
   | Top surface pattern | Monotonic line | Gives the back an even finish |
   | Brim | None | |

5. Leave room on the plate for the **prime tower** (the small block the printer purges into when
   it changes color). Drag it onto an empty spot if it's off the plate.
6. Fill the plate: select the card, press **+** to add copies, then **Arrange** (**A**). Three
   cards take barely longer than one, and fit comfortably on the A1 mini's plate.

**The card prints face-down, and that's correct.** The side touching the plate comes out
smoothest, so the files are already turned over: you'll see the back facing up, upside down. Don't
flip them.

## Add the pause for the NFC sticker

*Only for a card with NFC. A QR card has no pocket, so it prints straight through.*

The printer needs to stop halfway so you can put the sticker in.

1. Click **Slice plate**, then use the layer slider on the right of the preview.
2. Go to the layer for your version. The layer just below it should show an open round pocket;
   this layer should cover it.

   | | 0.2 mm nozzle | 0.4 mm nozzle |
   | --- | --- | --- |
   | Standard | **Layer 11** | **Layer 6** |
   | Thick sticker | **Layer 13** | **Layer 7** |

3. Right-click the **+** on the slider and choose **Add pause**.

When the printer pauses:

1. Peel the backing off a sticker (with your link already on it; see below) and press it flat into
   the round pocket, sticky side down. Do this for every card on the plate.
2. Run a fingernail over it. Nothing may stick up above the pocket's edge, or the nozzle will
   catch it.
3. Keep your fingers away from the hot nozzle, then press **Resume** on the printer.

## Put your link on the sticker

*Only for a card with NFC.*

Do this **before** the sticker goes in the card, so a faulty sticker only costs you the sticker.
(You can also rewrite a sticker through the finished card later.)

**On Android, with [Tilde](https://tbutman.com/tilde)** (free, the companion app):

1. Fill in your card in Tilde, then go to **Settings** → **Write a sticker**.
2. Choose what the card should open: your website, contact card, LinkedIn and so on.
3. Hold the sticker to the back of your phone until it buzzes. Hold the next one to write that too.

**On iPhone or Android, with NFC Tools** (free, by wakdev):

1. Open NFC Tools and go to **Write** → **Add a record** → **URL / URI**, and type your website
   address.
2. Tap **Write** and hold your phone against the sticker until it confirms.
3. To check: go to **Read** and hold the phone to the sticker. It should show your link.

**Locking is optional and permanent.** Tilde (tick **Lock it after writing**) and NFC Tools
(Other → Lock tag) can lock a sticker so nobody can change it, but then you can't either, ever.
Only lock it once the finished card works; you can lock it through the card.

## Check your first card

- The white square behind the QR code is white, not gray or speckled.
- The QR code's squares are crisp, and it scans with your phone's camera.
- With NFC: tapping the card on the "tap" marker opens your link. iPhones read NFC near the top edge, by the
  camera; Android phones usually in the middle or upper part of the back.
- The text is readable, including the small letters.
- The card is flat, with no curled corners (and, with NFC, no bump over the sticker).

## If something goes wrong

- **The white looks gray or has black specks:** increase the flushing volume from black to white
  (the **Flushing volumes** button next to the filament list).
- **Small letters on the front are missing or didn't stick:** wash the plate with dish soap and
  water (fingerprints stop small details sticking) and lower the initial layer speed, for example
  to 30 mm/s.
- **There's a bump over the sticker:** the sticker is too thick for the pocket. Print the
  thick-sticker version, or use thinner stickers.
- **The phone doesn't react to a tap:** check NFC is on (Android), move the phone slowly over the
  marker, and check the sticker works by tapping it before printing.

Details on how the model is built are in [docs/DESIGN.md](docs/DESIGN.md).
