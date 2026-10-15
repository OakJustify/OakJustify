#!/usr/bin/env python3
"""
Chess pieces as real geometry, drawn with pycairo instead of borrowed glyphs.

Why
---
`assets/chess.svg` draws every piece as a <text> holding a chess character
("♟", "♞", "♝", "♜", "♛") and lets `font-family` decide what it looks like. So
the board is not one image, it is five: Windows falls back to Segoe UI Symbol,
Linux to DejaVu, macOS to something else again, and a box with no match gets
tofu in the middle of the board. The pieces are the one thing on that board
which should not drift between visitors.

These are plain paths instead. Same silhouette everywhere, and the shapes belong
to the theme rather than to whichever font happened to be installed.

Details that matter
-------------------
* Everything is drawn inside a 100x100 box with the baseline at y=100, so a
  caller can place a piece with one translate + one scale and never think about
  units again.
* Holes (the knight's eye, the bishop's slit) are cut with the even-odd fill
  rule rather than by painting over in the background colour, so a piece stays
  correct on any square colour -- including the five contribution-level tints.
* No text is drawn here at all, so nothing depends on a font being present.

This module only draws. It knows nothing about contributions, boards or layout;
`chess_contrib.py` owns that.

Requires pycairo:
    pip install pycairo
"""

from __future__ import annotations

import math
import pathlib
import re
import tempfile

# NB: `from typing import ...` does not work in this directory -- scripts/typing.py
# shadows the standard library module for anything run from here. collections.abc
# is not shadowed, so that is the one to use.
from collections.abc import Callable

import cairo

# Every piece is authored in this box: origin top-left, baseline at y = UNIT.
UNIT = 100.0

# Piece -> drawing routine, in the order a queen, king, bishop ... would sit.
PIECES: dict[str, Callable[[cairo.Context], None]] = {}


def piece(name: str) -> Callable[[cairo.Context], None]:
    """Register a drawing routine under `name` and hand it back for the table."""
    def wrap(fn: Callable[[cairo.Context], None]) -> Callable[[cairo.Context], None]:
        PIECES[name] = fn
        return fn
    return wrap


# --------------------------------------------------------------- shared base --
# Every piece stands on the same plinth and rises out of the same column, so the
# five read as one set instead of five clip-art downloads. Changing BASELINE or
# PLINTH_H retunes the whole family at once.

BASELINE = 100.0
PLINTH_H = 12.0          # the wide foot slab
FLARE_H = 10.0           # the taper from foot to stem
STEM_TOP = 46.0          # where the column ends and the head begins
COLLAR_H = 7.0


def _plinth(c: cairo.Context) -> None:
    """Two-tier foot. Subtle enough to disappear, structural enough to notice."""
    y = BASELINE - PLINTH_H
    c.rectangle(4, y, 92, PLINTH_H)
    c.fill()

    # trapezoid flare: wide at the foot, narrow where the stem begins
    c.move_to(9, y)
    c.line_to(91, y)
    c.line_to(78, y - FLARE_H)
    c.line_to(22, y - FLARE_H)
    c.close_path()
    c.fill()


def _stem(c: cairo.Context) -> None:
    """Tapered column with slightly concave sides, like a turned chess piece."""
    top, bot = STEM_TOP, BASELINE - PLINTH_H - FLARE_H
    c.move_to(34, top)
    c.curve_to(31, top + 12, 30, bot - 10, 27, bot)
    c.line_to(73, bot)
    c.curve_to(70, bot - 10, 69, top + 12, 66, top)
    c.close_path()
    c.fill()


def _collar(c: cairo.Context) -> None:
    """Ring where the head meets the column."""
    c.rectangle(30, STEM_TOP - COLLAR_H, 40, COLLAR_H)
    c.fill()


def _wide_collar(c: cairo.Context) -> None:
    """Collar for the round-headed pieces, whose head would otherwise swallow it."""
    c.rectangle(26, STEM_TOP - COLLAR_H, 48, COLLAR_H)
    c.fill()


def _base(c: cairo.Context) -> None:
    _plinth(c)
    _stem(c)
    _collar(c)


def _disc(c: cairo.Context, cx: float, cy: float, r: float) -> None:
    c.new_sub_path()
    c.arc(cx, cy, r, 0, 2 * math.pi)
    c.close_path()


# --------------------------------------------------------------------- pieces --


@piece("pawn")
def _pawn(c: cairo.Context) -> None:
    """Smallest silhouette: sphere on a stem. Reads correctly at 40px."""
    _plinth(c)
    _stem(c)
    _wide_collar(c)
    _disc(c, 50, 28, 15)
    c.fill()


@piece("rook")
def _rook(c: cairo.Context) -> None:
    """Crenellated tower. Four merlons plus the necking band under them."""
    _base(c)
    c.rectangle(34, 22, 32, STEM_TOP - COLLAR_H - 22)
    c.fill()

    for i in range(4):
        c.rectangle(30 + i * 11, 11, 7.5, 13)
        c.fill()

    # necking: flares back out under the battlements
    c.move_to(27, 24)
    c.line_to(73, 24)
    c.line_to(69, 19)
    c.line_to(31, 19)
    c.close_path()
    c.fill()


@piece("knight")
def _knight(c: cairo.Context) -> None:
    """Horse head facing left, matching the old ♞/♘ glyphs.

    Drawn as an outline plus an eye. The eye is a sub-path filled with the
    even-odd rule so it becomes a genuine hole -- it shows the square colour
    through it, which keeps the piece correct on all six board tints.
    """
    _plinth(c)
    _stem(c)

    # Traced clockwise from the throat: face and muzzle first, then up the cheek,
    # through both ears, then down the crest.
    c.move_to(34, STEM_TOP)                 # throat, front of the neck
    c.curve_to(32, 37, 27, 33, 21, 30)      # cheekbone down to the bridge
    c.line_to(16, 28)                        # bridge of the nose
    c.line_to(14, 40)                        # blunt front of the muzzle
    c.curve_to(22, 44, 30, 45, 40, 45)       # lip along to the jaw
    c.line_to(48, 45)                        # under the cheek
    c.curve_to(54, 40, 56, 32, 56, 25)       # up the face
    c.line_to(57, 6)                         # front ear
    c.line_to(63, 18)                        # notch between the ears
    c.line_to(67, 4)                         # back ear
    c.line_to(71, 20)                        # notch behind it
    c.curve_to(82, 30, 82, 45, 74, STEM_TOP)  # crest, then down the neck
    c.close_path()

    _disc(c, 34, 33, 2.8)                    # eye, cut out by even-odd
    c.set_fill_rule(cairo.FillRule.EVEN_ODD)
    c.fill()
    c.set_fill_rule(cairo.FillRule.WINDING)


@piece("bishop")
def _bishop(c: cairo.Context) -> None:
    """Mitre with the traditional slit, plus the small ball on its crown."""
    _base(c)

    c.move_to(50, 9)
    c.curve_to(67, 25, 71, 37, 50, STEM_TOP)
    c.curve_to(29, 37, 33, 25, 50, 9)
    c.close_path()

    # slit: a thin lens cut through the mitre, widest in the middle
    c.move_to(50, 15)
    c.curve_to(55, 24, 55, 29, 50, 33)
    c.curve_to(45, 29, 45, 24, 50, 15)
    c.close_path()

    c.set_fill_rule(cairo.FillRule.EVEN_ODD)
    c.fill()
    c.set_fill_rule(cairo.FillRule.WINDING)

    _disc(c, 50, 4, 5)
    c.fill()


@piece("queen")
def _queen(c: cairo.Context) -> None:
    """Coronet: five points with a bead on each, over a straight coronet band."""
    _base(c)

    tips = [(24, 12), (37, 15), (50, 10), (63, 15), (76, 12)]
    valleys = [(30.5, 34), (43.5, 32), (56.5, 32), (69.5, 34)]

    outline: list[tuple[float, float]] = [(14, 45)]
    for tip, valley in zip(tips, valleys):
        outline.append(tip)
        outline.append(valley)
    outline.append(tips[-1])
    outline.append((86, 45))

    c.move_to(*outline[0])
    for x, y in outline[1:]:
        c.line_to(x, y)
    c.close_path()
    c.fill()

    # a bead capping each point, which is what separates a queen from a rook
    for x, y in tips:
        _disc(c, x, y, 4)
        c.fill()

    c.rectangle(12, 41, 76, 5)
    c.fill()


@piece("king")
def _king(c: cairo.Context) -> None:
    """Cross on a flared crown. Not used by the contribution levels today --
    kept so the set is complete and the family stays coherent."""
    _base(c)

    c.rectangle(46.5, 0, 7, 24)
    c.fill()
    c.rectangle(40, 7, 20, 7)
    c.fill()

    c.move_to(24, 45)
    c.line_to(31, 26)
    c.line_to(41, 36)
    c.line_to(50, 23)
    c.line_to(59, 36)
    c.line_to(69, 26)
    c.line_to(76, 45)
    c.close_path()
    c.fill()

    c.rectangle(22, 41, 56, 5)
    c.fill()


# ------------------------------------------------------------------- drawing --
# Contribution level -> piece, indexed the same way as LEVEL_COLOR in
# chess_contrib.py: 0 is the empty square, and the four occupied levels step up
# the pieces in the usual order.
#
# Four levels means four pieces, so the rook and the king never make it onto the
# board. They stay in PIECES because the set is drawn as a family and a piece
# that exists only for the sheet is still worth having.
LEVEL_PIECE: dict[int, str] = {1: "pawn", 2: "knight", 3: "bishop", 4: "queen"}

# The same table keyed for the legend, which needs a name for level 0 too.
LEVEL_LABEL: dict[int, str] = {0: "idle", 1: "pawn", 2: "knight", 3: "bishop", 4: "queen"}


def draw(c: cairo.Context, name: str, x: float, y: float, size: float) -> None:
    """Draw `name` with its baseline at (x, y), occupying a `size` x `size` box.

    (x, y) is the bottom-left of the box, matching how a chess piece sits on a
    square rather than where a path origin would land.
    """
    if name not in PIECES:
        raise KeyError(f"unknown piece {name!r}; have {sorted(PIECES)}")
    c.save()
    c.translate(x, y - size)
    c.scale(size / UNIT, size / UNIT)
    PIECES[name](c)
    c.restore()


def draw_level(c: cairo.Context, level: int, x: float, y: float, size: float) -> str:
    """Draw whatever piece `level` maps to. Level 0 draws nothing.

    Returns the piece name so callers can label it or key a style off it.
    """
    name = LEVEL_PIECE.get(level)
    if name is None:
        return ""
    draw(c, name, x, y, size)
    return name


# ------------------------------------------------------------- as SVG markup --
# The board in chess_contrib.py is still assembled as text, so these pieces have
# to be handed over as markup rather than as a cairo context. Cairo is happy to
# render one piece into its own SVG and emit nothing but <path> elements, which
# lift straight out of the <svg> wrapper.
#
# One <symbol> per piece plus a <use> per square keeps the board the size it is
# today: the five outlines are paid for once, and each square costs ~50 bytes
# instead of the ~500 a piece's worth of inline paths would run to.

_PATH_RE = re.compile(r"<path\b[^>]*/>")

_cache: dict[tuple[str, tuple[int, int, int]], str] = {}


def _paths(name: str, colour: tuple[int, int, int]) -> list[str]:
    key = (name, colour)
    if key in _cache:
        return _cache[key]  # type: ignore[return-value]

    # cairo will not write an SVG to anything but a file, so give it one in the
    # system temp dir and read it straight back.
    with tempfile.TemporaryDirectory() as tmp:
        scratch = pathlib.Path(tmp) / f"{name}.svg"
        surface = cairo.SVGSurface(str(scratch), UNIT, UNIT)
        context = cairo.Context(surface)
        context.set_source_rgb(*colour)
        PIECES[name](context)
        surface.finish()
        found = _PATH_RE.findall(scratch.read_text(encoding="utf-8"))

    if not found:
        raise RuntimeError(f"cairo produced no paths for piece {name!r}")
    _cache[key] = found
    return found


def symbol(name: str, colour: str = "#fff4f6") -> str:
    """Return a <symbol> for `name`, ready to drop inside <defs>."""
    rgb = _rgb(colour)
    body = "\n".join(_paths(name, rgb))
    return f'<symbol id="piece-{name}" viewBox="0 0 {UNIT:g} {UNIT:g}">{body}</symbol>'


def use(name: str, x: float, y: float, size: float, fill: str | None = None) -> str:
    """Return a <use> placing `name` at the top-left (x, y) in a size x size box."""
    href = f"#piece-{name}"
    style = f' fill="{fill}"' if fill else ""
    # xlink:href alongside href: GitHub sanitises SVG and older renderers still
    # only understand the namespaced form. Same belt-and-braces as header.py.
    return (
        f'<use x="{x:g}" y="{y:g}" width="{size:g}" height="{size:g}" '
        f'xlink:href="{href}" href="{href}"{style}/>'
    )


def _rgb(colour: str) -> tuple[int, int, int]:
    """#rgb or #rrggbb -> the 0..1 cairo wants. Kept local so the module does not
    grow a hard dependency on a colour library for three lines of arithmetic."""
    h = colour.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)