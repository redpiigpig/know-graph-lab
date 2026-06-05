"""Continuous auto-transcription queue for Max Müller's collected works.

Rolls through every public-domain Müller work on archive.org, one at a time,
producing a bilingual (英→繁中) reader book per work — download _djvu.txt →
OCR reflow → chapter split → translate paragraphs (NVIDIA deepseek) → cover +
JSONL → R2 + DB. Resumable per work + per section; a lock file stops a scheduled
re-fire from stacking on a still-running instance.

Bilingual by default (sources={en}; reader shows 中/對照/英). German parallels
exist for a few works (see WORKS[*]['de_id']) — those can be upgraded to真三欄
later, like 《宗教學導論》 (handled separately by mueller_build.py). 宗教學導論 is
NOT in this queue.

Reuses the pure helpers (reflow, engine, prompt) from mueller_build.

  python scripts/mueller_auto.py --list                 # show queue + status
  python scripts/mueller_auto.py --dry <slug>           # split/count one work, no LLM
  python scripts/mueller_auto.py --work <slug> --upload  # one work end-to-end
  python scripts/mueller_auto.py --run-queue            # all pending works, continuous
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import mueller_build as mb  # loads .env, reflow, engine, prompt  # noqa: E402
from multilang_chunks import build_multilang_chunk, validate_multilang_chunk, write_jsonl  # noqa: E402

DATA_ROOT = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works" / "mueller_data"
SRC_DIR = Path("c:/tmp/mueller_auto")
LOCK = DATA_ROOT / "_queue.lock"

# ── Registry: every Müller work to auto-transcribe (英→繁中 bilingual) ──────────
# eid = ebook_id; en_id = archive.org item; de_id = German parallel (for a later
# trilingual upgrade, NOT used by the bilingual auto run). split: 'lecture' tries
# LECTURE/ordinal headings then falls back to coarse; 'coarse' chunks by paragraph.
WORKS = [
    dict(slug="origin-growth-religion", eid="44444445-4444-4444-8444-444444444444",
         title="宗教起源與發展講座", title_en="Lectures on the Origin and Growth of Religion",
         year=1878, category="宗教學", subcategory="宗教學", parent="宗教學奠基",
         en_id="lecturesonthegro00mulluoft", de_id=None, split="lecture"),
    dict(slug="natural-religion", eid="44444441-4444-4444-8444-444444444444",
         title="自然宗教", title_en="Natural Religion", year=1889,
         category="宗教學", subcategory="宗教學", parent="吉福德講座（宗教學四部）",
         en_id="naturalreligiong00ml", de_id=None, split="lecture"),
    dict(slug="physical-religion", eid="44444442-4444-4444-8444-444444444444",
         title="物質宗教", title_en="Physical Religion", year=1891,
         category="宗教學", subcategory="宗教學", parent="吉福德講座（宗教學四部）",
         en_id="physicalreligion00ml", de_id="in.ernet.dli.2015.340661", split="lecture"),
    dict(slug="anthropological-religion", eid="44444443-4444-4444-8444-444444444444",
         title="人類學宗教", title_en="Anthropological Religion", year=1892,
         category="宗教學", subcategory="宗教學", parent="吉福德講座（宗教學四部）",
         en_id="anthropologicalr00ml", de_id=None, split="lecture"),
    dict(slug="psychological-religion", eid="44444444-4444-4444-8444-444444444444",
         title="心理宗教（神智學）", title_en="Theosophy, or Psychological Religion", year=1895,
         category="宗教學", subcategory="宗教學", parent="吉福德講座（宗教學四部）",
         en_id="theosophyorpsych00mluoft", de_id="11614918bsb", split="lecture"),
    dict(slug="comparative-mythology", eid="4444444b-4444-4444-8444-444444444444",
         title="比較神話學", title_en="Comparative Mythology", year=1856,
         category="宗教學", subcategory="神話學", parent="語言與神話學",
         en_id="comparativemytho00ml", de_id=None, split="coarse"),
    dict(slug="contributions-mythology-1", eid="4444444c-4444-4444-8444-444444444444",
         title="神話科學論集（卷一）", title_en="Contributions to the Science of Mythology, Vol. I",
         year=1897, category="宗教學", subcategory="神話學", parent="語言與神話學",
         en_id="conributionstosc01ml", de_id="beitrgezueinerw01ldgoog", split="coarse"),
    dict(slug="contributions-mythology-2", eid="4444444d-4444-4444-8444-444444444444",
         title="神話科學論集（卷二）", title_en="Contributions to the Science of Mythology, Vol. II",
         year=1897, category="宗教學", subcategory="神話學", parent="語言與神話學",
         en_id="conributionstosc02ml", de_id="beitrgezueinerw00ldgoog", split="coarse"),
    dict(slug="science-language-1", eid="44444446-4444-4444-8444-444444444444",
         title="語言科學講座（第一輯）", title_en="Lectures on the Science of Language, First Series",
         year=1864, category="宗教學", subcategory="宗教學", parent="語言與神話學",
         en_id="lecturesonscienc00mulliala", de_id="10583046bsb", split="lecture"),
    dict(slug="science-language-2", eid="44444447-4444-4444-8444-444444444444",
         title="語言科學講座（第二輯）", title_en="Lectures on the Science of Language, Second Series",
         year=1864, category="宗教學", subcategory="宗教學", parent="語言與神話學",
         en_id="b28135568", de_id="11104518bsb", split="lecture"),
    dict(slug="india-teach", eid="44444449-4444-4444-8444-444444444444",
         title="印度能教我們什麼？", title_en="India: What Can It Teach Us?", year=1883,
         category="宗教學", subcategory="宗教學", parent="印度學",
         en_id="indiawhatcanitte00ml", de_id="indieninseinerwe00ml", split="lecture"),
    dict(slug="six-systems", eid="4444444a-4444-4444-8444-444444444444",
         title="印度哲學六派", title_en="The Six Systems of Indian Philosophy", year=1899,
         category="宗教學", subcategory="宗教學", parent="印度學",
         en_id="sixsystemsofindi017601mbp", de_id=None, split="coarse"),
    dict(slug="chips-1", eid="44444448-4444-4444-8444-444444444444",
         title="德國作坊雜記（卷一）", title_en="Chips from a German Workshop, Vol. I", year=1867,
         category="宗教學", subcategory="宗教學", parent="文集與回憶",
         en_id="chipsfromagerma01mlgoog", de_id=None, split="coarse"),
]

# ── chapter splitting ────────────────────────────────────────────────────────
_ORD = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4, "FIFTH": 5, "SIXTH": 6,
        "SEVENTH": 7, "EIGHTH": 8, "NINTH": 9, "TENTH": 10, "ELEVENTH": 11, "TWELFTH": 12}
_LECT_NUM = re.compile(r"^\s*(LECTURE|VORLESUNG|CHAPTER)\s+([IVXLC]+|\d+)\b", re.I)
_LECT_ORD = re.compile(r"^\s*(" + "|".join(_ORD) + r")\s+(LECTURE|CHAPTER)\b", re.I)
_BACKMATTER = re.compile(r"longmans|paternoster|\bfcp\.?\s*8vo\b|williams\s+and\s+norgate|"
                         r"^\s*INDEX\s*$|by\s+the\s+same\s+author|works\s+by", re.I)


def _is_lecture_head(s: str) -> bool:
    return bool(_LECT_NUM.match(s) or _LECT_ORD.match(s))


_ROMAN_MAP = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
_ZH_NUM = "零一二三四五六七八九十"


def _roman(s: str) -> int | None:
    s = s.upper()
    if any(c not in _ROMAN_MAP for c in s):
        return None
    t = p = 0
    for c in reversed(s):
        v = _ROMAN_MAP[c]
        t += -v if v < p else v
        p = max(p, v)
    return t or None


def _zh_ord(n: int) -> str:
    if n <= 10:
        return _ZH_NUM[n]
    if n < 20:
        return "十" + _ZH_NUM[n - 10]
    if n < 100:
        return _ZH_NUM[n // 10] + "十" + (_ZH_NUM[n % 10] if n % 10 else "")
    return str(n)


def zh_section_title(head: str) -> str:
    """'LECTURE IV' → '第四講'; 'CHAPTER 3' → '第三章'; 'THIRD LECTURE' → '第三講';
    otherwise the cleaned original heading."""
    h = head.strip().rstrip(".")
    m = _LECT_NUM.match(h)
    if m:
        kind = m.group(1).upper()
        n = int(m.group(2)) if m.group(2).isdigit() else _roman(m.group(2))
        if n:
            unit = "章" if kind.startswith("CHAP") else "講"
            return f"第{_zh_ord(n)}{unit}"
    m = _LECT_ORD.match(h)
    if m:
        n = _ORD.get(m.group(1).upper())
        if n:
            unit = "章" if m.group(2).upper().startswith("CHAP") else "講"
            return f"第{_zh_ord(n)}{unit}"
    return re.sub(r"\s{2,}", " ", h)


def split_lecture(raw_lines: list[str]) -> list[dict] | None:
    """Slice on LECTURE/CHAPTER headings (numbered or ordinal). Returns
    [{title, lines}] candidate slices (caller reflows + filters TOC stubs)."""
    idxs = [i for i, l in enumerate(raw_lines) if _is_lecture_head(l.strip())]
    pruned: list[int] = []
    for i in idxs:
        if not pruned or i - pruned[-1] > 3:
            pruned.append(i)
    if len(pruned) < 3:
        return None
    secs = []
    for k, start in enumerate(pruned):
        end = pruned[k + 1] if k + 1 < len(pruned) else len(raw_lines)
        secs.append({"title": raw_lines[start].strip(), "lines": raw_lines[start + 1:end]})
    return secs


def _is_clean_prose(p: str) -> bool:
    """A real English prose paragraph: long, mostly ASCII letters/spaces, few
    digits/symbols. Filters call numbers, indices, Greek OCR specks, ad blurbs."""
    if len(p) < 250:
        return False
    letters = sum(c.isalpha() and ord(c) < 128 for c in p)
    nonascii = sum(ord(c) > 127 for c in p)
    digits = sum(c.isdigit() for c in p)
    return letters / len(p) > 0.7 and nonascii / len(p) < 0.03 and digits / len(p) < 0.05


def trim_frontmatter(paras: list[str]) -> list[str]:
    """Drop leading front matter (bookplate / title page / TOC / ads) — skip until
    the first clean prose paragraph."""
    for i, p in enumerate(paras):
        if _is_clean_prose(p):
            return paras[i:]
    return paras


def split_coarse(paras: list[str], per: int = 30) -> list[dict]:
    """Group already-reflowed paragraphs into ~`per`-paragraph chunks."""
    secs = []
    for k in range(0, len(paras), per):
        secs.append({"title": f"第 {k // per + 1} 節", "paras": paras[k:k + per]})
    return secs


def drop_backmatter(paras: list[str]) -> list[str]:
    """Trim trailing publisher catalogue / index paragraphs."""
    cut = len(paras)
    # scan the tail third for the first sustained back-matter run
    for i in range(len(paras) - 1, max(0, len(paras) * 2 // 3), -1):
        if _BACKMATTER.search(paras[i]):
            cut = i
    return paras[:cut]


def _lect_num(head: str) -> int | None:
    h = head.strip()
    m = _LECT_NUM.match(h)
    if m:
        return int(m.group(2)) if m.group(2).isdigit() else _roman(m.group(2))
    m = _LECT_ORD.match(h)
    if m:
        return _ORD.get(m.group(1).upper())
    return None


def build_sections(raw_lines: list[str], strategy: str) -> list[dict]:
    """→ [{title, paras}] for any work. Tries lecture split (filter TOC/front-matter
    stubs by ¶ count, dedupe by lecture number keeping the largest body, sanity-check
    the numbering); else coarse. Never loses body content."""
    if strategy == "lecture":
        lect = split_lecture(raw_lines)
        if lect:
            cand = []
            for s in lect:
                paras = drop_backmatter(mb.reflow(s["lines"], mb._EN_HEADER_RE))
                num = _lect_num(s["title"])
                if len(paras) >= 8 and num:  # real body with a parseable number
                    cand.append({"num": num, "title": s["title"], "paras": paras})
            # dedupe: one section per lecture number, keep the largest body
            best: dict[int, dict] = {}
            for c in cand:
                if c["num"] not in best or len(c["paras"]) > len(best[c["num"]]["paras"]):
                    best[c["num"]] = c
            ordered = [best[n] for n in sorted(best)]
            # sanity: contiguous-ish numbering, sensible count → trust the split
            if ordered and 3 <= len(ordered) <= 40 and max(best) <= len(ordered) * 1.6:
                return [{"title": zh_section_title(c["title"]), "paras": c["paras"]} for c in ordered]
    # coarse fallback (also strategy == "coarse")
    return split_coarse(trim_frontmatter(drop_backmatter(mb.reflow(raw_lines, mb._EN_HEADER_RE))))


# ── source download ──────────────────────────────────────────────────────────
def fetch_djvu(archive_id: str) -> Path:
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    dst = SRC_DIR / f"{archive_id}.txt"
    if dst.exists() and dst.stat().st_size > 10_000:
        return dst
    url = f"https://archive.org/download/{archive_id}/{archive_id}_djvu.txt"
    print(f"  downloading {url}", flush=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as r, open(dst, "wb") as f:
        f.write(r.read())
    return dst


# ── per-work cache + build ───────────────────────────────────────────────────
def work_dir(slug: str) -> Path:
    return DATA_ROOT / slug


def sec_path(slug: str, i: int) -> Path:
    return work_dir(slug) / f"sec{i}.json"


def translate_work(work: dict, translate_para, *, maxsec=None) -> int:
    """Download + split + translate one work, resumably. Returns paragraphs done."""
    txt = fetch_djvu(work["en_id"])
    raw_lines = txt.read_text(encoding="utf-8", errors="replace").splitlines()
    sections = build_sections(raw_lines, work["split"])
    if maxsec:
        sections = sections[:maxsec]
    work_dir(work["slug"]).mkdir(parents=True, exist_ok=True)
    print(f"  {work['slug']}: {len(sections)} sections "
          f"({sum(len(s['paras']) for s in sections)} ¶)", flush=True)
    done = 0
    for i, s in enumerate(sections):
        cp = sec_path(work["slug"], i)
        cache = json.loads(cp.read_text(encoding="utf-8")) if cp.exists() else {}
        en = s["paras"]
        zh = (cache.get("zh", []) + [None] * len(en))[:len(en)]
        todo = [j for j in range(len(en)) if not zh[j]]
        if todo:
            print(f"    sec{i}「{s['title'][:40]}」 ¶={len(en)} todo={len(todo)}", flush=True)
        for k, j in enumerate(todo, 1):
            zh[j] = translate_para(en[j], "")
            if k % 3 == 0 or k == len(todo):
                cp.write_text(json.dumps({"title": s["title"], "en": en, "zh": zh},
                                         ensure_ascii=False, indent=1), encoding="utf-8")
        if not todo:  # ensure cache exists even for already-complete sections
            cp.write_text(json.dumps({"title": s["title"], "en": en, "zh": zh},
                                     ensure_ascii=False, indent=1), encoding="utf-8")
        done += sum(1 for z in zh if z)
        if LOCK.exists():  # keep the lock fresh so a scheduled re-fire won't double-run
            LOCK.touch()
    return done


def cover_chunk(work: dict) -> dict:
    c = build_multilang_chunk(chunk_index=0, chapter_path="封面", content_zh="## 封面",
                              sources={}, source_order=[], volume=work["title"],
                              parent_volume=work["parent"], chunk_type="cover", page_number=1)
    validate_multilang_chunk(c)
    return c


def section_chunk(work: dict, sec: dict, ci: int) -> dict:
    zh_rows = [f"## {sec['title']}"] + [z or "" for z in sec["zh"]]
    en_rows = [f"## {sec['title']}"] + sec["en"]
    c = build_multilang_chunk(
        chunk_index=ci, chapter_path=f"{work['title']} · {sec['title']}",
        content_zh="\n\n".join(zh_rows), sources={"en": "\n\n".join(en_rows)},
        source_order=["en"], volume=work["title"], parent_volume=work["parent"],
        page_number=ci + 1, title_en=sec["title"])
    validate_multilang_chunk(c)
    return c


def assemble_and_upload(work: dict):
    chunks = [cover_chunk(work)]
    ci = 1
    i = 0
    while sec_path(work["slug"], i).exists():
        sec = json.loads(sec_path(work["slug"], i).read_text(encoding="utf-8"))
        if any(sec.get("zh") or []):
            chunks.append(section_chunk(work, sec, ci))
            ci += 1
        i += 1
    out = Path(os.environ["EBOOK_CHUNKS_DIR"]) / f"{work['eid']}.jsonl"
    write_jsonl(chunks, out)
    ensure_row(work)
    _upload(work["eid"], chunks, out)
    print(f"  ✓ {work['slug']} uploaded ({len(chunks)} chunks)", flush=True)


def ensure_row(work: dict):
    import requests
    row = {"id": work["eid"], "title": work["title"], "author": "弗里德里希‧馬克斯‧穆勒",
           "author_en": "Friedrich Max Müller", "original_title": work["title_en"],
           "original_publish_year": work["year"], "file_type": "epub",
           "category": work["category"], "subcategory": work["subcategory"]}
    te = _te()
    requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id",
                  headers={**te.H_JSON, "Prefer": "resolution=merge-duplicates"},
                  json=row, timeout=30)


def _te():
    import translate_ebook_to_zh as te
    return te


def _upload(eid: str, chunks: list[dict], out_path: Path):
    import requests
    te = _te()
    try:
        te.se.push_to_r2(eid, out_path)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ R2 push failed: {e}", flush=True)
    total_chars = sum(len(c["content"]) for c in chunks)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    patch = {"chunk_count": len(chunks), "total_chars": total_chars,
             "total_pages": len(chunks), "parsed_at": now, "standardized_at": now}
    requests.patch(f"{te.URL}/rest/v1/ebooks?id=eq.{eid}", headers=te.H_JSON, json=patch, timeout=30)
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}", headers=te.H_GET, timeout=30)
    rows = [{"ebook_id": eid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
             "page_number": c["page_number"], "chapter_path": c["chapter_path"],
             "content": c["content"][:200], "char_count": len(c["content"])} for c in chunks]
    for i in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=rows[i:i + 25], timeout=60)


def is_done(work: dict) -> bool:
    """Heuristic: at least one section cache exists and has no untranslated gaps."""
    wd = work_dir(work["slug"])
    secs = sorted(wd.glob("sec*.json")) if wd.exists() else []
    if not secs:
        return False
    for p in secs:
        s = json.loads(p.read_text(encoding="utf-8"))
        if any(z is None or z == "" for z in s.get("zh", [None])):
            return False
    return True


# ── lock ─────────────────────────────────────────────────────────────────────
def acquire_lock() -> bool:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        age = time.time() - LOCK.stat().st_mtime
        if age < 6 * 3600:  # a fresh lock means another run is active
            print(f"  another queue run holds the lock ({age/60:.0f} min old) — exiting", flush=True)
            return False
    LOCK.write_text(str(os.getpid()), encoding="utf-8")
    return True


def release_lock():
    try:
        LOCK.unlink()
    except FileNotFoundError:
        pass


# ── CLI ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--init-rows", action="store_true", help="create all ebook rows (metadata only)")
    ap.add_argument("--dry", metavar="SLUG")
    ap.add_argument("--work", metavar="SLUG")
    ap.add_argument("--run-queue", action="store_true")
    ap.add_argument("--maxsec", type=int, default=None, help="cap sections (smoke)")
    ap.add_argument("--upload", action="store_true")
    args = ap.parse_args()

    by_slug = {w["slug"]: w for w in WORKS}

    if args.list:
        for w in WORKS:
            print(f"  [{'✓' if is_done(w) else ' '}] {w['slug']:28s} {w['title']}  ({w['en_id']})")
        return

    if args.init_rows:
        for w in WORKS:
            ensure_row(w)
            print(f"  row {w['eid']}  {w['title']}", flush=True)
        return

    if args.dry:
        w = by_slug[args.dry]
        txt = fetch_djvu(w["en_id"])
        secs = build_sections(txt.read_text(encoding="utf-8", errors="replace").splitlines(), w["split"])
        print(f"{w['slug']}: {len(secs)} sections, {sum(len(s['paras']) for s in secs)} ¶")
        for i, s in enumerate(secs[:12]):
            print(f"  sec{i} 「{s['title'][:50]}」 ¶={len(s['paras'])} | {s['paras'][0][:60] if s['paras'] else '—'}")
        return

    if args.work:
        tp = mb.make_engine()
        w = by_slug[args.work]
        translate_work(w, tp, maxsec=args.maxsec)
        if args.upload:
            assemble_and_upload(w)
        return

    if args.run_queue:
        if not acquire_lock():
            return
        try:
            tp = mb.make_engine()
            for w in WORKS:
                if is_done(w):
                    print(f"  ✓ {w['slug']} already done — skip", flush=True)
                    continue
                print(f"▶ {w['slug']} — {w['title']}", flush=True)
                try:
                    translate_work(w, tp)
                    assemble_and_upload(w)
                except Exception as e:  # noqa: BLE001
                    print(f"  ✗ {w['slug']} failed: {type(e).__name__}: {e}", flush=True)
                    continue
            print("queue complete", flush=True)
        finally:
            release_lock()
        return

    ap.print_help()


if __name__ == "__main__":
    main()
