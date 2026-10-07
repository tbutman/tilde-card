"""Write makerworld/tilde-card.scad, the file uploaded to MakerWorld's customizer.

It is card.scad without the `use <fonts/...>` lines (MakerWorld has the same fonts installed, and
the local files aren't there). The defaults are set to the example person Jane Doe, as card.scad's
already are, so the model page always shows the sample card.

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
(ROOT / "makerworld" / "tilde-card.scad").write_text(out)
print("wrote makerworld/tilde-card.scad")
