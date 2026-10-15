#!/usr/bin/env python3
"""
Give the generated 3D contribution city an idle animation.

github-profile-3d-contrib emits a one-shot grow animation (the columns rise
once, then sit still). This wraps every cube in an extra <g> and animates the
wrapper, which keeps the generated markup and its own <animateTransform>
untouched — animating the cube's own group directly would fight the transform
attribute that positions it.

Design:
  * empty cells breathe very slightly, so the whole grid reads as alive
  * a cell with contributions bobs further the busier that day was
  * the delay is staggered per column, so the motion travels along the timeline
  * the un-animated state is the correct resting state, so if the browser does
    not run CSS animations the city simply sits still rather than breaking
  * prefers-reduced-motion turns it off

Run after the 3D action has written the file:

    python3 animate_city.py profile-3d-contrib/jane-night.svg
"""

from __future__ import annotations

import pathlib
import re
import sys

WRAPPER_CLASS = "cd"

CSS = f""".{WRAPPER_CLASS}{{animation:city-idle 3.4s ease-in-out infinite;animation-delay:var(--d)}}
@keyframes city-idle{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(var(--x),var(--a))}}}}
@media (prefers-reduced-motion:reduce){{.{WRAPPER_CLASS}{{animation:none}}}}
"""

# how far a cell rises at the peak of its bob, by contribution level
AMPLITUDE = {0: -1.2, 1: -3.0, 2: -3.8, 3: -4.6, 4: -5.4}

# a cube group never contains another <g>, so a lazy match to the first </g> is safe
CUBE = re.compile(r'<g transform="translate\(([-\d.]+) ([-\d.]+)\)">(.*?)</g>', re.S)
LEVEL = re.compile(r'class="cont-top-(\d)"')
ROWS_PER_COLUMN = 7
PERIOD = 3.4


def animate(path: pathlib.Path) -> tuple[int, int]:
    svg = path.read_text(encoding="utf-8")

    if f'class="{WRAPPER_CLASS}"' in svg:
        print(f"{path.name}: already animated, nothing to do")
        return 0, 0

    counters = {"moved": 0, "kept": 0}

    def wrap(m: re.Match) -> str:
        inner = m.group(3)
        lv = LEVEL.search(inner)
        if not lv:
            counters["kept"] += 1
            return m.group(0)
        level = int(lv.group(1))
        # the generator walks a column at a time, 7 rows per column
        index = counters["moved"] + counters["kept"]
        column, row = divmod(index, ROWS_PER_COLUMN)
        amp = AMPLITUDE.get(level, -1.2)
        drift = 1.1 if row % 2 == 0 else -1.1
        delay = -(column * (PERIOD / 56.0) + row * 0.03)
        counters["moved"] += 1
        return (
            f'<g class="{WRAPPER_CLASS}" '
            f'style="--d:{delay:.2f}s;--a:{amp}px;--x:{drift:.2f}px">'
            f'{m.group(0)}</g>'
        )

    out = CUBE.sub(wrap, svg)

    # park the animation next to the palette the action already writes
    if "</style>" not in out:
        raise SystemExit("no <style> block found; refusing to guess")
    out = out.replace("</style>", CSS + "</style>", 1)

    path.write_text(out, encoding="utf-8")
    return counters["moved"], counters["kept"]


def main() -> int:
    target = pathlib.Path(
        sys.argv[1] if len(sys.argv) > 1 else "profile-3d-contrib/jane-night.svg"
    )
    if not target.exists():
        raise SystemExit(f"{target} not found")
    moved, kept = animate(target)
    size = target.stat().st_size
    print(f"{target}: wrapped {moved} cubes ({kept} other groups left alone), {size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())