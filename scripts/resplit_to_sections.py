#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""resplit_to_sections.py
主動把章 (h2) 級 chunk 細切成節 (h3) 級。
不同於 resplit_giant_chunks (only >400K)：

  - 對 >5K chars 的 chunk 都檢查節邊界（threshold 低）
  - patterns 只認「節級」標記，不認「章級」（不會把章重切成章）
      h3 markdown:       ^### ...
      Chinese 節:        ^第N節 (N = digits / CJK 數字)
      Aquinas Question:  ^問題N. / ^Question N.
      Aquinas Article:   ^第N條
      English Section:   ^Section [IVXLCDM0-9]+
  - 每 chunk ≥2 個節邊界才切（避免單一節變獨立 chunk）
  - 不遞迴（切到節為止；不再往下切）
  - Annotation guard + Idempotency: 如果 chunk 開頭已是 ### 就視為「已是節 chunk」跳過

Usage:
  python scripts/resplit_to_sections.py status                # 列出 candidate
  python scripts/resplit_to_sections.py run --book <id> [--dry-run]
  python scripts/resplit_to_sections.py run --all [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import standardize_ebook as se
import standardize_pdf_lite as pl
import resplit_giant_chunks as v1

import requests


SECTION_MIN_CHUNK = 5_000          # chunk 內容小於此 → 不重切
SECTION_MIN_BOUNDARIES = 2         # 至少這麼多節邊界才切
PREVIEW_LEN = v1.PREVIEW_LEN


# 節級 patterns（不含章級！）
_H3_RX = re.compile(r"(?m)^###\s+(.+?)\s*$")
_CHINESE_SEC_RX = re.compile(
    r"(?m)^第[一二三四五六七八九十百千零〇兩两0-9]+節(?=\s|[一-鿿])"
)
_AQUINAS_QUESTION_RX = re.compile(
    r"(?m)^(?:問題|Question)\s*[0-9]+"
)
_AQUINAS_ARTICLE_RX = re.compile(
    r"(?m)^第[一二三四五六七八九十百千0-9]+條"
)
_ENGLISH_SECTION_RX = re.compile(
    r"(?m)^Section\s+[IVXLCDM0-9]+", re.IGNORECASE
)

SECTION_PATTERNS = [
    ("md_h3",         _H3_RX),
    ("chinese_jie",   _CHINESE_SEC_RX),
    ("aquinas_q",     _AQUINAS_QUESTION_RX),
    ("aquinas_a",     _AQUINAS_ARTICLE_RX),
    ("english_sec",   _ENGLISH_SECTION_RX),
]


def first_section_text(seg: str) -> str | None:
    """Best section label for a sub-segment."""
    # Prefer explicit markdown heading
    m = _H3_RX.search(seg)
    if m:
        return m.group(1).strip()[:80]
    for _, rx in SECTION_PATTERNS:
        m = rx.search(seg)
        if m:
            ls = seg.rfind("\n", 0, m.start()) + 1
            le = seg.find("\n", m.start())
            line = seg[ls:le if le != -1 else len(seg)].strip()
            return line[:80] if line else None
    return None


def find_section_offsets(content: str) -> tuple[list[int], str | None]:
    """Combine ALL section patterns in this chunk, dedupe by offset.
    Returns (sorted offsets list, method label). Empty list if no boundaries."""
    all_offsets: list[tuple[int, str]] = []
    for name, rx in SECTION_PATTERNS:
        for m in rx.finditer(content):
            all_offsets.append((m.start(), name))
    if not all_offsets:
        return [], None
    # Dedupe by offset (one offset is one boundary even if multiple patterns match)
    seen: dict[int, str] = {}
    for off, name in all_offsets:
        if off not in seen:
            seen[off] = name
    offsets = sorted(seen.keys())
    # Method label is the dominant pattern
    name_counts: dict[str, int] = {}
    for o in offsets:
        n = seen[o]
        name_counts[n] = name_counts.get(n, 0) + 1
    dominant = max(name_counts, key=name_counts.get)
    return offsets, dominant


def is_already_section_chunk(content: str) -> bool:
    """Chunk 已是節級 → 跳過避免雙切。判準: chunk 開頭是 ### 或 第N節，且
    內部沒有更深一層的 sub-section 邊界（沒有 第N節 / Q.N / Article 在 body 中）。
    (Aquinas 神學大全 case: chunk 開頭 `### 第N題` 是「題」級 = 章級，body 裡有
     多個 `第N節` = 節級 — 應該繼續切，不該跳過。)"""
    stripped = content.lstrip()
    starts_section = stripped.startswith("###") or bool(
        _CHINESE_SEC_RX.match(stripped.split("\n", 1)[0])
    )
    if not starts_section:
        return False
    # 看 body 內 (offset > 100 之後) 是否還有節邊界
    body = content[100:]
    inner_boundaries = (
        len(_CHINESE_SEC_RX.findall(body))
        + len(_AQUINAS_ARTICLE_RX.findall(body))
        + len(_AQUINAS_QUESTION_RX.findall(body))
        + len(_ENGLISH_SECTION_RX.findall(body))
    )
    # 還有內部節邊界 → 該書是更深 hierarchy，應該繼續切
    if inner_boundaries >= SECTION_MIN_BOUNDARIES:
        return False
    return True


def resplit_chunk_to_sections(chunk: dict) -> tuple[list[dict] | None, str | None]:
    content = chunk.get("content") or ""
    if len(content) < SECTION_MIN_CHUNK:
        return None, None
    if is_already_section_chunk(content):
        return None, None

    offsets, method = find_section_offsets(content)
    if len(offsets) < SECTION_MIN_BOUNDARIES:
        return None, None

    # Always include 0 as boundary so leading prose (chapter intro) gets its
    # own chunk, unless the first match is already at offset 0
    if 0 not in offsets:
        offsets = [0] + offsets

    parts = v1.split_at_offsets(content, offsets)
    if len(parts) < 2:
        return None, None

    base_chapter = chunk.get("chapter_path") or ""
    new_chunks = []
    for i, (off, seg) in enumerate(parts):
        sec_label = first_section_text(seg)
        if i == 0:
            # Leading segment — keep parent chapter title
            cp = base_chapter or None
        elif sec_label and base_chapter:
            cp = f"{base_chapter} / {sec_label}"
        elif sec_label:
            cp = sec_label
        else:
            cp = base_chapter or None
        nc = dict(chunk)
        nc["chapter_path"] = (cp or "")[:500] or None
        nc["content"] = seg
        new_chunks.append(nc)
    return new_chunks, method


def fetch_section_rich_books() -> list[dict]:
    """Scan local JSONL for books that look like candidates.
    Returns list of {id, n_chunks, total_boundaries}.
    Same logic as c:/tmp/probe_section_potential.py."""
    chunks_dir = Path(os.environ.get("EBOOK_CHUNKS_DIR") or se.CHUNKS_DIR)
    candidates: list[dict] = []
    for jp in chunks_dir.glob("*.jsonl"):
        try:
            chunks = [json.loads(l) for l in jp.read_text(encoding="utf-8").splitlines() if l.strip()]
        except Exception:
            continue
        if len(chunks) < 3:
            continue
        section_rich = 0
        total = 0
        for c in chunks:
            content = c.get("content") or ""
            if len(content) < SECTION_MIN_CHUNK:
                continue
            if is_already_section_chunk(content):
                continue
            offsets, _ = find_section_offsets(content)
            if len(offsets) >= SECTION_MIN_BOUNDARIES + 1:  # need ≥3 boundaries for sensible split
                section_rich += 1
                total += len(offsets)
        if section_rich >= 3 and total >= 10:
            candidates.append({
                "id": jp.stem,
                "n_chunks": len(chunks),
                "section_rich": section_rich,
                "total_boundaries": total,
            })
    return candidates


def process_book(book: dict, dry_run: bool = False) -> tuple[int, str | None, dict]:
    bid = book["id"]
    if v1.annotations_for(bid) > 0:
        return 0, "skipped: book has annotations", {}

    chunks = v1.load_chunks(bid)
    if not chunks:
        return 0, "skipped: JSONL missing", {}

    original_count = len(chunks)
    new_all = []
    method_stats: dict[str, int] = {}
    n_resplit = 0
    for c in chunks:
        sub, method = resplit_chunk_to_sections(c)
        if sub is None:
            new_all.append(c)
        else:
            new_all.extend(sub)
            n_resplit += 1
            method_stats[method] = method_stats.get(method, 0) + 1
    if n_resplit == 0:
        return 0, "no chunks needed section split", {}

    new_all = v1.renumber(new_all)
    added = len(new_all) - original_count

    if dry_run:
        return added, None, method_stats

    p = v1.write_jsonl(bid, new_all)
    try:
        v1.push_to_r2(bid, p)
    except Exception as e:
        return added, f"JSONL rewritten but R2 push failed: {str(e)[:120]}", method_stats
    try:
        v1.refresh_db(bid, new_all)
    except Exception as e:
        return added, f"R2 ok but DB refresh failed: {str(e)[:120]}", method_stats
    return added, None, method_stats


def cmd_status():
    cands = fetch_section_rich_books()
    print(f"Section-rich candidates (≥3 chunks with ≥3 section boundaries each): {len(cands)}")
    cands.sort(key=lambda c: -c["total_boundaries"])
    # Get titles for top 20
    ids = [c["id"] for c in cands[:30]]
    meta = {}
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        in_clause = ",".join(f'"{x}"' for x in batch)
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks?id=in.({in_clause})&select=id,title,file_type,subcategory",
            headers=se.H_GET, timeout=30).json()
        for row in r:
            meta[row["id"]] = row
    for c in cands[:20]:
        m = meta.get(c["id"], {})
        title = (m.get("title") or "?")[:50]
        print(f"  +{c['total_boundaries']:>4} bdry in {c['section_rich']:>3}/{c['n_chunks']:>4}  "
              f"{m.get('file_type'):<4}  {title}")


def cmd_run(book_id: str | None, do_all: bool, dry_run: bool):
    if book_id:
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks?id=eq.{book_id}"
            "&select=id,title,author,file_type,chunk_count,total_chars",
            headers=se.H_GET, timeout=30).json()
        if not r:
            print(f"⚠ ebook {book_id} not found", file=sys.stderr)
            sys.exit(1)
        books = r
    elif do_all:
        cands = fetch_section_rich_books()
        print(f"Found {len(cands)} section-rich candidates")
        # Pull metadata for all
        ids = [c["id"] for c in cands]
        books = []
        for i in range(0, len(ids), 50):
            batch = ids[i:i+50]
            in_clause = ",".join(f'"{x}"' for x in batch)
            r = requests.get(
                f"{se.URL}/rest/v1/ebooks?id=in.({in_clause})"
                "&select=id,title,author,file_type,chunk_count,total_chars",
                headers=se.H_GET, timeout=30).json()
            books.extend(r)
    else:
        print("Specify --book <id> or --all", file=sys.stderr)
        sys.exit(2)

    ok = 0
    skipped = 0
    failed = 0
    total_added = 0
    method_totals: dict[str, int] = {}
    for b in books:
        title = (b.get("title") or "?")[:55]
        try:
            n, err, stats = process_book(b, dry_run=dry_run)
        except Exception as e:
            print(f"  ✗ [{title}] exception: {str(e)[:160]}")
            failed += 1
            continue
        if err and err.startswith("skipped"):
            print(f"  · [{title}] {err}")
            skipped += 1
        elif err and "no chunks needed" in err:
            print(f"  · [{title}] {err}")
            skipped += 1
        elif err:
            print(f"  ⚠ [{title}] {err}")
            failed += 1
        else:
            method_summary = ", ".join(f"{k}:{v}" for k, v in stats.items())
            print(f"  ✓ [{title}] +{n} chunk(s)  [{method_summary}]")
            ok += 1
            total_added += n
            for k, v in stats.items():
                method_totals[k] = method_totals.get(k, 0) + v

    print(f"\nDone. OK: {ok}, Skipped: {skipped}, Failed: {failed}, new chunks: +{total_added}"
          f"{' (dry-run)' if dry_run else ''}")
    if method_totals:
        print(f"  Boundary methods used: {method_totals}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("status")
    pr = sub.add_parser("run")
    pr.add_argument("--book")
    pr.add_argument("--all", action="store_true")
    pr.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    if args.cmd == "status":
        cmd_status()
    elif args.cmd == "run":
        cmd_run(args.book, args.all, args.dry_run)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
