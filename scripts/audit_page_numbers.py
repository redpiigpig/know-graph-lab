# -*- coding: utf-8 -*-
"""稽核所有 reader JSONL 的 `page_number` 到底是不是**原書頁碼**。

為什麼要有這一支：使用者 2026-09-09 問「我引用時能知道是第幾頁嗎」。查下去發現
全集那條線把 `page_number` 填成 `chunk_index + 1`（見 `uchimura_auto.py`），也就是
**一個看起來像頁碼、其實是流水號的欄位**——比沒有更糟，因為它會讓人照著引。
圖書館那條線（PDF 解析）則保留真頁碼（[[feedback_pdf_page_number]]）。

判準（純函式，測試鎖在 scripts/tests/test_audit_page_numbers.py）：

  serial  page_number 幾乎逐一遞增且等於 index+1  → **假頁碼，不可引用**
  real    有跳號或重複（同一頁多個 chunk）        → 真頁碼
  none    全部 None                              → 沒有頁碼（電子底本／HTML 來源）
  sparse  部分有值                                → 混合，要個別看

  python -X utf8 scripts/audit_page_numbers.py            # 全掃並分類
  python -X utf8 scripts/audit_page_numbers.py --out c:/tmp/page_audit.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHUNKS = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
MAX_LINES = 30           # 前 30 條就分得出流水號與真頁碼


def classify(pages: list) -> str:
    """[page_number...]（依 chunk 順序）→ serial / real / none / sparse / empty。"""
    if not pages:
        return "empty"
    vals = [p for p in pages if isinstance(p, int)]
    if not vals:
        return "none"
    if len(vals) < len(pages):
        return "sparse"
    serial_hits = sum(1 for i, p in enumerate(vals) if p == i + 1)
    if serial_hits >= max(3, int(len(vals) * 0.95)):
        return "serial"
    return "real"


def scan_file(path: Path, max_lines: int = MAX_LINES, max_bytes: int = 262_144) -> tuple[str, int]:
    """只讀檔頭若干位元組。

    🚨 讀整檔在 Drive 上不可行：_chunks 有四千多個檔、單檔可達數 MB，Google Drive
    File Stream 會把整個檔從雲端拉下來，全掃要跑好幾小時。前 30 條 chunk 就足以
    分辨流水號與真頁碼，所以限位元組讀取，最後一行不完整就丟掉。"""
    with path.open("rb") as fh:
        buf = fh.read(max_bytes)
    text = buf.decode("utf-8", "ignore")
    lines = text.split(chr(10))
    if len(text) >= max_bytes:
        lines = lines[:-1]          # 最後一行可能被切斷
    pages = []
    for line in lines[:max_lines]:
        if not line.strip():
            continue
        try:
            pages.append(json.loads(line).get("page_number"))
        except Exception:
            pages.append(None)
    return classify(pages), len(pages)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--root", default=str(CHUNKS))
    args = ap.parse_args()
    root = Path(args.root)
    files = sorted(root.glob("*.jsonl"))
    print(f"掃描 {len(files):,} 個 JSONL …", flush=True)
    result = {}
    tally = Counter()
    for i, f in enumerate(files, 1):
        try:
            kind, n = scan_file(f)
        except Exception as e:
            kind, n = f"error:{type(e).__name__}", 0
        result[f.stem] = kind
        tally[kind] += 1
        if i % 500 == 0:
            print(f"  {i}/{len(files)}", flush=True)
    print()
    for k, v in tally.most_common():
        print(f"  {k:8s} {v:5d}")
    if args.out:
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print("已寫", args.out)


if __name__ == "__main__":
    main()
