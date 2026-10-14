# Artwork & attribution

Semua aset gambar di folder `assets/` berasal dari
[Jane Doe · Zenless Zone Zero Wiki](https://zenless-zone-zero.fandom.com/wiki/Jane_Doe)
(HoYoverse / COGNOSPHERE).

| File | Sumber | Dipakai di |
| --- | --- | --- |
| `jane-banner.webp` | *Potential Vision — Jane Doe* (2100×1080) | di-embed ke `header.svg` oleh `scripts/header.py` |
| `jane-portrait.webp` | *Agent Jane Doe Portrait* (1094×2048) | kolom "Focus Areas" |
| `jane-icon.webp` | *Agent Jane Doe Icon* (283×307) | `header.svg` + footer |
| `jane-mindscape.webp` | *Mindscape Jane Doe Full* (2500×1080) | footer |
| `header.svg` | dibuat lokal (`scripts/header.py`) | poster utama |
| `typing.svg` | dibuat lokal (`scripts/typing.py`) | banner typing |

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