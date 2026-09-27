#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""批次重新標準化目錄有問題的 EPUB（2026-09-27）。

對象：output/toc_audit/toc_audit.tsv 裡 type=epub 且帶 GIANT_CHUNK／NO_TOC／PRINTED_TOC_MISS／
SEQ_BROKEN／RUNNING_HEADER／BODY_AS_TITLE 任一旗標的書；排除全集（collection=collected-works）與
已有原文欄／譯文的書（重建會蓋掉譯文）。

每本先用新版 standardize() 乾跑，同時滿足才寫入（JSONL＋R2＋DB，留 .jsonl.bak_toc）：
  1. 新版字數 ≥ 舊版 95%（不能掉內容）
  2. 章名數變多且最大塊不超過舊版 1.5 倍，或最大塊縮小一半以上且章名數不減
其餘寫進報告不動。
  python -X utf8 scripts/restandardize_epub_toc.py [--apply] [--limit N]
"""
from __future__ import annotations

import json
import shutil
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import standardize_ebook as se  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CH = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")
FLAGS = {"GIANT_CHUNK", "NO_TOC", "PRINTED_TOC_MISS", "SEQ_BROKEN", "RUNNING_HEADER", "BODY_AS_TITLE"}


def metrics(chunks):
    return (sum(len(c.get("content") or "") for c in chunks),
            len({c.get("chapter_path") for c in chunks if c.get("chapter_path")}),
            max((len(c.get("content") or "") for c in chunks), default=0))


def main() -> int:
    apply = "--apply" in sys.argv
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    rows = [l.rstrip("\n").split("\t") for l in (ROOT / "output/toc_audit/toc_audit.tsv").open(encoding="utf-8")][1:]
    cands = [r for r in rows if r[2] == "epub" and r[3] != "collected-works" and FLAGS & set(r[-1].split(","))]
    if limit:
        cands = cands[:limit]
    rep = open(ROOT / "output/toc_audit/restandardize_report.tsv", "w", encoding="utf-8")
    rep.write("id\ttitle\tresult\told_chars\tnew_chars\told_titles\tnew_titles\told_max\tnew_max\n")
    stat = {}
    for n, r in enumerate(cands):
        bid = r[0]
        p = CH / f"{bid}.jsonl"
        try:
            old = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        except Exception:  # noqa: BLE001
            continue
        if any("source_text" in c or "sources" in c for c in old):
            res, nm = "skip-has-translation", (0, 0, 0)
        elif se.book_is_japanese(c.get("content") or "" for c in old):
            res, nm = "skip-japanese", (0, 0, 0)   # 保守：日文書一律不重建
        else:
            try:
                book = se.fetch_book(bid)
                import contextlib, io
                with contextlib.redirect_stdout(io.StringIO()):
                    new = se.standardize(book)
            except BaseException as e:  # noqa: BLE001  standardize 用 SystemExit 報錯
                res, new = f"error {type(e).__name__}: {str(e)[:60]}", None
            if new:
                om, nm = metrics(old), metrics(new)
                if nm[0] < 0.95 * om[0]:
                    res = "skip-content-shrank"
                elif ((nm[1] > om[1] and nm[2] <= 1.5 * max(om[2], 1))
                      or (nm[2] < 0.5 * om[2] and nm[1] >= om[1])):
                    # 2026-09-27 試跑：劍橋中國史章名 81→455 但最大塊 1.8 萬→16 萬字，不可只看章名數
                    res = "apply" if apply else "would-apply"
                    if apply:
                        bak = p.with_suffix(".jsonl.bak_toc")
                        if not bak.exists():
                            shutil.copy2(p, bak)
                        out = se.write_jsonl(bid, new)
                        se.push_to_r2(bid, out)
                        se.update_db(bid, new)
                else:
                    res = "no-improvement"
            else:
                nm = (0, 0, 0)
        om = metrics(old)
        stat[res.split(" ")[0]] = stat.get(res.split(" ")[0], 0) + 1
        rep.write(f"{bid}\t{r[1]}\t{res}\t{om[0]}\t{nm[0]}\t{om[1]}\t{nm[1]}\t{om[2]}\t{nm[2]}\n")
        rep.flush()
        if n % 25 == 0:
            print(n, len(cands), stat, flush=True)
    print("SUMMARY", stat, flush=True)
    print("RESTD_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
