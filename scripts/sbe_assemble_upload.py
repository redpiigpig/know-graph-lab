#!/usr/bin/env python3
"""東方聖書：逐卷彙整上傳（翻譯 lane 跑 --no-upload 時的收尾第一步）。

lane 帶 --no-upload 時只會走 translate_work 內建的「每 N 節整卷重傳」，
最後一段尾巴不會上去，要靠這支補。

🚨 work 取自 sbe_translate.WORKS，**不是 mueller_auto.WORKS**（後者只有穆勒本人
   16 部）。取錯會 KeyError，而且是靜靜地一本都沒傳——mueller_fill_residuals.py
   就這樣踩過。

用法：
    python -X utf8 scripts/sbe_assemble_upload.py                 # 預設第二批六卷
    python -X utf8 scripts/sbe_assemble_upload.py <slug> [slug…]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mueller_auto as ma  # noqa: E402
import sbe_translate as st  # noqa: E402

BATCH2 = ["sbe-25-laws-of-manu", "sbe-08-bhagavadgita", "sbe-09-quran-2",
          "sbe-15-upanishads-2", "sbe-21-lotus-sutra", "sbe-39-taoism-1"]


def main() -> int:
    slugs = sys.argv[1:] or BATCH2
    by_slug = {w["slug"]: w for w in st.WORKS}
    missing = [s for s in slugs if s not in by_slug]
    if missing:
        print(f"✗ 這些 slug 不在 sbe_translate.WORKS：{missing}", flush=True)
        return 1
    for slug in slugs:
        work = by_slug[slug]
        print(f"▶ {slug}  is_done={ma.is_done(work)}", flush=True)
        ma.assemble_and_upload(work)
    print(f"彙整完成 {len(slugs)} 卷", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
