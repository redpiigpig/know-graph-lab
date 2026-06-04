"""Build Max Müller's collected-works volumes into trilingual reader books.

English-primary (Müller wrote in English at Oxford; the German edition is his
supervised parallel translation). Per volume:

  raw EN djvu txt ─┐
                   ├─ slice 6 sections (4 lectures + 2 essays, by line ranges)
  raw DE djvu txt ─┘   → reflow OCR (drop running heads/page-nos, fix hyphenation,
                          merge header-split paragraphs)
                       → order-align DE paragraphs onto EN paragraphs (equal count)
                       → translate EN¶ → 繁中 (NVIDIA deepseek, Müller glossary)
                       → one chunk per section: content(zh)/sources.en/sources.de
                          all the SAME ¶ count so the reader rows line up
                       → JSONL + R2 + DB

Resumable: each section's {en,de,zh} rows cache to mueller_data/<vol>/secN.json;
a rerun only translates paragraphs whose zh is still missing.

Engine: no Gemini key in this env → NVIDIA-first chain (te.nvidia_with_gemini_fallback
= NVIDIA deepseek 4-key round-robin → Gemini → Haiku 救急). See
.claude/skills/ebook-collected-works/mueller_collected_works.md.

  python scripts/mueller_build.py --dry            # clean+align counts only, no LLM
  python scripts/mueller_build.py --probe          # one-paragraph engine smoke
  python scripts/mueller_build.py --only 0 --upload # just section 0 (Lecture I)
  python scripts/mueller_build.py --upload          # whole book, resumable
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Load .env into os.environ before importing the engine module (it reads keys at import).
_ENV_PATH = SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    for _l in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

from multilang_chunks import build_multilang_chunk, validate_multilang_chunk, write_jsonl  # noqa: E402

# ── Volume config: 《宗教學導論》Introduction to the Science of Religion (1873) ──
# Section line ranges in the archive.org djvu txts (start..end, 1-based, end exclusive).
EBOOK_ID = "33333333-3333-4333-8333-333333333333"
VOLUME = "宗教學導論（馬克斯‧穆勒）"
PARENT_VOLUME = "宗教學導論"
EN_TXT = Path("c:/tmp/mueller_isr_en_1873.txt")
DE_TXT = Path("c:/tmp/mueller_einleitung_de_1874.txt")
DATA_DIR = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works" / "mueller_data" / "isr"

SECTIONS = [
    # (繁中標題, en_head, EN start, EN end, de_head, DE start, DE end)
    ("第一講", "FIRST LECTURE", 192, 3719, "ERSTE VORLESUNG", 379, 4125),
    ("第二講", "SECOND LECTURE", 3719, 5312, "ZWEITE VORLESUNG", 4125, 5899),
    ("第三講", "THIRD LECTURE", 5312, 7699, "DRITTE VORLESUNG", 5899, 8528),
    ("第四講", "FOURTH LECTURE", 7699, 9849, "VIERTE VORLESUNG", 8528, 11274),
    ("論比較神學中的假類比", "ON FALSE ANALOGIES IN COMPARATIVE THEOLOGY", 9849, 11708,
     "ÜBER FALSCHE ANALOGIEN IN DER VERGLEICHENDEN THEOLOGIE", 11274, 13178),
    ("論神話的哲學", "ON THE PHILOSOPHY OF MYTHOLOGY", 11710, 13964,
     "ÜBER DIE PHILOSOPHIE DER MYTHOLOGIE", 13178, 15270),
]

# ── OCR reflow ──────────────────────────────────────────────────────────────
# Running headers on (almost) every page; OCR garbles them, so match fuzzily.
_EN_HEADER_RE = re.compile(r"(lect[uir]+es?\s+on\s+the\s+s[ce]i?ence\s+of\s+relig|"
                           r"introduction\s+to\s+the\s+s[ce]i?ence\s+of\s+relig)", re.I)
_DE_HEADER_RE = re.compile(r"vorles[uia]nge?n?\s+[aü]b?er\s+[rh]eli?gi", re.I)
_PAGENUM_RE = re.compile(r"^[^A-Za-zÄÖÜäöüß]*\d{1,4}[^A-Za-zÄÖÜäöüß]*$")
_FOOTNOTE_RE = re.compile(r"^\s*[*]\s*\)?")  # *) footnote lines (bibliographic apparatus)
_TERMINAL = ('.', '!', '?', ':', ';', '»', '"', "'", '’', '”', ')', '—')


def reflow(lines: list[str], header_re: re.Pattern) -> list[str]:
    """OCR lines → clean paragraphs. Drops running heads / page numbers / footnote
    lines / tiny junk; reflows hard-wrapped lines into paragraphs (blank line =
    break), fixes end-of-line hyphenation; then merges paragraphs that don't end
    in terminal punctuation (heals header-induced mid-paragraph splits)."""
    kept: list[str] = []
    for ln in lines:
        s = ln.strip()
        if not s:
            kept.append("")
            continue
        if header_re.search(s) or _PAGENUM_RE.match(s) or _FOOTNOTE_RE.match(s):
            continue
        if len(s) <= 2 and not (s[0].isalpha() and s[0].isupper()):
            continue  # OCR specks: lone 'o', 'j', '^', digits
        kept.append(s)

    paras: list[list[str]] = []
    cur: list[str] = []
    for s in kept:
        if s == "":
            if cur:
                paras.append(cur)
                cur = []
        else:
            cur.append(s)
    if cur:
        paras.append(cur)

    joined: list[str] = []
    for p in paras:
        buf = ""
        for ln in p:
            if buf.endswith("-"):
                buf = buf[:-1] + ln.lstrip()
            elif buf:
                buf += " " + ln
            else:
                buf = ln
        buf = re.sub(r"\s{2,}", " ", buf).strip()
        if buf:
            joined.append(buf)

    merged: list[str] = []
    for p in joined:
        if merged and not merged[-1].rstrip().endswith(_TERMINAL):
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    # drop a leading all-caps sub-heading paragraph (DELIVERED AT THE ROYAL INSTITUTION…)
    out = [p for p in merged if p and not (p.isupper() and len(p) < 90)]
    return out


def slice_lines(path: Path, start: int, end: int) -> list[str]:
    all_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return all_lines[start - 1:end - 1]


def align_de_to_en(en_paras: list[str], de_paras: list[str]) -> list[str]:
    """Return a DE list the SAME length as en_paras. Equal counts → 1:1; otherwise
    map each DE paragraph onto an EN slot by its positional (char-midpoint) fraction,
    joining multiple DE paras that land in one slot, padding empty slots with ''."""
    n = len(en_paras)
    if n == 0:
        return []
    if not de_paras:
        return [""] * n
    if len(de_paras) == n:
        return list(de_paras)
    total = sum(len(p) for p in de_paras) or 1
    slots: list[list[str]] = [[] for _ in range(n)]
    cum = 0
    for p in de_paras:
        frac = (cum + len(p) / 2) / total
        slots[min(n - 1, int(frac * n))].append(p)
        cum += len(p)
    return ["\n".join(s) for s in slots]


# ── translation ─────────────────────────────────────────────────────────────
MUELLER_PROMPT_TMPL = """你是宗教學經典的專業譯者，正在翻譯弗里德里希‧馬克斯‧穆勒（Friedrich Max Müller）1873 年《宗教學導論》。把下列**英文原文**翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；台灣用語；中間點用「‧」。
2. 只翻譯英文原文；附上的德文僅供消歧義參考，**不要翻譯德文**。
3. 忠實學術散文語氣，長句可順為通順中文；保留括號內的外文夾注（梵文/希臘文/拉丁文）。
4. 保留 Markdown（## 標題 / **粗體** / *斜體* / > 引文）。
5. 術語對齊：the science of religion→宗教學、comparative theology→比較神學、
   comparative mythology→比較神話學、the science of language→語言科學、
   henotheism→單一神教（henotheism）、kathenotheism→輪換主神教、
   monotheism→一神教、polytheism→多神教、"a disease of language"→「語言的疾病」、
   the Infinite→無限者、Aryan→雅利安、Semitic→閃語族、Turanian→圖蘭語族、
   Veda→吠陀、Rig-Veda→梨俱吠陀、Upanishad→奧義書、Dyaus→特尤斯、Deva→提婆。
   人名 Müller→穆勒（非「米勒」）。
6. 只輸出翻譯後的繁體中文，不要前言、說明或英文。

英文原文：
{source}"""


def make_engine():
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = MUELLER_PROMPT_TMPL
    if not getattr(te, "NVIDIA_KEYS", None):
        raise RuntimeError("no NVIDIA keys loaded — check .env (NVIDIA_API_Key_1..4)")

    def translate_para(en: str, de: str = "") -> str:
        src = en.strip()
        if not src:
            return ""
        if de.strip():
            src = f"{src}\n\n[德文參考 — 不要翻譯，僅供消歧義]\n{de.strip()}"
        pieces = te.split_oversized(src)
        out = " ".join(te.nvidia_with_gemini_fallback(p) for p in pieces)
        # Each EN paragraph → exactly ONE zh paragraph: drop any model-added
        # markdown heading lines and collapse internal newlines so the reader's
        # \n\n paragraph-split keeps zh/en/de row counts equal.
        out = re.sub(r"(?m)^\s*#{1,6}\s.*$", "", out)
        out = re.sub(r"\s*\n\s*", " ", out).strip()
        return out

    return translate_para


# ── per-section build (resumable) ────────────────────────────────────────────
def section_cache_path(idx: int) -> Path:
    return DATA_DIR / f"sec{idx}.json"


def prepare_section(idx: int) -> dict:
    """Slice + reflow + align one section. Loads existing zh from cache if present."""
    title_zh, en_head, en_s, en_e, de_head, de_s, de_e = SECTIONS[idx]
    en_paras = reflow(slice_lines(EN_TXT, en_s, en_e), _EN_HEADER_RE)
    de_paras = reflow(slice_lines(DE_TXT, de_s, de_e), _DE_HEADER_RE)
    de_aligned = align_de_to_en(en_paras, de_paras)
    cache = {}
    if section_cache_path(idx).exists():
        cache = json.loads(section_cache_path(idx).read_text(encoding="utf-8"))
    prev_zh = cache.get("zh", [])
    sec = {
        "idx": idx, "title_zh": title_zh, "en_head": en_head, "de_head": de_head,
        "en": en_paras, "de": de_aligned,
        "zh": (prev_zh + [None] * len(en_paras))[:len(en_paras)],
        "de_raw_count": len(de_paras),
    }
    return sec


def translate_section(sec: dict, translate_para, *, save_every: int = 3, maxparas=None) -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    n = len(sec["en"])
    todo = [i for i in range(n) if not sec["zh"][i]]
    if maxparas:
        todo = todo[:maxparas]
    print(f"  sec{sec['idx']} 「{sec['title_zh']}」 EN¶={n} DE¶={sec['de_raw_count']}→{n} "
          f"todo={len(todo)}", flush=True)
    for done, i in enumerate(todo, 1):
        sec["zh"][i] = translate_para(sec["en"][i], sec["de"][i])
        if done % save_every == 0 or done == len(todo):
            section_cache_path(sec["idx"]).write_text(
                json.dumps(sec, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"    {done}/{len(todo)} translated, cached", flush=True)
    return sec


def make_cover_chunk() -> dict:
    """Chunk 0 = cover. The reader forces page 1 to render as a metadata title
    page (isCoverPage = currentPage===1) and SUPPRESSES chunk content there, so
    real content must start at chunk 1 / page 2."""
    chunk = build_multilang_chunk(
        chunk_index=0,
        chapter_path="封面",
        content_zh="## 封面",
        sources={},
        source_order=[],
        volume=VOLUME,
        parent_volume=PARENT_VOLUME,
        chunk_type="cover",
        page_number=1,
    )
    validate_multilang_chunk(chunk)
    return chunk


def section_to_chunk(sec: dict, chunk_index: int) -> dict:
    """One section → one reader chunk. Row 0 = heading; equal ¶ counts across cols."""
    zh_rows = [f"## {sec['title_zh']}"] + [z or "" for z in sec["zh"]]
    en_rows = [f"## {sec['en_head']}"] + sec["en"]
    de_rows = [f"## {sec['de_head']}"] + sec["de"]
    assert len(zh_rows) == len(en_rows) == len(de_rows), \
        f"sec{sec['idx']} row mismatch zh={len(zh_rows)} en={len(en_rows)} de={len(de_rows)}"
    chunk = build_multilang_chunk(
        chunk_index=chunk_index,
        chapter_path=f"{PARENT_VOLUME} · {sec['title_zh']}",
        content_zh="\n\n".join(zh_rows),
        sources={"en": "\n\n".join(en_rows), "de": "\n\n".join(de_rows)},
        source_order=["en", "de"],
        volume=VOLUME,
        parent_volume=PARENT_VOLUME,
        page_number=chunk_index + 1,
        title_en=sec["en_head"],
    )
    validate_multilang_chunk(chunk)
    return chunk


def ensure_ebook_row():
    import translate_ebook_to_zh as te
    import requests
    row = {
        "id": EBOOK_ID,
        "title": "宗教學導論",
        "subtitle": "皇家研究院四講，附二論（英／德／繁中三欄對照）",
        "author": "弗里德里希‧馬克斯‧穆勒",
        "author_en": "Friedrich Max Müller",
        "original_title": "Introduction to the Science of Religion",
        "original_publish_year": 1873,
        "file_type": "epub",
        "category": "宗教學",
        "subcategory": "宗教學",
    }
    r = requests.post(f"{te.URL}/rest/v1/ebooks?on_conflict=id",
                      headers={**te.H_JSON, "Prefer": "resolution=merge-duplicates"},
                      json=row, timeout=30)
    print(f"  ebooks row upsert HTTP {r.status_code}", flush=True)


def upload(chunks: list[dict], out_path: Path):
    import datetime
    import requests
    import translate_ebook_to_zh as te
    try:
        te.se.push_to_r2(EBOOK_ID, out_path)
        print("  ✓ pushed R2", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ R2 push failed: {e}", flush=True)
    total_chars = sum(len(c["content"]) for c in chunks)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    patch = {"chunk_count": len(chunks), "total_chars": total_chars,
             "total_pages": len(chunks), "parsed_at": now, "standardized_at": now}
    requests.patch(f"{te.URL}/rest/v1/ebooks?id=eq.{EBOOK_ID}", headers=te.H_JSON,
                   json=patch, timeout=30).raise_for_status()
    requests.delete(f"{te.URL}/rest/v1/ebook_chunks?ebook_id=eq.{EBOOK_ID}", headers=te.H_GET, timeout=30)
    rows = [{"ebook_id": EBOOK_ID, "chunk_index": c["chunk_index"], "chunk_type": c["chunk_type"],
             "page_number": c["page_number"], "chapter_path": c["chapter_path"],
             "content": c["content"][:200], "char_count": len(c["content"])} for c in chunks]
    for i in range(0, len(rows), 25):
        requests.post(f"{te.URL}/rest/v1/ebook_chunks", headers=te.H_JSON, json=rows[i:i + 25], timeout=60)
    print(f"  ✓ ebooks row + previews updated  chunk_count={len(chunks)}", flush=True)


def out_jsonl_path() -> Path:
    base = os.environ.get("EBOOK_CHUNKS_DIR")
    if not base:
        raise RuntimeError("EBOOK_CHUNKS_DIR not set")
    return Path(base) / f"{EBOOK_ID}.jsonl"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="clean+align counts only, no LLM")
    ap.add_argument("--probe", action="store_true", help="translate one paragraph, print, exit")
    ap.add_argument("--only", type=int, default=None, help="build just one section index (0..5)")
    ap.add_argument("--maxparas", type=int, default=None, help="cap paragraphs translated per section (smoke)")
    ap.add_argument("--build-only", action="store_true", help="skip translation; assemble JSONL from cache")
    ap.add_argument("--upload", action="store_true", help="push R2 + DB after building")
    args = ap.parse_args()

    idxs = [args.only] if args.only is not None else list(range(len(SECTIONS)))

    if args.dry:
        for i in idxs:
            sec = prepare_section(i)
            print(f"sec{i} 「{sec['title_zh']}」 EN¶={len(sec['en'])} "
                  f"DE¶raw={sec['de_raw_count']}→aligned={len(sec['de'])} "
                  f"| EN[0]: {sec['en'][0][:70] if sec['en'] else '—'}")
        return

    if args.probe:
        tp = make_engine()
        sec = prepare_section(0)
        print("EN:", sec["en"][0][:120])
        print("ZH:", tp(sec["en"][0], sec["de"][0]))
        return

    ensure_ebook_row()
    # build/translate selected sections; assemble ALL cached sections into the JSONL
    if not args.build_only:
        tp = make_engine()
        for i in idxs:
            sec = prepare_section(i)
            translate_section(sec, tp, maxparas=args.maxparas)

    chunks = [make_cover_chunk()]
    ci = 1  # content starts at chunk 1 / page 2 (page 1 is the cover)
    for i in range(len(SECTIONS)):
        cp = section_cache_path(i)
        if not cp.exists():
            continue
        sec = json.loads(cp.read_text(encoding="utf-8"))
        if not any(sec.get("zh") or []):
            continue
        chunks.append(section_to_chunk(sec, ci))
        ci += 1
    out = out_jsonl_path()
    write_jsonl(chunks, out)
    print(f"Wrote {out} ({len(chunks)} chunks)", flush=True)
    if args.upload:
        upload(chunks, out)


if __name__ == "__main__":
    main()
