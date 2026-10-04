#!/usr/bin/env bash
# Regenerate everything from card.scad: QR matrix, one STL per colour, checks, preview.
# Needs Docker (OpenSCAD runs in the openscad/openscad:dev image) and the Python venv:
#   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
set -euo pipefail
cd "$(dirname "$0")"

url=$(sed -n 's/^qr_url = "\(.*\)";.*/\1/p' card.scad)
.venv/bin/python scripts/gen_qr.py "$url"

mkdir -p out
for part in body light accent chrome; do
  docker run --rm -v "$PWD":/w -w /w openscad/openscad:dev \
    openscad --backend=manifold -D "part=\"$part\"" --export-format binstl -o "out/card-$part.stl" card.scad 2>&1 |
    grep -E '^(ECHO|WARNING|ERROR)' | sort -u || true
  echo "exported out/card-$part.stl"
done

.venv/bin/python scripts/verify.py "$url"
.venv/bin/python scripts/render_preview.py
