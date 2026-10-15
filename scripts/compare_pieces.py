#!/usr/bin/env python3
"""
A/B sheet for the two piece renderings.

`chess_contrib.py --pieces` chooses between drawing the board with Unicode chess
characters (whatever the visitor's fonts make of them) and drawing it with the
geometry in `chess_pieces.py`. That choice is easy to argue about and hard to
judge from prose, so this renders both at the real on-board size, on the real
contribution tints, and writes a PNG you can put in a PR description.

    python3 compare_pieces.py --out ../assets/chess-pieces-comparison.png

Needs rsvg-convert (librsvg) or Inkscape to rasterise. If neither is present the
SVG is still written, just not the PNG.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

# Palette and level colours, copied from chess_contrib.py. Duplicated on purpose:
# this script has to import chess_pieces, and chess_pieces deliberately knows
# nothing about boards, so importing chess_contrib would be the coupling to avoid.
HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"

BG = "#0d0d16"
FRAME = "#2a2a3c"
INK = "#e9e9f5"
MUTED = "#7b7b96"
GOLD = "#ffd23f"
PIECE_FILL = "#fff4f6"
BOARD_DARK = "#101019"
LEVEL_COLOR = ["#2b2b3d", "#8a2f4a", "#c22745", "#ff4d6d", "#ff8ab4"]
LEVEL_KEY = ["idle", "1-2", "3-5", "6-9", "10+"]

SQ = 62          # the square edge the real board uses
INSET = 8.0      # ... and the piece inset chess_contrib applies
LABEL_W = 150     # left column, for the row caption
# Each row is a caption block, the tiles, then the commit-count key. The pitch
# has to clear square + key + caption or the next row's caption lands on this
# row's key.
LABEL_H = 116

SCALE_WIDTH = LABEL_W + 5 * SQ   # rasterised at 2x so it stays sharp in a PR


def _tiles(pieces, glyphs: list[str]) -> str:
    """One row: every level, as a board square with a piece on it."""
    out = []
    for level, name in enumerate(pieces):
        x = LABEL_W + level * SQ
        out.append(
            f'<rect x="{x}" y="0" width="{SQ}" height="{SQ}" '
            f'fill="{LEVEL_COLOR[level]}" stroke="{FRAME}"/>'
        )
        if not level:
            out.append(
                f'<circle cx="{x + SQ / 2}" cy="{SQ / 2}" r="3.5" fill="{FRAME}"/>'
            )
            continue
        inner = SQ - INSET * 2
        if name:  # cairo row
            href = f"#piece-{name}"   # matches the id chess_pieces.symbol emits
            out.append(
                f'<use x="{x + INSET}" y="{INSET}" width="{inner}" height="{inner}" '
                f'xlink:href="{href}" href="{href}"/>'
            )
        else:
            out.append(
                f'<text x="{x + SQ / 2}" y="{SQ / 2 + 15}" text-anchor="middle" '
                f'font-family="DejaVu Sans,Segoe UI Symbol,Noto Sans Symbols,sans-serif" '
                f'font-size="40" fill="{PIECE_FILL}">{glyphs[level]}</text>'
            )
    return "".join(out)


def build() -> str:
    import chess_pieces

    order = list(chess_pieces.LEVEL_PIECE)          # [1, 2, 3, 4]
    glyphs = ["", "♟", "♞", "♝", "♛"]
    width = SCALE_WIDTH
    height = LABEL_H * 2 + SQ + 30

    out: list[str] = []
    a = out.append
    a(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Glyph versus cairo chess pieces">'
    )
    a(
        "<defs>"
        + "".join(
            chess_pieces.symbol(chess_pieces.LEVEL_PIECE[l], PIECE_FILL) for l in order
        )
        + "</defs>"
    )
    a(f'<rect width="{width}" height="{height}" fill="{BG}"/>')

    for row, (title, note) in enumerate(
        [
            ("GLYPH", "&#9836; as &lt;text&gt; &#183; rendered by whatever font the visitor has"),
            ("CAIRO", "geometry from chess_pieces.py &#183; identical everywhere"),
        ]
    ):
        top = LABEL_H * row + LABEL_H
        a(
            f'<text x="16" y="{top - 18}" font-family="Verdana,DejaVu Sans,sans-serif" '
            f'font-size="15" font-weight="bold" fill="{GOLD}">{title}</text>'
        )
        a(
            f'<text x="16" y="{top - 3}" font-family="Verdana,DejaVu Sans,sans-serif" '
            f'font-size="9" fill="{MUTED}">{note}</text>'
        )

        # everything below is in row-local coordinates, so it all goes in the group
        a(f'<g transform="translate(0, {top})">')
        # the commit-count key, one swatch per column, tucked under the row so it
        # cannot collide with the caption above
        for level in range(5):
            x = LABEL_W + level * SQ
            a(f'<rect x="{x}" y="{SQ + 14}" width="22" height="10" rx="2" '
              f'fill="{LEVEL_COLOR[level]}"/>')
            a(
                f'<text x="{x + 28}" y="{SQ + 23}" '
                f'font-family="Verdana,DejaVu Sans,sans-serif" '
                f'font-size="10" fill="{MUTED}">{LEVEL_KEY[level]}</text>'
            )
        a(f'<rect x="8" y="0" width="{5 * SQ - 8}" height="{SQ}" fill="{BOARD_DARK}"/>')
        names = (
            [None] * 5
            if row == 0
            else [chess_pieces.LEVEL_PIECE.get(lvl) for lvl in range(5)]
        )
        a(_tiles(names, glyphs))
        a("</g>")

    a("</svg>")
    return "\n".join(out)


def rasterise(svg: pathlib.Path, png: pathlib.Path, scale: int = 2) -> bool:
    """Render `svg` to `png`. Tries each known tool in turn; False if none worked."""
    for argv in (
        ["rsvg-convert", "-w", str(SCALE_WIDTH * scale), "-o", str(png), str(svg)],
        ["inkscape", f"--export-filename={png}", f"--export-width={SCALE_WIDTH * scale}", str(svg)],
    ):
        if not shutil.which(argv[0]):
            continue
        try:
            subprocess.run(argv, check=True, capture_output=True, timeout=60)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            print(f"!! {argv[0]} failed: {exc}", file=sys.stderr)
            continue
        if png.exists():
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ASSETS / "chess-pieces-comparison.png"))
    ap.add_argument("--keep-svg", action="store_true", help="also leave the SVG beside the PNG")
    args = ap.parse_args()

    try:
        import chess_pieces  # noqa: F401
    except ImportError:
        print("!! pycairo is not installed (pip install pycairo)", file=sys.stderr)
        return 1

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    svg_path = out.with_suffix(".svg") if args.keep_svg else out.parent / (out.stem + ".svg")
    svg_path.write_text(build(), encoding="utf-8")

    if not rasterise(svg_path, out):
        print(f"!! no rasteriser available, wrote only {svg_path}", file=sys.stderr)
        return 1

    if not args.keep_svg:
        svg_path.unlink()
    print(f"wrote {out}  ({out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())