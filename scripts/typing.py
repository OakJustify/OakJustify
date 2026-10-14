#!/usr/bin/env python3
"""
Build the typing banner used under the header:  assets/typing.svg

The public readme-typing-svg service scrolls its text horizontally, so long
lines get clipped on the way in. This version keeps the text pinned in place
and only animates a reveal, and it pins the text with `textLength` so it fits
exactly no matter which font the browser actually resolves.

    python3 typing.py
"""

from __future__ import annotations

import pathlib

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"

W, H = 760, 46

BG = "#0d0d16"
INK = "#ffd23f"
ACCENT = "#ff5c8a"

# every line is the same rendered width, so nothing can ever overflow
TEXT_W = 660
LEFT = (W - TEXT_W) // 2

LINES = [
    "Computer Science Enthusiast",
    "Low-Level C++ Programming",
    "Vibe Coding with AI",
    "Building Games from Scratch",
]

STEP = 3.0      # seconds per line
TYPE = 1.1      # reveal duration
HOLD = 1.6      # pause after the line is fully revealed

FONT = "'JetBrains Mono','Fira Code','SF Mono','Consolas','Courier New',monospace"
TOTAL = STEP * len(LINES)


def build() -> str:
    s: list[str] = []
    a = s.append

    a(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{LINES[0]}; {LINES[1]}; '
        f'{LINES[2]}; {LINES[3]}">'
    )
    a("<defs>")
    a(
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{ACCENT}"/>'
        f'<stop offset="1" stop-color="{INK}"/>'
        "</linearGradient>"
    )
    for i in range(len(LINES)):
        a(
            f'<clipPath id="reveal{i}">'
            f'<rect x="{LEFT - 6}" y="0" width="0" height="{H}">'
            f'<animate attributeName="width" '
            f'values="0;{TEXT_W + 12};{TEXT_W + 12}" '
            f'keyTimes="0;{TYPE / STEP:.3f};1" dur="{STEP}s" '
            f'begin="{i * STEP}s" repeatCount="indefinite"/>'
            "</rect></clipPath>"
        )
    a("</defs>")

    # frame
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}"/>')
    a(
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" '
        f'stroke="{ACCENT}" stroke-opacity="0.55" stroke-width="1.5"/>'
    )
    a(f'<rect x="14" y="{H / 2 - 11}" width="4" height="22" rx="2" fill="url(#accent)"/>')

    base = H / 2 + 7
    for i, line in enumerate(LINES):
        a(
            f'<text x="{W / 2}" y="{base}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="21" font-weight="700" fill="{INK}" '
            f'textLength="{TEXT_W}" lengthAdjust="spacingAndGlyphs" '
            f'clip-path="url(#reveal{i})">{line}</text>'
        )
        # blinking caret that follows the reveal
        a(
            f'<rect x="{LEFT - 4}" y="{H / 2 - 13}" width="3" height="26" fill="{ACCENT}">'
            f'<animate attributeName="x" '
            f'values="{LEFT - 4};{LEFT - 4};{LEFT + TEXT_W + 10};{LEFT + TEXT_W + 10}" '
            f'keyTimes="0;{TYPE / STEP:.3f};0.80;1" dur="{STEP}s" '
            f'begin="{i * STEP}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;1;0;0" '
            f'keyTimes="0;0.80;0.86;1" dur="{STEP}s" '
            f'begin="{i * STEP}s" repeatCount="indefinite"/>'
            f"</rect>"
        )

    a("</svg>")
    return "\n".join(s)


def main() -> None:
    out = ASSETS / "typing.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}  ({out.stat().st_size} bytes, cycle {TOTAL:.0f}s)")


if __name__ == "__main__":
    main()