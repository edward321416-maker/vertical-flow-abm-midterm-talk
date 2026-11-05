#!/usr/bin/env bash
# Fetch the single typeface used by the refined deck: Pretendard 1.3.9 (SIL Open Font License 1.1).
# Source: npm package "pretendard@1.3.9" (registry.npmjs.org). The tarball checksum is pinned below.
# Only the four static TTF weights used by deck.css are extracted into ./fonts (git-ignored).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HERE/fonts"
TGZ_SHA256="0ffc240cee83be02520fb4ac1b2a0a51052b9d13506ade0ba90c591dbbb3bd53"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$DEST"
( cd "$WORK" && npm pack pretendard@1.3.9 --silent >/dev/null )
echo "$TGZ_SHA256  $WORK/pretendard-1.3.9.tgz" | sha256sum -c -
for w in Regular Medium SemiBold Bold; do
  tar -xzf "$WORK/pretendard-1.3.9.tgz" -C "$WORK" "package/dist/public/static/alternative/Pretendard-$w.ttf"
  cp "$WORK/package/dist/public/static/alternative/Pretendard-$w.ttf" "$DEST/"
done
tar -xzf "$WORK/pretendard-1.3.9.tgz" -C "$WORK" package/dist/LICENSE.txt
cp "$WORK/package/dist/LICENSE.txt" "$DEST/Pretendard-OFL-LICENSE.txt"
ls -l "$DEST"
