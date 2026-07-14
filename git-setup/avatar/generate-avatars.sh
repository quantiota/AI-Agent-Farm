#!/usr/bin/env bash
# generate-avatars.sh — node avatars: the call-sign on the microserver.network indigo tile.
#
# Needs: rsvg-convert (librsvg).
# Output: <BASE>/microserverNN/{microserverNN.svg, -512.png, -128.png}  for NN = 01..08
# Usage:  bash generate-avatars.sh [BASE]   (BASE defaults to ./avatar)
set -e
BASE="${1:-avatar}"

for n in 01 02 03 04 05 06 07 08; do
  d="$BASE/microserver$n"; mkdir -p "$d"
  cat > "$d/microserver$n.svg" <<SVG
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" role="img" aria-label="microserver$n">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#141a44"/>
      <stop offset="1" stop-color="#0b0e26"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" fill="url(#bg)"/>
  <circle cx="256" cy="256" r="188" fill="none" stroke="#2b336b" stroke-width="4"/>
  <text x="256" y="258" text-anchor="middle" dominant-baseline="central"
        font-family="DejaVu Sans, Verdana, sans-serif" font-weight="700"
        font-size="210" letter-spacing="6" fill="#aeb9ff">$n</text>
  <rect x="196" y="356" width="120" height="10" rx="5" fill="#5c7cfa"/>
</svg>
SVG
  rsvg-convert -w 512 -h 512 "$d/microserver$n.svg" -o "$d/microserver$n-512.png"
  rsvg-convert -w 128 -h 128 "$d/microserver$n.svg" -o "$d/microserver$n-128.png"
done
echo "done -> $BASE"
