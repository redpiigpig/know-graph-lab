"""
Re-anchor section headings across the three languages of a papal document so
they share a common alignment skeleton.

Strategy:
  - English `## ` headings are treated as the spine (positions defined by the
    paragraph number that immediately follows each heading).
  - For Latin & Chinese, scan the file to find headings + their next paragraph
    number. Keep only those whose next-para-num matches an English heading
    position. Drop the rest (likely false positives from the flat-heading
    detector / vatican.va Chinese PDF noise).
  - If a Chinese heading is missing for an English position, leave a
    placeholder `## ⏳` so alignDocs() still pairs the row. Same for Latin.

Usage:
  python scripts/align_papal_headings.py CENTURY POPE_SLUG DOC_SLUG
  e.g. python scripts/align_papal_headings.py 21 francis fratelli-tutti-2020
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PARA_RE = re.compile(r"^(\d{1,3})\.\s")
HEADING_RE = re.compile(r"^## (.+)$")
FOOTNOTE_SECTION_RE = re.compile(r"^## Footnotes?$", re.IGNORECASE)


def scan_headings(text: str) -> list[tuple[str, str]]:
    """Return [(heading_text, next_para_num)] in document order, plus a final
    `__END__` marker for the trailing `## Footnotes` boundary.

    Stops scanning once a `## Footnotes` heading is encountered.
    """
    blocks = re.split(r"\n{2,}", text)
    pending: list[str] = []
    out: list[tuple[str, str]] = []
    for raw in blocks:
        b = raw.strip()
        if not b:
            continue
        if FOOTNOTE_SECTION_RE.match(b):
            break
        hm = HEADING_RE.match(b)
        if hm:
            pending.append(hm.group(1).strip())
            continue
        pm = PARA_RE.match(b)
        if pm:
            n = pm.group(1)
            for h in pending:
                out.append((h, n))
            pending = []
    return out


def rewrite(target_path: Path, en_anchors_pairs: list[tuple[str, str]],
            target_anchors: list[tuple[str, str]],
            placeholder: str) -> int:
    """Drop `## ` headings in target file, then re-insert at EN anchor positions
    using target's matching headings (by next-para-num).

    Supports stacked headings (CHAPTER ONE + sub-title both anchored on same
    paragraph). EN dictates how many headings precede each paragraph; we pull
    that many target-language headings (in document order) for that anchor.
    """
    text = target_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n{2,}", text)

    # Group EN anchors by para-num, preserving order of appearance
    en_by_para: dict[str, list[str]] = {}
    en_para_order: list[str] = []
    for h, n in en_anchors_pairs:
        if n not in en_by_para:
            en_by_para[n] = []
            en_para_order.append(n)
        en_by_para[n].append(h)

    # Group target anchors by para-num similarly
    tgt_by_para: dict[str, list[str]] = {}
    for h, n in target_anchors:
        tgt_by_para.setdefault(n, []).append(h)

    # Drop all `## ` headings except `## Footnotes`
    cleaned: list[str] = []
    for raw in blocks:
        b = raw.strip()
        if not b:
            continue
        if HEADING_RE.match(b) and not FOOTNOTE_SECTION_RE.match(b):
            continue
        cleaned.append(b)

    # Re-insert at EN anchor positions
    out: list[str] = []
    inserted = 0
    for block in cleaned:
        pm = PARA_RE.match(block)
        if pm:
            n = pm.group(1)
            if n in en_by_para:
                en_headings = en_by_para[n]
                tgt_headings = tgt_by_para.get(n, [])
                for i, _ in enumerate(en_headings):
                    if i < len(tgt_headings):
                        out.append(f"## {tgt_headings[i]}")
                    else:
                        out.append(f"## {placeholder}")
                    inserted += 1
        out.append(block)

    target_path.write_text("\n\n".join(out).rstrip() + "\n", encoding="utf-8")
    return inserted


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: align_papal_headings.py CENTURY POPE_SLUG DOC_SLUG", file=sys.stderr)
        return 1
    century = int(sys.argv[1])
    pope_slug = sys.argv[2]
    doc_slug = sys.argv[3]

    folder = ROOT / "data" / "encyclicals" / f"{century:02d}c-{pope_slug}"
    en_path = folder / f"{doc_slug}-english.txt"
    la_path = folder / f"{doc_slug}-latin.txt"
    zh_path = folder / f"{doc_slug}-chinese.txt"

    if not en_path.exists():
        print(f"Missing EN file: {en_path}", file=sys.stderr)
        return 1

    en_anchors_pairs = scan_headings(en_path.read_text(encoding="utf-8"))
    en_anchors = [n for _, n in en_anchors_pairs]
    print(f"EN: {len(en_anchors_pairs)} heading anchors")
    if not en_anchors_pairs:
        print("EN has no headings — nothing to anchor against. Aborting.", file=sys.stderr)
        return 1

    if la_path.exists():
        la_anchors = scan_headings(la_path.read_text(encoding="utf-8"))
        n_la = rewrite(la_path, en_anchors_pairs, la_anchors, placeholder="⏳ 拉丁標題待補")
        print(f"LA: scanned {len(la_anchors)} headings; re-inserted {n_la} at EN anchors")
    if zh_path.exists():
        zh_anchors = scan_headings(zh_path.read_text(encoding="utf-8"))
        n_zh = rewrite(zh_path, en_anchors_pairs, zh_anchors, placeholder="⏳ 中譯標題待補")
        print(f"ZH: scanned {len(zh_anchors)} headings; re-inserted {n_zh} at EN anchors")

    return 0


if __name__ == "__main__":
    sys.exit(main())
