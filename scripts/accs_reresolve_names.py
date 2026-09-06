#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 accs_commentary 裡還是英文的署名與作品名重新過一次解析器。

為什麼要有這支：署名與作品名的解析結果會被兩件事推翻，而兩件事都會定期發生——

  1. **重跑 OCR**。accs_reocr_dirty_pages 會用 raw 覆蓋整卷，先前在資料庫上做的
     人工改正（例如把 rom 的 "JesusChrist" 清成 null）會一併被寫回去。既有的三支
     冪等修正腳本只處理它們各自的對照表，涵蓋不到解析器這一層。
  2. **詞庫與對照表變更**。補了教父、補了作品名、加了推導規則之後，先前判為
     unresolved 而留著英文的列並不會自己更新。

所以這支就是「拿現在的詞庫與規則，把還是英文的那些重跑一遍」。冪等，可以在
任何一次 OCR 重跑或詞庫更新之後直接再跑。

🚨 解析不出來的一律保持原樣（留英文），不臆造。這條規則在 resolve_work 的
   docstring 裡有說明：臆造書名比留英文糟。

  python scripts/accs_reresolve_names.py            # 只看會改什麼
  python scripts/accs_reresolve_names.py --apply
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests

from accs_ingest_epub import DELIBERATELY_UNRESOLVED, build_name_map, resolve_father, resolve_work
from ingest_new_books import URL, SB_HEADERS

BACKUP_DIR = Path("c:/tmp/accs_rows_backup")

# 不是教父，是經文人物或 OCR 雜訊。署名欄出現這些一律清空——把經文人物當成
# 註釋作者，比留白更誤導讀者。
NOT_FATHERS = {"JesusChrist", "Jesus Christ", "Abraham", "ESOO", "VERVIEW"}

_LATIN_START = re.compile(r"^[A-Za-z]")


def fetch_rows() -> list[dict]:
    rows, off = [], 0
    while True:
        r = requests.get(f"{URL}/rest/v1/accs_commentary"
                         f"?select=id,book_code,chapter,verse_start,father_name,father_name_en,work_title"
                         f"&offset={off}&limit=1000", headers=SB_HEADERS, timeout=90)
        r.raise_for_status()
        b = r.json()
        rows += b
        if len(b) < 1000:
            break
        off += 1000
    return rows


def plan(rows: list[dict], exact: dict[str, str]) -> list[dict]:
    """回傳要改的列。只碰「現在還是英文開頭」的欄位，中文的一律不動。"""
    out = []
    for x in rows:
        patch = {}
        f = (x.get("father_name") or "").strip()
        if f and _LATIN_START.match(f):
            if f in NOT_FATHERS:
                patch["father_name"] = None
            elif f not in DELIBERATELY_UNRESOLVED:
                zh, how = resolve_father(f, exact)
                if how != "unresolved" and zh and zh != f:
                    patch["father_name"] = zh
                    patch["father_name_en"] = x.get("father_name_en") or f
        w = (x.get("work_title") or "").strip()
        if w and _LATIN_START.match(w):
            zh, how = resolve_work(w)
            if how != "unresolved" and zh and zh != w:
                patch["work_title"] = zh
        if patch:
            out.append({**x, "_patch": patch})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    rows = fetch_rows()
    exact = build_name_map()
    todo = plan(rows, exact)
    print(f"全庫 {len(rows):,} 列 → 可重新解析 {len(todo)} 列")

    kinds = Counter()
    for t in todo:
        for k in t["_patch"]:
            kinds[k] += 1
    print("  " + "  ".join(f"{k} {v}" for k, v in kinds.most_common()))

    print("\n樣本：")
    for t in todo[:8]:
        p = t["_patch"]
        bits = [f"{k}: {t.get(k)!r} → {v!r}" for k, v in p.items()]
        print(f"  {t['book_code']} {t['chapter']}:{t['verse_start']}  " + " ｜ ".join(bits))

    still = Counter()
    for x in rows:
        for col in ("father_name", "work_title"):
            v = (x.get(col) or "").strip()
            if v and _LATIN_START.match(v) and not any(t["id"] == x["id"] and col in t["_patch"] for t in todo):
                still[f"{col}:{v[:40]}"] += 1
    if still:
        print(f"\n仍解析不出、維持英文的 {sum(still.values())} 列 / {len(still)} 種（前 10）：")
        for k, v in still.most_common(10):
            print(f"  {v:>3}  {k}")

    if not a.apply:
        print("\n（dry-run；要寫入請加 --apply）")
        return 0

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    f = BACKUP_DIR / f"reresolve_{datetime.datetime.now():%Y%m%d_%H%M%S}.jsonl"
    f.write_text("\n".join(json.dumps({k: v for k, v in t.items() if k != "_patch"},
                                      ensure_ascii=False) for t in todo), encoding="utf-8")
    print(f"\n備份原值 → {f.name}")

    ok = 0
    for t in todo:
        r = requests.patch(f"{URL}/rest/v1/accs_commentary?id=eq.{t['id']}",
                           headers={**SB_HEADERS, "Prefer": "return=minimal"},
                           json=t["_patch"], timeout=30)
        ok += r.ok
    print(f"已更新 {ok}/{len(todo)} 列")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
