#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""掃描本 OCR 的「跑一輪」驅動 —— 給 fleet_keeper 當 lane 用。

跟 `scan_ocr_resume_loop.sh` 的差別是**這支不自己迴圈**：挑出第一本還沒補滿的書，
跑一輪 `scan_ocr.py --resume` 就退出，重試交給 keeper 的 30 分鐘節奏。

為什麼要這樣改：nohup 的背景迴圈**隨 session 結束就死**（實測留下一個殘留 lock，
兩本各卡在 90/255 與 162/300 整晚沒動），只有工作排程器託管的東西活得過
（[[feedback_laptop_sleeps_design_for_resume]]、[[project_fleet_keeper]]）。

兩本都補滿就直接退出並印一行——不會像壞掉的排程那樣無限空轉
（[[feedback_disable_finished_schedules]]）。

  python -X utf8 scripts/scan_ocr_pass.py            # 跑一輪
  python -X utf8 scripts/scan_ocr_pass.py --status   # 只看進度
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import scan_books  # noqa: E402


def page_total(work_pdf: str) -> int:
    """工作 PDF 的頁數＝這本書的 OCR 目標。用檔案本身當目標，不寫死數字。"""
    import fitz
    doc = fitz.open(work_pdf)
    try:
        return len(doc)
    finally:
        doc.close()


def cached(cache_dir: str) -> int:
    p = Path(cache_dir)
    return len(list(p.glob("*.json"))) if p.exists() else 0


def survey() -> list[dict]:
    """每本書的 (已 OCR / 總頁)。快取夾取設定裡的第一個（＝現用的那個）。"""
    out = []
    for slug, book in scan_books.BOOKS.items():
        work = book["work_pdf"]
        if not Path(work).exists():
            out.append({"slug": slug, "title": book["title"], "missing_pdf": True,
                        "done": 0, "total": 0})
            continue
        out.append({"slug": slug, "title": book["title"], "missing_pdf": False,
                    "done": cached(book["ocr_cache"][0]), "total": page_total(work)})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--batch", type=int, default=6)
    a = ap.parse_args()

    rows = survey()
    for r in rows:
        flag = "⚠ 找不到工作 PDF" if r["missing_pdf"] else ""
        print(f"  {r['title']}　{r['done']}/{r['total']} {flag}", flush=True)
    if a.status:
        return

    todo = [r for r in rows if not r["missing_pdf"] and r["done"] < r["total"]]
    if not todo:
        print("✅ 全部補滿，這一輪沒事可做", flush=True)
        return

    # 一次只跑一本：兩本同時跑只會互搶同一批 key 的配額，
    # 而且看起來還「兩邊都在動」，很難發現量能被對半砍。
    r = todo[0]
    print(f"→ {r['title']}（{r['done']}/{r['total']}）", flush=True)
    cmd = [sys.executable, "-u", "-X", "utf8", str(SCRIPT_DIR / "scan_ocr.py"),
           "--book", r["slug"], "--batch", str(a.batch), "--resume"]
    raise SystemExit(subprocess.call(cmd, cwd=str(SCRIPT_DIR.parent)))


if __name__ == "__main__":
    main()
