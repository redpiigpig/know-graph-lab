#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""依 accs_volume_config.json 逐卷 OCR（呼叫 ingest_accs_genesis.py）。

預設只跑 status=ready（單書卷）；NT 優先。多書卷（needs_boundaries）待定界後另跑。
  python -X utf8 scripts/accs_ocr_run.py --engine gemini --batch 4 [--testament NT] [--only mat]
每卷 --resume。

額度政策＝**兩次連續失敗才退**（使用者定調）：單卷退出非 0 先跳過換下一卷，連續兩卷都
失敗才視為 provider 整體乾掉、停整批交給外層 runner 重探。2026-08-17 前是「一卷失敗就停
整批」，結果約翰福音額度乾之後，排在它後面的希伯來書／以賽亞書等於永遠排不到（DB 0 筆）。
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
    consecutive_fails = 0
    skipped: list[str] = []
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
            if rc == 0:
                consecutive_fails = 0
                continue
            consecutive_fails += 1
            skipped.append(book)
            if consecutive_fails >= 2:
                print(f"  [bail] {book} 退出碼 {rc}；連續 2 卷失敗＝provider 整體乾掉"
                      f" → 停整批，待重探續傳（本批已跳過：{', '.join(skipped)}）", flush=True)
                return 1
            print(f"  [skip] {book} 退出碼 {rc}（多半額度乾）→ 換下一卷，"
                  f"本卷 checkpoint 保留待續傳", flush=True)
    if skipped:
        print(f"\n本批跑完，跳過 {len(skipped)} 卷待續傳：{', '.join(skipped)}", flush=True)
        return 0
    print("\n本批 OCR 全數完成或無可跑項", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
