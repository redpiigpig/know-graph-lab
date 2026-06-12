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
    # ── 2026-06-12 補入：印度學早期卷 + 兩本回憶錄（user 拍板「都放進去」）──
    dict(slug="ancient-sanskrit-literature", eid="4444444e-4444-4444-8444-444444444444",
         title="古代梵文文學史", title_en="A History of Ancient Sanskrit Literature", year=1859,
         category="宗教學", subcategory="宗教學", parent="印度學",
         en_id="historyofancient00mluoft", de_id=None, split="coarse"),
    dict(slug="auld-lang-syne", eid="4444444f-4444-4444-8444-444444444444",
         title="往日時光（憶往）", title_en="Auld Lang Syne", year=1898,
         category="宗教學", subcategory="宗教學", parent="文集與回憶",
         en_id="auldlangsyne00mluoft", de_id=None, split="coarse"),
    dict(slug="my-autobiography", eid="44444450-4444-4444-8444-444444444444",
         title="自傳片段", title_en="My Autobiography: A Fragment", year=1901,
         category="宗教學", subcategory="宗教學", parent="文集與回憶",
         en_id="myautobiographyf00mluoft", de_id=None, split="coarse"),
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


def ingest_work(work: dict) -> int:
    """English-first ingest (NO LLM): download + split + write per-section caches
    (en filled, zh=None where missing) + upload. The book becomes readable in
    English immediately; translation fills 繁中 later. Returns section count."""
    txt = fetch_djvu(work["en_id"])
    sections = build_sections(txt.read_text(encoding="utf-8", errors="replace").splitlines(),
                              work["split"])
    work_dir(work["slug"]).mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(sections):
        cp = sec_path(work["slug"], i)
        if cp.exists():
            continue  # keep any existing translations
        cp.write_text(json.dumps({"title": s["title"], "en": s["paras"],
                                  "zh": [None] * len(s["paras"])}, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    assemble_and_upload(work)
    return len(sections)


# A segment that comes back empty this many translate passes is treated as
# unfillable (OCR running-head / printed marginalia / junk the engine refuses)
# and permanently skipped — the reader falls back to its English row. Without
# this, ~1 dead segment per section keeps a near-complete book under 100% so
# is_done() never fires, the queue re-sweeps it forever, and the remaining
# books are starved. translate_para already retries ×4 internally, so MAX_FAIL
# passes ≈ MAX_FAIL×4 real attempts before a segment is declared dead.
MAX_FAIL = 3


def translate_work(work: dict, translate_para, *, reupload_every: int = 12) -> int:
    """Fill 繁中 for one already-ingested work, resumably, reading the per-section
    caches ingest_work wrote. Re-uploads every `reupload_every` sections so the
    reader shows Chinese landing incrementally (English stays as fallback).
    Segments that fail MAX_FAIL passes are marked exhausted and skipped."""
    done = 0
    i = 0
    while sec_path(work["slug"], i).exists():
        cp = sec_path(work["slug"], i)
        s = json.loads(cp.read_text(encoding="utf-8"))
        en = s["en"]
        zh = (s.get("zh") or [None] * len(en))[:len(en)] + [None] * (len(en) - len(s.get("zh") or []))
        fail = (s.get("fail") or [0] * len(en))[:len(en)] + [0] * (len(en) - len(s.get("fail") or []))
        # skip already-translated AND exhausted (dead) segments
        todo = [j for j in range(len(en)) if not (zh[j] or "").strip() and fail[j] < MAX_FAIL]
        if todo:
            print(f"    {work['slug']} sec{i}「{s['title'][:36]}」 ¶={len(en)} todo={len(todo)}", flush=True)
        for k, j in enumerate(todo, 1):
            r = translate_para(en[j], "")
            if (r or "").strip():
                zh[j] = r
                fail[j] = 0
            else:
                fail[j] += 1  # count toward MAX_FAIL so we stop re-attempting dead segments
            if k % 3 == 0 or k == len(todo):
                s["zh"] = zh
                s["fail"] = fail
                cp.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
                if LOCK.exists():
                    LOCK.touch()
        s["zh"] = zh
        s["fail"] = fail
        cp.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
        done += sum(1 for z in zh if z)
        i += 1
        if reupload_every and i % reupload_every == 0:
            assemble_and_upload(work)
    return done


def cover_chunk(work: dict) -> dict:
    c = build_multilang_chunk(chunk_index=0, chapter_path="封面", content_zh="## 封面",
                              sources={}, source_order=[], volume=work["title"],
                              parent_volume=work["parent"], chunk_type="cover", page_number=1)
    validate_multilang_chunk(c)
    return c


def section_chunk(work: dict, sec: dict, ci: int) -> dict:
    # English-first: the main (繁中) column falls back to the English paragraph
    # until its translation lands, so an ingested-but-untranslated book is still
    # fully readable (in English) and progressively becomes Chinese.
    zh_src = (sec.get("zh") or []) + [None] * len(sec["en"])
    zh_rows = [f"## {sec['title']}"] + [(z or en) for z, en in zip(zh_src, sec["en"])]
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
        if sec.get("en"):  # English-first: include any section with source text (zh may be empty → falls back to EN)
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
    # author defaults to Müller (his own works) but is overridable so the same
    # pipeline can ingest the Sacred Books of the East volumes, each translated
    # by a different scholar (Legge, Bühler, …).
    row = {"id": work["eid"], "title": work["title"],
           "author": work.get("author", "弗里德里希‧馬克斯‧穆勒"),
           "author_en": work.get("author_en", "Friedrich Max Müller"),
           "original_title": work["title_en"],
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
    rows = [{"ebook_id": eid, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
             "page_number": c["page_number"], "chapter_path": c["chapter_path"],
             "content": c["content"][:200], "char_count": len(c["content"])} for c in chunks]
    sync_previews(eid, rows)


def sync_previews(eid: str, rows: list[dict]):
    """Replace ebook_chunks preview rows for one book, durably. The reader reads
    full text from R2/JSONL, but the library search/preview uses this table, so a
    half-finished insert (Drive/network blip) leaves stale previews. Delete then
    insert with per-batch retry, and verify the final count matches — without
    this, a flaky POST silently truncated previews on every re-upload."""
    import requests
    te = _te()
    # ebook_chunks.chunk_type has a CHECK constraint (page/chapter/section). The
    # cover chunk is 'cover' in the JSONL/R2 (reader uses it), but that value is
    # rejected by the table, so a cover in batch 0 used to fail the whole batch
    # (silently dropping ~25 previews per book). Coerce to an allowed type for
    # the preview table only; the R2 copy the reader reads keeps 'cover'.
    allowed = {"page", "chapter", "section"}
    for r in rows:
        if r.get("chunk_type") not in allowed:
            r["chunk_type"] = "page"
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}", headers=te.H_GET, timeout=30)
    for i in range(0, len(rows), 25):
        batch = rows[i:i + 25]
        for attempt in range(4):
            try:
                r = requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=batch, timeout=60)
                if r.status_code < 300:
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(2 * (attempt + 1))
        else:
            print(f"  ⚠ preview batch {i} failed after retries (eid {eid})", flush=True)
    # Verify — re-post any gap so the table count matches the JSONL length.
    got = requests.get(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{eid}&select=chunk_index",
                       headers={**te.H_GET, "Prefer": "count=exact", "Range": "0-0"}, timeout=30)
    have = int(got.headers.get("content-range", "*/0").split("/")[-1] or 0)
    if have != len(rows):
        print(f"  ⚠ preview count {have}≠{len(rows)} for {eid} (will self-heal next upload)", flush=True)


def is_done(work: dict) -> bool:
    """A work is done when every source segment is either translated or exhausted
    (failed MAX_FAIL passes → unfillable junk, left as an English fallback row).
    Without the exhausted clause, ~1 dead segment per section would keep a book
    forever incomplete and the queue would never advance past it."""
    wd = work_dir(work["slug"])
    secs = sorted(wd.glob("sec*.json")) if wd.exists() else []
    if not secs:
        return False
    for p in secs:
        s = json.loads(p.read_text(encoding="utf-8"))
        en = s.get("en") or []
        zh = s.get("zh") or []
        fail = s.get("fail") or []
        for j in range(len(en)):
            z = zh[j] if j < len(zh) else None
            f = fail[j] if j < len(fail) else 0
            if not (z or "").strip() and f < MAX_FAIL:
                return False
    return True


# ── lock ─────────────────────────────────────────────────────────────────────
LOCK_STALE_SECS = 25 * 60  # a live run touches the lock every ~3 paragraphs; older = dead/hung


def acquire_lock() -> bool:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        age = time.time() - LOCK.stat().st_mtime
        if age < LOCK_STALE_SECS:  # a fresh lock means another run is active
            print(f"  another queue run holds the lock ({age/60:.0f} min old) — exiting", flush=True)
            return False
        print(f"  stale lock ({age/60:.0f} min old, holder likely dead) — taking over", flush=True)
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
        w = by_slug[args.work]
        ingest_work(w)  # English-first
        tp = mb.make_engine()
        translate_work(w, tp)
        if args.upload:
            assemble_and_upload(w)
        return

    if args.run_queue:
        if not acquire_lock():
            return
        try:
            # Phase 1: English-first ingest — every book readable fast, no LLM.
            for w in WORKS:
                try:
                    print(f"⤓ ingest {w['slug']} — {w['title']}", flush=True)
                    ingest_work(w)
                except Exception as e:  # noqa: BLE001
                    print(f"  ✗ ingest {w['slug']} failed: {type(e).__name__}: {e}", flush=True)
            # Phase 2: translate gradually; English stays as the fallback column.
            tp = mb.make_engine()
            for w in WORKS:
                if is_done(w):
                    print(f"  ✓ {w['slug']} translated — skip", flush=True)
                    continue
                print(f"▶ translate {w['slug']} — {w['title']}", flush=True)
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
