# -*- coding: utf-8 -*-
"""全集 20 卷是不是都轉錄完了？完了回 0、還有沒轉的回 1。

夜班 bat 拿這個離開碼決定要不要把排程關掉。抽成一支小腳本，是因為原本那行
內嵌的 `python -c "...regex..."` 在 cmd 裡被引號與百分號咬到，等於永遠判不出來。

🚨 2026-09-18 改判準：本來查 `ebooks.chunk_count > 0`，但這條線根本不寫 DB ——
`mineru_ocr.py run --book` 只把 JSONL 寫到 Drive（全集不混進圖書館），
chunk_count 永遠是 null。於是 20 卷全轉完了這支也永遠回 1，排程**永遠不會關掉**、
每晚空轉。現在改看成品本身：Drive 上那份 JSONL 的段數。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uchimura_zenshu_ocr import VOLS, transcribed  # noqa: E402


def main() -> int:
    counts = {v: transcribed(v) for v in VOLS}
    missing = [v for v, n in counts.items() if not n]
    # 印出來才查得到為什麼沒關 —— 靜默回 1 跟「G: 沒掛」長得一模一樣。
    print(f"已轉錄 {len(VOLS) - len(missing)}/{len(VOLS)} 卷"
          + (f"，還缺：{missing}" if missing else "，全數完成"))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
