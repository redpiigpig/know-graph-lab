"""Pure parsing / dedup / alignment helpers for the /gnostic (諾斯底主義文獻)
ingestion pipeline.

Source = The Gnostic Society Library (http://gnosis.org/library.html). English
text is public-domain (Mead 1900s et al.); Chinese is our own per-paragraph
translation. Sections align EN↔ZH by order_index.

This module is import-safe with no network / no heavy deps on the pure path
(bs4 is lazy-imported inside the HTML parsers). Tested by
scripts/tests/test_gnostic_library.py.
"""
from __future__ import annotations

import re
from typing import Iterable
from urllib.parse import urljoin

GNOSIS_ROOT = "http://gnosis.org/"


# ── Taxonomy: the 13 gnosis.org library sections we mirror as sub-categories ──
# dedup_against_existing=True → before ingesting a doc, check it isn't already in
# /apocrypha or /fathers (per user: skip overlaps, don't re-transcribe).
CATEGORIES: list[dict] = [
    {"key": "nag_hammadi",        "label_zh": "拿戈瑪第經集",       "label_en": "Nag Hammadi Library",        "index_path": "naghamm/nhl.html",                 "display_order": 10, "dedup_against_existing": False},
    {"key": "gnostic_scriptures", "label_zh": "古典諾斯底經典",     "label_en": "Classic Gnostic Scriptures", "index_path": "library/gs.htm",                    "display_order": 20, "dedup_against_existing": False},
    {"key": "valentinus",         "label_zh": "瓦倫廷與其傳統",     "label_en": "Valentinus & His Tradition", "index_path": "library/valentinus/index.html",     "display_order": 30, "dedup_against_existing": False},
    {"key": "hermetica",          "label_zh": "赫密士文集",         "label_en": "Corpus Hermeticum",          "index_path": "library/hermet.htm",                "display_order": 40, "dedup_against_existing": False},
    {"key": "mead",               "label_zh": "G.R.S. Mead 文集",   "label_en": "GRS Mead Collection",        "index_path": "library/grs-mead/mead_index.htm",   "display_order": 50, "dedup_against_existing": False},
    {"key": "manichaean",         "label_zh": "摩尼教文獻",         "label_en": "Manichaean Writings",        "index_path": "library/manis.htm",                 "display_order": 60, "dedup_against_existing": False},
    {"key": "mandaean",           "label_zh": "曼達教文獻",         "label_en": "Mandaean Writings",          "index_path": "library/mand.htm",                  "display_order": 70, "dedup_against_existing": False},
    {"key": "cathar",             "label_zh": "卡特里派文獻",       "label_en": "Cathar Writings",            "index_path": "library/cathtx.htm",                "display_order": 80, "dedup_against_existing": False},
    {"key": "polemics",           "label_zh": "教父駁斥諾斯底文獻", "label_en": "Patristic Polemical Works",  "index_path": "library/polem.htm",                 "display_order": 90, "dedup_against_existing": True},
    {"key": "christian_apocrypha","label_zh": "基督教偽典",         "label_en": "Christian Apocrypha",        "index_path": "library/cac.htm",                   "display_order": 100, "dedup_against_existing": True},
    {"key": "alchemical",         "label_zh": "煉金術文獻",         "label_en": "Alchemical Writings",        "index_path": "library/alch.htm",                  "display_order": 110, "dedup_against_existing": False},
    {"key": "modern",             "label_zh": "現代文獻與近代學術", "label_en": "Modern Texts & Scholarship", "index_path": "library/modern.htm",                "display_order": 120, "dedup_against_existing": False},
    {"key": "dead_sea",           "label_zh": "死海古卷",           "label_en": "Dead Sea Scrolls",           "index_path": "library/dss/dss.htm",               "display_order": 130, "dedup_against_existing": True},
]

CATEGORY_BY_KEY = {c["key"]: c for c in CATEGORIES}


# ── Slug + dedup key ─────────────────────────────────────────────────────────
_LEADING_THE = re.compile(r"^the\s+", re.I)
_PARENS = re.compile(r"\([^)]*\)")
_NONWORD = re.compile(r"[^a-z0-9]+")


def _strip_title(title: str) -> str:
    """Lowercase, drop a leading 'The ', drop parenthetical credits/aliases."""
    t = title.strip()
    t = _PARENS.sub(" ", t)
    t = _LEADING_THE.sub("", t.strip())
    return t.strip().lower()


_SLUG_MAX = 110  # gnostic_documents.slug is VARCHAR(120); leave headroom


def make_slug(title: str) -> str:
    """URL-safe kebab slug. Drops leading 'The', parentheticals, punctuation;
    caps length at a hyphen boundary so it fits the slug PK column."""
    t = _strip_title(title)
    s = _NONWORD.sub("-", t).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    if len(s) > _SLUG_MAX:
        s = s[:_SLUG_MAX].rsplit("-", 1)[0]  # cut back to last full word
    return s.strip("-")


def normalize_title(title: str) -> str:
    """Dedup key: leading 'The' + parentheticals + punctuation removed, spaces
    collapsed. normalize('The Gospel of Thomas') == normalize('Gospel of
    Thomas (Lambdin)')."""
    t = _strip_title(title)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def is_duplicate(title: str, existing: Iterable[str]) -> bool:
    """True if `title` matches (by normalized key) any title in `existing`
    (e.g. apocrypha.title_en / father_works.title_en already on the site)."""
    key = normalize_title(title)
    return any(key == normalize_title(e) for e in existing)


# ── HTML: category index page → doc links ────────────────────────────────────
# Links that are site navigation / boilerplate, never document content.
_NAV_BLOCKLIST = {
    "welcome.html", "eghome.htm", "bookstore1.htm", "lectures.html",
    "search_form.html", "library.html", "ecindex.htm", "index.html",
}
_NAV_TEXT_BLOCKLIST = {
    "search", "bookstore", "home", "top", "back", "next", "previous",
    "gnosis archive", "library", "web lectures", "the gnostic society",
    "contact", "about",
}


# Non-document asset extensions (audio / image / archive / pdf scans).
_ASSET_EXT = (".mp3", ".mp4", ".mov", ".m4a", ".wav", ".pdf", ".jpg", ".jpeg",
              ".png", ".gif", ".zip", ".doc", ".docx")
# Basenames of the 13 category index pages — cross-links between sections, not docs.
_CATEGORY_INDEX_TAILS = {c["index_path"].rstrip("/").rsplit("/", 1)[-1] for c in CATEGORIES}
_AUX_INDEX_TAILS = {
    "nhl.html", "nhlalpha.html", "nhlcodex.html", "nhlintro.html", "nhsearch.html",
    "gnostsoc.htm", "ecindex.htm",
}


def _is_nav_link(href: str, text: str) -> bool:
    h = href.strip().lower()
    if not h or h.startswith(("#", "mailto:", "javascript:")):
        return True
    path = h.split("?", 1)[0].split("#", 1)[0]
    if path.endswith(_ASSET_EXT):
        return True
    tail = path.rstrip("/").rsplit("/", 1)[-1]
    if tail in _NAV_BLOCKLIST or tail in _CATEGORY_INDEX_TAILS or tail in _AUX_INDEX_TAILS:
        return True
    if " ".join(text.split()).lower() in _NAV_TEXT_BLOCKLIST:
        return True
    # external links off gnosis.org are not our documents
    if h.startswith(("http://", "https://")) and "gnosis.org" not in h:
        return True
    return len(text.strip()) <= 2


def parse_category_index(html: str, base_path: str = "library/library.html") -> list[dict]:
    """A gnosis.org category page → [{title, url}] of document links.

    base_path is the category page's own path relative to gnosis.org root, used
    to resolve relative hrefs. Nav / boilerplate / external links are dropped;
    near-duplicate titles (same normalized key) are de-duplicated keeping the
    first occurrence.
    """
    from bs4 import BeautifulSoup

    base_url = urljoin(GNOSIS_ROOT, base_path)
    soup = BeautifulSoup(html, "html.parser")
    out: list[dict] = []
    seen: set[str] = set()
    for a in soup.find_all("a"):
        href = a.get("href") or ""
        text = " ".join(a.get_text(" ", strip=True).split())  # collapse internal whitespace
        if _is_nav_link(href, text):
            continue
        key = normalize_title(text)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append({"title": text, "url": urljoin(base_url, href)})
    return out


# ── HTML: document page → English paragraph sections ─────────────────────────
_DOC_DROP_PARENTS = {"script", "style", "head"}
_DOC_BLOCK = {"p", "blockquote", "li"}
# Nav/footer/front-matter chrome that rides inside <p> on gnosis.org pages.
_DOC_BOILERPLATE = re.compile(
    r"^(return to|back to|copyright|the gnostic society|gnostic society library"
    r"|home\b|library\b|index\b|next\b|previous\b|translated by|translation by"
    r"|the nag hammadi library|presented in the gnostic|under license|by permission"
    r"|visit the|see also|reprinted from|from the|edited by|prepared by"
    r"|this (original )?(translation|text|edition))",
    re.I,
)
_HAS_LETTER_RE = re.compile(r"[A-Za-zÀ-ɏ]")


_BR_RE = re.compile(r"<br\s*/?>", re.I)
_DOC_BLOCK_LIST = list(_DOC_BLOCK)


def _doc_soup(html: str):
    """Parse a document page, preferring an HTML5-compliant tree builder.

    Many gnosis.org hymn pages (Manichaean / Mandaean) ship ancient HTML with
    UNCLOSED <p> tags. HTML5 auto-closes a <p> at the next <p>; Python's stdlib
    'html.parser' instead NESTS them, so every content <p> looked like it
    "contained another block" and was dropped as a non-leaf → 0 sections. lxml
    follows the HTML5 rule and reads them as siblings. Fall back to html.parser
    when lxml isn't installed (behaviour unchanged for well-formed pages).
    """
    from bs4 import BeautifulSoup
    try:
        return BeautifulSoup(html, "lxml")
    except Exception:
        return BeautifulSoup(html, "html.parser")


def _clean_para(text: str) -> str:
    t = text.replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", t).strip()


def _block_paragraphs(el) -> list[str]:
    """Split one leaf block's inner HTML into paragraphs.

    gnosis.org puts whole treatises in a single <p>/<blockquote> with lines
    broken by <br> and paragraphs separated by a blank `&nbsp;<br>` line. So:
    <br> → newline, strip tags, then group runs of non-blank lines into one
    paragraph (blank line = boundary). Lines within a paragraph join by space.
    """
    from bs4 import BeautifulSoup

    # <br> → sentinel so only real <br> line breaks count; source newlines /
    # indentation inside a segment are collapsed to single spaces.
    inner = _BR_RE.sub("\x00", el.decode_contents())
    text = BeautifulSoup(inner, "html.parser").get_text().replace("\xa0", " ")
    segs = [" ".join(seg.split()) for seg in text.split("\x00")]

    paras: list[str] = []
    cur: list[str] = []
    for seg in segs:
        if not seg:                       # blank <br> line = paragraph boundary
            if cur:
                paras.append(_clean_para(" ".join(cur))); cur = []
        else:
            cur.append(seg)
    if cur:
        paras.append(_clean_para(" ".join(cur)))
    return [p for p in paras
            if p and _HAS_LETTER_RE.search(p) and not _DOC_BOILERPLATE.match(p)]


def parse_document(html: str) -> dict:
    """A gnosis.org treatise page → {title, sections: [str, ...]}.

    title comes from <h1>/<h3> else <title> (site suffix trimmed). sections are
    the leaf block paragraphs (<p>/<blockquote>/<li>), with <br>-delimited
    paragraphs split out and empty / &nbsp;-only / boilerplate blocks dropped.
    A block that contains another block is not a leaf (avoids double-counting
    nested <blockquote>).
    """
    soup = _doc_soup(html)

    title = ""
    head = soup.find(["h1", "h2", "h3"])
    if head:
        title = " ".join(head.get_text(" ", strip=True).split())
    if not title and soup.title:
        title = re.split(r"\s+[-–|]\s+", soup.title.get_text(" ", strip=True))[0].strip()

    root = soup.body or soup
    sections: list[str] = []
    for el in root.find_all(_DOC_BLOCK):
        if any(p.name in _DOC_DROP_PARENTS for p in el.parents):
            continue
        if el.find(_DOC_BLOCK_LIST):   # not a leaf — its inner blocks handle the text
            continue
        sections.extend(_block_paragraphs(el))
    return {"title": title, "sections": sections}


# ── Alignment gate (EN ↔ ZH per paragraph) ───────────────────────────────────
def align_ok(en: list, zh: list) -> bool:
    """The /gnostic invariant: one ZH paragraph per EN paragraph."""
    return len(en) == len(zh)


def assert_aligned(en: list, zh: list) -> None:
    if not align_ok(en, zh):
        raise ValueError(
            f"section count mismatch: {len(en)} EN vs {len(zh)} ZH "
            "(every English paragraph needs exactly one Chinese paragraph)"
        )


# ── Translation quality gate ──────────────────────────────────────────────────
# assert_aligned only checks COUNT (en==zh). It cannot catch the real 2026-06-06
# failure mode: a short EN heading hallucinated into a long fabricated ZH essay
# (count still matched, so it passed). This gate is the missing SOURCE↔OUTPUT
# invariant — run it on every paragraph at translation time, not just post-hoc.
#
# Engine meta-commentary / refusal / note markers that leak into ZH content,
# anchored near the START (leaks lead the output) and bound to task-referencing
# context so legitimate first-person prose ("我無法保持貞潔") is NOT flagged.
META_LEAD_RE = re.compile(
    r"^[\s「『（(]*("
    r"我(?:已)?準備好(?:接收|進行|翻譯|為您)|我注意到您|"
    r"我(?:無法|不能|沒辦法)(?:完成|識別|確定|判斷|提供(?:翻譯|準確)|翻譯這|處理這|"
    r"直接(?:轉|翻)譯|為您翻譯)|"
    r"無法(?:識別|確定|判斷)(?:這(?:個|段)|您|此|原文|出)|"
    r"我(?:必須|需要)坦誠(?:告知)?|我感謝您的(?:信任|請求)|"
    r"作為(?:一個|一名)?(?:AI|人工智慧|語言模型)|很抱歉(?:，|,)?我|"
    r"請(?:您)?提供(?:要|您要|完整|您想|需要)|您提供的(?:英文|文本|文段|內容|片段|文字)|"
    r"你提供的(?:英文|文本|文段|內容|片段|文字)|這(?:個|段)文(?:本|字)(?:並非|不是|看起來)|"
    r"根據(?:著作權|版權)|基於(?:著作權|版權)|"
    r"以下(?:是|為).{0,15}(?:翻譯|譯文)|這是.{0,12}的(?:繁體中文)?翻譯|"
    r"此處「.{0,20}」(?:應譯|建議)|建議(?:保留|譯為|使用「)|"
    r"\*\*原文|\*\*翻譯|原文：|翻譯：|逐字翻譯[：:]|繁體中文翻譯："
    r")")

# Word-by-word English gloss leak ("我（I）是（am）那（the）光（Light）"): common
# ENGLISH FUNCTION WORDS bracketed inline. Must NOT match legitimate scholarly
# transliteration annotations like （gnosis）（batos）（syzygy）（ruha）.
WORD_GLOSS_RE = re.compile(
    r"（(?:the|is|am|are|and|of|to|in|that|which|a|an|he|she|it|was|were|be|"
    r"for|with|i|you|they|we|his|her|this|these|those|from|by|on|at|as|but|"
    r"or|not|all|out|into)）", re.I)


def latin_ratio(s: str) -> float:
    """Fraction of characters that are Latin letters (untranslated signal)."""
    if not s:
        return 0.0
    return len(re.sub(r"[^A-Za-z]", "", s)) / len(s)


# Distinctive 文言 (classical Chinese) sentence particles that the user-mandated
# 白話/《和合本》 register must NOT use (和合本 says 「名叫」「說」, never 名曰／焉／矣).
# Only HIGH-PRECISION markers — 之／其／乃 are excluded (they occur in 白話 too).
WENYAN_RE = re.compile(r"名曰|曰[：「『]|[^。！？\s]焉[。，、！]|矣[。，！]|哉[！。]")


def classify_translation(en: str, zh: str) -> str | None:
    """Return a failure-mode tag if the ZH translation of EN is bad, else None.

    Tags: empty / meta_leak / word_gloss / untranslated / halluc_heading / wenyan.
    halluc_heading = a short EN source blown up into a long ZH essay (the
    fabrication signal); the real body, if any, lives in an adjacent section.
    wenyan = drifted into classical Chinese (register violation; 白話/和合本 only).
    """
    en, zh = (en or "").strip(), (zh or "").strip()
    if not zh:
        return "empty"
    if META_LEAD_RE.match(zh):
        return "meta_leak"
    if len(WORD_GLOSS_RE.findall(zh)) >= 3:
        return "word_gloss"
    if len(zh) > 40 and latin_ratio(zh) > 0.5:
        return "untranslated"
    if 0 < len(en) < 70 and len(zh) >= 2.5 * len(en) and latin_ratio(zh) <= 0.5:
        return "halluc_heading"
    if WENYAN_RE.search(zh):
        return "wenyan"
    return None
