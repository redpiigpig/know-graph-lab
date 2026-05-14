#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standardize one or more EPUBs into the "reader-ready" format:
  - Re-parse with HTML structure (h1/h2/h3/b/em → markdown)
  - Drop publisher boilerplate (Digital Lab ads, repeated copyright pages)
  - Convert simplified Chinese → traditional (opencc s2tw)
  - Re-chunk by chapter (one HTML doc = one chunk; split at TOC anchors for
    multi-volume sets)
  - Push new JSONL to local + R2 + refresh DB previews

Usage — single book:
  python scripts/standardize_ebook.py <ebook_id>
  python scripts/standardize_ebook.py <ebook_id> --dry-run
  python scripts/standardize_ebook.py <ebook_id> --no-r2

Usage — batch (auto-skips PDFs):
  python scripts/standardize_ebook.py --category 哲學
  python scripts/standardize_ebook.py --category 哲學 --subcategory 近代哲學
  python scripts/standardize_ebook.py --category 哲學 --limit 5
  python scripts/standardize_ebook.py --all   # every parsed EPUB across all categories

Idempotent: re-running overwrites local JSONL, R2 object, and DB previews.
"""
import gzip
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import requests
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup, NavigableString, Tag
    import opencc
except ImportError as e:
    print(f"Missing: {e}. pip install requests ebooklib beautifulsoup4 opencc", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from parse_worker import load_env
from parse_drive_inventory import TRAD_FIXES

ENV = load_env()
URL = ENV["SUPABASE_URL"]
KEY = ENV["SUPABASE_SERVICE_ROLE_KEY"]
H_JSON = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path(ENV.get("EBOOK_CHUNKS_DIR") or "G:/我的雲端硬碟/資料/電子書/_chunks")
PREVIEW_LEN = 200

CC = opencc.OpenCC("s2tw")  # simplified → traditional (Taiwan idioms)


def normalize_chapter_title(title: str) -> str:
    """Cosmetic renames of well-known boilerplate titles. Keeps the chunk
    content intact — just changes how it's labelled in the sidebar."""
    t = (title or "").strip()
    if not t:
        return t
    # CIP / 圖書在版編目 → 版權頁
    if "圖書在版編目" in t or "图书在版编目" in t or t.upper().startswith("CIP"):
        return "版權頁"
    # 版權信息 / 版权信息 → 版權頁 (unify the multiple terms publishers use)
    if t in ("版權信息", "版权信息", "版權頁", "版权页"):
        return "版權頁"
    return t


# Series-banner phrases that publishers prepend to every front-matter page —
# bad chapter titles. When the first content line matches, prefer the next.
_BANNER_RX = re.compile(r"叢書|丛书|名著|系列|文集|文庫|文库|出版社")
# Real chapter heading patterns — accepted even if longer than the short-line cap.
_CHAPTER_HEAD_RX = re.compile(
    r"^第[一二三四五六七八九十百千零〇\d]+(章|卷|編|编|册|冊|部|集|篇|節|节|回|课|課)"
)
# English chapter heading — `CHAPTER 1. Title…`, `BOOK II.`, `Part 3`, etc.
# Triggered for English EPUBs (e.g. Complete Works of Josephus) where the
# Chinese-only _CHAPTER_HEAD_RX never matches and otherwise long English titles
# (>60 chars) fall through to the filename fallback.
_CHAPTER_HEAD_EN_RX = re.compile(
    r"^(?:CHAPTER|Chapter|BOOK|Book|PART|Part|SECTION|Section)\s+"
    r"(?:\d+|[IVXLCDM]+)\b",
    re.IGNORECASE
)
# Truncate cap for the "last resort" path — better than leaking a filename.
_FALLBACK_TRUNCATE = 60


def derive_chapter_title(md_tw: str, fallback: str) -> str:
    """Find a meaningful chapter title:
       1. Use the first markdown heading if any (skip headings whose text is
          just a numeric/letter marker like "1" / "II" / "Ch.3" — common in
          academic EPUBs where <h2>1</h2><h1>Real Title</h1> is the pattern)
       2. Else look at first 3 non-empty lines and pick the best:
          a. Any line matching '第N章/卷/編/…' pattern wins
          b. Else first short (≤30) non-banner line
       3. Else fall back to file name
    Then normalize for cosmetic renames (e.g. CIP → 版權頁)."""
    # Collect up to the first 4 headings; prefer the first non-numeric one.
    # is_continuation_title catches the same noise patterns we want to skip
    # at the heading level here, so reuse it.
    headings = re.findall(r"^#{1,4}\s+(.+)$", md_tw, re.M)[:4]
    for h in headings:
        h = h.strip()
        if not is_continuation_title(h):
            return normalize_chapter_title(h)
    if headings:
        # All headings are numeric/letter markers (e.g. publisher patterns
        # like <h2>01</h2><p>王權的誕生</p>). Look at the first short non-empty
        # content line right after the first heading — if it looks like a
        # chapter subtitle, combine both into "01 王權的誕生".
        first_h = headings[0].strip()
        m = re.search(r"^#{1,4}\s+" + re.escape(first_h) + r"\s*$", md_tw, re.M)
        if m:
            after = md_tw[m.end():]
            for raw in after.split("\n"):
                s = raw.strip()
                if not s:
                    continue
                # Strip markdown wrappers (** / * / # / > / -) before length check
                s_clean = re.sub(r"^[#>\-]+\s*", "", s)
                s_clean = re.sub(r"[*_`]+", "", s_clean).strip()
                if not s_clean:
                    continue
                if (len(s_clean) <= 30
                        and not _BANNER_RX.search(s_clean)
                        and not is_continuation_title(s_clean)):
                    return normalize_chapter_title(f"{first_h} {s_clean}")
                break  # first non-empty line wasn't title-like; give up
        return normalize_chapter_title(first_h)

    candidates = []
    for line in md_tw.split("\n"):
        s = line.strip()
        if not s:
            continue
        s = re.sub(r"[*_`]+", "", s).strip()
        if s:
            candidates.append(s)
        if len(candidates) >= 3:
            break

    # CIP detection — sniff the first few lines
    for c in candidates:
        if "圖書在版編目" in c[:50] or "图书在版编目" in c[:50]:
            return "版權頁"

    # PRIORITY 1: earliest short non-banner line — natural document order wins
    # so "目錄" beats a later "第一章" inside a TOC chunk's content.
    for c in candidates:
        if len(c) <= 30 and not _BANNER_RX.search(c):
            return normalize_chapter_title(c)

    # PRIORITY 2: explicit chapter heading anywhere — handles long chapter titles
    # that exceed 30 chars (e.g. 君主論's 「第四章 為什麼亞歷山大大帝...」 in
    # Chinese, or `CHAPTER 1. The Constitution Of The World…` in English).
    for c in candidates:
        if _CHAPTER_HEAD_RX.match(c) or _CHAPTER_HEAD_EN_RX.match(c):
            return normalize_chapter_title(c)

    # Last resort: first candidate if reasonable length
    if candidates and len(candidates[0]) <= 60:
        return normalize_chapter_title(candidates[0])

    # Better than leaking the EPUB filename (e.g. `text/part0007.html`) — truncate
    # the first candidate at a clause boundary so the sidebar shows something
    # related to the chunk's actual content. Real fallback to file_name happens
    # only when the chunk has zero usable text.
    #
    # CAVEAT: the same-chapter cross-spine merge in standardize() collapses
    # consecutive chunks whose (volume, chapter_path) match exactly. If two spine
    # docs (OR two anchor-split segments inside one spine doc) share the same
    # opening line, the truncated titles would collide and the merge would eat
    # hundreds of pages into one chunk (city-history book 城市發展史 collapsed
    # 16 → 5 with a 700KB chunk). Append a 4-char content hash so each chunk's
    # title is unique even when neighbors share both opening text and spine doc.
    if candidates:
        c = candidates[0]
        cut = c[:_FALLBACK_TRUNCATE]
        for sep in ("。", ".", "，", ",", ":", "：", ";", "；"):
            idx = cut.rfind(sep)
            if idx >= 15:
                cut = cut[: idx + 1]
                break
        else:
            cut = cut + "…"
        import hashlib
        h = hashlib.md5(md_tw.encode("utf-8", errors="ignore")).hexdigest()[:4]
        return normalize_chapter_title(f"{cut} [{h}]")

    return normalize_chapter_title(fallback)


# Titles that look like continuation markers — merged into previous chunk
# instead of becoming standalone chunks. Matches: single Chinese numeral,
# single Latin letter, pure digits 1-3 chars, or empty.
_CONT_RX = re.compile(
    r"^\s*(?:"
    r"[一二三四五六七八九十百千]+"          # 一 / 二 / 十一 …
    r"|[A-Za-z]"                              # A / B / … (e.g. index letters)
    r"|\d{1,3}"                               # 1 / 23 / …
    r"|"                                      # empty
    r")\s*[、。．\.]?\s*$"
)

def is_continuation_title(title: str) -> bool:
    return bool(_CONT_RX.match(title or ""))


# Part-divider regex — matches 第N部/卷/編/集/篇 at start of title (with
# optional fullwidth/halfwidth space, suffix). Used to detect implicit volume
# starts that the publisher dropped from the TOC (anonymous TOC group).
_PART_DIVIDER_RX = re.compile(
    r"^第[一二三四五六七八九十百千零〇\d]+(部|卷|編|编|冊|册|集|篇)"
)


def promote_implicit_volumes(chunks):
    """When a multi-volume book's TOC has an anonymous group (publisher
    forgot to name 第一部 explicitly), the chapters end up flat (vol=None).
    This walks the chunk list and promotes any 第N部/卷-titled vol=None
    chunks into proper volume markers, applying that volume to subsequent
    vol=None chunks until the next explicit volume or another part divider.

    Idempotent — already-volumed chunks are never overwritten."""
    has_named_vol = any(c.get("volume") for c in chunks)
    if not has_named_vol:
        return  # flat book, nothing to promote

    implicit_vol = None  # currently-active synthetic volume name
    for c in chunks:
        if c.get("volume"):
            # Hit an explicit volume — implicit run ends here.
            implicit_vol = None
            continue
        title = c.get("chapter_path") or ""
        if _PART_DIVIDER_RX.match(title):
            implicit_vol = title
            c["volume"] = title
        elif implicit_vol:
            c["volume"] = implicit_vol


# Patterns to extract publisher metadata from 版權頁 / title-page chunks.
# Allow optional fullwidth spaces between characters of the field name and
# either ：or : as the separator.
_FULL_TITLE_RX = re.compile(
    r"(?:書\s*名|Title)\s*[：:]\s*([^\n]+)",
    re.IGNORECASE,
)
_ORIG_TITLE_RX = re.compile(
    r"(?:原\s*文?\s*書\s*名|原\s*書\s*名|原\s*名|英\s*文\s*書\s*名|Original\s*Title)\s*[：:]\s*([^\n]+)",
    re.IGNORECASE,
)
# author + parenthesized English name, e.g. 「作　者：伊迪絲．漢彌敦（Edith Hamilton）」
_AUTHOR_EN_RX = re.compile(
    r"(?:作\s*者|Author)\s*[：:]\s*[^\n（(]*[（(]([^）)]+)[）)]",
    re.IGNORECASE,
)
# Field-value stop characters: newline, fullwidth/halfwidth pipe (publishers
# use 「│」 / 「|」 to pack multiple metadata fields onto one line), comma,
# semicolon, slash, paren — anything that signals "next field starts here".
_FIELD_STOP = r"\n│|，,；;／/（(、"

_TRANSLATOR_RX = re.compile(
    rf"(?:譯\s*者|译\s*者|Translator|Translated\s+by)\s*[：:]\s*([^{_FIELD_STOP}]+)",
    re.IGNORECASE,
)
# 出版 / 出版社 / 出版者 — but NOT 出版日期 / 出版年 / 出版時間 / 出版地
_PUBLISHER_RX = re.compile(
    rf"(?:出\s*版(?:社|者)?|Published\s+by|Publisher)(?!\s*(?:日期|年|時間|時期|地))\s*[：:]\s*([^{_FIELD_STOP}]+)",
    re.IGNORECASE,
)
# Find a 4-digit year next to a Chinese print-date label
_PUBLISH_YEAR_RX = re.compile(
    r"(?:初\s*版(?:首刷)?|再\s*版|電\s*子\s*書|出\s*版\s*日?\s*期?|出\s*版\s*年|出\s*版\s*時?\s*期|First\s+published|Published)\D{0,12}(\d{4})\s*年?",
    re.IGNORECASE,
)
# 「Copyright © 1942 by Edith Hamilton」 — gives both original year and author
_ORIG_COPYRIGHT_RX = re.compile(
    r"Copyright\s*©?\s*(\d{4})\s+by\s+([^\n.,]+)",
    re.IGNORECASE,
)


def _clean_extracted(s: str) -> str:
    """Strip markdown noise (** _ leading/trailing) from extracted metadata."""
    if not s:
        return s
    s = s.strip()
    # Iteratively peel off matched bold/em wrappers
    for _ in range(3):
        s = s.strip()
        if s.startswith("**") and s.endswith("**") and len(s) > 4:
            s = s[2:-2]
            continue
        if s.startswith("*") and s.endswith("*") and len(s) > 2:
            s = s[1:-1]
            continue
        break
    # Strip dangling asterisks/underscores/punctuation tail
    return s.strip().strip("*_").rstrip("。．.").strip()


def _extract_publisher_metadata(chunks):
    """Scan all chunks for 版權頁-style metadata lines. Returns a dict with
    keys: full_title, original_title, author_en, translator, publisher,
    publish_year, original_publish_year, original_author. Any value may be
    None if not present in the source.

    Strategy: 「first hit wins」 per field. Walks chunks in order so the
    nearest-to-cover 版權頁 page dominates over any later mentions in body
    text. Also tries the cover chunk's content first since some EPUBs
    embed structured metadata there too."""
    out = {
        "full_title": None,
        "original_title": None,
        "author_en": None,
        "translator": None,
        "publisher": None,
        "publish_year": None,
        "original_publish_year": None,
        "original_author": None,
    }
    for c in chunks:
        content = c.get("content") or ""
        if not content:
            continue
        if out["full_title"] is None:
            m = _FULL_TITLE_RX.search(content)
            if m:
                cand = _clean_extracted(m.group(1))
                if cand and len(cand) >= 2:
                    out["full_title"] = cand
        if out["original_title"] is None:
            m = _ORIG_TITLE_RX.search(content)
            if m:
                cand = _clean_extracted(m.group(1))
                if cand and len(cand) >= 3:
                    out["original_title"] = cand
        if out["author_en"] is None:
            m = _AUTHOR_EN_RX.search(content)
            if m:
                cand = _clean_extracted(m.group(1))
                if cand and re.search(r"[A-Za-z]", cand):
                    out["author_en"] = cand
        if out["translator"] is None:
            m = _TRANSLATOR_RX.search(content)
            if m:
                cand = _clean_extracted(m.group(1))
                if cand and len(cand) >= 1:
                    out["translator"] = cand
        if out["publisher"] is None:
            m = _PUBLISHER_RX.search(content)
            if m:
                cand = _clean_extracted(m.group(1))
                # Reject if it looks like 'YYYY 年' / '日期…' garbage
                if cand and len(cand) >= 2 and not re.match(r"^\d{2,}\s*年?$", cand):
                    out["publisher"] = cand
        if out["publish_year"] is None:
            m = _PUBLISH_YEAR_RX.search(content)
            if m:
                yr = int(m.group(1))
                if 1500 <= yr <= 2100:
                    out["publish_year"] = yr
        if out["original_publish_year"] is None or out["original_author"] is None:
            m = _ORIG_COPYRIGHT_RX.search(content)
            if m:
                yr = int(m.group(1))
                ath = _clean_extracted(m.group(2))
                if 1500 <= yr <= 2100:
                    out["original_publish_year"] = out["original_publish_year"] or yr
                if ath and re.search(r"[A-Za-z]", ath):
                    out["original_author"] = out["original_author"] or ath
        if all(out.values()):
            break
    return out


def _split_title_subtitle(title: str):
    """Split a title like 「希臘羅馬神話：永恆的諸神…」 into (main, subtitle).
    Returns (title, None) if no separator found. Common separators: ：: ——"""
    if not title:
        return title, None
    for sep in ("：", ":", " — ", "——", " - "):
        if sep in title:
            main, sub = title.split(sep, 1)
            main = main.strip()
            sub = sub.strip()
            if main and sub:
                return main, sub
    return title.strip(), None


def build_cover_content(book, chunks) -> str:
    """Compose a rich 封面 chunk from DB metadata + 版權頁 extraction.

    Layout (markdown):
        ## 封面
        # {main title}
        ## {subtitle}             (only if extractable)
        **{original_title}**       (only if extractable)
        {author}
        *{author_en}*              (only if extractable)
    """
    title = (book.get("title") or "").strip()
    author = (book.get("author") or "").strip()
    meta = _extract_publisher_metadata(chunks)
    full_title     = meta["full_title"]
    original_title = meta["original_title"]
    author_en      = meta["author_en"]

    # Prefer the publisher's full-form title when available (it usually contains
    # the subtitle that DB.title omits); only use it if it starts with DB.title
    # to avoid hijacking the cover with a different book's metadata.
    canonical = title
    if full_title and full_title.startswith(title) and len(full_title) > len(title):
        canonical = full_title
    main_title, subtitle = _split_title_subtitle(canonical)

    lines = ["## 封面", ""]
    if main_title:
        lines += [f"# {main_title}", ""]
    if subtitle:
        lines += [f"## {subtitle}", ""]
    if original_title:
        lines += [f"**{original_title}**", ""]
    if author:
        # author + author_en on consecutive lines (markdown two-space line break)
        if author_en:
            lines += [f"{author}  ", f"*{author_en}*", ""]
        else:
            lines += [author, ""]
    return "\n".join(lines).rstrip() + "\n"


# Titles that count as the table-of-contents page in either language —
# everything between the cover and this chunk is rolled up into 出版資訊.
_CONTENTS_TITLE_RX = re.compile(
    r"^(?:目\s*錄|目\s*次|目\s*录|contents?|table\s*of\s*contents)\s*$",
    re.IGNORECASE,
)


def consolidate_frontmatter_into_publisher(chunks):
    """Many EPUBs have noisy pre-CONTENTS frontmatter — dedications, repeated
    title pages, series banners, epigraphs, multi-line copyright pages — each
    of which becomes its own sidebar entry. Squash all of them into a single
    「出版資訊」 chunk between the cover and the CONTENTS page.

    Conservative: only fires when (a) the cover chunk is at index 0,
    (b) a CONTENTS-style chunk exists in the early frontmatter, and (c) every
    chunk we'd be merging is in flat (vol=None) territory — never crosses a
    volume boundary."""
    if len(chunks) < 3:
        return
    if chunks[0].get("chapter_path") != "封面":
        return

    # Locate the first CONTENTS-style chunk (search the first 12 entries to
    # avoid pathological "目錄 placed in the middle of body" cases).
    contents_idx = None
    for i, c in enumerate(chunks[:12]):
        title = (c.get("chapter_path") or "").strip()
        if _CONTENTS_TITLE_RX.match(title):
            contents_idx = i
            break
    if contents_idx is None or contents_idx <= 1:
        return  # nothing between cover and CONTENTS

    # Safety: don't fold across a volume start
    middle = chunks[1:contents_idx]
    if any(c.get("volume") for c in middle):
        return

    # Build merged content
    parts = ["## 出版資訊"]
    for c in middle:
        body = (c.get("content") or "").strip()
        if not body:
            continue
        # Strip the leading heading line — we already wrote ## 出版資訊
        body = re.sub(r"^#{1,4}\s+.+\n+", "", body, count=1).strip()
        if body:
            parts.append(body)
    merged = {
        "chunk_index": 0,  # re-indexed below
        "chunk_type": "chapter",
        "page_number": None,
        "chapter_path": "出版資訊",
        "volume": None,
        "format": "markdown",
        "content": "\n\n---\n\n".join(parts),
    }

    # Splice: cover + merged + everything from CONTENTS onward
    chunks[:] = [chunks[0], merged] + chunks[contents_idx:]
    for i, c in enumerate(chunks):
        c["chunk_index"] = i


def apply_cover_enrichment(chunks, book):
    """Replace the placeholder 「## 封面 (書本封面)」 chunk with rich metadata,
    or insert a new cover chunk at index 0 if none exists.

    Idempotent — re-runs produce identical output for the same book."""
    rich = build_cover_content(book, chunks)

    if chunks and chunks[0].get("chapter_path") == "封面":
        chunks[0]["content"] = rich
        chunks[0]["chapter_path"] = "封面"
        return

    # No cover chunk — synthesize one at the head and shift indices.
    new_cover = {
        "chunk_index": 0,
        "chunk_type": "chapter",
        "page_number": None,
        "chapter_path": "封面",
        "volume": None,
        "format": "markdown",
        "content": rich,
    }
    for c in chunks:
        c["chunk_index"] = c["chunk_index"] + 1
    chunks.insert(0, new_cover)


def to_traditional(text: str) -> str:
    """opencc s2tw + post-fix substitutions to correct over-conversion bugs
    (e.g. s2tw turns 历史 → 曆史 when it should be 歷史). The fix table is
    shared with parse_drive_inventory so filename + content stay consistent."""
    if not text:
        return text
    out = CC.convert(text)
    for wrong, right in TRAD_FIXES:
        out = out.replace(wrong, right)
    return out

# ── Boilerplate patterns ───────────────────────────────────────
# Hard drop: chunks dedicated to publisher self-promotion (no content value).
# Keep these patterns NARROW — they should match only useless filler, never
# real content like copyright pages (which user wants kept as 出版頁).
HARD_DROP_PATTERNS = [
    r"Digital\s*Lab是上海译文出版社",            # the standard "about Digital Lab" page
    r"我们致力于将优质的资源送到读者手中",         # same page, alt opening
    r"上海译文出版社\|Digital\s*Lab",            # closing line of that page
]
HARD_DROP_RX = [re.compile(p) for p in HARD_DROP_PATTERNS]

# Patterns whose FIRST occurrence is kept, subsequent occurrences dropped.
# (Matches in plain text head; many publishers repeat copyright/CIP per sub-volume.)
DEDUPE_PATTERNS = [
    r"^版权信息",     # 版权页 — keep one for the whole book
    r"^版權信息",     # already-converted form (defensive)
    r"圖書在版編目",   # CIP 數據 page (multi-volume sets repeat this per volume)
    r"图书在版编目",
]
DEDUPE_RX = [re.compile(p) for p in DEDUPE_PATTERNS]


# ── HTML → Markdown ────────────────────────────────────────────
def _bool_class(node, substr):
    """True iff any class contains substr (case-insensitive)."""
    classes = node.get("class") or []
    return any(substr in c.lower() for c in classes)


def el_to_md(el, depth=0):
    """Convert a BeautifulSoup element to markdown. Preserves h1-h4, b/strong, em/i, p, blockquote."""
    if isinstance(el, NavigableString):
        return str(el)

    name = el.name.lower() if el.name else ""

    # Skip non-content tags
    if name in ("script", "style", "head", "meta", "link", "svg", "image", "img", "br", "hr"):
        if name == "br":
            return "\n"
        if name == "hr":
            return "\n\n---\n\n"
        return ""

    # Footnote refs: drop entirely (they're decorative without target resolution)
    if name == "sup":
        return ""
    if name == "a" and (_bool_class(el, "footnote") or el.find("sup")):
        return ""

    inner = "".join(el_to_md(c, depth + 1) for c in el.children)

    if name in ("h1",):
        # parttitle (Volume) → ##  ;  prefacetitle / chaptertitle → ##
        return f"\n\n## {inner.strip()}\n\n"
    if name == "h2":
        return f"\n\n### {inner.strip()}\n\n"
    if name in ("h3", "h4"):
        return f"\n\n#### {inner.strip()}\n\n"
    if name in ("b", "strong"):
        s = inner.strip()
        return f"**{s}**" if s else ""
    if name in ("em", "i"):
        s = inner.strip()
        return f"*{s}*" if s else ""
    if name == "blockquote":
        lines = inner.strip().split("\n")
        return "\n\n" + "\n".join(f"> {ln}" for ln in lines if ln.strip()) + "\n\n"
    if name == "p":
        s = re.sub(r"[ \t]+", " ", inner).strip()
        return f"\n\n{s}\n\n" if s else ""
    if name in ("div", "section", "article", "html", "body"):
        return inner
    if name in ("ul", "ol"):
        return inner
    if name == "li":
        return f"\n- {inner.strip()}"

    # Default: pass through inner
    return inner


def html_to_markdown(html_bytes):
    """Convert chapter HTML to markdown. Returns (markdown, plain_for_detection)."""
    soup = BeautifulSoup(html_bytes, "html.parser")
    body = soup.find("body") or soup
    md = el_to_md(body)
    # Clean: collapse 3+ newlines to 2; trim
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    # Plain text (markdown stripped) — for boilerplate detection
    plain = re.sub(r"[#*>_`\[\]\(\)]", "", md)
    plain = re.sub(r"\s+", " ", plain).strip()
    return md, plain


def is_hard_drop(plain):
    """True if the plain text is publisher-only filler with no content value."""
    return any(rx.search(plain) for rx in HARD_DROP_RX)


def matched_dedupe_pattern(plain):
    """Return the regex pattern string if plain text matches a dedupe pattern, else None."""
    for rx in DEDUPE_RX:
        if rx.search(plain):
            return rx.pattern
    return None


# ── Pipeline ───────────────────────────────────────────────────
def fetch_book(ebook_id):
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*", headers=H_GET, timeout=15)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        raise SystemExit(f"Book not found: {ebook_id}")
    return rows[0]


VOLUME_MARKERS = ("卷", "冊", "册", "部", "集", "篇")


def looks_like_volume(title: str) -> bool:
    """Heuristic: a TOC top-level entry is a 'volume' (multi-book set) only if
    its title uses a volume marker like 卷/冊/部. Without this check we'd
    promote chapters / 目錄 / 插頁 / 出版說明 to volumes, which is wrong for
    single-volume books."""
    return any(m in title for m in VOLUME_MARKERS)


_CHAPTER_TITLE_RE = re.compile(
    r"^(?:第[\d一二三四五六七八九十百千零兩两]+(?:章|回|课|課|课时|讲|講)|"
    r"Chapter\s+\d+|"
    r"\d+[\.、:：]\s*\S)",
    re.I,
)

# Appendix-style chapters whose sub-entries (節) should NOT be split into
# individual sidebar items — readers expect ONE collapsed entry per appendix.
# Matches inside a stripped title.
_APPENDIX_TITLE_RE = re.compile(
    r"(索引|附\s*錄|參考(?:資料|文獻|書目)|書目|文獻|"
    r"延伸閱讀|進一步閱讀|further\s*read|"
    r"年表|大事記|"
    r"帝王世系|統治者|皇朝表|"
    r"致謝|謝詞|致敬|acknowledg|"
    r"後記|譯後記|譯者後記|跋|"
    r"glossary|bibliography|index|"
    r"術語表|名詞解釋|對照表|譯名對照|插圖出處)",
    re.I,
)


def _is_chapter_title(title: str) -> bool:
    """Heuristic: title looks like a printed-book chapter (single-volume hierarchy)."""
    if not title:
        return False
    return bool(_CHAPTER_TITLE_RE.match(title.strip()))


def _is_appendix_title(title: str) -> bool:
    """Title that should NOT be subdivided — appendix, bibliography, index, etc."""
    if not title:
        return False
    return bool(_APPENDIX_TITLE_RE.search(title.strip()))


def parse_toc_hierarchical(book):
    """Detect 2-level TOC structure with two possible roles.

    Walks book.toc to find top-level Sections that have ≥2 children. Then decides:

      * **multi-volume** (e.g. 羅馬帝國衰亡史) — top Sections look like volumes
        (titles aren't 第N章). Split each spine doc at every CHILD anchor;
        each child becomes a chunk tagged with vol+chapter from TOC.

      * **single-volume hierarchical** (e.g. 現代世界史) — top Sections are
        themselves chapters (titles match 第N章 / Chapter N / 1. ...).
        Split at TOP Section anchors only; deeper child entries (節) remain
        inline as h3/h4 inside each chapter chunk. volume = None.

    Returns dict with keys:
      role:             "multi_volume" or "single_chapter"
      volumes:          list of (vol_title, [(chap_title, file, anchor), ...])
                        — for logging; empty for single_chapter role
      doc_chap_starts:  {file: (vol_or_None, chap_title)}      # chapter starts at file top
      doc_chap_splits:  {file: {anchor: (vol_or_None, chap_title)}}  # chapter anchor inside file
      flat_links:       [(title, file, anchor), ...]           # top-level Links (front matter)

    Returns None when no usable 2-level structure found."""
    top_sections = []  # [(title, file_no_anchor, anchor_or_None, [(child_title, file, anchor), ...])]
    flat_links = []

    for it in book.toc:
        if isinstance(it, tuple):
            section, children = it
            sect_title = (getattr(section, "title", "") or "").strip()
            sect_href = getattr(section, "href", "")
            if not sect_title or len(children) < 2:
                continue
            if any(skip in sect_title for skip in ("版权", "版權", "Digital Lab")):
                continue
            child_list = []
            for ch in children:
                if isinstance(ch, tuple):
                    sec2, _gc = ch
                    ct = (getattr(sec2, "title", "") or "").strip()
                    ch_h = getattr(sec2, "href", "")
                elif hasattr(ch, "title") and hasattr(ch, "href"):
                    ct = (ch.title or "").strip()
                    ch_h = ch.href or ""
                else:
                    continue
                if ct and ch_h:
                    f, _, a = ch_h.partition("#")
                    child_list.append((ct, f, a or None))
            if child_list:
                f, _, a = sect_href.partition("#") if sect_href else ("", "", "")
                top_sections.append((sect_title, f or "", a or None, child_list))
        elif hasattr(it, "title") and hasattr(it, "href"):
            t = (it.title or "").strip()
            if t and it.href:
                f, _, a = it.href.partition("#")
                flat_links.append((t, f, a or None))

    if len(top_sections) < 2:
        return None

    # Decide role: are top Sections chapters or volumes?
    chap_count = sum(1 for t, _, _, _ in top_sections if _is_chapter_title(t))
    vol_marker_count = sum(1 for t, _, _, _ in top_sections if looks_like_volume(t))
    if chap_count >= len(top_sections) * 0.5 and chap_count > vol_marker_count:
        role = "single_chapter"
    else:
        role = "multi_volume"

    doc_chap_starts = {}
    doc_chap_splits = {}
    volumes_log = []

    # Helper: walk one Section's children for grandchildren (sections beneath
    # chapters, e.g. "1. 古代" beneath "第1章 歐洲的興起"). Used to expose 節 as
    # sidebar entries indented under their chapter.
    def _children_anchored(children_iter):
        out = []
        for ch in children_iter:
            if isinstance(ch, tuple):
                sec, _gc = ch
                t = (getattr(sec, "title", "") or "").strip()
                h = getattr(sec, "href", "")
            elif hasattr(ch, "title") and hasattr(ch, "href"):
                t = (ch.title or "").strip()
                h = ch.href or ""
            else:
                continue
            if t and h:
                f, _, a = h.partition("#")
                out.append((t, f, a or None))
        return out

    if role == "multi_volume":
        # Top = volume; depth-1 children = chapters; depth-2 grandchildren = 節.
        for vol_title, _vol_f, _vol_a, child_list in top_sections:
            volumes_log.append((vol_title, child_list))
            # Walk the original tree to get this volume's grandchildren too
            # (parse_toc_hierarchical only retains depth-1; we need depth-2 for 節).
            # Re-walk: find this volume's Section node again.
            for it in book.toc:
                if not isinstance(it, tuple):
                    continue
                sect, ch_list = it
                if (getattr(sect, "title", "") or "").strip() != vol_title:
                    continue
                # For each chapter (depth-1)
                for ch in ch_list:
                    if isinstance(ch, tuple):
                        chap_sec, grand_list = ch
                        chap_title = (getattr(chap_sec, "title", "") or "").strip()
                        chap_href = getattr(chap_sec, "href", "") or ""
                    elif hasattr(ch, "title"):
                        chap_title = (ch.title or "").strip()
                        chap_href = ch.href or ""
                        grand_list = []
                    else:
                        continue
                    if chap_title and chap_href:
                        f, _, a = chap_href.partition("#")
                        payload = (vol_title, chap_title, "###")
                        if a:
                            doc_chap_splits.setdefault(f, {})[a] = payload
                        else:
                            doc_chap_starts[f] = payload
                    # 節 (grandchildren of volume) — skipped for appendix chapters
                    if _is_appendix_title(chap_title):
                        continue
                    for sec_t, sec_f, sec_a in _children_anchored(grand_list):
                        payload = (vol_title, sec_t, "####")
                        if sec_a:
                            doc_chap_splits.setdefault(sec_f, {})[sec_a] = payload
                        else:
                            doc_chap_starts[sec_f] = payload
                break
    else:  # single_chapter
        # Top Sections are chapters; depth-1 children are 節.
        for chap_title, file, anchor, child_list in top_sections:
            payload = (None, chap_title, "##")
            if anchor:
                doc_chap_splits.setdefault(file, {})[anchor] = payload
            else:
                doc_chap_starts[file] = payload
            # Skip 節 splits for appendix-style chapters (索引/附錄/書目/...)
            if _is_appendix_title(chap_title):
                continue
            for sec_t, sec_f, sec_a in child_list:
                sec_payload = (None, sec_t, "###")
                if sec_a:
                    doc_chap_splits.setdefault(sec_f, {})[sec_a] = sec_payload
                else:
                    doc_chap_starts[sec_f] = sec_payload

    return {
        "role": role,
        "volumes": volumes_log,
        "doc_chap_starts": doc_chap_starts,
        "doc_chap_splits": doc_chap_splits,
        "flat_links": flat_links,
    }


def parse_volume_toc(book):
    """Returns (doc_volume_starts, doc_anchor_splits):
      - doc_volume_starts: {file_name: volume_title}    — TOC entries with no anchor
      - doc_anchor_splits: {file_name: [(anchor_id, volume_title), ...]}  — TOC entries with anchors
    Returns ({}, {}) if no multi-volume structure detected.

    A TOC top-level entry is considered a volume only when its title contains
    a volume marker (卷/冊/部/集/篇). This avoids promoting unrelated front
    matter (目錄, 插頁, 出版說明, 譯者序) into the volume hierarchy."""
    top_entries = []  # [(href_no_anchor, anchor_or_None, title)]
    for it in book.toc:
        if isinstance(it, tuple):
            section, _children = it
            title = getattr(section, "title", str(section))
            href = getattr(section, "href", "")
        else:
            title = getattr(it, "title", "")
            href = getattr(it, "href", "")
        if not href or not title:
            continue
        if any(skip in title for skip in ("版权", "版權", "Digital Lab")):
            continue
        if "#" in href:
            file_name, anchor = href.split("#", 1)
        else:
            file_name, anchor = href, None
        top_entries.append((file_name, anchor, title.strip()))

    # Filter to entries that look like volume titles. If fewer than 2 remain,
    # treat as flat (single-volume) book — don't impose a volume hierarchy.
    volume_entries = [e for e in top_entries if looks_like_volume(e[2])]
    if len(volume_entries) < 2:
        return {}, {}

    starts = {}
    splits = {}
    for fn, anchor, title in volume_entries:
        if anchor:
            splits.setdefault(fn, []).append((anchor, title))
        else:
            starts[fn] = title
    return starts, splits


def split_body_at_anchors(body, anchor_to_vol):
    """Split a <body> into ordered segments at elements whose id matches a key in
    anchor_to_vol. Returns [(html_segment, transition_volume_or_None), ...].
    Splits at ANY depth, in document order — many publishers wrap the entire
    chapter list inside one big `<div>` directly under body, so a top-level
    iteration would only catch the first anchor. We descend, find every match,
    then string-split the body at the matched elements' positions."""
    matches = []  # [(elem, anchor_id)] in document order — dedupe by anchor id
    seen_anchors = set()
    for elem in body.find_all(attrs={"id": True}):
        cid = elem.get("id")
        if cid in anchor_to_vol and cid not in seen_anchors:
            matches.append((elem, cid))
            seen_anchors.add(cid)

    body_html = str(body)
    if not matches:
        return [(body_html, None)]

    # Open/close tags of <body…>: locate them so we can keep wrappers intact.
    open_end = body_html.find(">") + 1  # end of "<body …>"
    close_start = body_html.rfind("</body>")
    if close_start == -1:
        close_start = len(body_html)
    open_tag = body_html[:open_end]
    close_tag = "</body>"
    inner = body_html[open_end:close_start]

    # For each anchor, find the start position of its enclosing element in `inner`.
    # We search for id="X" or id='X' and walk backwards to the <.
    positions = []  # [(pos_in_inner, anchor_id)]
    used_pos = set()
    for elem, anchor in matches:
        for marker in (f'id="{anchor}"', f"id='{anchor}'"):
            idx = inner.find(marker)
            while idx != -1 and idx in used_pos:
                idx = inner.find(marker, idx + 1)
            if idx != -1:
                tag_start = inner.rfind("<", 0, idx)
                if tag_start != -1:
                    used_pos.add(idx)
                    positions.append((tag_start, anchor))
                break
    positions.sort()
    if not positions:
        return [(body_html, None)]

    out = []
    # Pre-anchor segment
    if positions[0][0] > 0:
        pre = inner[:positions[0][0]]
        if pre.strip():
            out.append((open_tag + pre + close_tag, None))
    # Each anchored segment
    for i, (start, anchor) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(inner)
        seg_inner = inner[start:end]
        out.append((open_tag + seg_inner + close_tag, anchor_to_vol[anchor]))
    return out


def merge_appendix_subentries(chunks):
    """Fold appendix sub-entries into their parent appendix chunk.

    Many EPUBs put each entry of an appendix (kingdoms list under 統治者和
    統治年代, per-chapter bibliography under 延伸閱讀, A-Z under 索引, etc.)
    as its own spine document, so each becomes a separate chunk with its own
    chapter_path — cluttering the sidebar. The user wants ONE collapsed entry
    per appendix.

    Heuristic: walk in order. The first chunk whose chapter_path matches
    `_is_appendix_title` opens "appendix mode". Every later non-appendix-titled
    chunk gets folded into the most recent appendix. A new appendix-titled
    chunk starts a fresh appendix and becomes the new fold target.

    The tail of a book is almost always all-appendix (索引/書目/年表/etc.) so
    once appendix mode opens we stay in it. If a book has body chapters AFTER
    an appendix (rare), this heuristic would over-merge — acceptable trade-off."""
    out: list[dict] = []
    current_appendix_idx: int | None = None

    for c in chunks:
        cp = (c.get("chapter_path") or "").strip()
        if _is_appendix_title(cp):
            out.append(c)
            current_appendix_idx = len(out) - 1
        elif current_appendix_idx is not None:
            # Fold into current appendix — strip the duplicate heading line first
            cont = c.get("content", "") or ""
            cont = re.sub(r"^\s*#{1,4}\s+.+\n+", "", cont, count=1).strip()
            if cont:
                out[current_appendix_idx]["content"] = (
                    (out[current_appendix_idx].get("content") or "").rstrip()
                    + "\n\n"
                    + cont
                )
        else:
            out.append(c)

    # Renumber chunk_index since we may have removed chunks
    for i, c in enumerate(out):
        c["chunk_index"] = i

    # Mutate the input list in place so callers using `chunks` reference see it
    chunks.clear()
    chunks.extend(out)


def rebuild_toc_chunk(chunks, book=None):
    """Rebuild the 目錄 chunk's content from the book's actual chapter / section
    structure (the same data driving the sidebar) so the in-content TOC mirrors
    the sidebar exactly. Heading is `## <u>目錄</u>` so the user can confirm
    the right chunk was found.

    Format (when the book has volumes/chapters/sections):
        ## <u>目錄</u>

        ### 第一卷 …            ← volume row, only if multi-volume
        **第1章 歐洲的興起**     ← chapter (bold)
        1. 古代：希臘、羅馬…    ← section (plain line, joined by single newline)
        2. 中世紀初期…
        ...

        **第2章 …**
        5. 14世紀的災難
        ...

    No-op when there is no 目錄 chunk to rewrite, or when the book has fewer
    than 3 chapter-like entries to list."""
    skip_titles = {"目錄", "封面", "版權", "版權頁", "出版資訊", "出版說明",
                   "出版前言", "前言", "序", "致謝", "扉頁", "書名", "封底",
                   "Cover", "Title Page"}
    # Title of the book itself — chunks whose chapter_path is just the book
    # title leak in (publisher repeats the title on title-page / dedication
    # / etc.). Strip them.
    book_title_norm = re.sub(r"[\s　]", "", (book.get("title") if book else "") or "")

    seen = set()  # dedupe (volume, title)
    entries = []  # [(volume, title, kind)]  kind ∈ {"chapter", "section"}
    for c in chunks:
        cp = (c.get("chapter_path") or "").strip()
        if not cp:
            continue
        # Normalize full-width spaces for skip-set lookup ("目　錄" → "目錄")
        cp_norm = re.sub(r"[\s　]", "", cp)
        if cp_norm in skip_titles:
            continue
        # Drop chunks whose title is just the book title (front-matter repeats)
        if book_title_norm and cp_norm == book_title_norm:
            continue
        # Dedupe (some publishers repeat the same title on multiple front pages)
        key = (c.get("volume"), cp_norm)
        if key in seen:
            continue
        seen.add(key)
        # Detect whether this chunk is a chapter or a section by the FIRST
        # heading depth inside its content (matches how the reader's loadToc
        # decides level for the sidebar).
        content = c.get("content") or ""
        head = re.match(r"^\s*(#{1,4})\s+", content)
        depth = len(head.group(1)) if head else 2
        kind = "chapter" if depth <= 2 else "section"
        entries.append({"volume": c.get("volume"), "title": cp, "kind": kind})

    chap_count = sum(1 for e in entries if e["kind"] == "chapter")
    if chap_count < 3:
        return  # too sparse to bother

    # Find the 目錄 chunk to rewrite. Prefer the EARLIEST one.
    toc_chunk = None
    for c in chunks:
        if (c.get("chapter_path") or "").strip() == "目錄":
            toc_chunk = c
            break
    if toc_chunk is None:
        # No existing 目錄 chunk — synthesize one and insert right after the
        # cover/front-matter. We look for the first chunk that ISN'T pure front
        # matter (封面 / 出版資訊 / 版權 / 書名 / 扉頁 / Cover) and insert before it.
        front_titles = {"封面", "出版資訊", "版權", "版權頁", "書名", "扉頁",
                        "Cover", "Title Page", "出版說明"}
        insert_at = 0
        for i, c in enumerate(chunks):
            cp = (c.get("chapter_path") or "").strip()
            if cp not in front_titles:
                insert_at = i
                break
        else:
            insert_at = len(chunks)
        # Build a stub chunk that the writer below will populate
        toc_chunk = {
            "chunk_index": insert_at,
            "chunk_type": "chapter",
            "page_number": None,
            "chapter_path": "目錄",
            "volume": None,
            "format": "markdown",
            "content": "",
        }
        chunks.insert(insert_at, toc_chunk)
        # Renumber chunk_index
        for i, c in enumerate(chunks):
            c["chunk_index"] = i

    lines: list[str] = ["## <u>目錄</u>"]
    last_vol = "<unset>"
    cur_chapter_block: list[str] = []

    def flush_chapter():
        if cur_chapter_block:
            lines.append("")
            lines.append("\n".join(cur_chapter_block))
            cur_chapter_block.clear()

    for e in entries:
        v = e["volume"]
        if v != last_vol:
            flush_chapter()
            if v:
                lines.append("")
                lines.append(f"### {v}")
            last_vol = v
        if e["kind"] == "chapter":
            flush_chapter()
            cur_chapter_block.append(f"**{e['title']}**")
        else:  # section — append on next line within current chapter block
            cur_chapter_block.append(e["title"])
    flush_chapter()

    toc_chunk["content"] = "\n".join(lines)


def standardize(book):
    """Re-parse EPUB → cleaned markdown chunks."""
    if book["file_type"] != "epub":
        raise SystemExit(f"Only epub supported in this script, got file_type={book['file_type']}")

    src = Path(book["file_path"])
    if not src.exists():
        raise SystemExit(f"EPUB missing on disk: {src}")

    print(f"Parsing: {src.name}  ({src.stat().st_size//1024} KB)")
    b = epub.read_epub(str(src))

    # Iterate documents in spine order (preserves reading order)
    spine_ids = [s[0] for s in b.spine]
    docs = []
    for sid in spine_ids:
        item = b.get_item_with_id(sid)
        if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
            docs.append(item)

    print(f"Spine docs: {len(docs)}")

    # First try the rich 2-level path (top-level Sections containing chapter
    # anchors). If hierarchy is present we can split docs at each chapter
    # anchor and tag chunks with both volume + chapter from TOC. Otherwise
    # fall back to the legacy single-level volume-marker detection.
    hier = parse_toc_hierarchical(b)
    using_hier = bool(hier)
    if using_hier:
        # Payloads are (vol_title, chap_title) tuples; vol_title is None for single_chapter role
        doc_volume_starts = dict(hier["doc_chap_starts"])  # {file: (vol, chap)}
        doc_anchor_splits = {fn: list(amap.items())  # [(anchor, (vol, chap))]
                             for fn, amap in hier["doc_chap_splits"].items()}
        if hier["role"] == "multi_volume":
            print(f"Hierarchical TOC (multi-volume): {len(hier['volumes'])} volumes "
                  f"× total {sum(len(c) for _, c in hier['volumes'])} chapters")
        else:
            n_chaps = len(hier["doc_chap_starts"]) + sum(len(m) for m in hier["doc_chap_splits"].values())
            print(f"Hierarchical TOC (single-volume): {n_chaps} chapters; "
                  f"sub-section entries (節) stay inline as h3/h4")
    else:
        doc_volume_starts, doc_anchor_splits = parse_volume_toc(b)

    # Validate anchored splits: some EPUBs put #anchor in the TOC href but
    # never actually emit a matching id="…" in the HTML. When that happens
    # the volume marker would silently never fire. For docs whose anchors
    # don't resolve, promote the first anchor's title to a doc-level start
    # so the volume transition still happens (just at doc beginning instead
    # of mid-doc).
    if doc_anchor_splits:
        fname_to_doc = {d.file_name: d for d in docs}
        promoted_count = 0
        for fn, lst in list(doc_anchor_splits.items()):
            d = fname_to_doc.get(fn)
            if not d:
                doc_anchor_splits.pop(fn)
                continue
            soup_check = BeautifulSoup(d.get_content(), "html.parser")
            body_check = soup_check.find("body") or soup_check
            real_anchors = [(a, t) for a, t in lst if body_check.find(attrs={"id": a})]
            if real_anchors:
                doc_anchor_splits[fn] = real_anchors
            else:
                # No anchor lands → use the first declared title as a doc-level start.
                doc_volume_starts[fn] = lst[0][1]
                doc_anchor_splits.pop(fn)
                promoted_count += 1
        if promoted_count:
            print(f"  ({promoted_count} anchored volume(s) had no resolvable id — promoted to doc-level starts)")

    def _vol_label(payload):
        """Payload is either a str (vol_title) or a tuple (vol_title, chap_title).
        Return the volume-level title for either."""
        return payload[0] if isinstance(payload, tuple) else payload

    multi_volume = bool(doc_volume_starts or doc_anchor_splits)
    if multi_volume:
        all_vols = set()
        for v in doc_volume_starts.values():
            all_vols.add(_vol_label(v))
        for lst in doc_anchor_splits.values():
            for _, t in lst:
                all_vols.add(_vol_label(t))
        print(f"Detected {len(all_vols)} volume(s): {sorted(all_vols)}")
    else:
        print("No volume hierarchy detected — flat TOC.")

    chunks = []
    seen_dedupe_keys = set()
    dropped = []
    current_volume = None  # spine-walk running state

    for i, d in enumerate(docs):
        # Volume transition that fires at the START of this doc (no anchor).
        if d.file_name in doc_volume_starts:
            current_volume = doc_volume_starts[d.file_name]

        # Decide whether to split the doc at internal anchors.
        anchors_here = doc_anchor_splits.get(d.file_name, [])
        try:
            if anchors_here:
                soup = BeautifulSoup(d.get_content(), "html.parser")
                body = soup.find("body") or soup
                segments = split_body_at_anchors(body, dict(anchors_here))
            else:
                segments = [(d.get_content(), None)]
        except Exception as e:
            print(f"  ⚠ doc {i} ({d.file_name}) split failed: {e}", file=sys.stderr)
            continue

        for seg_idx, (seg_html, seg_vol_transition) in enumerate(segments):
            # Transition to the new volume at the anchor.
            if seg_vol_transition:
                current_volume = seg_vol_transition

            try:
                md, plain = html_to_markdown(seg_html)
            except Exception as e:
                print(f"  ⚠ doc {i} seg {seg_idx} parse failed: {e}", file=sys.stderr)
                continue

            seg_label = f"{d.file_name}" if len(segments) == 1 else f"{d.file_name}#seg{seg_idx}"

            if (not plain or len(plain) < 5):
                is_cover = (i < 3 and d.file_name and "cover" in d.file_name.lower()
                            or d.file_name == "titlepage.xhtml")
                if is_cover and seg_idx == 0 and "cover" not in seen_dedupe_keys:
                    seen_dedupe_keys.add("cover")
                    chunks.append({
                        "chunk_index": len(chunks),
                        "chunk_type": "chapter",
                        "page_number": None,
                        "chapter_path": "封面",
                        "volume": None,
                        "format": "markdown",
                        "content": "## 封面\n\n*（書本封面）*",
                    })
                    continue
                dropped.append((i, seg_label, "empty"))
                continue

            if is_hard_drop(plain):
                dropped.append((i, seg_label, "publisher boilerplate"))
                continue

            dedupe_key = matched_dedupe_pattern(plain[:50])
            if dedupe_key:
                if dedupe_key in seen_dedupe_keys:
                    dropped.append((i, seg_label, f"duplicate ({dedupe_key})"))
                    continue
                seen_dedupe_keys.add(dedupe_key)

            md_tw = to_traditional(md)
            # Hierarchical payload: current_volume = (vol, chap, level) 3-tuple
            #   (older 2-tuple still accepted for backward compat with hot-loaded code paths)
            # Legacy payload: current_volume = vol_title (str)
            hier_level_override = None
            if isinstance(current_volume, tuple):
                if len(current_volume) >= 3:
                    vol_only, hier_chap, hier_level_override = current_volume[0], current_volume[1], current_volume[2]
                else:
                    vol_only, hier_chap = current_volume[0], current_volume[1]
                volume = to_traditional(vol_only) if vol_only else None
                hier_chap_tw = to_traditional(hier_chap) if hier_chap else None
            else:
                volume = to_traditional(current_volume) if current_volume else None
                hier_chap_tw = None

            # Hierarchical mode wins when TOC gave us a chapter title; the
            # in-content first-heading scan only runs as a fallback.
            chapter_title = hier_chap_tw or derive_chapter_title(md_tw, d.file_name)

            # In hierarchical mode the reader's TOC sidebar derives nesting
            # from each chunk's first heading depth. EPUB bodies often use
            # inconsistent <h1>/<h2>/<h3> for chapter titles (publisher quirk),
            # which makes some chapters render as level-2 sidebar entries and
            # others as level-3+ children of preceding chunks. Force a uniform
            # level for hierarchical chapters: ## when single-volume (no parent
            # volume groups), ### when multi-volume (## reserved for volume).
            if hier_chap_tw:
                # Use payload's level override (when 節 splits are in play)
                target_level = hier_level_override or ("###" if (volume is not None) else "##")
            else:
                target_level = None  # legacy mode — keep original level

            head_match = re.match(r"^(#{1,4})\s+(.+)$", md_tw, re.M)
            if head_match:
                desired_level = target_level or head_match.group(1)
                if (head_match.group(2).strip() != chapter_title
                        or (target_level and head_match.group(1) != target_level)):
                    md_tw = md_tw.replace(
                        head_match.group(0),
                        f"{desired_level} {chapter_title}",
                        1,
                    )
            elif target_level:
                # No heading at all in content — prepend one so the reader
                # sidebar can render this chunk's level correctly.
                md_tw = f"{target_level} {chapter_title}\n\n{md_tw.lstrip()}"
            elif chapter_title:
                # Legacy (flat-TOC) mode + no heading in content. Without this
                # the reader's loadToc derives level=2 from nothing, and any
                # later content line with a `## ...` would mistakenly anchor the
                # sidebar nesting. Force `##` so single-volume books with no
                # hierarchical TOC still get consistent sidebar levels — matches
                # what hierarchical-mode single-volume books emit.
                md_tw = f"## {chapter_title}\n\n{md_tw.lstrip()}"

            # Continuation merge: if this chunk's title is just a numeric/letter
            # marker (e.g. 後記 split into 「後記」+「二」, or 索引 split into A-Z),
            # fold its content into the previous chunk instead of creating a new
            # one. Volume must match — don't merge across volume boundaries.
            # Size cap: only merge tiny continuation chunks. Real chapters that
            # happen to start with <h2>1</h2> markers (academic EPUBs) are big
            # and must NOT be eaten — they are real content even if the title
            # derives to a numeric token.
            CONT_MERGE_MAX_CHARS = 800
            if (chunks and is_continuation_title(chapter_title)
                    and chunks[-1].get("volume") == volume
                    and len(plain) <= CONT_MERGE_MAX_CHARS):
                # Strip the redundant heading line from md_tw before appending —
                # it adds nothing and creates "二 / A" mid-paragraph artifacts.
                stripped_md = re.sub(r"^#{1,4}\s+.+\n+", "", md_tw, count=1).strip()
                if stripped_md:
                    chunks[-1]["content"] = chunks[-1]["content"].rstrip() + "\n\n" + stripped_md
                continue

            # Hierarchical-mode same-chapter merge: when the previous chunk has
            # the EXACT same volume + chapter_path, this is a continuation
            # (cross-spine-doc spillover or multi-page chapter title image).
            # Strip the duplicate heading and append.
            if (using_hier and chunks
                    and chunks[-1].get("volume") == volume
                    and chunks[-1].get("chapter_path") == chapter_title):
                stripped_md = re.sub(r"^#{1,4}\s+.+\n+", "", md_tw, count=1).strip()
                if stripped_md:
                    chunks[-1]["content"] = chunks[-1]["content"].rstrip() + "\n\n" + stripped_md
                continue

            chunks.append({
                "chunk_index": len(chunks),
                "chunk_type": "chapter",
                "page_number": None,
                "chapter_path": chapter_title,
                "volume": volume,
                "format": "markdown",
                "content": md_tw,
            })

    # Post-process. Order matters:
    #   1. promote_implicit_volumes — fix 第N部 chapters mis-tagged as flat
    #   2. apply_cover_enrichment   — needs raw 版權頁 chunk to extract metadata
    #   3. consolidate_frontmatter_into_publisher — runs LAST so the publisher
    #      page that cover_enrichment just sniffed gets folded into 出版資訊
    promote_implicit_volumes(chunks)
    apply_cover_enrichment(chunks, book)
    consolidate_frontmatter_into_publisher(chunks)
    # Fold appendix sub-entries into parent appendix BEFORE rebuilding TOC
    merge_appendix_subentries(chunks)
    # Rebuild 目錄 chunk (or synthesize one) from the now-final structure
    rebuild_toc_chunk(chunks, book)

    print(f"Kept: {len(chunks)} chunks, dropped: {len(dropped)}")
    if dropped[:8]:
        print("  Dropped (sample):")
        for i, fn, why in dropped[:8]:
            print(f"    [{i}] {fn}  — {why}")
    return chunks


def write_jsonl(book_id, chunks):
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHUNKS_DIR / f"{book_id}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return out


def push_to_r2(book_id, jsonl_path):
    import boto3
    raw = Path(jsonl_path).read_bytes()
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
        gz.write(raw)
    c = boto3.client("s3", region_name="auto", endpoint_url=ENV["R2_ENDPOINT"],
                     aws_access_key_id=ENV["R2_ACCESS_KEY"], aws_secret_access_key=ENV["R2_SECRET_KEY"])
    c.put_object(
        Bucket=ENV["R2_BUCKET"],
        Key=f"ebook-chunks/{book_id}.jsonl.gz",
        Body=buf.getvalue(),
        ContentType="application/x-ndjson",
        ContentEncoding="gzip",
    )
    return len(buf.getvalue())


def update_db(book_id, chunks):
    total_chars = sum(len(c["content"]) for c in chunks)

    # Build the patch body: always update counts/timestamps, plus any
    # publisher metadata we managed to extract from 版權頁. Fields are only
    # included when present so we never overwrite a manually-set value with
    # null on a later re-run.
    patch = {
        "chunk_count": len(chunks),
        "total_chars": total_chars,
        "total_pages": len(chunks),
        "parsed_at": datetime.utcnow().isoformat() + "Z",
    }
    meta = _extract_publisher_metadata(chunks)
    if meta["full_title"]:
        # subtitle = part after ':'/':' if the full title contains one
        _, sub = _split_title_subtitle(meta["full_title"])
        if sub:
            patch["subtitle"] = sub
    if meta["original_title"]:        patch["original_title"]        = meta["original_title"]
    if meta["author_en"]:             patch["author_en"]             = meta["author_en"]
    if meta["translator"]:            patch["translator"]            = meta["translator"]
    if meta["publisher"]:             patch["publisher"]             = meta["publisher"]
    if meta["publish_year"]:          patch["publication_year"]      = meta["publish_year"]
    if meta["original_publish_year"]: patch["original_publish_year"] = meta["original_publish_year"]
    if meta["original_author"]:       patch["original_author"]       = meta["original_author"]

    requests.patch(
        f"{URL}/rest/v1/ebooks?id=eq.{book_id}",
        headers=H_JSON,
        json=patch,
        timeout=30,
    )

    # Also refresh ebook_chunks preview rows so search still works.
    requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{book_id}", headers=H_GET, timeout=30)
    rows = [{
        "ebook_id": book_id,
        "chunk_index": c["chunk_index"],
        "chunk_type": c["chunk_type"],
        "page_number": c["page_number"],
        "chapter_path": c["chapter_path"],
        "content": c["content"][:PREVIEW_LEN],
        "char_count": len(c["content"]),
    } for c in chunks]
    BATCH = 50
    for i in range(0, len(rows), BATCH):
        r = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON, json=rows[i:i+BATCH], timeout=60)
        if not r.ok:
            print(f"  ⚠ chunk preview insert failed: {r.status_code} {r.text[:120]}", file=sys.stderr)
            return


def fetch_books_by_category(category: str = None, subcategory: str = None, limit: int = None):
    """Return list of parsed EPUB books, optionally filtered by category. Skips
    PDFs (script can't handle them), books without parsed content, and books
    missing on disk. Pass category=None to fetch every parsed EPUB."""
    params = (
        "select=id,title,author,file_type,file_path,parsed_at,chunk_count,category"
        "&parsed_at=not.is.null"
        "&file_type=eq.epub"
        "&order=category,title"
        "&limit=2000"
    )
    if category:
        params += f"&category=eq.{requests.utils.quote(category)}"
    if subcategory:
        params += f"&subcategory=eq.{requests.utils.quote(subcategory)}"
    r = requests.get(f"{URL}/rest/v1/ebooks?{params}", headers=H_GET, timeout=30)
    r.raise_for_status()
    books = r.json()
    if limit:
        books = books[:limit]
    return books


def standardize_one(ebook_id: str, dry_run: bool = False, no_r2: bool = False):
    """Run the full pipeline on a single book. Returns (chunks_count, error_or_None)."""
    try:
        book = fetch_book(ebook_id)
    except Exception as e:
        return 0, f"fetch failed: {e}"
    if book["file_type"] != "epub":
        return 0, f"not an EPUB ({book['file_type']})"
    if not Path(book["file_path"]).exists():
        return 0, f"file missing: {book['file_path']}"
    try:
        chunks = standardize(book)
    except Exception as e:
        return 0, f"parse failed: {str(e)[:200]}"
    if not chunks:
        return 0, "no chunks produced"
    if dry_run:
        return len(chunks), None
    try:
        out = write_jsonl(ebook_id, chunks)
        if not no_r2:
            push_to_r2(ebook_id, out)
        update_db(ebook_id, chunks)
    except Exception as e:
        return 0, f"persist failed: {str(e)[:200]}"

    # Auto-split fresh 套書 — per feedback memory "套書要拆成個別書", and the
    # 2026-05-14 TODO #4 ("auto-split-on-ingest"). Triggers iff title matches
    # 套書 pattern and book has no annotations. Non-fatal — split failures
    # don't roll back the standardize itself.
    try:
        _maybe_auto_split(ebook_id, book, chunks)
    except Exception as e:
        print(f"  ⚠ auto-split skipped: {str(e)[:160]}", file=sys.stderr)

    return len(chunks), None


def _maybe_auto_split(ebook_id: str, book: dict, chunks: list[dict]) -> None:
    """If `book` is a 套書 and its chunks reveal ≥2 volumes (either already
    populated, or after detect_set_volumes runs Haiku), split it into per-volume
    child ebooks. No-op for non-套書 titles."""
    sys.path.insert(0, str(Path(__file__).parent))
    from split_ebook_set import (
        SET_TITLE_RX, SPLIT_MARKER, NOT_A_SET_MARKER,
        annotations_for, split_one, load_chunks as _load_chunks,
    )
    title = book.get("title") or ""
    if not SET_TITLE_RX.search(title):
        return
    pe = book.get("parse_error") or ""
    if pe.startswith(SPLIT_MARKER) or pe.startswith(NOT_A_SET_MARKER):
        return
    if annotations_for(ebook_id) > 0:
        print(f"  · {title[:40]}: has annotations — auto-split skipped")
        return

    n_with_vol = len(set(c.get("volume") for c in chunks if c.get("volume")))
    if n_with_vol < 2:
        # No volume metadata from standardize — ask Haiku for boundaries.
        try:
            from detect_set_volumes import make_client, process_one as _detect_one
        except ImportError:
            print(f"  · {title[:40]}: detect_set_volumes unavailable", file=sys.stderr)
            return
        print(f"  → {title[:40]}: 套書 w/o volume metadata, running detect_set_volumes…", flush=True)
        client = make_client()
        result = _detect_one(client, book, dry_run=False)
        print(f"    {result}", flush=True)
        # Re-read chunks to see whether detect wrote `volume` field
        new_chunks = _load_chunks(ebook_id) or []
        n_with_vol = len(set(c.get("volume") for c in new_chunks if c.get("volume")))
        if n_with_vol < 2:
            return  # detect marked NOT_A_SET, nothing to split

    print(f"  → {title[:40]}: auto-splitting into {n_with_vol} volumes…", flush=True)
    fresh = fetch_book(ebook_id)
    n_new, err = split_one(fresh)
    if err:
        print(f"  ⚠ auto-split: {err}", flush=True)
    else:
        print(f"  ✓ auto-split: created {n_new} child ebooks (parent deleted)", flush=True)


def cmd_batch(category: str = None, subcategory: str = None, limit: int = None,
              dry_run: bool = False, no_r2: bool = False):
    books = fetch_books_by_category(category, subcategory, limit)
    label = "ALL categories" if not category else f"Category: {category}{f' / {subcategory}' if subcategory else ''}"
    print(label)
    print(f"Eligible EPUBs: {len(books)}")
    if not books:
        print("Nothing to do.")
        return

    if dry_run:
        for b in books[:20]:
            print(f"  - {b['title'][:50]:50s}  /  {(b.get('author') or '')[:20]}  ({b.get('chunk_count','?')} chunks)")
        if len(books) > 20:
            print(f"  ... and {len(books) - 20} more")
        return

    import time as _time
    t0 = _time.time()
    ok = 0
    failed = []
    for i, b in enumerate(books, 1):
        title = (b["title"] or "Untitled")[:40]
        n, err = standardize_one(b["id"], no_r2=no_r2)
        elapsed = _time.time() - t0
        rate = i / elapsed if elapsed else 0
        eta = (len(books) - i) / rate if rate else 0
        if err:
            failed.append((title, err))
            print(f"  [{i:3d}/{len(books)}] ⚠ {title}: {err[:80]}", flush=True)
        else:
            ok += 1
            print(f"  [{i:3d}/{len(books)}] ✓ {title}: {n} chunks  ETA {int(eta)}s", flush=True)

    print(f"\nDone in {_time.time() - t0:.0f}s. OK: {ok}, Failed: {len(failed)}")
    if failed:
        print("Failures:")
        for n, e in failed[:20]:
            print(f"  - {n}: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)

    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    no_r2 = "--no-r2" in args

    if "--all" in args:
        limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
        cmd_batch(category=None, limit=limit, dry_run=dry_run, no_r2=no_r2)
        return

    if "--category" in args:
        category = args[args.index("--category") + 1]
        subcategory = None
        if "--subcategory" in args:
            subcategory = args[args.index("--subcategory") + 1]
        limit = None
        if "--limit" in args:
            limit = int(args[args.index("--limit") + 1])
        cmd_batch(category, subcategory, limit, dry_run, no_r2)
        return

    # Single-book mode
    ebook_id = args[0]
    book = fetch_book(ebook_id)
    print(f"Book: {book['title']}  ({book['file_type']})")
    print(f"Author: {book.get('author')}")
    print()

    chunks = standardize(book)

    if dry_run:
        print("\n--- DRY RUN — first 3 chunks ---")
        for c in chunks[:3]:
            print(f"\n[{c['chunk_index']}] {c['chapter_path']}")
            print(c["content"][:400])
        return

    out = write_jsonl(ebook_id, chunks)
    print(f"\nWrote {out}  ({out.stat().st_size//1024} KB)")

    if not no_r2:
        gz_size = push_to_r2(ebook_id, out)
        print(f"Pushed R2: ebook-chunks/{ebook_id}.jsonl.gz  ({gz_size//1024} KB)")

    update_db(ebook_id, chunks)
    print(f"DB: chunk_count={len(chunks)}, total_chars={sum(len(c['content']) for c in chunks)}")
    print("\n✓ Done. Open the reader — markdown headings should render.")


if __name__ == "__main__":
    main()
