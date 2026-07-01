"""Add the German 1921 source column to Jung's *Psychological Types* trilingual reader.

The English (Baynes 1923) + 繁中 edition already exists (257 chunks, ebook
22222223-…), built by ``jung_psychological_types_overnight.py``. That English is
a faithful translation of the 1921 German original, so chapter order and
paragraph order match. This script:

  1. parses the clean Gutenberg #61543 German HTML into per-chapter paragraphs,
  2. maps the 13 German sections onto the 12 English chapter-groups
     (Einleitung→INTRODUCTION, I..XI→CHAPTER I..XI, Schlusswort→CHAPTER XI),
  3. distributes each chapter's German paragraphs across that chapter's English
     chunks *proportionally by cumulative char length* (chunk-level alignment,
     ebook-collected-works align-strategy #4 — column not strictly per-paragraph),
  4. rebuilds the reader JSONL with sources={de,en}, source_order=[de,en]
     (原文德在前、英譯後), and upserts previews.

Run ``--inspect`` first (no upload; writes a sample to c:/tmp) then a real run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html as htmllib
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from multilang_chunks import build_multilang_chunk, validate_multilang_chunk, write_jsonl

EBID = "22222223-2222-4222-8222-222222222223"
TITLE = "心理類型（1921德文·1923英譯·繁中三欄）"
DATA = Path(".claude/skills/ebook-collected-works/jung_data/psychological-types-1923")
PARTS = DATA / "parts"
DE_HTML = Path(r"C:/tmp/jung_ptypen_de_1921.html")

# German h2 (exact prefixes) → English heading group. Skipped: TOC, Vorrede, license.
DE_CHAP_ORDER = [
    ("Einleitung", "INTRODUCTION"),
    ("I Das Typenproblem in der antiken", "CHAPTER I"),
    ("II Über Schillers Ideen", "CHAPTER II"),
    ("III Das Apollinische", "CHAPTER III"),
    ("IV Das Typenproblem in der Menschenkenntnis", "CHAPTER IV"),
    ("V Das Typenproblem in der Dichtkunst", "CHAPTER V"),
    ("VI Das Typenproblem in der Psychiatrie", "CHAPTER VI"),
    ("VII Das Problem der typischen Einstellungen", "CHAPTER VII"),
    ("VIII Das Typenproblem in der modernen Philosophie", "CHAPTER VIII"),
    ("IX Das Typenproblem in der Biographik", "CHAPTER IX"),
    ("X Allgemeine Beschreibung der Typen", "CHAPTER X"),
    ("XI Definitionen", "CHAPTER XI"),
    ("Schlusswort", "CONCLUSION"),
]


def load_env() -> None:
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def parse_german_chapters() -> dict[str, list[str]]:
    """Return {english_heading: [german paragraph, …]} in document order."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(DE_HTML.read_text(encoding="utf-8"), "html.parser")
    # Drop noise: page numbers, footnote blocks, PG boilerplate header/footer.
    for sel in soup.select("span.pagenum, div.footnotes, #pg-header, #pg-footer, .toc, #pg-machine-header"):
        sel.decompose()
    for a in soup.find_all("a"):
        txt = a.get_text()
        if re.fullmatch(r"\[?\d+\]?", txt.strip()):  # footnote ref marker
            a.decompose()
        else:
            a.unwrap()

    # Walk body top-level in order, switching chapter at each mapped h2.
    body = soup.body or soup
    chapters: dict[str, list[str]] = {}
    current: str | None = None
    for el in body.descendants:
        if getattr(el, "name", None) == "h2":
            head = re.sub(r"\s+", " ", el.get_text(" ")).strip()
            current = None
            for prefix, eng in DE_CHAP_ORDER:
                if head.startswith(prefix):
                    current = eng
                    chapters.setdefault(eng, [])
                    break
        elif getattr(el, "name", None) in ("p", "h3") and current is not None:
            # h3 subheadings are kept as their own short paragraph.
            txt = _clean(el.get_text(" "))
            if txt:
                if el.name == "h3":
                    txt = "### " + txt
                chapters[current].append(txt)
    return chapters


# Chapter XI (Definitionen) is ordered alphabetically by *headword*, which
# differs between German and English (de #20 Empfindung = en #47 Sensation), so
# the monotonic paragraph aligner cannot be used there. Match German definitions
# to the English definition's chunk by translated headword instead. English key
# = lower-cased headword as it appears in the Baynes text (see extraction).
DE2EN_DEF = {
    "abstraktion": "abstraction", "affektivität": "affectivity", "affekt": "affect",
    "anima": "anima", "apperception": "apperception", "apperzeption": "apperception",
    "archaismus": "archaism", "assimilation": "assimilation", "bewusstsein": "consciousness",
    "bild": "image", "collektiv": "collective", "kollektiv": "collective",
    "kompensation": "compensation", "concretismus": "concretism", "konkretismus": "concretism",
    "construktiv": "constructive", "konstruktiv": "constructive", "denken": "thinking",
    "differenzierung": "differentiation", "dissimilation": "dissimilation",
    "einfühlung": "feeling-into", "einstellung": "attitude", "enantiodromie": "enantiodromia",
    "empfindung": "sensation", "extraversion": "extraversion", "fühlen": "feeling",
    "gefühl": "feeling", "funktion": "function", "ich": "ego", "idee": "idea",
    "identifikation": "identification", "identität": "identity", "individualität": "individuality",
    "individuation": "individuation", "individuum": "individual", "intellekt": "intellect",
    "introjektion": "introjection", "introversion": "introversion", "intuition": "intuition",
    "irrational": "irrational", "libido": "libido", "machtkomplex": "power-complex",
    "minderwertige funktion": "inferior", "orientierung": "orientation", "phantasie": "phantasy",
    "projektion": "projection", "rational": "rational", "reduktiv": "reductive",
    "seele": "soul", "seelenbild": "soul-image", "selbst": "self", "subjektstufe": "subjective",
    "symbol": "symbol", "synthetisch": "synthetic", "transscendente funktion": "transcendent",
    "transzendente funktion": "transcendent", "trieb": "instinct", "typus": "type",
    "unbewusst": "unconscious", "wille": "will",
}


def align_definitions(de_paras: list[str], rows: list[dict]) -> dict[int, list[str]]:
    """Headword-match German definitions onto the English definition's chunk."""
    from collections import defaultdict

    # record each English definition's chunk + a within-chapter ordering rank so
    # German defs sharing a chunk can be re-sorted into the English (not German)
    # alphabetical order → their first paragraphs line up column-to-column.
    en_chunk_of: dict[str, int] = {}
    en_rank_of: dict[str, int] = {}
    rank = 0
    for r in rows:
        for mm in re.finditer(r"(?:^|\s)(\d{1,2})\s?\.\s+([A-Z][A-Za-z\-]{2,})", r["en"]):
            w = mm.group(2).lower()
            if w != "definitions" and w not in en_chunk_of:
                en_chunk_of[w] = r["idx"]
                en_rank_of[w] = rank
                rank += 1
    first_def_chunk = min(en_chunk_of.values()) if en_chunk_of else rows[0]["idx"]

    # split German paragraphs into definition blocks (numbered para starts one)
    blocks: list[tuple[str, list[str]]] = []
    for p in de_paras:
        mm = re.match(r"\s*\d+\.\s+([A-Za-zÄÖÜäöüß][\wÄÖÜäöüß\- ]*?)[\.,]", p)
        if mm:
            hw = re.sub(r"\s+", " ", mm.group(1)).strip().lower()
            blocks.append((hw, [p]))
        elif blocks:
            blocks[-1][1].append(p)
        else:
            blocks.append(("__preamble__", [p]))

    staged: dict[int, list[tuple[int, list[str]]]] = defaultdict(list)
    for hw, paras in blocks:
        en_hw = DE2EN_DEF.get(hw) or hw
        if en_hw in en_chunk_of:
            staged[en_chunk_of[en_hw]].append((en_rank_of[en_hw], paras))
        elif hw == "__preamble__":
            staged[first_def_chunk].append((-1, paras))
        # else unmatched → leave blank rather than misalign

    chunk_de: dict[int, list[str]] = {}
    for cidx, items in staged.items():
        items.sort(key=lambda t: t[0])  # English order within the chunk
        chunk_de[cidx] = [p for _, paras in items for p in paras]
    return chunk_de


def _clean(s: str) -> str:
    s = htmllib.unescape(s)
    s = s.replace("\xad", "")           # soft hyphen
    s = re.sub(r"\[\d+\]", "", s)       # stray footnote markers
    s = re.sub(r"\s+", " ", s).strip()
    return s


def align_paras(en: list[str], de: list[str]) -> dict[int, int]:
    """Length-based monotonic DP paragraph alignment (Gale-Church style).

    Returns ``{de_index: en_index}``. Handles 1-1/1-2/2-1/2-2 blocks plus
    insert/delete, so a locally varying DE/EN length ratio no longer causes the
    cumulative drift that pure proportional split suffers from.
    """
    import math

    n, m = len(en), len(de)
    el = [len(x) + 1 for x in en]
    dl = [len(x) + 1 for x in de]
    INF = float("inf")
    D = [[INF] * (m + 1) for _ in range(n + 1)]
    back: list[list] = [[None] * (m + 1) for _ in range(n + 1)]
    D[0][0] = 0.0
    # English (a) is over-segmented ~2.6–3.4× vs German (b) in the narrative
    # chapters, so allow up to 3 English paras per German. The log-ratio cost
    # picks the best a per b; penalties only break ties toward fewer merges.
    steps = [(1, 1, 0.0), (1, 2, 1.0), (2, 1, 1.0), (2, 2, 1.2), (1, 0, 2.5), (0, 1, 2.5)]

    def cost(i: int, j: int, a: int, b: int, pen: float) -> float:
        if a == 0 or b == 0:
            return pen
        se, sd = sum(el[i:i + a]), sum(dl[j:j + b])
        return (math.log(se / sd)) ** 2 + pen

    for i in range(n + 1):
        for j in range(m + 1):
            if D[i][j] == INF:
                continue
            for a, b, pen in steps:
                if i + a <= n and j + b <= m:
                    c = D[i][j] + cost(i, j, a, b, pen)
                    if c < D[i + a][j + b]:
                        D[i + a][j + b] = c
                        back[i + a][j + b] = (i, j, a, b)

    i, j = n, m
    de2en: dict[int, int] = {}
    while (i, j) != (0, 0):
        pi, pj, a, b = back[i][j]
        en_idx = pi if a > 0 else max(0, pi - 1)   # DE-insert → attach to prev EN
        for jj in range(pj, pj + b):
            de2en[jj] = en_idx
        i, j = pi, pj
    return de2en


def build(inspect: bool, upload: bool) -> None:
    load_env()
    chapters = parse_german_chapters()

    src_rows = [json.loads(l) for l in (DATA / "source_chunks.jsonl").open(encoding="utf-8")]
    # group English chunks by heading (in order)
    groups: list[tuple[str, list[dict]]] = []
    for r in src_rows:
        h = r["heading"]
        if not groups or groups[-1][0] != h:
            groups.append((h, []))
        groups[-1][1].append(r)

    # map each English group-heading to its CHAPTER key
    def keyof(h: str) -> str:
        h = h.strip().upper()
        if h.startswith("INTRODUCTION"):
            return "INTRODUCTION"
        m = re.match(r"CHAPTER\s+([IVXLCDM]+)", h)
        return f"CHAPTER {m.group(1)}" if m else h

    from collections import defaultdict

    def para_align(de_paras: list[str], rows: list[dict]) -> dict[int, list[str]]:
        en_paras, en_chunk = [], []
        for r in rows:
            for p in r["en"].split("\n\n"):
                if p.strip():
                    en_paras.append(p)
                    en_chunk.append(r["idx"])
        cd: dict[int, list[str]] = defaultdict(list)
        if de_paras and en_paras:
            de2en = align_paras(en_paras, de_paras)
            for jj, de in enumerate(de_paras):
                cd[en_chunk[de2en.get(jj, len(en_paras) - 1)]].append(de)
        return cd

    de_by_chunkidx: dict[int, str] = {}
    report = []
    for head, rows in groups:
        key = keyof(head)
        de_paras = chapters.get(key, [])
        if key == "CHAPTER XI":
            # This heading group holds Definitions + the Conclusion (Schlusswort).
            # Split at the last definition chunk: defs → headword match (order
            # differs per language), conclusion → paragraph DP (same order).
            en_def_chunk = {}
            for r in rows:
                for mm in re.finditer(r"(?:^|\s)(\d{1,2})\s?\.\s+([A-Z][A-Za-z\-]{2,})", r["en"]):
                    if mm.group(2).lower() != "definitions":
                        en_def_chunk.setdefault(mm.group(2).lower(), r["idx"])
            last_def = max(en_def_chunk.values()) if en_def_chunk else rows[-1]["idx"]
            def_rows = [r for r in rows if r["idx"] <= last_def]
            concl_rows = [r for r in rows if r["idx"] > last_def]
            chunk_de = align_definitions(de_paras, def_rows)
            for cidx, paras in para_align(chapters.get("CONCLUSION", []), concl_rows).items():
                chunk_de.setdefault(cidx, []).extend(paras)
        else:
            chunk_de = para_align(de_paras, rows)
        for r in rows:
            de_by_chunkidx[r["idx"]] = "\n\n".join(chunk_de.get(r["idx"], []))
        report.append((key, len(rows), len(de_paras),
                       sum(1 for r in rows if de_by_chunkidx[r["idx"]])))

    print("chapter        en_chunks  de_paras  chunks_with_de")
    for key, nch, ndp, nwith in report:
        print(f"{key:14s} {nch:9d} {ndp:9d} {nwith:15d}")

    # assemble trilingual JSONL
    out_chunks = [{
        "chunk_index": 0, "chunk_type": "chapter", "page_number": None,
        "chapter_path": "封面", "format": "markdown", "content": f"## {TITLE}",
    }]
    for idx in sorted(de_by_chunkidx):
        part = PARTS / f"{idx:04d}.json"
        obj = json.loads(part.read_text(encoding="utf-8"))
        de = de_by_chunkidx[idx]
        # keep the de key even when blank so every content page offers the same
        # 中/德/英 toggle (a handful of pages fall inside one continuous German
        # paragraph shared with a neighbour → blank de column, ZH+EN intact).
        c = build_multilang_chunk(
            chunk_index=idx,
            chapter_path=f"{TITLE} · {idx:04d}",
            volume=TITLE, parent_volume="榮格早期著作",
            title_en=obj["heading"],
            content_zh=obj["zh"], sources={"de": de, "en": obj["en"]},
            source_order=["de", "en"],
        )
        validate_multilang_chunk(c)
        out_chunks.append(c)

    if inspect:
        # dump a mid-Chapter-I sample for eyeballing
        sample = next(c for c in out_chunks if c["chunk_index"] == 12)
        Path(r"C:/tmp/_ptypen_sample.txt").write_text(
            "=== ZH ===\n" + sample["content"][:1500] +
            "\n\n=== DE ===\n" + sample.get("sources", {}).get("de", "")[:1500] +
            "\n\n=== EN ===\n" + sample.get("sources", {}).get("en", "")[:1500],
            encoding="utf-8")
        print(f"\ninspect: assembled {len(out_chunks)} chunks; sample → C:/tmp/_ptypen_sample.txt")
        return

    base = Path(os.environ.get("EBOOK_CHUNKS_DIR") or r"G:/我的雲端硬碟/資料/電子書/_chunks")
    base.mkdir(parents=True, exist_ok=True)
    out = base / f"{EBID}.jsonl"
    write_jsonl(out_chunks, out)
    print(f"wrote {len(out_chunks)} chunks -> {out}")

    if not upload:
        return
    import requests
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h_json = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json",
              "Prefer": "resolution=merge-duplicates"}
    h_get = {"apikey": key, "Authorization": f"Bearer {key}"}
    now = dt.datetime.utcnow().isoformat() + "Z"
    row = {"id": EBID, "title": TITLE, "display_mode": "standard",
           "chunk_count": len(out_chunks), "total_pages": len(out_chunks),
           "total_chars": sum(len(c["content"]) for c in out_chunks),
           "standardized_at": now}
    requests.patch(f"{url}/rest/v1/ebooks?id=eq.{EBID}", headers=h_json, json=row, timeout=30).raise_for_status()
    requests.delete(f"{url}/rest/v1/ebook_chunks?ebook_id=eq.{EBID}", headers=h_get, timeout=60).raise_for_status()
    previews = [{"ebook_id": EBID, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
                 "page_number": c.get("page_number"), "chapter_path": c["chapter_path"],
                 "content": c["content"][:200], "char_count": len(c["content"])} for c in out_chunks]
    for i in range(0, len(previews), 20):
        r = requests.post(f"{url}/rest/v1/ebook_chunks", headers=h_json, json=previews[i:i + 20], timeout=60)
        r.raise_for_status()
    print(f"upserted ebook {EBID} previews={len(previews)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("--no-upload", action="store_true")
    args = ap.parse_args()
    build(inspect=args.inspect, upload=not args.no_upload)


if __name__ == "__main__":
    main()
