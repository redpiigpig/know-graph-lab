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
    (engine chain Gemini→NVIDIA→Haiku, each tier 2-strike), cached per section in secN.json
  - one reader chunk per section: content=繁中 / sources.<lang>=original, equal ¶
  - cover + chunks → JSONL + R2 + DB

  python scripts/panikkar_auto.py --list
  python scripts/panikkar_auto.py --probe experience-of-god      # extract + 1-para translate
  python scripts/panikkar_auto.py --work experience-of-god --upload
  python scripts/panikkar_auto.py --work rhythm-of-being --translate-only --maxparas 10 --save-every 1 --backend haiku
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
        pages = ocr.ocr_pdf(src, model=os.environ.get("GEMINI_MODEL", "gemini-flash-latest"), mark_headings=True, batch=20)
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


def _split_long_paras(secs: list[dict], max_chars: int = 4000) -> list[dict]:
    """Split any paragraph longer than max_chars on sentence boundaries. Prevents
    oversized translate prompts (epub bodies without clean <p> splits produced a
    single 200k-token 'paragraph' → 400 prompt-too-long). Both translate and build
    use this, so 繁中 stays 1:1 with the (split) source paragraphs."""
    import re
    out: list[dict] = []
    for s in secs:
        np: list[str] = []
        for p in s["paras"]:
            if len(p) <= max_chars:
                np.append(p)
                continue
            parts = re.split(r"(?<=[.!?。！？；;])\s+", p)
            buf = ""
            for part in parts:
                if buf and len(buf) + len(part) + 1 > max_chars:
                    np.append(buf)
                    buf = part
                else:
                    buf = (buf + " " + part).strip() if buf else part
            if buf:
                np.append(buf)
        out.append({"heading": s["heading"], "paras": np})
    return out


def load_orig_sections(slug: str) -> list[dict]:
    return _split_long_paras(pb.load_en_sections(extract_original(slug)))


def _provenance(cache: dict, zh: list, size: int) -> list:
    engines = list(cache.get("engines") or [])
    engines = (engines + [None] * size)[:size]
    for i, value in enumerate(zh):
        if value and not engines[i]:
            engines[i] = "unknown"
    return engines


def translate_work(
    slug: str,
    translate_para,
    *,
    save_every: int = 5,
    maxparas=None,
    max_total_paras: int | None = None,
    engine_name: str = "unknown",
) -> int:
    secs = load_orig_sections(slug)
    lang = WORKS[slug]["lang"]
    print(f"  {slug}: {len(secs)} sections (lang={lang})", flush=True)
    translated_total = 0
    for i, s in enumerate(secs):
        if max_total_paras is not None and translated_total >= max_total_paras:
            break
        cp = _sec_path(slug, i)
        cache = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
        src = list(s["paras"])
        zh = cache.get("zh", [])
        zh = (zh + [None] * len(src))[:len(src)]
        engines = _provenance(cache, zh, len(src))
        title_zh = cache.get("title_zh") or None
        todo = [j for j in range(len(src)) if not zh[j]]
        if maxparas:
            todo = todo[:maxparas]
        if max_total_paras is not None:
            todo = todo[:max(0, max_total_paras - translated_total)]
        if title_zh is None and s["heading"] not in ("(front)", ""):
            title_zh = translate_para(s["heading"].lstrip("# ")) or s["heading"]
            title_engine = engine_name if title_zh != s["heading"] else "source-fallback"
        elif title_zh is None:
            title_zh = s["heading"]
            title_engine = "source"
        else:
            title_engine = cache.get("title_engine") or "unknown"

        def save() -> None:
            cp.write_text(json.dumps({
                **cache,
                "heading": s["heading"],
                "title_zh": title_zh,
                "title_engine": title_engine,
                "src": src,
                "zh": zh,
                "engines": engines,
            }, ensure_ascii=False, indent=1), encoding="utf-8")

        for done, j in enumerate(todo, 1):
            output = translate_para(src[j])
            if output:
                zh[j] = output
                engines[j] = engine_name
                translated_total += 1
            if done % save_every == 0 or done == len(todo):
                save()
        if not todo:  # nothing to translate but ensure cache exists
            save()
        filled = sum(1 for z in zh if z)
        print(f"    sec{i} 「{(title_zh or '')[:18]}」 {filled}/{len(src)}", flush=True)
    return translated_total


def review_local_work(
    slug: str,
    translate_para,
    *,
    engine_name: str,
    max_total_paras: int | None = None,
) -> int:
    """Replace only Ollama drafts with an online translation, preserving all
    pre-existing cloud/unknown paragraphs. Does not upload by itself."""
    reviewed = 0
    folder = _data_dir(slug)
    for cp in sorted(folder.glob("sec*.json"), key=lambda p: int(p.stem[3:])):
        cache = json.loads(cp.read_text(encoding="utf-8"))
        src = list(cache.get("src") or [])
        zh = (list(cache.get("zh") or []) + [None] * len(src))[:len(src)]
        engines = _provenance(cache, zh, len(src))
        todo = [i for i in range(len(src)) if zh[i] and engines[i] == "ollama"]
        if max_total_paras is not None:
            todo = todo[:max(0, max_total_paras - reviewed)]
        for i in todo:
            output = translate_para(src[i])
            if output:
                zh[i] = output
                engines[i] = engine_name
                reviewed += 1
                cache.update({"zh": zh, "engines": engines})
                cp.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
            if max_total_paras is not None and reviewed >= max_total_paras:
                break
        if max_total_paras is not None and reviewed >= max_total_paras:
            break
    print(f"  {slug}: reviewed {reviewed} Ollama draft paragraphs via {engine_name}", flush=True)
    return reviewed


def count_local_drafts(slug: str) -> int:
    count = 0
    for cp in _data_dir(slug).glob("sec*.json"):
        try:
            cache = json.loads(cp.read_text(encoding="utf-8"))
            count += sum(e == "ollama" for e in (cache.get("engines") or []))
        except (OSError, json.JSONDecodeError):
            continue
    return count


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
MAX_PARAS_PER_CHUNK = 10


def _chunked_paras(zh: list[str], src: list[str], max_paras: int = MAX_PARAS_PER_CHUNK):
    """Yield paragraph groups so a heading-less EPUB does not become one huge page."""
    for start in range(0, len(zh), max_paras):
        yield zh[start:start + max_paras], src[start:start + max_paras]


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
        base_title = (c.get("title_zh") or s["heading"] or "").strip()
        if base_title in ("", "(front)"):
            base_title = w["title"]
        source_head = s["heading"].lstrip("# ").strip()
        if source_head in ("", "(front)"):
            source_head = w["original_title"]
        groups = list(_chunked_paras(zh, src))
        for part_no, (zh_group, src_group) in enumerate(groups, start=1):
            title = base_title if len(groups) == 1 else f"{base_title}（{part_no}）"
            head = source_head if len(groups) == 1 else f"{source_head} ({part_no})"
            chunk = pb.build_section_chunk(
                chunk_index=ci, title_zh=title,
                zh_paras=zh_group, source_paras={lang: src_group},
                source_heads={lang: head},
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


def run_draft_queue_step(backend: str, max_total_paras: int) -> int:
    """Fill a small number of missing paragraphs locally; never build/upload."""
    for slug in QUEUE:
        try:
            if is_done(slug):
                continue
            engine = pb.make_engine(WORKS[slug]["lang"], backend=backend)
            count = translate_work(
                slug, engine, save_every=1, max_total_paras=max_total_paras,
                engine_name=backend)
            print(f"SUPERVISOR_RESULT job=local-draft slug={slug} translated={count}", flush=True)
            return count
        except Exception as exc:  # keep looking for a source that is locally available
            print(f"  ⚠ local draft {slug} skipped: {str(exc)[:200]}", flush=True)
    print("SUPERVISOR_RESULT job=local-draft all-done-or-unavailable translated=0", flush=True)
    return 0


def run_review_queue_step(backend: str, max_total_paras: int, do_upload: bool) -> int:
    """Online-AI handoff: replace a bounded batch of Ollama drafts, then publish
    only a work that no longer contains local drafts."""
    for slug in QUEUE:
        if not count_local_drafts(slug):
            continue
        engine = pb.make_engine(WORKS[slug]["lang"], backend=backend)
        count = review_local_work(
            slug, engine, engine_name=backend, max_total_paras=max_total_paras)
        if do_upload and count_local_drafts(slug) == 0:
            build_and_upload(slug, do_upload=True)
        print(f"SUPERVISOR_RESULT job=online-review slug={slug} reviewed={count} "
              f"remaining={count_local_drafts(slug)}", flush=True)
        return count
    print("SUPERVISOR_RESULT job=online-review no-local-drafts reviewed=0", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--work", type=str)
    ap.add_argument("--probe", type=str)
    ap.add_argument("--extract", type=str)
    ap.add_argument("--maxparas", type=int, default=None)
    ap.add_argument("--max-total-paras", type=int, default=None,
                    help="global paragraph budget across all sections")
    ap.add_argument("--save-every", type=int, default=5)
    ap.add_argument("--backend",
                    choices=["auto", "gemini", "gemini-first", "nvidia", "haiku", "ollama"],
                    default="auto",
                    help="translation backend for self-translate runs; auto preserves the existing chain")
    ap.add_argument("--translate-only", action="store_true",
                    help="only fill sec*.json cache; do not build JSONL or upload")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--run-queue", action="store_true")
    ap.add_argument("--draft-queue-step", action="store_true",
                    help="bounded local draft pass; checkpoint only, never upload")
    ap.add_argument("--review-local", action="store_true",
                    help="with --work: replace only provenance=ollama paragraphs")
    ap.add_argument("--review-queue-step", action="store_true",
                    help="bounded online review pass over provenance=ollama paragraphs")
    ap.add_argument("--local-draft-status", action="store_true")
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
    if args.local_draft_status:
        for slug in QUEUE:
            print(f"{slug}\tollama_drafts={count_local_drafts(slug)}")
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
        if args.review_local:
            if args.backend == "ollama":
                ap.error("--review-local requires an online backend")
            eng = pb.make_engine(WORKS[args.work]["lang"], backend=args.backend)
            review_local_work(
                args.work, eng, engine_name=args.backend,
                max_total_paras=args.max_total_paras)
            if args.upload and count_local_drafts(args.work) == 0:
                build_and_upload(args.work, do_upload=True)
            return
        if args.translate_only:
            eng = pb.make_engine(WORKS[args.work]["lang"], backend=args.backend)
            translate_work(
                args.work, eng, save_every=max(1, args.save_every),
                maxparas=args.maxparas, max_total_paras=args.max_total_paras,
                engine_name=args.backend)
            return
        run_work(args.work, do_upload=args.upload, maxparas=args.maxparas)
        return
    if args.run_queue:
        run_queue()
        return
    if args.draft_queue_step:
        if args.backend != "ollama":
            ap.error("--draft-queue-step is restricted to --backend ollama")
        run_draft_queue_step(args.backend, max(1, args.max_total_paras or 3))
        return
    if args.review_queue_step:
        if args.backend == "ollama":
            ap.error("--review-queue-step requires an online backend")
        run_review_queue_step(
            args.backend, max(1, args.max_total_paras or 10), args.upload)
        return
    ap.print_help()


if __name__ == "__main__":
    main()
