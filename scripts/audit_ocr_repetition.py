#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回頭掃已入庫的書，找出「某一頁其實是上一頁的複述」的 OCR 幻覺。

ocr_with_gemini 從 2026-09-07 起會在寫入前擋掉這種書（detect_repeated_pages），
但那之前 OCR 的書沒經過這道閘。這一支就是補掃歷史資料。

判準與寫入端同一份程式碼（直接 import），不另外複製一套邏輯 —— 兩邊的門檻若
各走各的，稽核就會跟實際行為對不上。

全文在 Drive 的 _chunks/{id}.jsonl，不在 DB（DB 只有 100 字 preview，而重複多半
發生在頁的尾段，preview 抓不到）。所以這支是掃 Drive、不是掃 DB。

  python scripts/audit_ocr_repetition.py                 # 只報告
  python scripts/audit_ocr_repetition.py --limit 200      # 先掃一部分
  python scripts/audit_ocr_repetition.py --apply          # 把不合格的退回 OCR 佇列

--apply 做三件事（每本）：
  1. {id}.jsonl → {id}.jsonl.bad-repetition（保留原始輸出，不刪）
  2. 刪掉 ebook_chunks 裡該書的 preview 列
  3. parsed_at 清空、parse_error 寫回 OCR 佇列的標記
書於是回到 ocr_with_gemini 的待辦清單，下一輪重跑；重跑時新的閘門會擋住同樣的
壞輸出，不會再寫進來。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import requests

from parse_worker import URL, H

CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
# ocr_with_gemini 的待辦判準是 parse_error 含這串；退回佇列就是把它寫回去。
REQUEUE_MARKER = "no extractable text (needs OCR)"
REPORT = Path("c:/tmp/ocr_repetition_audit.json")


def _load_detector():
    """直接載入 ocr_with_gemini 取用同一份判準。

    用 spec 載入而不是 `import ocr_with_gemini`，是因為那支在模組層會讀 .env 與
    建立 client；這裡只要兩個純函式，走 spec 一樣拿得到，且不必再開一條路徑。
    """
    spec = importlib.util.spec_from_file_location(
        "_ocr", str(Path(__file__).resolve().parent / "ocr_with_gemini.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def requeue_blocked(b: dict) -> str:
    """這本書能不能退回 OCR 佇列？回傳擋下來的理由，空字串表示可以。

    兩種書偵測得到重複、卻不該用這條路修：

      **非 PDF**。ocr_with_gemini 的對象是掃描 PDF；EPUB 的文字本來就抽得出來，
      它的重複是解析或重複入庫的問題，不是 OCR 幻覺。把 EPUB 標成「待 OCR」只會
      讓它卡在一條永遠處理不到它的佇列裡。

      **全集（collection 非 null）**。那是人工策展的，上架閘門本來就豁免它，
      而重跑會刪掉 chunk、把書從 /collected-works 的 reader 上拿掉。

    2026-09-07 那批 83 本裡，兩個條件都命中同一本《佛光祈願文》（EPUB＋全集）。
    """
    if (b.get("file_type") or "").lower() != "pdf":
        return f"非 PDF（{b.get('file_type')}）"
    if b.get("collection"):
        return f"全集（{b.get('collection')}）"
    return ""


def fetch_parsed_books(limit: int | None) -> list[dict]:
    """已 parse 的書，keyset 分頁（🚨 不帶 limit 的 select 會被 PostgREST 靜默
    截在 1000 筆，這個坑在本 repo 咬過三次）。"""
    out: list[dict] = []
    last = ""
    while True:
        cur = f"&id=gt.{last}" if last else ""
        r = requests.get(
            f"{URL}/rest/v1/ebooks?select=id,title,chunk_count,file_type,collection"
            f"&parsed_at=not.is.null&order=id{cur}&limit=1000",
            headers=H, timeout=90)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        out.extend(page)
        if limit and len(out) >= limit:
            return out[:limit]
        if len(page) < 1000:
            break
        last = page[-1]["id"]
    return out


def read_pages(book_id: str) -> list[dict] | None:
    p = CHUNKS_DIR / f"{book_id}.jsonl"
    if not p.exists():
        return None
    pages = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            pages.append({"page": r.get("page_number"), "text": r.get("content") or ""})
    return pages


def requeue(book_id: str) -> bool:
    src = CHUNKS_DIR / f"{book_id}.jsonl"
    if src.exists():
        src.replace(src.with_suffix(".jsonl.bad-repetition"))
    d = requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}",
                        headers={**H, "Prefer": "return=minimal"}, timeout=90)
    u = requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{book_id}",
                       headers={**H, "Prefer": "return=minimal"},
                       json={"parsed_at": None, "chunk_count": 0,
                             "parse_error": REQUEUE_MARKER,
                             "quality_score": None, "quality_checked_at": None},
                       timeout=60)
    return d.ok and u.ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    O = _load_detector()
    books = fetch_parsed_books(a.limit)
    print(f"已 parse 的書：{len(books):,} 本，逐本掃 Drive JSONL…", flush=True)

    bad, no_file, scanned = [], 0, 0
    for n, b in enumerate(books, 1):
        pages = read_pages(b["id"])
        if pages is None:
            no_file += 1
            continue
        scanned += 1
        ok, why = O.repetition_verdict(pages)
        if not ok:
            bad.append({"id": b["id"], "title": b["title"], "pages": len(pages),
                        "why": why, "blocked": requeue_blocked(b)})
            print(f"  ✗ {b['title'][:44]}\n      {why}", flush=True)
        if n % 500 == 0:
            print(f"  …{n:,}/{len(books):,}（不合格 {len(bad)}）", flush=True)

    print(f"\n掃了 {scanned:,} 本（另有 {no_file:,} 本在 Drive 上找不到 JSONL）")
    print(f"重複幻覺不合格：{len(bad)} 本")
    REPORT.write_text(json.dumps(bad, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ {REPORT}")

    if not a.apply:
        print("\n（只報告；要退回 OCR 佇列請加 --apply）")
        return 0

    todo = [x for x in bad if not x["blocked"]]
    held = [x for x in bad if x["blocked"]]
    if held:
        print(f"\n不退回佇列的 {len(held)} 本（理由見 requeue_blocked）：")
        for x in held:
            print(f"  [{x['blocked']}] {x['title'][:44]}")
    done = sum(requeue(x["id"]) for x in todo)
    print(f"已退回佇列 {done}/{len(todo)} 本（原始輸出留在 .jsonl.bad-repetition）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
