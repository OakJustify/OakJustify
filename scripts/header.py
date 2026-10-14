#!/usr/bin/env python3
"""
Build the README hero poster:  assets/header.svg

The Jane Doe artwork is embedded straight into the SVG as a base64 data URI, so
GitHub renders one single self-contained image with no external hotlinks and no
Camo breakage.  Re-run after swapping the artwork:

    python3 header.py
"""

from __future__ import annotations

import base64
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"

W, H = 1200, 460

BG = "#08080d"
INK = "#e9e9f5"
GOLD = "#ffd23f"
RED = "#e4324b"
PINK = "#ff5c8a"
MUTED = "#8a8aa6"

DISPLAY = "Impact, 'Arial Black', 'Helvetica Neue', Helvetica, sans-serif"
MONO = "'Fira Code', 'JetBrains Mono', 'Courier New', monospace"


def data_uri(path: pathlib.Path) -> str:
    mime = "image/webp" if path.suffix == ".webp" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def build() -> str:
    art = data_uri(ASSETS / "jane-banner.webp")
    icon = data_uri(ASSETS / "jane-icon.webp")

    s: list[str] = []
    a = s.append

    a(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="OakJustify - Junior Developer, Zenless Zone Zero themed profile">'
    )
    a(
        "<defs>"
        # fade the artwork out towards the left so the text stays legible
        f'<linearGradient id="scrim" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{BG}" stop-opacity="0.97"/>'
        f'<stop offset="0.42" stop-color="{BG}" stop-opacity="0.86"/>'
        f'<stop offset="0.72" stop-color="{BG}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{BG}" stop-opacity="0"/>'
        "</linearGradient>"
        f'<linearGradient id="bottom" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{BG}" stop-opacity="0.70"/>'
        "</linearGradient>"
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{RED}"/>'
        f'<stop offset="1" stop-color="{GOLD}"/>'
        "</linearGradient>"
        f'<pattern id="hz" width="26" height="26" patternUnits="userSpaceOnUse" '
        f'patternTransform="rotate(45)">'
        f'<rect width="13" height="26" fill="{GOLD}"/>'
        "</pattern>"
        f'<pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">'
        f'<path d="M26 0H0V26" fill="none" stroke="{MUTED}" stroke-opacity="0.13" '
        f'stroke-width="1"/>'
        "</pattern>"
        "</defs>"
    )

    # --------------------------------------------------------------- backdrop
    a(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
    a(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    a(
        f'<image x="0" y="0" width="{W}" height="{H}" '
        f'preserveAspectRatio="xMidYMid slice" xlink:href="{art}" href="{art}"/>'
    )
    a(f'<rect width="{W}" height="{H}" fill="url(#scrim)"/>')
    a(f'<rect width="{W}" height="{H}" fill="url(#bottom)"/>')

    # ------------------------------------------------------------- decorations
    a(f'<rect x="0" y="0" width="{W}" height="7" fill="url(#accent)"/>')
    a(f'<rect x="0" y="{H - 7}" width="{W}" height="7" fill="url(#accent)"/>')
    # corner hazard blocks
    a(f'<rect x="34" y="40" width="96" height="9" fill="url(#hz)" opacity="0.95"/>')
    a(f'<rect x="34" y="{H - 62}" width="96" height="9" fill="url(#hz)" opacity="0.95"/>')
    # frame corners
    for x, y, sx, sy in ((34, 34, 1, 1), (W - 34, 34, -1, 1), (34, H - 34, 1, -1), (W - 34, H - 34, -1, -1)):
        a(
            f'<path d="M{x} {y + 26 * sy} L{x} {y} L{x + 26 * sx} {y}" fill="none" '
            f'stroke="{PINK}" stroke-width="3" opacity="0.8"/>'
        )

    # --------------------------------------------------------------- identity
    a(
        f'<g transform="translate(34,44)">'
        f'<image x="0" y="0" width="62" height="62" xlink:href="{icon}" href="{icon}"/>'
        f'<rect x="0" y="0" width="62" height="62" fill="none" stroke="{RED}" stroke-width="3"/>'
        f"</g>"
    )
    a(
        f'<text x="112" y="70" font-family="{MONO}" font-size="15" letter-spacing="4" '
        f'fill="{PINK}">P R O X Y  //  N E W  E R I D U</text>'
    )
    a(
        f'<text x="112" y="96" font-family="{MONO}" font-size="12" letter-spacing="2" '
        f'fill="{MUTED}">ZENLESS ZONE ZERO  ·  JUNIOR DEVELOPER</text>'
    )

    # name
    a(
        f'<text x="34" y="222" font-family="{DISPLAY}" font-size="92" font-weight="900" '
        f'letter-spacing="2" fill="{INK}" stroke="{BG}" stroke-width="6" '
        f'paint-order="stroke">OAKJUSTIFY</text>'
    )
    a(
        f'<rect x="36" y="244" width="300" height="6" rx="3" fill="url(#accent)"/>'
    )

    # tagline
    a(
        f'<text x="34" y="292" font-family="{DISPLAY}" font-size="27" font-weight="700" '
        f'letter-spacing="1" fill="{GOLD}">FIRST, SOLVE THE PROBLEM. THEN, WRITE THE CODE.</text>'
    )

    # quick stat chips
    chips = ["C++", "C#", "JavaScript", "Python", "Godot", "Discord.js"]
    cx = 36
    for label in chips:
        w = 26 + len(label) * 10
        a(
            f'<rect x="{cx}" y="316" width="{w}" height="32" rx="6" fill="{BG}" '
            f'fill-opacity="0.72" stroke="{RED}" stroke-width="1.5"/>'
        )
        a(
            f'<text x="{cx + w / 2}" y="337" text-anchor="middle" font-family="{MONO}" '
            f'font-size="13" fill="{INK}">{label}</text>'
        )
        cx += w + 10

    # footer strip
    a(
        f'<text x="36" y="{H - 74}" font-family="{MONO}" font-size="13" letter-spacing="1" '
        f'fill="{MUTED}">16 public repos  ·  learning in public  ·  "Lady, mind if I take a look?"</text>'
    )
    a(
        f'<text x="{W - 36}" y="{H - 74}" text-anchor="end" font-family="{MONO}" '
        f'font-size="13" letter-spacing="3" fill="{GOLD}">AGENT 1142 · 6★ PHYSICAL</text>'
    )

    a("</svg>")
    return "\n".join(s)


def main() -> None:
    out = ASSETS / "header.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"wrote {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()