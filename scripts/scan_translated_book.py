"""Scan a translated ebook for LLM-quality bugs that the structural
validator can't catch.

Where this fits:
  validate_book_structure.py  ← structural / TOC / range checks (R001-R022)
  scan_translated_book.py     ← translation-quality checks    (T1-T7)

T1  title-bleed     h3/h4 heading > 30 chars AND contains punctuation
T2  volume-h3 drift content's first h3 disagrees with volume name
T3  title repeated  h3 text reappears verbatim inside body paragraphs
T4  chapter_path bad  contains markdown control chars (* _ `[^N]`)
T5  volume re-entry  same volume name appears in two non-contiguous spans
T6  orphan index    chapter_path 含「索引」but volume isn't 索引/Indexes
T7  cover/front     chunk[0] chapter_path != 「封面」or chunk[1] not 前言/序
T9  cross-work bleed   source_text 有一個 h3 標題指向別封信 / 另一作者的
                       作品（CCEL EPUB 把下一封信的 intro 打包到上一封
                       信末尾的常見問題）。靠 LETTER_CN_LABELS 比對
                       parent 與 letter 來判斷
T10 footnote ref/body mismatch    chunk 內 [^N] refs 跟 (N) body 數量
                                   或編號對不起來
T11 bilingual paragraph drift     ZH 段落數 vs EN 段落數差 > 25%

Usage:
    python scripts/scan_translated_book.py <ebook_id>
    python scripts/scan_translated_book.py <ebook_id> --json
    python scripts/scan_translated_book.py --all
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "scripts"))
try:
    from consolidate_by_ncx import (
        LETTER_CN_LABELS, PARENT_CN_FALLBACK,
        parse_ncx_letters, find_epub, chinese_label,
    )
except Exception:
    LETTER_CN_LABELS = []
    PARENT_CN_FALLBACK = {}
    parse_ncx_letters = None
    find_epub = None
    chinese_label = None

URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H_GET = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

CHUNKS_DIR = Path(os.environ.get("EBOOK_CHUNKS_DIR")
                  or r"G:\我的雲端硬碟\資料\電子書\_chunks")

# A heading line is title-bleed when body-style language ("connective +
# clause") appears mid-heading. Real CCEL titles describe a noun phrase
# («科林多教會因嫉妒和競爭而陷入分裂後的悲慘狀況»); body bleeds slip
# 連詞 / 第二人稱 vocatives / 副詞 starting a new clause:
#   bleed: 「第一章—書信寫作的契機既然我看到你」       「既然」starts new clause
#   bleed: 「第四章——古代已有許多惡行源自此因蓋經上記著」 「蓋」starts body
#   bleed: 「第十章—上述內容的續論亞伯拉罕被稱為「朋友」」「亞伯拉罕被稱為」 vocative body
# We only check the part AFTER the em-dash so we don't false-positive on
# numbered titles like「第一章—蓋天蓋地」(unlikely but theoretically clean).
HEADING_LINE_RE = re.compile(r"^(#{3,4})\s+(.+?)\s*$", re.M)
EM_DASH_SPLIT_RE = re.compile(r"(?:第[一二三四五六七八九十百千零0-9]+章\s*[—\-－]+\s*)(.+)")
TITLE_CLOSE_PUNCT = re.compile(r"[。！？」）]\s*$")  # heading ends with closure
# Body markers — when present mid-heading (i.e. not at position 0 of the
# post-emdash portion) signal a clause break that doesn't belong in a
# title. Curated from observed bleeds.
BODY_MARKERS = [
    "既然", "誠然", "親愛的", "讓我們", "誠如",
    "若你", "若我", "蓋此", "蓋我", "蓋經上", "蓋誠",
    "雖然", "但關於", "但是我", "然而我",
    "因此我", "正如我", "我先前", "我所說", "只要前一",
    "亞伯拉罕被", "本書信", "在已過去", "從一開始",
]

# Markdown control chars that shouldn't appear inside a clean chapter_path
BAD_CP_CHARS = re.compile(r"[\*_`]|\[\^\d+\]")

# Front-matter chapter_paths we DO expect for chunk 0 / 1
FRONT_MATTER_OK_CHUNK0 = {"封面"}
FRONT_MATTER_OK_CHUNK1 = {"前言", "序言", "書名頁", "前言／序"}

# Index labels — chunks with these in chapter_path should sit under an
# index-style volume, not under the last author's volume (the fallback
# bug we saw: 印刷版頁碼索引 attached to 愛任紐《駁異端》).
INDEX_PATH_RE = re.compile(r"索引|目錄|Index", re.I)
INDEX_VOLUME_RE = re.compile(r"索引|Indexes", re.I)

# Bilingual paragraph-drift threshold — if either side has more than 25%
# more paragraphs than the other, the EN-to-ZH alignment is broken and
# the bilingual reader's row pairing won't line up.
BILINGUAL_DRIFT_RATIO = 0.25


def para_count(s: str) -> int:
    """Count non-empty paragraphs (blank-line-delimited blocks)."""
    return sum(1 for p in (s or "").split("\n\n") if p.strip())


def paragraph_drift(zh: str, en: str) -> Optional[float]:
    """Relative paragraph-count drift between aligned ZH/EN text, or None
    when either side has < 4 paragraphs (too short to measure reliably).

    This is the metric behind the T11 「逐段對照」alignment gate. Exposed at
    module level so it can be reused as a post-translation quality check
    (e.g. flag a chunk for re-translation when the bilingual columns won't
    line up row-by-row in the reader)."""
    nz, ne = para_count(zh), para_count(en)
    if nz < 4 or ne < 4:
        return None
    bigger, smaller = max(nz, ne), min(nz, ne)
    return (bigger - smaller) / bigger


# Non-prose chapter_paths where paragraph alignment is meaningless — indexes,
# abbreviation lists, covers, publisher ad pages. Their ZH/EN paragraph counts
# legitimately diverge (list entries collapse/expand differently), so re-
# translating them to "align" is pointless and (for big indexes) very costly.
NONPROSE_PATH_RE = re.compile(
    r"索引|目錄|Index|Indices|縮寫|略語|Abbreviation|封面|cover|"
    r"更多.*著作|出版社的著作|版權|奧客來|參考書目|Bibliography",
    re.I)


def is_nonprose_chunk(chunk: dict) -> bool:
    """True for index / abbreviation / cover / ad chunks — list-like content
    where bilingual paragraph alignment carries no meaning."""
    return bool(NONPROSE_PATH_RE.search(chunk.get("chapter_path") or ""))


def alignment_gate(chunks: list[dict],
                   threshold: float = BILINGUAL_DRIFT_RATIO,
                   skip_nonprose: bool = True) -> list[dict]:
    """逐段對照 gate — return the re-translation worklist.

    For every bilingual PROSE chunk (has both `content` ZH and `source_text`
    EN), flag it when paragraph_drift exceeds `threshold`: the reader pairs
    the 中英對照 columns row-by-row, so a drift past the gate means the
    columns won't line up and the chunk is a re-translation candidate.

    Index / abbreviation / cover / ad chunks are skipped by default
    (`skip_nonprose`) — their paragraph counts legitimately diverge and
    re-translating them to align is meaningless.

    Pure + importable so it runs as a post-translation quality gate (after a
    book is translated) or ad-hoc over any JSONL — independent of the full
    DB/NCX-backed scan()."""
    flagged: list[dict] = []
    for c in chunks:
        zh = c.get("content") or ""
        en = c.get("source_text") or ""
        if not zh or not en:
            continue
        if skip_nonprose and is_nonprose_chunk(c):
            continue
        drift = paragraph_drift(zh, en)
        if drift is not None and drift > threshold:
            flagged.append({
                "chunk_index": c.get("chunk_index"),
                "chapter_path": c.get("chapter_path"),
                "zh_paras": para_count(zh),
                "en_paras": para_count(en),
                "drift": round(drift, 3),
            })
    return flagged


def normalize_heading(s: str) -> str:
    """Strip trailing footnote refs, collapse whitespace + dashes for
    fuzzy matching of headings across source vs NCX."""
    s = re.sub(r"\[\^?\d+\]", "", s)
    s = re.sub(r"[—–\-]+", "-", s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


_INTRO_PREFIX_RE = re.compile(
    r"^introductory\s+notes?\s+to\s+(?:the\s+)?", re.I)


def build_ncx_index(epub_path: Path) -> list[dict]:
    """Return the NCX as a flat list of {en_norm, en_letter_norm, parent}.

    `en_norm` is the literal navLabel text normalized for fuzzy matching.
    `en_letter_norm` is the underlying letter title (for「Introductory
    Note to X」navPoints we strip the prefix so the intro maps to X) —
    this is what we compare against each chunk's `title_en` field set by
    the consolidator. English-only matching keeps the rule robust across
    different Chinese-translation choices.
    """
    if parse_ncx_letters is None:
        return []
    letters = parse_ncx_letters(epub_path)
    out: list[dict] = []
    for L in letters:
        parent = L["parent_label"]
        letter = L["letter_label"]
        m = _INTRO_PREFIX_RE.match(letter)
        underlying = letter[m.end():].strip() if m else letter
        # File stems (basename minus .html) for this letter — lets the T9
        # check resolve a filename-style title_en (e.g. 'anf02.iv.ii.ii.xxxi
        # .html', common in NPNF/ANF) back to its owning letter via prefix.
        stems: set[str] = set()
        for f in [L.get("letter_file", "")] + [cf for cf, _ in L.get("chapters", [])]:
            s = re.sub(r"\.x?html?$", "", re.sub(r"#.*$", "", f or "").split("/")[-1].strip().lower())
            if s:
                stems.add(s)
        out.append({
            "en_norm": normalize_heading(letter),
            "en_letter_norm": normalize_heading(underlying),
            "parent": parent,
            "file_stems": stems,
        })
    return out


def attribute_heading(heading: str,
                      ncx_index: list[dict]) -> Optional[dict]:
    """Find the NCX entry whose normalized navLabel matches the heading.

    Two-tier matching:
      1. Substring (either direction) for NCX entries ≥ 15 chars. Short
         NCX entries like 「fragments」 are too generic for substring;
         skipping them here avoids 「Justin's fragments on resurrection」
         falsely attributing to Papias's bare 「Fragments」 navPoint.
      2. Token-set overlap (Jaccard ≥ 0.5) as a fallback that picks the
         most-overlap entry across the WHOLE NCX, regardless of length.
    """
    h = normalize_heading(heading)
    if len(h) < 8:
        return None
    h_toks = set(t for t in re.split(r"\W+", h) if len(t) >= 3)
    # Disambiguator: if the heading mentions a parent author name
    # ("Ignatius", "Polycarp", "Clement"...) ONLY one of the candidate
    # NCX entries should match. Pre-compute which parents appear in the
    # heading text so the substring/token tiers can prefer them.
    heading_parents = set()
    for entry in ncx_index:
        parent_low = entry["parent"].lower()
        # First word of parent (e.g. "CLEMENT" from "CLEMENT OF ROME").
        # NPNF CCEL NCX depth-1 labels can be empty → guard against IndexError.
        parent_toks = parent_low.split()
        if not parent_toks:
            continue
        parent_first = parent_toks[0]
        if parent_first and parent_first in h and len(parent_first) >= 4:
            heading_parents.add(entry["parent"])
    # Tier 1: substring on long NCX entries
    best = None
    best_len = 0
    for entry in ncx_index:
        en = entry["en_norm"]
        if len(en) < 15:
            continue
        if en in h or h in en:
            # When the heading explicitly names a parent author,
            # restrict matches to that author's NCX entries.
            if heading_parents and entry["parent"] not in heading_parents:
                continue
            if len(en) > best_len:
                best = entry
                best_len = len(en)
    if best:
        return best
    # Tier 1b: substring on shorter NCX entries WITH parent disambiguation.
    # Many NCX entries are short titles like 「Epistle to the Philippians」
    # that appear under BOTH POLYCARP (real) and IGNATIUS (pseudo) parents.
    # Without the parent guard the first matching entry wins arbitrarily.
    if heading_parents:
        for entry in ncx_index:
            if entry["parent"] not in heading_parents:
                continue
            en = entry["en_norm"]
            if len(en) < 8:
                continue
            if en in h or h in en:
                if len(en) > best_len:
                    best = entry
                    best_len = len(en)
        if best:
            return best
    # Tier 2: strict token-set overlap (Jaccard ≥ 0.7), with parent
    # disambiguation. When two NCX entries score equally (e.g. POLYCARP
    # vs IGNATIUS-pseudo both have「Epistle to the Philippians」), prefer
    # the entry whose parent is mentioned in the heading.
    candidates: list[tuple[float, dict]] = []
    for entry in ncx_index:
        en_toks = set(t for t in re.split(r"\W+", entry["en_letter_norm"])
                      if len(t) >= 3)
        if not en_toks:
            continue
        score = len(h_toks & en_toks) / max(len(h_toks | en_toks), 1)
        if score >= 0.7:
            candidates.append((score, entry))
    if not candidates:
        return None
    # Sort by (score desc, parent-in-heading first)
    candidates.sort(key=lambda x: (
        -x[0],
        0 if x[1]["parent"] in heading_parents else 1,
        -len(x[1]["en_norm"]),
    ))
    return candidates[0][1]


class Issue:
    __slots__ = ("rule", "severity", "chunk_index", "message")

    def __init__(self, rule: str, severity: str,
                 chunk_index: Optional[int], message: str):
        self.rule = rule
        self.severity = severity
        self.chunk_index = chunk_index
        self.message = message

    def to_dict(self):
        return {"rule": self.rule, "severity": self.severity,
                "chunk_index": self.chunk_index, "message": self.message}


def load_jsonl(ebook_id: str) -> Optional[list[dict]]:
    fn = CHUNKS_DIR / f"{ebook_id}.jsonl"
    if not fn.exists():
        return None
    return [json.loads(l) for l in fn.read_text(encoding="utf-8").splitlines() if l]


def fetch_book(ebook_id: str) -> Optional[dict]:
    # Select * — T9 (NCX-driven cross-bleed) needs file_path to locate
    # the EPUB; T2 needs volume; future rules may use other fields.
    r = requests.get(f"{URL}/rest/v1/ebooks?id=eq.{ebook_id}&select=*",
                     headers=H_GET, timeout=30)
    if r.status_code != 200:
        return None
    rows = r.json()
    return rows[0] if rows else None


def strip_md(s: str) -> str:
    """Strip markdown markers from a heading line for length measurement."""
    s = re.sub(r"\[\^\d+\]", "", s)        # footnote refs
    s = re.sub(r"\{\{p:\d+\}\}", "", s)    # page markers
    s = re.sub(r"\*+", "", s)              # bold/italic markers
    return s.strip()


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def scan(ebook_id: str) -> list[Issue]:
    issues: list[Issue] = []
    chunks = load_jsonl(ebook_id)
    if not chunks:
        return [Issue("ENV", "FAIL", None, f"JSONL not found / empty: {ebook_id}")]

    # ── T1 title-bleed ──
    for c in chunks:
        idx = c.get("chunk_index")
        for m in HEADING_LINE_RE.finditer(c.get("content") or ""):
            heading_text = strip_md(m.group(2))
            # Only inspect chapter-numbered headings; non-numbered headings
            # are letter titles or section names and have their own shape.
            tail_m = EM_DASH_SPLIT_RE.match(heading_text)
            if not tail_m:
                continue
            tail = tail_m.group(1)
            # If the heading closes with 「。！？」）」, the body marker is
            # part of a legitimate descriptive exhortation title
            # (e.g.「第二十七章——在復活的盼望中，讓我們緊貼…的上帝。」).
            if TITLE_CLOSE_PUNCT.search(tail):
                continue
            for marker in BODY_MARKERS:
                pos = tail.find(marker)
                if pos >= 2:  # not at the very start
                    issues.append(Issue("T1", "WARN", idx,
                        f"heading body-marker '{marker}' at pos {pos} in: {heading_text[:60]}"))
                    break

    # ── T2 volume vs first-h3 drift ──
    # For each chunk that has a volume, find the first h2/h3 in content.
    # If that heading is a "Letter title" (e.g. 「瑪忒特致狄奧格尼特斯書信」),
    # it should be similar to the volume name 「致丟格那妥書」.
    # We only flag when similarity is < 0.4 (very different), to avoid
    # noisy false positives on chapter headings.
    for c in chunks:
        idx = c.get("chunk_index")
        vol = (c.get("volume") or "").strip()
        if not vol:
            continue
        content = c.get("content") or ""
        # First non-chapter heading inside the chunk = the letter title.
        # The consolidator emits the letter title as h3 (### ...), then
        # individual chapters as h4 (#### 第一章—...). So we want the
        # first h3 that ISN'T a chapter heading (doesn't match 第X章).
        first_letter_title = None
        for m in re.finditer(r"^#{2,3}\s+(.+?)\s*$", content, re.M):
            t = strip_md(m.group(1))
            if not re.match(r"第[一二三四五六七八九十百千零0-9]+章", t):
                first_letter_title = t
                break
        if not first_letter_title:
            continue
        first_h2 = first_letter_title
        # Drop trailing chapter-range tag from volume if any
        vol_core = re.sub(r"\s*第\d+(-\d+)?章\s*$", "", vol)
        if similar(first_h2, vol_core) < 0.4 and len(first_h2) > 4:
            issues.append(Issue("T2", "WARN", idx,
                f"first H2 '{first_h2}' diverges from volume '{vol_core}'"))

    # ── T3 chapter_path appears again in body ──
    # When chapter_path is also a heading inside the body it's harmless
    # (that's expected). We only flag when the chapter_path is found in a
    # *paragraph* line of the content — that means the consolidator pulled
    # a body sentence up as a heading and the original sits stuck in prose.
    # Implementation kept loose for now.
    # (No T3 emitted by default; placeholder for later expansion.)

    # ── T4 chapter_path control chars ──
    for c in chunks:
        idx = c.get("chunk_index")
        cp = c.get("chapter_path", "")
        if BAD_CP_CHARS.search(cp):
            issues.append(Issue("T4", "WARN", idx,
                f"chapter_path has markdown/footnote chars: {cp}"))

    # ── T5 volume re-entry ──
    # For each volume name, record the chunk_index span where it appears.
    # If indices are non-contiguous (e.g. 14-16 then 96 again), that's a
    # split / orphan attachment.
    by_vol: dict[str, list[int]] = defaultdict(list)
    for c in chunks:
        vol = c.get("volume")
        if not vol:
            continue
        by_vol[vol].append(c.get("chunk_index"))
    for vol, idxs in by_vol.items():
        if len(idxs) < 2:
            continue
        idxs_sorted = sorted(idxs)
        # Detect gaps: a gap of >2 between consecutive entries is suspicious
        # (1 means contiguous; 2 tolerates a single interleaved divider).
        for a, b in zip(idxs_sorted, idxs_sorted[1:]):
            if b - a > 2:
                issues.append(Issue("T5", "WARN", b,
                    f"volume '{vol}' re-enters at {b} after gap (last seen {a})"))
                break

    # ── T6 orphan index page ──
    for c in chunks:
        idx = c.get("chunk_index")
        cp = c.get("chapter_path", "")
        vol = c.get("volume", "")
        if INDEX_PATH_RE.search(cp) and not INDEX_VOLUME_RE.search(vol or ""):
            # 「目錄」也算 — front matter where volume is None is OK
            if vol:
                issues.append(Issue("T6", "WARN", idx,
                    f"index-like chapter_path '{cp}' attached to volume '{vol}'"))

    # ── T7 cover / preface naming ──
    if chunks:
        cp0 = chunks[0].get("chapter_path", "")
        if cp0 not in FRONT_MATTER_OK_CHUNK0:
            issues.append(Issue("T7", "WARN", 0,
                f"chunk 0 chapter_path is '{cp0}', expected one of {FRONT_MATTER_OK_CHUNK0}"))
    if len(chunks) > 1:
        cp1 = chunks[1].get("chapter_path", "")
        if cp1 not in FRONT_MATTER_OK_CHUNK1:
            issues.append(Issue("T7", "INFO", 1,
                f"chunk 1 chapter_path is '{cp1}', expected one of {FRONT_MATTER_OK_CHUNK1}"))

    # ── T9 cross-work bleed (NCX-driven, English-only) ──
    # NCX is the authoritative TOC. For each chunk, the consolidator
    # stamped `title_en` with the NCX letter label this chunk represents.
    # For each h3 in source_text, find which NCX entry it points to via
    # fuzzy substring match — if that entry's underlying letter title
    # disagrees with the chunk's `title_en`, content from another work
    # has been packaged here (CCEL EPUB common layout quirk).
    #
    # All matching is English-only so we don't depend on the brittle
    # LETTER_CN_LABELS Chinese-name table.
    book = fetch_book(ebook_id)
    ncx_index: list[dict] = []
    if book and find_epub:
        try:
            ep = find_epub(book)
            ncx_index = build_ncx_index(ep)
        except Exception:
            ncx_index = []
    def _entry_parent(letter_norm: str) -> Optional[str]:
        """Find which NCX parent_label owns this normalized letter."""
        for e in ncx_index:
            if e["en_letter_norm"] == letter_norm:
                return e["parent"].upper()
        # Looser: token-set match
        toks = set(t for t in re.split(r"\W+", letter_norm) if len(t) >= 3)
        if not toks:
            return None
        for e in ncx_index:
            etoks = set(t for t in re.split(r"\W+", e["en_letter_norm"]) if len(t) >= 3)
            if etoks and len(toks & etoks) / max(len(toks | etoks), 1) >= 0.6:
                return e["parent"].upper()
        return None

    if ncx_index:
        for c in chunks:
            idx = c.get("chunk_index")
            # Only check consolidated letter pages — front matter and
            # back-matter (chunk_type='chapter') don't represent any
            # specific letter, so cross-bleed comparison is meaningless.
            if c.get("chunk_type") != "page":
                continue
            chunk_title_en = (c.get("title_en") or "").strip()
            if not chunk_title_en:
                continue
            # title_en may be a CCEL filename ('anf02.iv.ii.ii.xxxi.html') rather
            # than a letter title. Resolve it to its owning NCX letter by longest
            # file-stem prefix so the comparison below isn't junk-vs-letter.
            chunk_entry = None
            if re.search(r"\.x?html?$", chunk_title_en.lower()):
                cstem = re.sub(r"\.x?html?$", "", chunk_title_en.split("/")[-1].strip().lower())
                best_len = 0
                for e in ncx_index:
                    for st in e.get("file_stems", ()):  # exact or dotted-prefix
                        if (cstem == st or cstem.startswith(st + ".")) and len(st) > best_len:
                            chunk_entry, best_len = e, len(st)
            if chunk_entry:
                chunk_letter_norm = chunk_entry["en_letter_norm"]
                chunk_parent = chunk_entry["parent"].upper()
            else:
                chunk_letter_norm = normalize_heading(chunk_title_en)
                chunk_parent = _entry_parent(chunk_letter_norm)
            # If we can't pin the chunk to a filename-resolved letter NOR to an
            # NCX parent, its title_en is a bare label (work name / chapter
            # title) and the English letter comparison below is unreliable —
            # it produces false 'bleeds' for a work's own title appearing as an
            # h3 on its own page. Skip: no identity → no defensible verdict.
            if not chunk_entry and not chunk_parent:
                continue
            src = c.get("source_text") or ""
            if not src:
                continue
            # h3 may wrap across multiple lines in CCEL EPUBs (e.g.
            # 「### Introductory Note to the Epistle of\nMathetes to
            # Diognetus」). Consume until next blank line or next heading
            # so the FULL title sits in group 1, then collapse internal
            # whitespace for attribution.
            heading_re = re.compile(
                r"^###[ \t]+([\s\S]+?)(?=\n[ \t]*\n|\n#|\Z)", re.M)
            seen_headings: set[str] = set()
            for m in heading_re.finditer(src):
                raw = m.group(1)
                heading = re.sub(r"\s+", " ", raw).strip()
                if len(heading) < 4:
                    continue
                h_norm = normalize_heading(heading)
                if h_norm in seen_headings:
                    continue
                seen_headings.add(h_norm)
                # Back-matter index section headers (e.g.「### THEOPHILUS.」
                # immediately followed by「#### INDEX OF SUBJECTS.」) are the
                # per-author subject-index dividers folded into the last
                # content page — NOT a content bleed. Skip when an index
                # marker sits right after the heading.
                tail = src[m.end():m.end() + 80]
                if re.search(r"index of subjects|general index|index of|印書頁碼索引|主題索引", tail, re.I):
                    continue
                attributed = attribute_heading(heading, ncx_index)
                if attributed is None:
                    continue
                # Compare attributed letter to chunk's own letter. NCX
                # entries and consolidator-stamped title_en are seldom
                # character-identical — NCX may say 「First Epistle of
                # Clement to the Corinthians」 while title_en is the
                # shorter 「First Epistle to the Corinthians」. Use a
                # token-set overlap (Jaccard) — if ≥0.6 tokens in common
                # they refer to the same letter.
                a = attributed["en_letter_norm"]
                b = chunk_letter_norm
                a_toks = set(t for t in re.split(r"\W+", a) if len(t) >= 3)
                b_toks = set(t for t in re.split(r"\W+", b) if len(t) >= 3)
                overlap = len(a_toks & b_toks) / max(len(a_toks | b_toks), 1)
                same_letter = (overlap >= 0.6) or (a in b) or (b in a)
                # Same-parent intros (e.g.「Introductory Note to the
                # Epistles of Ignatius」inside any Ignatius letter chunk)
                # are not cross-bleeds — NCX intros legitimately fold
                # into the first letter of their parent group.
                if not same_letter and chunk_parent and attributed.get("parent","").upper() == chunk_parent:
                    same_letter = True
                if not same_letter:
                    issues.append(Issue("T9", "WARN", idx,
                        f"source h3 '{heading[:60]}' attributes to NCX "
                        f"letter '{a}' but chunk title_en is '{b}' "
                        f"(cross-work bleed)"))

    # ── T10 footnote ref vs body mismatch ──
    # Within a single chunk's content, the body's `[^N]` refs and the
    # footnote section's `(N) ...` items should have the same set of
    # numbers. A diff means LLM dropped an item or invented a ref.
    REF_RE = re.compile(r"\[\^(\d+)\]")
    FN_BODY_RE = re.compile(r"^\((\d+)\)\s", re.M)
    for c in chunks:
        idx = c.get("chunk_index")
        content = c.get("content") or ""
        if not content:
            continue
        ref_nums = set(int(n) for n in REF_RE.findall(content))
        fn_nums = set(int(n) for n in FN_BODY_RE.findall(content))
        if not ref_nums and not fn_nums:
            continue
        only_in_refs = ref_nums - fn_nums
        only_in_body = fn_nums - ref_nums
        if only_in_refs:
            issues.append(Issue("T10", "WARN", idx,
                f"{len(only_in_refs)} refs without body: {sorted(only_in_refs)[:5]}"))
        if only_in_body:
            # Footnotes-without-refs are common and benign (translator
            # comments etc.), so only report when count > 3.
            if len(only_in_body) > 3:
                issues.append(Issue("T10", "INFO", idx,
                    f"{len(only_in_body)} fn body without refs: {sorted(only_in_body)[:5]}"))

    # ── T11 bilingual paragraph drift ──
    # For each chunk with both source_text and content, count blank-
    # line-delimited paragraphs on each side. Bilingual reader pairs
    # row-by-row, so a count drift > 25% means the right column won't
    # line up with the left.
    for c in chunks:
        idx = c.get("chunk_index")
        zh = c.get("content") or ""
        en = c.get("source_text") or ""
        if not zh or not en:
            continue
        drift = paragraph_drift(zh, en)
        if drift is None:
            continue  # too short to meaningfully measure
        if drift > BILINGUAL_DRIFT_RATIO:
            issues.append(Issue("T11", "INFO", idx,
                f"paragraph count drift: ZH={para_count(zh)} vs EN={para_count(en)} ({drift*100:.0f}%)"))

    return issues


def report(ebook_id: str, issues: list[Issue], title: str = "") -> tuple[int, int]:
    print(f"\n=== {title or ebook_id} ===")
    if not issues:
        print("  ✓ scan clean")
        return 0, 0
    by_rule = defaultdict(list)
    for i in issues:
        by_rule[i.rule].append(i)
    warn = info = 0
    for rule in sorted(by_rule):
        lst = by_rule[rule]
        sev = lst[0].severity
        sym = "⚠" if sev == "WARN" else "i"
        print(f"\n  {sym} [{rule}] {len(lst)} issue{'s' if len(lst)>1 else ''}")
        for it in lst[:8]:
            loc = f"chunk {it.chunk_index}" if it.chunk_index is not None else "book"
            print(f"    · {loc}: {it.message}")
        if len(lst) > 8:
            print(f"    · ... +{len(lst)-8} more")
        if sev == "WARN":
            warn += len(lst)
        else:
            info += len(lst)
    print(f"\n  Totals: {warn} WARN · {info} INFO")
    return warn, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ebook_id", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--gate", action="store_true",
                    help="逐段對照 gate — list chunks whose bilingual alignment "
                         "drifts past the threshold (re-translation worklist). "
                         "JSONL-only, no DB needed.")
    ap.add_argument("--gate-threshold", type=float, default=BILINGUAL_DRIFT_RATIO,
                    help=f"alignment drift threshold (default {BILINGUAL_DRIFT_RATIO})")
    args = ap.parse_args()

    if args.gate:
        ids = ([jp.stem for jp in sorted(CHUNKS_DIR.glob("*.jsonl"))]
               if args.all else [args.ebook_id])
        if not ids or ids == [None]:
            sys.exit("usage: scan_translated_book.py <ebook_id> --gate [--gate-threshold R]")
        report_obj = []
        for eid in ids:
            chunks = load_jsonl(eid)
            if not chunks:
                continue
            flagged = alignment_gate(chunks, args.gate_threshold)
            if args.json:
                report_obj.append({"ebook_id": eid, "flagged": flagged})
            elif flagged:
                print(f"\n=== {eid} — {len(flagged)} chunk(s) need re-translation "
                      f"(drift > {args.gate_threshold}) ===")
                for f in flagged[:30]:
                    print(f"  · chunk {f['chunk_index']} [{f['chapter_path']}]: "
                          f"ZH={f['zh_paras']} vs EN={f['en_paras']} paras "
                          f"(drift {f['drift']})")
                if len(flagged) > 30:
                    print(f"  · ... +{len(flagged)-30} more")
        if args.json:
            print(json.dumps(report_obj, ensure_ascii=False, indent=2))
        return

    if args.all:
        # Scan every ebook whose JSONL exists locally
        jsonls = sorted(CHUNKS_DIR.glob("*.jsonl"))
        all_results = []
        for jp in jsonls:
            eid = jp.stem
            book = fetch_book(eid)
            title = book["title"] if book else eid
            issues = scan(eid)
            if args.json:
                all_results.append({
                    "ebook_id": eid, "title": title,
                    "issues": [i.to_dict() for i in issues],
                })
            else:
                report(eid, issues, title)
        if args.json:
            print(json.dumps(all_results, ensure_ascii=False, indent=2))
        return

    if not args.ebook_id:
        sys.exit("usage: scan_translated_book.py <ebook_id> | --all")
    book = fetch_book(args.ebook_id)
    title = book["title"] if book else args.ebook_id
    issues = scan(args.ebook_id)
    if args.json:
        print(json.dumps({
            "ebook_id": args.ebook_id, "title": title,
            "issues": [i.to_dict() for i in issues],
        }, ensure_ascii=False, indent=2))
        return
    report(args.ebook_id, issues, title)


if __name__ == "__main__":
    main()
