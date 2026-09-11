#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""替 /collected-works 的佛學作家補肖像（2026-09-11 使用者要求）。

維基與 Commons 上這幾位**沒有現成的條目主圖**，所以逐一查來源、逐一目視確認。
取到的三張與其授權：

  太虛大師   Commons《释太虚法师全身肖像照》  **公有領域**（1947 圓寂，攝於民國時期）
  星雲大師   Commons《Hsing Yun (cropped)》  **CC BY 2.0**（lovesx-70）
  昭慧法師   弘誓學院官網 /dharma-teachers/zhaohui/ 的 profile_chaohwei.webp
             ——道場自家頁面，登入制私人研究站使用（使用者 2026-09-11 裁定）

🚨 **差一點放錯臉**：弘誓 `/about/` 上另有 `profile_jiangan.webp` 與
`profile_singhow.webp`，檔名看起來像「見岸」「性廣」，實際上頁面結構化資料裡
`profile_jiangan` 標的是**昭慧法師**、`profile_singhow` 標的是**心皓法師**——
檔名、JSON-LD 的 name 欄與照片本人三者互相對不上。只有從**本人專屬頁**
（/dharma-teachers/zhaohui/）取的那張三方一致。所以規矩是：
**一定要從本人專屬頁取，而且要把圖打開看過**，不能信檔名。

性廣法師的專屬頁沒有照片，聖嚴法師與印順法師在 Commons 查到的全是同名他人
（Sheng Yen → 盧勝彥），一律留空用 emoji 佔位，不硬放。

  python -X utf8 scripts/cw_portraits_install.py            # dry-run
  python -X utf8 scripts/cw_portraits_install.py --apply
"""
from __future__ import annotations

import argparse
import io
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "public/portraits"
UA = {"User-Agent": "know-graph-lab/1.0 (private research library; redpiigpig@gmail.com)"}

PORTRAITS = [
    {
        "slug": "taixu", "name": "太虛大師", "file": "taixu.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/ee/"
               "%E9%87%8A%E5%A4%AA%E8%99%9A%E6%B3%95%E5%B8%88%E5%85%A8%E8%BA%AB%E8%82%96%E5%83%8F%E7%85%A7.jpg",
        "credit": "Wikimedia Commons，公有領域",
        # 全身像，頭在上方三分之一；裁成頭肩比例才不會在卡片上變成一顆小點
        "crop": (0.22, 0.02, 0.78, 0.42),
    },
    {
        "slug": "hsingyun", "name": "星雲大師", "file": "hsingyun.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Hsing_Yun_%28cropped%29.jpg",
        "credit": "Wikimedia Commons，lovesx-70，CC BY 2.0",
        "crop": None,
    },
    {
        "slug": "chao-hwei", "name": "昭慧法師", "file": "chao-hwei.jpg",
        "url": "https://www.hongshi.org.tw/press/master/profile_chaohwei.webp",
        "credit": "佛教弘誓學院官網",
        "crop": None,
    },
]

MAX_EDGE = 500  # 卡片與 hub 都只用到幾百 px，存大圖沒有意義


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    from PIL import Image
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in PORTRAITS:
        raw = fetch(p["url"])
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        before = im.size
        if p["crop"]:
            w, h = im.size
            l, t, r, b = p["crop"]
            im = im.crop((int(w * l), int(h * t), int(w * r), int(h * b)))
        im.thumbnail((MAX_EDGE, MAX_EDGE))
        dest = OUT_DIR / p["file"]
        print(f"  {p['name']:<8} {before} → {im.size}　{p['credit']}")
        if a.apply:
            im.save(dest, "JPEG", quality=86)
            print(f"      ✅ {dest.relative_to(ROOT)}")
    if not a.apply:
        print("\n（dry-run，加 --apply 才會寫檔）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
