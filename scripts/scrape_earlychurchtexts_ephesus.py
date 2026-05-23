"""
Scrape Greek text of Council of Ephesus 431 canons from earlychurchtexts.com.

The site has 8 canons across 2 pages:
  canons_of_ephesus_01.shtml — canons 1-6
  canons_of_ephesus_02.shtml — canons 7-8

Layout per canon: a section with Greek + Latin + English in parallel.
We extract just the Greek (polytonic) and write to:
  data/creeds/ecumenical-councils/early/early-03-greek.txt
"""
from __future__ import annotations

import os
import re
import sys
import urllib.request

from bs4 import BeautifulSoup, Tag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(
    ROOT, "data", "creeds", "ecumenical-councils", "early", "early-03-greek.txt"
)

URLS = [
    "https://earlychurchtexts.com/main/ephesus/canons_of_ephesus_01.shtml",
    "https://earlychurchtexts.com/main/ephesus/canons_of_ephesus_02.shtml",
]


def fetch_html(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 know-graph-lab/1.0 (ephesus-greek)"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8")


# Polytonic Greek + diacritics range
GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]")


def is_greek_paragraph(text: str) -> bool:
    """Pure Greek paragraph: >85% Greek (excludes mixed Greek+Latin cells)."""
    if not text:
        return False
    greek_chars = sum(1 for c in text if GREEK_RE.match(c))
    latin_chars = sum(1 for c in text if c.isalpha() and not GREEK_RE.match(c))
    total = greek_chars + latin_chars
    return total > 50 and greek_chars > 0.85 * total


def extract_greek_canons(html: str) -> list[tuple[int, str]]:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("body") or soup
    for tag in body.find_all(["script", "style"]):
        tag.decompose()

    results: list[tuple[int, str]] = []
    current_canon: int | None = None
    current_greek_chunks: list[str] = []

    # Walk paragraph-like leaf elements (avoid <div>/<td> which contain nested
    # <p> and would produce duplicate content).
    for el in body.find_all(["p", "h3", "h4"]):
        text = el.get_text(" ", strip=True)
        if not text:
            continue
        text = re.sub(r"\s+", " ", text).strip()

        # Detect canon number markers in any language form
        # "Canon 1" or "Κανών 1" or simply "1." at start of dedicated header element
        canon_m = re.match(r"^(?:Canon|Κανών|Κανὼν)\s+([IVX\d]+|[ΑΒΓΔΕΖΗΘΙ]['ʹ])", text, re.IGNORECASE)
        if canon_m and len(text) < 50:
            # finish previous
            if current_canon is not None and current_greek_chunks:
                results.append((current_canon, "\n\n".join(current_greek_chunks)))
            # parse number
            raw_num = canon_m.group(1)
            # Greek letter numerals
            greek_num_map = {"Α": 1, "Β": 2, "Γ": 3, "Δ": 4, "Ε": 5, "Ζ": 6, "Η": 7, "Θ": 8, "Ι": 9}
            if raw_num and raw_num[0] in greek_num_map:
                current_canon = greek_num_map[raw_num[0]]
            elif raw_num.isdigit():
                current_canon = int(raw_num)
            else:
                # Roman
                roman_map = {"I": 1, "V": 5, "X": 10}
                try:
                    total = 0
                    prev = 0
                    for c in reversed(raw_num):
                        v = roman_map.get(c, 0)
                        if v < prev:
                            total -= v
                        else:
                            total += v
                            prev = v
                    current_canon = total
                except (KeyError, ValueError):
                    current_canon = None
            current_greek_chunks = []
            continue

        # Greek body paragraph — pure Greek only, no Latin/English mixed
        if is_greek_paragraph(text) and current_canon is not None:
            current_greek_chunks.append(text)

    # Each canon page has the Greek text duplicated in adjacent table cells (header
    # row + body row). Just keep the LONGEST single chunk per canon — that's the
    # canonical full text.
    def _pick_canonical(chunks: list[str]) -> str:
        if not chunks:
            return ""
        return max(chunks, key=len).strip()

    if current_canon is not None and current_greek_chunks:
        results.append((current_canon, _pick_canonical(current_greek_chunks)))

    # Aggregate across pages: pick longest body per canon number
    by_canon: dict[int, str] = {}
    for n, body in results:
        if n not in by_canon or len(body) > len(by_canon[n]):
            by_canon[n] = body
    return [(n, by_canon[n]) for n in sorted(by_canon.keys())]


def main() -> int:
    all_canons: dict[int, str] = {}
    for url in URLS:
        print(f"Fetching {url}")
        html = fetch_html(url)
        canons = extract_greek_canons(html)
        for n, body in canons:
            all_canons[n] = body
        print(f"  ✓ found {len(canons)} canons: {sorted(n for n, _ in canons)}")

    if not all_canons:
        print("  ! no canons extracted; check page structure")
        return 1

    sorted_nums = sorted(all_canons.keys())
    body_lines = [
        "# Council of Ephesus 431 — Greek Canons",
        "# Source: earlychurchtexts.com (canons 1-8) — based on Schaff NPNF2 Vol 14",
        "",
        f"Ἐν Ἐφέσῳ Ἁγία καὶ Οἰκουμενικὴ Γ´ Σύνοδος (431)",
        "",
    ]
    for n in sorted_nums:
        body_lines.append(f"{n}. {all_canons[n]}")
        body_lines.append("")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(body_lines))

    print(f"\n✓ wrote {OUT_PATH}: {len(sorted_nums)} canons")
    return 0


if __name__ == "__main__":
    sys.exit(main())
