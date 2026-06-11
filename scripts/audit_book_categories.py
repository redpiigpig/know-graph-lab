#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only categorization audit (no writes).

Runs the new offline book_classifier over every existing `ebooks` row and
reports where it *confidently* disagrees with the stored category. This is a
SUSPECT LIST for human review, NOT an auto-fix — the stored categories are
partly hand-curated and must not be clobbered.

Usage:
  python scripts/audit_book_categories.py            # writes _category_audit.txt
"""
import collections
import sys
from pathlib import Path

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent))
import book_classifier as bc

# High-confidence disagreement threshold: only flag when the local scorer is
# quite sure, to keep the review list short and high-signal.
FLAG_CONFIDENCE = 0.5


def load_env():
    env = {}
    for line in open(Path(__file__).parent.parent / ".env", encoding="utf-8-sig"):
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main():
    env = load_env()
    URL, KEY = env["SUPABASE_URL"], env["SUPABASE_SERVICE_ROLE_KEY"]
    H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

    rows = []
    step = 1000
    offset = 0
    while True:
        chunk = requests.get(
            f"{URL}/rest/v1/ebooks?select=id,title,author,category,subcategory"
            f"&order=id&offset={offset}&limit={step}",
            headers=H, timeout=120,
        ).json()
        rows.extend(chunk)
        if len(chunk) < step:
            break
        offset += step

    disagree = []        # local-confident AND != stored
    uncertain = []       # local can't place (would have gone to review queue)
    review_now = []      # already sitting in the review queue / default dump
    by_stored = collections.Counter()

    for b in rows:
        stored = b.get("category") or "(none)"
        by_stored[stored] += 1
        if stored in ("_待審分類",):
            review_now.append(b)
        r = bc.classify(b.get("title") or "", b.get("author") or "")
        if r.category is None or r.uncertain:
            uncertain.append(b)
            continue
        if r.category != stored:
            disagree.append((b, r))

    disagree.sort(key=lambda x: -x[1].confidence)

    out = Path("_category_audit.txt")
    with out.open("w", encoding="utf-8") as f:
        f.write(f"ebooks total: {len(rows)}\n")
        f.write(f"high-confidence disagreements (≥{FLAG_CONFIDENCE}): "
                f"{sum(1 for _, r in disagree if r.confidence >= FLAG_CONFIDENCE)}\n")
        f.write(f"all disagreements: {len(disagree)}\n")
        f.write(f"local-uncertain (no clear signal): {len(uncertain)}\n")
        f.write(f"already in review queue: {len(review_now)}\n\n")

        f.write("=== HIGH-CONFIDENCE DISAGREEMENTS (review these) ===\n")
        for b, r in disagree:
            if r.confidence < FLAG_CONFIDENCE:
                continue
            f.write(f"  [{b.get('category')!r} → {r.category!r}] conf={r.confidence} "
                    f"| {(b.get('title') or '')[:60]!r} by {(b.get('author') or '')[:24]!r}"
                    f"  ({r.reason})\n")

        f.write("\n=== LOWER-CONFIDENCE DISAGREEMENTS (maybe) ===\n")
        for b, r in disagree:
            if r.confidence >= FLAG_CONFIDENCE:
                continue
            f.write(f"  [{b.get('category')!r} → {r.category!r}] conf={r.confidence} "
                    f"| {(b.get('title') or '')[:60]!r}\n")

    # console summary (ascii-safe)
    n_high = sum(1 for _, r in disagree if r.confidence >= FLAG_CONFIDENCE)
    print(f"ebooks total:               {len(rows)}")
    print(f"high-conf disagreements:    {n_high}")
    print(f"all disagreements:          {len(disagree)}")
    print(f"local-uncertain:            {len(uncertain)}")
    print(f"already in review queue:    {len(review_now)}")
    print(f"\nfull report -> {out}")


if __name__ == "__main__":
    main()
