# -*- coding: utf-8 -*-
"""把重 OCR 切好的《基督教典外文獻・新約篇》四冊寫回 /apocrypha。

    python scripts/ingest_cct_apocrypha.py --dry-run
    python scripts/ingest_cct_apocrypha.py --write
    python scripts/ingest_cct_apocrypha.py --dry-run --only gnazarenes

上游是 `apocrypha_extract_works.py`（目錄定界 → 書眉對帳 → 切節）。本檔只做
「對應到 doc_slug、整理成列、蓋掉舊的」這一段。

三個已定案的作法（2026-09-19 使用者裁示）：
  ① **雙欄抄本**：單一版本＋行內標籤。右欄以書上原本的欄標為前綴，附在該節後面，
     不另開 version_code（異文只有四頁，開第二個版本會逼得整部正文複製一份）。
  ② **註腳**：`footnote_defs` 存成 {標記: 定義}，並把正文裡對應的數字轉成上標，
     reader 才連得起來。連不上的照樣寫進去（reader 已改成一併列出）。
  ③ **粒度**：照重 OCR 的結果收，即使比舊資料粗。舊的節數多半是壞掉的 chunk
     假數字（`acts-paul` 宣稱 272 節，其中大半根本不是保羅行傳）。

🚨 只動 `version_code = 'cct_zh'` 這一組列，別的版本（英譯等）不碰。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

from apocrypha_audit_quality import env, fetch_all  # noqa: E402
from apocrypha_extract_works import (fill_printed, load_pages, markers_of,  # noqa: E402
                                     peel_columns, slice_work, split_front,
                                     two_column_pages)
from apocrypha_footnotes import link_page, page_footnotes  # noqa: E402
from apocrypha_missing_numbers import for_work  # noqa: E402
from apocrypha_sectionize import choose  # noqa: E402
from apocrypha_toc import load as load_toc  # noqa: E402

VERSION = "cct_zh"

# doc_slug → (冊, 部分, 卷)。**手動核過**的對照表。
# 🚨 不要用書名模糊比對自動配：DB 與書上的用字常差一個字（索菲**亞**／索菲**婭**、
#    安**得**烈／安**德**烈、革老**丟**／革老**丢**、以賽亞**昇**／**升**天記），
#    而且《皮斯特斯·索菲婭》在第一冊與第二冊各出現一次（v1 只有三頁的節錄、
#    v2 才是正文十二頁）。配錯的後果是整部內容掛到別人的 slug 底下。
MAPPING: dict[str, tuple[int, int | None, int]] = {
    # ── 本輪要修的壞檔（品質閘點名的那些）──
    "gnazarenes": (1, 1, 3),            # 拿撒勒派人福音
    "gebionites": (1, 1, 4),            # 伊便尼派人福音
    "gmatthias": (1, 1, 6),             # 馬提亞福音（舊資料把它與託馬太名福音混在一起）
    "protoevangelium-james": (1, 2, 1),  # 雅各原始福音
    "infancy-thomas": (1, 2, 2),        # 多馬的耶穌嬰孩時期福音
    "joseph-carpenter": (1, 2, 9),      # 木匠約瑟的歷史
    "gthom": (1, 3, 2),                 # 多馬福音（114 則語錄）
    "gpet": (1, 3, 5),                  # 彼得福音
    "q-mani": (2, 1, 18),               # 摩尼福音
    "pistis-sophia": (2, 1, 2),         # 皮斯特斯·索菲婭 ← 取第二冊的正文，不是第一冊的節錄
    "joseph-arimathea": (2, 3, 8),      # 亞利馬太約瑟的記述
    "acts-paul": (3, 1, 1),          # 保羅行傳
    "acts-john": (3, 1, 3),          # 約翰行傳
    "acts-thomas": (3, 1, 5),        # 多馬行傳
}

# 這幾份在新約篇四冊裡**沒有**對應的卷，本輪不動，理由記在這裡免得下次再找一遍。
NOT_IN_NT_SET = {
    "3-cor": "《哥林多三書》不是獨立一卷，它是《保羅行傳》的一部分（v3 卷1 之內）",
    "acts-philip": "《腓力行傳》四冊目錄皆無，來源另有出處",
    "cct-gospels-unsplit": "暫存桶，不是作品；等各卷都重收完再決定要不要刪",
    "joseph-aseneth": "屬舊約篇",
    "4-ezra": "屬舊約篇",
}

# 專名統一：站上其他地方一律用「公義者雅各」（6 處，無一處用裸「義者雅各」），
# 這批新進的文字要跟著一致。使用者定名為最高原則。
TERM_FIXES = [(re.compile(r"(?<!公)義者雅各"), "公義者雅各")]


def fix_terms(s: str) -> str:
    for pat, rep in TERM_FIXES:
        s = pat.sub(rep, s)
    return s


def build_doc(slug: str, vol: int, part: int | None, juan: int) -> dict:
    """切好一部作品 → 準備寫進 DB 的列。"""
    items, _junk, _ = load_toc(f"cct-nt-{vol}")
    pages, _gaps = load_pages(f"cct-nt-{vol}")
    fill_printed(pages)
    printed_hi = max((p["printed"] for p in pages if p["printed"]), default=0)

    idx = next((i for i, it in enumerate(items)
                if it["kind"] == "work" and it["part"] == part and it["juan"] == juan), None)
    if idx is None:
        raise SystemExit(f"{slug}: cct-nt-{vol} 目錄裡找不到 第{part}部分 卷{juan}")
    it = items[idx]
    lo = it["printed"]
    hi = (items[idx + 1]["printed"] - 1) if idx + 1 < len(items) else printed_hi
    wp = slice_work(pages, lo, hi)
    if not wp:
        raise SystemExit(f"{slug}: 印刷頁 {lo}–{hi} 一頁都沒抓到")

    markers = {p["printed"]: markers_of(p) for p in wp}
    intro, body, _name, seen_text = split_front(wp)
    sp, note = choose(body, markers, first=1, missing=for_work(it["title"]))
    if sp is None:
        raise SystemExit(f"{slug}: 切不出節 —— {note}")

    secondary, twocol = peel_columns(wp)

    # 🚨 卷首沒有「文本」小標時（《多馬福音》那個小標排在表格裡，認不出來），
    #    split_front 會退回「整卷都是正文」，於是**主編的簡介變成第一節**。
    #    那一段其實是 intro_zh，不是文獻本身；這裡把它移回去。
    if not seen_text and not intro and sp.prologue:
        intro = [x["text"] for x in sp.prologue]
        sp.prologue.clear()

    rows: list[dict] = []
    if sp.prologue:
        text = fix_terms("\n".join(x["text"] for x in sp.prologue).strip())
        rows.append({"doc_slug": slug, "version_code": VERSION, "order_index": 0,
                     "section_label": "序", "section_label_clean": "序",
                     "chapter": None, "verse": None,
                     "page_number": sp.prologue[0]["page"],
                     "text": text, "char_count": len(text), "footnote_defs": None})
    for i, s in enumerate(sp.sections, start=len(rows)):
        text = fix_terms("\n".join(x for x in s.paras if x).strip())
        rows.append({"doc_slug": slug, "version_code": VERSION, "order_index": i,
                     "section_label": s.label, "section_label_clean": s.label,
                     "chapter": s.chapter, "verse": s.verse,
                     "page_number": s.page, "text": text,
                     "char_count": len(text), "footnote_defs": None})

    # ── 雙欄的右欄：附在該頁的第一節後面，冠上書上的欄標 ──
    appended = 0
    for (printed, _blk), pieces in sorted(secondary.items()):
        host = next((r for r in rows if r["page_number"] == printed), None)
        if host is None:
            continue
        chunks = []
        last = None
        for label, txt in pieces:
            if label and label != last:
                chunks.append(f"〔{label}〕{txt}")
                last = label
            else:
                chunks.append(txt)
        add = fix_terms("\n".join(chunks).strip())
        host["text"] = (host["text"] + "\n" + add).strip()
        host["char_count"] = len(host["text"])
        appended += 1

    # ── 註腳：逐頁解析 → 正文轉上標 → 逐節掛定義 ──
    fn_total = fn_linked = 0
    for p in wp:
        if not p["notes"]:
            continue
        defs, _un = page_footnotes(p["notes"])
        if not defs:
            continue
        fn_total += len(defs)
        here = [r for r in rows if r["page_number"] == p["printed"]]
        if not here:
            continue
        texts = [r["text"] for r in here]
        new, missed = link_page(texts, sorted(defs))
        fn_linked += len(defs) - len(missed)
        for r, t in zip(here, new):
            r["text"] = t
            r["char_count"] = len(t)
        # 定義掛在「正文含該上標」的那一節；連不上的掛在該頁第一節
        for mk, d in sorted(defs.items()):
            sup = str(mk).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
            target = next((r for r in here if sup in r["text"]), here[0])
            target["footnote_defs"] = {**(target["footnote_defs"] or {}), str(mk): d}

    intro_text = fix_terms("\n\n".join(intro).strip())
    return {"slug": slug, "title": it["title"], "vol": vol, "part": part, "juan": juan,
            "printed": (lo, hi), "pages": len(wp), "rows": rows, "scheme": sp.scheme,
            "note": note, "intro": intro_text, "twocol": twocol, "appended": appended,
            "fn_total": fn_total, "fn_linked": fn_linked}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", nargs="*", help="只處理這幾個 slug")
    a = ap.parse_args()
    if not (a.write or a.dry_run):
        ap.error("要 --dry-run 或 --write")

    e = env()
    url = e["SUPABASE_URL"].rstrip("/")
    h = {"apikey": e["SUPABASE_SERVICE_ROLE_KEY"],
         "Authorization": "Bearer " + e["SUPABASE_SERVICE_ROLE_KEY"],
         "Content-Type": "application/json"}

    old = fetch_all(url, h, "apocrypha_sections",
                    {"select": "doc_slug", "version_code": f"eq.{VERSION}"})
    from collections import Counter
    before = Counter(r["doc_slug"] for r in old)

    targets = {k: v for k, v in MAPPING.items() if not a.only or k in a.only}
    built = []
    for slug, (vol, part, juan) in targets.items():
        built.append(build_doc(slug, vol, part, juan))

    print(f"{'slug':24}{'舊節':>5}{'新節':>5}  體例        印刷頁     註腳(連上/總)  雙欄")
    for b in built:
        print(f"  {b['slug']:22}{before.get(b['slug'], 0):>5}{len(b['rows']):>5}  "
              f"{b['scheme']:<10}{b['printed'][0]}-{b['printed'][1]:<7}"
              f"{b['fn_linked']}/{b['fn_total']:<12}"
              f"{('✓ ' + str(len(b['twocol'])) + ' 頁') if b['twocol'] else '—'}")
        if "沒切到" in b["note"]:
            print(f"      ⚠ {b['note'].split('　')[-1]}")

    if a.dry_run:
        print("\n（dry-run：沒有寫入）")
        return 0

    for b in built:
        r = requests.delete(f"{url}/rest/v1/apocrypha_sections", headers=h,
                            params={"doc_slug": f"eq.{b['slug']}",
                                    "version_code": f"eq.{VERSION}"}, timeout=120)
        if r.status_code >= 400:
            print(f"⛔ 刪舊列失敗 {b['slug']}：{r.status_code} {r.text[:200]}")
            return 1
        for i in range(0, len(b["rows"]), 500):
            chunk = b["rows"][i:i + 500]
            r = requests.post(f"{url}/rest/v1/apocrypha_sections", headers=h,
                              data=json.dumps(chunk, ensure_ascii=False).encode("utf-8"),
                              timeout=180)
            if r.status_code >= 400:
                print(f"⛔ 寫入失敗 {b['slug']}：{r.status_code} {r.text[:300]}")
                return 1
        if b["intro"]:
            r = requests.patch(f"{url}/rest/v1/apocrypha_documents", headers=h,
                               params={"slug": f"eq.{b['slug']}"},
                               data=json.dumps({"intro_zh": b["intro"]},
                                               ensure_ascii=False).encode("utf-8"),
                               timeout=60)
            if r.status_code >= 400:
                print(f"⛔ 寫簡介失敗 {b['slug']}：{r.status_code} {r.text[:200]}")
                return 1
        print(f"✓ {b['slug']}：{len(b['rows'])} 節、簡介 {len(b['intro'])} 字")
    return 0


if __name__ == "__main__":
    sys.exit(main())
