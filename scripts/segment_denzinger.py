"""
Denzinger Phase-2 segmenter — page-level chunks → DH-indexed chunks.

Spec: .claude/skills/ebook-pipeline/book-structure-bilingual-parallel.md §4

Reads consolidated `_chunks/{id}.jsonl` (output of _denzinger_consolidate.py),
emits new chunks with bilingual-parallel schema:

  {
    chunk_index, chunk_type ('chapter' | 'section'),
    section_type ('header' | 'entry' | 'commentary'),
    chapter_path, content, source_text?, source_lang?='lat',
    dh_number?, dh_range?,
    page_number, page_numbers,
  }

⚠ This is a skeleton — regexes are first-cut drafts per the spec. Run with
   `--dry-run --report` after full OCR completes to see segmentation stats,
   then iterate before `--apply`.

Usage:
  python scripts/segment_denzinger.py --dry-run          # stats only
  python scripts/segment_denzinger.py --dry-run --report # + per-page sample dump
  python scripts/segment_denzinger.py --write-jsonl      # writes .bilingual.jsonl
  python scripts/segment_denzinger.py --apply            # DB + R2 + display_mode
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_with_gemini import (  # noqa: E402
    CHUNKS_DIR,
    URL,
    H,
    push_to_r2,
    update_book_done,
)
import requests  # noqa: E402
import shutil  # noqa: E402

BOOK_ID = "568726d3-967e-457a-ab69-7452b21d606f"
MAIN_JSONL = CHUNKS_DIR / f"{BOOK_ID}.jsonl"
BILINGUAL_JSONL = CHUNKS_DIR / f"{BOOK_ID}.bilingual.jsonl"
PRE_SEGMENT_BACKUP = CHUNKS_DIR / f"{BOOK_ID}.jsonl.presegment.bak"
# Column-aware re-OCR output. When present, overlays the page-level main
# JSONL — divider-formatted text takes precedence so the segmenter can
# split lat / zh deterministically instead of guessing line-by-line.
RECOLUMN_JSONL = CHUNKS_DIR / f"{BOOK_ID}.recolumn.jsonl"

# Divider markers emitted by _denzinger_recolumn_ocr.py
LAT_DIVIDER = "--- 拉丁文 ---"
ZH_DIVIDER = "--- 中譯 ---"

# ──────────────────────────────────────────────────────────────
# Regex / heuristic drafts (per spec §4 — validate against real OCR)
# ──────────────────────────────────────────────────────────────

# A DH marker is a 1-5 digit number at the start of a line, followed by a space
# and content starting with a *letter* (Latin / Greek / CJK / parenthesised symbol).
# The letter-start guard suppresses false positives like trailing page numbers or
# stray data digits while still allowing single-digit DH (DH 1-76 in Part I).
DH_MARKER = re.compile(
    r"(?m)^[ \t]*(\d{1,5})\s+"
    r"([A-Za-zÀ-ÿĀ-žΑ-Ωα-ω㐀-鿿豈-﫿（(《【「『‘“].*)"
)

# TOC artifacts — dot leaders (".....") + trailing page number
DOT_LEADER = re.compile(r"\.{5,}")
TOC_PAGE_HEADER = ("詳細目錄", "目錄")

# Section header patterns (block-level — match at line start)
SECTION_HEADER_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("會期", re.compile(r"^第\s*[一二三四五六七八九十\d]+\s*場?\s*會議")),
    ("教宗",     re.compile(r"^教宗\s*[一-鿿]{1,8}")),
    ("通諭名",   re.compile(r"^《[一-鿿\s]+》\s*通諭")),
    ("大公會議", re.compile(r"^[一-鿿]{2,8}大公會議")),
    ("拉特朗",   re.compile(r"^拉特朗\s*第?\s*[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ\d]+\s*次")),
    ("年代",     re.compile(r"^[一-鿿]{2,12}\s*\(\s*\d{3,4}[\-–]\d{3,4}\s*\)")),
]

# Commentary hints (within a block — case-insensitive substring)
COMMENTARY_HINTS = ["本選集", "【出版】", "【參考】", "cf. DH", "本書收錄", "編註"]

# CJK char detection — Unified Ideographs + common punctuation
CJK_RE = re.compile(r"[㐀-鿿豈-﫿]")


def cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    total = sum(1 for ch in text if not ch.isspace())
    if not total:
        return 0.0
    cjk = sum(1 for ch in text if CJK_RE.match(ch))
    return cjk / total


def classify_lang(text: str) -> str:
    """Return 'zh' (≥0.4 CJK), 'lat' (<0.1 CJK), 'mixed' otherwise."""
    r = cjk_ratio(text)
    if r >= 0.4:
        return "zh"
    if r < 0.1:
        return "lat"
    return "mixed"


def is_section_header(line: str) -> str | None:
    """Return the label of the matching header pattern, or None."""
    line = line.strip()
    if not line:
        return None
    for label, pat in SECTION_HEADER_PATTERNS:
        if pat.search(line):
            return label
    return None


def looks_like_commentary(text: str) -> bool:
    if any(hint in text for hint in COMMENTARY_HINTS):
        return True
    return False


def is_toc_page(content: str) -> bool:
    """Detect a 詳細目錄 page: explicit header text, OR ≥20% lines have dot
    leaders. Recolumn'd pages prefix the content with `--- 拉丁文 --- / ---
    中譯 ---` dividers, so we also peek inside the zh block."""
    head = content.lstrip()
    if any(head.startswith(h) for h in TOC_PAGE_HEADER):
        return True
    # Recolumn 詳細目錄 pages: zh column starts with 「詳細目錄」 marker.
    if ZH_DIVIDER in content:
        zh_block = content.split(ZH_DIVIDER, 1)[1].lstrip()
        if any(zh_block.startswith(h) for h in TOC_PAGE_HEADER):
            return True
    lines = [ln for ln in content.splitlines() if ln.strip()]
    if not lines:
        return False
    dot_lines = sum(1 for ln in lines if DOT_LEADER.search(ln))
    return dot_lines / len(lines) > 0.2


def looks_like_toc_entry(text: str) -> bool:
    """An 'entry' that's really a TOC line — has dot leader OR is one short line."""
    if DOT_LEADER.search(text):
        return True
    # Single-line + < 30 chars + no Latin = TOC pointer
    stripped = text.strip()
    if "\n" not in stripped and len(stripped) < 30 and classify_lang(stripped) == "zh":
        return True
    return False


# ──────────────────────────────────────────────────────────────
# Block extraction within a page
# ──────────────────────────────────────────────────────────────

# DH numbers 1-99 only exist in Part I (信經) which sits on PDF pp 75-114.
# Any "DH 1-99" appearing later in the book is a false positive — typically
# an enumeration inside a 39 Articles homily list, an appendix table row, or
# a footnote cf. — that DH_MARKER's letter-start guard cannot distinguish.
# We hard-gate by page number to filter those out.
DH_LOW_RANGE_MAX_PAGE = 115


_LATIN_GREEK_START = re.compile(r"^[A-ZΑ-Ω]")


def is_valid_dh(dh: int, pn: int | None, rest: str = "") -> bool:
    if dh < 100:
        if pn is None or pn >= DH_LOW_RANGE_MAX_PAGE:
            return False
        # Denzinger Part I creed entries always open the actual document
        # text with a Latin or Greek capital letter (Credo, Iesum,
        # Πιστεύομεν, etc.). A DH-marker followed by Chinese / lowercase /
        # punctuation is a stray "9 及第 10 篇" cross-reference inside
        # prose, not a real entry start.
        return bool(_LATIN_GREEK_START.match(rest.strip()))
    return True


def split_into_blocks(page_content: str, pn: int | None = None) -> list[dict]:
    """
    Walk the page text linewise. A new DH-marked line starts a new block.
    Any leading non-DH lines become a 'preamble' block. Returns blocks like:

      {kind: 'preamble' | 'dh', dh_number?: int, text: str, lang: 'zh'|'lat'|'mixed'}

    Headers are NOT split out here — that's phase 2 (cross-block).

    `pn` (page_number) is consulted to suppress DH 1-99 false positives that
    appear past 第一部分信經 — see DH_LOW_RANGE_MAX_PAGE.
    """
    lines = page_content.splitlines()
    blocks: list[dict] = []
    current: dict | None = None

    def flush():
        nonlocal current
        if current is not None:
            current["text"] = current["text"].rstrip()
            if current["text"]:
                current["lang"] = classify_lang(current["text"])
                blocks.append(current)
            current = None

    for ln in lines:
        m = DH_MARKER.match(ln)
        if m and is_valid_dh(int(m.group(1)), pn, m.group(2)):
            flush()
            dh = int(m.group(1))
            rest = m.group(2)
            current = {"kind": "dh", "dh_number": dh, "text": rest + "\n"}
        else:
            if current is None:
                current = {"kind": "preamble", "text": ""}
            current["text"] += ln + "\n"
    flush()
    return blocks


# ──────────────────────────────────────────────────────────────
# Phase 2/3: pair Latin+Chinese DH blocks, identify headers/commentary
# ──────────────────────────────────────────────────────────────

def _segment_divider_page(content: str, pn: int) -> list[dict] | None:
    """
    Column-aware re-OCR'd pages contain explicit `--- 拉丁文 ---` / `--- 中譯 ---`
    dividers. We split the page into two clean blocks and run DH detection
    inside each separately, then pair by DH number. Returns None when the
    dividers aren't present so caller falls through to the line-by-line
    classifier.
    """
    if LAT_DIVIDER not in content or ZH_DIVIDER not in content:
        return None

    # Split into [optional preamble] + [lat block] + [zh block]
    # We trust LAT_DIVIDER comes before ZH_DIVIDER (recolumn prompt guarantees it).
    after_lat = content.split(LAT_DIVIDER, 1)[1]
    lat_block, zh_block = after_lat.split(ZH_DIVIDER, 1)
    lat_block = lat_block.strip()
    zh_block = zh_block.strip()

    # If page has only one column (one side empty) — treat as commentary
    if not lat_block and not zh_block:
        return []
    if not lat_block and zh_block:
        # Commentary-only page
        return [{
            "section_type": "commentary",
            "chunk_type": "section",
            "chapter_path": "註解",
            "content": zh_block,
            "page_number": pn,
            "page_numbers": [pn],
        }]

    # Both columns present — find DH markers in each
    def by_dh_in_block(text: str) -> tuple[list[dict], dict[int, str]]:
        """Return (preamble_blocks, {dh: text}). Preamble = lines before
        the first DH marker — typically a section header or commentary
        intro for the column."""
        lines = text.splitlines()
        preamble_lines: list[str] = []
        by_dh: dict[int, list[str]] = {}
        cur_dh: int | None = None
        for ln in lines:
            m = DH_MARKER.match(ln)
            if m and is_valid_dh(int(m.group(1)), pn, m.group(2)):
                cur_dh = int(m.group(1))
                by_dh.setdefault(cur_dh, []).append(m.group(2))
            elif cur_dh is not None:
                by_dh[cur_dh].append(ln)
            else:
                preamble_lines.append(ln)
        preamble_text = "\n".join(preamble_lines).strip()
        preambles: list[dict] = []
        if preamble_text:
            preambles.append({"text": preamble_text, "lang": classify_lang(preamble_text)})
        return preambles, {d: "\n".join(ls).strip() for d, ls in by_dh.items()}

    lat_preambles, lat_by_dh = by_dh_in_block(lat_block)
    zh_preambles, zh_by_dh = by_dh_in_block(zh_block)

    out: list[dict] = []

    # Preambles → header (if matches section pattern) or commentary
    for p in (zh_preambles + lat_preambles):
        if len(p["text"].strip()) < 12:
            continue
        first_line = p["text"].strip().splitlines()[0]
        header_label = is_section_header(first_line)
        if header_label:
            out.append({
                "section_type": "header",
                "chunk_type": "chapter",
                "chapter_path": first_line[:35],
                "content": p["text"].strip(),
                "page_number": pn,
                "page_numbers": [pn],
            })
        elif p["lang"] == "zh" and len(p["text"].strip()) > 30:
            out.append({
                "section_type": "commentary",
                "chunk_type": "section",
                "chapter_path": "註解",
                "content": p["text"].strip(),
                "page_number": pn,
                "page_numbers": [pn],
            })

    # Entries: pair lat + zh by DH number (union of both sides)
    all_dhs = sorted(set(lat_by_dh) | set(zh_by_dh))
    for dh in all_dhs:
        lat = lat_by_dh.get(dh, "").strip()
        zh = zh_by_dh.get(dh, "").strip()
        if not lat and not zh:
            continue
        if (zh and looks_like_toc_entry(zh)) or (lat and looks_like_toc_entry(lat)):
            continue
        out.append({
            "section_type": "entry",
            "chunk_type": "section",
            "chapter_path": f"DH {dh}",
            "content": zh,
            "source_text": lat or None,
            "source_lang": "lat" if lat else None,
            "dh_number": dh,
            "page_number": pn,
            "page_numbers": [pn],
        })

    return out


def segment_page(page: dict) -> list[dict]:
    """
    Convert one page chunk → list of typed sub-chunks (without final chunk_index).
    Each sub-chunk carries page_number for later consolidation across pages.
    """
    pn = page["page_number"]

    # Short-circuit: 詳細目錄 / TOC pages emit ONE header chunk; no DH entries.
    # (Adjacent TOC pages get merged into one big TOC header by the cross-page pass.)
    if is_toc_page(page["content"]):
        return [{
            "section_type": "header",
            "chunk_type": "chapter",
            "chapter_path": "詳細目錄",
            "content": page["content"].strip(),
            "page_number": pn,
            "page_numbers": [pn],
        }]

    # Column-aware re-OCR'd page → divider-based deterministic split
    divider_out = _segment_divider_page(page["content"], pn)
    if divider_out is not None:
        return divider_out

    blocks = split_into_blocks(page["content"], pn=pn)

    out: list[dict] = []

    # Group DH blocks by number → at most one Latin + one Chinese block per DH
    by_dh: dict[int, dict[str, dict]] = {}  # dh → {lang: block}
    preambles: list[dict] = []
    for b in blocks:
        if b["kind"] == "dh":
            d = b["dh_number"]
            slot = by_dh.setdefault(d, {})
            # If a slot already taken (rare: same DH twice in same lang on one page),
            # concat — let downstream notice in --report.
            if b["lang"] in slot:
                slot[b["lang"]]["text"] += "\n" + b["text"]
            else:
                slot[b["lang"]] = b
        else:
            preambles.append(b)

    # Preambles: classify as 'header' (if any line matches section pattern) or
    # 'commentary' (mostly Chinese, has hints) or skipped (e.g. running headers)
    for p in preambles:
        # Drop if very short — likely OCR'd page header / numbering noise
        if len(p["text"].strip()) < 12:
            continue

        header_label = None
        for line in p["text"].splitlines():
            lbl = is_section_header(line)
            if lbl:
                header_label = lbl
                break

        if header_label:
            out.append({
                "section_type": "header",
                "chunk_type": "chapter",
                "chapter_path": p["text"].strip().splitlines()[0][:35],
                "content": p["text"].strip(),
                "page_number": pn,
                "page_numbers": [pn],
            })
        elif p["lang"] == "zh" and (looks_like_commentary(p["text"])
                                     or len(p["text"].strip()) > 50):
            out.append({
                "section_type": "commentary",
                "chunk_type": "section",
                "chapter_path": "註解",
                "content": p["text"].strip(),
                "page_number": pn,
                "page_numbers": [pn],
            })
        # else: skip noise

    # Entries: emit one per DH number on this page
    for dh in sorted(by_dh.keys()):
        slot = by_dh[dh]
        lat = slot.get("lat", {}).get("text", "").strip()
        zh = slot.get("zh", {}).get("text", "").strip()
        mixed = slot.get("mixed", {}).get("text", "").strip()

        # If only mixed, try to split — fallback: put whole thing in content
        if not lat and not zh and mixed:
            # The simplest heuristic: line-by-line classify
            lat_lines, zh_lines = [], []
            for ln in mixed.splitlines():
                if classify_lang(ln) == "zh":
                    zh_lines.append(ln)
                elif classify_lang(ln) == "lat":
                    lat_lines.append(ln)
                else:
                    # short / mixed line: send to zh by default
                    zh_lines.append(ln)
            lat = "\n".join(lat_lines).strip()
            zh = "\n".join(zh_lines).strip()

        # Backstop: drop TOC-shaped entry stragglers (any block w/ dot leaders)
        if (zh and looks_like_toc_entry(zh)) or (lat and looks_like_toc_entry(lat)):
            continue

        out.append({
            "section_type": "entry",
            "chunk_type": "section",
            "chapter_path": f"DH {dh}",
            "content": zh,
            "source_text": lat or None,
            "source_lang": "lat" if lat else None,
            "dh_number": dh,
            "page_number": pn,
            "page_numbers": [pn],
        })

    return out


# ──────────────────────────────────────────────────────────────
# Cross-page consolidation
# ──────────────────────────────────────────────────────────────

def consolidate_across_pages(per_page: list[list[dict]]) -> list[dict]:
    """
    Cross-page rules:
    - Adjacent same-DH entries (entry spilled across pages) → merge content,
      append page_number to page_numbers
    - Adjacent commentary→commentary → merge
    - **Entry → commentary fold**: if a commentary directly follows an entry
      with no header break, treat the commentary's Chinese prose as the
      entry's `content` (Denzinger lists the original text under the DH
      number, then the Chinese intro/translation in a follow-on paragraph).
      Eliminates the「DH 11 国王... · 註解」sidebar duplicate that just
      truncates back to「DH 11 国王...」, AND fills the empty `content`
      that makes the reader's 中-mode look blank.

    Returns a single flat list with chunk_index 0..N-1.
    """
    flat: list[dict] = []
    for page_chunks in per_page:
        for ch in page_chunks:
            if flat:
                last = flat[-1]
                last_sec = last.get("section_type")
                cur_sec = ch.get("section_type")

                # entry-entry merge if same DH
                if (last_sec == cur_sec == "entry"
                        and last.get("dh_number") == ch.get("dh_number")):
                    if ch.get("content"):
                        last["content"] = (last.get("content", "") + "\n" + ch["content"]).strip()
                    if ch.get("source_text"):
                        last["source_text"] = ((last.get("source_text") or "") + "\n"
                                                + ch["source_text"]).strip()
                    last["page_numbers"].extend(ch["page_numbers"])
                    continue

                # entry → commentary fold: commentary's zh becomes entry's content
                if last_sec == "entry" and cur_sec == "commentary":
                    com_text = (ch.get("content") or "").strip()
                    if com_text:
                        last["content"] = (last.get("content", "") + "\n" + com_text).strip() \
                            if last.get("content") else com_text
                    last["page_numbers"].extend(ch["page_numbers"])
                    continue

                # commentary-commentary merge
                if last_sec == cur_sec == "commentary":
                    last["content"] = (last.get("content", "") + "\n" + ch["content"]).strip()
                    last["page_numbers"].extend(ch["page_numbers"])
                    continue

                # header-header merge if same chapter_path (e.g. 詳細目錄 spans pages)
                if (last_sec == cur_sec == "header"
                        and last.get("chapter_path") == ch.get("chapter_path")):
                    last["content"] = (last.get("content", "") + "\n\n" + ch["content"]).strip()
                    last["page_numbers"].extend(ch["page_numbers"])
                    continue

            flat.append(dict(ch))

    # Renumber chunk_index, dedupe page_numbers
    for i, ch in enumerate(flat):
        ch["chunk_index"] = i
        ch["page_numbers"] = sorted(set(ch.get("page_numbers", [])))
    return flat


# ──────────────────────────────────────────────────────────────
# Orchestration
# ──────────────────────────────────────────────────────────────

def load_pages(path: Path) -> list[dict]:
    out: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    out.sort(key=lambda c: c.get("page_number", 0))
    return out


def overlay_recolumn(pages: list[dict]) -> int:
    """When `_chunks/{id}.recolumn.jsonl` exists, replace the content of
    each page present in it with the column-aware re-OCR'd version, and
    INJECT new page records for recolumn pages that are missing from
    `pages` (e.g. originals OCR'd as blank). Returns the count of pages
    touched (overlaid + injected). Idempotent — last-write-wins if the
    same page appears twice in recolumn."""
    if not RECOLUMN_JSONL.exists():
        return 0
    latest: dict[int, str] = {}
    with RECOLUMN_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            pn = o.get("page_number")
            content = (o.get("content") or "").strip()
            if isinstance(pn, int) and content:
                latest[pn] = content
    if not latest:
        return 0
    existing: set[int] = set()
    n = 0
    for p in pages:
        pn = p.get("page_number")
        if isinstance(pn, int):
            existing.add(pn)
            if pn in latest:
                p["content"] = latest[pn]
                p["_recolumn"] = True
                n += 1
    injected = 0
    for pn, content in sorted(latest.items()):
        if pn in existing:
            continue
        pages.append({
            "page_number": pn,
            "content": content,
            "chunk_type": "page",
            "section_type": "page",
            "_recolumn": True,
            "_injected": True,
        })
        injected += 1
        n += 1
    if injected:
        pages.sort(key=lambda c: c.get("page_number", 0))
        print(f"  [overlay_recolumn] injected {injected} recolumn-only pages "
              f"(absent from main JSONL)")
    return n


def report_stats(flat: list[dict], per_page_counts: list[int]) -> None:
    type_counter = Counter(c["section_type"] for c in flat)
    dh_numbers = [c["dh_number"] for c in flat
                  if c.get("section_type") == "entry" and c.get("dh_number")]
    entries_with_zh = sum(1 for c in flat
                          if c["section_type"] == "entry" and (c.get("content") or "").strip())
    entries_with_lat = sum(1 for c in flat
                           if c["section_type"] == "entry" and (c.get("source_text") or "").strip())

    print("\n=== Segmenter stats ===")
    print(f"Total emitted chunks   : {len(flat)}")
    for k, v in type_counter.items():
        print(f"  {k:11s}: {v}")
    print(f"Entries w/ Chinese     : {entries_with_zh}")
    print(f"Entries w/ Latin       : {entries_with_lat}")
    if dh_numbers:
        print(f"DH range observed      : {min(dh_numbers)} – {max(dh_numbers)}")
        # Detect non-monotonic
        out_of_order = sum(1 for a, b in zip(dh_numbers, dh_numbers[1:]) if b < a)
        print(f"Non-monotonic adjacent : {out_of_order}")
        dupes = [n for n, c in Counter(dh_numbers).items() if c > 1]
        print(f"Duplicate DH numbers   : {len(dupes)} (e.g. {dupes[:5]})")
    # Pages with zero emitted chunks (suspicious)
    zero_pages = sum(1 for n in per_page_counts if n == 0)
    print(f"Pages with 0 emissions : {zero_pages} (legitimately blank or regex miss)")


def sample_dump(flat: list[dict], n: int = 5) -> None:
    print("\n=== Sample emitted chunks (first N of each type) ===")
    seen: Counter = Counter()
    for ch in flat:
        st = ch["section_type"]
        if seen[st] >= n:
            continue
        seen[st] += 1
        print(f"\n--- [{st}] chunk_index={ch['chunk_index']} "
              f"page_numbers={ch['page_numbers']} dh={ch.get('dh_number')} ---")
        print(f"chapter_path: {ch['chapter_path']}")
        c = (ch.get("content") or "")
        s = (ch.get("source_text") or "")
        print(f"content[:120]: {c[:120].replace(chr(10), ' ⏎ ')}")
        if s:
            print(f"source_text[:120]: {s[:120].replace(chr(10), ' ⏎ ')}")


def write_jsonl(path: Path, flat: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for ch in flat:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")


def update_display_mode(mode: str) -> None:
    r = requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{BOOK_ID}",
        headers=H,
        json={"display_mode": mode},
        timeout=30,
    )
    if r.status_code >= 300:
        raise RuntimeError(f"display_mode patch failed: {r.status_code} {r.text[:200]}")


def replace_db_chunks(flat: list[dict]) -> None:
    """Replace ebook_chunks rows for this book with full segmented chunks
    (full content, not previews — bilingual reader fetches from DB)."""
    # PostgREST bulk insert requires every object in the array to expose the
    # same set of keys (PGRST102). Build rows with a fixed key set; populate
    # missing bilingual fields as null/None.
    rows = []
    for ch in flat:
        rows.append({
            "ebook_id": BOOK_ID,
            "chunk_index": ch["chunk_index"],
            "chunk_type": ch["chunk_type"],
            "page_number": ch.get("page_number"),
            "chapter_path": ch.get("chapter_path"),
            "content": ch.get("content") or "",
            "char_count": len((ch.get("content") or "")) + len((ch.get("source_text") or "")),
            "section_type": ch.get("section_type"),
            "source_text": ch.get("source_text"),
            "source_lang": ch.get("source_lang"),
            "dh_number": ch.get("dh_number"),
            "page_numbers": ch.get("page_numbers"),
        })

    requests.delete(
        f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{BOOK_ID}",
        headers=H,
        timeout=30,
    )

    # Adaptive batching — Supabase free tier hits statement timeout (57014)
    # at 50-row batches when each row holds ~2KB of mixed Latin/Chinese text.
    # Step down to smaller batches on timeout, same recipe as
    # ocr_with_gemini.insert_chunk_previews.
    BATCH_SIZES = [25, 10, 5, 1]
    i = 0
    inserted = 0
    while i < len(rows):
        for bs in BATCH_SIZES:
            batch = rows[i:i + bs]
            r = requests.post(
                f"{URL}/rest/v1/ebook_chunks",
                headers=H,
                json=batch,
                timeout=120,
            )
            if r.status_code in (200, 201):
                i += len(batch)
                inserted += len(batch)
                if inserted % 200 == 0 or i == len(rows):
                    print(f"  inserted {inserted}/{len(rows)}", flush=True)
                break
            # Unknown-column / schema-cache → re-raise with helpful DDL.
            if "PGRST204" in r.text or "schema cache" in r.text:
                raise RuntimeError(
                    f"ebook_chunks missing bilingual columns. Add a migration:\n"
                    f"  ALTER TABLE ebook_chunks ADD COLUMN section_type text;\n"
                    f"  ALTER TABLE ebook_chunks ADD COLUMN source_text text;\n"
                    f"  ALTER TABLE ebook_chunks ADD COLUMN source_lang text;\n"
                    f"  ALTER TABLE ebook_chunks ADD COLUMN dh_number int;\n"
                    f"  ALTER TABLE ebook_chunks ADD COLUMN page_numbers int[];\n"
                    f"DB error was: {r.text[:300]}"
                )
            # 57014 = statement timeout. Retry smaller batch.
            if "57014" in r.text or "timeout" in r.text.lower() or r.status_code >= 500:
                if bs > BATCH_SIZES[-1]:
                    continue
            raise RuntimeError(f"insert failed at batch_size={bs}, row {i}: "
                               f"{r.status_code} {r.text[:200]}")
        else:
            raise RuntimeError(f"insert failed at batch_size=1, row {i}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", action="store_true", help="with --dry-run, dump samples")
    ap.add_argument("--write-jsonl", action="store_true",
                    help="write _chunks/{id}.bilingual.jsonl (no DB / R2)")
    ap.add_argument("--apply", action="store_true",
                    help="write DB + R2 + display_mode='bilingual-parallel'")
    args = ap.parse_args()

    # On re-runs after a prior --apply, MAIN_JSONL is already segmented (it got
    # overwritten with the bilingual chunks so dev reads match prod). Prefer the
    # presegment backup as the page-level source when it exists, so re-running
    # this script is idempotent — never re-segment already-segmented output.
    source = PRE_SEGMENT_BACKUP if PRE_SEGMENT_BACKUP.exists() else MAIN_JSONL
    if not source.exists():
        print(f"ERROR: page-level JSONL missing: {source}", file=sys.stderr)
        print("Run scripts/_denzinger_consolidate.py first.", file=sys.stderr)
        return 1

    pages = load_pages(source)
    print(f"Loaded {len(pages)} page chunks from {source.name}")

    overlaid = overlay_recolumn(pages)
    if overlaid:
        print(f"Overlaid {overlaid} pages from {RECOLUMN_JSONL.name} "
              f"(divider-aware segmentation enabled)")

    per_page = [segment_page(p) for p in pages]
    per_page_counts = [len(x) for x in per_page]
    flat = consolidate_across_pages(per_page)

    report_stats(flat, per_page_counts)
    if args.report:
        sample_dump(flat)

    if args.dry_run and not args.write_jsonl and not args.apply:
        print("\n[DRY RUN] no writes.")
        return 0

    if args.write_jsonl or args.apply:
        write_jsonl(BILINGUAL_JSONL, flat)
        print(f"\nWrote {BILINGUAL_JSONL}  ({len(flat)} chunks)")

    if args.apply:
        # Replace main .jsonl with bilingual content so dev (local) and prod (R2)
        # see the same segmented chunks. Backup the page-level main once.
        if MAIN_JSONL.exists() and not PRE_SEGMENT_BACKUP.exists():
            shutil.copyfile(MAIN_JSONL, PRE_SEGMENT_BACKUP)
            print(f"Backed up page-level main → {PRE_SEGMENT_BACKUP.name}")
        tmp = MAIN_JSONL.with_suffix(".jsonl.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            for ch in flat:
                f.write(json.dumps(ch, ensure_ascii=False) + "\n")
        tmp.replace(MAIN_JSONL)
        print(f"Overwrote main JSONL with bilingual segmented chunks: {MAIN_JSONL.name}")

        try:
            push_to_r2(BOOK_ID, MAIN_JSONL)
            print("✓ R2 push ok (bilingual JSONL replaces standard at R2 key)")
        except Exception as e:
            print(f"⚠ R2 push failed: {str(e)[:200]}", file=sys.stderr)
            return 2

        replace_db_chunks(flat)
        print(f"✓ ebook_chunks replaced with {len(flat)} segmented rows")

        update_display_mode("bilingual-parallel")
        print("✓ ebooks.display_mode = 'bilingual-parallel'")

        # Sync ebooks.chunk_count / total_chars with the segmented count.
        total_chars = sum(len((c.get("content") or "")) + len((c.get("source_text") or ""))
                          for c in flat)
        total_pages = max(
            (max(c.get("page_numbers") or [c.get("page_number") or 0]) for c in flat),
            default=0,
        )
        update_book_done(
            BOOK_ID,
            total_chars=total_chars,
            chunk_count=len(flat),
            total_pages=total_pages,
        )
        print(f"✓ ebooks row updated: chunk_count={len(flat)}, "
              f"total_chars={total_chars:,}, total_pages={total_pages}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
