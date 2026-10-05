"""Write makerworld/nfc-business-card.scad, the file uploaded to MakerWorld's customizer.

It is card.scad with two changes: no `use <fonts/...>` lines (MakerWorld has the same fonts
installed, and the local files aren't there), and the example person Jane Doe as the defaults, so
the model page shows a sample card rather than Thomas's.

    .venv/bin/python scripts/make_makerworld.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = {
    "name_line_1": "Jane",
    "name_line_2": "Doe",
    "handle": "janedoe",
    "qr_url": "https://example.com",
    "website_text": "example.com",
    "back_name": "jane doe",
    "back_title": "product designer",
    "back_email": "jane@example.com",
}

source = (ROOT / "card.scad").read_text()
lines = source.splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith("// Local copies of the fonts."))
end = max(i for i, l in enumerate(lines) if l.startswith("use <fonts/"))
out = "\n".join(lines[:start] + lines[end + 2:]) + "\n"
for name, value in EXAMPLE.items():
    out, n = re.subn(rf'^{name} = "[^"]*";', f'{name} = "{value}";', out, count=1, flags=re.M)
    assert n == 1, name
out = "// MakerWorld version, generated from card.scad by scripts/make_makerworld.py.\n" + out
(ROOT / "makerworld").mkdir(exist_ok=True)
(ROOT / "makerworld" / "nfc-business-card.scad").write_text(out)
print("wrote makerworld/nfc-business-card.scad")
