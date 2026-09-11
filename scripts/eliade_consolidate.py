#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把散在電子圖書館的伊利亞德各卷收攏進 全集/宗教學/伊利亞德/。

為什麼要有這支：2026-09-11 盤點發現伊利亞德在庫裡有 12 筆，只有 2 筆在全集，
其餘 10 筆散在「_待審分類」「宗教學」「神學」三個夾，其中三組還是同一本書的重複
列名。hub 的七筆書目只有兩筆連得到內容——書其實都在，只是沒有被收攏。

搬檔與改 DB 是同一件事的兩半，分開做就會出現「Drive 上移走了、線上圖書館還指著
舊路徑」（[[feedback_set_books_subfolder]]）。所以這支一起做完，並且 dry-run 預設。

  python scripts/eliade_consolidate.py            # 只看要做什麼
  python scripts/eliade_consolidate.py --apply    # 真的搬＋改 file_path
"""
from __future__ import annotations

import argparse
import json
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\全集\宗教學\伊利亞德")

# 要搬進全集的卷。刻意用 id 寫死而不是靠書名比對——書名重複的正是這批書的問題。
MOVE = [
    ("69441666-4c72-4ec8-b603-8b2034622fdb", "Patterns in Comparative Religion（英文原著，499 段）"),
    ("d7fef009-254a-470c-8d89-1e7ddedd3e0a", "神聖的存在：比較宗教的範型（上一本的中譯，239 段）"),
    ("50739442-8ba3-43b3-a0a6-0799e473943a", "宗教思想史 第三卷（19 段）"),
    ("094b90d9-559d-4e61-94c7-1439b07236bd", "Myth and Reality（3 段，待重解析）"),
    ("9cb99c8d-9ec7-459d-84ed-e3eb4c2b3f33", "The Sacred And The Profane（2 段，待重解析）"),
    ("b035c464-a14d-4da6-b5d7-9834e83496e6", "神聖與世俗（2 段，待重解析）"),
    ("693cb778-39d7-4b3d-b702-5770dbc75c1e", "宗教思想史（36.9 MB PDF，未解析）"),
]

# 疑似重複，**不自動刪**——刪 row 這件事留給使用者定奪，這裡只報告。
DUPES = [
    ("5b22cdfb-feba-4a4c-af20-44a442d8da16",
     "Shamanism：與全集那份 f1dc179e 同為 1.7 MB，同一個檔"),
    ("64e0d3ed-f948-496a-99e7-15094193aa9e",
     "神聖的存在：與 d7fef009 同為 23.1 MB，同一個檔但這筆 0 段"),
    ("c566e150-e7fd-4d75-8e03-df342c49c623",
     "神聖的存在：1.0 MB，與上面兩筆不同檔，file_path 是空的——來源不明"),
]


def env() -> dict:
    out = {}
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip("\"'")
    return out


E = env()
URL = E["SUPABASE_URL"]
KEY = E.get("SUPABASE_SERVICE_ROLE_KEY") or E.get("SUPABASE_SERVICE_KEY")
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def api(path: str, method: str = "GET", body=None):
    req = urllib.request.Request(
        URL + "/rest/v1/" + urllib.parse.quote(path, safe="?&=.,*()-"),
        method=method,
        headers={**H, **({"Prefer": "return=representation"} if method == "PATCH" else {})},
        data=json.dumps(body).encode() if body is not None else None,
    )
    raw = urllib.request.urlopen(req).read().decode("utf-8")
    return json.loads(raw) if raw.strip() else []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    if not DEST.exists():
        print(f"⚠ 目的地不存在：{DEST}（Drive 沒掛載？）")
        if a.apply:
            raise SystemExit(1)

    print(f"{'實際執行' if a.apply else '預演（加 --apply 才會動）'}　→ {DEST}\n")
    moved = 0
    for eid, label in MOVE:
        rows = api(f"ebooks?select=id,title,file_path&id=eq.{eid}")
        if not rows:
            print(f"  ✗ 查無 {eid[:8]}  {label}")
            continue
        r = rows[0]
        src = Path(r["file_path"]) if r.get("file_path") else None
        if not src:
            print(f"  ✗ {label}：DB 沒有 file_path，跳過")
            continue
        if not src.exists():
            print(f"  ✗ {label}：檔案不在 {src}")
            continue
        dst = DEST / src.name
        if dst.exists() and dst.resolve() == src.resolve():
            print(f"  ・已在全集夾：{label}")
            continue
        print(f"  → {label}")
        print(f"      {src.name}")
        if a.apply:
            DEST.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            # 🚨 搬完一定要同步 file_path，否則線上圖書館還指著舊路徑
            api(f"ebooks?id=eq.{eid}", "PATCH", {"file_path": str(dst)})
            moved += 1

    print(f"\n{'搬了 ' + str(moved) + ' 本' if a.apply else ''}")
    print("疑似重複（**不自動刪**，等你定奪）：")
    for eid, why in DUPES:
        print(f"  · {eid[:8]}  {why}")


if __name__ == "__main__":
    main()
