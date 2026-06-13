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

# ── Book registry (per-volume metadata) ──────────────────────────────────────
# Each book = one ebook row + reader. REFERENCE-mode books pair the existing 中譯
# (main column) with the English original; SELF-TRANSLATE books render my own 繁中.
REGISTRY = {
    "unknown-christ": {
        "ebook_id": "55555555-5555-4555-8555-555555555555",
        "title": "印度教中未知的基督",
        "subtitle": "基督宗教與印度教的交會（英／繁中對照）",
        "author": "雷蒙‧潘尼卡", "author_en": "Raimon Panikkar",
        "original_title": "The Unknown Christ of Hinduism", "year": 1981,
        "category": "世界宗教", "subcategory": "基督教",
        "volume": "印度教中未識的基督（雷蒙‧潘尼卡）", "parent_volume": "印度教與基督宗教",
    },
    "intrareligious-dialogue": {
        "ebook_id": "55555556-5555-4555-8555-555555555555",
        "title": "宗教內對話",
        "subtitle": "英文原典＋王志成‧思竹中譯逐段對照（第三方參考譯本）",
        "author": "雷蒙‧潘尼卡", "author_en": "Raimon Panikkar",
        "original_title": "The Intrareligious Dialogue", "year": 1999,
        "category": "世界宗教", "subcategory": "基督教",
        "volume": "宗教內對話（雷蒙‧潘尼卡）", "parent_volume": "宗教間／宗教內對話",
        # Chapter manifest (prologue + 10 chapters, same order both sides) for
        # split_chapters_by_manifest. EN anchors use clean tokens robust to the
        # PDF's broken font cmap (ŚŪNYATĀ→"SONYATA" → use "BUDDHIST"; HINDU→"HINou"
        # → "TOWARD A HIN"). ZH anchors give 第N章 + a title fallback for chapters
        # whose number the scan-OCR dropped (第5章 → "懸置").
        "chapters_en": [
            "SERMON ON THE MOUNT", "RHETORIC OF THE DIALOGUE", "THE DIALOGICAL DIALOGUE",
            "FAITH AND BELIEF", "RULES OF THE GAME", "EPOCH", "CATEGORY OF GROWTH",
            "ECUMENICAL ECUMENISM", "RAMON LLULL", "BUDDHIST", "TOWARD A HIN",
        ],
        "chapters_zh": [
            "山上訓道", ["第1章", "修辭學"], ["第2章", "對話的對話"], ["第3章", "信仰與信念"],
            ["第4章", "遊戲規則"], ["第5章", "懸置"], ["第6章", "成長範疇", "範疇"],
            ["第7章", "普世的普世主義"], ["第8章", "拉蒙"], ["第9章", "空與實"],
            ["第10章", "印度教-基督教", "走向印度教"],
        ],
    },
}

# Active book (mutated by select_book()); defaults to the pilot 起手卷.
BOOK_META = REGISTRY["unknown-christ"]
EBOOK_ID = BOOK_META["ebook_id"]
VOLUME = BOOK_META["volume"]
PARENT_VOLUME = BOOK_META["parent_volume"]
SOURCE_ORDER = ["en"]  # bilingual; 升三欄 → ["en", "es"]
DATA_DIR = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works" / "panikkar_data" / "uch"


def select_book(slug: str) -> dict:
    """Point the module globals at a registry book so cover/chunks/ebook-row use
    its ebook_id, volume tree and metadata."""
    global BOOK_META, EBOOK_ID, VOLUME, PARENT_VOLUME
    if slug not in REGISTRY:
        raise SystemExit(f"unknown --book {slug!r}; known: {', '.join(REGISTRY)}")
    BOOK_META = REGISTRY[slug]
    EBOOK_ID = BOOK_META["ebook_id"]
    VOLUME = BOOK_META["volume"]
    PARENT_VOLUME = BOOK_META["parent_volume"]
    return BOOK_META

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


# CJK chapter headings (existing 中譯 are split on these). Simplified + traditional
# forms both covered, since split runs on the raw 簡體 text before opencc.
# A real heading is the token (第N章 / 導論 / 前言…) followed by a BOUNDARY
# (whitespace, colon, dot, 、, or end-of-line) — NOT a continuing char like 的/是,
# so a body sentence starting "第一章的正文。" is correctly NOT a heading.
_CJK_HEADING_RE = re.compile(
    r"^("
    r"第[一二三四五六七八九十百千零〇两兩0-9]+[章節节部編编卷講讲篇回]"   # 第一章 / 第3節 …
    r"|導論|导论|緒論|绪论|導言|导言|前言|序言|自序|序|引言|引論|引论"
    r"|結論|结论|結語|结语|餘論|余论|附錄|附录|附論|附论|目錄|目录|凡例"
    r"|跋|後記|后记|後語|后语|譯後記|译后记|譯序|译序|致謝|致谢"
    r")(?:[\s：:．.、]|$).*$")


def _is_heading(line: str) -> bool:
    s = line.strip()
    if not s or len(s) > 69:
        return False
    return bool(_HEADING_RE.match(s) or _CJK_HEADING_RE.match(s))


def split_sections(text: str) -> list[dict]:
    """Split source text into [{heading, paras:[...]}] on chapter-heading anchors.
    Front matter before the first heading is kept as a '(front)' section. Long
    lines that merely mention 'Chapter 1' never split (length guard)."""
    # Isolate markdown heading lines into their own blocks: Gemini OCR
    # (--mark-headings) emits `## Title` on its own line but glues it to the next
    # paragraph with a single \n; block-splitting only breaks on blank lines, so
    # surround every `#…` heading line with blanks first.
    text = re.sub(r"(?m)^[ \t]*(#{1,6}\s+\S.*?)[ \t]*$", r"\n\1\n", text)
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


# ── reference-translation mode (existing full 中譯 → 逐段對照, NO re-translation) ─
# When a work already has a complete published Chinese translation (e.g. 王志成
# 的潘尼卡譯本), we do NOT re-translate: the existing 中譯 becomes the main column
# and the English original is shown side-by-side, paragraph-aligned. Marked as a
# third-party reference translation (private-use, see SKILL.md). 簡體先 opencc→繁.
def build_reference_chunk(
    *,
    chunk_index: int,
    title_zh: str,
    en_head: str,
    zh_paras: list,
    en_paras: list,
    volume: str = VOLUME,
    parent_volume: str = PARENT_VOLUME,
    page_number: int | None = None,
) -> dict:
    """One section → one reader chunk where `content` is the EXISTING 中譯 (main
    column) and `sources.en` is the English original aligned to the 中譯's
    paragraph count. The translation drives the row count; English is padded/
    joined onto it (align_secondary)."""
    en_aligned = align_secondary(zh_paras, en_paras)
    zh_rows = [f"## {title_zh}"] + [z or "" for z in zh_paras]
    en_rows = [f"## {en_head}"] + en_aligned
    assert len(zh_rows) == len(en_rows), \
        f"chunk {chunk_index}: zh {len(zh_rows)} != en {len(en_rows)}"
    chunk = build_multilang_chunk(
        chunk_index=chunk_index,
        chapter_path=f"{PARENT_VOLUME} · {title_zh}",
        content_zh="\n\n".join(zh_rows),
        sources={"en": "\n\n".join(en_rows)},
        source_order=["en"],
        volume=volume,
        parent_volume=parent_volume,
        page_number=page_number if page_number is not None else chunk_index + 1,
        title_en=en_head,
    )
    validate_multilang_chunk(chunk)
    return chunk


# Front/end matter headings to drop before pairing chapters (EN + 簡/繁中). NOT
# 導論/緒論/introduction — those can be real content chapters.
_FRONTMATTER_RE = re.compile(
    r"(?i)(preface|foreword|a note to the reader|table of contents|contents\b|"
    r"acknowledg|^index$|bibliograph|about the author|abbreviation|glossary|"
    r"copyright|前言|序言|序\b|自序|原版序|新版序|譯序|译序|譯者的話|译者的话|"
    r"作者簡介|作者简介|編者|编者|目錄|目录|凡例|索引|參考書目|参考书目|"
    r"致謝|致谢|縮寫|缩写|版權|版权|附錄|附录)")


def is_frontmatter(heading: str) -> bool:
    """True if a section heading is front/end matter (preface, TOC, 作者簡介…) and
    should not be paired as a chapter. '(front)' (text before the first heading)
    is always front matter."""
    h = heading.lstrip("# ").strip()
    if h == "(front)":
        return True
    return bool(_FRONTMATTER_RE.search(h))


def merge_repeated_headings(sections: list[dict]) -> list[dict]:
    """Merge consecutive sections sharing the SAME heading into one. OCR
    (--mark-headings) re-marks a running head on every page, fragmenting one
    chapter/preface into N sections with an identical `## ` title."""
    out: list[dict] = []
    for s in sections:
        if out and out[-1]["heading"] == s["heading"]:
            out[-1]["paras"].extend(s["paras"])
        else:
            out.append({"heading": s["heading"], "paras": list(s["paras"])})
    return out


def chapter_sections(sections: list[dict]) -> list[dict]:
    """Real chapters only: merge OCR-fragmented repeats, then drop front/end matter."""
    return [s for s in merge_repeated_headings(sections) if not is_frontmatter(s["heading"])]


def _norm_anchor(s: str) -> str:
    """Normalize a heading for anchor matching: strip diacritics (ŚŪNYATĀ→SUNYATA,
    EPOCHÊ→EPOCH), drop non-alphanumerics, uppercase. CJK passes through."""
    import unicodedata
    s = unicodedata.normalize("NFKD", s.lstrip("# "))
    return "".join(c for c in s if c.isalnum() and not unicodedata.combining(c)).upper()


def split_chapters_by_manifest(sections: list[dict], anchors: list[str],
                               min_chapter_chars: int = 300) -> list[dict]:
    """Split heading-marked sections into chapters by sequentially matching an
    ordered list of distinctive `anchors` (one per chapter, prologue first).

    The robust discriminator against the two OCR hazards — a TABLE OF CONTENTS
    (every chapter title listed back-to-back) and RUNNING-HEAD fragmentation (the
    title re-marked on later pages) — is the **following body**: a real chapter
    carries `min_chapter_chars`+ of text before the NEXT anchor match, whereas a
    contents-list entry's next anchor sits immediately after it (≈0 body), and a
    running-head repeat already lies inside an accepted chapter (skipped as we've
    advanced past that anchor). Everything between two accepted chapter starts —
    including sub-section `## ` headings — folds into the chapter (headings kept as
    body lines so they show + give more rows to align on)."""
    # Each chapter anchor is a string OR a list of alternatives (match if ANY) —
    # so a chapter whose number ("第5章") the OCR dropped still matches on its title
    # ("懸置"). Normalize all alternatives up front.
    alts = [[_norm_anchor(a) for a in (anc if isinstance(anc, (list, tuple)) else [anc]) if a]
            for anc in anchors]
    secs = merge_repeated_headings(sections)
    match = []
    for s in secs:
        hn = _norm_anchor(s["heading"])
        match.append(next((i for i, A in enumerate(alts) if any(a in hn for a in A)), -1))
    bodychars = [sum(len((p or "").strip()) for p in s["paras"]) for s in secs]
    anchor_pos = [k for k in range(len(secs)) if match[k] >= 0]

    following: dict = {}
    for idx, k in enumerate(anchor_pos):
        nxt = anchor_pos[idx + 1] if idx + 1 < len(anchor_pos) else len(secs)
        following[k] = sum(bodychars[k:nxt])

    starts: list[int] = []
    ai = 0
    prev = -1
    for k in anchor_pos:
        if ai < len(anchors) and match[k] == ai and k > prev and following[k] >= min_chapter_chars:
            starts.append(k)
            prev = k
            ai += 1

    chapters: list[dict] = []
    for si, k in enumerate(starts):
        end = starts[si + 1] if si + 1 < len(starts) else len(secs)
        paras = list(secs[k]["paras"])
        for j in range(k + 1, end):
            if secs[j]["heading"] != "(front)":
                paras.append(secs[j]["heading"])
            paras.extend(secs[j]["paras"])
        chapters.append({"heading": secs[k]["heading"].lstrip("# ").strip(), "paras": paras})
    return chapters


def align_reference_chapters(en_sections: list[dict], zh_sections: list[dict]) -> tuple[list[tuple], int, int]:
    """Drop front matter + merge repeats on both sides, then pair the remaining
    chapters by order → (pairs, n_en_chapters, n_zh_chapters). Caller checks the
    two counts match before trusting the alignment (a mismatch means OCR over/
    under-split and needs a per-book manifest)."""
    en_ch = chapter_sections(en_sections)
    zh_ch = chapter_sections(zh_sections)
    return pair_sections(en_ch, zh_ch), len(en_ch), len(zh_ch)


def pair_sections(en_sections: list[dict], zh_sections: list[dict]) -> list[tuple]:
    """Pair English + existing-中譯 sections by order (translations keep the
    author's chapter order) → [(title_zh, en_head, en_paras, zh_paras)]. Uneven
    counts are padded with empty paras so no chapter is dropped (log/inspect when
    counts differ; a real mismatch means the split needs tuning)."""
    out: list[tuple] = []
    n = max(len(en_sections), len(zh_sections))
    blank = {"heading": "", "paras": []}
    for i in range(n):
        en = en_sections[i] if i < len(en_sections) else blank
        zh = zh_sections[i] if i < len(zh_sections) else blank
        out.append((zh["heading"], en["heading"], list(en["paras"]), list(zh["paras"])))
    return out


def assemble_reference(en_sections: list[dict], zh_sections: list[dict]) -> list[dict]:
    """Build cover + one reference chunk per paired section (existing 中譯 main,
    English aligned). No LLM — this is the path for works with a complete
    published Chinese translation. Forwards the ACTIVE volume/parent_volume
    (build_reference_chunk's defaults are frozen at def-time, so select_book()'s
    reassignment must be passed explicitly)."""
    chunks = [make_cover_chunk()]
    man_en = BOOK_META.get("chapters_en")
    man_zh = BOOK_META.get("chapters_zh")
    if man_en and man_zh:
        en_ch = split_chapters_by_manifest(en_sections, man_en)
        zh_ch = split_chapters_by_manifest(zh_sections, man_zh)
        pairs, n_en, n_zh = pair_sections(en_ch, zh_ch), len(en_ch), len(zh_ch)
    else:
        pairs, n_en, n_zh = align_reference_chapters(en_sections, zh_sections)
    if n_en != n_zh:
        print(f"  ⚠ chapter count mismatch: EN={n_en} ZH={n_zh} — pairing by order; "
              f"verify alignment (may need a per-book chapter manifest)", flush=True)
    for i, (title_zh, en_head, en_paras, zh_paras) in enumerate(pairs, start=1):
        chunks.append(build_reference_chunk(
            chunk_index=i, title_zh=title_zh, en_head=en_head,
            zh_paras=zh_paras, en_paras=en_paras, page_number=i + 1,
            volume=VOLUME, parent_volume=PARENT_VOLUME))
    return chunks


def load_zh_sections(src_path: Path, *, to_traditional: bool = True) -> list[dict]:
    """Load an existing Chinese translation → [{heading, paras}]. Splits on
    heading anchors; each blank-line block is ONE paragraph (clean digital text,
    so no English-style reflow/merge — that would glue 中文 paragraphs, which end
    in 。！？ not '.'); 簡體 → 繁中 via opencc s2tw (standardize_ebook.to_traditional)
    unless disabled (tests)."""
    text = src_path.read_text(encoding="utf-8", errors="replace")
    conv = None
    if to_traditional:
        import standardize_ebook as se
        conv = se.to_traditional
    out: list[dict] = []
    for s in split_sections(text):
        paras = [re.sub(r"\s*\n\s*", "", p).strip() for p in s["paras"]]
        paras = [p for p in paras if p]
        head = s["heading"]
        if conv:
            head = conv(head)
            paras = [conv(p) for p in paras]
        if head == "(front)" and not paras:
            continue
        out.append({"heading": head, "paras": paras})
    return out


# ── translation engine (prod only) ───────────────────────────────────────────
# {srclang} is filled per book (英文 / 義大利文 / 西班牙文) — Panikkar wrote his
# works in several languages; the no-中譯 volumes are self-translated from whatever
# original we hold (the Jaca Book Opera Omnia is Italian; others English/Spanish).
PANIKKAR_PROMPT_TMPL = """你是比較神學與宗教哲學經典的專業譯者，正在翻譯雷蒙‧潘尼卡（Raimon Panikkar）的著作。把下列**{srclang}原文**翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；台灣天主教用語；中間點用「‧」。
2. 只翻譯{srclang}原文；不要加前言或說明。
3. 忠實學術／神學散文語氣，長句可順為通順中文；保留括號內的外文夾注（梵文/拉丁文/希臘文，如 Brahman、advaita、Logos、plērōma）。
4. 保留 Markdown（## 標題 / **粗體** / *斜體* / > 引文）。
5. 潘尼卡自鑄詞鎖死（首見括注原詞）：cosmotheandric→宇宙神人共融、intrareligious dialogue→宗教內對話、interreligious dialogue→宗教間對話、Christophany→基督顯現、the whole Christ→全基督、pluralism→多元論、advaita→不二、tempiternity→時永。聖神（非聖靈）。
   印度術語對齊：Brahman→梵、ātman→阿特曼、dharma→達磨/法、karma→業、Veda→吠陀、Upaniṣad→奧義書。
   人名 Panikkar→潘尼卡（非帕尼卡）。
6. 只輸出翻譯後的繁體中文。

{srclang}原文：
{{source}}"""

_SRC_LABELS = {"en": "英文", "it": "義大利文", "es": "西班牙文", "de": "德文", "fr": "法文"}


def make_engine(src_lang: str = "en"):
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = PANIKKAR_PROMPT_TMPL.format(srclang=_SRC_LABELS.get(src_lang, "外文"))

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
    m = BOOK_META
    row = {
        "id": EBOOK_ID,
        "title": m["title"],
        "subtitle": m["subtitle"],
        "author": m["author"],
        "author_en": m["author_en"],
        "original_title": m["original_title"],
        "original_publish_year": m["year"],
        "file_type": "epub",
        "category": m["category"],
        "subcategory": m["subcategory"],
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


def load_en_sections(src_path: Path) -> list[dict]:
    """Read a plain-text English source → [{heading, paras}]. Split on heading
    anchors FIRST, then reflow each section's body (de-wrap / de-hyphenate / heal
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
        out.append({"heading": s["heading"], "paras": paras})
    return out


def load_sections_from_src(src_path: Path) -> list[dict]:
    """English sections in the assemble_pilot (self-translate) shape:
    [{title_zh, heads:{en}, sources:{en:[paras]}}]."""
    return [{"title_zh": s["heading"], "heads": {"en": s["heading"]},
             "sources": {"en": s["paras"]}} for s in load_en_sections(src_path)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=str, help="English source text file")
    ap.add_argument("--zh-src", type=str, default=None,
                    help="existing 中譯 text file → REFERENCE mode (no re-translation; "
                         "既有中譯為主欄 + 英文逐段對照，簡體自動轉繁)")
    ap.add_argument("--book", default="unknown-christ",
                    help=f"registry slug ({', '.join(REGISTRY)})")
    ap.add_argument("--dry", action="store_true", help="split + counts only, no LLM")
    ap.add_argument("--probe", action="store_true", help="translate one paragraph, print, exit")
    ap.add_argument("--limit", type=int, default=None, help="only first N sections")
    ap.add_argument("--upload", action="store_true", help="push R2 + DB after building")
    args = ap.parse_args()

    select_book(args.book)
    if not args.src:
        ap.error("--src required (English source text)")
    reference = args.zh_src is not None
    en_secs = load_en_sections(Path(args.src))
    zh_secs = load_zh_sections(Path(args.zh_src)) if reference else []
    if args.limit:
        en_secs = en_secs[:args.limit]
        zh_secs = zh_secs[:args.limit]

    if args.dry:
        mode = "REFERENCE (既有中譯+英文)" if reference else "SELF-TRANSLATE (英→繁中)"
        print(f"mode: {mode}")
        if reference:
            pairs, n_en, n_zh = align_reference_chapters(en_secs, zh_secs)
            print(f"chapters after front-matter filter: EN={n_en} ZH={n_zh}"
                  + ("  ⚠ MISMATCH" if n_en != n_zh else "  ✓ aligned"))
            for i, (title_zh, en_head, en_p, zh_p) in enumerate(pairs, start=1):
                print(f"ch{i} 「{(title_zh or en_head)[:30]}」 ↔ 「{en_head[:30]}」 ZH¶={len(zh_p)} EN¶={len(en_p)}")
        else:
            for i, s in enumerate(en_secs):
                n = len(s["paras"])
                first = s["paras"][0][:66] if n else "—"
                print(f"sec{i} 「{s['heading'][:34]}」 EN¶={n} | {first}")
        return

    ensure_ebook_row()
    if reference:
        chunks = assemble_reference(en_secs, zh_secs)
    else:
        tp = make_engine()
        if args.probe:
            for s in en_secs:
                if s["paras"]:
                    print("EN:", s["paras"][0][:120])
                    print("ZH:", tp(s["paras"][0]))
                    return
            print("no body paragraphs found")
            return
        sections = [{"title_zh": s["heading"], "heads": {"en": s["heading"]},
                     "sources": {"en": s["paras"]}} for s in en_secs]
        chunks = assemble_pilot(sections, tp, source_order=SOURCE_ORDER)
    out = out_jsonl_path()
    write_jsonl(chunks, out)
    print(f"Wrote {out} ({len(chunks)} chunks)", flush=True)
    if args.upload:
        upload(chunks, out)


if __name__ == "__main__":
    main()
