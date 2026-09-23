# -*- coding: utf-8 -*-
"""一次性：把 c:/tmp/aquinas_clean 的清理快取從「冊_序號」改成「冊_原文雜湊」。

2026-09-23 重寫切節（補回被 OCR 打壞標記而漏切的節、題號改從正文讀）。舊快取以
**第幾節（流水序）**為鍵，重切後序號位移，照舊鍵拿會把甲節的清理結果套到乙節上。
改以**該節原文的 SHA-1** 為鍵：原文沒變的節照樣命中，被拆開的節才重新清理。

🚨 必須用**舊版**切節邏輯算雜湊（跟產生這批快取時一樣），所以這支要在改
aquinas_build.split_articles 之前跑；它把舊邏輯凍結在 OLD_OPENER 裡以防萬一。

  python -X utf8 scripts/aquinas_cache_migrate.py
"""
from __future__ import annotations

import hashlib
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")
import aquinas_build as ab  # noqa: E402

OLD_OPENER = re.compile(r"有關第([一二三四五六七八九十百]+)節[，,]?\s*我們討論如下[：:]")


def body_key(raw: str) -> str:
    return hashlib.sha1(raw.strip().encode("utf-8")).hexdigest()[:16]


def main() -> None:
    src_dir = Path("c:/tmp/aquinas_clean")
    dst_dir = src_dir / "by_hash"
    dst_dir.mkdir(exist_ok=True)
    moved = missing = 0
    for vol in ab.REGISTRY:
        rows = ab._load_source(ab.REGISTRY[vol][0])
        full = ab.clean_ocr_light("\n".join(r.get("content", "") for r in rows))
        first = OLD_OPENER.search(full)
        text = full[first.start():] if first else full
        ops = list(OLD_OPENER.finditer(text))
        for k, m in enumerate(ops):
            body = text[m.end(): ops[k + 1].start() if k + 1 < len(ops) else len(text)]
            old = src_dir / f"{vol:02d}_{k:04d}.txt"
            if not old.exists():
                missing += 1
                continue
            shutil.copy2(old, dst_dir / f"{vol:02d}_{body_key(body)}.txt")
            moved += 1
        print(f"  冊{vol}: {len(ops)} 節", flush=True)
    print(f"轉存 {moved} 筆，舊快取缺 {missing} 筆 → {dst_dir}")


if __name__ == "__main__":
    main()
