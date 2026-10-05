#!/usr/bin/env bash
# Regenerate everything from card.scad, once per nozzle and sticker thickness: QR matrix, one STL
# per colour, checks, preview. Each version goes to out/nozzle-<size>/ (stickers up to 0.2 mm) or
# out/nozzle-<size>-thick-sticker/ (up to 0.4 mm). Pass nozzle sizes to build only those:
#   ./build.sh          # 0.2 and 0.4
#   ./build.sh 0.2
# Needs Docker (OpenSCAD runs in the openscad/openscad:dev image) and the Python venv:
#   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
set -euo pipefail
cd "$(dirname "$0")"

nozzles=("$@")
[[ ${#nozzles[@]} -gt 0 ]] || nozzles=(0.2 0.4)

url=$(sed -n 's/^qr_url = "\(.*\)";.*/\1/p' card.scad)
.venv/bin/python scripts/gen_qr.py "$url"

status=0
for nozzle in "${nozzles[@]}"; do
for sticker in thin thick; do
  dir="out/nozzle-$nozzle"
  [[ $sticker == thick ]] && dir+="-thick-sticker"
  mkdir -p "$dir"
  echo "== $nozzle mm nozzle, $sticker sticker -> $dir"
  log=$(mktemp)
  for part in body light accent chrome; do
    docker run --rm -v "$PWD":/w -w /w openscad/openscad:dev \
      openscad --backend=manifold -D "nozzle=$nozzle" -D "nfc_sticker=\"$sticker\"" -D "part=\"$part\"" --export-format binstl \
      -o "$dir/card-$part.stl" card.scad 2>&1 | grep -E '^(ECHO|WARNING|ERROR)' >>"$log" || true
  done
  sort -u "$log" | grep -v PRINTER || true
  limits=$(grep -m1 PRINTER "$log")
  rm "$log"
  min_stroke=$(sed -n 's/.*min_stroke=\([0-9.]*\).*/\1/p' <<<"$limits")
  min_gap=$(sed -n 's/.*min_gap=\([0-9.]*\).*/\1/p' <<<"$limits")
  face_down=$(sed -n 's/.*face_down=\([a-z]*\).*/\1/p' <<<"$limits")
  advisory=()
  grep -q 'strict_gaps=false' <<<"$limits" && advisory=(--gaps-advisory)
  .venv/bin/python scripts/verify.py --dir "$dir" --face-down "$face_down" --min-stroke "$min_stroke" --min-gap "$min_gap" \
    ${advisory[@]+"${advisory[@]}"} "$url" || status=1
  .venv/bin/python scripts/render_preview.py --dir "$dir" --face-down "$face_down"
done
done
exit $status
