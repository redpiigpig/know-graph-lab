#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Clean per-page OCR text so copied quotes don't carry running headers / page
numbers / wrapped-line noise.

The scanned-book OCR dump preserves physical line breaks and (worse) prepends the
running header — page number + book title — onto the first body line, e.g.

    "ii 埃及、希臘與羅馬出。作者汲取了古代史各領域的專家的成果："

Copying that gives "ii 埃及、希臘與羅馬" glued to the sentence. These pure
functions strip that and reflow wrapped lines into paragraphs. They need only a
single page's text plus the (known) book title — no cross-page state — so they
run cheaply per chunk and are fully unit-testable.

Pipeline: clean_ocr_page(text, title) = strip_running_header → normalize_cjk_linebreaks
"""
from __future__ import annotations

import re

# A page-number token: arabic, roman numerals (incl. OCR slips like lone m/v),
# or CJK 第N頁. Used ONLY immediately before the (known) title — never to strip a
# bare leading number, which would eat years (1914) and list numbers.
_PAGENO_TOKEN = r"(?:[0-9]{1,4}|[ivxlcdmIVXLCDM]{1,6}|第?\s*[0-9一二三四五六七八九十百]+\s*頁?)"
# A line that is ONLY a page number (running footer/header on its own line).
_PURE_PAGENO = re.compile(r"^[\s　]*(?:[0-9]{1,4}|[ivxlcdmIVXLCDM]{1,6})[\s　]*$")

_CJK_SENT_END = "。！？；：…」』）)】》"
# Only reflow (join) a line onto the previous one when the previous line is at
# least this long — i.e. it plausibly wrapped. Short lines are left as-is so we
# don't glue years / headings / list items together.
_WRAP_MIN = 14


def _title_pattern(title: str) -> re.Pattern | None:
    """Regex matching the title even if OCR inserted spaces / dropped CJK
    punctuation between characters."""
    chars = [c for c in (title or "") if not c.isspace() and c not in "、，。·,.-—"]
    if len(chars) < 2:
        return None
    body = r"[\s　、，·,.\-—]*".join(re.escape(c) for c in chars)
    return re.compile(body)


def strip_running_header(text: str, title: str | None = None) -> str:
    """Remove the running header (page-number + book TITLE) from each line —
    whether it stands alone or is glued to the start of body text. The title is
    the anchor: a leading page number is stripped ONLY when the title follows it,
    so bare years (1914) and Latin words are never touched. Also drops standalone
    pure-page-number lines at the very top / bottom of the page."""
    if not text:
        return text
    tp = _title_pattern(title) if title else None
    head = re.compile(r"^[\s　]*(?:" + _PAGENO_TOKEN + r"[\s　.\-–·]+)?(?:" + tp.pattern + r")") if tp else None
    lines = text.split("\n")
    out: list[str] = []
    for ln in lines:
        s = ln
        if head:
            m = head.match(s)
            if m:
                rest = s[m.end():]
                if rest.strip() == "":
                    continue  # whole line was the running header → drop it
                s = rest.lstrip(" 　:：.-–·")
        out.append(s)
    while out and _PURE_PAGENO.match(out[-1]):
        out.pop()
    while out and _PURE_PAGENO.match(out[0]):
        out.pop(0)
    return "\n".join(out).strip()


def normalize_cjk_linebreaks(text: str) -> str:
    """Reflow OCR's per-visual-line breaks into paragraphs: join a line onto the
    previous one unless the previous line ended a sentence or this line is a
    short standalone (heading-like) line. Blank lines stay paragraph breaks."""
    if not text:
        return text
    paras: list[str] = []
    cur = ""
    for raw in text.split("\n"):
        ln = raw.strip()
        if not ln:
            if cur:
                paras.append(cur)
                cur = ""
            continue
        if not cur:
            cur = ln
            continue
        prev_end = cur[-1]
        # Join onto the previous line only when it plausibly WRAPPED: it's long
        # enough, didn't end a sentence, and neither line is a heading. Otherwise
        # start a new paragraph. Conservative on purpose — avoids gluing short
        # lines / years / headings together.
        wrapped = (len(cur) >= _WRAP_MIN and prev_end not in _CJK_SENT_END
                   and not _looks_heading(ln) and not _looks_heading(cur))
        if wrapped:
            # No space when joining CJK (ideograph or full-width punctuation);
            # a space only between Latin words.
            sep = " " if ord(prev_end) < 128 else ""
            cur += sep + ln
        else:
            paras.append(cur)
            cur = ln
    if cur:
        paras.append(cur)
    return "\n\n".join(paras)


_HEADING_RE = re.compile(
    r"^("
    r"第\s*[0-9一二三四五六七八九十百]+\s*[章節編部卷講篇]"          # 第N章/節/卷…
    r"|(?:第\s*[0-9一二三四五六七八九十百]+\s*版\s*)?"               # 可選「第N版」前綴
    r"(序言?|自序|前言|導論|緒論|結語|結論|致謝|謝辭|目錄|附錄|參考文獻|索引|後記|引言|凡例)"
    r")"
)


def _looks_heading(line: str) -> bool:
    return bool(_HEADING_RE.match(line.strip())) and len(line.strip()) <= 24


def clean_ocr_page(text: str, title: str | None = None) -> str:
    """Full per-page cleanup pipeline."""
    return normalize_cjk_linebreaks(strip_running_header(text, title))
