"""Write makerworld/tilde-card.scad, the file uploaded to MakerWorld's customizer.

It is card.scad without the `use <fonts/...>` lines (MakerWorld has the same fonts installed, and
the local files aren't there). The defaults are set to the example person Jane Doe, as card.scad's
already are, so the model page always shows the sample card.

MakerWorld shows the script's comments in its Code panel, so the file reads for makers: a short
header instead of card.scad's developer one, and the comments about this repo's tooling (build
and check scripts, local files, print history) rewritten or left out. Every setting keeps its
one-line help, and the code is unchanged.

    .venv/bin/python scripts/make_makerworld.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = {
    "first_name": "Jane",
    "last_name": "Doe",
    "handle": "janedoe",
    "qr_code_link": "https://example.com",
    "website_on_card": "example.com",
    "terminal_command": "whoami",
    "back_line_1": "jane doe",
    "back_line_2": "product designer",
    "back_line_3": "jane@example.com",
}

HEADER = """\
// Tilde card: a credit-card-sized business card you print all at once on a multi-color printer.
// The front has your name, your website and a QR code that opens your link; an optional NFC
// sticker, sealed inside during the print, lets phones tap it too. Made for Tilde, the free
// Android app that turns your phone into the same card.
//
// Click Customize and fill in the sections: the front, the back, the tap mark, colors and printing.
// The print settings and the pause for the NFC sticker are in the model's description.
//
// Full source, instructions and the developer version: https://github.com/tbutman/tilde-card
// (MIT; CC BY 4.0 on MakerWorld).

"""
# card.scad comments that only make sense in the repo, and what makers see instead ("" drops them).
COMMENTS = {
    """// Which face prints against the plate. The plate side comes out flatter and matte (the 0.4 mm
// sample, 5 October 2026), so the front goes down. The output is in print orientation.""":
    """// Which face prints against the plate. The plate side comes out flatter and matte, so the front
// goes down. The output is in print orientation.""",
    """ The
// 0.2 mm sample (5 October 2026) printed "tap to connect" cleanly, but the short label reads better
// at a glance. The 0.2 nozzle keeps that sample's lighter Bold at 2.6 mm; the 0.4 nozzle needs
// ExtraBold at 3 mm. A longer label shrinks to fit the QR code's height, down to min_cap.""":
    """
// The 0.2 nozzle uses Inter Bold at 2.6 mm; the 0.4 nozzle needs ExtraBold at 3 mm. A longer label
// shrinks to fit the QR code's height, down to min_cap.""",
    """// name the steps. scripts/test_qr.py checks the output module for module against segno.""":
    """// name the steps.""",
    """ Scans like segno does, so both pick the
// same mask for the same data.""":
    """ Scans the way reference encoders do, so
// the mask matches theirs for the same data.""",
    """// build.sh reads this line to give verify.py the same limits.
// The 0.4 version's small type has gaps narrower than its nozzle can print (the 0.2 version exists
// for that), so its gap check reports rather than fails.
""":
    """// A summary in the console: thickness, the nozzle's limits, the QR code, text sizes and the pause.
""",
}

source = (ROOT / "card.scad").read_text()
# The developer header and the font lines go; the maker header takes their place.
out = HEADER + source[source.index("/* [Front of the card] */"):]
for old, new in COMMENTS.items():
    assert out.count(old) == 1, old
    out = out.replace(old, new)
for name, value in EXAMPLE.items():
    out, n = re.subn(rf'^{name} = "[^"]*";', f'{name} = "{value}";', out, count=1, flags=re.M)
    assert n == 1, name
(ROOT / "makerworld").mkdir(exist_ok=True)
(ROOT / "makerworld" / "tilde-card.scad").write_text(out)
print("wrote makerworld/tilde-card.scad")
