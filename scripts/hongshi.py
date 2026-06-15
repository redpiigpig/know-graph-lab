# -*- coding: utf-8 -*-
"""Pure helpers for the 印順學派與弘誓研究資料 collection pipeline (test-first).

No network / env / heavy deps — just parsing, cleanup and OCR-decision logic that
the scraper/OCR drivers (`hongshi_*.py`, `hongshi_*.mjs`) rely on. The regex zoo
here is the part that actually bit us during scraping (3 magazine PDF filename
patterns; EDM old issues using .htm not .html; Cloudflare challenge pages captured
as content), so it lives in one tested place.

Tested by scripts/tests/test_hongshi.py.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple

# ── Cloudflare / boilerplate detection ──────────────────────────────────────────
# The site is behind Cloudflare; a not-yet-solved challenge renders this text. A
# captured challenge page must NEVER be stored as content.
_CHALLENGE = re.compile(r"正在執行安全驗證|安全驗證|惡意機器人|just a moment|請稍候|稍候", re.I)
# Site chrome that, if a scrape grabs the wrong container, shows up instead of body.
_NAV_HEAD = re.compile(r"最新消息|弘誓學團|護持捐款|友善連結")
# Contact-info footer stub returned by empty/non-existent log/EDM pages.
_FOOTER_STUB = re.compile(r"與我們聯繫|電\s*話\s*[:：]|傳\s*真\s*[:：]")

MIN_CONTENT_CHARS = 120  # shorter than this ⇒ stub / challenge / empty, not real content


def is_challenge_page(text: str) -> bool:
    """True if `text` is a Cloudflare challenge capture (must be rejected/retried)."""
    return bool(_CHALLENGE.search(text or ""))


def is_real_content(text: str) -> bool:
    """True if scraped text is genuine article content (not challenge / nav / stub)."""
    t = (text or "").strip()
    if len(t) < MIN_CONTENT_CHARS:
        return False
    if is_challenge_page(t):
        return False
    # a page that is *only* the contact footer (≈ empty issue) is not content
    if _FOOTER_STUB.search(t[:120]) and len(t) < 1000:
        return False
    return True


# ── 弘誓雙月刊 PDF filename / URL → issue number + date ──────────────────────────
# Three patterns seen in the wild, all must resolve to the same issue number:
#   hongshi-magazine-187-20240215.pdf   (standard, hyphenated, 8-digit AD date)
#   magazine190-20240815.pdf            (no hyphen after 'magazine')
#   180hongshi-1111216.pdf              (number-first, 'hongshi', ROC date)
#   弘誓雙月刊-188.pdf                    (our canonical local name)
_MAG_PATTERNS = (
    re.compile(r"弘誓雙月刊-(\d{1,3})(?:-p\d)?\.pdf$", re.I),
    re.compile(r"magazine-?(\d{1,3})\b", re.I),
    re.compile(r"(?:^|/)(\d{1,3})hongshi\b", re.I),
)
_AD_DATE = re.compile(r"(20\d{2})(\d{2})(\d{2})")


def magazine_issue(name_or_url: str) -> Optional[int]:
    """Issue number from any 弘誓雙月刊 PDF filename/URL, else None."""
    s = name_or_url or ""
    for pat in _MAG_PATTERNS:
        m = pat.search(s)
        if m:
            return int(m.group(1))
    return None


def magazine_ad_date(name_or_url: str) -> str:
    """AD date 'YYYY/MM' embedded in a standard filename, else '' (ROC dates skipped)."""
    m = _AD_DATE.search(name_or_url or "")
    return f"{m.group(1)}/{m.group(2)}" if m else ""


# ── 弘誓電子報 href → issue number ──────────────────────────────────────────────
# Old issues use .htm, recent use .html; spread across EDM/ and epaper/hongshi pic*/.
_EDM_HREF = re.compile(r"/(\d+)\.html?(?:[?#]|$)", re.I)


def edm_issue(href: str) -> Optional[int]:
    """Issue number from an EDM issue href (.htm or .html), else None.

    Only matches URLs under EDM/ or epaper/ to avoid catching unrelated numbered
    pages (e.g. teacher-page.php?n=).
    """
    h = href or ""
    if not re.search(r"EDM/|epaper/", h, re.I):
        return None
    m = _EDM_HREF.search(h)
    return int(m.group(1)) if m else None


# ── EDM body → (date, title) ────────────────────────────────────────────────────
_EDM_DATE = re.compile(r"(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")
_EDM_TITLE = re.compile(r"本\s*期\s*目\s*錄\s*[\n■、\s]*([^\n■]{4,40})")


def parse_edm_meta(text: str) -> Tuple[str, str]:
    """→ (date 'YYYY/MM/DD', first 目錄 title). Either may be '' if absent."""
    t = text or ""
    date = ""
    m = _EDM_DATE.search(t[:400])
    if m:
        date = f"{m.group(1)}/{int(m.group(2)):02d}/{int(m.group(3)):02d}"
    title = ""
    mt = _EDM_TITLE.search(t)
    if mt:
        title = mt.group(1).strip()
    return date, title


# ── OCR decision (PDF text-layer sufficiency) ───────────────────────────────────
MIN_TEXT_PER_PAGE = 60


def pdf_text_sufficient(text: str, n_pages: int, min_per_page: int = MIN_TEXT_PER_PAGE) -> bool:
    """True if an extracted PDF text layer is rich enough to skip OCR.

    A scanned-image PDF yields little/no text → returns False → caller must OCR.
    """
    if n_pages <= 0:
        return False
    return len((text or "").strip()) >= min_per_page * n_pages
