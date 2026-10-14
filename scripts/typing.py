#!/usr/bin/env python3
"""
Build the typing banner used under the header:  assets/typing.svg

Two rules drive the design:

1. Every line carries an explicit base `opacity`, so if SMIL animations are
   unavailable the banner still renders one clean, readable line instead of
   stacking all four on top of each other.
2. The typewriter wipe lives in a CSS @keyframes block and nowhere else, so a
   browser without CSS animation support simply skips it and shows the full
   line.

`textLength` pins the rendered width, so the text fits whatever font the
browser resolves and can never be clipped horizontally.

    python3 typing.py
"""

from __future__ import annotations

import pathlib

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"

W, H = 760, 48

BG = "#0d0d16"
INK = "#ffd23f"
ACCENT = "#ff5c8a"

TEXT_W = 620
LEFT = (W - TEXT_W) // 2

LINES = [
    "Computer Science Enthusiast",
    "Low-Level C++ Programming",
    "Vibe Coding with AI",
    "Building Games from Scratch",
]

STEP = 3.2          # seconds per line
FADE_IN = 0.06      # fraction of STEP spent fading in
FADE_OUT = 0.88     # fraction of STEP where the fade-out starts

FONT = "'JetBrains Mono','Fira Code','SF Mono','Consolas','Courier New',monospace"


def build() -> str:
    s: list[str] = []
    a = s.append

    a(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{", ".join(LINES)}">'
    )

    # ---------------------------------------------------------------- frame --
    a(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}"/>')
    a(
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" '
        f'stroke="{ACCENT}" stroke-opacity="0.5" stroke-width="1.5"/>'
    )
    a(
        f'<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{ACCENT}"/>'
        f'<stop offset="1" stop-color="{INK}"/>'
        "</linearGradient>"
    )
    a(f'<rect x="15" y="{H / 2 - 12}" width="4" height="24" rx="2" fill="url(#bar)"/>')

    base = H / 2 + 7
    caret_x = W / 2 + TEXT_W / 2 + 12

    # ---------------------------------------------------------------- lines --
    for i, line in enumerate(LINES):
        # base opacity is what shows when no animation runs: line 0 only
        base_opacity = 1 if i == 0 else 0
        cls = f' class="ln ln{i}"'

        if i == 0:
            values = f"1;1;0;0"
            times = f"0;{FADE_OUT};{FADE_OUT + 0.05};1"
        else:
            values = f"0;0;1;1;0;0"
            times = f"0;{FADE_IN * 0.4:.3f};{FADE_IN};{FADE_OUT};{FADE_OUT + 0.05};1"

        a(
            f'<text{cls} x="{W / 2}" y="{base}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="21" font-weight="700" fill="{INK}" opacity="{base_opacity}" '
            f'textLength="{TEXT_W}" lengthAdjust="spacingAndGlyphs">{line}'
            f'<animate attributeName="opacity" values="{values}" keyTimes="{times}" '
            f'dur="{STEP}s" begin="{i * STEP}s" repeatCount="indefinite"/>'
            f"</text>"
        )

    # ---------------------------------------------------------------- caret --
    # every line is exactly TEXT_W wide, so the caret sits at the same spot
    # for all of them and needs no animation to stay aligned.
    a(
        f'<rect x="{caret_x}" y="{H / 2 - 13}" width="3" height="26" rx="1.5" '
        f'fill="{ACCENT}" opacity="0.9">'
        f'<animate attributeName="opacity" values="0.9;0.9;0;0;0.9" '
        f'keyTimes="0;0.45;0.5;0.95;1" dur="1.1s" repeatCount="indefinite"/>'
        f"</rect>"
    )

    # -------------------------------------------------- typewriter (CSS only)
    # Declared here and nowhere else: if the browser cannot animate CSS, the
    # rules are ignored and the line simply shows in full.
    a(
        "<style>"
        "@keyframes jane-wipe {"
        f"  0%   {{ clip-path: inset(0 100% 0 0); }}"
        f"  {FADE_IN * 100:.0f}% {{ clip-path: inset(0 0% 0 0); }}"
        f"  100% {{ clip-path: inset(0 0% 0 0); }}"
        "}"
        ".ln { animation: jane-wipe 3.2s steps(28, end) infinite; }"
        "</style>"
    )

    a("</svg>")
    return "\n".join(s)


def main() -> None:
    out = ASSETS / "typing.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}  ({out.stat().st_size} bytes, cycle {STEP * len(LINES):.1f}s)")


if __name__ == "__main__":
    main()