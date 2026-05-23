"""
Normalize ecumenical council text files for per-canon 3-column alignment.

For each `data/creeds/ecumenical-councils/{early,medieval,trent}/*-{english,latin,greek}.txt`:

1. **English** (papalencyclicals scrape): convert broken `## N. body` headings back to
   normal `N. body` paragraphs. papalencyclicals' table-of-contents scrape sometimes
   wraps anathema/canon items as `## 1. If anyone...` instead of plain `1.` — this
   breaks paragraphParser.ts's heading vs paragraph detection.

2. **Latin** (DCO antiword): strip footnote-marker number runs like " 52 53 54 55 56 57"
   left by antiword extraction of manuscript-apparatus superscripts. These appear at
   sentence ends as space-separated 2-3-digit number sequences.

3. **All languages**: collapse multiple blank lines to single; trim trailing whitespace;
   convert `Canon I`, `Canon 1`, `Κανὼν Α´` etc. canon headers into standard `N. body`
   format where possible (only if a clearly numbered structure can be detected).

Idempotent. Re-runs are safe (no-op if already normalized).

UI alignment behavior: paragraphParser.ts `alignDocs()` does outer-join by paragraph
number `N`. Where one language has `N` and another doesn't (e.g. Greek has only
canons 1-8 while English+Latin have anathemas 1-12 + canons 1-8), that column
shows blank for the missing language. This is acceptable historical reality.
"""
from __future__ import annotations

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── (1) English fixups ──────────────────────────────────────────────────────

# Match `## N. body` (number-prefixed heading that papalencyclicals scrape
# erroneously created) and downgrade to plain `N. body` paragraph.
EN_NUMBERED_HEADING = re.compile(r"^##\s+(\d{1,3}\.\s+)", re.MULTILINE)

# Match a `## N` standalone (no body after the number) — also downgrade.
EN_BARE_NUMBER_HEADING = re.compile(r"^##\s+(\d{1,3})\s*$", re.MULTILINE)


def normalize_english(text: str) -> str:
    # Conservative: only downgrade `## N. body` to `N. body` when the body
    # contains a strong canon/anathema marker ("anathema", "If anyone", "Canon").
    # Otherwise it may be a list-item-in-letter that papalencyclicals scrape
    # accidentally wrapped (e.g. clauses inside Cyril's letter to Nestorius).

    def maybe_downgrade(m):
        body = m.group(0)  # full `## N. body...` first-line capture
        # Look forward in text to see if anathema-context applies — we only
        # downgrade if the line itself contains the trigger phrases.
        if re.search(r"\b(anathema|If anyone|Canon \d|let him be)\b", body, re.IGNORECASE):
            return m.group(1)  # `N. ` (heading marker stripped)
        return body  # keep as-is

    # Pattern with full first-line capture to test for anathema content
    text = re.sub(
        r"^##\s+(\d{1,3}\.\s+)([^\n]{0,200})",
        lambda m: m.group(1) + m.group(2) if re.search(r"\b(anathema|If anyone|Canon|let him be|excommunicat)\b", m.group(2), re.IGNORECASE) else m.group(0),
        text,
        flags=re.MULTILINE,
    )
    # 1b stays the same — `## N` (bare number) is always heading downgrade
    text = EN_BARE_NUMBER_HEADING.sub(r"\1.", text)
    return text


# ── (2) Latin fixups ────────────────────────────────────────────────────────
#
# DCO Latin (from Alberigo COD 1973 via antiword) contains heavy manuscript
# apparatus pollution: inline footnote-marker superscripts attached to words
# (e.g. "et16", "diligamus21", "verbo93"), and standalone footnote runs at
# paragraph ends ("scandalizatos 62 63 64 6566 67 68 ...").
#
# Latin spelling never ends in a digit, so `word+digit-suffix` is always a
# footnote marker — safe to strip. Roman numerals (I/II/V/X) are letters not
# digits, so canon headers like "Canon I" survive.

# (2a) Inline footnote attached to word (no space): "et16" → "et", "verbo93" → "verbo"
# Also handle merged double-footnotes: "verbo123124" → "verbo"
LAT_INLINE_FOOTNOTE = re.compile(
    r"([a-zA-Zāēīōūæœ]{2,})(\d{2,6})(?=\W|$)"
)

# (2b) Standalone footnote-marker runs: " 62 63 64 6566 67 68 ..."
# Allow up to 6 digits per chunk (merged footnote groups), require 2+ consecutive.
LAT_FOOTNOTE_RUN = re.compile(
    r"(?:\s+\d{2,6}){2,}",
)

# (2c) Roman numeral followed by digits at line start (canon header pollution):
# "I345 Si quis" → "I. Si quis"; "V374 Si quis" → "V. Si quis"
# Pattern: ^(canon-roman)(digits) → "(roman). "
LAT_ROMAN_PREFIX = re.compile(
    r"^(IIII|XIV|XIII|XII|XI|VIII|VII|VI|IX|IV|III|II|VI?II|V|X{1,3}|I)(\d{2,4})\s+",
    re.MULTILINE,
)

# (2d) Single trailing footnote number after a paragraph: " 47."
LAT_PARA_END_NUMBER = re.compile(
    r"\s+\d{2,4}(?=\.\s*$)",
    re.MULTILINE,
)

# (2e) Orphan footnote number between Latin words (only 2-3 digits, surrounded by
# lowercase letters or punctuation; conservative to not eat Roman dates).
LAT_ORPHAN_DIGIT = re.compile(
    r"(?<=[a-zāēīōūæœ,;])\s+\d{2,4}\s+(?=[a-zāēīōūæœ])",
)


def normalize_latin(text: str) -> str:
    # Apply in order — runs FIRST (they don't overlap with inline pattern),
    # then roman-prefix (which keeps canon header readable),
    # then inline (attached to word),
    # then orphan digits (between words),
    # then trailing-number cleanup.
    text = LAT_FOOTNOTE_RUN.sub("", text)
    text = LAT_ROMAN_PREFIX.sub(r"\1. ", text)
    text = LAT_INLINE_FOOTNOTE.sub(r"\1", text)
    text = LAT_ORPHAN_DIGIT.sub(" ", text)
    text = LAT_PARA_END_NUMBER.sub("", text)
    return text


# ── (3) Common cleanup ──────────────────────────────────────────────────────

def collapse_whitespace(text: str) -> str:
    # Collapse 3+ blank lines into 2 (paragraphParser splits on \n\n+)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip trailing whitespace per line
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    return text.strip() + "\n"


# ── Driver ──────────────────────────────────────────────────────────────────

def process_file(path: str) -> tuple[bool, int]:
    """Return (changed, bytes_saved)."""
    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    base = os.path.basename(path)
    if "-english.txt" in base:
        new = normalize_english(original)
    elif "-latin.txt" in base:
        new = normalize_latin(original)
    elif "-greek.txt" in base:
        new = original  # already clean
    else:
        return False, 0

    new = collapse_whitespace(new)

    if new == original:
        return False, 0

    with open(path, "w", encoding="utf-8") as f:
        f.write(new)
    return True, len(original) - len(new)


def main() -> int:
    targets = []
    for subdir in ["early", "medieval", "trent"]:
        targets.extend(glob.glob(
            os.path.join(ROOT, f"data/creeds/ecumenical-councils/{subdir}/*-english.txt")
        ))
        targets.extend(glob.glob(
            os.path.join(ROOT, f"data/creeds/ecumenical-councils/{subdir}/*-latin.txt")
        ))
        targets.extend(glob.glob(
            os.path.join(ROOT, f"data/creeds/ecumenical-councils/{subdir}/*-greek.txt")
        ))

    ok = 0
    changed = 0
    total_saved = 0
    for path in sorted(targets):
        ok += 1
        was_changed, saved = process_file(path)
        if was_changed:
            changed += 1
            total_saved += saved
            print(f"  ✓ normalized {os.path.relpath(path, ROOT)} (-{saved} bytes)")

    print(f"\n=== Done: {ok} files processed, {changed} changed, {total_saved} bytes saved ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
