"""Post-translation polish for AI-translated ebooks.

Fixes two ship-breaking issues from `translate_ebook_to_zh.py` output:

1. **Overlong chapter_path** — when the LLM emits `#### heading\nbody...`
   without the newline (mashing heading + first paragraph), the existing
   regex `^(#{2,4})\s+(.+)` greedy-captures the whole line. ~57% of
   ANF Vol 1 chunks suffer this.

   Fix: detect mashed headings, split at first sensible boundary (Chinese
   sentence break, body-starter phrase, or hard cap), update both
   chapter_path AND the content (insert newline between heading and body).

2. **No parent-work grouping in TOC** — every chunk is a standalone TOC
   entry, so a 65-chapter letter (e.g. 革利免一書) shows up as 65 lines.

   Fix: detect parent-work boundaries from the source_text H3 `### ...`
   heading. When a chunk's source_text has an H3 heading that matches a
   known parent-work pattern, we record it as a volume divider. Subsequent
   chunks inherit that volume until the next H3 boundary. The reader's
   existing `volumes` TOC grouping picks this up automatically.

Usage:
    python scripts/polish_translated_book.py <ebook_id>
    python scripts/polish_translated_book.py <ebook_id> --dry-run
    python scripts/polish_translated_book.py <ebook_id> --skip-chapter-clean
    python scripts/polish_translated_book.py <ebook_id> --skip-volumes

Idempotent — running twice is a no-op.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# Import shared utils from translate_ebook_to_zh.py
sys.path.insert(0, str(ROOT / "scripts"))
import standardize_ebook as se  # for push_to_r2

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}
H_JSON = {**H_GET, "Content-Type": "application/json", "Prefer": "return=minimal"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")


# ── Chapter-path cleanup ──────────────────────────────────────────────────

# Common phrase markers where heading ends and body begins. Tuned for ANF
# translations (Sonnet/Haiku output). Order matters — we pick the EARLIEST
# match in the title.
BODY_STARTER_PHRASES = [
    # Safe — these phrases are almost always BODY connectors, not title text.
    # Anything that could plausibly start a chapter title (上帝/主/基督/我/我們應當/讓我們/聖經)
    # has been removed to prevent false-positive cuts.
    "親愛的弟兄們", "親愛之弟兄", "弟兄們，",
    "因此，", "因此 ", "因為，", "因為 ",
    "此外，", "此外 ", "再者，", "再者 ", "然而，", "然而 ",
    "正如先前", "正如我們所", "正如已",
    "我已得知", "我聽聞", "我已聽聞", "我已知曉",
    "夫然", "夫，", "蓋，",
    "在這方面", "在這件事", "在所有事上",
    "若有人", "倘若有人",
]
BODY_STARTER_RE = re.compile("|".join(re.escape(p) for p in BODY_STARTER_PHRASES))

# Chinese chapter prefix (number + 章/節/集 etc.)
CHAPTER_PREFIX_RE = re.compile(
    r"^(?P<prefix>第[一二三四五六七八九十百千零\d]+[章節集篇卷編冊部部分]"
    r"[\s——\-．\.：:。]*)"
    r"(?P<rest>.*)$"
)


SUBTITLE_HARD_CAP = 22  # Subtitle (after `第N章——`) max length
FRONTMATTER_CAP = 16    # Non-prefixed titles (前言/引言/封面) max length

# Standard front-matter heading words. When chapter_path STARTS with one
# of these and is followed by body text (no separator), truncate to just
# the heading word — these are universal section labels.
FRONTMATTER_HEAD_WORDS = [
    "前言", "引言", "序言", "序",
    "封面", "目錄", "目　錄", "目　　錄",
    "版權頁", "版權資訊", "出版資訊", "出版說明",
    "扉頁", "卷首語", "凡例", "編者按", "編序", "編輯前言",
    "導論", "導言", "緒論",
    "圖目錄", "表目錄", "插圖目錄",
]
FRONTMATTER_HEAD_RE = re.compile(
    r"^(" + "|".join(re.escape(w) for w in FRONTMATTER_HEAD_WORDS) + r")(.{1,}?)?$"
)


def clean_chapter_path(raw: str, max_len: int = 32) -> tuple[str, bool]:
    """Return (cleaned_title, was_truncated).

    Algorithm (subtitle = chars after `第N章——`):
      1. Front-matter heading-word truncation: if raw starts with a
         standard heading word (前言/引言/序/封面/目錄/…) followed by other
         characters, drop the trailing characters. Runs FIRST so it works
         even on titles already under max_len (which an earlier polish
         pass truncated to 「前言本卷所收錄的內容，等同於愛丁」).
      2. If raw already short enough: keep as-is.
      3. Strip chapter prefix (`第N章——`) → `rest`.
      4. In rest, find earliest of (in priority):
         a. Hard period 「。」 within first SUBTITLE_HARD_CAP chars.
         b. Comma/colon/semicolon 「，：；」 within first SUBTITLE_HARD_CAP chars,
            BUT only when it would leave subtitle ≥ 4 chars.
         c. Body-starter phrase AFTER position 3 of rest.
      5. Hard cap at SUBTITLE_HARD_CAP chars.
    """
    raw = raw.strip().replace("\n", " ")

    # (1) Front-matter heading-word truncation
    fm_match = FRONTMATTER_HEAD_RE.match(raw)
    if fm_match and fm_match.group(1) != raw:
        return fm_match.group(1), True

    if len(raw) <= max_len:
        return raw, False

    m = CHAPTER_PREFIX_RE.match(raw)
    if m:
        prefix = m.group("prefix")
        rest = m.group("rest").strip(" 　")

        cut_at = SUBTITLE_HARD_CAP

        # (a) Hard period — strongest boundary signal
        period_pos = rest.find("。")
        if 0 < period_pos <= SUBTITLE_HARD_CAP:
            cut_at = period_pos

        # (b) Comma/colon when subtitle would still be ≥ 4 chars
        else:
            for sep in ["，", "：", "；"]:
                p = rest.find(sep)
                # First occurrence: skip if too early (might be inside a real
                # multi-clause title); prefer second occurrence if first is < 6
                if 0 < p <= SUBTITLE_HARD_CAP and p >= 4:
                    # If there's a SECOND occurrence still in range and the
                    # first one is < 10, the title probably has internal comma
                    # → take the second.
                    p2 = rest.find(sep, p + 1)
                    if 0 < p2 <= SUBTITLE_HARD_CAP and p < 10:
                        cut_at = min(cut_at, p2)
                    else:
                        cut_at = min(cut_at, p)
                    break

            # (c) Starter phrase, but only after position 3 (allow short title)
            starter_match = BODY_STARTER_RE.search(rest[3:])
            if starter_match:
                starter_abs = starter_match.start() + 3
                if 3 < starter_abs <= SUBTITLE_HARD_CAP:
                    cut_at = min(cut_at, starter_abs)

        subtitle = rest[:cut_at].strip(" 　．")
        subtitle = re.sub(r"[\-—－]+$", "", subtitle).strip()
        return f"{prefix.rstrip()}{subtitle}".strip(), True

    # No chapter prefix — check for standard front-matter heading word
    # (前言/引言/序/封面/目錄/…) followed by body. If found, drop the body
    # and keep just the heading word. CCEL ebooks frequently emit `### PREFACE.`
    # + body as one block, and the LLM merges them with no separator
    # → my regex captures "前言本卷所收錄的內容…" as the chapter_path.
    fm_match = FRONTMATTER_HEAD_RE.match(raw)
    if fm_match:
        return fm_match.group(1), True

    # Otherwise — cut at first sentence break or hard cap
    period_pos = raw.find("。")
    if 0 < period_pos < FRONTMATTER_CAP * 1.5:
        return raw[:period_pos], True
    return raw[:FRONTMATTER_CAP], True


# ── Volume detection (parent-work grouping) ───────────────────────────────

# Match a source_text H3 heading. Each chunk's source_text starts with its
# markdown structure; the H3 (`### ...`) marks a parent-work boundary in
# ANF/NPNF EPUBs (Schaff CCEL convention).
H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.M)
# H4 chapter headings (within a parent work) — used to ignore noise.
H4_CHAPTER_RE = re.compile(r"^####\s+(Chapter|chapter)\s+[IVXLCDM\d]+", re.M)

# Map English H3 headings → Chinese parent-work names. Patterns are
# substring matches (case-sensitive). Keys are checked in order; first hit
# wins. None means "ignore this H3 — front matter / introduction noise".
ANF_VOLUMES: list[tuple[str, Optional[str]]] = [
    # === ANF Vol 1 ===
    ("First Epistle of Clement", "革利免致哥林多人前書"),
    ("Second Epistle of Clement", "革利免致哥林多人後書"),
    ("Epistle of Ignatius to the Ephesians", "依納爵致以弗所人書"),
    ("Epistle of Ignatius to the Magnesians", "依納爵致馬內夏人書"),
    ("Epistle of Ignatius to the Trallians", "依納爵致特拉勒人書"),
    ("Epistle of Ignatius to the Romans", "依納爵致羅馬人書"),
    ("Epistle of Ignatius to the Philadelphians", "依納爵致非拉鐵非人書"),
    ("Epistle of Ignatius to the Smyrnaeans", "依納爵致士每拿人書"),
    ("Epistle of Ignatius to Polycarp", "依納爵致坡旅甲書"),
    ("Epistle of Polycarp to the Philippians", "坡旅甲致腓立比人書"),
    ("Encyclical Epistle of the Church at Smyrna", "士每拿教會通諭"),  # Martyrdom of Polycarp
    ("Martyrdom of Polycarp", "坡旅甲殉道記"),
    ("Epistle of Mathetes to Diognetus", "致丟格那妥書"),
    ("Mathetes to Diognetus", "致丟格那妥書"),
    ("Epistle of Barnabas", "巴拿巴書信"),
    ("Pastor of Hermas", "黑馬牧者書"),
    ("Shepherd of Hermas", "黑馬牧者書"),
    ("Fragments of Papias", "帕皮亞殘篇"),
    ("First Apology of Justin", "殉道者猶斯定第一護教辭"),
    ("Second Apology of Justin", "殉道者猶斯定第二護教辭"),
    ("Dialogue of Justin", "與特里弗的對話"),
    ("Dialogue with Trypho", "與特里弗的對話"),
    ("Discourse to the Greeks", "猶斯定致希臘人辭"),
    ("Hortatory Address to the Greeks", "勸勉希臘人辭"),
    ("On the Sole Government of God", "論神獨一治理"),
    ("On the Resurrection", "論復活"),
    ("Other Fragments from the Lost Writings of Justin", "猶斯定遺著殘篇"),
    ("Martyrdom of the Holy Martyrs", "聖殉道者殉道記"),
    # Irenaeus — 5 books of Against Heresies
    ("Against Heresies", "愛任紐《駁異端》"),
    ("Adversus Haereses", "愛任紐《駁異端》"),
    ("Irenæus Against Heresies", "愛任紐《駁異端》"),
    ("Irenaeus Against Heresies", "愛任紐《駁異端》"),
    ("Fragments from the Lost Writings of Irenaeus", "愛任紐遺著殘篇"),
    # === ANF Vol 2 — second-century fathers ===
    ("Address of Tatian to the Greeks", "他提安致希臘人辭"),
    ("Plea for the Christians", "雅典那哥拉護教辭"),
    ("Resurrection of the Dead", "論死人復活"),
    ("Theophilus to Autolycus", "提阿非羅致奧托呂庫書"),
    ("Exhortation to the Heathen", "革利免勸勉希臘人"),
    ("Instructor", "革利免《教師》"),
    ("Stromata", "革利免《雜文集》"),
    ("Salvation of the Rich Man", "革利免《富者得救》"),
    # === NPNF1 — Augustine ===
    ("Confessions", "懺悔錄"),
    ("City of God", "上帝之城"),
    ("On Christian Doctrine", "論基督教教義"),
    ("On the Holy Trinity", "論三位一體"),
    ("Enchiridion", "信仰手冊"),
    # === NPNF2 — various ===
    ("Church History", "教會史"),
    ("Ecclesiastical History", "教會史"),
    ("Life of Constantine", "君士坦丁傳"),
]


INTRO_NOTE_RE = re.compile(r"^Introductory\s+Notes?\s+to\s+(?:the\s+)?(.+)$", re.I)


def detect_volume(source_text: str) -> Optional[str]:
    """If this chunk's source_text starts with an H3 that names a known
    parent work, return the Chinese volume name. Otherwise None.

    Patterns checked (in order):
      1. "Introductory Note to X" → resolve to X's volume (CCEL prefaces
         each parent work with a separate translator note chunk that's
         logically part of the same parent work — chunk 4 in ANF Vol 1
         was misclassified as front matter before this).
      2. Direct ANF_VOLUMES substring match.

    We only look at the FIRST H3 in the chunk; deeper H3s (rare) are noise.
    """
    if not source_text:
        return None
    m = H3_RE.search(source_text)
    if not m:
        return None
    heading = m.group(1).strip()
    # Strip leading "The " for matching
    h_norm = heading
    if h_norm.lower().startswith("the "):
        h_norm = h_norm[4:]

    # (1) Introductory Note → look for parent work name inside it
    intro_m = INTRO_NOTE_RE.match(h_norm)
    if intro_m:
        target = intro_m.group(1).strip()
        for pattern, vol in ANF_VOLUMES:
            if pattern.lower() in target.lower():
                return vol

    # (2) Direct match against ANF_VOLUMES
    for pattern, vol in ANF_VOLUMES:
        if pattern.lower() in heading.lower() or pattern.lower() in h_norm.lower():
            return vol
    return None


# ── Pipeline ──────────────────────────────────────────────────────────────

def polish(ebook_id: str, dry_run: bool = False,
           skip_chapter_clean: bool = False,
           skip_volumes: bool = False) -> None:
    jsonl_path = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not jsonl_path.exists():
        sys.exit(f"JSONL not found: {jsonl_path}")

    chunks: list[dict] = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    print(f"Loaded {len(chunks)} chunks from {jsonl_path.name}", flush=True)

    n_cleaned = 0
    n_volume_set = 0
    n_volume_headers = 0
    current_volume: Optional[str] = None
    sample_cleans: list[tuple[int, str, str]] = []

    # If chunks have already been consolidated (chunk_type='page' set by
    # consolidate_by_ncx.py with letter-level Chinese names), DON'T re-run
    # volume detection — polish's generic patterns (e.g. "Against Heresies"
    # → "愛任紐《駁異端》") would overwrite the more precise consolidator
    # labels ("愛任紐《駁異端》卷一/卷二/卷三/卷四/卷五") and lump all 5
    # books into one volume, scrambling the TOC.
    skip_existing_volumes = any(
        c.get("chunk_type") == "page" and c.get("volume") for c in chunks
    )
    if skip_existing_volumes:
        print("  (volume tags from consolidator already present — skipping volume detection)")

    for c in chunks:
        # ─ Volume injection (must run before chapter cleanup so we can use
        #   source_text H3 to detect parent-work boundary) ─
        if not skip_volumes and not skip_existing_volumes:
            new_vol = detect_volume(c.get("source_text", ""))
            volume_changed = new_vol and new_vol != current_volume
            if new_vol:
                current_volume = new_vol
            # Set volume ONLY if not already set — polish should never
            # overwrite a tag the consolidator already chose.
            if current_volume and not c.get("volume"):
                c["volume"] = current_volume
                n_volume_set += 1
            if volume_changed:
                c["is_volume_header"] = True
                n_volume_headers += 1
            elif "is_volume_header" in c and not c.get("volume"):
                del c["is_volume_header"]

        # ─ Chapter-path cleanup ─
        if not skip_chapter_clean:
            raw = c.get("chapter_path", "")
            cleaned, was_trunc = clean_chapter_path(raw)
            if was_trunc:
                if len(sample_cleans) < 8:
                    sample_cleans.append((c["chunk_index"], raw[:80], cleaned))
                c["chapter_path"] = cleaned
                # Also fix the content's first heading line so the in-page
                # H3/H4 anchor + breadcrumb match the new title.
                content = c.get("content", "")
                lines = content.split("\n", 1)
                if lines and re.match(r"^#{2,4}\s+", lines[0]):
                    pre_m = re.match(r"^(#{2,4})\s+", lines[0])
                    if pre_m:
                        hashes = pre_m.group(1)
                        body_after = lines[1] if len(lines) > 1 else ""
                        old_line = lines[0][len(hashes) + 1:]
                        body_mashed = old_line[len(cleaned):].strip()
                        new_first = f"{hashes} {cleaned}"
                        new_body = body_after
                        # Reinject body_mashed ONLY when:
                        #   - body_after is empty (LLM put everything on
                        #     one heading line; this IS the body to restore)
                        #   - OR body_mashed is long enough to plausibly be
                        #     a real lost body, AND not already at the
                        #     start of body_after.
                        # Skip otherwise — short body_mashed with non-empty
                        # body_after is almost always a STALE fragment from
                        # a prior polish run, and reinjecting it splits
                        # CJK words at the truncation boundary (e.g.
                        # "愛丁" + "堡系列" should be "愛丁堡系列").
                        if body_mashed and not body_after:
                            new_body = body_mashed
                        elif body_mashed and len(body_mashed) >= 30 and not body_after.startswith(body_mashed[:10]):
                            new_body = f"{body_mashed}\n\n{body_after}"
                        c["content"] = f"{new_first}\n\n{new_body}".rstrip() + "\n"
                n_cleaned += 1

    print(f"\n  chapter_path cleaned: {n_cleaned}")
    print(f"  volume tags applied:  {n_volume_set}")
    if sample_cleans:
        print(f"\n  Sample cleanups:")
        for idx, before, after in sample_cleans:
            print(f"    [{idx}] {before[:70]}")
            print(f"      → {after}")

    if dry_run:
        print("\n(dry-run, not writing)")
        return

    # Rewrite JSONL
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    size_kb = jsonl_path.stat().st_size // 1024
    print(f"\n  ✓ rewrote {jsonl_path.name}  ({size_kb} KB)")

    # Push R2
    try:
        se.push_to_r2(ebook_id, jsonl_path)
        print(f"  ✓ pushed R2")
    except Exception as e:
        print(f"  ⚠ R2 push failed: {e}", file=sys.stderr)

    # Refresh ebook_chunks previews (DELETE + INSERT)
    try:
        r = requests.delete(f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{ebook_id}",
                            headers=H_GET, timeout=30)
        if r.status_code not in (200, 204):
            print(f"  ⚠ preview DELETE: {r.status_code} {r.text[:200]}", file=sys.stderr)
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
            r = requests.post(f"{URL}/rest/v1/ebook_chunks", headers=H_JSON,
                              json=batch, timeout=30)
            if r.status_code not in (200, 201):
                # Retry once with smaller batch
                for row in batch:
                    rr = requests.post(f"{URL}/rest/v1/ebook_chunks",
                                       headers=H_JSON, json=row, timeout=30)
                    if rr.status_code not in (200, 201):
                        print(f"  ⚠ preview row [{row['chunk_index']}]: "
                              f"{rr.status_code} {rr.text[:120]}", file=sys.stderr)
        print(f"  ✓ refreshed ebook_chunks previews ({len(rows)} rows)")
    except Exception as e:
        print(f"  ⚠ preview refresh failed: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-chapter-clean", action="store_true")
    ap.add_argument("--skip-volumes", action="store_true")
    args = ap.parse_args()
    polish(args.ebook_id, dry_run=args.dry_run,
           skip_chapter_clean=args.skip_chapter_clean,
           skip_volumes=args.skip_volumes)


if __name__ == "__main__":
    main()
