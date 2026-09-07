# -*- coding: utf-8 -*-
"""兩次獨立 OCR 的分歧點 —— 精修時該看哪裡。

逐字精修最花時間的不是改，是**找**：一頁上千字，錯的可能只有五個，
而且每一個單獨看都很通順（OCR 錯字幾乎都是形近字，讀起來不彆扭）。

跑兩次獨立 OCR 再比對，可以把「要看圖裁定的地方」從整本縮到分歧處。
兩次都對的地方通常真的對；兩次不一樣的地方一定有一次是錯的。
（兩次犯同一個錯的仍會漏掉 —— 這個方法縮小範圍，不保證窮盡。）

    python scripts/ndl_ocr_diff.py 1099766 --a gemini --b gemini2

見 .claude/skills/ebook-collected-works/ndl_open_scans.md 的「逐字精修」一節。
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import ndl_build as nb  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def diff_spans(a: str, b: str, ctx: int = 12) -> list:
    """兩份文字的不同處 → [(a 片段, b 片段, a 的前後文)]。"""
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        out.append((a[i1:i2], b[j1:j2],
                    a[max(0, i1 - ctx):i1] + "〔" + a[i1:i2] + "〕" + a[i2:i2 + ctx]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pid")
    ap.add_argument("--a", default="gemini")
    ap.add_argument("--b", default="gemini2")
    ap.add_argument("--img", type=int, default=None, help="只看某一張影像")
    args = ap.parse_args()

    da = nb.CACHE_DIR / args.pid / ("ocr-" + args.a)
    db = nb.CACHE_DIR / args.pid / ("ocr-" + args.b)
    total = 0
    for fa in sorted(da.glob("*.txt")):
        img = int(fa.stem)
        if args.img and img != args.img:
            continue
        fb = db / fa.name
        if not fb.exists():
            print("影像 %d：%s 沒有對應檔" % (img, args.b))
            continue
        a, b = fa.read_text(encoding="utf-8"), fb.read_text(encoding="utf-8")
        spans = diff_spans(a, b)
        if not spans:
            continue
        print("\n===== 影像 %d（%d 處分歧）" % (img, len(spans)))
        for x, y, ctx in spans:
            total += 1
            print("  A:%-14s B:%-14s | %s" % (repr(x)[1:-1][:14], repr(y)[1:-1][:14], ctx))
    print("\n合計 %d 處分歧 —— 這些要看圖裁定" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
