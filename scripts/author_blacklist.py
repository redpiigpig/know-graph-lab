#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""作者黑名單 —— 「這個人的東西不值得讀」的單一事實來源。

名單在 data/author-blacklist.json，三個消費端：
  * zlib_wanted.py       產每日獵書清單時濾掉（最省事，根本不去搜）
  * zlib_fetch.mjs       搜尋結果挑版本時排除（清單以外的漏網之魚）
  * ingest_new_books.py  drop 夾把關（隔離到 _blacklisted/，不進 Drive 不入庫）

比對前把兩邊都正規化：去空白／全形轉半形／簡轉繁，然後看黑名單的名字有沒有出現在
「作者欄」或「整個檔名／書目字串」裡。中文人名夠獨特，子字串比對不會誤傷；西文作者
請把 "Last, First"／"First Last" 兩種寫法都放進 aka。

  python scripts/author_blacklist.py            # 列出名單
  python scripts/author_blacklist.py 孫中興 …    # 測比對
"""
from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

BLACKLIST_FILE = Path(__file__).resolve().parents[1] / "data" / "author-blacklist.json"


def _norm(s: str) -> str:
    """去空白、全形→半形、簡→繁、轉小寫。比對用，不回寫任何地方。"""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    try:
        from parse_drive_inventory import to_traditional

        s = to_traditional(s)
    except Exception:
        pass  # 沒有 opencc 也要能比對，只是簡體寫法會漏
    return "".join(s.split()).lower()


def load() -> list[dict]:
    if not BLACKLIST_FILE.exists():
        return []
    data = json.loads(BLACKLIST_FILE.read_text(encoding="utf-8"))
    return data.get("authors", [])


def match(*fields: str) -> dict | None:
    """任一欄位命中黑名單就回那筆 entry，否則 None。

    fields 通常是 (作者, 書名, 檔名) —— 作者欄常常被檔名格式弄丟，所以多給幾個。
    """
    hay = _norm(" | ".join(f for f in fields if f))
    if not hay:
        return None
    for entry in load():
        for name in [entry["name"], *entry.get("aka", [])]:
            n = _norm(name)
            if n and n in hay:
                return entry
    return None


def main() -> int:
    entries = load()
    if len(sys.argv) > 1:
        hit = match(*sys.argv[1:])
        if hit:
            print(f"命中黑名單：{hit['name']} — {hit.get('note', '')}")
            return 1
        print("不在黑名單")
        return 0
    print(f"{BLACKLIST_FILE}（{len(entries)} 位）")
    for e in entries:
        aka = f"（{', '.join(e['aka'])}）" if e.get("aka") else ""
        print(f"  {e['name']}{aka}  {e.get('at', '')}  {e.get('note', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
