#!/usr/bin/env bash
# Export the inlay test strip: one STL per color (body = black, light = white) and a 3MF with both,
# into the folder given (default test/out). Needs Docker, like build.sh.
#   test/build-inlay-test.sh [folder]
set -euo pipefail
cd "$(dirname "$0")/.."
out=${1:-test/out}
mkdir -p "$out"
for part in body light; do
  docker run --rm -v "$PWD":/w -w /w openscad/openscad:dev \
    openscad --backend=manifold -D "part=\"$part\"" --export-format binstl -o "test/.tmp-$part.stl" test/inlay-test.scad 2>&1 | grep -E 'WARNING|ERROR' || true
  mv "test/.tmp-$part.stl" "$out/inlay-test-$part.stl"
done
docker run --rm -v "$PWD":/w -w /w openscad/openscad:dev \
  openscad --backend=manifold -o test/.tmp.3mf test/inlay-test.scad 2>&1 | grep -E 'WARNING|ERROR' || true
mv test/.tmp.3mf "$out/inlay-test.3mf"
ls -la "$out"
