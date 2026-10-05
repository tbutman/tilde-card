"""Test the QR encoder in card.scad, which MakerWorld runs to make each customised card.

For a range of links (every version and error level the card uses, accented letters, and text that
exactly fills each size) and every mask, OpenSCAD encodes the symbol and this checks that:

- ZXing decodes it to exactly the input;
- where the text fills the symbol exactly, it matches segno module for module. (With shorter text
  segno adds an extra 0x00 byte after the terminator, which ISO/IEC 18004 7.4.10 doesn't, so the
  symbols differ while both decode.)
- a link over the card's limit is refused.

    .venv/bin/python scripts/test_qr.py
"""

import ast
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import segno
import zxingcpp

ROOT = Path(__file__).resolve().parent.parent
CASES = [
    "https://example.com",
    "https://tbutman.com/hello",
    "a",
    "https://www.linkedin.com/in/janedoe",
    "https://github.com/someone-with-a-long-name",
    "https://café.example/olá",
]
# Text that exactly fills each version and level: [text, version, level].
EXACT = [["x" * 14, 1, "m"], ["x" * 26, 2, "m"], ["x" * 42, 3, "m"], ["x" * 53, 3, "l"]]

texts = CASES + [e[0] for e in EXACT]
with tempfile.TemporaryDirectory() as tmp:
    Path(tmp, "test.scad").write_text("\n".join([
        "use </card/card.scad>",
        f"texts = {json.dumps(texts)};",
        'for (i = [0 : len(texts) - 1]) for (m = [-1 : 7]) let(q = qr_encode(texts[i], m)) echo("QR", i, m, q[2], q[3], q[1]);',
        'echo("TOO_LONG_REFUSED", qr_encode("' + "x" * 54 + '") == undef);',
        "cube(1);",
    ]))
    subprocess.run(["docker", "run", "--rm", "-v", f"{ROOT}:/card", "-v", f"{tmp}:/t", "-w", "/t", "openscad/openscad:dev",
                    "openscad", "-o", "test.echo", "test.scad"], check=True, capture_output=True)
    output = Path(tmp, "test.echo").read_text()

failures = []
decoded = identical = symbols = 0
refused = False
for line in output.splitlines():
    if line.startswith('ECHO: "TOO_LONG_REFUSED"'):
        refused = line.endswith("true")
    if not line.startswith('ECHO: "QR"'):
        continue
    i, mask, designator, chosen, matrix = ast.literal_eval("[" + line[len('ECHO: "QR", '):] + "]")
    text = texts[i]
    symbols += 1
    image = np.kron(np.pad(1 - np.array(matrix, dtype=np.uint8), 4, constant_values=1) * 255,
                    np.ones((10, 10), dtype=np.uint8))
    found = zxingcpp.read_barcodes(image)
    if found and found[0].text == text:
        decoded += 1
    else:
        failures.append(f"{text[:30]!r} mask {mask}: decoded {found[0].text if found else None!r}")
    exact = next((e for e in EXACT if e[0] == text), None)
    if exact and mask >= 0:
        ref = segno.make(text, error=exact[2], version=exact[1], mask=mask, boost_error=False, micro=False)
        if [[1 if v else 0 for v in row] for row in ref.matrix] == matrix:
            identical += 1
        else:
            failures.append(f"{text[:30]!r} mask {mask}: differs from segno")

print(f"{decoded}/{symbols} symbols decode to their text")
print(f"{identical}/{len(EXACT) * 8} exact-fit symbols identical to segno")
print(f"a 54-character link is {'refused' if refused else 'NOT refused'}")
for f in failures:
    print("FAIL", f)
sys.exit(1 if failures or not refused or symbols == 0 else 0)
