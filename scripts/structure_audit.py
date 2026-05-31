"""Read-only structural-quality audit over the whole ebook library.

Phase-1 diagnostic (see discussion 2026-05-31). Touches NOTHING — it only
READS DB chunk previews (content[:200], char_count, chapter_path, chunk_type,
source_lang) and scores each book on how badly its STRUCTURE (not OCR
accuracy) was assembled. Goal: turn "I can't check 1743 books by hand" into
"here are the 50 messiest, and why".

Signals (all computable from the 200-char DB preview):
  S1 NO_TOC          — fraction of chunks with empty chapter_path (empty sidebar)
  S2 BODY_AS_TITLE   — chapter_paths that look like a body sentence, not a title
  S3 HEADER_POLLUTE  — a running header/booktitle string repeats at the start of
                       many chunks (page furniture bled into body)
  S4 PAGENUM_NOISE   — chunks whose body starts with a bare page number
  S5 HEADING_BLEED   — markdown heading line that swallowed the first body sentence
  S6 GIANT_CHUNK     — a chunk far larger than the median (ate its neighbours)

mess_score in [0,100]; primary_defect = the dominant contributor.

Usage:
    python scripts/structure_audit.py                 # full run -> c:/tmp/*
    python scripts/structure_audit.py --limit 50      # quick test on 50 books
"""
from __future__ import annotations
import argparse, json, os, re, statistics, sys
from collections import Counter
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

OUT_JSON = Path("c:/tmp/structure_audit.json")
OUT_TXT = Path("c:/tmp/structure_audit_report.txt")

HEADING_RE = re.compile(r"^\s*#{1,4}\s+(.+?)\s*$")
BODY_PUNCT_MID = re.compile(r"[，。！？；](?=.{4,})")   # punctuation with text after it
LEAD_PAGENUM_RE = re.compile(r"^\s*\d{1,4}(\s|$|[^\d一-鿿])")
EM_DASH_HEADING = re.compile(r"第[一二三四五六七八九十百千零0-9]+[章節卷]\s*[—\-－]+")


def fetch_all(path: str, select: str, page: int = 1000) -> list[dict]:
    """Paginate a PostgREST GET fully (no ordering — used for the ebooks list)."""
    out, offset = [], 0
    while True:
        r = requests.get(f"{URL}/rest/v1/{path}?select={select}",
                         headers={**H, "Range-Unit": "items", "Range": f"{offset}-{offset+page-1}"},
                         timeout=120)
        r.raise_for_status()
        rows = r.json()
        out.extend(rows)
        if len(rows) < page:
            break
        offset += page
    return out


CHUNK_SELECT = "chunk_index,chunk_type,page_number,chapter_path,char_count,content,source_lang"


def fetch_book_chunks(bid: str, page: int = 1000) -> list[dict]:
    """Fetch one book's chunk previews, paginated, ordered by chunk_index.
    Per-book filter hits the ebook_id FK index — avoids the full-table sort
    that 500s the server."""
    out, offset = [], 0
    while True:
        r = requests.get(
            f"{URL}/rest/v1/ebook_chunks?ebook_id=eq.{bid}&select={CHUNK_SELECT}&order=chunk_index",
            headers={**H, "Range-Unit": "items", "Range": f"{offset}-{offset+page-1}"},
            timeout=120)
        r.raise_for_status()
        rows = r.json()
        out.extend(rows)
        if len(rows) < page:
            break
        offset += page
    return out


def strip_md(s: str) -> str:
    s = re.sub(r"^\s*#{1,4}\s+", "", s)
    return s.strip()


def looks_like_body(cp: str) -> bool:
    """A chapter_path that is really a body fragment, not a title."""
    if not cp:
        return False
    cp = cp.strip()
    if len(cp) <= 16:
        return False
    # A title rarely has mid-sentence punctuation followed by more text.
    if BODY_PUNCT_MID.search(cp):
        return True
    # Very long with no heading-ish shape.
    return len(cp) > 34


def score_book(meta: dict, chunks: list[dict]) -> dict:
    n = len(chunks)
    if n == 0:
        return {}
    cps = [(c.get("chapter_path") or "").strip() for c in chunks]
    contents = [(c.get("content") or "") for c in chunks]
    ccs = [c.get("char_count") or 0 for c in chunks]
    has_src = any(c.get("source_lang") for c in chunks)
    types = Counter(c.get("chunk_type") for c in chunks)

    # Underparsed: a whole book collapsed into 1-2 chunks is a PARSE failure,
    # not a structure-mess. Tag it separately and skip the noisy signals.
    underparsed = n <= 2

    # S1 no TOC
    n_no_cp = sum(1 for x in cps if not x)
    s1 = n_no_cp / n

    # S2 body-as-title (needs a meaningful sample of present chapter_paths)
    cp_present = [x for x in cps if x]
    n_bodylike = sum(1 for x in cp_present if looks_like_body(x))
    s2 = (n_bodylike / len(cp_present)) if len(cp_present) >= 5 else 0.0

    # S3 running-header pollution: most common 6-12 char body prefix
    # (only meaningful with enough chunks)
    s3, hdr_str, hdr_pct = 0.0, None, 0.0
    if n >= 5:
        prefixes = []
        for ct in contents:
            body = strip_md(ct).replace(" ", "")
            if len(body) >= 6:
                prefixes.append(body[:10])
        if prefixes:
            top, freq = Counter(prefixes).most_common(1)[0]
            hdr_pct = freq / n
            if hdr_pct >= 0.20 and len(top) >= 4:
                s3 = min(1.0, hdr_pct / 0.6)
                hdr_str = top

    # S4 leading page-number noise
    n_pagenum = sum(1 for ct in contents if LEAD_PAGENUM_RE.match(strip_md(ct)))
    s4 = n_pagenum / n

    # S5 heading bleed
    def bleed(ct: str) -> bool:
        first = ct.split("\n", 1)[0]
        m = HEADING_RE.match(first)
        if not m:
            return False
        h = m.group(1)
        if len(h) <= 25:
            return False
        # long heading that contains an em-dash chapter marker + mid punctuation
        if EM_DASH_HEADING.search(h) and BODY_PUNCT_MID.search(h):
            return True
        return BODY_PUNCT_MID.search(h) is not None
    n_bleed = sum(1 for ct in contents if bleed(ct))
    s5 = min(1.0, n_bleed / max(1, n) * 5)   # even a few % is notable

    # S6 giant chunk (needs enough chunks for a stable median)
    med = statistics.median(ccs) if ccs else 0
    n_giant = sum(1 for x in ccs if med and x > 3 * med) if n >= 5 else 0
    s6 = min(1.0, n_giant / max(1, n) * 4)

    # composite (weights tuned so "raw page dump" floats to the top)
    mess = (35 * s1 + 20 * s2 + 20 * s3 + 10 * s4 + 10 * s5 + 5 * s6)

    comps = {"NO_TOC": 35 * s1, "BODY_AS_TITLE": 20 * s2, "HEADER_POLLUTE": 20 * s3,
             "PAGENUM_NOISE": 10 * s4, "HEADING_BLEED": 10 * s5, "GIANT_CHUNK": 5 * s6}
    primary = max(comps, key=comps.get) if mess > 0 else "OK"
    if underparsed:
        primary = "UNDERPARSED"

    return {
        "id": meta["id"], "title": meta.get("title"), "file_type": meta.get("file_type"),
        "category": meta.get("category"), "subcategory": meta.get("subcategory"),
        "n_chunks": n, "chunk_types": dict(types), "has_source_text": has_src,
        "mess_score": round(mess, 1), "primary_defect": primary,
        "signals": {
            "no_toc_pct": round(s1, 3), "body_as_title_pct": round(s2, 3),
            "header_str": hdr_str, "header_pct": round(hdr_pct, 3),
            "pagenum_noise_pct": round(s4, 3), "heading_bleed_n": n_bleed,
            "giant_chunk_n": n_giant,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only first N books (test)")
    args = ap.parse_args()

    print("fetching ebooks list…", flush=True)
    books = fetch_all("ebooks", "id,title,file_type,category,subcategory,chunk_count")
    books = [b for b in books if (b.get("chunk_count") or 0) > 0]
    if args.limit:
        books = books[:args.limit]
    bymeta = {b["id"]: b for b in books}
    print(f"  {len(books)} books with chunks", flush=True)

    print("fetching chunk previews per-book (DB only, no Drive)…", flush=True)
    from concurrent.futures import ThreadPoolExecutor, as_completed
    grouped: dict[str, list] = {}
    n_rows = 0
    done = 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(fetch_book_chunks, bid): bid for bid in bymeta}
        for fut in as_completed(futs):
            bid = futs[fut]
            try:
                ch = fut.result()
            except Exception as e:
                print(f"  ! {bid}: {str(e)[:80]}", flush=True)
                ch = []
            grouped[bid] = ch
            n_rows += len(ch)
            done += 1
            if done % 200 == 0:
                print(f"  {done}/{len(bymeta)} books, {n_rows} chunks so far", flush=True)
    rows = list(range(n_rows))  # only len() is used later
    print(f"  {n_rows} chunk rows", flush=True)

    results = []
    for bid, meta in bymeta.items():
        ch = grouped.get(bid)
        if not ch:
            continue
        sc = score_book(meta, ch)
        if sc:
            results.append(sc)

    results.sort(key=lambda x: x["mess_score"], reverse=True)
    OUT_JSON.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- human report ----
    L = []
    L.append(f"STRUCTURE AUDIT — {len(results)} books, {len(rows)} chunks\n")
    # distribution
    defect_dist = Counter(r["primary_defect"] for r in results)
    band = lambda s: ("≥60 嚴重" if s >= 60 else "40-60 偏髒" if s >= 40 else
                      "20-40 輕微" if s >= 20 else "<20 大致乾淨")
    band_dist = Counter(band(r["mess_score"]) for r in results)
    ft_band = Counter((r["file_type"], band(r["mess_score"])) for r in results)
    L.append("== 亂度分布 ==")
    for k in ["≥60 嚴重", "40-60 偏髒", "20-40 輕微", "<20 大致乾淨"]:
        L.append(f"  {k}: {band_dist.get(k,0)}")
    L.append("\n== 主要病徵分布 ==")
    for k, v in defect_dist.most_common():
        L.append(f"  {k}: {v}")
    L.append("\n== file_type × 亂度 ==")
    for (ft, b), v in sorted(ft_band.items()):
        L.append(f"  {ft:5} {b}: {v}")

    L.append("\n\n== 最髒 50 本 ==")
    for r in results[:50]:
        s = r["signals"]
        why = []
        if s["no_toc_pct"] >= 0.4: why.append(f"無目錄{int(s['no_toc_pct']*100)}%")
        if s["body_as_title_pct"] >= 0.3: why.append(f"標題像內文{int(s['body_as_title_pct']*100)}%")
        if s["header_str"]: why.append(f"頁眉重複「{s['header_str']}」{int(s['header_pct']*100)}%")
        if s["pagenum_noise_pct"] >= 0.2: why.append(f"頁碼滲入{int(s['pagenum_noise_pct']*100)}%")
        if s["heading_bleed_n"]: why.append(f"標題吃內文×{s['heading_bleed_n']}")
        if s["giant_chunk_n"]: why.append(f"超大chunk×{s['giant_chunk_n']}")
        L.append(f"[{r['mess_score']:5.1f}] {r['primary_defect']:14} {r['file_type']:4} "
                 f"n={r['n_chunks']:<4} {(r['title'] or '')[:34]}")
        L.append(f"         {r['id']}  | {'; '.join(why)}")

    OUT_TXT.write_text("\n".join(L), encoding="utf-8")
    print(f"\n✓ wrote {OUT_JSON}")
    print(f"✓ wrote {OUT_TXT}")
    print("\n".join(L[:30]))


if __name__ == "__main__":
    main()
