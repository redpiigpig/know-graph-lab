#!/usr/bin/env python3
"""
add_missing_dates.py — insert missing龐 sermon dates into queue txt files.

These are dates the user told us are 龐 sermons but have no YouTube URL
(special services, holidays, etc.). We add them to the year file with
a special marker so they're tracked but the pipeline skips them.

Usage:
  python add_missing_dates.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE_DIR = ROOT / "pong-archive" / "stores" / "城中教會講道清單"

# (date, title) — entries to add. Marker will be "# 📅 無錄影" (date, no recording)
MISSING = [
    ("2020-02-26", "聖灰日禮拜"),
    ("2020-12-24", "平安夜燭光禮拜"),
    ("2021-02-17", "聖灰日聯合禮拜"),
    ("2021-04-02", "聖週五受難日晚聯合崇拜"),
    ("2021-11-20", "城中教會成立六十週年感恩禮拜"),
    ("2021-12-24", "平安夜燭光禮拜"),
    ("2022-03-02", "聖灰日禮拜"),
    ("2022-11-13", "聖靈降臨節後第廿三主日"),
    ("2022-12-24", "平安夜燭光禮拜"),
    ("2023-04-09", "復活主日"),
    ("2024-10-13", "聖靈降臨節後第廿一主日"),
    ("2025-12-24", "平安夜燭光禮拜"),
]


def parse_year_blocks(text):
    """Parse a year file into a list of (marker, title_line, url_line, blank).

    Returns list of dicts: {marker, date, title, url} sorted by date.
    """
    lines = text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#"):
            marker = line.rstrip()
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines):
                break
            title_line = lines[j].strip()
            m = re.match(r"^(\d{4}-\d{2}-\d{2})\s+(.*)", title_line)
            if not m:
                i = j + 1
                continue
            date = m.group(1)
            title = m.group(2)
            k = j + 1
            while k < len(lines) and not lines[k].strip():
                k += 1
            url = lines[k].strip() if k < len(lines) else ""
            blocks.append({"marker": marker, "date": date, "title": title, "url": url})
            i = k + 1
        else:
            i += 1
    return blocks


def render_blocks(blocks):
    """Sort by date and render as a year file."""
    blocks.sort(key=lambda b: b["date"])
    out = []
    for b in blocks:
        out.append(b["marker"])
        out.append(f"{b['date']} {b['title']}")
        if b["url"]:
            out.append(b["url"])
        else:
            out.append("(無錄影)")
        out.append("")
    return "\n".join(out)


def main():
    by_year = {}
    for date, title in MISSING:
        year = date[:4]
        by_year.setdefault(year, []).append((date, title))

    for year, entries in by_year.items():
        p = QUEUE_DIR / f"城中教會講道_{year}.txt"
        text = p.read_text(encoding="utf-8")
        blocks = parse_year_blocks(text)
        existing_dates = {b["date"] for b in blocks}

        added = 0
        for date, title in entries:
            if date in existing_dates:
                print(f"  {date}: already in queue, skipping")
                continue
            blocks.append({
                "marker": "# 📅 無錄影",
                "date": date,
                "title": title,
                "url": "",
            })
            print(f"  {date}: added — {title}")
            added += 1

        if added > 0:
            new_text = render_blocks(blocks)
            p.write_text(new_text + "\n", encoding="utf-8")
            print(f"  → wrote {p.name} ({added} new)")


if __name__ == "__main__":
    main()
