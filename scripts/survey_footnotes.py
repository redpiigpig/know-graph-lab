#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""唯讀盤點：電子圖書館（ebooks.collection is null）全館「註釋寫法」分類（2026-09-28）。

只讀 Supabase ebooks 表與本機 _chunks/*.jsonl，不寫任何檔案、不動 DB、不推 R2。
每本書可能同時中好幾類（例如已標準化的一部分＋還沒轉的一部分），用來估計
scripts/link_footnotes.py 能吃下多少、報告要另外列哪些類還沒辦法自動處理。

用法：
  python -X utf8 scripts/survey_footnotes.py            # 全館（電子圖書館）
  python -X utf8 scripts/survey_footnotes.py --sample 50 # 抽樣（穩定亂數種子）
  python -X utf8 scripts/survey_footnotes.py --json out.json  # 額外存機器可讀結果
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import consolidate_page_chunks as cp  # noqa: E402  重用它的頁尾分隔線判準

CH = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")

_CJK = r"[\u4e00-\u9fff]"
SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_RE = re.compile(f"[{SUP_DIGITS}]{{1,3}}")

RULE_RE = re.compile(r"^[—－\-]{15,}\s*$")
PAGE_NOTE_LINE = re.compile(r"^\d{1,4}\s*(?=\S)(?!\d)")
ALREADY_LINKED = re.compile(r"\[\^\d{1,4}\]")
PAREN_ENTRY_RE = re.compile(r"^\((\d{1,4})\)\s*\S")
BRACKET_ENTRY_RE = re.compile(r"^\[(\d{1,4})\]\s*\S")
HEADING_RE = re.compile(r"^#{1,4}\s+(.+)$")
NOTES_WORD = re.compile(r"^(?:註釋|注釋|附註|註解|注解|Notes?)\s*$", re.I)
# 註N／注N 緊接在中文字或標點之後（避免「注意」「關注」這種詞）；右界排除年月日頁
ZHU_N = re.compile(r"(?:(?<=" + _CJK + r")|(?<=[，。、；：！？」』）]))"
                    r"(?:註|注)(\d{1,3})(?![\d年月日%％頁])")
BRACKET_INLINE = re.compile(r"(?:(?<=" + _CJK + r")|(?<=[，。、；：！？」』）]))\[(\d{1,3})\](?!\()")


def classify_chunk(content: str) -> set[str]:
    """比照 reader（pages/ebook/[id].vue renderMarkdown）逐段（\\n{2,} 分段）掃描：
    只有「15+ 破折號分隔線」會切換 in-footnotes 模式；標題只會把模式切回正文，
    不會切進註釋模式。所以章節目錄／大綱裡的「(1) 廣度量」這種行首數字，
    reader 並不會當註釋——分類必須照這個規則掃，不能只 grep `^\\(\\d+\\)`
    （否則會把目錄／大綱誤判成大量「已有 (N) 條列註釋」）。"""
    tags = set()
    if not content:
        return tags
    if ALREADY_LINKED.search(content):
        tags.add("linked")

    blocks = re.split(r"\n{2,}", content)
    in_foot = False
    working_paren = 0        # 切換模式內、reader 真的會渲染成註釋條目的 (N)
    stray_paren_outside = 0  # 模式外的 (N)（多半是目錄/大綱，非註釋）
    working_bracket = 0
    saw_rule = False
    saw_notes_heading_no_rule_yet = False
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if RULE_RE.match(b):
            in_foot = not in_foot
            saw_rule = True
            continue
        h = HEADING_RE.match(b)
        if h:
            if in_foot:
                in_foot = False
            elif NOTES_WORD.match(h.group(1).strip()) and not saw_rule:
                saw_notes_heading_no_rule_yet = True
            continue
        if in_foot:
            if PAREN_ENTRY_RE.match(b):
                working_paren += 1
            elif BRACKET_ENTRY_RE.match(b):
                working_bracket += 1
        else:
            if PAREN_ENTRY_RE.match(b):
                stray_paren_outside += 1

    if working_paren >= 2:
        tags.add("paren_entries_working")
    if working_bracket >= 2:
        tags.add("bracket_entries_in_foot_mode")  # 進了模式但格式是 [N]，reader 仍不認得
    if saw_notes_heading_no_rule_yet:
        tags.add("heading_notes_no_rule")  # 「## 註釋」標題但全篇沒有分隔線→整段是死的
    if stray_paren_outside >= 3:
        tags.add("paren_like_toc_or_outline")  # 大量行首 (N) 但不在切換模式內：多半是目錄/大綱

    # 頁尾分隔線＋數字起頭註文：直接重用 consolidate_page_chunks.split_page
    # 的判準，跟那支工具認的是同一件事，避免自己另一套邏輯兜出不同答案。
    _, page_notes = cp.split_page(content)
    if page_notes:
        tags.add("page_rule_bare_number_notes")

    if len(SUP_RE.findall(content)) >= 2:
        tags.add("superscript")
    if len(ZHU_N.findall(content)) >= 2:
        tags.add("zhu_n_inline")
    if len(BRACKET_INLINE.findall(content)) >= 2:
        tags.add("bracket_inline")
    return tags


def load_book_chunks(ebook_id: str) -> list[dict] | None:
    p = CH / f"{ebook_id}.jsonl"
    if not p.exists():
        return None
    try:
        return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
    except Exception:  # noqa: BLE001
        return None


def fetch_library() -> list[dict]:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    rows: list[dict] = []
    offset = 0
    while True:
        r = requests.get(
            f"{url}/rest/v1/ebooks?select=id,title,file_type&collection=is.null&order=id"
            f"&limit=1000&offset={offset}",
            headers=headers, timeout=60,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        offset += 1000
        if len(batch) < 1000:
            break
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=20260928)
    ap.add_argument("--json", type=str, default="")
    args = ap.parse_args()

    library = fetch_library()
    print(f"電子圖書館（collection is null）共 {len(library)} 本", flush=True)
    if args.sample:
        random.seed(args.seed)
        library = random.sample(library, min(args.sample, len(library)))
        print(f"抽樣 {len(library)} 本", flush=True)

    book_tags: dict[str, set[str]] = {}
    titles: dict[str, str] = {}
    skipped = Counter()
    n_read = 0
    for i, row in enumerate(library):
        bid = row["id"]
        titles[bid] = row.get("title") or bid
        chunks = load_book_chunks(bid)
        if chunks is None:
            skipped["no-local-jsonl"] += 1
            continue
        if any(("source_text" in c or "sources" in c) for c in chunks):
            skipped["bilingual-skip"] += 1
            continue
        tags: set[str] = set()
        for c in chunks:
            if c.get("chunk_type") not in ("page", "chapter", "section", None) and c.get("chunk_type"):
                continue
            fmt = c.get("format")
            if fmt and fmt not in ("markdown", "text", "md"):
                continue
            tags |= classify_chunk(c.get("content") or "")
        if not tags:
            tags = {"none_detected"}
        book_tags[bid] = tags
        n_read += 1
        if n_read % 500 == 0:
            print(f"  ...已讀 {n_read}/{len(library)}", flush=True)

    print(f"實際讀取 {n_read} 本；略過 {dict(skipped)}", flush=True)

    cat_books: dict[str, list[str]] = defaultdict(list)
    for bid, tags in book_tags.items():
        for t in tags:
            cat_books[t].append(bid)

    LABELS = {
        "linked": "已經是 [^N]（標準化過，reader 可點）",
        "page_rule_bare_number_notes": "OCR／MinerU 頁尾分隔線＋數字起頭註文（consolidate_page_chunks 可吃）",
        "paren_entries_working": "已有 (N) 條列註釋，且在切換模式內（reader 已認得，但正文未必連上 [^N]）",
        "bracket_entries_in_foot_mode": "切換模式內是 [N] 條列（reader 不認得這個括號、需改成 (N)）",
        "heading_notes_no_rule": "章末「註釋／Notes」標題但全篇沒有分隔線（reader 完全不會渲染成註釋，是死的）",
        "paren_like_toc_or_outline": "行首多個 (N)，但不在切換模式內（多半是目錄／大綱，非註釋，過濾用）",
        "superscript": "正文含上標數字 ¹²³",
        "zhu_n_inline": "正文含行內「註N／注N」",
        "bracket_inline": "正文含行內「[N]」（緊接中文或標點）",
        "none_detected": "以上皆未偵測到（可能無註釋或格式特殊）",
    }

    print("\n=== 分類統計（本數；書可能跨多類） ===")
    rows_out = []
    for cat, ids in sorted(cat_books.items(), key=lambda kv: -len(kv[1])):
        examples = [titles[i][:40] for i in ids[:3]]
        label = LABELS.get(cat, cat)
        print(f"{label:45s} {len(ids):5d} 本   例：{'／'.join(examples)}")
        rows_out.append({"category": cat, "label": label, "count": len(ids),
                          "examples": [{"id": i, "title": titles[i]} for i in ids[:3]]})

    if args.json:
        Path(args.json).write_text(
            json.dumps({"total_library": len(library), "n_read": n_read,
                        "skipped": dict(skipped), "categories": rows_out,
                        "book_tags": {k: sorted(v) for k, v in book_tags.items()}},
                       ensure_ascii=False, indent=1),
            encoding="utf-8")
        print(f"\n已存 {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
