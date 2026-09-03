#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「同一個 pericope_order 底下混了好幾個經文範圍」的章重編號。

  python -X utf8 scripts/accs_fix_pericope_groups.py            # 只列出
  python -X utf8 scripts/accs_fix_pericope_groups.py --apply

為什麼要修：`/api/scripture/commentary` 按 `pericope_order` 分組，並拿**該組第一
列**的 verse_start/verse_end 當整組的經文範圍。一組裡混著兩個範圍時，後面那個範圍
的註釋就會顯示在前一個範圍底下——畫面看起來完全正常，只是掛錯節。

怎麼混進來的：`build_rows` 的 pericope_order 是**該次執行內**依範圍首次出現順序編
的。同一章分兩次跑（續傳、補頁、重 OCR）時，兩次各自從 1 編起，於是不同範圍拿到
同一個號碼。實測全表 12,683 組裡有 3 組（isa 42、isa 30、mat 14）。

修法：把受影響的**整章**依 (verse_start, verse_end) 首次出現順序重編 pericope_order。
ACCS 的段落本來就是照經文順序排的，所以重編之後顯示順序不變、分組才變對。
entry_order 不動（它的分組鍵是經文範圍，本來就對）。
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import requests
import translate_ebook_to_zh as te

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

TABLE = "accs_commentary"
BACKUP_DIR = Path("c:/tmp/accs_rows_backup")


def fetch_all() -> list[dict]:
    """分頁完整撈——PostgREST 預設只回 1000 列而且不報錯。"""
    out, off = [], 0
    while True:
        r = requests.get(f"{te.URL}/rest/v1/{TABLE}", headers=te.H_GET, timeout=120,
                         params={"select": "id,book_code,chapter,pericope_order,"
                                           "entry_order,verse_start,verse_end",
                                 "limit": "1000", "offset": str(off), "order": "id"})
        r.raise_for_status()
        b = r.json()
        out += b
        off += len(b)
        if len(b) < 1000:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--skip-books", default="",
                    help="逗號分隔的 book_code，這些書卷不動"
                         "（例：jer,lam —— 它們由 accs_ingest_epub --upload 自己重編）")
    a = ap.parse_args()
    skip = {b.strip() for b in a.skip_books.split(",") if b.strip()}

    rows = fetch_all()
    print(f"撈到 {len(rows)} 列（分頁完整撈）")

    groups: dict[tuple, set] = defaultdict(set)
    for x in rows:
        groups[(x["book_code"], x["chapter"], x["pericope_order"])].add(
            (x["verse_start"], x["verse_end"]))
    bad_chapters = sorted({k[:2] for k, v in groups.items()
                           if len(v) > 1 and k[0] not in skip})
    print(f"{len(groups)} 個 pericope 組；範圍不一致的章 {len(bad_chapters)}：{bad_chapters}")
    if not bad_chapters:
        print("沒有要修的。")
        return 0

    updates = []
    for bc, ch in bad_chapters:
        chap = sorted((x for x in rows if x["book_code"] == bc and x["chapter"] == ch),
                      key=lambda y: (y["pericope_order"], y["entry_order"]))
        order: dict[tuple, int] = {}
        for x in chap:
            k = (x["verse_start"], x["verse_end"])
            if k not in order:
                order[k] = len(order) + 1
            if x["pericope_order"] != order[k]:
                updates.append({"id": x["id"], "old": x["pericope_order"],
                                "new": order[k], "ref": f"{bc} {ch}:{k[0]}-{k[1]}"})
        print(f"  {bc} {ch}：{len(chap)} 列 → {len(order)} 組")

    print(f"\n要改 pericope_order 的 {len(updates)} 列")
    for u in updates[:10]:
        print(f"   {u['ref']}  {u['old']} → {u['new']}")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    bak = BACKUP_DIR / f"accs_pericope_renumber_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
    bak.write_text("\n".join(json.dumps(u, ensure_ascii=False) for u in updates) + "\n",
                   encoding="utf-8")
    print(f"備份對照 → {bak}（{len(updates)} 列）")

    if not a.apply:
        print("\n(dry-run；要寫入請加 --apply)")
        return 0

    for u in updates:
        r = requests.patch(f"{te.URL}/rest/v1/{TABLE}", headers=te.H_JSON, timeout=60,
                           params={"id": f"eq.{u['id']}"},
                           json={"pericope_order": u["new"]})
        if not r.ok:
            print("✗", u["ref"], r.status_code, r.text[:200])
            return 1
    print(f"已改 {len(updates)} 列")

    again = fetch_all()
    g2: dict[tuple, set] = defaultdict(set)
    for x in again:
        g2[(x["book_code"], x["chapter"], x["pericope_order"])].add(
            (x["verse_start"], x["verse_end"]))
    left = [k for k, v in g2.items() if len(v) > 1 and k[0] not in skip]
    print(f"複查：仍混著多個範圍的組 {len(left)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
