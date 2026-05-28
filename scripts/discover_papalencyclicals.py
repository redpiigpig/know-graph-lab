"""
Discover all documents for a pope on papalencyclicals.net.

The site organises documents under https://www.papalencyclicals.net/category/{popekey}/
(e.g. pius09, leo13, greg16, ben14, urban8, leoX, innocent3, etc.) — each item is rendered
inside an <article> with an <a> linking to the doc page and a trailing span with the date.

Output: JSON list of {slug, title, subtitle, date, url} (one entry per <article>).

Usage:
  python scripts/discover_papalencyclicals.py --pope-key pius09 --out tmp/p9_list.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Tag  # type: ignore
except ImportError:
    print("ERROR: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


USER_AGENT = "Mozilla/5.0 (compatible; know-graph-lab papal discoverer)"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode("utf-8", errors="replace")


_MONTH = {
    "january": "01", "jan": "01",
    "february": "02", "feb": "02",
    "march": "03", "mar": "03",
    "april": "04", "apr": "04",
    "may": "05",
    "june": "06", "jun": "06",
    "july": "07", "jul": "07",
    "august": "08", "aug": "08",
    "september": "09", "sep": "09", "sept": "09",
    "october": "10", "oct": "10",
    "november": "11", "nov": "11",
    "december": "12", "dec": "12",
}


def parse_date(s: str) -> str:
    """Try to extract YYYY-MM-DD from a free-form date string."""
    s = s.strip()
    # 1) ISO already
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    # 2) "December 8, 1864"
    m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", s)
    if m:
        mon = _MONTH.get(m.group(1).lower())
        if mon:
            return f"{m.group(3)}-{mon}-{int(m.group(2)):02d}"
    # 3) "1864"
    m = re.search(r"(\d{4})", s)
    if m:
        return f"{m.group(1)}-01-01"
    return ""


def discover_category(pope_key: str) -> list[dict]:
    """Walk all paginated category pages and collect docs."""
    base = f"https://www.papalencyclicals.net/category/{pope_key}/"
    seen: dict[str, dict] = {}
    page = 1
    while True:
        url = base if page == 1 else f"{base}page/{page}/"
        try:
            html = fetch(url)
        except Exception:
            break
        soup = BeautifulSoup(html, "html.parser")
        # Each item is a <li> (or <article>) containing an <a rel="bookmark">.
        # Use the bookmark anchors directly to be robust across page templates.
        anchors = soup.find_all("a", attrs={"rel": "bookmark"})
        new = 0
        for a in anchors:
            href = a.get("href", "")
            if not href.startswith("http"):
                continue
            # Skip if pointing back to category
            if "/category/" in href:
                continue
            # Skip external links (PDFs hosted elsewhere) — only papalencyclicals.net HTML
            if "papalencyclicals.net" not in href:
                continue
            if not href.lower().endswith((".htm", ".html")):
                continue
            title = a.get_text(strip=True)
            slug = href.rstrip("/").rsplit("/", 1)[-1].replace(".htm", "")
            if slug in seen:
                continue
            # Parent text typically: <a>Title</a> <span>(subtitle) - date</span>
            parent = a.parent
            tail = ""
            if parent:
                full = parent.get_text(" ", strip=True)
                if title and full.startswith(title):
                    tail = full[len(title):].strip()
                # Drop everything from "Ereader Files" / newline onwards
                tail = re.split(r"\r|\n|Ereader Files", tail, maxsplit=1)[0].strip()
            subtitle = ""
            date_s = ""
            # Tail looks like "(Condemning Current Errors) - December 8, 1864"
            m = re.match(r"^\((.*?)\)\s*[-–—]\s*(.+)$", tail)
            if m:
                subtitle = m.group(1).strip()
                date_s = m.group(2).strip()
            else:
                m = re.match(r"^[-–—]\s*(.+)$", tail)
                if m:
                    date_s = m.group(1).strip()
                elif tail and re.match(r"^[A-Za-z]+\s+\d", tail):
                    date_s = tail
            # If subtitle contains an older parseable date (papalencyclicals.net puts the
            # real bull date inside parens for some medieval docs, with the CMS upload
            # date appearing in the tail span), prefer that. We accept a subtitle-derived
            # date only if it's earlier than the trailing date by ≥ 50 years — otherwise
            # the trailing date is the canonical one.
            primary_date = parse_date(date_s)
            sub_dates = re.findall(
                r"([A-Za-z]+\s+\d{1,2},?\s+\d{3,4})", subtitle
            )
            for sd in sub_dates:
                pd = parse_date(sd)
                if pd and primary_date and pd < primary_date and int(primary_date[:4]) - int(pd[:4]) >= 50:
                    primary_date = pd
                    date_s = sd
                    break

            seen[slug] = {
                "slug": slug,
                "title": title,
                "subtitle": subtitle,
                "date_raw": date_s,
                "date": primary_date,
                "url": href,
            }
            new += 1
        # Check for next-page link
        if new == 0:
            break
        nxt = soup.find("a", string=re.compile(r"Next|next|»|>")) or soup.find(
            "a", attrs={"class": re.compile(r"next")}
        )
        if not nxt:
            break
        page += 1
        if page > 50:
            break

    items = list(seen.values())
    items.sort(key=lambda x: x["date"] or "0000-00-00")
    return items


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pope-key", required=True, help="e.g. pius09 / leo13 / greg16 / ben14")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    items = discover_category(args.pope_key)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Discovered {len(items)} documents for {args.pope_key}")
    for it in items[:5]:
        print(f"  {it['date']}  {it['title']}  {it['url']}")
    if len(items) > 5:
        print(f"  ...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
