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


def vent(cx: float, cy: float, cols: int = 3, rows: int = 4) -> str:
    """Side speaker grille."""
    out = []
    for r in range(rows):
        for c in range(cols):
            x = cx + c * 9
            y = cy + r * 9
            out.append(f'<circle cx="{x}" cy="{y}" r="2.1" fill="{EDGE}"/>')
    return "".join(out)


# --- transport buttons: |<<  <<  pause/play  >>  >>| ---------------------
BTN_W, BTN_H, BTN_R = 54, 38, 12

TRI_S = 7.0  # half height of a transport triangle
TRI_D = TRI_S * 0.88  # how far the apex reaches past the base
PITCH = 7.0  # base-to-base distance between two triangles
BAR_W = 2.6  # the | on the skip keys
GAP = 3.0  # clearance between the bar and the arrows, and key to edge


def tri(x: float, y: float, s: float = TRI_S, right: bool = True) -> str:
    """One play/rewind triangle.  `x` is the BASE; the apex sits TRI_D away."""
    d = s * 0.88
    if right:
        return f"M{x:.1f} {y - s:.1f}L{x + d:.1f} {y:.1f}L{x:.1f} {y + s:.1f}Z"
    return f"M{x:.1f} {y - s:.1f}L{x - d:.1f} {y:.1f}L{x:.1f} {y + s:.1f}Z"


def bar(x: float, y: float, h: float = 15.0, w: float = BAR_W) -> str:
    """The | on the skip keys; `x` is its LEFT edge."""
    return f"M{x:.1f} {y - h / 2:.1f}h{w:.1f}v{h:.1f}h{-w:.1f}Z"


def _arrows(left: float, cy: float, n: int, right: bool) -> str:
    """n arrows whose row starts at `left` and stays inside [left, left+width]."""
    width = (n - 1) * PITCH + TRI_D
    base0 = left + TRI_D if not right else left  # left-pointing apex pokes left
    return "".join(tri(base0 + i * PITCH, cy, right=right) for i in range(n))


def glyph(kind: str, cx: float, cy: float, fill: str) -> str:
    """Transport glyph centred on (cx, cy), laid out from measured extents so
    the | and the arrows can never collide."""
    row = PITCH + TRI_D  # width of a two-arrow row
    if kind == "rew":  # <<
        d = _arrows(cx - row / 2, cy, 2, right=False)
    elif kind == "fwd":  # >>
        d = _arrows(cx - row / 2, cy, 2, right=True)
    else:  # |<<  and  >>|
        right = kind == "next"
        total = row + GAP + BAR_W
        left = cx - total / 2
        if right:
            d = _arrows(left, cy, 2, right=True) + bar(left + row + GAP, cy)
        else:
            d = bar(left, cy) + _arrows(left + BAR_W + GAP, cy, 2, right=False)
    return f'<path d="{d}" fill="{fill}"/>'


def play_pause(cx: float, cy: float, fill: str) -> str:
    """Play triangle and pause bars, cross-fading forever like a real deck."""
    play = f'<path d="{tri(cx + TRI_D / 2, cy, s=8.5)}" fill="{fill}" opacity="0">'
    play += (
        '<animate attributeName="opacity" values="0;0;1;1;0" dur="2.4s" '
        'repeatCount="indefinite" keyTimes="0;0.5;0.5;0.95;1"/></path>'
    )
    pw = 3.0
    pgap = 3.0
    total = pw * 2 + pgap
    left = cx - total / 2
    pause = (
        f'<path d="{bar(left, cy, h=16, w=pw)}'
        f'{bar(left + pw + pgap, cy, h=16, w=pw)}" fill="{fill}">'
    )
    pause += (
        '<animate attributeName="opacity" values="1;1;0;0;1" dur="2.4s" '
        'repeatCount="indefinite" keyTimes="0;0.5;0.5;0.95;1"/></path>'
    )
    return play + pause


def button(kind: str, cx: float, cy: float) -> str:
    """One key on the deck: smoked-grey caps that sit in the bezel.  Only the
    play/pause key gets the accent tint, so the primary control still reads."""
    primary = kind == "toggle"
    out = [
        f'<g><rect x="{cx - BTN_W / 2:.1f}" y="{cy - BTN_H / 2:.1f}" '
        f'width="{BTN_W}" height="{BTN_H}" rx="{BTN_R}" '
        f'fill="{PINK if primary else "#ffffff"}" '
        f'fill-opacity="{0.22 if primary else 0.09}" '
        f'stroke="{PINK if primary else "#ffffff"}" '
        f'stroke-opacity="{0.55 if primary else 0.26}" '
        f'stroke-width="1.2"/>',
        # top gloss, the way a moulded plastic key catches light
        f'<rect x="{cx - BTN_W / 2 + 4:.1f}" y="{cy - BTN_H / 2 + 3:.1f}" '
        f'width="{BTN_W - 8}" height="{BTN_H / 2 - 6:.1f}" rx="{BTN_R / 2}" '
        f'fill="#ffffff" opacity="{0.16 if primary else 0.07}"/>',
    ]
    if primary:
        out.append(play_pause(cx, cy, INK))
    else:
        out.append(glyph(kind, cx, cy, INK))
    out.append("</g>")
    return "".join(out)


def transport(cx0: float, cx1: float, cy: float) -> str:
    """Five keys spread evenly across the strip."""
    order = ["prev", "rew", "toggle", "fwd", "next"]
    step = (cx1 - cx0) / (len(order) - 1)
    return "".join(button(k, cx0 + i * step, cy) for i, k in enumerate(order))


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
        '<linearGradient id="deck" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{SHELL}"/>'
        f'<stop offset="1" stop-color="{SHELL_LO}"/></linearGradient>'
    )
    a(
        '<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{RED}" stop-opacity="0.55"/>'
        f'<stop offset="0.5" stop-color="{PINK}" stop-opacity="0.55"/>'
        f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0.55"/>'
        "</linearGradient>"
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

    # ---- deck: the transport bar, tuned to the bezel instead of fighting it
    a(
        f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="{SHELF_R}" '
        f'fill="url(#deck)" stroke="{SHELL_HI}" stroke-opacity="0.45" '
        f'stroke-width="1.2"/>'
    )
    a(
        f'<path d="M{hx + 10} {hy + 4} H{hx + hw - 10}" stroke="#ffffff" '
        f'stroke-opacity="0.10" stroke-width="1.5" stroke-linecap="round"/>'
    )
    # one thin accent hairline, the only nod left to the old holo strip
    a(
        f'<rect x="{hx + 10}" y="{hy + hh - 5}" width="{hw - 20}" height="2" '
        f'rx="1" fill="url(#accent)"/>'
    )
    a(transport(hx + 96, hx + hw - 96, hy + hh / 2))

    # deck legs
    for lx in (hx + 26, hx + hw - 26):
        a(
            f'<path d="M{lx} {hy + hh - 2} v22" stroke="{SHELL_HI}" '
            f'stroke-opacity="0.5" stroke-width="5" stroke-linecap="round"/>'
        )
        a(
            f'<circle cx="{lx}" cy="{hy + hh + 22}" r="4" fill="{SHELL_LO}" '
            f'stroke="{SHELL_HI}" stroke-opacity="0.7" stroke-width="1.2"/>'
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