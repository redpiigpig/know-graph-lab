"""Merge static + LLM-text + LLM-vision proofreader outputs into a single
prioritized review report.

Inputs (all auto-located by ebook_id):
  - JSONL of the book
  - scripts/logs/proofread_<id>.json        (B — Haiku text)
  - scripts/logs/vision_proofread_<id>.json (C — Haiku vision)
  - Static scan run inline                  (A — T1-T11)

Output: scripts/logs/REVIEW_<id>.md         (human-readable per-chunk list)
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
from scan_translated_book import scan  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# Issue-type → priority weight. Higher = more disruptive / actionable.
PRIORITY = {
    "ATTRIBUTION": 10,    # cross-work bleed — high
    "FOOTNOTE_BLEED": 9,  # body in footnote area
    "HEADING": 8,         # mislabeled heading
    "T9": 10, "T2": 7,    # static cross-bleed / h3 drift
    "TERM": 5,            # term inconsistency
    "T1": 4,              # title bleed
    "TRANSLATION": 4,     # translation drift
    "FOOTNOTE": 3, "T10": 3,
    "T11": 2, "LAYOUT": 2, "FONT": 2, "MISSING": 2,
    "STRUCTURE": 5, "OTHER": 1,
    "T4": 1, "T5": 3, "T6": 6, "T7": 3,
}


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    return r.json()[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    args = ap.parse_args()
    eid = args.ebook_id

    book = fetch_book(eid)
    jsonl = CHUNKS_DIR / f"{eid}.jsonl"
    chunks = [json.loads(l) for l in jsonl.read_text(encoding="utf-8").splitlines() if l]
    chapter_paths = {c["chunk_index"]: c.get("chapter_path", "")
                     for c in chunks}

    # ── A: static scan ──
    A_issues = scan(eid)
    print(f"A (static): {len(A_issues)} issues")

    # ── B: text proofread ──
    b_path = ROOT / "scripts" / "logs" / f"proofread_{eid}.json"
    B = json.loads(b_path.read_text(encoding="utf-8")) if b_path.exists() else {"results": []}
    print(f"B (text):   {sum(len(r.get('issues',[])) for r in B['results'])} issues")

    # ── C: vision proofread ──
    c_path = ROOT / "scripts" / "logs" / f"vision_proofread_{eid}.json"
    C = json.loads(c_path.read_text(encoding="utf-8")) if c_path.exists() else {"results": []}
    print(f"C (vision): {sum(len(r.get('issues',[])) for r in C['results'])} issues")

    # Aggregate per chunk_index
    per_chunk: dict[int, list[dict]] = defaultdict(list)
    for iss in A_issues:
        if iss.chunk_index is None:
            continue
        per_chunk[iss.chunk_index].append({
            "source": "A",
            "type": iss.rule,
            "severity": iss.severity,
            "description": iss.message,
        })
    for res in B["results"]:
        ci = res.get("chunk_index")
        if ci is None:
            continue
        for iss in res.get("issues", []):
            per_chunk[ci].append({
                "source": "B",
                "type": iss.get("type", "OTHER"),
                "severity": iss.get("severity", "WARN"),
                "description": iss.get("description", ""),
                "snippet": iss.get("snippet", ""),
            })
    for res in C["results"]:
        # vision keys by `page` (1-indexed); chunks 0-indexed
        page = res.get("page")
        if page is None:
            continue
        ci = page - 1
        for iss in res.get("issues", []):
            per_chunk[ci].append({
                "source": "C",
                "type": iss.get("type", "OTHER"),
                "severity": iss.get("severity", "WARN"),
                "description": iss.get("description", ""),
                "where": iss.get("where", ""),
            })

    # Score each chunk for priority sort
    def score(items: list[dict]) -> int:
        return sum(PRIORITY.get(it["type"], 1) *
                   (2 if it["severity"] == "WARN" else 1)
                   for it in items)

    chunks_sorted = sorted(per_chunk.items(), key=lambda kv: -score(kv[1]))

    # ── Write markdown report ──
    out = ROOT / "scripts" / "logs" / f"REVIEW_{eid}.md"
    lines: list[str] = []
    lines.append(f"# 校對報告 — {book['title']}")
    lines.append("")
    lines.append(f"來源：A 靜態規則 (T1-T11) + B Haiku 文字 + C Haiku Vision")
    lines.append(f"總 chunks 有問題：**{len(per_chunk)} / {len(chunks)}**")
    lines.append("")

    # Overall by type
    type_counts: dict[str, int] = defaultdict(int)
    for items in per_chunk.values():
        for it in items:
            type_counts[it["type"]] += 1
    lines.append("## Issues by type")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|---|---|")
    for t, n in sorted(type_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {t} | {n} |")
    lines.append("")

    # Per-chunk listings — ordered by priority score
    lines.append("## 按優先序排列（最緊急在最前）")
    lines.append("")
    for ci, items in chunks_sorted:
        sc = score(items)
        cp = chapter_paths.get(ci, "?")
        page = ci + 1
        lines.append(f"### chunk {ci} · p{page} · {cp} [priority={sc}, {len(items)} issues]")
        lines.append("")
        # Group by source within chunk
        by_src = defaultdict(list)
        for it in items:
            by_src[it["source"]].append(it)
        for src in ("A", "B", "C"):
            if not by_src[src]:
                continue
            label = {"A": "A 靜態", "B": "B 文字 LLM", "C": "C Vision LLM"}[src]
            lines.append(f"**{label}**")
            lines.append("")
            for it in by_src[src]:
                t = it["type"]
                sev = it["severity"]
                desc = it["description"]
                extra = []
                if it.get("snippet"):
                    extra.append(f"`{it['snippet'][:50]}...`")
                if it.get("where"):
                    extra.append(f"位置: {it['where']}")
                extra_s = " — " + " · ".join(extra) if extra else ""
                lines.append(f"- [{t}/{sev}] {desc}{extra_s}")
            lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✓ wrote {out}  ({out.stat().st_size//1024} KB)")
    print(f"\nTop 10 chunks by priority:")
    for ci, items in chunks_sorted[:10]:
        sc = score(items)
        cp = chapter_paths.get(ci, "?")
        print(f"  chunk {ci:3d} ({cp[:35]:35s}): score={sc}, {len(items)} issues")


if __name__ == "__main__":
    main()
