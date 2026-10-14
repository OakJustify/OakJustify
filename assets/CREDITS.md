# Artwork & attribution

Semua aset gambar di folder `assets/` berasal dari
[Jane Doe · Zenless Zone Zero Wiki](https://zenless-zone-zero.fandom.com/wiki/Jane_Doe)
(HoYoverse / COGNOSPHERE).

| File | Sumber | Dipakai di |
| --- | --- | --- |
| `jane-banner.webp` | *Potential Vision — Jane Doe* (2100×1080) | di-embed ke `header.svg` oleh `scripts/header.py` |
| `jane-portrait.webp` | *Agent Jane Doe Portrait* (1094×2048) | kolom "Signal Acquired" |
| `jane-icon.webp` | *Agent Jane Doe Icon* (283×307) | `header.svg` + footer |
| `jane-mindscape.webp` | *Mindscape Jane Doe Full* (2500×1080) | footer |

Semua gambar sudah dikompres ke WebP (±60–80 KB) lalu disimpan **lokal** di repo
supaya README tidak bergantung pada hotlink pihak ketiga.

## Regenerasi

```bash
python3 scripts/header.py        # -> assets/header.svg
python3 scripts/chess_contrib.py --out assets/chess.svg
```

> Proyek fan — bukan afiliasi resmi HoYoverse.