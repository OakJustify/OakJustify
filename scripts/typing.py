#!/usr/bin/env python3
"""
Build the focus banner under the header:  assets/typing.svg

Design notes
------------
* JetBrains Mono Bold is embedded as a base64 TTF subset. An SVG loaded
  through <img> is not allowed to fetch external resources, so an @font-face
  pointing at a CDN would silently fall back to a system font. Embedding is
  the only way to guarantee the typeface. (Same pattern readme-typing-svg uses.)
* The rows cycle with a CSS animation and staggered negative delays. Nothing
  depends on SMIL. If CSS animation is unavailable the rows simply stay at
  their base opacity and all four are legible at once, which is a perfectly
  good static banner.
* No <clipPath>, no <animate>, and no textLength: each row is left-aligned, so
  there is nothing that can overlap or overflow.

    python3 typing.py
"""

from __future__ import annotations

import base64
import pathlib

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
FONT = ASSETS / "fonts" / "JetBrainsMono-Bold-subset.ttf"

W = 760
ROW_H = 34
TOP = 52
LABEL = "FOCUS"
LINES = [
    "Computer Science Enthusiast",
    "Low-Level C++ Programming",
    "Vibe Coding with AI",
    "Building Games from Scratch",
]

H = TOP + ROW_H * len(LINES) + 20

BG = "#0d0d16"
INK = "#ffd23f"
ACCENT = "#ff5c8a"
DIM = "#7a6a35"

STEP = 3.2
CYCLE = STEP * len(LINES)


def build() -> str:
    font_b64 = base64.b64encode(FONT.read_bytes()).decode()

    s: list[str] = []
    a = s.append

    a(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{LABEL}: {", ".join(LINES)}">'
    )

    # ------------------------------------------------------------------ css --
    # Everything animated lives here. Base styles below are the no-animation
    # fallback and are already correct on their own.
    a(
        "<defs>"
        f'<style>'
        "@font-face{"
        f"font-family:'JBMono';"
        f"font-weight:700;"
        f"font-style:normal;"
        f"src:url(data:font/ttf;base64,{font_b64}) format('truetype');"
        "}"
        f".t{{font-family:'JBMono',ui-monospace,'DejaVu Sans Mono',monospace;"
        f"font-weight:700;font-size:21px;fill:{INK};}}"
        f".lbl{{font-size:11px;letter-spacing:4px;fill:{DIM};}}"
        f".row{{animation:jbm-row {CYCLE}s linear infinite;}}"
        f".dot{{animation:jbm-dot {CYCLE}s linear infinite;}}"
        "@keyframes jbm-row{"
        f"0%{{opacity:1;}}"
        f"{STEP / CYCLE * 100 - 3:.1f}%{{opacity:1;}}"
        f"{STEP / CYCLE * 100:.1f}%{{opacity:.34;}}"
        f"100%{{opacity:.34;}}"
        "}"
        "@keyframes jbm-dot{"
        f"0%{{fill:{INK};}}"
        f"{STEP / CYCLE * 100 - 3:.1f}%{{fill:{INK};}}"
        f"{STEP / CYCLE * 100:.1f}%{{fill:{DIM};}}"
        f"100%{{fill:{DIM};}}"
        "}"
        "@media (prefers-reduced-motion: reduce){"
        ".row,.dot{animation:none;}"
        "}"
        "</style>"
        "</defs>"
    )

    # ---------------------------------------------------------------- frame --
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}"/>')
    a(
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" '
        f'stroke="{ACCENT}" stroke-opacity="0.45" stroke-width="1.5"/>'
    )
    a(
        f'<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{ACCENT}"/>'
        f'<stop offset="1" stop-color="{INK}"/>'
        "</linearGradient>"
    )
    a(f'<rect x="16" y="24" width="4" height="18" rx="2" fill="url(#bar)"/>')
    a(f'<text class="t lbl" x="32" y="38">{LABEL}</text>')
    a(
        f'<text class="t lbl" x="{W - 18}" y="38" text-anchor="end">NEW ERIDU</text>'
    )

    # ----------------------------------------------------------------- rows --
    for i, line in enumerate(LINES):
        y = TOP + i * ROW_H + 24
        delay = -(i * STEP)
        a(
            f'<g class="row" style="animation-delay:{delay}s">'
            f'<circle class="dot" cx="26" cy="{y - 7}" r="4" fill="{DIM}"/>'
            f'<text class="t" x="44" y="{y}">{line}</text>'
            "</g>"
        )

    # ---------------------------------------------------------------- caret --
    # Blinking block cursor parked at the end of the last row.
    caret_x = 44 + len(LINES[-1]) * 21 * 0.6 + 10
    a(
        f'<rect x="{caret_x:.0f}" y="{TOP + (len(LINES) - 1) * ROW_H + 5}" '
        f'width="9" height="21" rx="2" fill="{INK}" opacity="0.85">'
        f'<animate attributeName="opacity" values="0.85;0.85;0;0;0.85" '
        f'keyTimes="0;0.45;0.5;0.95;1" dur="1.1s" repeatCount="indefinite"/>'
        f"</rect>"
    )

    a("</svg>")
    return "\n".join(s)


def main() -> None:
    out = ASSETS / "typing.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}  ({out.stat().st_size // 1024} KB, cycle {CYCLE:.1f}s)")


if __name__ == "__main__":
    main()