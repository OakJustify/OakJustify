#!/usr/bin/env python3
"""
Contribution Chess  --  render the last 64 days of GitHub contributions as a
chess position.

Every square is one day. A day with contributions gets a piece whose type tells
you how busy that day was; the piece colour tells you how hot.  Pure stdlib so it
runs anywhere inside GitHub Actions.

    python3 chess_contrib.py --user OakJustify --out ../assets/chess.svg

Pieces come in two flavours, chosen with --pieces:

    glyph  (default) the chess characters ♟♞♝♜♛ as <text>. No dependencies,
           but whichever font the visitor's browser picks decides what they look
           like, so the board is not the same image for everyone.
    cairo  the same five pieces as geometry drawn by chess_pieces.py and reused
           with <use>. Identical everywhere. Needs pycairo installed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone
from xml.sax.saxutils import escape

# ---------------------------------------------------------------- palette ---
# Zenless Zone Zero / Jane Doe inspired ramp.
BG = "#08080d"
BOARD_DARK = "#101019"
BOARD_LIGHT = "#1a1a26"
FRAME = "#2a2a3c"
INK = "#e9e9f5"
MUTED = "#7b7b96"
GOLD = "#ffd23f"
RED = "#e4324b"

# 0 -> 4 (GitHub contribution levels) mapped to the ZZZ ramp.
LEVEL_COLOR = ["#2b2b3d", "#8a2f4a", "#c22745", "#ff4d6d", "#ff8ab4"]

# Indexed by contribution level, so index 0 is the empty square. These line up
# one for one with LEVEL_PIECE in chess_pieces.py -- the board and the legend
# below read from the same table, which they did not used to (the board drew
# PIECE_GLYPH[level + 1] while the legend printed PIECE_GLYPH[level], so every
# square showed one piece heavier than its own key said it should).
PIECE_GLYPH = ["", "♟", "♞", "♝", "♛"]

# Legend caption per level, for glyph mode. cairo mode reads the same names out
# of chess_pieces.LEVEL_LABEL instead.
LEGEND_LABELS = ["idle", "pawn", "knight", "bishop", "queen"]

# Two ways to get a piece onto the board, picked with --pieces:
#
#   glyph  the characters above, as <text>. Cheap, editable, and it renders
#          differently on every machine because whichever of DejaVu / Segoe UI
#          Symbol / whatever else the visitor happens to have gets to decide what
#          a knight looks like.
#   cairo  the same four pieces drawn as geometry by scripts/chess_pieces.py, one
#          <symbol> per piece reused with <use>. Identical everywhere.
PIECE_MODES = ("glyph", "cairo")

# how much of each square the piece occupies, and the colour it is drawn in
PIECE_INSET = 8.0
PIECE_FILL = "#fff4f6"

FILES = "abcdefgh"

QUERY = """
query($login:String!){
  user(login:$login){
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount contributionLevel weekday } }
      }
    }
  }
}
"""


def level_for(count: int) -> int:
    """Bucket a raw commit count the way GitHub's own heatmap does."""
    if count <= 0:
        return 0
    if count < 3:
        return 1
    if count < 6:
        return 2
    if count < 10:
        return 3
    return 4


def fetch(login: str, token: str) -> dict:
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "User-Agent": "contribution-chess",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError(payload["errors"][0].get("message", "graphql error"))
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


# ------------------------------------------------------------------ render --
def _load_pieces() -> object:
    """Import chess_pieces lazily so the script still runs without pycairo."""
    try:
        import chess_pieces
    except ImportError as exc:  # pragma: no cover - depends on the runner
        raise SystemExit(
            "--pieces cairo needs pycairo (pip install pycairo); "
            "the default --pieces glyph does not"
        ) from exc
    return chess_pieces


def build_svg(days: list[dict], username: str, total: int, pieces: str = "glyph") -> str:
    if pieces not in PIECE_MODES:
        raise ValueError(f"pieces must be one of {PIECE_MODES}, got {pieces!r}")

    sq = 62                      # square edge
    pad = 26                     # board padding
    board = sq * 8
    header = 104
    footer = 70
    width = board + pad * 2
    height = header + board + pad + footer

    pieces_mod = _load_pieces() if pieces == "cairo" else None
    piece_size = sq - PIECE_INSET * 2

    def emit_piece(add, name: str, level: int, x: float, y: float, size: float) -> None:
        """Drop one piece into the output. `x`/`y` are the box's top-left."""
        if pieces_mod is not None:
            add(pieces_mod.use(name, x, y, size))
        else:
            add(
                f'<text x="{x + size / 2:g}" y="{y + size / 2 + size * 0.38:.1f}" '
                f'text-anchor="middle" '
                f'font-family="DejaVu Sans,Segoe UI Symbol,Noto Sans Symbols,sans-serif" '
                f'font-size="{size * 0.82:.0f}" fill="{PIECE_FILL}">'
                f"{PIECE_GLYPH[level]}</text>"
            )

    def piece_for(level: int) -> str:
        """The piece name behind a contribution level, whichever mode is active."""
        if pieces_mod is not None:
            return pieces_mod.LEVEL_PIECE[level]
        return ""

    # Keep the newest 64 days, oldest first -> reads like a game's move list.
    days = days[-64:]
    days = days + [
        {"date": None, "contributionCount": 0, "contributionLevel": "NONE"}
    ] * (64 - len(days))

    out: list[str] = []
    add = out.append

    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="GitHub contributions of {escape(username)} as a chess board">'
    )
    add(
        "<defs>"
        f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#0d0d16"/>'
        f'<stop offset="1" stop-color="{BG}"/>'
        "</linearGradient>"
        f'<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{RED}"/>'
        f'<stop offset="1" stop-color="{GOLD}"/>'
        "</linearGradient>"
        f'<filter id="glow" x="-60%" y="-60%" width="220%" height="220%">'
        f'<feGaussianBlur stdDeviation="5" result="b"/>'
        f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
        "</filter>"
        + (
            ""
            if pieces_mod is None
            else "".join(
                pieces_mod.symbol(n, PIECE_FILL) for n in pieces_mod.PIECES if n != "king"
            )
        )
        + "</defs>"
    )
    add(f'<rect width="{width}" height="{height}" rx="18" fill="url(#bg)"/>')
    add(
        f'<rect x="1.5" y="1.5" width="{width - 3}" height="{height - 3}" rx="17" '
        f'fill="none" stroke="{FRAME}" stroke-width="3"/>'
    )

    # ------------------------------------------------------------- header ---
    add(
        f'<text x="{pad}" y="44" font-family="Verdana,DejaVu Sans,sans-serif" '
        f'font-size="24" font-weight="bold" fill="{INK}" letter-spacing="4">'
        f'CONTRIBUTION CHESS</text>'
    )
    add(
        f'<text x="{width - pad}" y="44" text-anchor="end" '
        f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="28" font-weight="bold" '
        f'fill="{GOLD}">{total}</text>'
    )
    add(
        f'<text x="{width - pad}" y="62" text-anchor="end" '
        f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="10" fill="{MUTED}" '
        f'letter-spacing="2">COMMITS · LAST 64 DAYS</text>'
    )
    add(
        f'<rect x="{pad}" y="74" width="{board}" height="4" rx="2" fill="url(#accent)"/>'
    )
    add(
        f'<text x="{pad}" y="96" font-family="Verdana,DejaVu Sans,sans-serif" '
        f'font-size="11" fill="{MUTED}" letter-spacing="1.5">'
        f'{escape(username.upper())} · EVERY SQUARE IS A DAY · a8 = OLDEST → h1 = NEWEST'
        f'</text>'
    )

    # -------------------------------------------------------------- board ---
    top = header
    for row in range(8):
        for col in range(8):
            day = days[row * 8 + col]
            lvl = level_for(day.get("contributionCount", 0))
            x = pad + col * sq
            y = top + row * sq
            dark = (row + col) % 2 == 0
            fill = BOARD_DARK if dark else BOARD_LIGHT
            if lvl:
                fill = LEVEL_COLOR[lvl]
            add(
                f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="{fill}" '
                f'stroke="{FRAME}" stroke-width="1"/>'
            )

            if lvl == 0:
                add(
                    f'<circle cx="{x + sq / 2}" cy="{y + sq / 2}" r="3.5" '
                    f'fill="{FRAME}"/>'
                )
                continue

            emit_piece(add, piece_for(lvl), lvl, x + PIECE_INSET, y + PIECE_INSET, piece_size)
            if lvl >= 4:
                add(
                    f'<rect x="{x + 2}" y="{y + 2}" width="{sq - 4}" height="{sq - 4}" '
                    f'rx="6" fill="none" stroke="{GOLD}" stroke-width="2.5" '
                    f'filter="url(#glow)"/>'
                )

    # coordinates
    for col, letter in enumerate(FILES):
        add(
            f'<text x="{pad + col * sq + sq / 2}" y="{top + board + 18}" '
            f'text-anchor="middle" font-family="Verdana,DejaVu Sans,sans-serif" '
            f'font-size="11" fill="{MUTED}">{letter}</text>'
        )
    for row in range(8):
        add(
            f'<text x="{pad - 10}" y="{top + row * sq + sq / 2 + 4}" text-anchor="end" '
            f'font-family="Verdana,DejaVu Sans,sans-serif" font-size="11" '
            f'fill="{MUTED}">{8 - row}</text>'
        )

    # ------------------------------------------------------------- footer ---
    fy = top + board + pad + 20
    legend = ["0", "1-2", "3-5", "6-9", "10+"]
    labels = [pieces_mod.LEVEL_LABEL[i] if pieces_mod else LEGEND_LABELS[i]
              for i in range(len(legend))]
    lx = pad
    for i, c in enumerate(LEVEL_COLOR):
        add(f'<rect x="{lx}" y="{fy}" width="26" height="12" rx="3" fill="{c}"/>')
        add(
            f'<text x="{lx + 33}" y="{fy + 11}" font-family="Verdana,DejaVu Sans,sans-serif" '
            f'font-size="11" fill="{MUTED}">{legend[i]}</text>'
        )
        lx += 99
    # second line spells out what each piece means
    lx = pad
    for i in range(len(legend)):
        if i:
            if pieces_mod is not None:
                add(pieces_mod.use(pieces_mod.LEVEL_PIECE[i], lx, fy + 16, 22))
                label_x = lx + 28
            else:
                add(
                    f'<text x="{lx}" y="{fy + 34}" '
                    f'font-family="Verdana,DejaVu Sans,sans-serif" '
                    f'font-size="15" fill="{INK}">{PIECE_GLYPH[i]}</text>'
                )
                label_x = lx + 17
            add(
                f'<text x="{label_x}" y="{fy + 33}" '
                f'font-family="Verdana,DejaVu Sans,sans-serif" '
                f'font-size="10" fill="{MUTED}">{labels[i]}</text>'
            )
        lx += 99

    add("</svg>")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("USERNAME", "OakJustify"))
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN", ""))
    ap.add_argument("--out", default="../assets/chess.svg")
    ap.add_argument(
        "--pieces",
        choices=PIECE_MODES,
        default="glyph",
        help="glyph: Unicode chess characters, rendered by the visitor's fonts. "
        "cairo: geometry from chess_pieces.py, identical everywhere (needs pycairo).",
    )
    args = ap.parse_args()

    if not args.token:
        print("!! no GITHUB_TOKEN, writing placeholder board", file=sys.stderr)

    try:
        cal = fetch(args.user, args.token)
        days = [d for w in cal["weeks"] for d in w["contributionDays"]]
        total = cal["totalContributions"]
    except Exception as exc:  # network / auth / rate-limit
        print(f"!! contribution fetch failed: {exc}", file=sys.stderr)
        cal, total, days = None, 0, []

    svg = build_svg(days, args.user, total, pieces=args.pieces)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {args.out} ({total} contributions, pieces={args.pieces})")
    return 0


if __name__ == "__main__":
    sys.exit(main())