# Artwork & attribution

Semua aset gambar di folder `assets/` berasal dari
[Jane Doe · Zenless Zone Zero Wiki](https://zenless-zone-zero.fandom.com/wiki/Jane_Doe)
(HoYoverse / COGNOSPHERE).

| File | Sumber | Dipakai di |
| --- | --- | --- |
| `jane-banner.webp` | *Potential Vision — Jane Doe* (2100×1080) | di-embed ke `header.svg` oleh `scripts/header.py` |
| `jane-portrait.webp` | *Agent Jane Doe Portrait* (1094×2048) | kolom "Focus Areas" |
| `jane-icon.webp` | *Agent Jane Doe Icon* (283×307) | `header.svg` + footer |
| `jane-mindscape.webp` | *Mindscape Jane Doe Full* (2500×1080) | tidak dipakai di README (footer kini memakai GIF GIPHY) |
| `header.svg` | dibuat lokal (`scripts/header.py`) | poster utama |
| `typing.svg` | dibuat lokal (`scripts/typing.py`) | banner focus |
| `fonts/JetBrainsMono-Bold-subset.ttf` | [JetBrains Mono Bold](https://www.jetbrains.com/lp/mono/), di-subset ke 88 glyph | di-embed ke `typing.svg` |

## GIF footer

GIF di footer README (bagian "Railway Transportation") di-hotlink langsung dari
GIPHY, dengan kredit di bawah gambarnya:

- [Jane Doe · Zenless Zone Zero](https://giphy.com/gifs/zzz-jane-doe-zenlesszonezero-z1cQsP01hYb4DrK9Rz) — GIPHY

## Lisensi font

JetBrains Mono released di bawah **SIL Open Font License 1.1**. Subset di
`assets/fonts/` dan BASE64-nya di-embed ke `assets/typing.svg`, jadi font itu
ikut terdistribusi bersama repo. OFL mengizinkan hal tersebut asal atribusi
disertakan:

```
JetBrains Mono
Copyright (c) 2020 The JetBrains Mono Project Authors (https://github.com/JetBrains/JetBrainsMono)
Licensed under the SIL Open Font License, Version 1.1
https://scripts.sil.org/OFL
```

Semua gambar sudah dikompres ke WebP (±60–80 KB) lalu disimpan **lokal** di repo
supaya README tidak bergantung pada hotlink pihak ketiga.

Regenerate after swapping the artwork:

```bash
python3 scripts/header.py        # -> assets/header.svg
python3 scripts/typing.py        # -> assets/typing.svg
python3 scripts/chess_contrib.py --out assets/chess.svg
```

> Relative image paths in `README.md` carry a `?v=N` suffix. Bump it whenever an
> asset changes, otherwise GitHub's camo proxy keeps serving the cached copy.

> Proyek fan — bukan afiliasi resmi HoYoverse.