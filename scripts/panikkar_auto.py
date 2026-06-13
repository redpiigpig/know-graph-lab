#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumable self-translate queue for Panikkar works WITHOUT an existing 中譯.

Per the user's rule: books that have a published Chinese translation go through
panikkar_build REFERENCE mode (既有中譯 + 原文逐段對照); books that DON'T are
self-translated here — I render my own 繁中 from the original (English / Italian /
Spanish, mostly the Jaca Book Opera Omnia which is Italian), with the original as
the parallel column. No cross-version alignment problem: 繁中 is 1:1 with the
original paragraphs by construction (I translate each one).

Modeled on scripts/mueller_auto.py (resumable, lock, queue):
  - extract original text once (font heading-marking for born-digital PDFs;
    Gemini OCR for scanned) → panikkar_data/<slug>/orig.txt
  - split into sections (## headings) → translate each paragraph → 繁中
    (engine chain NVIDIA→Gemini→Haiku), cached per section in secN.json
  - one reader chunk per section: content=繁中 / sources.<lang>=original, equal ¶
  - cover + chunks → JSONL + R2 + DB

  python scripts/panikkar_auto.py --list
  python scripts/panikkar_auto.py --probe experience-of-god      # extract + 1-para translate
  python scripts/panikkar_auto.py --work experience-of-god --upload
  python scripts/panikkar_auto.py --run-queue                    # all, resumable

Copyrighted source text + my 繁中 stay in local files / DB — never printed.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

_ENV = SCRIPT_DIR.parent / ".env"
if _ENV.exists():
    for _l in _ENV.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

import panikkar_build as pb  # noqa: E402
import ocr_pdf_to_text as ocr  # noqa: E402
from multilang_chunks import write_jsonl  # noqa: E402

Z = SCRIPT_DIR.parent / "z-lib"
DATA_ROOT = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works" / "panikkar_data"

# ── Registry: Panikkar works with NO existing 中譯 → self-translate ────────────
# src = filename PREFIX in z-lib/ (matched by glob). extract: 'font' (born-digital
# text layer) | 'gemini' (scanned). lang = source language for the translate prompt.
WORKS = {
    "experience-of-god": {
        "ebook_id": "55555561-5555-4555-8555-555555555555",
        "title": "神的經驗：奧祕的聖像", "original_title": "The Experience of God: Icons of the Mystery",
        "year": 2006, "src": "The Experience of God", "lang": "en", "extract": "font",
        "volume": "神的經驗（雷蒙‧潘尼卡）", "parent_volume": "神祕與靈性",
    },
    "rhythm-of-being": {
        "ebook_id": "55555562-5555-4555-8555-555555555555",
        "title": "存在的韻律", "original_title": "The Rhythm of Being (Gifford Lectures)",
        "year": 2010, "src": "The Rhythm of Being", "lang": "en", "extract": "epub",
        "volume": "存在的韻律（雷蒙‧潘尼卡）", "parent_volume": "哲學與神學",
    },
    "vedic-experience": {
        "ebook_id": "55555563-5555-4555-8555-555555555555",
        "title": "吠陀經驗", "original_title": "I Veda. Mantramañjari",
        "year": 1977, "src": "I Veda", "lang": "it", "extract": "font",
        "volume": "吠陀經驗（雷蒙‧潘尼卡）", "parent_volume": "印度教",
    },
    "myth-faith-hermeneutics": {
        "ebook_id": "55555564-5555-4555-8555-555555555555",
        "title": "神話、信仰與詮釋學", "original_title": "Mito, fede ed ermeneutica",
        "year": 2000, "src": "Mito, fede ed ermeneutica", "lang": "it", "extract": "font",
        "volume": "神話、信仰與詮釋學（雷蒙‧潘尼卡）", "parent_volume": "奧祕與詮釋學",
    },
    "mysticism-fullness": {
        "ebook_id": "55555565-5555-4555-8555-555555555555",
        "title": "神祕：生命的圓滿", "original_title": "Mística, plenitud de vida (Opera Omnia I.1)",
        "year": 2008, "src": "Obras completas. Tomo I", "lang": "es", "extract": "font",
        "volume": "神祕：生命的圓滿（雷蒙‧潘尼卡）", "parent_volume": "神祕與靈性",
    },
    "pace-interculturalita": {
        "ebook_id": "55555566-5555-4555-8555-555555555555",
        "title": "和平與跨文化", "original_title": "Pace e interculturalità",
        "year": 2002, "src": "Pace e interculturalità", "lang": "it", "extract": "font",
        "volume": "和平與跨文化（雷蒙‧潘尼卡）", "parent_volume": "文化與宗教的對話",
    },
    "religion-world-body": {
        "ebook_id": "55555567-5555-4555-8555-555555555555",
        "title": "宗教、世界與身體", "original_title": "La religión, el mundo y el cuerpo",
        "year": 2014, "src": "La religión, el mundo y el cuerpo", "lang": "es", "extract": "font",
        "volume": "宗教、世界與身體（雷蒙‧潘尼卡）", "parent_volume": "神祕與靈性",
    },
    "mundanal-silencio": {
        "ebook_id": "55555568-5555-4555-8555-555555555555",
        "title": "世間的靜默", "original_title": "El Mundanal Silencio",
        "year": 1999, "src": "El Mundanal Silencio", "lang": "es", "extract": "font",
        "volume": "世間的靜默（雷蒙‧潘尼卡）", "parent_volume": "神祕與靈性",
    },
}

# Order: English first (cleanest), then Italian, then Spanish; huge Mantramañjari last.
QUEUE = ["experience-of-god", "rhythm-of-being", "myth-faith-hermeneutics",
         "pace-interculturalita", "mysticism-fullness", "religion-world-body",
         "mundanal-silencio", "vedic-experience"]


def _data_dir(slug: str) -> Path:
    return DATA_ROOT / slug


def _find_src(prefix: str) -> Path:
    hits = sorted(Z.glob(f"{prefix}*"))
    if not hits:
        raise FileNotFoundError(f"no z-lib file starting with {prefix!r}")
    return hits[0]


# ── extract original → orig.txt (cached) ──────────────────────────────────────
def extract_original(slug: str, *, force: bool = False) -> Path:
    w = WORKS[slug]
    d = _data_dir(slug)
    d.mkdir(parents=True, exist_ok=True)
    out = d / "orig.txt"
    if out.exists() and not force and out.stat().st_size > 100:
        return out
    src = _find_src(w["src"])
    if w["extract"] == "font":
        pages = ocr.extract_text_with_font_headings(src)
    elif w["extract"] == "epub":
        text = _epub_to_marked_text(src)
        out.write_text(text, encoding="utf-8")
        return out
    else:  # gemini OCR (scanned)
        pages = ocr.ocr_pdf(src, model="gemini-2.5-flash", mark_headings=True, batch=20)
    out.write_text(ocr.pages_to_text(pages), encoding="utf-8")
    return out


def _epub_to_marked_text(src: Path) -> str:
    """EPUB → text with `## ` headings (h1-h3) for self-translate splitting."""
    import zipfile
    import re
    from bs4 import BeautifulSoup
    rows: list[str] = []
    with zipfile.ZipFile(src) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith((".xhtml", ".html", ".htm"))]
        for n in sorted(names):
            soup = BeautifulSoup(zf.read(n), "html.parser")
            for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "blockquote", "li"]):
                txt = re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()
                if not txt:
                    continue
                if el.name in ("h1", "h2", "h3", "h4"):
                    rows.append("")
                    rows.append("## " + txt)
                    rows.append("")
                else:
                    rows.append(txt)
    return "\n".join(rows)


# ── translate (resumable per section) ─────────────────────────────────────────
def _sec_path(slug: str, idx: int) -> Path:
    return _data_dir(slug) / f"sec{idx}.json"


def load_orig_sections(slug: str) -> list[dict]:
    return pb.load_en_sections(extract_original(slug))


def translate_work(slug: str, translate_para, *, save_every: int = 5, maxparas=None) -> None:
    secs = load_orig_sections(slug)
    lang = WORKS[slug]["lang"]
    print(f"  {slug}: {len(secs)} sections (lang={lang})", flush=True)
    for i, s in enumerate(secs):
        cp = _sec_path(slug, i)
        cache = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
        src = list(s["paras"])
        zh = cache.get("zh", [])
        zh = (zh + [None] * len(src))[:len(src)]
        title_zh = cache.get("title_zh") or None
        todo = [j for j in range(len(src)) if not zh[j]]
        if maxparas:
            todo = todo[:maxparas]
        if title_zh is None and s["heading"] not in ("(front)", ""):
            title_zh = translate_para(s["heading"].lstrip("# ")) or s["heading"]
        elif title_zh is None:
            title_zh = s["heading"]
        for done, j in enumerate(todo, 1):
            zh[j] = translate_para(src[j])
            if done % save_every == 0 or done == len(todo):
                cp.write_text(json.dumps(
                    {"heading": s["heading"], "title_zh": title_zh, "src": src, "zh": zh},
                    ensure_ascii=False, indent=1), encoding="utf-8")
        if not todo:  # nothing to translate but ensure cache exists
            cp.write_text(json.dumps(
                {"heading": s["heading"], "title_zh": title_zh, "src": src, "zh": zh},
                ensure_ascii=False, indent=1), encoding="utf-8")
        filled = sum(1 for z in zh if z)
        print(f"    sec{i} 「{(title_zh or '')[:18]}」 {filled}/{len(src)}", flush=True)


def is_done(slug: str) -> bool:
    secs = load_orig_sections(slug)
    for i, s in enumerate(secs):
        cp = _sec_path(slug, i)
        if not cp.exists():
            return False
        c = json.loads(cp.read_text(encoding="utf-8"))
        zh = c.get("zh") or []
        # allow a few holdout paras (engine refusals) — 95% filled = done
        n = len(s["paras"])
        if n and sum(1 for z in zh if z) < max(1, int(n * 0.95)):
            return False
    return True


# ── build + upload ────────────────────────────────────────────────────────────
def build_chunks(slug: str) -> list[dict]:
    w = WORKS[slug]
    pb.select_book("unknown-christ")  # neutral defaults; we pass volume explicitly
    lang = w["lang"]
    chunks = [pb.build_multilang_chunk(
        chunk_index=0, chapter_path="封面", content_zh="## 封面", sources={}, source_order=[],
        volume=w["volume"], parent_volume=w["parent_volume"], chunk_type="cover", page_number=1)]
    secs = load_orig_sections(slug)
    ci = 1
    for i, s in enumerate(secs):
        cp = _sec_path(slug, i)
        if not cp.exists():
            continue
        c = json.loads(cp.read_text(encoding="utf-8"))
        zh = c.get("zh") or []
        src = c.get("src") or []
        zh = [(z or sv) for z, sv in zip(zh, src)]  # fallback to original if a para unfilled
        if not any(zh):
            continue
        chunk = pb.build_section_chunk(
            chunk_index=ci, title_zh=c.get("title_zh") or s["heading"],
            zh_paras=zh, source_paras={lang: src},
            source_heads={lang: s["heading"].lstrip("# ").strip()},
            source_order=[lang], volume=w["volume"], parent_volume=w["parent_volume"],
            page_number=ci + 1)
        chunks.append(chunk)
        ci += 1
    return chunks


def ensure_row(slug: str):
    import requests
    import translate_ebook_to_zh as te
    w = WORKS[slug]
    row = {"id": w["ebook_id"], "title": w["title"],
           "subtitle": f"{_SRC_LABEL.get(w['lang'],'外文')}原典＋繁中逐段自譯",
           "author": "雷蒙‧潘尼卡", "author_en": "Raimon Panikkar",
           "original_title": w["original_title"], "original_publish_year": w["year"],
           "file_type": "epub", "category": "世界宗教", "subcategory": "基督教"}
    r = requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id",
                      headers={**te.H_JSON, "Prefer": "resolution=merge-duplicates"},
                      json=row, timeout=30)
    print(f"  ebooks row upsert HTTP {r.status_code}", flush=True)


_SRC_LABEL = {"en": "英文", "it": "義大利文", "es": "西班牙文"}


def upload(slug: str, chunks: list[dict], out_path: Path):
    import datetime
    import requests
    import translate_ebook_to_zh as te
    eid = WORKS[slug]["ebook_id"]
    try:
        te.se.push_to_r2(eid, out_path)
        print("  ✓ pushed R2", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ R2 push failed: {e}", flush=True)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    patch = {"chunk_count": len(chunks), "total_chars": sum(len(c["content"]) for c in chunks),
             "total_pages": len(chunks), "parsed_at": now, "standardized_at": now}
    requests.patch(f"{te.URL}/rest/v1/ebooks?id=eq.{eid}", headers=te.H_JSON, json=patch, timeout=30)
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}", headers=te.H_GET, timeout=30)
    rows = [{"ebook_id": eid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
             "page_number": c["page_number"], "chapter_path": c["chapter_path"],
             "content": c["content"][:200], "char_count": len(c["content"])} for c in chunks]
    for k in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=rows[k:k + 25], timeout=60)
    print(f"  ✓ row + previews  chunk_count={len(chunks)}", flush=True)


def out_jsonl(slug: str) -> Path:
    base = os.environ.get("EBOOK_CHUNKS_DIR")
    if not base:
        raise RuntimeError("EBOOK_CHUNKS_DIR not set")
    return Path(base) / f"{WORKS[slug]['ebook_id']}.jsonl"


def build_and_upload(slug: str, *, do_upload: bool):
    chunks = build_chunks(slug)
    out = out_jsonl(slug)
    write_jsonl(chunks, out)
    print(f"  wrote {out.name} ({len(chunks)} chunks)", flush=True)
    if do_upload:
        ensure_row(slug)
        upload(slug, chunks, out)


# ── queue ─────────────────────────────────────────────────────────────────────
def run_work(slug: str, *, do_upload: bool, maxparas=None):
    print(f"=== {slug} : {WORKS[slug]['title']} ===", flush=True)
    engine = pb.make_engine(WORKS[slug]["lang"])
    translate_work(slug, engine, maxparas=maxparas)
    build_and_upload(slug, do_upload=do_upload)


def run_queue():
    for slug in QUEUE:
        try:
            if is_done(slug):
                print(f"=== {slug}: already done, (re)building ===", flush=True)
                build_and_upload(slug, do_upload=True)
                continue
            run_work(slug, do_upload=True)
        except Exception as e:  # noqa: BLE001 — keep the queue going
            print(f"  ⚠ {slug} failed: {str(e)[:200]}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--work", type=str)
    ap.add_argument("--probe", type=str)
    ap.add_argument("--extract", type=str)
    ap.add_argument("--maxparas", type=int, default=None)
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--run-queue", action="store_true")
    args = ap.parse_args()

    if args.list:
        for slug in QUEUE:
            w = WORKS[slug]
            try:
                src = _find_src(w["src"]).name[:40]
            except FileNotFoundError:
                src = "⚠ MISSING"
            print(f"  {slug:26} {w['lang']} {w['extract']:6} done={is_done(slug) if _sec_path(slug,0).exists() else False}  {src}")
        return
    if args.extract:
        p = extract_original(args.extract, force=True)
        secs = load_orig_sections(args.extract)
        print(f"{args.extract}: extracted → {p} ({len(secs)} sections)")
        return
    if args.probe:
        eng = pb.make_engine(WORKS[args.probe]["lang"])
        secs = load_orig_sections(args.probe)
        body = next((p for s in secs for p in s["paras"] if len(p) > 80), "")
        zh = eng(body)
        # stats only — don't echo copyrighted source / translated text
        print(f"{args.probe}: sections={len(secs)} src_para_chars={len(body)} "
              f"zh_chars={len(zh)} ok={bool(zh.strip())}")
        return
    if args.work:
        run_work(args.work, do_upload=args.upload, maxparas=args.maxparas)
        return
    if args.run_queue:
        run_queue()
        return
    ap.print_help()


if __name__ == "__main__":
    main()
