#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_set_volumes.py — Haiku-driven volume boundary detection for 套書 with no
volume metadata, so split_ebook_set.py can act on them.

For each target ebook:
  1. Read JSONL → build a TOC view (h2 headings + chunk_index)
  2. Ask Claude Haiku: is this multi-volume? if so, list (chunk_index, volume_title)
  3a. Multi-volume → rewrite JSONL with `volume` field on each chunk +
      push R2. Caller can then run `split_ebook_set.py run --book <id>`.
  3b. Single-volume → mark `ebooks.parse_error = NOT_A_SET_MARKER` so
      `split_ebook_set.py` excludes it from the candidate list.

Usage:
  python scripts/detect_set_volumes.py status                 # what would be processed
  python scripts/detect_set_volumes.py run --book <id>        # one book
  python scripts/detect_set_volumes.py run --book <id> --dry-run
  python scripts/detect_set_volumes.py run --all              # all 16 (one at a time)

Per `feedback_ocr_strategy.md` and the 2026-05-14 Haiku-bulk lesson, this
script processes books strictly one-at-a-time. Text-only Haiku is much cheaper
than vision OCR, so the rate-limit risk is lower, but we still sleep between
books to be polite.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import standardize_ebook as se
import standardize_pdf_lite as pl
from split_ebook_set import SET_TITLE_RX, SPLIT_MARKER, fetch_set_candidates, load_chunks

import requests

try:
    import anthropic as _anthropic
except ImportError:
    print("Missing anthropic. pip install anthropic", file=sys.stderr)
    sys.exit(1)


NOT_A_SET_MARKER = "not actually a 套書 — single volume"
HAIKU_MODEL = "claude-haiku-4-5-20251001"
HAIKU_MAX_TOKENS = 2048

# Headings that are obviously frontmatter / publisher boilerplate, never a
# volume boundary. We strip these BEFORE sending to Haiku to keep the prompt
# short and the LLM's job focused.
FRONTMATTER_HEADINGS = {
    "封面", "版權頁", "版權信息", "版权信息", "出版資訊", "出版资讯",
    "目錄", "目录", "總目錄", "总目录", "前置內容", "前置内容",
    "前言", "序", "序言", "緒言", "绪言", "總序", "总序", "導讀", "导读",
    "扉頁", "扉页", "書名頁", "书名页",
    "後記", "后记", "跋", "譯後記", "译后记", "再版譯序", "再版译序",
    "譯序", "译序", "編後記", "编后记",
    "附錄", "附录", "致謝", "致谢", "索引", "人名索引",
    "參考文獻", "参考文献", "文獻", "文献", "譯名對照表", "译名对照表",
    "專業術語漢英對照表", "专业术语汉英对照表", "評論文章", "评论文章",
    "叢書", "丛书", "漢譯世界學術名著叢書", "汉译世界学术名著丛书",
    "再版後記", "再版后记",
}

# Regex hints — chunk's first heading line starts with these → likely chapter, not volume
NON_VOLUME_HEADING_RX = re.compile(
    r"^(##\s*)?(\[\d+\]|\d+\.|第\d+節|第\d+节|第\d+章|第[一二三四五六七八九十百千]+節|第[一二三四五六七八九十百千]+节)"
)


def get_first_heading(chunk_content: str) -> tuple[int, str] | None:
    """Return (level, text) of the first heading in a chunk, or None."""
    if not chunk_content:
        return None
    m = re.search(r"^(#{1,4})\s+(.+?)(\r?\n|$)", chunk_content, re.M)
    if not m:
        return None
    return (len(m.group(1)), m.group(2).strip())


def build_toc(chunks: list[dict]) -> list[tuple[int, int, str]]:
    """Return [(chunk_index, heading_level, heading_text)] for chunks whose
    first line is a top-level (## / ###) heading and isn't obvious frontmatter."""
    out: list[tuple[int, int, str]] = []
    for i, c in enumerate(chunks):
        h = get_first_heading(c.get("content") or "")
        if not h:
            continue
        level, text = h
        if level > 3:
            continue  # h4+ are too granular for volume detection
        clean = text.replace("<u>", "").replace("</u>", "").strip()
        if clean in FRONTMATTER_HEADINGS:
            continue
        if NON_VOLUME_HEADING_RX.search(c.get("content") or ""):
            continue
        # Skip obvious footnote/citation chunks (start with [N] or numeric)
        if re.match(r"^\[\d+\]|^\d+\.\s", clean):
            continue
        # Skip very long titles — likely actual content fragments, not headings
        if len(clean) > 60:
            continue
        out.append((i, level, clean))
    return out


def ask_haiku(client, title: str, toc: list[tuple[int, int, str]]) -> dict:
    """Ask Haiku for volume boundaries. Returns parsed JSON dict."""
    toc_lines = []
    for ci, level, text in toc:
        prefix = "##" if level == 2 else "###"
        toc_lines.append(f"  [{ci}] {prefix} {text}")
    toc_str = "\n".join(toc_lines) if toc_lines else "  (no headings)"

    prompt = f"""You are analyzing the table of contents of an ebook titled "{title}".

The title suggests it's a multi-volume work (套書 / 全集 / 套裝 / 共N冊 / 共N卷 / N卷套裝), but the publisher EPUB may actually contain only ONE constituent volume.

TOC (chunk_index → markdown heading, frontmatter already filtered):
{toc_str}

Your task: Identify the VOLUME boundaries. A "volume" here means a constituent book within the set — e.g., one of the 6 卷 in 卡謬全集, or one of the 14 卷 in 世界佛教通史. It is NOT an internal chapter / section / essay.

Heuristics:
- A volume boundary typically marks a self-contained work — its own title, its own (publication year?), often followed by multiple chapters.
- "## 第一章 / 第二章 / 第N章" are CHAPTERS inside one volume, NOT volume boundaries.
- A 文集 / 全集 with N essays is a SINGLE-VOLUME work (the essays are chapters, not volumes).
- "卷" or "冊" or "編" or specific dated titles ("局外人（1942年）", "鼠疫（1947年）") often signal volume boundaries.
- If only ONE clear self-contained work appears (with introduction / chapters / appendix), this is single-volume even if the title says 全集.

Output ONLY a JSON object — no markdown fences, no commentary:

If multi-volume (≥2 distinct volumes detected):
{{"single_volume": false, "volumes": [{{"chunk_index": 5, "volume_title": "局外人"}}, {{"chunk_index": 6, "volume_title": "鼠疫"}}, ...]}}

If single-volume:
{{"single_volume": true, "reason": "short reason — e.g. 'all chapters of one 神學大全 volume'"}}"""

    resp = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=HAIKU_MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text if resp.content else ""
    # Strip possible markdown fences
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.I)
    text = re.sub(r"\s*```\s*$", "", text)
    return json.loads(text)


def rewrite_chunks_with_volume(chunks: list[dict], volumes: list[dict]) -> list[dict]:
    """Propagate volume_title to each chunk based on boundary chunk_index.

    - chunks before the first boundary → volume=None (folded into first vol by split logic)
    - chunks at and after boundary[i], before boundary[i+1] → volume=boundary[i].volume_title
    """
    if not volumes:
        return chunks
    # Sort boundaries by chunk_index ascending
    sorted_vols = sorted(volumes, key=lambda v: int(v["chunk_index"]))
    out = []
    for i, c in enumerate(chunks):
        nc = dict(c)
        # Find which volume bucket this chunk falls into
        current_vol = None
        for v in sorted_vols:
            if i >= int(v["chunk_index"]):
                current_vol = v["volume_title"]
            else:
                break
        nc["volume"] = current_vol
        out.append(nc)
    return out


def write_jsonl(ebook_id: str, chunks: list[dict]) -> Path:
    p = se.CHUNKS_DIR / f"{ebook_id}.jsonl"
    with p.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return p


def push_r2(ebook_id: str, jsonl_path: Path) -> None:
    pl.push_to_r2(ebook_id, jsonl_path)


def mark_not_a_set(ebook_id: str, reason: str) -> None:
    msg = f"{NOT_A_SET_MARKER}: {reason}"[:500]
    requests.patch(
        f"{se.URL}/rest/v1/ebooks?id=eq.{ebook_id}",
        headers=se.H_JSON, json={"parse_error": msg}, timeout=30,
    )


def make_client():
    api_key = se.ENV.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return _anthropic.Anthropic(api_key=api_key)
    cred = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", ""))) / ".claude" / ".credentials.json"
    if cred.exists():
        try:
            with cred.open(encoding="utf-8") as f:
                token = json.load(f).get("claudeAiOauth", {}).get("accessToken", "")
            if token:
                return _anthropic.Anthropic(auth_token=token)
        except Exception:
            pass
    raise RuntimeError("No Anthropic credentials")


def list_unsplittable() -> list[dict]:
    """Same logic as split_ebook_set.cmd_status, but returns the unsplittable list."""
    cands = fetch_set_candidates()
    out = []
    for b in cands:
        pe = b.get("parse_error") or ""
        if pe.startswith(SPLIT_MARKER) or pe.startswith(NOT_A_SET_MARKER):
            continue
        chunks = load_chunks(b["id"])
        if not chunks:
            continue
        n_with_vol = len(set(c.get("volume") for c in chunks if c.get("volume")))
        if n_with_vol >= 2:
            continue  # already splittable, skip
        out.append(b)
    return out


def process_one(client, book: dict, dry_run: bool = False) -> str:
    """Returns one-line status."""
    bid = book["id"]
    title = book.get("title") or "?"
    chunks = load_chunks(bid)
    if not chunks:
        return "  ✗ JSONL missing"

    toc = build_toc(chunks)
    print(f"    TOC has {len(toc)} candidate headings (after frontmatter filter)")

    if not toc:
        if not dry_run:
            mark_not_a_set(bid, "no h2/h3 headings outside frontmatter")
        return "  → marked NOT_A_SET (no usable headings)"

    try:
        result = ask_haiku(client, title, toc)
    except Exception as e:
        return f"  ✗ Haiku call failed: {str(e)[:160]}"

    if result.get("single_volume"):
        reason = (result.get("reason") or "single volume")[:200]
        if dry_run:
            return f"  → SINGLE-VOLUME: {reason}"
        mark_not_a_set(bid, reason)
        return f"  → marked NOT_A_SET ({reason})"

    volumes = result.get("volumes") or []
    if len(volumes) < 2:
        if not dry_run:
            mark_not_a_set(bid, f"Haiku found only {len(volumes)} volume(s)")
        return f"  → only {len(volumes)} volumes (treated as single)"

    # Validate chunk_index values
    valid = []
    for v in volumes:
        try:
            ci = int(v.get("chunk_index"))
        except (TypeError, ValueError):
            continue
        title_ = (v.get("volume_title") or "").strip()
        if 0 <= ci < len(chunks) and title_:
            valid.append({"chunk_index": ci, "volume_title": title_})
    if len(valid) < 2:
        return f"  ✗ Haiku output invalid: {result}"

    print(f"    Haiku identified {len(valid)} volumes:")
    for v in valid:
        print(f"      [{v['chunk_index']:3d}] {v['volume_title']}")

    if dry_run:
        return f"  → MULTI-VOLUME (dry-run, {len(valid)} volumes)"

    rewritten = rewrite_chunks_with_volume(chunks, valid)
    p = write_jsonl(bid, rewritten)
    try:
        push_r2(bid, p)
    except Exception as e:
        return f"  ⚠ JSONL rewritten locally but R2 push failed: {str(e)[:120]}"
    return f"  ✓ wrote volume field for {len(valid)} volumes, ready for split"


def cmd_status():
    books = list_unsplittable()
    print(f"Unsplittable 套書 candidates: {len(books)}")
    for b in books:
        print(f"  {b['title'][:70]}  id={b['id']}")


def cmd_run(book_id: str | None, do_all: bool, dry_run: bool):
    if book_id:
        r = requests.get(
            f"{se.URL}/rest/v1/ebooks?id=eq.{book_id}"
            "&select=id,title,author,file_type,file_path,category,subcategory,"
            "chunk_count,total_chars,parse_error",
            headers=se.H_GET, timeout=30).json()
        if not r:
            print(f"⚠ ebook {book_id} not found", file=sys.stderr)
            sys.exit(1)
        books = r
    elif do_all:
        books = list_unsplittable()
        print(f"Found {len(books)} unsplittable 套書 to inspect")
    else:
        print("Specify --book <id> or --all", file=sys.stderr)
        sys.exit(2)

    client = make_client()
    for i, b in enumerate(books, 1):
        print(f"\n[{i}/{len(books)}] {b['title'][:55]}  id={b['id']}")
        try:
            status = process_one(client, b, dry_run=dry_run)
        except Exception as e:
            status = f"  ✗ exception: {str(e)[:200]}"
        print(status)
        if i < len(books):
            time.sleep(2.0)  # gentle pacing


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
