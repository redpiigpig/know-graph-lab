#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""依 accs_volume_config.json 逐卷 OCR（呼叫 ingest_accs_genesis.py）。

預設只跑 status=ready（單書卷）；NT 優先。多書卷（needs_boundaries）待定界後另跑。
  python -X utf8 scripts/accs_ocr_run.py --engine gemini --batch 4 [--testament NT] [--only mat]
每卷 --resume；某卷因額度乾退出即停整批（交由外層 runner 重探 Gemini 後續傳）。
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = ROOT / "accs_volume_config.json"

# book_code → 繁中書名（source_vol 用；對齊 bible_books.name_zh）
NAME = {
    "mat": "馬太福音", "mrk": "馬可福音", "luk": "路加福音", "jhn": "約翰福音",
    "act": "使徒行傳", "rom": "羅馬書", "heb": "希伯來書", "rev": "啟示錄",
    "job": "約伯記", "psa": "詩篇", "isa": "以賽亞書",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", default="gemini", choices=["gemini", "sonnet", "haiku"])
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--testament", choices=["NT", "OT"], help="只跑此約")
    ap.add_argument("--only", help="只跑此 book_code")
    ap.add_argument("--include-multi", action="store_true",
                    help="也跑多書卷（需已補好 ranges）")
    args = ap.parse_args()

    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    for vol in cfg:
        if not args.include_multi and vol["status"] != "ready":
            continue
        if args.testament and vol["testament"] != args.testament:
            continue
        if vol["ranges"] is None:
            print(f"  [skip] {vol['vol_key']} 尚未定界", flush=True)
            continue
        for rng in vol["ranges"]:
            book = rng["book"]
            if args.only and book != args.only:
                continue
            vol_name = NAME.get(book, book)
            src_vol = f"ACCS（{vol_name}）"
            print(f"\n=== {book}  {rng['pages']}  {os.path.basename(vol['pdf'])} ===", flush=True)
            cmd = [
                sys.executable, "-X", "utf8", str(ROOT / "ingest_accs_genesis.py"),
                "--pdf", vol["pdf"], "--book", book, "--pages", rng["pages"],
                "--source-vol", src_vol, "--engine", args.engine,
                "--batch", str(args.batch), "--resume", "--sleep", "1",
            ]
            rc = subprocess.run(cmd).returncode
            if rc != 0:
                print(f"  [bail] {book} 退出碼 {rc}（多半額度乾）→ 停整批，待重探續傳", flush=True)
                return 1
    print("\n本批 OCR 全數完成或無可跑項", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
