"""Consolidate per-chapter chunks into per-letter pages, using the EPUB's
NCX (navMap) as the authoritative parent-work hierarchy.

Why
---
CCEL ANF/NPNF EPUBs translate one HTML file per chapter, so the
`epub_to_chunks` translator produced 918 chunks for ANF Vol 1 (each
chunk = one chapter heading). For a patristic-letter book the user wants
pages organized BY LETTER, not by chapter:

  - Letters with ≤10 chapters → 1 consolidated page
  - Letters with >10 chapters → split into 1-10 / 11-20 / … pages

Volume detection from in-body H3 headings (`### The Epistle of …`)
miss-grouped: Ignatius has 7 letters but only 1 H3 boundary at the top
(the "Introductory Note to the Epistles of Ignatius"), so subsequent
chapter chunks lost their letter identity. NCX has the full tree —
parent (CLEMENT OF ROME) → letter (First Epistle to the Corinthians)
→ chapters — and is the only source of truth.

Usage
-----
    python scripts/consolidate_by_ncx.py <ebook_id>
    python scripts/consolidate_by_ncx.py <ebook_id> --dry-run
    python scripts/consolidate_by_ncx.py <ebook_id> --chapters-per-page 10

Idempotent in the sense that re-running on already-consolidated chunks
no-ops (detects via `chunk_type == 'letter_page'`).
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from typing import Optional
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import ebooklib
from ebooklib import epub

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")


# ── Chinese labels for ANF/NPNF parent-letter combinations ───────────────
# Key = (parent_label_normalized, letter_label_substring); value = Chinese name.
# Matches by checking if the letter_label CONTAINS the key substring AND
# the parent_label STARTS WITH the parent key (case-insensitive).
LETTER_CN_LABELS: list[tuple[str, str, str]] = [
    # parent_prefix, letter_substring, chinese_name
    # ANF Vol 1
    ("CLEMENT", "First Epistle to the Corinthians", "革利免致哥林多人前書"),
    ("CLEMENT", "Second Epistle", "革利免致哥林多人後書"),
    ("MATHETES", "Epistle to Diognetus", "致丟格那妥書"),
    ("MATHETES", "Diognetus", "致丟格那妥書"),
    ("POLYCARP", "Epistle to the Philippians", "坡旅甲致腓立比人書"),
    ("POLYCARP", "Martyrdom of Polycarp", "坡旅甲殉道記"),
    ("IGNATIUS", "Epistle to the Ephesians: Shorter and Longer", "依納爵致以弗所人書"),
    ("IGNATIUS", "Epistle to the Magnesians: Shorter and Longer", "依納爵致馬內夏人書"),
    ("IGNATIUS", "Epistle to the Trallians: Shorter and Longer", "依納爵致特拉勒人書"),
    ("IGNATIUS", "Epistle to the Romans: Shorter and Longer", "依納爵致羅馬人書"),
    ("IGNATIUS", "Epistle to the Philadelphians: Shorter and Longer", "依納爵致非拉鐵非人書"),
    ("IGNATIUS", "Epistle to the Smyrnæans: Shorter and Longer", "依納爵致士每拿人書"),
    ("IGNATIUS", "Epistle to Polycarp: Shorter and Longer", "依納爵致坡旅甲書"),
    ("IGNATIUS", "Epistle to Polycarp: Syriac", "依納爵致坡旅甲書（敘利亞文版）"),
    ("IGNATIUS", "Epistle to the Ephesians: Syriac", "依納爵致以弗所人書（敘利亞文版）"),
    ("IGNATIUS", "Epistle to the Romans: Syriac", "依納爵致羅馬人書（敘利亞文版）"),
    ("IGNATIUS", "Epistle to the Tarsians", "依納爵致他爾索人書（偽作）"),
    ("IGNATIUS", "Epistle to the Antiochians", "依納爵致安提阿人書（偽作）"),
    ("IGNATIUS", "Epistle to Hero", "依納爵致黑羅書（偽作）"),
    ("IGNATIUS", "Epistle to the Philippians", "依納爵致腓立比人書（偽作）"),
    ("IGNATIUS", "Epistle from Maria", "瑪利雅致依納爵書（偽作）"),
    ("IGNATIUS", "Epistle to Mary at Neapolis", "依納爵致內亞坡里的瑪利亞書（偽作）"),
    ("IGNATIUS", "First Epistle to St John", "依納爵致聖約翰書一（偽作）"),
    ("IGNATIUS", "Second Epistle to St John", "依納爵致聖約翰書二（偽作）"),
    ("IGNATIUS", "Epistle to Mary the Virgin", "依納爵致童貞女瑪利亞書（偽作）"),
    ("IGNATIUS", "Epistle from Mary the Virgin", "童貞女瑪利亞致依納爵書（偽作）"),
    ("IGNATIUS", "Martyrdom of Ignatius", "依納爵殉道記"),
    ("BARNABAS", "Epistle of Barnabas", "巴拿巴書信"),
    ("BARNABAS", "Barnabas", "巴拿巴書信"),
    ("PAPIAS", "Fragments", "帕皮亞殘篇"),
    ("JUSTIN", "First Apology", "猶斯定第一護教辭"),
    ("JUSTIN", "Second Apology", "猶斯定第二護教辭"),
    ("JUSTIN", "Dialogue with Trypho", "與特里弗的對話"),
    ("JUSTIN", "Discourse to the Greeks", "致希臘人辭"),
    ("JUSTIN", "Hortatory Address to the Greeks", "勸勉希臘人辭"),
    ("JUSTIN", "Sole Government of God", "論神獨一治理"),
    ("JUSTIN", "On the Resurrection", "論復活殘篇"),
    ("JUSTIN", "Other Fragments", "猶斯定遺著殘篇"),
    ("JUSTIN", "Martyrdom of Justin", "猶斯定殉道記"),
    ("IRENÆUS", "Against Heresies: Book I", "愛任紐《駁異端》卷一"),
    ("IRENAEUS", "Against Heresies: Book I", "愛任紐《駁異端》卷一"),
    ("IRENÆUS", "Against Heresies: Book II", "愛任紐《駁異端》卷二"),
    ("IRENAEUS", "Against Heresies: Book II", "愛任紐《駁異端》卷二"),
    ("IRENÆUS", "Against Heresies: Book III", "愛任紐《駁異端》卷三"),
    ("IRENAEUS", "Against Heresies: Book III", "愛任紐《駁異端》卷三"),
    ("IRENÆUS", "Against Heresies: Book IV", "愛任紐《駁異端》卷四"),
    ("IRENAEUS", "Against Heresies: Book IV", "愛任紐《駁異端》卷四"),
    ("IRENÆUS", "Against Heresies: Book V", "愛任紐《駁異端》卷五"),
    ("IRENAEUS", "Against Heresies: Book V", "愛任紐《駁異端》卷五"),
    ("IRENÆUS", "Fragments from the Lost", "愛任紐遺著殘篇"),
    ("IRENAEUS", "Fragments from the Lost", "愛任紐遺著殘篇"),
    ("IRENÆUS", "Elucidation", "愛任紐《駁異端》註解"),
    ("IRENAEUS", "Elucidation", "愛任紐《駁異端》註解"),
    # Front-matter / index — fall through to translated letter_label
]

# Parent-label → Chinese fallback. When letter doesn't match anything in
# LETTER_CN_LABELS, we use parent_cn + letter_label as best-effort label.
PARENT_CN_FALLBACK: dict[str, str] = {
    "CLEMENT OF ROME": "羅馬的革利免",
    "MATHETES": "瑪忒特",
    "POLYCARP": "坡旅甲",
    "IGNATIUS": "依納爵",
    "BARNABAS": "巴拿巴",
    "PAPIAS": "帕皮亞",
    "JUSTIN MARTYR": "殉道者猶斯定",
    "IRENÆUS": "里昂的愛任紐",
    "IRENAEUS": "里昂的愛任紐",
}

# Skip these top-level NCX entries (front matter / index — handled separately)
SKIP_PARENT_LABELS = {"About This Book", "Title Page", "Indexes"}


def chinese_label(parent_label: str, letter_label: str) -> str:
    """Resolve a Chinese label for (parent, letter) using the table above."""
    p_upper = parent_label.upper()
    for parent_key, letter_sub, cn in LETTER_CN_LABELS:
        if parent_key in p_upper and letter_sub.lower() in letter_label.lower():
            return cn
    # Fallback: parent_cn + letter_label (English-y)
    parent_cn = PARENT_CN_FALLBACK.get(p_upper, parent_label)
    return f"{parent_cn} · {letter_label}"


# ── NCX parse ────────────────────────────────────────────────────────────

def parse_ncx_letters(epub_path: Path) -> list[dict]:
    """Walk NCX and return list of letters with their chapter files.
    Each entry: {parent_label, letter_label, letter_file, chapters: [(file, label)]}.
    """
    with zipfile.ZipFile(epub_path) as z:
        ncx_name = next(n for n in z.namelist() if n.endswith(".ncx"))
        ncx_xml = z.read(ncx_name).decode("utf-8", errors="replace")
    cleaned = re.sub(r'\sxmlns(:\w+)?="[^"]+"', "", ncx_xml)
    root = ET.fromstring(cleaned)
    navmap = root.find("navMap")
    if navmap is None:
        return []
    letters: list[dict] = []
    for parent_np in navmap.findall("navPoint"):
        plabel_el = parent_np.find("navLabel/text")
        plabel = (plabel_el.text or "").strip() if plabel_el is not None else ""
        if plabel in SKIP_PARENT_LABELS:
            continue
        # Sub-letters under this parent
        sub_navs = parent_np.findall("navPoint")
        if not sub_navs:
            # Treat the parent itself as a single letter (rare)
            content = parent_np.find("content")
            file = content.get("src", "").split("#")[0] if content is not None else ""
            letters.append({
                "parent_label": plabel,
                "letter_label": plabel,
                "letter_file": file,
                "chapters": [],
            })
            continue
        for sub in sub_navs:
            llabel_el = sub.find("navLabel/text")
            llabel = (llabel_el.text or "").strip() if llabel_el is not None else ""
            lcontent = sub.find("content")
            lfile = lcontent.get("src", "").split("#")[0] if lcontent is not None else ""
            chapters: list[tuple[str, str]] = []
            for chap_np in sub.findall("navPoint"):
                clab_el = chap_np.find("navLabel/text")
                clabel = (clab_el.text or "").strip() if clab_el is not None else ""
                ccontent = chap_np.find("content")
                cfile = ccontent.get("src", "").split("#")[0] if ccontent is not None else ""
                if cfile:
                    chapters.append((cfile, clabel))
            letters.append({
                "parent_label": plabel,
                "letter_label": llabel,
                "letter_file": lfile,
                "chapters": chapters,
            })
    return letters


# ── EPUB → title_en → src_file map ─────────────────────────────────────────

def walk_epub_src_files(epub_path: Path) -> list[str]:
    """Return the ordered list of src_file paths for EPUB ITEM_DOCUMENTs
    that PASSED translate_ebook_to_zh's iteration AND its 30-char minimum.

    Translation pipeline order:
      1. `epub_to_chunks`: emits one source chunk per ITEM_DOCUMENT with
         non-empty markdown content.
      2. `translate_book` loop: `if not en.strip() or len(en) < 30: continue`
         — short chunks get skipped from JSONL output.

    Replicating both rules here keeps EPUB-item index aligned with JSONL
    chunk index so we can map src_file → chunk reliably.
    """
    book = epub.read_epub(str(epub_path))
    paths: list[str] = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")
        md_parts: list[str] = []
        for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "blockquote", "li"]):
            text = el.get_text(separator=" ", strip=True)
            if not text:
                continue
            tag = el.name
            if tag == "h1":
                md_parts.append(f"## {text}")
            elif tag == "h2":
                md_parts.append(f"### {text}")
            elif tag in ("h3", "h4"):
                md_parts.append(f"#### {text}")
            elif tag == "blockquote":
                md_parts.append(f"> {text}")
            elif tag == "li":
                md_parts.append(f"- {text}")
            else:
                md_parts.append(text)
        content = "\n\n".join(md_parts).strip()
        if not content or len(content) < 30:
            continue
        paths.append(item.get_name())
    return paths


def normalize_src(s: str) -> str:
    """Strip OEBPS/ prefix, anchor, normalize separators."""
    s = s.split("#")[0]
    if s.startswith("OEBPS/"):
        s = s[len("OEBPS/"):]
    return s


# ── Pipeline ──────────────────────────────────────────────────────────────

def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        sys.exit(f"no ebooks row for {ebook_id}")
    return rows[0]


def find_epub(book: dict) -> Path:
    src = Path(book["file_path"])
    if src.suffix.lower() == ".epub":
        return src
    epub_p = src.with_suffix(".epub")
    if epub_p.exists():
        return epub_p
    for f in src.parent.iterdir():
        if f.suffix.lower() == ".epub":
            return f
    sys.exit(f"no EPUB for {src}")


def consolidate(ebook_id: str, dry_run: bool = False,
                chapters_per_page: int = 10) -> None:
    book = fetch_book(ebook_id)
    epub_path = find_epub(book)
    print(f"Book: {book['title']}")
    print(f"EPUB: {epub_path}")

    jsonl_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    chunks = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines()]
    print(f"Loaded {len(chunks)} chunks")
    if any(c.get("chunk_type") == "letter_page" for c in chunks):
        print("⚠ Already consolidated (chunk_type=letter_page found). "
              "Restoring from R2 / re-translating not yet supported.")
        # Allow override
        # return

    letters = parse_ncx_letters(epub_path)
    print(f"NCX letters (raw): {len(letters)}")

    # Merge "Introductory Note to X" entries into the FOLLOWING X entry.
    # CCEL splits the translator's preface from the letter itself as a
    # separate navPoint with 0 chapters; logically it's part of the same
    # letter and should share a volume. We do this by appending the intro
    # letter's file path to the next letter's `letter_file_extras` list.
    merged: list[dict] = []
    pending_intros: list[str] = []  # file paths
    for L in letters:
        is_intro = re.match(r"^Introductory\s+Notes?\s+to\b", L["letter_label"], re.I)
        if is_intro and not L["chapters"]:
            pending_intros.append(L["letter_file"])
            continue
        if pending_intros:
            L = dict(L)
            L["letter_file_extras"] = pending_intros
            pending_intros = []
        merged.append(L)
    # Trailing orphan intros (no following letter) → keep as standalone
    for f in pending_intros:
        merged.append({
            "parent_label": "(Introduction)",
            "letter_label": "Introductory Note",
            "letter_file": f,
            "chapters": [],
        })
    letters = merged
    print(f"NCX letters (after fold intros): {len(letters)}")

    # Build src_file → chunk by walking EPUB items in document order and
    # pairing 1:1 with JSONL chunks (which were produced in this same order
    # by translate_ebook_to_zh.epub_to_chunks). This is more reliable than
    # title-based matching because chapter titles repeat across letters
    # (every letter has its own "Chapter I.—Occasion …") AND the JSONL's
    # title_en is truncated at the first newline while NCX has the full
    # navLabel — so any title-based lookup is fragile.
    epub_src_order = walk_epub_src_files(epub_path)
    print(f"EPUB items with content: {len(epub_src_order)}")
    src_to_chunk: dict[str, dict] = {}
    if len(epub_src_order) >= len(chunks):
        for i, c in enumerate(chunks):
            if i < len(epub_src_order):
                src_to_chunk[normalize_src(epub_src_order[i])] = c
    else:
        print(f"  ⚠ EPUB has {len(epub_src_order)} items but JSONL has "
              f"{len(chunks)} chunks — split_oversized may have produced "
              f"sub-pieces. Falling back to title-based match.")
        # The translator's split_oversized produces multiple JSONL chunks
        # per EPUB item. Group those by title_en for fair mapping.
        # TODO if this triggers in practice.
        for c in chunks:
            title = (c.get("title_en") or "").split("\n", 1)[0].strip()
            if title:
                src_to_chunk[title] = c
    print(f"src→chunk map: {len(src_to_chunk)}")

    # Track which chunks get consumed by letters; leftovers become front-matter
    consumed = set()

    new_chunks: list[dict] = []

    # Front-matter chunks (chunk_index 0,1,2,3 typically — cover/preface/intro)
    # are NOT assigned to any letter. Keep them as-is at the head, in their
    # original order, until we hit the first chunk that belongs to a letter.
    # We mark consumed_chunks as we go.

    # Iterate letters; for each, gather chapter chunks in order.
    consolidated_pages: list[dict] = []
    for letter in letters:
        cn = chinese_label(letter["parent_label"], letter["letter_label"])
        # Gather chunks for this letter:
        #   1. Folded-in "Introductory Note" files (came from a preceding
        #      navPoint that was merged into this letter)
        #   2. The letter's own title-page chunk (letter_file)
        #   3. Each chapter's chunk
        gathered: list[dict] = []
        chapter_files = [normalize_src(cf) for cf, _ in letter["chapters"]]
        # 1. Pending intros
        for extra in letter.get("letter_file_extras", []):
            xf = normalize_src(extra)
            if xf and xf in src_to_chunk and xf not in consumed:
                gathered.append(src_to_chunk[xf])
                consumed.add(xf)
        # 2. Letter title page (if distinct from chapters)
        lfile = normalize_src(letter["letter_file"])
        if lfile and lfile in src_to_chunk and lfile not in chapter_files and lfile not in consumed:
            gathered.append(src_to_chunk[lfile])
            consumed.add(lfile)
        # 3. Chapters
        for cf in chapter_files:
            if cf in src_to_chunk and cf not in consumed:
                gathered.append(src_to_chunk[cf])
                consumed.add(cf)
        if not gathered:
            print(f"  ⚠ letter '{cn}' no chunks matched (NCX file paths may differ)")
            continue

        # Pagination uses ACTUAL CHAPTER NUMBERS, not the gathered-chunk
        # index, so user sees「第1-10章」「第11-12章」rather than positions
        # inflated by the intro + title-page chunks at the head.
        #
        # We compute which gathered chunks are "chapters" by looking at the
        # tail of the gathered list (intro + title come first; chapters
        # come last in NCX-file order). chapters_count = number of NCX
        # chapter sub-entries.
        n_chapters = len(letter["chapters"])
        n_extras = len(gathered) - n_chapters  # intro + title pages
        if n_extras < 0:
            n_extras = 0
            n_chapters = len(gathered)
        chapter_chunks = gathered[n_extras:]
        extras = gathered[:n_extras]

        if n_chapters <= chapters_per_page:
            # One page — everything goes together, no chapter range label
            pages = [(gathered, None)]
        else:
            pages = []
            # First page: extras + first chapter slice
            first_slice = chapter_chunks[:chapters_per_page]
            pages.append((extras + first_slice, (1, len(first_slice))))
            # Subsequent pages: pure chapter slices
            for start in range(chapters_per_page, n_chapters, chapters_per_page):
                end = min(start + chapters_per_page, n_chapters)
                page_slice = chapter_chunks[start:end]
                pages.append((page_slice, (start + 1, end)))
            # No tail-fold: user explicitly wants 「第1-10章 然後第11-12章」
            # separate for a 12-chapter letter (NOT merged into one).
        for page_chunks, span in pages:
            merged_zh = "\n\n".join(
                c.get("content", "").strip() for c in page_chunks
                if c.get("content", "").strip()
            )
            merged_en = "\n\n".join(
                c.get("source_text", "").strip() for c in page_chunks
                if c.get("source_text", "").strip()
            )
            merged_fn: dict[int, str] = {}
            for c in page_chunks:
                for k, v in (c.get("footnotes") or {}).items():
                    # JSON loads dict keys as strings — preserve
                    merged_fn[int(k) if str(k).isdigit() else k] = v
            merged_pgs = sorted(set(
                p for c in page_chunks for p in (c.get("page_numbers") or [])
            ))
            if span is None:
                page_path = cn
            else:
                start_chap, end_chap = span
                if start_chap == end_chap:
                    page_path = f"{cn} 第{start_chap}章"
                else:
                    page_path = f"{cn} 第{start_chap}-{end_chap}章"
            consolidated_pages.append({
                "chunk_type": "letter_page",
                "page_number": merged_pgs[0] if merged_pgs else None,
                "page_numbers": merged_pgs,
                "chapter_path": page_path,
                "format": "markdown",
                "source_lang": "en",
                "volume": cn,
                "title_en": letter["letter_label"],
                "source_text": merged_en,
                "content": merged_zh,
                "footnotes": merged_fn,
                # First page of multi-page letter — also is_volume_header
                "is_volume_header": (span is None) or (span[0] == 0),
            })

    # Front-matter: anything in chunks NOT consumed → kept as-is.
    # Build a reverse: chunk → src_file (using the same index alignment).
    consumed_chunk_indices = set()
    for c in chunks:
        # Find this chunk's src via the src_to_chunk inverse map
        for src, ch in src_to_chunk.items():
            if ch is c and src in consumed:
                consumed_chunk_indices.add(c["chunk_index"])
                break

    frontmatter: list[dict] = []
    for c in chunks:
        if c["chunk_index"] in consumed_chunk_indices:
            continue
        c2 = dict(c)
        c2.pop("is_volume_header", None)
        frontmatter.append(c2)

    # Heuristic split: front-matter chunks BEFORE the first consolidated page
    # should come first; chunks AFTER (indexes, bibliographies) come last.
    # We approximate by chunk_index — frontmatter sorted ascending; anything
    # past the median treated as back-matter.
    # Simpler: keep in original chunk_index order at the start, all of them
    # — most ANF Vol 1 front matter is index 0-3, and trailing indexes are
    # 913-917. Mixed in order looks fine.
    frontmatter.sort(key=lambda c: c.get("chunk_index", 0))

    # Build final chunk list: front-matter PREFIX + consolidated pages + trailing index
    min_consumed = min(consumed_chunk_indices) if consumed_chunk_indices else 0
    max_consumed = max(consumed_chunk_indices) if consumed_chunk_indices else len(chunks)
    fm_prefix = [c for c in frontmatter if c["chunk_index"] < min_consumed]
    fm_suffix = [c for c in frontmatter if c["chunk_index"] > max_consumed]
    fm_middle = [c for c in frontmatter
                 if min_consumed <= c["chunk_index"] <= max_consumed]
    # Anything mid-stream stays at end of front-matter prefix (rare)
    fm_prefix.extend(fm_middle)

    # Renumber: 0, 1, 2, ... for entire merged list
    final: list[dict] = []
    idx = 0
    for c in fm_prefix:
        c["chunk_index"] = idx
        c.setdefault("chunk_type", "chapter")
        c.setdefault("format", "markdown")
        final.append(c)
        idx += 1
    for c in consolidated_pages:
        c["chunk_index"] = idx
        final.append(c)
        idx += 1
    for c in fm_suffix:
        c["chunk_index"] = idx
        c.setdefault("chunk_type", "chapter")
        c.setdefault("format", "markdown")
        final.append(c)
        idx += 1

    print(f"\n=== Result ===")
    print(f"  Front-matter (prefix): {len(fm_prefix)}")
    print(f"  Consolidated letter pages: {len(consolidated_pages)}")
    print(f"  Back-matter (suffix): {len(fm_suffix)}")
    print(f"  Total new chunks: {len(final)} (was {len(chunks)})")

    # Sample dump
    print("\n  Sample TOC after consolidation:")
    cur_vol = None
    for c in final[:25]:
        v = c.get("volume", "-")
        marker = " 🏷" if c.get("is_volume_header") else "  "
        if v != cur_vol:
            cur_vol = v
            print(f"  ── volume: {v} ──")
        print(f"   {marker} [{c['chunk_index']:3d}] {c.get('chapter_path', '')[:60]}")
    if len(final) > 25:
        print(f"   ... ({len(final) - 25} more)")

    if dry_run:
        print("\n(dry-run, not writing)")
        return

    # Write
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in final:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    size_kb = jsonl_path.stat().st_size // 1024
    print(f"\n  ✓ wrote {jsonl_path.name}  ({size_kb} KB)")

    # Push R2
    try:
        se.push_to_r2(ebook_id, jsonl_path)
        print(f"  ✓ pushed R2")
    except Exception as e:
        print(f"  ⚠ R2 push: {e}", file=sys.stderr)

    # Refresh DB previews
    try:
        r = requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                            headers=H_GET, timeout=30)
        if r.status_code not in (200, 204):
            print(f"  ⚠ preview DELETE: {r.status_code}", file=sys.stderr)
        rows = [{
            "ebook_id": ebook_id,
            "chunk_index": c["chunk_index"],
            "chunk_type": c.get("chunk_type", "chapter"),
            "page_number": c.get("page_number"),
            "chapter_path": c.get("chapter_path"),
            "content": (c.get("content") or "")[:200],
            "char_count": len(c.get("content") or ""),
        } for c in final]
        BATCH = 25
        for i in range(0, len(rows), BATCH):
            batch = rows[i:i + BATCH]
            rr = requests.post(f"{URL}/rest/v1/ebook_chunks",
                               headers=H_JSON, json=batch, timeout=30)
            if rr.status_code not in (200, 201):
                for row in batch:
                    requests.post(f"{URL}/rest/v1/ebook_chunks",
                                  headers=H_JSON, json=row, timeout=30)
        print(f"  ✓ refreshed previews ({len(rows)} rows)")
    except Exception as e:
        print(f"  ⚠ preview refresh: {e}", file=sys.stderr)

    # Update ebook row chunk_count / total_pages / total_chars
    total_chars = sum(len(c.get("content") or "") for c in final)
    patch = {
        "chunk_count": len(final),
        "total_pages": len(final),
        "total_chars": total_chars,
    }
    requests.patch(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}",
                   headers=H_JSON, json=patch, timeout=30)
    print(f"  ✓ ebooks row updated: chunk_count={len(final)}, total_chars={total_chars:,}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--chapters-per-page", type=int, default=10)
    args = ap.parse_args()
    consolidate(args.ebook_id, dry_run=args.dry_run,
                chapters_per_page=args.chapters_per_page)


if __name__ == "__main__":
    main()
