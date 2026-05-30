"""
Rescue zh-empty DH entry chunks by mining raw OCR content for Chinese prose.

After paragraph-aligned segment + entry-merged consolidate, 24 entries
remain with `content=""` but `source_text>200`. Three causes:
  A. Book only printed the original language (e.g. early creeds in
     Latin/Greek only) — `recolumn` zh block is just「- N -」page footer
  B. Recolumn DID capture 中譯 but segmenter's paragraph alignment
     misrouted it to a neighbouring chunk
  C. The page wasn't picked up by recolumn at all — its presegment.bak
     content has lat + zh mixed inline (two-column OCR'd as one stream)

For (B) and (C) the Chinese text exists in the OCR'd data; we just need
to extract CJK paragraphs from `presegment.bak` and assign them to the
target entry. (A) we cannot rescue — the book itself has no translation.

Approach per zh-empty entry:
  1. Load the raw `presegment.bak` page content for the entry's
     `page_numbers`
  2. Strip the recolumn `--- 拉丁文 ---` / `--- 中譯 ---` markers if
     present, take ONLY the zh half (or the whole content if no marker)
  3. Split into paragraphs (blank-line separated)
  4. Keep paragraphs whose CJK ratio is ≥ 0.30 (excludes pure-Latin
     paragraphs that snuck into the zh column)
  5. Drop page-footer noise (`- N -`, `(N)`)
  6. If ≥1 paragraph survived → assign joined text to entry's `content`

Run after the consolidate / strip / markdownize phases.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ocr_with_gemini import CHUNKS_DIR, URL, H, push_to_r2  # noqa: E402
import requests  # noqa: E402

BOOK_ID = "568726d3-967e-457a-ab69-7452b21d606f"
MAIN_JSONL = CHUNKS_DIR / f"{BOOK_ID}.jsonl"
PRESEGMENT_BAK = CHUNKS_DIR / f"{BOOK_ID}.jsonl.presegment.bak"
RECOLUMN_JSONL = CHUNKS_DIR / f"{BOOK_ID}.recolumn.jsonl"

CJK_RE = re.compile(r"[一-鿿]")
PAGE_FOOTER_RE = re.compile(
    r"^\s*(?:-\s*\d{1,4}\s*-|\(\s*\d{1,4}\s*\)|\d{1,4})\s*$"
)


def cjk_ratio(text: str) -> float:
    non_space = [c for c in text if not c.isspace()]
    if not non_space:
        return 0.0
    cjk = sum(1 for c in non_space if CJK_RE.match(c))
    return cjk / len(non_space)


def load_presegment_pages() -> dict[int, str]:
    out: dict[int, str] = {}
    with PRESEGMENT_BAK.open(encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            pn = c.get("page_number")
            if isinstance(pn, int):
                out[pn] = c.get("content") or ""
    return out


def load_recolumn_pages() -> dict[int, str]:
    """Recolumn JSONL is the column-aware re-OCR — typically richer for
    pages where presegment.bak only has a page-footer."""
    out: dict[int, str] = {}
    if not RECOLUMN_JSONL.exists():
        return out
    with RECOLUMN_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                c = json.loads(line)
            except json.JSONDecodeError:
                continue
            pn = c.get("page_number")
            content = c.get("content") or ""
            if isinstance(pn, int) and content:
                out[pn] = content
    return out


def extract_zh_paragraphs(page_content: str) -> list[str]:
    """Pull Chinese-rich paragraphs out of a page's raw OCR."""
    # If recolumn divider present AND the zh-half is non-trivial, take
    # only that. Some pages have the divider at the very END (the OCR
    # appended an empty 中譯 marker) — in that case fall back to the
    # whole content so we can still find Chinese paragraphs in what was
    # tagged as the Latin column.
    if "--- 中譯 ---" in page_content:
        zh_half = page_content.split("--- 中譯 ---", 1)[1].strip()
        body = zh_half if len(zh_half) > 50 else page_content
    else:
        body = page_content
    # Strip leftover lat-divider line
    body = re.sub(r"^---\s*拉丁文\s*---\s*$", "", body, flags=re.MULTILINE)

    paragraphs = re.split(r"\n{2,}", body)
    out: list[str] = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # Drop page-footer paragraphs
        lines = [
            ln for ln in p.split("\n")
            if not PAGE_FOOTER_RE.match(ln)
        ]
        cleaned = "\n".join(lines).strip()
        if not cleaned:
            continue
        if cjk_ratio(cleaned) < 0.15:
            continue
        # Drop "noise" snippets shorter than 8 CJK chars
        cjk_count = sum(1 for c in cleaned if CJK_RE.match(c))
        if cjk_count < 8:
            continue
        out.append(cleaned)
    return out


def load_chunks() -> list[dict]:
    out: list[dict] = []
    with MAIN_JSONL.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def push_db(chunks: list[dict]) -> None:
    print("Patching DB rows…")
    import time
    t0 = time.time()
    n = 0
    for c in chunks:
        idx = c["chunk_index"]
        payload = {"content": c.get("content") or ""}
        r = requests.patch(
            f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{BOOK_ID}&chunk_index=eq.{idx}",
            headers=H,
            json=payload,
            timeout=60,
        )
        if r.status_code in (200, 204):
            n += 1
        else:
            print(f"  ⚠ row {idx} → {r.status_code}: {r.text[:120]}")
    print(f"✓ patched {n}/{len(chunks)} DB rows in {time.time()-t0:.0f}s")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-db", action="store_true")
    ap.add_argument("--no-r2", action="store_true")
    args = ap.parse_args()

    pre_pages = load_presegment_pages()
    recol_pages = load_recolumn_pages()
    chunks = load_chunks()
    print(f"Loaded {len(pre_pages)} presegment pages, {len(recol_pages)} recolumn pages")

    rescued: list[dict] = []
    skipped_book_blank: list[tuple[int, str]] = []
    for c in chunks:
        if c.get("section_type") != "entry":
            continue
        cp = c.get("chapter_path") or ""
        if not cp.startswith("DH "):
            continue
        zh_existing = (c.get("content") or "").strip()
        lat_existing = (c.get("source_text") or "").strip()
        # Target every zh-empty entry that has at least some Latin source.
        # (Earlier threshold of 200 was a noise filter that incorrectly
        # skipped short entries like DH 1101-1103 and DH 3190 whose
        # Latin segments are only ~150-190 chars.)
        if zh_existing or len(lat_existing) < 50:
            continue
        page_list = c.get("page_numbers") or []
        if not page_list:
            page_list = [c.get("page_number")] if c.get("page_number") else []

        # Collect zh paragraphs across all pages for this entry — prefer
        # recolumn (column-aware re-OCR) over presegment.bak when present.
        all_paras: list[str] = []
        for p in page_list:
            raw = recol_pages.get(p) or pre_pages.get(p, "")
            if not raw:
                continue
            all_paras.extend(extract_zh_paragraphs(raw))

        if not all_paras:
            skipped_book_blank.append((c["chunk_index"], cp[:50]))
            continue

        rescued_text = "\n\n".join(all_paras).strip()
        c["content"] = rescued_text
        rescued.append({
            "chunk_index": c["chunk_index"],
            "chapter_path": cp[:55],
            "paras": len(all_paras),
            "chars": len(rescued_text),
        })

    print(f"Rescued {len(rescued)} entries; {len(skipped_book_blank)} blank "
          f"(book truly has no Chinese — type A)\n")
    for r in rescued:
        print(f"  [{r['chunk_index']:04d}] +{r['paras']}p / {r['chars']:5}ch  | "
              f"{r['chapter_path']}")
    print()
    if skipped_book_blank:
        print("Truly blank (book limitation, can't rescue):")
        for ci, cp in skipped_book_blank:
            print(f"  [{ci:04d}] {cp}")

    if args.dry_run:
        print("\n[DRY RUN] no writes.")
        return 0

    with MAIN_JSONL.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n✓ Wrote main JSONL ({len(chunks)} chunks)")

    if not args.no_r2:
        push_to_r2(BOOK_ID, MAIN_JSONL)
        print("✓ R2 push ok")

    if not args.no_db:
        push_db(chunks)

    return 0


if __name__ == "__main__":
    sys.exit(main())
