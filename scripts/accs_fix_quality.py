#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修 accs_audit_quality 抓出來的兩個**使用者看得到**的問題。

A 卷名顯示成書卷代碼（15,646 列 / 53 卷）
  `source_vol` 直接印在讀經頁上（scripture/[book]/[chapter].vue 第 95 行），
  所以這些列現在顯示成「ACCS（gen）‧古代基督信仰聖經註釋叢書」而不是「ACCS（創世記）」。
  同一個欄位有三種寫法（中文名／代碼／次經），統一成中文書名。

B 索引頁被當成註釋收進來（250 列 / 5 卷）
  書末的主題索引、作者索引、經文索引被 ingest 當成正文，掛在該卷最後一章底下，
  `father_name` 存的是索引詞（「餅、糧」「麥基洗德是閃的說法」「使徒信經」），
  `body_zh` 整段是頁碼（「9-10, 31-32, 115」）。頁面上就是一堆數字。
  判準＝去空白後數字與頁碼標點佔比 > 60%，且長度 ≥ 12。

刪除前一律先把整列匯出到 --backup（預設 c:/tmp/accs_index_rows_backup.json）。

  python -X utf8 scripts/accs_fix_quality.py            # dry-run，只報數
  python -X utf8 scripts/accs_fix_quality.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# ── 純函式（scripts/tests/test_accs_fix_quality.py 鎖定）──────────────────

_PAGEREF_CHARS = set(",-–—. ivxlcIVXLC")


def index_row_score(body: str) -> float:
    """整段裡「頁碼與其標點」的佔比。索引列會很高（多半 > 0.8）。

    正文再怎麼引經據典也不會通篇只有數字，所以這個判準對正文幾乎不會誤傷；
    但**太短的段落**（「9-10」也可能是正常的節號註記）要另外用長度擋掉。
    """
    core = re.sub(r"\s", "", body or "")
    if not core:
        return 0.0
    return sum(1 for c in core if c.isdigit() or c in _PAGEREF_CHARS) / len(core)


_PAGE_TOKEN_RE = re.compile(r"^[0-9ivxlcIVXLC]+(-[0-9ivxlcIVXLC]+)?$")
_SENT_END = "。！？；"


def is_term_index_row(body: str, max_len: int = 60) -> bool:
    """中文索引詞型：`誇張, xxii`、`使徒保羅, 1-12`、`教會是混合的群體，xxiii, 129`。

    🚨 第一版只看「數字佔比 > 60%」，這一類因為前面掛著中文索引詞而佔比不足，
    **883 筆全部漏抓**（rev 377、rom 282、heb 220、isa 4）。
    判準改成結構：逗號切開後，**第一段之後的欄位幾乎都是純頁碼**，而且整段
    沒有句末標點——正文再短也會有句號。
    """
    t = (body or "").strip()
    if not t or len(t) > max_len:
        return False
    if any(p in t for p in _SENT_END):
        return False
    parts = [p.strip() for p in re.split(r"[,，]", t) if p.strip()]
    if len(parts) < 2:
        return False
    tail = parts[1:]
    return sum(1 for p in tail if _PAGE_TOKEN_RE.match(p)) / len(tail) >= 0.8


def is_index_row(body: str, min_len: int = 12, threshold: float = 0.6) -> bool:
    """這一列是不是書末索引被當成註釋收進來的？兩種型態都算。"""
    core = re.sub(r"\s", "", body or "")
    if len(core) >= min_len and index_row_score(body) > threshold:
        return True
    return is_term_index_row(body)


def normalize_source_vol(source_vol: str, book_zh: str) -> str | None:
    """`ACCS（gen）` → `ACCS（創世記）`。已經是中文名或次經卷名就回 None（不用改）。

    只動「整個括號內容都是英數代碼」的那種，才不會把
    「ACCS（耶利米書‧耶利米哀歌）」這種合卷名誤改。
    """
    sv = (source_vol or "").strip()
    if not sv or not book_zh:
        return None
    if not re.match(r"^ACCS（[A-Za-z0-9]{2,4}）$", sv):
        return None
    return f"ACCS（{book_zh}）"


# ── I/O ────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup", default="c:/tmp/accs_index_rows_backup.json")
    a = ap.parse_args()

    from accs_audit_quality import _env
    from audit_page_numbers_db import run_sql

    env = _env()
    books = {b["code"]: b["name_zh"] for b in run_sql(env, "select code, name_zh from bible_books")}

    rows = []
    last = ""
    while True:
        batch = run_sql(env, ("select id::text, book_code, chapter, father_name, body_zh, source_vol "
                              f"from accs_commentary where id::text > '{last}' order by id::text limit 2000"))
        if not batch:
            break
        rows += batch
        last = batch[-1]["id"]
    print(f"讀入 {len(rows)} 列", flush=True)

    drop = [r for r in rows if is_index_row(r["body_zh"] or "")]
    fix = [(r["id"], normalize_source_vol(r["source_vol"] or "", books.get(r["book_code"], "")))
           for r in rows]
    fix = [(i, v) for i, v in fix if v]

    import collections
    print(f"\nA 卷名要正規化：{len(fix)} 列")
    print(f"B 索引垃圾要刪：{len(drop)} 列 → "
          f"{dict(collections.Counter(r['book_code'] for r in drop))}")
    for r in drop[:3]:
        print(f"    {r['book_code']} {r['chapter']} father={r['father_name']!r} :: {(r['body_zh'] or '')[:50]}")

    if not a.apply:
        print("\n（dry-run，加 --apply 才會動資料）")
        return 0

    Path(a.backup).parent.mkdir(parents=True, exist_ok=True)
    Path(a.backup).write_text(json.dumps(drop, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n✅ 已備份 {len(drop)} 列 → {a.backup}")

    # A：同一個 source_vol 舊值一次更新，比逐列 update 少幾千次往返
    pairs: dict[tuple[str, str], list[str]] = {}
    for i, v in fix:
        pairs.setdefault(v, []).append(i)
    for new_vol, ids in pairs.items():
        for k in range(0, len(ids), 500):
            chunk = "','".join(ids[k:k + 500])
            run_sql(env, f"update accs_commentary set source_vol = '{new_vol}' "
                         f"where id::text in ('{chunk}')")
    print(f"✅ 卷名已正規化 {len(fix)} 列")

    ids = [r["id"] for r in drop]
    for k in range(0, len(ids), 500):
        chunk = "','".join(ids[k:k + 500])
        run_sql(env, f"delete from accs_commentary where id::text in ('{chunk}')")
    print(f"✅ 已刪除 {len(ids)} 列索引垃圾")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
