"""Validate ebook JSONL structure against the consolidated-reader spec.

The spec — what a "well-formed" book looks like AFTER the pipeline
(translate → polish → extract_epub_extras → consolidate_by_ncx):

  STRUCTURAL (FAIL on violation)
    R001  chunk_index forms contiguous 0..N-1 sequence
    R002  chunk_type ∈ {page, chapter, section}
    R003  every chunk has non-empty `content`
    R004  every chunk has non-empty `chapter_path`

  TOC NAMING (WARN on violation; pipeline output should pass)
    R010  chapter_path ≤ 35 chars (catches title-bleed where heading regex
           sucked in body text)
    R011  if `volume` set: chapter_path starts with volume name
           (avoids the bleed we saw: chunk tagged 「依納爵致坡旅甲書」
           with chapter_path 「依納爵致士每拿人書 第1-10章」)
    R012  no two chunks share an identical chapter_path within same volume
           (catches Irenaeus 5-book bleed where every book labeled 卷一)
    R013  chapter ranges within volume are contiguous (gaps like 1-10 /
           21-30 / 11-20 are bugs)
    R014  chapter ranges within volume non-overlapping
    R015  page numbers monotonically increasing across chunks
           (page_numbers from extract_epub_extras should ascend)

  CONTENT QUALITY (INFO; reportable but not failing)
    R020  source_text has [^N] refs if footnotes dict is populated
    R021  every chunk has at least one h2/h3/h4 heading in content
    R022  volume-less chunks should be <10% of total (front matter cap)

Usage:
    python scripts/validate_book_structure.py <ebook_id>
    python scripts/validate_book_structure.py --all
    python scripts/validate_book_structure.py <ebook_id> --json > out.json

Exit codes:
    0 — all FAIL-severity rules passed
    1 — at least one FAIL-severity rule violated
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from collections import defaultdict
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
                  or r"G:\我的雲端硬碟\資料\知識圖工作室\_chunks")

ALLOWED_CHUNK_TYPES = {"page", "chapter", "section"}

# Range parser: matches 「第N-M章」or 「第N章」at end of chapter_path
RANGE_RE = re.compile(r"第(\d+)(?:-(\d+))?章\s*$")


class Issue:
    __slots__ = ("rule", "severity", "chunk_index", "message")

    def __init__(self, rule: str, severity: str, chunk_index: Optional[int], message: str):
        self.rule = rule
        self.severity = severity
        self.chunk_index = chunk_index
        self.message = message

    def __repr__(self):
        return f"<{self.severity} {self.rule} [chunk={self.chunk_index}] {self.message}>"

    def to_dict(self):
        return {
            "rule": self.rule, "severity": self.severity,
            "chunk_index": self.chunk_index, "message": self.message,
        }


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


def parse_range(chapter_path: str, volume: Optional[str]) -> Optional[tuple[int, int]]:
    """Extract (start, end) chapter numbers from chapter_path of the form
    「volume 第1-10章」or 「volume 第5章」. Returns None if no range found."""
    m = RANGE_RE.search(chapter_path)
    if not m:
        return None
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else start
    return (start, end)


def validate(ebook_id: str) -> list[Issue]:
    issues: list[Issue] = []
    chunks = load_jsonl(ebook_id)
    if chunks is None:
        return [Issue("ENV", "FAIL", None, f"JSONL not found at {CHUNKS_DIR}/{ebook_id}.jsonl")]
    if not chunks:
        return [Issue("ENV", "FAIL", None, "JSONL is empty")]

    n = len(chunks)

    # ── R001 chunk_index contiguous ──
    indices = [c.get("chunk_index") for c in chunks]
    expected = list(range(n))
    if indices != expected:
        # Identify first divergence
        for i, (a, b) in enumerate(zip(indices, expected)):
            if a != b:
                issues.append(Issue("R001", "FAIL", i,
                    f"chunk_index gap/duplicate at position {i}: got {a}, expected {b}"))
                break

    # ── R002 chunk_type valid ──
    for c in chunks:
        ct = c.get("chunk_type")
        if ct not in ALLOWED_CHUNK_TYPES:
            issues.append(Issue("R002", "FAIL", c.get("chunk_index"),
                f"chunk_type '{ct}' not in {ALLOWED_CHUNK_TYPES}"))

    # ── R003 / R004 content + chapter_path non-empty ──
    for c in chunks:
        if not (c.get("content") or "").strip():
            issues.append(Issue("R003", "FAIL", c.get("chunk_index"),
                "content is empty"))
        if not (c.get("chapter_path") or "").strip():
            issues.append(Issue("R004", "FAIL", c.get("chunk_index"),
                "chapter_path is empty"))

    # ── R010 chapter_path length ──
    for c in chunks:
        cp = c.get("chapter_path", "")
        if len(cp) > 35:
            issues.append(Issue("R010", "WARN", c.get("chunk_index"),
                f"chapter_path is {len(cp)} chars (>35): {cp[:60]}…"))

    # ── R011 chapter_path matches volume ──
    for c in chunks:
        vol = c.get("volume")
        cp = c.get("chapter_path", "")
        if not vol or not cp:
            continue
        if not (cp.startswith(vol) or cp == vol):
            issues.append(Issue("R011", "WARN", c.get("chunk_index"),
                f"volume mismatch: vol='{vol}' but chapter_path='{cp}'"))

    # ── R012 / R013 / R014 — per-volume range checks ──
    by_vol: dict[str, list[tuple[int, str, Optional[tuple[int, int]]]]] = defaultdict(list)
    for c in chunks:
        vol = c.get("volume")
        if not vol:
            continue
        cp = c.get("chapter_path", "")
        rng = parse_range(cp, vol)
        by_vol[vol].append((c.get("chunk_index"), cp, rng))

    for vol, entries in by_vol.items():
        # R012 — duplicate chapter_path
        seen = {}
        for idx, cp, _ in entries:
            if cp in seen:
                issues.append(Issue("R012", "WARN", idx,
                    f"duplicate chapter_path in volume '{vol}': "
                    f"chunks {seen[cp]} and {idx} both '{cp}'"))
            else:
                seen[cp] = idx

        # R013 / R014 — range contiguity + overlap
        ranges = [(idx, rng) for idx, _, rng in entries if rng is not None]
        ranges.sort(key=lambda x: x[1][0])  # sort by start chapter
        prev_end = 0
        for idx, (start, end) in ranges:
            if start <= prev_end:
                issues.append(Issue("R014", "WARN", idx,
                    f"chapter range overlap in '{vol}': {start}-{end} "
                    f"overlaps with prior end {prev_end}"))
            elif start > prev_end + 1 and prev_end > 0:
                issues.append(Issue("R013", "WARN", idx,
                    f"chapter range gap in '{vol}': prior end {prev_end} → "
                    f"this start {start} (skipped {prev_end+1}-{start-1})"))
            prev_end = max(prev_end, end)

    # ── R015 page_numbers monotonic across chunks ──
    last_pg = 0
    for c in chunks:
        pgs = c.get("page_numbers") or []
        if not pgs:
            continue
        first_pg = pgs[0]
        if first_pg < last_pg:
            issues.append(Issue("R015", "INFO", c.get("chunk_index"),
                f"page_numbers regression: this chunk starts at {first_pg} "
                f"but a prior chunk had {last_pg}"))
        last_pg = max(last_pg, pgs[-1] if pgs else 0)

    # ── R020 source_text has [^N] refs if footnotes present ──
    for c in chunks:
        fn_dict = c.get("footnotes") or {}
        src = c.get("source_text") or ""
        if fn_dict and not re.search(r"\[\^\d+\]", src):
            issues.append(Issue("R020", "INFO", c.get("chunk_index"),
                f"chunk has {len(fn_dict)} footnotes but source_text "
                f"contains no [^N] refs"))

    # ── R021 content has at least one heading ──
    for c in chunks:
        content = c.get("content") or ""
        if not re.search(r"^#{2,4}\s+\S", content, re.M):
            issues.append(Issue("R021", "INFO", c.get("chunk_index"),
                f"content has no h2/h3/h4 heading"))

    # ── R022 volume-less chunk ratio ──
    no_vol = sum(1 for c in chunks if not c.get("volume"))
    ratio = no_vol / n
    if ratio > 0.10:
        issues.append(Issue("R022", "INFO", None,
            f"{no_vol}/{n} ({ratio*100:.0f}%) chunks have no volume — "
            "consolidator may have missed some letters"))

    return issues


def report(ebook_id: str, issues: list[Issue], book_title: str = "") -> tuple[int, int, int]:
    """Print pretty report. Returns (fail_count, warn_count, info_count)."""
    title = book_title or ebook_id
    print(f"\n=== {title} ===")
    counts = {"FAIL": 0, "WARN": 0, "INFO": 0}
    for i in issues:
        counts[i.severity] = counts.get(i.severity, 0) + 1
    if not issues:
        print(f"  ✓ all checks passed")
        return 0, 0, 0
    # Group by rule
    by_rule = defaultdict(list)
    for i in issues:
        by_rule[i.rule].append(i)
    # Print FAILs first, then WARNs, then INFOs
    for severity in ("FAIL", "WARN", "INFO"):
        relevant = [(r, lst) for r, lst in by_rule.items() if any(i.severity == severity for i in lst)]
        if not relevant:
            continue
        sym = {"FAIL": "✗", "WARN": "⚠", "INFO": "i"}[severity]
        print(f"\n  {sym} {severity}:")
        for rule, lst in sorted(relevant):
            sev_lst = [i for i in lst if i.severity == severity]
            print(f"    [{rule}] ({len(sev_lst)} issue{'s' if len(sev_lst)>1 else ''})")
            for issue in sev_lst[:5]:
                chunk = f"chunk {issue.chunk_index}" if issue.chunk_index is not None else "book-level"
                print(f"      · {chunk}: {issue.message}")
            if len(sev_lst) > 5:
                print(f"      · ... +{len(sev_lst)-5} more")
    print(f"\n  Totals: {counts['FAIL']} FAIL  ·  {counts['WARN']} WARN  ·  {counts['INFO']} INFO")
    return counts["FAIL"], counts["WARN"], counts["INFO"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id", nargs="?")
    ap.add_argument("--all", action="store_true",
                    help="Validate every JSONL in the chunks dir")
    ap.add_argument("--json", action="store_true",
                    help="Output JSON (one line per book), suitable for CI")
    args = ap.parse_args()

    targets: list[str]
    if args.all:
        targets = sorted([p.stem for p in CHUNKS_DIR.glob("*.jsonl")])
    elif args.ebook_id:
        targets = [args.ebook_id]
    else:
        sys.exit("usage: validate_book_structure.py <ebook_id> | --all")

    total_fail = 0
    if args.json:
        for eb in targets:
            issues = validate(eb)
            print(json.dumps({
                "ebook_id": eb,
                "issues": [i.to_dict() for i in issues],
                "fail_count": sum(1 for i in issues if i.severity == "FAIL"),
            }, ensure_ascii=False))
            total_fail += sum(1 for i in issues if i.severity == "FAIL")
    else:
        for eb in targets:
            book = fetch_book(eb)
            title = book.get("title", "") if book else ""
            issues = validate(eb)
            f, _, _ = report(eb, issues, title)
            total_fail += f

    sys.exit(1 if total_fail > 0 else 0)


if __name__ == "__main__":
    main()
