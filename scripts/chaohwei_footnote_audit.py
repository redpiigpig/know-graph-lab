#!/usr/bin/env python
"""《初期唯識思想》註號稽核 —— 找出 OCR 把註號讀壞的頁。

    python scripts/chaohwei_footnote_audit.py            # 稽核，印分母
    python scripts/chaohwei_footnote_audit.py --worklist # 只印要重跑的掃描頁

本書的註號**每章從 1 重編**（實證：肆章 p122＝6、p128＝10；柒章 p201＝1,2、
p233＝27,28；捌章 p250＝1,2、p269＝23,24,25。若是全書連號，p122 不可能只到 6）。

🚨 壞法不是「兩位數被截成一位」，而是兩種更麻煩的：

1. **註文內部的引文列舉被當成註號。**p174 正文的上標其實是 13，而註 13 的內容
   是「1. 玄奘…／2. 遺教東流…」兩段引文；OCR 把 1. 2. 當成註號，還把**一條註
   拆成兩條**。p186 同樣（正文上標是 5、6，註文裡印的 1. 2. 是引文編號）。
2. 真正的誤讀（p47 的 17 讀成 1 之類）。

所以不能只是「重新排序號」—— 假的註也會被編進去。要先把每一章真正的註數弄對，
才談得上重編。本工具只負責把可疑的頁找出來，交給 chaohwei_ocr.py 用加強過的
prompt 重跑到 ocr2/（load_cache 前面的快取優先，舊的只補沒跑到的頁）。
"""

import argparse
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import chaohwei_build as cb            # noqa: E402
import chaohwei_vijnapti_build as vb   # noqa: E402

DEF = re.compile(r"\[\^(\d+|續|\?)\]:")
MARK = re.compile(r"(?<!:)\[\^(\d+|\?)\](?!:)")
# 註文開頭若緊接著「1.」「2.」這類列舉號，多半是註內引文編號被當成了註號
INNER_ENUM = re.compile(r"^\[\^\d+\]:\s*\d+[.、]\s")


def pages_in_order():
    recs = [r for r in cb.load_cache([Path(c) for c in vb.CACHE], Path(vb.WORK))
            if r["work_page"] not in vb.SKIP_WP]
    recs = vb.prefix_front_matter(cb.prepare_records(recs))
    titles = [c["title"] for c in vb.CHAPTERS]
    rep = cb.audit_pages(recs, titles)
    keep = {r["work_page"] for r in recs} & set(rep["keep"]) if rep.get("keep") else None
    by_wp = {r["work_page"]: r for r in recs}
    pages = cb.tag_chapters(cb.pages_for_stitch(recs, rep["keep"], titles), vb.CHAPTERS)
    # pages_for_stitch 丟掉了 work_page，靠 printed 對回去
    wp_of = {}
    for wp, r in by_wp.items():
        wp_of.setdefault(r.get("printed"), wp)
    for pg in pages:
        pg["work_page"] = wp_of.get(pg.get("printed"))
    return pages, titles


def scan():
    pages, titles = pages_in_order()
    per_chapter: dict[int, list] = {}
    for pg in pages:
        txt = "\n".join(pg.get("paras") or [])
        defs = [m.group(1) for m in DEF.finditer(txt)]
        marks = [m.group(1) for m in MARK.finditer(txt)]
        inner = [ln for ln in txt.split("\n") if INNER_ENUM.match(ln)]
        if defs or marks:
            per_chapter.setdefault(pg.get("chapter", -1), []).append({
                "printed": pg.get("printed"), "work_page": pg.get("work_page"),
                "defs": defs, "marks": marks, "inner_enum": len(inner),
            })
    return per_chapter, titles


def judge(rows):
    """回傳 (問題清單, 期待的下一個號)。每章應為 1,2,3… 嚴格遞增、不跳不重。"""
    problems, expect = [], 1
    for r in rows:
        nums = [int(d) for d in r["defs"] if d.isdigit()]
        for n in nums:
            if n != expect:
                problems.append((r, n, expect))
            expect = max(expect, n) + 1
        if r["inner_enum"]:
            problems.append((r, "註內列舉被當註號", expect))
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worklist", action="store_true", help="只印要重跑的掃描頁範圍")
    a = ap.parse_args()

    per_chapter, titles = scan()
    bad_pages: set[int] = set()
    total_defs = total_bad = 0

    for ch in sorted(per_chapter):
        rows = per_chapter[ch]
        name = titles[ch] if 0 <= ch < len(titles) else f"（章 {ch}）"
        problems = judge(rows)
        n_defs = sum(len(r["defs"]) for r in rows)
        total_defs += n_defs
        total_bad += len(problems)
        for r, got, exp in problems:
            if r["work_page"]:
                bad_pages.add(r["work_page"])
        if not a.worklist:
            print(f"\n── {name}　有註的頁 {len(rows)}／註釋定義 {n_defs}／可疑 {len(problems)}")
            for r, got, exp in problems[:8]:
                print(f"    p{r['printed']:>6}（掃描頁 {r['work_page']}）：讀到 {got}，"
                      f"依序應為 {exp}")
            if len(problems) > 8:
                print(f"    …另有 {len(problems) - 8} 筆")

    if a.worklist:
        for wp in sorted(bad_pages):
            print(wp)
        return

    print(f"\n{'=' * 52}")
    print(f"註釋定義合計 {total_defs}　可疑 {total_bad}　"
          f"要重跑的掃描頁 {len(bad_pages)}")
    print("重跑：python scripts/chaohwei_ocr.py --work c:/tmp/chaohwei_vijnapti/work.pdf \\")
    print("        --cache c:/tmp/chaohwei_vijnapti/ocr2 --pages <範圍> --resume")


if __name__ == "__main__":
    main()
