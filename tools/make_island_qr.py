#!/usr/bin/env python3
"""產生會場投影版用的 QR code：island/qr.png，內容是 island_meta.SHOW["qr_url"]（工作坊總覽首頁）。

網址沒變就不必重產；產物要 commit。需要 segno（純 Python，不裝進專案）：
  uv run --with segno python tools/make_island_qr.py
"""
import sys
from pathlib import Path

import segno

sys.path.insert(0, str(Path(__file__).resolve().parent))
import island_meta as M  # noqa: E402

OUT = M.ROOT / "island" / "qr.png"
qr = segno.make(M.SHOW["qr_url"], error="m", micro=False)
qr.save(OUT, scale=12, border=2, dark="#1b1b2b", light="#ffffff")
print(f"寫入 {OUT.relative_to(M.ROOT)}：{M.SHOW['qr_url']}（版本 {qr.version}，{OUT.stat().st_size} bytes）")
