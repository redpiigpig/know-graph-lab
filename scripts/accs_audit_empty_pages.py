#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""盤點 ACCS 有沒有「整段章節悄悄沒進資料庫」的書卷。

  python -X utf8 scripts/accs_audit_empty_pages.py            # 只列有嫌疑的
  python -X utf8 scripts/accs_audit_empty_pages.py --all      # 全部列出

為什麼需要這支：`ingest_accs_genesis.py` 的 `.done` 只檢查「目標頁是否都在
checkpoint 裡」，**不檢查那些頁有沒有吐出東西**。視覺引擎乾掉的那一夜，每一頁
照樣寫進 `{"pages": [...], "entries": []}`，然後整本被標成完成，排程從此不再重跑
——書打得開、前面幾章讀起來正常，後面整段悄悄不見。

🚨 **不要用「連續空頁」當判準**。每一卷書末都有附錄（教父人物小傳、主題索引、
   引用經文索引），那幾十上百頁本來就吐不出註釋條目；拿空頁去掃，13 個
   checkpoint 全部中，其中 11 個是正常的附錄。真正的判準是**資料庫裡的章覆蓋率**
   ——缺一整段連續的章才是出事，零星缺單章多半是 ACCS 本來就沒註（族譜那些）。

2026-09-02 實測抓到的真問題：
  · 詩篇 缺 28–50 章（詩1-50 卷第 325 頁之後全空）
  · 利未記 缺 12–27 章（第 294 頁之後全空）
  · 雅歌 缺 3–8 章 —— 這一本不是 OCR 的錯，**掃描檔只掃到一半**。
    《箴言、傳道書、雅歌》（校園 2010，ISBN 978-986-198-152-9）目錄寫著
    箴言 1／傳道書 259／**雅歌 395**／附錄 515。掃描檔 472 頁，最後一頁是書頁
    430、頁眉「歌 2.1-7」，而且在句子中間斷掉（「因為」之後沒了）。
    偏移量：書頁 ＝ PDF 頁 − 42（書頁 395 ＝ PDF 437，與 config 的 sng 起點相符）。
    **要補的是書頁 431–514（84 頁）**，即雅歌 2:8 到 8:14。附錄 515 之後不影響註釋。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
TMP = Path("c:/tmp" if sys.platform == "win32" else "/tmp")
# 連續缺幾章以上才算「整段不見」，低於這個數多半是 ACCS 本來就沒註的族譜等段落
RUN = 3

# ACCS 本來就不註的段落——2026-09-02 回 PDF 逐段核過，不是我們漏掉的：
#   ezk 21–27：掃描本第 163 頁印的是「結 20.40-44」、第 165 頁已經是第 28 章，
#              中間只隔一頁，塞不下七章。ACCS 從以西結 20 直接跳到 28。
#   ezk 5–8、29–32：同樣的形狀（前後兩頁相鄰）。
#   1ch 2–4、18–20：族譜與戰功名單，ACCS 沒有教父註釋。
# 🚨 這一份是「查過而且確定沒問題」的清單，不是「先放過再說」。要往裡面加東西，
#    先回 PDF 看前後兩頁的頁眉章號夠不夠塞得下那幾章。
KNOWN_SPARSE: dict[str, list[tuple[int, int]]] = {
    "ezk": [(5, 8), (21, 27), (29, 32)],
    "1ch": [(2, 4), (18, 20)],
}

sys.path.insert(0, str(ROOT / "scripts"))
from accs_commentary import CHAPTER_COUNTS      # noqa: E402


def load_env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def fetch_coverage() -> dict[str, set[int]]:
    import requests
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    out: dict[str, set[int]] = {}
    off = 0
    while True:
        r = requests.get(f"{url}/rest/v1/accs_commentary", headers=h, timeout=120,
                         params={"select": "book_code,chapter", "limit": "1000",
                                 "offset": str(off), "order": "id"})
        r.raise_for_status()
        batch = r.json()
        for row in batch:
            out.setdefault(row["book_code"], set()).add(row["chapter"])
        off += len(batch)
        if len(batch) < 1000:
            break
    return out


def gaps(have: set[int], total: int) -> list[tuple[int, int]]:
    missing = [c for c in range(1, total + 1) if c not in have]
    runs: list[tuple[int, int]] = []
    for c in missing:
        if runs and c == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], c)
        else:
            runs.append((c, c))
    return [r for r in runs if r[1] - r[0] + 1 >= RUN]


def last_live_page(book: str) -> str:
    """該書每一個 checkpoint 裡最後一個吐得出東西的頁，供人回 PDF 對照。

    一本書可能拆成好幾個 PDF（詩篇分 1-50／51-150），要逐個報——只報一個的話
    會挑到沒出事的那一半，把人指向錯的檔案。
    """
    found: list[str] = []
    for ckpt in TMP.glob(f"accs_{book}_*.raw.jsonl"):
        live = []
        for line in ckpt.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("entries"):
                live += [p for p in (rec.get("pages") or []) if isinstance(p, int)]
        if live:
            all_pages = []
            for line in ckpt.read_text(encoding="utf-8", errors="replace").splitlines():
                if line.strip():
                    try:
                        all_pages += (json.loads(line).get("pages") or [])
                    except json.JSONDecodeError:
                        pass
            flag = " ←整段吐空" if max(all_pages) - max(live) > 25 else ""
            found.append(f"{ckpt.name}：最後有內容的頁 {max(live)}／共 {max(all_pages)} 頁{flag}")
    return (chr(10) + "     ").join(found) if found else "（找不到 checkpoint）"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    load_env()
    cov = fetch_coverage()
    bad = 0
    for book, total in CHAPTER_COUNTS.items():
        have = cov.get(book, set())
        if not have:
            print(f"🚨 {book:<4} 一條註釋都沒有（該書 {total} 章）")
            bad += 1
            continue
        known = KNOWN_SPARSE.get(book, [])
        bad_runs = [r for r in gaps(have, total) if r not in known]
        if bad_runs:
            bad += 1
            span = "、".join(f"{x}–{y}" if x != y else str(x) for x, y in bad_runs)
            print(f"🚨 {book:<4} {len(have)}/{total} 章；連續缺 {span}")
            print(f"     {last_live_page(book)}")
        elif a.all:
            print(f"   {book:<4} {len(have)}/{total} 章")
    print(f"\n{len(CHAPTER_COUNTS)} 卷裡 {bad} 卷有整段缺口（連續缺 {RUN} 章以上）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
