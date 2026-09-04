#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「整本擠成一塊」的書重新切成可讀單位。

為什麼需要這支：standardize 的邏輯是**合併**，對「碎片太多」有效，對「巨塊」
反而幫倒忙 —— 2026-09-04 實測，《文明的衝突與演化(6冊)》重標準化後中位數從
287 修到 2,438（好事），最大一塊卻從 985,174 字變成 2,462,851 字。跑完 94 本
「0 失敗」，卻只有 5 本脫離 RESTANDARDIZE tier，因為它們的病是巨塊不是碎片。

典型長相（《1683維也納之戰》，36 分）：全書只有 6 個 chunk，5 個是封面／版權／
目錄之類的前置頁，第 6 個是 207,229 字的整本正文。所謂「碎片過半」只是分母
太小造成的假象。

切法兩段式：
  1. 先在 markdown 標題切 —— 順便把 chapter_path 還原成該段的標題
  2. 標題之間仍然過長的，再在空行段落邊界切成 target 大小；**絕不切進段落中間**

🚨 page_number 是神聖的（見 [[feedback_pdf_page_number]]）：切出來的每一片
   原樣沿用來源 chunk 的 page_number，只複製不重編，也絕不跨頁合併。
   本支完全不做合併 —— 資料顯示那些小 chunk 是正當的前置頁，合併它們既救不了
   分數，又會踩壞逐頁 PDF 的頁碼。

  python scripts/resegment_ebook.py --scan                 # 只列出誰需要切
  python scripts/resegment_ebook.py --ids a,b,c [--dry-run]
  python scripts/resegment_ebook.py --all [--limit N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests

from ingest_new_books import URL, SB_HEADERS

CHUNKS_DIR = Path("G:/我的雲端硬碟/資料/知識圖工作室/_chunks")
PREVIEW_LEN = 100

# 🚨 偵測門檻與切分門檻是兩回事，別共用一個數字。
# GIANT 是 quality_sweep 判 UNDER_SEGMENTED 的線；只切超過它的塊，會留下一堆
# 「78,491 字」這種剛好在門檻底下的塊 —— 分數上算過關，實際上一塊七萬多字根本
# 沒法讀。又是一個「看起來像成功」。所以切分用低得多的 SPLIT_ABOVE。
GIANT = 80_000      # 與 quality_sweep 同一條線，只用來挑「哪些書要處理」
SPLIT_ABOVE = 20_000  # 超過這個長度的塊一律重切；一塊兩萬字已經是一章的量
TARGET = 2_500      # 切完之後每片的目標字數
MAX_PIECE = 8_000   # 單片上限；段落本身超過這個長度才允許硬切

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)


def split_sections(text: str) -> list[tuple[str | None, str]]:
    """依 markdown 標題切成 (標題, 內文) 段。標題以前的內容標題為 None。"""
    marks = list(_HEADING.finditer(text))
    if not marks:
        return [(None, text)]
    out: list[tuple[str | None, str]] = []
    if marks[0].start() > 0:
        head = text[: marks[0].start()].strip()
        if head:
            out.append((None, head))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        body = text[m.start():end].strip()
        if body:
            out.append((m.group(2).strip(), body))
    return out


def pack_paragraphs(text: str, target: int = TARGET, max_piece: int = MAX_PIECE) -> list[str]:
    """把一段文字依空行段落打包成接近 target 的片段。

    絕不切進段落中間 —— 除非單一段落本身就超過 max_piece（多半是沒有斷行的
    OCR 產物），那時才在句號處退而求其次地硬切。
    """
    paras = [p for p in re.split(r"\n{2,}", text) if p.strip()]
    pieces: list[str] = []
    buf: list[str] = []
    size = 0
    for p in paras:
        if len(p) > max_piece:
            if buf:
                pieces.append("\n\n".join(buf)); buf, size = [], 0
            pieces.extend(_hard_split(p, target, max_piece))
            continue
        if size and size + len(p) > target:
            pieces.append("\n\n".join(buf)); buf, size = [], 0
        buf.append(p)
        size += len(p) + 2
    if buf:
        pieces.append("\n\n".join(buf))
    return pieces or [text]


def _hard_split(para: str, target: int, max_piece: int) -> list[str]:
    """單一超長段落：在句末標點切，切不動才按字數切。"""
    sents = re.split(r"(?<=[。！？.!?])\s*", para)
    out, buf, size = [], [], 0
    for s in sents:
        if not s:
            continue
        if len(s) > max_piece:                       # 連句子都超長：只能硬切
            if buf:
                out.append("".join(buf)); buf, size = [], 0
            out.extend(s[i:i + target] for i in range(0, len(s), target))
            continue
        if size and size + len(s) > target:
            out.append("".join(buf)); buf, size = [], 0
        buf.append(s)
        size += len(s)
    if buf:
        out.append("".join(buf))
    return out


def resegment(chunks: list[dict], giant: int = SPLIT_ABOVE, target: int = TARGET) -> list[dict]:
    """回傳重切後的 chunk 串列。沒有巨塊就原樣回傳（同一個物件內容）。

    只切不合併。切出來的每一片沿用來源 chunk 的 page_number 與 chunk_type；
    chapter_path 優先用該片所屬的 markdown 標題，沒有標題才沿用來源的。
    """
    out: list[dict] = []
    for c in chunks:
        content = c.get("content") or ""
        if len(content) <= giant:
            out.append(dict(c))
            continue
        for title, body in split_sections(content):
            path = title or c.get("chapter_path")
            for piece in pack_paragraphs(body, target=target):
                out.append({**c, "content": piece, "chapter_path": path})
    for i, c in enumerate(out):
        c["chunk_index"] = i
    return out


# --------------------------------------------------------------------------- IO

def load_jsonl(book_id: str) -> list[dict] | None:
    p = CHUNKS_DIR / f"{book_id}.jsonl"
    if not p.exists():
        return None
    try:
        return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
    except Exception:
        return None


def save_jsonl(book_id: str, chunks: list[dict]) -> None:
    """整檔覆寫。舊內容就是舊的分段，留著沒有意義，直接換掉。"""
    p = CHUNKS_DIR / f"{book_id}.jsonl"
    tmp = p.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(p)          # 原子替換：中途掛掉不會留下半截檔案


def push_previews(book_id: str, chunks: list[dict]) -> bool:
    """DB 只存 100 字預覽，全文正本在 Drive。先刪光舊列再整批寫入。"""
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}",
                    headers=SB_HEADERS, timeout=60)
    rows = [{
        "ebook_id": book_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c.get("chunk_type"),
        "page_number": c.get("page_number"),
        "chapter_path": c.get("chapter_path"),
        "content": (c.get("content") or "")[:PREVIEW_LEN],
        "char_count": len(c.get("content") or ""),
    } for c in chunks]
    for i in range(0, len(rows), 50):
        r = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=SB_HEADERS,
                          json=rows[i:i + 50], timeout=60)
        if not r.ok:
            print(f"    ⚠ preview insert 失敗: {r.status_code} {r.text[:120]}", file=sys.stderr)
            return False
    requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{book_id}", headers=SB_HEADERS,
                   json={"chunk_count": len(rows),
                         "total_chars": sum(x["char_count"] for x in rows)}, timeout=30)
    return True


def fetch_candidates(limit: int | None = None) -> list[dict]:
    """所有還沒及格、且有 chunk 的圖書館書。"""
    rows, off = [], 0
    while True:
        r = requests.get(f"{URL}/rest/v1/ebooks?collection=is.null&quality_score=not.is.null"
                         f"&quality_score=lt.80&select=id,title,file_type,quality_score"
                         f"&offset={off}&limit=1000", headers=SB_HEADERS, timeout=90)
        r.raise_for_status()
        b = r.json()
        rows += b
        if len(b) < 1000:
            break
        off += 1000
    return rows[:limit] if limit else rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--scan", action="store_true", help="只盤點誰有巨塊，不動任何東西")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--split-above", type=int, default=SPLIT_ABOVE,
                    help=f"超過幾個字就重切（預設 {SPLIT_ABOVE}）")
    a = ap.parse_args()

    if a.ids:
        ids = [x.strip() for x in a.ids.split(",") if x.strip()]
        books = [{"id": i, "title": i, "quality_score": None} for i in ids]
    elif a.all or a.scan:
        books = fetch_candidates(a.limit)
    else:
        print(__doc__)
        return 1

    need, done, skip = [], 0, 0
    for b in books:
        cs = load_jsonl(b["id"])
        if not cs:
            skip += 1
            continue
        if not any(len(c.get("content") or "") > a.split_above for c in cs):
            skip += 1
            continue
        need.append((b, cs))

    print(f"掃描 {len(books)} 本 → 有 >{a.split_above:,} 字巨塊需要重切的 {len(need)} 本"
          f"（其餘 {skip} 本沒有巨塊或找不到 JSONL）", flush=True)
    if a.scan:
        for b, cs in need[:40]:
            big = max(len(c.get("content") or "") for c in cs)
            print(f"  {str(b.get('quality_score')):>4}分 {len(cs):>5} chunk 最大 {big:>9,}  {b['title'][:44]}")
        return 0

    for i, (b, cs) in enumerate(need, 1):
        new = resegment(cs, giant=a.split_above)
        big_before = max(len(c.get("content") or "") for c in cs)
        big_after = max(len(c.get("content") or "") for c in new)
        line = (f"[{i}/{len(need)}] {len(cs)}→{len(new)} chunk, "
                f"最大 {big_before:,}→{big_after:,}  {b['title'][:38]}")
        if a.dry_run:
            print("  DRY " + line, flush=True)
            continue
        save_jsonl(b["id"], new)
        ok = push_previews(b["id"], new)
        print(("  OK  " if ok else "  FAIL ") + line, flush=True)
        done += ok
    print(f"\n完成 {done}/{len(need)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
