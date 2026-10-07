#!/usr/bin/env bash
# Regenerate everything from card.scad, once per nozzle and sticker thickness: one STL per colour,
# the checks and the preview. Each version goes to out/nozzle-<size>/ (stickers up to 0.2 mm) or
# out/nozzle-<size>-thick-sticker/ (up to 0.4 mm). Pass nozzle sizes to build only those:
#   ./build.sh          # 0.2 and 0.4
#   ./build.sh 0.2
# out/ holds the sample card, Jane Doe (card.scad's defaults). If card.local.scad exists (git-ignored;
# start from card.local.example.scad), your own card is built too, into out/local/ (also ignored).
# Needs Docker (OpenSCAD runs in the openscad/openscad:dev image) and the Python venv:
#   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
set -euo pipefail
cd "$(dirname "$0")"

nozzles=("$@")
[[ ${#nozzles[@]} -gt 0 ]] || nozzles=(0.2 0.4)

# The QR code is generated inside card.scad; verify.py checks it decodes to this link.
link_in() { sed -n 's/^qr_code_link = "\(.*\)";.*/\1/p' "$1"; }

status=0
# Builds every nozzle and sticker version into $1/nozzle-*/; the rest are -D settings for OpenSCAD.
build_cards() {
local root=$1 url=$2
shift 2
for nozzle in "${nozzles[@]}"; do
for sticker in thin thick; do
  dir="$root/nozzle-$nozzle"
  [[ $sticker == thick ]] && dir+="-thick-sticker"
  mkdir -p "$dir"
  rm -f "$dir"/card-*.stl
  echo "== $nozzle mm nozzle, $sticker sticker -> $dir"
  log=$(mktemp)
  for part in body light accent chrome; do
    docker run --rm -v "$PWD":/w -w /w openscad/openscad:dev \
      openscad --backend=manifold "$@" -D "nozzle=$nozzle" -D "nfc_sticker=\"$sticker\"" -D "part=\"$part\"" --export-format binstl \
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
}

build_cards out "$(link_in card.scad)"

# Your own card: each `setting = value;` line in card.local.scad becomes a -D flag.
if [[ -f card.local.scad ]]; then
  local_flags=()
  while IFS= read -r line; do local_flags+=(-D "$line"); done \
    < <(sed -n 's/^\([a-z_][a-z0-9_]*\) *= *\(.*\);.*/\1=\2/p' card.local.scad)
  local_url=$(link_in card.local.scad)
  build_cards out/local "${local_url:-$(link_in card.scad)}" ${local_flags[@]+"${local_flags[@]}"}
fi

# The MakerWorld file: write it, then build and check sample cards from it the way MakerWorld
# would, with the fonts found by name (OPENSCAD_FONT_PATH stands in for its installed fonts): the
# default, and a QR-only card with no NFC sticker and the plain back.
.venv/bin/python scripts/make_makerworld.py
sample_url=$(link_in makerworld/tilde-card.scad)
for sample in default qr-only-plain; do
  dir="out/makerworld-sample"
  extra=()
  if [[ $sample == qr-only-plain ]]; then dir+="-qr-only-plain"; extra=(-D 'nfc_sticker="none"' -D 'back_style="plain"'); fi
  mkdir -p "$dir"
  rm -f "$dir"/card-*.stl  # a part with nothing in it writes no file, so clear old ones
  echo "== MakerWorld file, $sample, 0.2 mm nozzle -> $dir"
  for part in body light accent chrome; do
    docker run --rm -v "$PWD":/w -w /w -e OPENSCAD_FONT_PATH=/w/fonts openscad/openscad:dev \
      openscad --backend=manifold -D "part=\"$part\"" "${extra[@]+"${extra[@]}"}" --export-format binstl \
      -o "$dir/card-$part.stl" makerworld/tilde-card.scad 2>&1 | grep -E '^(ECHO: "(CARD|No NFC|NFC pocket)|WARNING|ERROR)' || true
  done
  .venv/bin/python scripts/verify.py --dir "$dir" --face-down front --min-stroke 0.3 --min-gap 0.22 "$sample_url" || status=1
  .venv/bin/python scripts/render_preview.py --dir "$dir" --face-down front
done
exit $status
