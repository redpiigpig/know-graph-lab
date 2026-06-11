"""Pure parsing / pagination / alignment helpers for the /apocrypha 逐節重建
pipeline (典外文獻 per-verse rebuild).

Design (locked with user 2026-06-10):
  - The PUBLIC-DOMAIN English edition (Charles APOT 1913 for OT pseudepigrapha,
    M.R. James 1924 for NT) is the AUTHORITATIVE chapter:verse skeleton.
  - The 黃根春 Chinese is mapped ONTO that skeleton 1:1, so verse counts track the
    English (no over-segmentation) and ZH↔EN align by (chapter, verse).
  - order_index = chapter*1000 + verse  → the shared alignment key across versions.
  - Reader paginates 10 CHAPTERS per page; each chapter shows a 「第 N 章」 heading
    and every verse carries its verse number.

Import-safe: no network / no DB / no env at import time (mirrors
gnostic_library.py). bs4/lxml are only needed by tests indirectly; the Charles
parser here is plain-regex on already-text-extracted HTML. Tested by
scripts/tests/test_apocrypha_verses.py.
"""
from __future__ import annotations

import html as _html
import re

VERSE_MULT = 1000  # order_index = chapter*VERSE_MULT + verse (verse < 1000)


# ── order_index <-> (chapter, verse) ─────────────────────────────────────────
def order_index(chapter: int, verse: int) -> int:
    """Shared cross-version alignment key. verse must be in [0, 999]."""
    if not (0 <= verse < VERSE_MULT):
        raise ValueError(f"verse {verse} out of range [0,{VERSE_MULT})")
    return chapter * VERSE_MULT + verse


def decode_order_index(oi: int) -> tuple[int, int]:
    return divmod(oi, VERSE_MULT)


# ── 10-chapters-per-page pagination ──────────────────────────────────────────
def chapter_pages(chapter_nums, per: int = 10) -> list[list[int]]:
    """Group the sorted distinct chapter numbers into pages of `per` chapters.

    Returns a list of pages, each a list of chapter numbers. Non-contiguous
    chapter sets are handled (we group the sorted sequence, not numeric ranges)."""
    if per < 1:
        raise ValueError("per must be >= 1")
    chs = sorted(set(int(c) for c in chapter_nums))
    return [chs[i:i + per] for i in range(0, len(chs), per)]


def page_label(page_chapters: list[int]) -> str:
    """'第 1–10 章' / '第 11 章' for a page's chapter list."""
    if not page_chapters:
        return ""
    lo, hi = page_chapters[0], page_chapters[-1]
    return f"第 {lo} 章" if lo == hi else f"第 {lo}–{hi} 章"


def page_index_for_chapter(pages: list[list[int]], chapter: int) -> int:
    """1-based page number containing `chapter`, or 1 if not found."""
    for i, pg in enumerate(pages):
        if chapter in pg:
            return i + 1
    return 1


# ── Charles APOT (CCEL) chapter:verse parser ─────────────────────────────────
# CCEL Charles pages mark chapters as "[ Chapter N ]" and verses as bare
# sequential integers (1,2,3,…). Charles sometimes omits the "1" for a
# single-verse chapter, so an empty marker run means the whole body is verse 1.
_CHAPTER_SPLIT = re.compile(r"\[\s*Chapter\s+(\d+)\s*\]")
_BARE_INT = re.compile(r"(?<![\d.])(\d{1,3})(?![\d])")


def _clean_verse_text(s: str) -> str:
    s = s.replace("\r", "")
    s = re.sub(r"\n{2,}", "\n", s).strip()
    s = re.sub(r"[ \t]*\n[ \t]*", "\n", s)
    return s.strip()


def parse_charles_chapters(plain_text: str) -> dict[int, dict[int, str]]:
    """Tag-stripped CCEL Charles text → {chapter: {verse: text}}.

    `plain_text` is the page(s) with HTML already converted to text (block tags
    → newlines). Verse markers are accepted only when they continue the expected
    ascending sequence from 1, so numerals inside prose are not mistaken for
    verse numbers."""
    parts = _CHAPTER_SPLIT.split(plain_text)
    out: dict[int, dict[int, str]] = {}
    for i in range(1, len(parts), 2):
        ch = int(parts[i])
        body = parts[i + 1]
        nums = list(_BARE_INT.finditer(body))
        seq: list[tuple[int, int, int]] = []  # (verse, start, end)
        expect = 1
        for m in nums:
            if int(m.group(1)) == expect:
                seq.append((expect, m.start(), m.end()))
                expect += 1
        vmap: dict[int, str] = {}
        if not seq:
            txt = _clean_verse_text(body)
            if txt:
                vmap[1] = txt
        for j, (v, _s, e) in enumerate(seq):
            end = seq[j + 1][1] if j + 1 < len(seq) else len(body)
            txt = _clean_verse_text(body[e:end])
            if txt:
                vmap[v] = txt
        if vmap:
            out[ch] = vmap
    return out


# ── Charles APOT (CCEL) ANCHOR-based parser (authoritative) ──────────────────
# The CCEL Charles HTML carries an UNAMBIGUOUS per-verse anchor:
#     <a name="9_2"><sup> 2</sup></a>  → chapter 9, verse 2 starts here.
# and a chapter anchor  <b>[<a name="Chapter 9">Chapter 9</a>]</b>.
# The old parse_charles_chapters() stripped these tags and then guessed verse
# boundaries from inline bare integers — but CCEL renders the verse number as a
# <sup> floated MID-sentence, so the guesses landed inside words and silently
# merged trailing verses (e.g. ch9 8–11 collapsed into "verse 7"). Splitting on
# the name="C_V" anchors instead recovers the exact versification. Verses CCEL
# leaves un-anchored (it occasionally omits one, e.g. 9:8) fold into the prior
# verse — surfaced as a coverage gap rather than a wrong boundary.
_V_ANCHOR = re.compile(r'<a\s+name="(\d+)_(\d+)"\s*>.*?</a>', re.S | re.I)
_CH_ANCHOR = re.compile(r'<a\s+name="Chapter\s+(\d+)"\s*>.*?</a>', re.S | re.I)
_MARKER = re.compile('\x01(\\d+)\\|(\\d+)\x02|\x03(\\d+)\x04')


def _normalize_ws(s: str) -> str:
    s = s.replace('\x03', ' ').replace('\x04', ' ').replace('\r', '')
    s = re.sub(r'[ \t]*\n[ \t]*', '\n', s)
    s = re.sub(r'\n{2,}', '\n', s)
    s = re.sub(r'[ \t]{2,}', ' ', s)
    return s.strip()


def parse_ccel_anchored(raw_html: str) -> dict[int, dict[int, str]]:
    """Parse RAW CCEL Charles HTML into {chapter: {verse: text}} by splitting on
    the `<a name="C_V">` verse anchors (the chapter number is taken from the verse
    anchor itself, so it is robust even where the chapter heading is malformed).

    Pass the concatenated raw HTML of the book's pages — NOT tag-stripped text."""
    s = _V_ANCHOR.sub(lambda m: f'\x01{m.group(1)}|{m.group(2)}\x02', raw_html)
    s = _CH_ANCHOR.sub(lambda m: f'\x03{m.group(1)}\x04', s)
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'</(p|div|br|tr|li|h\d)>', '\n', s, flags=re.I)
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = _html.unescape(s)

    out: dict[int, dict[int, str]] = {}
    marks = list(_MARKER.finditer(s))
    for i, m in enumerate(marks):
        if m.group(1) is None:        # chapter marker — skip; verses carry chapter
            continue
        ch, v = int(m.group(1)), int(m.group(2))
        end = marks[i + 1].start() if i + 1 < len(marks) else len(s)
        txt = _normalize_ws(s[m.end():end])
        if txt:
            # keep-longest if the same (ch,v) anchor appears twice (rare dup)
            prev = out.get(ch, {}).get(v)
            if prev is None or len(txt) > len(prev):
                out.setdefault(ch, {})[v] = txt
    return out


# ── pseudepigrapha.com Charles parser (route b — books not on CCEL) ──────────
# pseudepigrapha.com hosts Charles' OT-pseudepigrapha (Jubilees, 2 Enoch, the
# Testaments, 2–4 Baruch, Psalms of Solomon, Sibyllines …) as one page per
# chapter: `<h5>[Chapter N]</h5>` then an `<ol>` whose `<li>` items ARE the
# verses (1..k). Far cleaner than the inline-number guess. The leading editorial
# summary lives in a `<blockquote>` BEFORE the `[Chapter N]` heading, so it never
# enters the verse list. Single-chapter works (no `[Chapter N]`) → chapter 1.
_PSEUD_CH = re.compile(r'\[\s*Chapter\s+(\d+)\s*\]', re.I)
_PSEUD_OL = re.compile(r'<ol\b[^>]*>(.*?)</ol>', re.S | re.I)
_PSEUD_LI_SPLIT = re.compile(r'<li\b[^>]*>', re.I)


def _ol_items(ol_inner: str) -> list[str]:
    """Split an <ol> body into its <li> items. pseudepigrapha.com leaves <li>
    UNCLOSED (no </li>), so split on the opening <li> tag rather than requiring a
    close. Any stray </li> is removed by the later tag strip."""
    return _PSEUD_LI_SPLIT.split(ol_inner)[1:]  # drop preamble before first <li>


def _strip_html_text(s: str) -> str:
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = _html.unescape(s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def parse_pseudepigrapha_html(raw_html: str) -> dict[int, dict[int, str]]:
    """Parse pseudepigrapha.com Charles chapter HTML → {chapter: {verse: text}}.

    Pass the concatenated raw HTML of the chapter pages. Each `[Chapter N]`
    heading is followed by an `<ol>`; its `<li>` children become verses 1..k.
    If no `[Chapter N]` marker is present the whole first `<ol>` is chapter 1."""
    out: dict[int, dict[int, str]] = {}
    marks = list(_PSEUD_CH.finditer(raw_html))
    if not marks:
        ol = _PSEUD_OL.search(raw_html)
        if ol:
            for i, li in enumerate(_ol_items(ol.group(1)), start=1):
                t = _strip_html_text(li)
                if t:
                    out.setdefault(1, {})[i] = t
        return out
    for j, m in enumerate(marks):
        ch = int(m.group(1))
        end = marks[j + 1].start() if j + 1 < len(marks) else len(raw_html)
        region = raw_html[m.end():end]
        ol = _PSEUD_OL.search(region)        # first <ol> after the heading
        if not ol:
            continue
        for i, li in enumerate(_ol_items(ol.group(1)), start=1):
            t = _strip_html_text(li)
            if t:
                out.setdefault(ch, {})[i] = t
    return out


# ── ZH-onto-EN-skeleton merge (driver feeds per-window LLM output here) ───────
def merge_verse_windows(window_results, skeleton) -> dict[int, dict[int, str]]:
    """Merge per-window {chapter:{verse:text}} fragments into one map, KEEPING the
    longest text per (ch,v) (overlapping windows re-emit boundary verses), and
    CLAMPING to the English skeleton: only (ch,v) that exist in `skeleton`
    (an EN {ch:{v:...}} or {ch: set(v)}) are kept. This is what enforces the
    "English skeleton is authoritative" invariant and kills over-segmentation."""
    allowed: dict[int, set[int]] = {}
    for ch, vs in skeleton.items():
        allowed[int(ch)] = set(int(v) for v in (vs.keys() if isinstance(vs, dict) else vs))

    out: dict[int, dict[int, str]] = {}
    for frag in window_results:
        for ch, vs in frag.items():
            ch = int(ch)
            if ch not in allowed:
                continue
            for v, text in vs.items():
                v = int(v)
                if v not in allowed[ch]:
                    continue
                t = (text or "").strip()
                if not t:
                    continue
                prev = out.get(ch, {}).get(v)
                if prev is None or len(t) > len(prev):
                    out.setdefault(ch, {})[v] = t
    return out


# ── Mapped-text cleanup (post-LLM) ───────────────────────────────────────────
_LEADING_VERSE_MARKERS = re.compile(r'^\s*(?:\d{1,3}\s+)+')
_CJK_RE = re.compile(r'[㐀-鿿]')
_LATIN_RE = re.compile(r'[A-Za-z]')


def strip_leading_verse_markers(text: str) -> str:
    """Drop leaked leading verse-number tokens, e.g. '7 你們…' → '你們…',
    '10 11 他們…' → '他們…'. Only strips a run of bare numbers at the very start
    (a number glued to CJK like '7你們' is left alone — could be meaningful)."""
    return _LEADING_VERSE_MARKERS.sub('', text or '').strip()


def looks_english(text: str, min_len: int = 12) -> bool:
    """True when a *Chinese* verse slot actually holds English (the LLM copied the
    English anchor because it found no Chinese). Heuristic: enough Latin letters,
    essentially no CJK."""
    t = (text or '').strip()
    if len(t) < min_len:
        return False
    latin = len(_LATIN_RE.findall(t))
    cjk = len(_CJK_RE.findall(t))
    return latin >= 8 and cjk <= 1


def clean_zh_verses(verses_by_ch: dict[int, dict[int, str]]) -> dict[int, dict[int, str]]:
    """Apply per-verse cleanup to a ZH map: strip leaked leading verse markers and
    DROP verses that are actually English (leaked anchors). Empty chapters removed."""
    out: dict[int, dict[int, str]] = {}
    for ch, vs in verses_by_ch.items():
        for v, txt in vs.items():
            t = strip_leading_verse_markers(txt)
            if not t or looks_english(t):
                continue
            out.setdefault(ch, {})[v] = t
    return out


# ── Tolerant LLM-output parsing (windows may truncate at token cap) ───────────
import json as _json

_VERSE_OBJ_RE = re.compile(
    r'"chapter"\s*:\s*(\d{1,3})\s*,\s*"verse"\s*:\s*(\d{1,3})\s*,\s*"text"\s*:\s*"((?:[^"\\]|\\.)*)"'
)


def extract_verse_objects(raw: str) -> list[dict]:
    """Pull {chapter,verse,text} objects out of an LLM JSON reply, tolerant of
    truncation / trailing garbage (a window may hit the token cap mid-array). Tries
    strict json first; on failure salvages every complete verse object via regex.
    Always returns a list of {'chapter':int,'verse':int,'text':str}."""
    out: list[dict] = []
    try:
        j = _json.loads(raw)
        for it in j.get("verses", []):
            try:
                out.append({"chapter": int(it["chapter"]), "verse": int(it["verse"]),
                            "text": str(it.get("text") or "")})
            except (KeyError, ValueError, TypeError):
                continue
        if out:
            return out
    except Exception:
        pass
    for m in _VERSE_OBJ_RE.finditer(raw):
        try:
            text = _json.loads('"' + m.group(3) + '"')   # unescape via json
        except Exception:
            text = m.group(3)
        out.append({"chapter": int(m.group(1)), "verse": int(m.group(2)), "text": text})
    return out


# ── Chinese-own skeleton (no PD English available) ───────────────────────────
def renumber_chapters_sequential(verses_by_ch: dict[int, dict[int, str]]) -> dict[int, dict[int, str]]:
    """For docs with no English skeleton: remap whatever chapter keys the LLM
    emitted to a clean 1..N sequence (preserving order), keeping each chapter's
    verses renumbered 1..k by their sorted original verse order. Guarantees a
    self-consistent 章:節 for the reader (10-ch pagination, 第N章 headings)."""
    out: dict[int, dict[int, str]] = {}
    for new_ch, old_ch in enumerate(sorted(verses_by_ch), start=1):
        vs = verses_by_ch[old_ch]
        out[new_ch] = {}
        for new_v, old_v in enumerate(sorted(vs), start=1):
            t = (vs[old_v] or "").strip()
            if t:
                out[new_ch][new_v] = t
        if not out[new_ch]:
            del out[new_ch]
    # re-compact chapter numbers after possible empties
    return {i + 1: out[ch] for i, ch in enumerate(sorted(out))}


# ── DB rows ──────────────────────────────────────────────────────────────────
def verse_rows(slug: str, version_code: str,
               verses_by_ch: dict[int, dict[int, str]]) -> list[dict]:
    """Flatten {ch:{v:text}} into apocrypha_sections insert rows."""
    rows: list[dict] = []
    for ch in sorted(verses_by_ch):
        for v in sorted(verses_by_ch[ch]):
            txt = verses_by_ch[ch][v]
            rows.append({
                "doc_slug": slug,
                "version_code": version_code,
                "order_index": order_index(ch, v),
                "chapter": ch,
                "verse": v,
                "section_label": f"{ch}:{v}",
                "text": txt,
                "char_count": len(txt),
            })
    return rows


# ── Monotonic accumulate guard ───────────────────────────────────────────────
def union_fill(verses: dict[int, dict[int, str]],
               seed: dict[int, dict[int, str]]) -> dict[int, dict[int, str]]:
    """Re-add any (ch,v) present in `seed` but missing from `verses`, using the
    seed text. Guarantees an --accumulate pass is MONOTONIC: keep-longest +
    clean_zh_verses can drop a previously-aligned verse (a new longer candidate
    that then fails the English/number cleanup), which would regress coverage
    (observed: wisdom-solomon 435→364). The seed was itself a prior clean pass, so
    re-filling from it never re-introduces noise. New verses in `verses` win."""
    out: dict[int, dict[int, str]] = {ch: dict(vs) for ch, vs in verses.items()}
    for ch, vs in seed.items():
        for v, t in vs.items():
            t = (t or "").strip()
            if t and v not in out.get(ch, {}):
                out.setdefault(ch, {})[v] = t
    return out


# ── Coverage / alignment gate ────────────────────────────────────────────────
def coverage(en: dict[int, dict[int, str]], zh: dict[int, dict[int, str]]) -> dict:
    """Alignment report between the EN skeleton and the mapped ZH.

    aligned = (ch,v) present in both; en_only = skeleton verses with no ZH;
    zh_extra = ZH verses outside the skeleton (should be 0 after merge clamp)."""
    en_keys = {(c, v) for c, vs in en.items() for v in vs}
    zh_keys = {(c, v) for c, vs in zh.items() for v in vs}
    aligned = en_keys & zh_keys
    return {
        "en_verses": len(en_keys),
        "zh_verses": len(zh_keys),
        "aligned": len(aligned),
        "en_only": len(en_keys - zh_keys),
        "zh_extra": len(zh_keys - en_keys),
        "coverage": round(len(aligned) / len(en_keys), 4) if en_keys else 0.0,
    }
