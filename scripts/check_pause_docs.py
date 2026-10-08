"""Check that the pause layers people read match the ones the model computes.

build.sh passes the computed ones (from card.scad's "pause before layer" echo) as
nozzle:sticker:layer, for example 0.4:thin:6. The documented ones are in card.scad's help line
for nfc_sticker (which MakerWorld's Customizer shows), and in the pause tables and plain lines of
makerworld/listing.md and PRINTING.md.

    .venv/bin/python scripts/check_pause_docs.py 0.2:thin:11 0.2:thick:13 0.4:thin:6 0.4:thick:7
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
computed = {(n, s): int(layer) for n, s, layer in (arg.split(":") for arg in sys.argv[1:])}
found = {}  # where -> {(nozzle, sticker): layer}

help_line = next(l for l in (ROOT / "card.scad").read_text().splitlines() if l.startswith("// An NFC sticker"))
m = re.search(r"layer (\d+) \(thin\) or (\d+) \(thick\) on a 0\.4 mm nozzle, (\d+) or (\d+) on 0\.2 mm", help_line)
found["card.scad nfc_sticker help"] = (
    {("0.4", "thin"): int(m[1]), ("0.4", "thick"): int(m[2]), ("0.2", "thin"): int(m[3]), ("0.2", "thick"): int(m[4])} if m else {}
)

for name in ["makerworld/listing.md", "PRINTING.md"]:
    text = (ROOT / name).read_text()
    for sticker in ["thin", "thick"]:
        row = re.search(rf"\| {sticker.capitalize()} stickers \([^|]*\) \| \**Layer (\d+)\** \| \**Layer (\d+)\** \|", text)
        found.setdefault(f"{name} table", {}).update(
            {("0.2", sticker): int(row[1]), ("0.4", sticker): int(row[2])} if row else {})
    plain = re.search(r"Thin stickers: layer (\d+) \(0\.2 mm nozzle\) or layer (\d+) \(0\.4 mm\)\. Thick stickers: layer (\d+)"
                      r" \(0\.2 mm\)\s+or layer (\d+) \(0\.4 mm\)", text)
    if plain or name.startswith("makerworld"):  # the listing must have them, for editors without tables
        found[f"{name} plain lines"] = {("0.2", "thin"): int(plain[1]), ("0.4", "thin"): int(plain[2]),
                                        ("0.2", "thick"): int(plain[3]), ("0.4", "thick"): int(plain[4])} if plain else {}

failed = False
for where, layers in found.items():
    wrong = [f"{n} mm {s}: says {layers.get((n, s))}, model {layer}" for (n, s), layer in computed.items()
             if layers.get((n, s)) != layer]
    print(f"{'FAIL' if wrong else 'PASS'}  pause layers in {where}" + (": " + "; ".join(wrong) if wrong else ""))
    failed |= bool(wrong)
sys.exit(1 if failed else 0)
