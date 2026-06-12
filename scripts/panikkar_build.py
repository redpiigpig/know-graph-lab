"""Build Raimon Panikkar's collected-works volumes into reader books.

Panikkar (1918–2010) is FULLY in copyright (life+70 ≈ 2080) → English-first:
no clean public-domain full text exists (unlike Müller's archive.org djvu);
source text comes from private sites / user-supplied files. The reader only
ever shows MY 繁中 translation + a source-language column; no third-party
Chinese translation is ingested. See
.claude/skills/ebook-collected-works/panikkar_collected_works.md.

Pilot = 《The Unknown Christ of Hinduism》(1964, rev. 1981), originally English
→ bilingual (en + 繁中). 升三欄 (en + es + 繁中) later if the parallel Spanish
《El Cristo desconocido del hinduismo》is obtained.

Per chapter:
  raw EN text ─→ reflow (drop running heads / page-nos, fix hyphenation,
                  heal header-split paragraphs)
              ─→ split into chapter sections (heading anchors)
              ─→ translate EN¶ → 繁中 (engine chain, Panikkar glossary)
              ─→ one chunk per section: content(zh)/sources.en[/.es]
                 all the SAME ¶ count so the reader rows line up
              ─→ JSONL + R2 + DB

The PURE helpers below (reflow / split_sections / align_secondary /
build_section_chunk / make_cover_chunk / assemble_pilot) carry no network/LLM/DB
and are locked by scripts/tests/test_panikkar_build.py. Engine + upload reuse
the ebook-translate / mueller_build infrastructure.

  python scripts/panikkar_build.py --dry  --src c:/tmp/uch_en.txt   # split counts only
  python scripts/panikkar_build.py --probe --src c:/tmp/uch_en.txt  # one-paragraph smoke
  python scripts/panikkar_build.py --src c:/tmp/uch_en.txt --limit 1 --upload  # one section
  python scripts/panikkar_build.py --src c:/tmp/uch_en.txt --upload            # whole book
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

# ── Pilot config: 《The Unknown Christ of Hinduism》(1964, rev. 1981) ──
EBOOK_ID = "55555555-5555-4555-8555-555555555555"
VOLUME = "印度教中未識的基督（雷蒙‧潘尼卡）"
PARENT_VOLUME = "印度教與基督宗教"
SOURCE_ORDER = ["en"]  # bilingual; 升三欄 → ["en", "es"]
DATA_DIR = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works" / "panikkar_data" / "uch"

# ── OCR / text reflow ────────────────────────────────────────────────────────
_PAGENUM_RE = re.compile(r"^[^A-Za-zÀ-ÿ]*\d{1,4}[^A-Za-zÀ-ÿ]*$")
_FOOTNOTE_RE = re.compile(r"^\s*[*]\s*\)?")
_TERMINAL = ('.', '!', '?', ':', ';', '»', '"', "'", '’', '”', ')', '—')


def reflow(lines: list[str], header_re: re.Pattern | None = None) -> list[str]:
    """OCR lines → clean paragraphs. Drops running heads (optional fuzzy regex) /
    page numbers / footnote markers / tiny specks; reflows hard-wrapped lines into
    paragraphs (blank line = break), fixes end-of-line hyphenation; then merges
    paragraphs that don't end in terminal punctuation (heals running-head splits).
    Mirrors mueller_build.reflow so the two books behave identically."""
    kept: list[str] = []
    for ln in lines:
        s = ln.strip()
        if not s:
            kept.append("")
            continue
        if (header_re and header_re.search(s)) or _PAGENUM_RE.match(s) or _FOOTNOTE_RE.match(s):
            continue
        if len(s) <= 2 and not (s[0].isalpha() and s[0].isupper()):
            continue  # OCR specks: lone 'o', 'j', '^', stray digits
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
    return merged


# ── section splitting ────────────────────────────────────────────────────────
# A heading: a SHORT line (<70 chars) that looks like a chapter/part marker.
_HEADING_RE = re.compile(
    r"^(#{1,6}\s+.+"                                  # markdown heading
    r"|(?:PART|CHAPTER|LECTURE|SECTION)\b.*"          # CHAPTER 1 / PART II …
    r"|INTRODUCTION|PREFACE|FOREWORD|CONCLUSION|EPILOGUE|PROLOGUE"
    r"|[IVXLC]+\.\s+.+"                               # "IV. The whole Christ"
    r"|\d{1,3}\.\s+\S.*)$", re.I)


def _is_heading(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 69:
        return False
    return bool(_HEADING_RE.match(s))


def split_sections(text: str) -> list[dict]:
    """Split source text into [{heading, paras:[...]}] on chapter-heading anchors.
    Front matter before the first heading is kept as a '(front)' section. Long
    lines that merely mention 'Chapter 1' never split (length guard)."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    sections: list[dict] = []
    cur: dict | None = None
    for b in blocks:
        if _is_heading(b):
            cur = {"heading": b, "paras": []}
            sections.append(cur)
        else:
            if cur is None:
                cur = {"heading": "(front)", "paras": []}
                sections.append(cur)
            cur["paras"].append(b)
    return sections


def align_secondary(primary: list[str], secondary: list[str]) -> list[str]:
    """Return a secondary list the SAME length as `primary`. Equal counts → 1:1;
    empty → all ''; otherwise map each secondary paragraph onto a primary slot by
    its positional char-midpoint fraction (joining collisions, padding gaps) so
    every reader row lines up. Mirror of mueller_build.align_de_to_en."""
    n = len(primary)
    if n == 0:
        return []
    if not secondary:
        return [""] * n
    if len(secondary) == n:
        return list(secondary)
    total = sum(len(p) for p in secondary) or 1
    slots: list[list[str]] = [[] for _ in range(n)]
    cum = 0
    for p in secondary:
        frac = (cum + len(p) / 2) / total
        slots[min(n - 1, int(frac * n))].append(p)
        cum += len(p)
    return ["\n".join(s) for s in slots]


# ── chunk assembly ───────────────────────────────────────────────────────────
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


def build_section_chunk(
    *,
    chunk_index: int,
    title_zh: str,
    zh_paras: list[str],
    source_paras: dict,
    source_heads: dict,
    source_order: list = SOURCE_ORDER,
    volume: str = VOLUME,
    parent_volume: str = PARENT_VOLUME,
    page_number: int | None = None,
) -> dict:
    """One section → one reader chunk. Row 0 = heading; every column has the SAME
    ¶ count (zh is 1:1 with the primary source; other sources are aligned+padded)
    so the reader's \\n\\n split keeps rows in lock-step."""
    zh_rows = [f"## {title_zh}"] + [z or "" for z in zh_paras]
    primary = source_order[0]
    n_body = len(zh_paras)
    sources: dict = {}
    for lang in source_order:
        paras = source_paras.get(lang, [])
        if lang != primary:
            paras = align_secondary(zh_paras, paras)
        else:
            # primary must match zh length 1:1; pad/trim defensively
            paras = (list(paras) + [""] * n_body)[:n_body]
        head = source_heads.get(lang, "")
        rows = [f"## {head}"] + paras
        assert len(rows) == len(zh_rows), \
            f"chunk {chunk_index} lang {lang}: rows {len(rows)} != zh {len(zh_rows)}"
        sources[lang] = "\n\n".join(rows)
    chunk = build_multilang_chunk(
        chunk_index=chunk_index,
        chapter_path=f"{PARENT_VOLUME} · {title_zh}",
        content_zh="\n\n".join(zh_rows),
        sources=sources,
        source_order=source_order,
        volume=volume,
        parent_volume=parent_volume,
        page_number=page_number if page_number is not None else chunk_index + 1,
        title_en=source_heads.get(primary),
    )
    validate_multilang_chunk(chunk)
    return chunk


def assemble_pilot(sections: list[dict], translate_para, *, source_order: list = SOURCE_ORDER) -> list[dict]:
    """sections: [{title_zh, heads:{lang:str}, sources:{lang:[paras]}}]. Translate
    each primary-source paragraph → 繁中, build cover + one chunk per section
    (indices 0..N). `translate_para(str)->str` is the engine boundary (LLM in
    prod, stub in tests)."""
    primary = source_order[0]
    chunks = [make_cover_chunk()]
    for i, sec in enumerate(sections, start=1):
        src = sec["sources"]
        zh_paras = [translate_para(p) for p in src[primary]]
        chunks.append(build_section_chunk(
            chunk_index=i,
            title_zh=sec["title_zh"],
            zh_paras=zh_paras,
            source_paras=src,
            source_heads=sec["heads"],
            source_order=source_order,
            page_number=i + 1,
        ))
    return chunks


# ── translation engine (prod only) ───────────────────────────────────────────
PANIKKAR_PROMPT_TMPL = """你是比較神學與宗教哲學經典的專業譯者，正在翻譯雷蒙‧潘尼卡（Raimon Panikkar）的著作《印度教中未識的基督》。把下列**英文原文**翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；台灣天主教用語；中間點用「‧」。
2. 只翻譯英文原文；不要加前言或說明。
3. 忠實學術／神學散文語氣，長句可順為通順中文；保留括號內的外文夾注（梵文/拉丁文/希臘文，如 Brahman、advaita、Logos、plērōma）。
4. 保留 Markdown（## 標題 / **粗體** / *斜體* / > 引文）。
5. 潘尼卡自鑄詞鎖死（首見括注原詞）：cosmotheandric→宇宙神人共融、intrareligious dialogue→宗教內對話、interreligious dialogue→宗教間對話、Christophany→基督顯現、the whole Christ→全基督、the Unknown Christ→未識的基督、pluralism→多元論、advaita→不二、tempiternity→時永。聖神（非聖靈）。
   印度術語對齊：Brahman→梵、ātman→阿特曼、dharma→達磨/法、karma→業、Veda→吠陀、Upaniṣad→奧義書。
   人名 Panikkar→潘尼卡（非帕尼卡）。
6. 只輸出翻譯後的繁體中文。

英文原文：
{source}"""


def make_engine():
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = PANIKKAR_PROMPT_TMPL

    def _clean(out: str) -> str:
        # Each EN paragraph → exactly ONE zh paragraph: drop model-added heading
        # lines and collapse internal newlines so the reader's \n\n split keeps
        # zh/en row counts equal.
        out = re.sub(r"(?m)^\s*#{1,6}\s.*$", "", out)
        return re.sub(r"\s*\n\s*", " ", out).strip()

    def translate_para(en: str) -> str:
        src = (en or "").strip()
        if not src:
            return ""
        pieces = te.split_oversized(src)
        out = ""
        for _ in range(4):  # retry-on-empty (engine occasionally returns blank under load)
            out = _clean(" ".join(te.nvidia_with_gemini_fallback(p) for p in pieces))
            if out:
                return out
        return out

    return translate_para


def ensure_ebook_row():
    import requests
    import translate_ebook_to_zh as te
    row = {
        "id": EBOOK_ID,
        "title": "印度教中未識的基督",
        "subtitle": "基督宗教與印度教的交會（英／繁中對照‧自譯本）",
        "author": "雷蒙‧潘尼卡",
        "author_en": "Raimon Panikkar",
        "original_title": "The Unknown Christ of Hinduism",
        "original_publish_year": 1981,
        "file_type": "epub",
        "category": "世界宗教",
        "subcategory": "基督教",
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


# ── section cache (resumable) ────────────────────────────────────────────────
def _cache_path(idx: int) -> Path:
    return DATA_DIR / f"sec{idx}.json"


def load_sections_from_src(src_path: Path) -> list[dict]:
    """Read a plain-text English source → split into sections on heading anchors
    FIRST, then reflow each section's body (de-wrap / de-hyphenate / heal
    running-head splits). Splitting before reflow is essential: reflow merges
    paragraphs that don't end in terminal punctuation, which would otherwise
    swallow the (punctuation-free) chapter headings into the preceding body."""
    text = src_path.read_text(encoding="utf-8", errors="replace")
    out: list[dict] = []
    for s in split_sections(text):
        body_lines: list[str] = []
        for p in s["paras"]:
            body_lines.extend(p.splitlines())
            body_lines.append("")  # keep paragraph boundaries for reflow
        paras = reflow(body_lines)
        if s["heading"] == "(front)" and not paras:
            continue
        out.append({"title_zh": s["heading"], "heads": {"en": s["heading"]},
                    "sources": {"en": paras}})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=str, help="English source text file")
    ap.add_argument("--dry", action="store_true", help="split + counts only, no LLM")
    ap.add_argument("--probe", action="store_true", help="translate one paragraph, print, exit")
    ap.add_argument("--limit", type=int, default=None, help="only first N sections")
    ap.add_argument("--upload", action="store_true", help="push R2 + DB after building")
    args = ap.parse_args()

    if not args.src:
        ap.error("--src required (English source text)")
    sections = load_sections_from_src(Path(args.src))
    if args.limit:
        sections = sections[:args.limit]

    if args.dry:
        for i, s in enumerate(sections):
            head = s["heads"]["en"]
            n = len(s["sources"]["en"])
            first = s["sources"]["en"][0][:70] if n else "—"
            print(f"sec{i} 「{head[:40]}」 EN¶={n} | {first}")
        return

    tp = make_engine()
    if args.probe:
        for s in sections:
            if s["sources"]["en"]:
                print("EN:", s["sources"]["en"][0][:120])
                print("ZH:", tp(s["sources"]["en"][0]))
                return
        print("no body paragraphs found")
        return

    ensure_ebook_row()
    chunks = assemble_pilot(sections, tp, source_order=SOURCE_ORDER)
    out = out_jsonl_path()
    write_jsonl(chunks, out)
    print(f"Wrote {out} ({len(chunks)} chunks)", flush=True)
    if args.upload:
        upload(chunks, out)


if __name__ == "__main__":
    main()
