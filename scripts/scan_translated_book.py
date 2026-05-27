"""Scan a translated ebook for LLM-quality bugs that the structural
validator can't catch.

Where this fits:
  validate_book_structure.py  ← structural / TOC / range checks (R001-R022)
  scan_translated_book.py     ← translation-quality checks    (T1-T7)

T1  title-bleed     h3/h4 heading > 30 chars AND contains punctuation
T2  volume-h3 drift content's first h3 disagrees with volume name
T3  title repeated  h3 text reappears verbatim inside body paragraphs
T4  chapter_path bad  contains markdown control chars (* _ `[^N]`)
T5  volume re-entry  same volume name appears in two non-contiguous spans
T6  orphan index    chapter_path 含「索引」but volume isn't 索引/Indexes
T7  cover/front     chunk[0] chapter_path != 「封面」or chunk[1] not 前言/序

Usage:
    python scripts/scan_translated_book.py <ebook_id>
    python scripts/scan_translated_book.py <ebook_id> --json
    python scripts/scan_translated_book.py --all
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# A heading line is title-bleed when body-style language ("connective +
# clause") appears mid-heading. Real CCEL titles describe a noun phrase
# («科林多教會因嫉妒和競爭而陷入分裂後的悲慘狀況»); body bleeds slip
# 連詞 / 第二人稱 vocatives / 副詞 starting a new clause:
#   bleed: 「第一章—書信寫作的契機既然我看到你」       「既然」starts new clause
#   bleed: 「第四章——古代已有許多惡行源自此因蓋經上記著」 「蓋」starts body
#   bleed: 「第十章—上述內容的續論亞伯拉罕被稱為「朋友」」「亞伯拉罕被稱為」 vocative body
# We only check the part AFTER the em-dash so we don't false-positive on
# numbered titles like「第一章—蓋天蓋地」(unlikely but theoretically clean).
HEADING_LINE_RE = re.compile(r"^(#{3,4})\s+(.+?)\s*$", re.M)
EM_DASH_SPLIT_RE = re.compile(r"(?:第[一二三四五六七八九十百千零0-9]+章\s*[—\-－]+\s*)(.+)")
TITLE_CLOSE_PUNCT = re.compile(r"[。！？」）]\s*$")  # heading ends with closure
# Body markers — when present mid-heading (i.e. not at position 0 of the
# post-emdash portion) signal a clause break that doesn't belong in a
# title. Curated from observed bleeds.
BODY_MARKERS = [
    "既然", "誠然", "親愛的", "讓我們", "誠如",
    "若你", "若我", "蓋此", "蓋我", "蓋經上", "蓋誠",
    "雖然", "但關於", "但是我", "然而我",
    "因此我", "正如我", "我先前", "我所說", "只要前一",
    "亞伯拉罕被", "本書信", "在已過去", "從一開始",
]

# Markdown control chars that shouldn't appear inside a clean chapter_path
BAD_CP_CHARS = re.compile(r"[\*_`]|\[\^\d+\]")

# Front-matter chapter_paths we DO expect for chunk 0 / 1
FRONT_MATTER_OK_CHUNK0 = {"封面"}
FRONT_MATTER_OK_CHUNK1 = {"前言", "序言", "書名頁", "前言／序"}

# Index labels — chunks with these in chapter_path should sit under an
# index-style volume, not under the last author's volume (the fallback
# bug we saw: 印刷版頁碼索引 attached to 愛任紐《駁異端》).
INDEX_PATH_RE = re.compile(r"索引|目錄|Index", re.I)
INDEX_VOLUME_RE = re.compile(r"索引|Indexes", re.I)


class Issue:
    __slots__ = ("rule", "severity", "chunk_index", "message")

    def __init__(self, rule: str, severity: str,
                 chunk_index: Optional[int], message: str):
        self.rule = rule
        self.severity = severity
        self.chunk_index = chunk_index
        self.message = message

    def to_dict(self):
        return {"rule": self.rule, "severity": self.severity,
                "chunk_index": self.chunk_index, "message": self.message}


def load_jsonl(ebook_id: str) -> Optional[list[dict]]:
    fn = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not fn.exists():
        return None
    return [json.loads(l) for l in fn.read_text(encoding="utf-8").splitlines() if l]


def fetch_book(ebook_id: str) -> Optional[dict]:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=id,title,chunk_count",
                     headers=H_GET, timeout=30)
    if r.status_code != 200:
        return None
    rows = r.json()
    return rows[0] if rows else None


def strip_md(s: str) -> str:
    """Strip markdown markers from a heading line for length measurement."""
    s = re.sub(r"\[\^\d+\]", "", s)        # footnote refs
    s = re.sub(r"\{\{p:\d+\}\}", "", s)    # page markers
    s = re.sub(r"\*+", "", s)              # bold/italic markers
    return s.strip()


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def scan(ebook_id: str) -> list[Issue]:
    issues: list[Issue] = []
    chunks = load_jsonl(ebook_id)
    if not chunks:
        return [Issue("ENV", "FAIL", None, f"JSONL not found / empty: {ebook_id}")]

    # ── T1 title-bleed ──
    for c in chunks:
        idx = c.get("chunk_index")
        for m in HEADING_LINE_RE.finditer(c.get("content") or ""):
            heading_text = strip_md(m.group(2))
            # Only inspect chapter-numbered headings; non-numbered headings
            # are letter titles or section names and have their own shape.
            tail_m = EM_DASH_SPLIT_RE.match(heading_text)
            if not tail_m:
                continue
            tail = tail_m.group(1)
            # If the heading closes with 「。！？」）」, the body marker is
            # part of a legitimate descriptive exhortation title
            # (e.g.「第二十七章——在復活的盼望中，讓我們緊貼…的上帝。」).
            if TITLE_CLOSE_PUNCT.search(tail):
                continue
            for marker in BODY_MARKERS:
                pos = tail.find(marker)
                if pos >= 2:  # not at the very start
                    issues.append(Issue("T1", "WARN", idx,
                        f"heading body-marker '{marker}' at pos {pos} in: {heading_text[:60]}"))
                    break

    # ── T2 volume vs first-h3 drift ──
    # For each chunk that has a volume, find the first h2/h3 in content.
    # If that heading is a "Letter title" (e.g. 「瑪忒特致狄奧格尼特斯書信」),
    # it should be similar to the volume name 「致丟格那妥書」.
    # We only flag when similarity is < 0.4 (very different), to avoid
    # noisy false positives on chapter headings.
    for c in chunks:
        idx = c.get("chunk_index")
        vol = (c.get("volume") or "").strip()
        if not vol:
            continue
        content = c.get("content") or ""
        # First non-chapter heading inside the chunk = the letter title.
        # The consolidator emits the letter title as h3 (### ...), then
        # individual chapters as h4 (#### 第一章—...). So we want the
        # first h3 that ISN'T a chapter heading (doesn't match 第X章).
        first_letter_title = None
        for m in re.finditer(r"^#{2,3}\s+(.+?)\s*$", content, re.M):
            t = strip_md(m.group(1))
            if not re.match(r"第[一二三四五六七八九十百千零0-9]+章", t):
                first_letter_title = t
                break
        if not first_letter_title:
            continue
        first_h2 = first_letter_title
        # Drop trailing chapter-range tag from volume if any
        vol_core = re.sub(r"\s*第\d+(-\d+)?章\s*$", "", vol)
        if similar(first_h2, vol_core) < 0.4 and len(first_h2) > 4:
            issues.append(Issue("T2", "WARN", idx,
                f"first H2 '{first_h2}' diverges from volume '{vol_core}'"))

    # ── T3 chapter_path appears again in body ──
    # When chapter_path is also a heading inside the body it's harmless
    # (that's expected). We only flag when the chapter_path is found in a
    # *paragraph* line of the content — that means the consolidator pulled
    # a body sentence up as a heading and the original sits stuck in prose.
    # Implementation kept loose for now.
    # (No T3 emitted by default; placeholder for later expansion.)

    # ── T4 chapter_path control chars ──
    for c in chunks:
        idx = c.get("chunk_index")
        cp = c.get("chapter_path", "")
        if BAD_CP_CHARS.search(cp):
            issues.append(Issue("T4", "WARN", idx,
                f"chapter_path has markdown/footnote chars: {cp}"))

    # ── T5 volume re-entry ──
    # For each volume name, record the chunk_index span where it appears.
    # If indices are non-contiguous (e.g. 14-16 then 96 again), that's a
    # split / orphan attachment.
    by_vol: dict[str, list[int]] = defaultdict(list)
    for c in chunks:
        vol = c.get("volume")
        if not vol:
            continue
        by_vol[vol].append(c.get("chunk_index"))
    for vol, idxs in by_vol.items():
        if len(idxs) < 2:
            continue
        idxs_sorted = sorted(idxs)
        # Detect gaps: a gap of >2 between consecutive entries is suspicious
        # (1 means contiguous; 2 tolerates a single interleaved divider).
        for a, b in zip(idxs_sorted, idxs_sorted[1:]):
            if b - a > 2:
                issues.append(Issue("T5", "WARN", b,
                    f"volume '{vol}' re-enters at {b} after gap (last seen {a})"))
                break

    # ── T6 orphan index page ──
    for c in chunks:
        idx = c.get("chunk_index")
        cp = c.get("chapter_path", "")
        vol = c.get("volume", "")
        if INDEX_PATH_RE.search(cp) and not INDEX_VOLUME_RE.search(vol or ""):
            # 「目錄」也算 — front matter where volume is None is OK
            if vol:
                issues.append(Issue("T6", "WARN", idx,
                    f"index-like chapter_path '{cp}' attached to volume '{vol}'"))

    # ── T7 cover / preface naming ──
    if chunks:
        cp0 = chunks[0].get("chapter_path", "")
        if cp0 not in FRONT_MATTER_OK_CHUNK0:
            issues.append(Issue("T7", "WARN", 0,
                f"chunk 0 chapter_path is '{cp0}', expected one of {FRONT_MATTER_OK_CHUNK0}"))
    if len(chunks) > 1:
        cp1 = chunks[1].get("chapter_path", "")
        if cp1 not in FRONT_MATTER_OK_CHUNK1:
            issues.append(Issue("T7", "INFO", 1,
                f"chunk 1 chapter_path is '{cp1}', expected one of {FRONT_MATTER_OK_CHUNK1}"))

    return issues


def report(ebook_id: str, issues: list[Issue], title: str = "") -> tuple[int, int]:
    print(f"\n=== {title or ebook_id} ===")
    if not issues:
        print("  ✓ scan clean")
        return 0, 0
    by_rule = defaultdict(list)
    for i in issues:
        by_rule[i.rule].append(i)
    warn = info = 0
    for rule in sorted(by_rule):
        lst = by_rule[rule]
        sev = lst[0].severity
        sym = "⚠" if sev == "WARN" else "i"
        print(f"\n  {sym} [{rule}] {len(lst)} issue{'s' if len(lst)>1 else ''}")
        for it in lst[:8]:
            loc = f"chunk {it.chunk_index}" if it.chunk_index is not None else "book"
            print(f"    · {loc}: {it.message}")
        if len(lst) > 8:
            print(f"    · ... +{len(lst)-8} more")
        if sev == "WARN":
            warn += len(lst)
        else:
            info += len(lst)
    print(f"\n  Totals: {warn} WARN · {info} INFO")
    return warn, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.all:
        # Scan every ebook whose JSONL exists locally
        jsonls = sorted(CHUNKS_DIR.glob("*.jsonl"))
        all_results = []
        for jp in jsonls:
            eid = jp.stem
            book = fetch_book(eid)
            title = book["title"] if book else eid
            issues = scan(eid)
            if args.json:
                all_results.append({
                    "ebook_id": eid, "title": title,
                    "issues": [i.to_dict() for i in issues],
                })
            else:
                report(eid, issues, title)
        if args.json:
            print(json.dumps(all_results, ensure_ascii=False, indent=2))
        return

    if not args.ebook_id:
        sys.exit("usage: scan_translated_book.py <ebook_id> | --all")
    book = fetch_book(args.ebook_id)
    title = book["title"] if book else args.ebook_id
    issues = scan(args.ebook_id)
    if args.json:
        print(json.dumps({
            "ebook_id": args.ebook_id, "title": title,
            "issues": [i.to_dict() for i in issues],
        }, ensure_ascii=False, indent=2))
        return
    report(args.ebook_id, issues, title)


if __name__ == "__main__":
    main()
