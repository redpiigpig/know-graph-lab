"""Pure parsing / key / alignment helpers for the /works 研究回顧 (literature
review) ingestion pipeline.

A 研究回顧 is a structured 文獻綜述 attached to a 論文寫作 project (e.g. the
八敬法 review under 昭慧法師的戒律學思想與實踐). Each bibliography entry has
metadata + abstract from the综述 report; for the openly-available ones we fetch
the full text, segment it into paragraphs, translate each into 繁中, and store
原文↔中譯 aligned by order_index — mirroring /gnostic (gnostic_documents /
gnostic_sections + the EN↔ZH 1:1 gate).

Import-safe: no env reads, no network, no heavy deps on the pure path (bs4 is
lazy-imported inside the HTML parser). Tested by
scripts/tests/test_lit_review.py.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Optional


# ── Themes: the 4 thematic section headers in the八敬法 report ────────────────
# Entries are grouped under these `#` headers; each entry inherits its theme.
THEMES: list[dict] = [
    {"key": "textual",     "label": "文本考證與來源研究", "order": 10},
    {"key": "women",       "label": "女性議題與比丘尼制度", "order": 20},
    {"key": "interpretive","label": "詮釋爭論與真偽問題",   "order": 30},
    {"key": "cross",       "label": "跨傳統比較",           "order": 40},
]
THEME_LABELS = {t["label"] for t in THEMES}


# ── Doc-type sections: for a paper's *actual* 參考文獻 (works cited) ───────────
# The 4 THEMES above group a generated 文獻綜述 by subject matter. A paper's own
# bibliography is instead organised by document type (佛典 / 專書 / 期刊 …), the
# way it prints under 參考文獻. parse_review_report() recognises both header sets,
# so one project can carry a thematic survey AND the paper's real works-cited
# list side by side (each entry keeps the section header it sits under as theme).
DOC_TYPE_THEMES: list[dict] = [
    {"key": "canon",      "label": "佛典與檔案",       "order": 110},
    {"key": "books",      "label": "專書著作",         "order": 120},
    {"key": "journals",   "label": "期刊文章",         "order": 130},
    {"key": "chapters",   "label": "研討會與專書論文", "order": 140},
    {"key": "theses",     "label": "學位論文",         "order": 150},
    {"key": "press",      "label": "報刊與雜誌",       "order": 160},
    {"key": "web",        "label": "網路文章",         "order": 170},
]
DOC_TYPE_LABELS = {t["label"] for t in DOC_TYPE_THEMES}


# ── Supplement sections: extra reading recommended for an English-journal rewrite
# (theoretical framing + key English-language scholarship the original paper did
# not engage). Mostly copyright → seeded as 書目＋摘要＋連結 (fulltext_status
# 'unavailable'); they enrich the 研究回顧 without claiming a full-text translation.
SUPPLEMENT_THEMES: list[dict] = [
    {"key": "gender_theory", "label": "性別與佛教理論框架（英文改寫補充）", "order": 210},
    {"key": "taiwan_en",     "label": "台灣佛教與人間佛教（英文研究）",   "order": 220},
    {"key": "tw_field",      "label": "大專學佛運動與解嚴後台灣佛教（改寫補充）", "order": 230},
]
SUPPLEMENT_LABELS = {t["label"] for t in SUPPLEMENT_THEMES}


# ── Book-survey themes: thematic axes for a 專書 multi-language 研究回顧 ──────────
# A book project (kind='book', e.g.《當代的大愛道革命》) groups its survey by the
# book's own subject axes rather than the 4 八敬法 THEMES. Headers in the report
# may sit at any heading level (`##`), so parse_review_report matches SECTION_LABELS
# regardless of `#` depth.
BOOK_SURVEY_THEMES: list[dict] = [
    {"key": "humanistic", "label": "人間佛教思想與印順學脈絡", "order": 310},
    {"key": "gender",     "label": "性別平權與大愛道革命",     "order": 320},
    {"key": "engaged",    "label": "社會運動與入世佛教",       "order": 330},
    {"key": "meditation", "label": "禪觀修持與佛教養生",       "order": 340},
    {"key": "history",    "label": "史料與當代台灣佛教脈絡",   "order": 350},
    {"key": "dharmadrum", "label": "法鼓山與聖嚴法師人間佛教", "order": 360},
    {"key": "intellect",  "label": "佛教知識化、高教與電子佛典", "order": 370},
]
BOOK_SURVEY_LABELS = {t["label"] for t in BOOK_SURVEY_THEMES}


# ── Genesis-philosophy themes: the 4 research domains for each 創生哲學 volume's
# 參考資料庫 (per-volume reference DB, scoped by book_id). Every 創生哲學 卷 groups
# its 研究回顧 by these 4 domains; used to rewrite the volume against current research.
GENESIS_THEMES: list[dict] = [
    {"key": "science",    "label": "自然科學",   "order": 410},
    {"key": "psychology", "label": "心理學",     "order": 420},
    {"key": "philosophy", "label": "哲學",       "order": 430},
    {"key": "religion",   "label": "宗教與神話", "order": 440},
]
GENESIS_THEME_LABELS = {t["label"] for t in GENESIS_THEMES}


# ── 世界宗教文化導論（lecture, book_id 'WR1'）：八大界域框架的研究回顧主題軸。
# 對應講義章節：定義/靈性(1-2)、起源演化(3)、分類學與時代分期(4-5)、地理學方法論與
# 八大界域提出(6)、七至十四章八大界域巡禮、實踐儀式(15)、現代社會(16)、跨宗教對話(17)。
WORLD_RELIGIONS_THEMES: list[dict] = [
    {"key": "wr_theory",    "label": "宗教定義、神聖與宗教學理論",           "order": 510},
    {"key": "wr_evolution", "label": "宗教的起源、演化與認知科學",           "order": 520},
    {"key": "wr_method",    "label": "宗教分類學與宗教地理學方法論",         "order": 530},
    {"key": "wr_sphere1",   "label": "中央、東方與西方界域研究",             "order": 540},
    {"key": "wr_sphere2",   "label": "北方、南方、亞太、北美與拉美界域研究", "order": 550},
    {"key": "wr_ritual",    "label": "儀式、實踐與宗教現象學",               "order": 560},
    {"key": "wr_modernity", "label": "宗教、現代性與世俗化",                 "order": 570},
    {"key": "wr_dialogue",  "label": "全球化與跨宗教對話",                   "order": 580},
]
WORLD_RELIGIONS_LABELS = {t["label"] for t in WORLD_RELIGIONS_THEMES}


# ── 宗教系國文講義·漢字文學史（lecture, book_id 'SL1'）：以漢字書寫圈與宗教為軸的
# 文學史研究回顧主題軸。對應章節：框架(1)、文字學與神話卜辭(2-3)、經典正典化(4)、
# 佛典漢譯(5)、大藏經與六朝唐中古宗教文學(6-8)、講唱變文戲曲神魔小說(9-11)、
# 東亞漢文學日韓越台(12-15)、聖經漢譯漢語神學與近代轉型(16-17)。
SINOGRAPHIC_THEMES: list[dict] = [
    {"key": "sl_frame",     "label": "漢字書寫圈與文學史框架方法論", "order": 610},
    {"key": "sl_philology", "label": "漢字文字學與經典的正典化",     "order": 620},
    {"key": "sl_transl",    "label": "佛典漢譯與翻譯史",             "order": 630},
    {"key": "sl_canon",     "label": "大藏經與中古宗教文學",         "order": 640},
    {"key": "sl_perform",   "label": "講唱、變文與宗教戲曲演藝",     "order": 650},
    {"key": "sl_eastasia",  "label": "東亞漢文學（日‧韓‧越‧台）",   "order": 660},
    {"key": "sl_bible",     "label": "聖經漢譯、漢語神學與近代轉型", "order": 670},
]
SINOGRAPHIC_LABELS = {t["label"] for t in SINOGRAPHIC_THEMES}

# Any header recognised as a section divider (theme assignment).
SECTION_LABELS = (THEME_LABELS | DOC_TYPE_LABELS | SUPPLEMENT_LABELS
                  | BOOK_SURVEY_LABELS | GENESIS_THEME_LABELS
                  | WORLD_RELIGIONS_LABELS | SINOGRAPHIC_LABELS)


# ── Language label (語言：英文) → ISO code ───────────────────────────────────
_LANG_MAP = {
    "英文": "en", "中文": "zh", "德文": "de", "法文": "fr", "日文": "ja",
    "拉丁文": "la", "希臘文": "grc", "西班牙文": "es", "義大利文": "it",
    "韓文": "ko", "越南文": "vi",
}


def detect_language(label: str) -> str:
    """語言 label → ISO code; unknown → 'other'.

    Tolerates a parenthetical qualifier after the base label, e.g.
    「中文（簡體，引用時轉繁）」→ zh — so a simplified-Chinese source is still
    recognised as zh (and thus gets no 逐段 full-text fetch).
    """
    base = re.split(r"[（(]", (label or "").strip(), maxsplit=1)[0].strip()
    return _LANG_MAP.get(base, "other")


# ── ref_key (stable, url-safe, per bibliography entry) ───────────────────────
_AUTHOR_BRACKETS = re.compile(r"^[【\[]\s*|\s*[】\]]$")
_REF_KEY_MAX = 100  # lit_review_entries.ref_key headroom


def _ascii_slug(text: str) -> str:
    """Transliterate to ASCII (ā→a), keep [a-z0-9], collapse to hyphens.
    Returns '' for pure-CJK input (no ASCII letters survive)."""
    if not text:
        return ""
    # NFKD splits accented letters into base + combining mark; drop the marks.
    decomposed = unicodedata.normalize("NFKD", text)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def make_ref_key(authors: str, year: Optional[int], title: str) -> str:
    """Stable url-safe key from author + year + title.

    English author → 'analayo-2016-the-foundation-history'.
    Same author+year is disambiguated by the title slug. Pure-CJK entries (no
    transliteration available) get a 'zh<hash>' token derived from author+title
    so they stay deterministic and distinct.
    """
    auth = _ascii_slug(_AUTHOR_BRACKETS.sub("", authors or ""))
    ttl = _ascii_slug(title or "")
    if not auth and not ttl:
        h = hashlib.md5(f"{authors}|{title}".encode("utf-8")).hexdigest()[:8]
        auth = f"zh{h}"
    parts = [p for p in (auth, str(year) if year else "", ttl) if p]
    key = re.sub(r"-{2,}", "-", "-".join(parts)).strip("-").lower()
    if len(key) > _REF_KEY_MAX:
        key = key[:_REF_KEY_MAX].rsplit("-", 1)[0]
    return key.strip("-")


# ── One entry block → structured dict ─────────────────────────────────────────
_RE_BRACKET = re.compile(r"[【\[]([^】\]]+)[】\]]")          # 【作者】
_RE_YEAR = re.compile(r"[（(]\s*(\d{4})\s*[)）]")            # （2016）
_RE_ANGLE = re.compile(r"〈([^〉]+)〉")                       # 〈篇名〉 (article)
_RE_DOUBLE = re.compile(r"《([^》]+)》")                      # 《書名/期刊》
_RE_FIELD = {
    "language": re.compile(r"^語言\s*[：:]\s*(.+)$", re.M),
    "dimension": re.compile(r"^所屬面向\s*[：:]\s*(.+)$", re.M),
    "stance": re.compile(r"^立場\s*[：:]\s*(.+)$", re.M),
    "abstract": re.compile(r"^摘要\s*[：:]\s*(.+)$", re.M),
}
# > **全文**：[label](url)   /   **連結**：[label](url)
_RE_FULLTEXT = re.compile(r"(?:全文|連結|PDF)\*{0,2}\s*[：:]\s*\[[^\]]*\]\((https?://[^)]+)\)")
_RE_ANY_MD_LINK = re.compile(r"\[[^\]]*\]\((https?://[^)]+)\)")


def parse_entry_block(block: str) -> dict:
    """One 【作者】（年）〈題〉，《刊》… block (+ 語言/所屬面向/立場/摘要/全文
    lines) → structured entry dict, with ref_key filled in.

    Article (〈題〉 present): title=〈〉, venue=first 《》.
    Book (no 〈〉): title=first 《》, venue=publisher tail of the first line.
    """
    block = block.strip()
    lines = [ln.rstrip() for ln in block.splitlines()]
    head = lines[0] if lines else ""

    m_auth = _RE_BRACKET.search(head)
    authors = m_auth.group(1).strip() if m_auth else ""

    m_year = _RE_YEAR.search(head)
    year = int(m_year.group(1)) if m_year else None

    m_angle = _RE_ANGLE.search(head)
    doubles = _RE_DOUBLE.findall(head)
    if m_angle:
        title = m_angle.group(1).strip()
        venue = doubles[0].strip() if doubles else ""
    elif doubles:
        title = doubles[0].strip()
        # venue = text after the 《title》, trimmed of trailing punctuation
        tail = head.split("》", 1)[1] if "》" in head else ""
        venue = re.sub(r"^[，,、\s]+", "", tail).rstrip("。 \t")
    else:
        # title-in-bracket fallback (e.g. an anonymous thesis): bracket = title
        title = authors
        authors = ""
        venue = re.sub(r"[【\[][^】\]]+[】\]]", "", head).strip("，,。 \t")

    def field(name: str) -> Optional[str]:
        m = _RE_FIELD[name].search(block)
        return m.group(1).strip() if m else None

    language = detect_language(field("language") or "")
    ft = _RE_FULLTEXT.search(block)
    if not ft:
        # any markdown link on a 全文/連結-ish line
        for ln in lines[1:]:
            if any(tag in ln for tag in ("全文", "連結", "PDF", "頁面")):
                m = _RE_ANY_MD_LINK.search(ln)
                if m:
                    ft = m
                    break

    return {
        "authors": authors,
        "year": year,
        "title": title,
        "venue": venue,
        "language": language,
        "dimension": field("dimension"),
        "stance": field("stance"),
        "abstract": field("abstract") or "",
        "fulltext_url": ft.group(1) if ft else None,
        "ref_key": make_ref_key(authors, year, title),
    }


# ── Whole 文獻綜述 markdown → {summary, gaps, entries} ────────────────────────
def parse_review_report(md: str) -> dict:
    """Parse the full literature-review markdown.

    - summary: the paragraph(s) under `## 執行摘要` (up to 主要研究空白).
    - gaps: the numbered list items under 主要研究空白包括：.
    - entries: every 【…】 block, each tagged with the `#theme` header it sits
      under (one of THEME_LABELS).
    """
    lines = md.splitlines()

    # summary: text between '## 執行摘要' and '主要研究空白'
    summary_parts: list[str] = []
    in_summary = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("## 執行摘要"):
            in_summary = True
            continue
        if in_summary:
            if s.startswith("主要研究空白") or (s.startswith("#") and not s.startswith("##")):
                break
            if s:
                summary_parts.append(s)
    summary = " ".join(summary_parts).strip()

    # gaps: numbered list after 主要研究空白包括：
    gaps: list[str] = []
    in_gaps = False
    for ln in lines:
        s = ln.strip()
        if s.startswith("主要研究空白"):
            in_gaps = True
            continue
        if in_gaps:
            if re.match(r"^\d+[.．、]", s):
                item = re.sub(r"^\d+[.．、]\s*", "", s)
                item = item.lstrip("#").strip()
                gaps.append(item)
            elif s.startswith("#") or s.startswith("【"):
                break

    # entries: split the document into theme sections, then into 【…】 blocks
    entries: list[dict] = []
    current_theme: Optional[str] = None
    block_lines: list[str] = []

    def flush():
        nonlocal block_lines
        if block_lines:
            text = "\n".join(block_lines).strip()
            if text.startswith(("【", "[")):
                e = parse_entry_block(text)
                e["theme"] = current_theme
                entries.append(e)
        block_lines = []

    for ln in lines:
        s = ln.strip()
        # a `#`-prefixed header (any level) that names one of our themes — a paper
        # report uses single `#`, a book survey may use `##`; both match by label.
        if s.startswith("#"):
            header = s.lstrip("#").strip()
            if header in SECTION_LABELS:
                flush()
                current_theme = header
                continue
        # a new entry begins at a line starting with 【 — flush the previous one
        if s.startswith("【") or s.startswith("["):
            flush()
            block_lines = [ln]
        elif block_lines:
            block_lines.append(ln)
    flush()

    return {"summary": summary, "gaps": gaps, "entries": entries}


# ── Fetched full text → paragraph list ────────────────────────────────────────
_HAS_LETTER = re.compile(r"[A-Za-zÀ-ɏͰ-Ͽ]")  # latin (+accents) or greek
# Running headers / journal chrome that show up as their own lines in PDF text.
_FULLTEXT_BOILERPLATE = re.compile(
    r"^(journal of buddhist ethics|buddhist studies review|the journal of"
    r"|wiener zeitschrift|sri lanka international journal|downloaded from"
    r"|issn |doi:|https?://|©|copyright|all rights reserved"
    r"|this work is licensed)",
    re.I,
)
_MIN_PARA_CHARS = 36       # shorter blocks need sentence punctuation to survive
_SENT_PUNCT = re.compile(r"[.。!！?？]")


def _dehyphenate(text: str) -> str:
    """Join words split across a line break by a trailing hyphen: 'inter-\\nnal'
    → 'internal'. Other newlines become spaces."""
    text = re.sub(r"([A-Za-zÀ-ɏ])-\s*\n\s*([a-zà-ÿ])", r"\1\2", text)
    return re.sub(r"\s*\n\s*", " ", text)


def _clean(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text.replace("\xa0", " ")).strip()


def _keep_para(p: str) -> bool:
    if not p or not _HAS_LETTER.search(p):
        return False
    if p.strip().isdigit():                       # bare page number
        return False
    if _FULLTEXT_BOILERPLATE.match(p.strip()):
        return False
    if len(p) < _MIN_PARA_CHARS and not _SENT_PUNCT.search(p):
        return False
    return True


def extract_paragraphs_from_text(text: str) -> list[str]:
    """PDF-extracted plain text → ordered content paragraphs.

    Paragraphs are blank-line separated; wrapped lines within a paragraph are
    joined (de-hyphenating across breaks). Page numbers, running headers,
    journal/DOI boilerplate, and too-short fragments are dropped.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n[ \t]*\n", text)
    out: list[str] = []
    for blk in blocks:
        para = _clean(_dehyphenate(blk))
        if _keep_para(para):
            out.append(para)
    return out


def extract_paragraphs_from_html(html: str) -> list[str]:
    """HTML full-text page → ordered content paragraphs (leaf <p>/<blockquote>/
    <li>), dropping script/style/nav chrome and empty/&nbsp;/boilerplate."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "head", "nav", "header", "footer"]):
        tag.decompose()
    out: list[str] = []
    blocks = {"p", "blockquote", "li"}
    for el in soup.find_all(blocks):
        if el.find(list(blocks)):     # not a leaf — inner blocks carry the text
            continue
        para = _clean(_dehyphenate(el.get_text("\n")))
        if _keep_para(para):
            out.append(para)
    return out


# ── Resumable translation ─────────────────────────────────────────────────────
def missing_indices(done: set, total: int) -> list[int]:
    """Ordered positions in range(total) not yet translated (not in `done`).
    Lets a quota-interrupted full-text translation resume paragraph-by-paragraph
    instead of restarting the whole (often 400+ paragraph) article."""
    return [i for i in range(total) if i not in done]


# ── Alignment gate (原文 ↔ 中譯, one ZH paragraph per source paragraph) ──────
def align_ok(src: list, zh: list) -> bool:
    return len(src) == len(zh)


def assert_aligned(src: list, zh: list) -> None:
    if not align_ok(src, zh):
        raise ValueError(
            f"section count mismatch: {len(src)} source vs {len(zh)} ZH "
            "(every source paragraph needs exactly one Chinese paragraph)"
        )
