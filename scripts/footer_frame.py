#!/usr/bin/env python3
"""
Build the README footer device frame:  assets/footer-frame.svg

A ZZZ-style rugged screen bezel with the Railway Transportation GIF playing
inside the panel.  The GIF is embedded as a base64 data URI, exactly like
header.py does with the hero artwork, so the README stays self-contained: no
hotlink, no Camo breakage, and the frame can never drift away from the clip.

Re-run after swapping the GIF:

    python3 footer_frame.py
"""

from __future__ import annotations

import base64
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"

GIF = ASSETS / "jane-railway.webp"
OUT = ASSETS / "footer-frame.svg"

# --- palette (shared with header.svg / typing.svg / chess.svg) -------------
SHELL_HI = "#3b3b54"
SHELL = "#22222f"
SHELL_LO = "#14141d"
EDGE = "#2a2a3c"
PANEL = "#0d0d16"
INK = "#e9e9f5"
GOLD = "#ffd23f"
RED = "#e4324b"
PINK = "#ff5c8a"
MUTED = "#8a8aa6"

MONO = "'Fira Code', 'JetBrains Mono', 'DejaVu Sans Mono', monospace"
DISPLAY = "Impact, 'Arial Black', 'Helvetica Neue', sans-serif"

SCREEN_LABEL = "NEW ERTOU"

# --- geometry -------------------------------------------------------------
W, H = 1080, 664

BODY = (8, 8, 1064, 648)  # x, y, w, h
BODY_R = 28

# the GIF keeps its 480x234 aspect ratio (2.0513), doubled for crispness
SCREEN = (60, 86, 960, 468)
SCREEN_R = 12

SHELF = (118, 576, 844, 54)  # holographic bar under the panel
SHELF_R = 14

SCREW = [(40, 40), (1040, 40), (40, 624), (1040, 624)]
SCREW_R = 10


def data_uri(path: pathlib.Path) -> str:
    mime = "image/webp" if path.suffix == ".webp" else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def sparkle(cx: float, cy: float, r: float, fill: str, opacity: float) -> str:
    """Four-point star, the shape used on the holographic shelf."""
    d = (
        f"M{cx:.1f} {cy - r:.1f}"
        f"Q{cx:.1f} {cy:.1f} {cx + r:.1f} {cy:.1f}"
        f"Q{cx:.1f} {cy:.1f} {cx:.1f} {cy + r:.1f}"
        f"Q{cx:.1f} {cy:.1f} {cx - r:.1f} {cy:.1f}"
        f"Q{cx:.1f} {cy:.1f} {cx:.1f} {cy - r:.1f}Z"
    )
    return f'<path d="{d}" fill="{fill}" opacity="{opacity}"/>'


def vent(cx: float, cy: float, cols: int = 3, rows: int = 4) -> str:
    """Side speaker grille."""
    out = []
    for r in range(rows):
        for c in range(cols):
            x = cx + c * 9
            y = cy + r * 9
            out.append(f'<circle cx="{x}" cy="{y}" r="2.1" fill="{EDGE}"/>')
    return "".join(out)


def build() -> str:
    s: list[str] = []
    a = s.append

    sx, sy, sw, sh = SCREEN
    fx, fy, fw, fh = BODY
    hx, hy, hw, hh = SHELF

    a(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-labelledby="t d">'
    )
    a('<title id="t">Jane Doe — Railway Transportation</title>')
    a(
        '<desc id="d">The Railway Transportation clip playing inside a rugged '
        'agent terminal bezel.</desc>'
    )

    # ---- defs
    a("<defs>")
    a(
        '<linearGradient id="shell" x1="0" y1="0" x2="0.35" y2="1">'
        f'<stop offset="0" stop-color="{SHELL_HI}"/>'
        f'<stop offset="0.42" stop-color="{SHELL}"/>'
        f'<stop offset="1" stop-color="{SHELL_LO}"/></linearGradient>'
    )
    a(
        '<linearGradient id="holo" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{RED}"/>'
        f'<stop offset="0.45" stop-color="{PINK}"/>'
        f'<stop offset="1" stop-color="{GOLD}"/></linearGradient>'
    )
    a(
        '<linearGradient id="sheen" x1="0" y1="0" x2="0.8" y2="1">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0.14"/>'
        '<stop offset="0.38" stop-color="#ffffff" stop-opacity="0.02"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/></linearGradient>'
    )
    a(
        '<linearGradient id="vig" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#000000" stop-opacity="0.28"/>'
        '<stop offset="0.25" stop-color="#000000" stop-opacity="0"/>'
        '<stop offset="0.78" stop-color="#000000" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.34"/>'
        '</linearGradient>'
    )
    a(
        f'<clipPath id="screen"><rect x="{sx}" y="{sy}" width="{sw}" '
        f'height="{sh}" rx="{SCREEN_R}"/></clipPath>'
    )
    a(
        '<filter id="drop" x="-12%" y="-12%" width="124%" height="130%">'
        '<feDropShadow dx="0" dy="10" stdDeviation="14" '
        'flood-color="#000000" flood-opacity="0.45"/></filter>'
    )
    a("</defs>")

    # ---- body shell
    a(
        f'<g filter="url(#drop)"><rect x="{fx}" y="{fy}" width="{fw}" '
        f'height="{fh}" rx="{BODY_R}" fill="url(#shell)" stroke="{EDGE}" '
        f'stroke-width="2"/></g>'
    )
    # top bevel + bottom bevel
    a(
        f'<path d="M{fx + BODY_R} {fy + 1.5} H{fx + fw - BODY_R}" stroke="{SHELL_HI}" '
        f'stroke-width="1.5" opacity="0.85"/>'
    )
    a(
        f'<path d="M{fx + BODY_R} {fy + fh - 1.5} H{fx + fw - BODY_R}" stroke="#000000" '
        f'stroke-width="1.5" opacity="0.5"/>'
    )
    # corner brackets, like the reference's angled shoulders
    for gx, gy, sx_, sy_ in (
        (fx + 20, fy + 16, 1, 1),
        (fx + fw - 20, fy + 16, -1, 1),
        (fx + 20, fy + fh - 16, 1, -1),
        (fx + fw - 20, fy + fh - 16, -1, -1),
    ):
        a(
            f'<path d="M{gx + 40 * sx_} {gy} L{gx + 11 * sx_} {gy} '
            f'Q{gx} {gy} {gx} {gy + 11 * sy_} L{gx} {gy + 40 * sy_}" '
            f'stroke="{SHELL_HI}" stroke-width="2" fill="none" opacity="0.4" '
            f'stroke-linecap="round"/>'
        )

    # ---- screws
    for cx, cy in SCREW:
        a(
            f'<circle cx="{cx}" cy="{cy}" r="{SCREW_R}" fill="{SHELL_LO}" '
            f'stroke="{SHELL_HI}" stroke-width="1.6"/>'
        )
        a(
            f'<circle cx="{cx}" cy="{cy}" r="{SCREW_R - 3.4}" fill="none" '
            f'stroke="{EDGE}" stroke-width="1"/>'
        )
        a(
            f'<path d="M{cx - 4.5} {cy} H{cx + 4.5}" stroke="{SHELL_HI}" '
            f'stroke-width="2" stroke-linecap="round" opacity="0.85"/>'
        )

    # ---- side grilles
    a(vent(30, 258))
    a(vent(1036, 258))

    # ---- top rail label:  ◀◀ NEW ERTOU ▶▶
    mid = W / 2
    ty = 50
    a(
        f'<text x="{mid}" y="{ty}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="17" font-weight="bold" letter-spacing="4" fill="{INK}">'
        f"{SCREEN_LABEL}</text>"
    )
    for dir, off in ((-1, 128), (1, 128)):
        base = mid + dir * off
        for k in range(2):
            bx = base + dir * k * 15
            a(
                f'<path d="M{bx} {ty - 12} L{bx - 9 * dir} {ty - 5} '
                f'L{bx} {ty + 2} Z" fill="{GOLD}"/>'
            )

    # ---- screen bezel
    a(
        f'<rect x="{sx - 7}" y="{sy - 7}" width="{sw + 14}" height="{sh + 14}" '
        f'rx="{SCREEN_R + 7}" fill="{SHELL_LO}" stroke="{EDGE}" stroke-width="1.5"/>'
    )
    a(
        f'<rect x="{sx - 2.5}" y="{sy - 2.5}" width="{sw + 5}" height="{sh + 5}" '
        f'rx="{SCREEN_R + 2}" fill="{PANEL}" stroke="{PINK}" stroke-opacity="0.5" '
        f'stroke-width="1.5"/>'
    )

    # ---- the GIF itself
    a("<g clip-path=\"url(#screen)\">")
    a(
        f'<image x="{sx}" y="{sy}" width="{sw}" height="{sh}" '
        f'preserveAspectRatio="xMidYMid slice" xlink:href="{data_uri(GIF)}" '
        f'href="{data_uri(GIF)}"/>'
    )
    a(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#vig)"/>')
    a(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="url(#sheen)"/>')
    a(
        '<g opacity="0.07">'
        + "".join(
            f'<rect x="{sx}" y="{sy + i * 4}" width="{sw}" height="1" fill="#ffffff"/>'
            for i in range(0, sh // 4)
        )
        + "</g>"
    )
    a("</g>")

    # ---- holographic shelf
    a(
        f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="{SHELF_R}" '
        f'fill="url(#holo)"/>'
    )
    a(
        f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="{SHELF_R}" '
        f'fill="none" stroke="{INK}" stroke-opacity="0.55" stroke-width="1.5"/>'
    )
    a(
        f'<path d="M{hx + 8} {hy + 5} H{hx + hw - 8}" stroke="#ffffff" '
        f'stroke-opacity="0.45" stroke-width="2" stroke-linecap="round"/>'
    )
    for i in range(5):
        cx = hx + 118 + i * 152
        r = 26 if i % 2 == 0 else 19
        a(sparkle(cx, hy + hh / 2, r, "#ffffff", 0.9))
        a(sparkle(cx, hy + hh / 2, r * 0.42, "#ffffff", 1))

    # shelf legs
    for lx in (hx + 26, hx + hw - 26):
        a(
            f'<path d="M{lx} {hy + hh - 2} v22" stroke="{SHELL_LO}" '
            f'stroke-width="5" stroke-linecap="round"/>'
        )
        a(
            f'<circle cx="{lx}" cy="{hy + hh + 22}" r="4" fill="{SHELL_LO}" '
            f'stroke="{SHELL_HI}" stroke-width="1.2"/>'
        )

    # ---- plate marks: corners of the top rail, clear of the title and screws
    a(
        f'<text x="74" y="{ty + 2}" font-family="{MONO}" font-size="12" '
        f'letter-spacing="3" fill="{MUTED}">JANE DOE</text>'
    )
    a(
        f'<text x="{W - 74}" y="{ty + 2}" text-anchor="end" '
        f'font-family="{DISPLAY}" font-size="15" letter-spacing="2" '
        f'fill="{GOLD}">ZZZ</text>'
    )
    a(
        f'<text x="{hx + hw / 2}" y="{hy - 6}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="10" letter-spacing="3" '
        f'fill="{MUTED}" opacity="0.7">SIGNAL · AGENT 1142</text>'
    )

    a("</svg>")
    return "\n".join(s)


def main() -> None:
    if not GIF.exists():
        raise SystemExit(f"missing {GIF}")
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT}  ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()