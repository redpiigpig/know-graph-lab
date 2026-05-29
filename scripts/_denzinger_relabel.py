"""
Rewrite every Denzinger chunk's chapter_path / volume / parent_volume so
the reader sidebar shows real Chinese titles + 3-level tree instead of a
flat "DH 100, DH 101, ..." list.

Pre-requisite — run `_denzinger_parse_toc.py` first to produce
`scripts/_denzinger_toc/dh_titles.json` and `entries.json`.

Behavior per chunk:
  - chunks 0-6  → hard-coded front-matter labels (封面 / 目錄 / 序言 / …)
  - section_type == 'entry'  with dh_number N
       → chapter_path = dh_titles[N], volume + parent_volume from entries.json
  - section_type == 'commentary' (註解)
       → inherit from preceding non-commentary chunk in same volume,
         label as "<preceding_chapter> · 註解" so dedupe keeps each row
  - section_type == 'header'
       → strip "# " prefix + trim; assign as volume break
  - else → leave chapter_path, fill volume from inheritance only

Writes a new JSONL atomically (backs up old → .jsonl.prerelabel.bak),
pushes to R2, optionally PATCHes ebook_chunks rows to keep DB previews in
sync. The reader's loadToc() reads JSONL via R2, not the DB column, so
R2 push alone is enough for the sidebar.

Usage:
  python scripts/_denzinger_relabel.py --dry-run    # plan only
  python scripts/_denzinger_relabel.py              # write + R2 + DB
  python scripts/_denzinger_relabel.py --no-db      # write + R2, skip DB
  python scripts/_denzinger_relabel.py --no-push    # write JSONL only
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_with_gemini import CHUNKS_DIR, push_to_r2  # noqa: E402

BOOK_ID = "568726d3-967e-457a-ab69-7452b21d606f"
JSONL = CHUNKS_DIR / f"{BOOK_ID}.jsonl"
BACKUP = CHUNKS_DIR / f"{BOOK_ID}.jsonl.prerelabel.bak"
TOC_DIR = Path(__file__).parent / "_denzinger_toc"


# Front matter overrides keyed by page_number (chunk_index drifts every time
# segmenter re-runs, but page numbers are stable). Volume None means render at
# top level (no parent grouping).
FRONT_MATTER: dict[int, dict] = {
    2:  {"chapter_path": "封面", "volume": None, "parent_volume": None,
         "section_type": "header"},
    4:  {"chapter_path": "綜合目錄", "volume": None, "parent_volume": None,
         "section_type": "header"},
    5:  {"chapter_path": "序言", "volume": None, "parent_volume": None,
         "section_type": "header"},
    6:  {"chapter_path": "壹、本書介紹", "volume": None, "parent_volume": None,
         "section_type": "header"},
    21: {"chapter_path": "詳細目錄", "volume": None, "parent_volume": None,
         "section_type": "header"},
    75: {"chapter_path": "第一部分 引言：信經來源與內容說明",
         "volume": "引言",
         "parent_volume": "第一部分：信經",
         "section_type": "header"},
}


def _truncate_title(t: str, max_chars: int = 50) -> str:
    """Sidebar truncates to fit; we trim raw at the data layer too so
    saved titles are reasonable. Strip wrap-induced internal whitespace."""
    cleaned = re.sub(r"\s+", " ", t).strip()
    if len(cleaned) > max_chars:
        return cleaned[:max_chars] + "…"
    return cleaned


def _strip_header_noise(s: str) -> str:
    """Header chunks frequently arrive as '# 塞爾狄卡(Serdika)地區會議...   '
    with stray markdown + trailing spaces. Strip both."""
    s = s.strip()
    # Drop leading '#' markdown hashes
    s = re.sub(r"^#+\s*", "", s)
    # Normalise inner whitespace
    s = re.sub(r"\s+", " ", s)
    # Drop dot-leader page tails sometimes glued on by segmenter
    s = re.sub(r"\.{2,}\s*\d+\s*$", "", s)
    return s.strip()


def load_toc() -> tuple[dict[str, str], list[dict]]:
    dh_path = TOC_DIR / "dh_titles.json"
    entries_path = TOC_DIR / "entries.json"
    if not dh_path.exists() or not entries_path.exists():
        print(
            f"ERROR: {dh_path.name} / {entries_path.name} missing. Run "
            f"_denzinger_parse_toc.py first.",
            file=sys.stderr,
        )
        sys.exit(2)
    dh_titles = json.loads(dh_path.read_text(encoding="utf-8"))
    entries = json.loads(entries_path.read_text(encoding="utf-8"))
    return dh_titles, entries


def build_dh_to_volume(entries: list[dict]) -> dict[int, tuple[str, str]]:
    """{dh_number: (volume_label, part_label)}. First-write-wins so
    canonical pope/council header sticks for every DH in its range."""
    out: dict[int, tuple[str, str]] = {}
    for e in entries:
        start, end = e.get("dh_start"), e.get("dh_end")
        if start is None:
            continue
        vol = e.get("volume") or ""
        part = e.get("part") or ""
        for n in range(start, (end or start) + 1):
            out.setdefault(n, (vol, part))
    return out


def relabel(dry_run: bool, skip_db: bool, push: bool) -> int:
    if not JSONL.exists():
        print(f"ERROR: {JSONL} not found", file=sys.stderr)
        return 1

    dh_titles, entries = load_toc()
    dh_to_vol = build_dh_to_volume(entries)

    chunks: list[dict] = []
    with JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))

    stats = {
        "front_matter": 0,
        "entry_relabel": 0,
        "entry_missing_dh": 0,
        "commentary_inherit": 0,
        "header_clean": 0,
        "unchanged": 0,
    }
    prev_volume: str | None = None
    prev_parent: str | None = None
    prev_chapter: str | None = None
    new_chunks: list[dict] = []
    fm_used_pages: set[int] = set()  # apply each FRONT_MATTER entry only once

    for c in chunks:
        idx = c.get("chunk_index")
        sec = c.get("section_type")
        dh = c.get("dh_number")
        pn = c.get("page_number")
        out = dict(c)

        # 1. Front-matter override — keyed by page_number so chunk_index
        # drift doesn't mislabel chunks. Apply once per page on the first
        # chunk we hit (typical: header or commentary, never a DH entry).
        if pn in FRONT_MATTER and pn not in fm_used_pages and not (sec == "entry" and isinstance(dh, int)):
            fm_used_pages.add(pn)
            override = FRONT_MATTER[pn]
            out["chapter_path"] = override["chapter_path"]
            out["volume"] = override["volume"]
            out["parent_volume"] = override["parent_volume"]
            if override.get("section_type"):
                out["section_type"] = override["section_type"]
            prev_volume = override["volume"]
            prev_parent = override["parent_volume"]
            prev_chapter = override["chapter_path"]
            stats["front_matter"] += 1
            new_chunks.append(out)
            continue

        # 2. Entry with DH number
        if sec == "entry" and isinstance(dh, int):
            title = dh_titles.get(str(dh))
            vol_part = dh_to_vol.get(dh)
            if title:
                out["chapter_path"] = _truncate_title(f"DH {dh} {title}")
                if vol_part:
                    out["volume"] = vol_part[0] or None
                    out["parent_volume"] = vol_part[1] or None
                prev_volume = out.get("volume") or prev_volume
                prev_parent = out.get("parent_volume") or prev_parent
                prev_chapter = out["chapter_path"]
                stats["entry_relabel"] += 1
            else:
                # No TOC match — keep raw "DH N" but inherit volume
                out["chapter_path"] = f"DH {dh}"
                if prev_volume:
                    out["volume"] = prev_volume
                if prev_parent:
                    out["parent_volume"] = prev_parent
                stats["entry_missing_dh"] += 1
            new_chunks.append(out)
            continue

        # 3. Header chunk (council/pope page-start header)
        if sec == "header":
            raw_title = out.get("chapter_path") or ""
            cleaned = _strip_header_noise(raw_title)
            if cleaned:
                out["chapter_path"] = cleaned
                # Headers become a volume break
                out["volume"] = cleaned
                if prev_parent:
                    out["parent_volume"] = prev_parent
                prev_volume = cleaned
                prev_chapter = cleaned
                stats["header_clean"] += 1
            else:
                stats["unchanged"] += 1
            new_chunks.append(out)
            continue

        # 4. Commentary (註解) — inherit from preceding non-commentary
        if sec == "commentary":
            if prev_chapter and prev_chapter != "註解":
                out["chapter_path"] = f"{prev_chapter} · 註解"
            else:
                # Fall back to page-anchored unique label
                pn = c.get("page_number")
                out["chapter_path"] = f"註解（第 {pn} 頁）" if pn else "註解"
            if prev_volume:
                out["volume"] = prev_volume
            if prev_parent:
                out["parent_volume"] = prev_parent
            stats["commentary_inherit"] += 1
            new_chunks.append(out)
            continue

        # 5. Anything else — keep but try to inherit volume so it doesn't
        #    orphan in the sidebar
        if prev_volume and not out.get("volume"):
            out["volume"] = prev_volume
        if prev_parent and not out.get("parent_volume"):
            out["parent_volume"] = prev_parent
        stats["unchanged"] += 1
        new_chunks.append(out)

    # ── Report ─────────────────────────────────────────────────
    print(f"Total chunks      : {len(chunks)}")
    for k, v in stats.items():
        print(f"  {k:<22}: {v}")
    print()
    print("─ Sample first 12 chunks ─")
    for c in new_chunks[:12]:
        vol = c.get("volume") or "—"
        par = c.get("parent_volume") or "—"
        print(f"  [{c['chunk_index']:03d}] {c.get('chapter_path','')!s:<40} "
              f"vol={vol[:25]:<25} parent={par[:20]}")
    print()
    print("─ Sample DH 100-115 range ─")
    sampled = 0
    for c in new_chunks:
        if c.get("section_type") == "entry" and isinstance(c.get("dh_number"), int):
            if 100 <= c["dh_number"] <= 115:
                vol = (c.get("volume") or "—")[:30]
                print(f"  [{c['chunk_index']:03d}] DH {c['dh_number']:<5} {c.get('chapter_path','')[:45]:<45} vol={vol}")
                sampled += 1
                if sampled >= 8:
                    break

    if dry_run:
        print("\n[DRY RUN] no files written, no R2 push, no DB update")
        return 0

    # ── Write ──────────────────────────────────────────────────
    if not BACKUP.exists():
        shutil.copyfile(JSONL, BACKUP)
        print(f"\nBacked up old JSONL → {BACKUP.name}")
    else:
        print(f"\nExisting backup kept: {BACKUP.name}")

    tmp = JSONL.with_suffix(".jsonl.tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for c in new_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(JSONL)
    print(f"Wrote new JSONL: {JSONL}")

    if not push:
        print("[--no-push] R2 not updated")
        return 0

    try:
        push_to_r2(BOOK_ID, JSONL)
        print("✓ R2 push ok")
    except Exception as e:
        print(f"⚠ R2 push failed: {str(e)[:200]}", file=sys.stderr)
        return 2

    if skip_db:
        print("[--no-db] DB previews not patched (chapter_path stale in DB)")
        return 0

    # PATCH each ebook_chunks row's chapter_path so /ebook list + search
    # show real titles. We do it chunk-by-chunk via chunk_index to avoid
    # accidentally re-inserting which would reset section_type / dh_number.
    import time
    import requests
    from ocr_with_gemini import URL, KEY  # noqa: E402

    H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    n = 0
    t0 = time.time()
    for c in new_chunks:
        idx = c["chunk_index"]
        chap = c.get("chapter_path")
        vol = c.get("volume")
        parent = c.get("parent_volume")
        payload = {"chapter_path": chap}
        # volume / parent_volume columns may not exist; PostgREST silently
        # 400s on unknown columns — we'd then fall back to chapter_path-only.
        r = requests.patch(
            f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{BOOK_ID}"
            f"&chunk_index=eq.{idx}",
            headers=H,
            json=payload,
            timeout=30,
        )
        if r.status_code not in (200, 204):
            print(f"  ⚠ row {idx} patch {r.status_code}: {r.text[:100]}",
                  file=sys.stderr)
        else:
            n += 1
        if n and n % 200 == 0:
            print(f"  patched {n}/{len(new_chunks)} ({time.time()-t0:.0f}s)")
    print(f"✓ patched {n}/{len(new_chunks)} DB rows in {time.time()-t0:.0f}s")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-db", action="store_true",
                    help="JSONL + R2 only; don't PATCH DB chapter_path")
    ap.add_argument("--no-push", action="store_true",
                    help="JSONL only; skip R2 + DB (debug)")
    args = ap.parse_args()
    return relabel(
        dry_run=args.dry_run,
        skip_db=args.no_db,
        push=not args.no_push,
    )


if __name__ == "__main__":
    sys.exit(main())
