"""Rule-based sweep over a translated book JSONL to fix the LLM-quality
bugs the structural pipeline can't catch.

Pairs with `scan_translated_book.py`:
  - scan reports T1 (heading bleed) and T2 (h3 vs volume drift).
  - sweep applies in-place fixes for those two classes.

T1 fix — heading bleed: split heading at the body-marker position, prepend
the trailing portion onto the next paragraph. Example:

  Before:
    #### 第一章—書信寫作的契機既然我看到你
    ，最為卓越的狄奧格尼圖，極其渴慕要學習...

  After:
    #### 第一章—書信寫作的契機

    既然我看到你，最為卓越的狄奧格尼圖，極其渴慕要學習...

T2 fix — first-h3 letter-title drift: when the chunk has a `volume` set
and its first h3 (### ...) doesn't match the volume, replace the h3 text
with the volume name (since the volume is what the sidebar / breadcrumb
shows; the LLM's literal H3 wording shouldn't override that). The fix is
SKIPPED when the chunk has multiple h3s — those are EPUB-packaging cross-
work bleed cases (next letter's intro got pulled into prev chunk) and
need a careful split that this sweep doesn't attempt.

Usage:
    python scripts/sweep_book_quality.py <ebook_id> --dry-run
    python scripts/sweep_book_quality.py <ebook_id>
    python scripts/sweep_book_quality.py <ebook_id> --no-push
    python scripts/sweep_book_quality.py <ebook_id> --only-t1   # T1 only
    python scripts/sweep_book_quality.py <ebook_id> --only-t2   # T2 only
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se  # noqa: E402

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# Reuse scan's body-marker set — keep in sync.
BODY_MARKERS = [
    "既然", "誠然", "親愛的", "讓我們", "誠如",
    "若你", "若我", "蓋此", "蓋我", "蓋經上", "蓋誠",
    "雖然", "但關於", "但是我", "然而我",
    "因此我", "正如我", "我先前", "我所說", "只要前一",
    "亞伯拉罕被", "本書信", "在已過去", "從一開始",
]
TITLE_CLOSE_PUNCT = re.compile(r"[。！？」）]\s*$")
EM_DASH_SPLIT_RE = re.compile(r"^(第[一二三四五六七八九十百千零0-9]+章\s*[—\-－]+\s*)(.+)$")


def find_bleed_split(heading_text: str) -> tuple[str, str] | None:
    """If heading is a bleed, return (title_proper, body_bleed); else None.

    `heading_text` is the text AFTER the leading `#### ` markers. We:
      1. Skip if heading already closes with 「。！？」」 — that's a clean
         descriptive title with body-marker-like words used legitimately.
      2. Split at「第X章—」boundary if present; inspect the tail.
      3. Find the EARLIEST body marker in the tail at position > 1; split
         the heading there.
    """
    if TITLE_CLOSE_PUNCT.search(heading_text):
        return None
    m = EM_DASH_SPLIT_RE.match(heading_text)
    if not m:
        return None
    prefix, tail = m.group(1), m.group(2)
    best_pos = None
    best_marker = None
    for marker in BODY_MARKERS:
        pos = tail.find(marker)
        if pos >= 2 and (best_pos is None or pos < best_pos):
            best_pos = pos
            best_marker = marker
    if best_pos is None:
        return None
    title_proper = prefix + tail[:best_pos].rstrip()
    body_bleed = tail[best_pos:].strip()
    return title_proper, body_bleed


def sweep_t1(content: str) -> tuple[str, int]:
    """Apply T1 (heading bleed) fix to a chunk's markdown content.
    Returns (new_content, num_fixes)."""
    lines = content.split("\n")
    out: list[str] = []
    fixes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        h_match = re.match(r"^(#{3,4})\s+(.+?)\s*$", line)
        if not h_match:
            out.append(line)
            i += 1
            continue
        marks, heading_text = h_match.group(1), h_match.group(2)
        split = find_bleed_split(heading_text)
        if not split:
            out.append(line)
            i += 1
            continue
        title_proper, body_bleed = split
        out.append(f"{marks} {title_proper}")
        # Locate the next non-empty non-heading line — that's the body
        # paragraph the bleed escaped from. Prepend the bleed onto it.
        j = i + 1
        # Skip blank lines after the heading
        while j < len(lines) and not lines[j].strip():
            out.append(lines[j])
            j += 1
        if j < len(lines):
            next_line = lines[j]
            # If the next line starts with a heading marker, the bleed has
            # nowhere natural to go — emit it as its own paragraph rather
            # than mash it into another heading.
            if re.match(r"^#{1,4}\s", next_line):
                out.append("")
                out.append(body_bleed)
            else:
                # The body line often starts with 「，」(orphan comma left
                # over from the bleed cut). Stitch cleanly.
                stitched = (body_bleed + next_line).replace("  ", " ")
                out.append(stitched)
            i = j + 1
        else:
            out.append("")
            out.append(body_bleed)
            i = j
        fixes += 1
    return "\n".join(out), fixes


def sweep_t2(content: str, volume: str) -> tuple[str, int]:
    """If chunk has ONE h3 and it differs from volume, replace it with
    the volume name. SKIPS chunks with multiple h3s (cross-work bleed
    artifacts that need a different fix)."""
    if not volume:
        return content, 0
    # Count h3 lines (### + space + text), excluding chapter-numbered ones
    # (a 「### 第X章—」 would be a chapter heading at h3 depth, which is rare
    # but possible — we don't touch those).
    h3_lines = re.findall(r"^(### )(.+?)\s*$", content, re.M)
    letter_titles = [t for marker, t in
                     [(m, txt) for m, txt in h3_lines]
                     if not re.match(r"第[一二三四五六七八九十百千零0-9]+章", t)]
    if len(letter_titles) != 1:
        # Either zero h3 (nothing to fix) or multiple h3 (cross-bleed)
        return content, 0
    current = letter_titles[0].strip()
    # Strip [^N] refs for comparison
    current_clean = re.sub(r"\[\^\d+\]", "", current).strip()
    if current_clean == volume:
        return content, 0
    # Replace the first matching h3
    def _replace(m: re.Match) -> str:
        body = m.group(2).strip()
        body_clean = re.sub(r"\[\^\d+\]", "", body).strip()
        if body_clean == current_clean:
            return f"### {volume}"
        return m.group(0)
    new_content, n = re.subn(r"^(### )(.+?)\s*$", _replace, content,
                             count=1, flags=re.M)
    return new_content, n


def fetch_book(ebook_id: str) -> dict:
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        sys.exit(f"no ebooks row for {ebook_id}")
    return rows[0]


def sweep(ebook_id: str, dry_run: bool = False, push: bool = True,
          only_t1: bool = False, only_t2: bool = False) -> None:
    book = fetch_book(ebook_id)
    print(f"Book: {book['title']}")

    jsonl_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    chunks = [json.loads(l) for l in jsonl_path.read_text(encoding="utf-8").splitlines() if l]
    print(f"Loaded {len(chunks)} chunks")

    t1_total = t2_total = 0
    t1_chunks = t2_chunks = 0

    for c in chunks:
        content = c.get("content") or ""
        new_content = content
        if not only_t2:
            new_content, n1 = sweep_t1(new_content)
            if n1:
                t1_total += n1
                t1_chunks += 1
        if not only_t1:
            new_content, n2 = sweep_t2(new_content, c.get("volume") or "")
            if n2:
                t2_total += n2
                t2_chunks += 1
        if new_content != content:
            c["content"] = new_content

    print(f"\nT1 (heading bleed) fixes: {t1_total} in {t1_chunks} chunks")
    print(f"T2 (h3 letter-title) fixes: {t2_total} in {t2_chunks} chunks")

    if dry_run:
        print("\n(dry-run; not writing)")
        return

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n✓ wrote {jsonl_path.name} ({jsonl_path.stat().st_size // 1024} KB)")

    if push:
        try:
            se.push_to_r2(ebook_id, jsonl_path)
            print("✓ pushed R2")
        except Exception as e:
            print(f"⚠ R2 push: {e}", file=sys.stderr)

        # Refresh DB previews — content[:200] now reflects the fixed text.
        try:
            r = requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                                headers=H_GET, timeout=30)
            if r.status_code not in (200, 204):
                print(f"⚠ preview DELETE: {r.status_code}", file=sys.stderr)
            rows = [{
                "ebook_id": ebook_id,
                "chunk_index": c["chunk_index"],
                "chunk_type": c.get("chunk_type", "chapter"),
                "page_number": c.get("page_number"),
                "chapter_path": c.get("chapter_path"),
                "content": (c.get("content") or "")[:200],
                "char_count": len(c.get("content") or ""),
            } for c in chunks]
            BATCH = 25
            for i in range(0, len(rows), BATCH):
                batch = rows[i:i + BATCH]
                rr = requests.post(f"{URL}/rest/v1/ebook_chunks",
                                   headers=H_JSON, json=batch, timeout=30)
                if rr.status_code not in (200, 201):
                    for row in batch:
                        requests.post(f"{URL}/rest/v1/ebook_chunks",
                                      headers=H_JSON, json=row, timeout=30)
            print(f"✓ refreshed previews ({len(rows)} rows)")
        except Exception as e:
            print(f"⚠ preview refresh: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--only-t1", action="store_true")
    ap.add_argument("--only-t2", action="store_true")
    args = ap.parse_args()
    sweep(args.ebook_id, dry_run=args.dry_run, push=not args.no_push,
          only_t1=args.only_t1, only_t2=args.only_t2)


if __name__ == "__main__":
    main()
