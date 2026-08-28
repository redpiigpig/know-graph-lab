#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析英文版 ACCS（IVP）EPUB 的純函式。

中文各卷是掃描頁走 Gemini vision OCR（見 ingest_accs_genesis.py）；英文版是
數位 EPUB，結構完整且規則，不需要 OCR，也不會有 OCR 那些錯字與跨批次斷句。

版式（實際取自 ACCS_Jeremiah_Lamentations.epub）：

    <h1 class="chap_tit">…段落標題<br/>
        <a href="…search=Jeremiah+2%3A1-8&version=RSV">JEREMIAH 2:1-8</a></h1>
    <p class="txt_courant_ssalinea"><b>O<small>VERVIEW:</small></b> …總論…</p>
    <h2 class="int_niv1">2:1-4 <i>Israel Faithful in Its Youth</i></h2>
    <p class="txt_courant_ssalinea"><b>P<small>ROPHETIC </small>I<small>NSPIRATION. </small></b>
       A<small>THANASIUS: </small>…正文…
       D<small>ISCOURSES </small>A<small>GAINST THE </small>A<small>RIANS</small> 2.18.32.</p>

小型大寫是用「首字母在外、其餘包在 <small> 裡」做的，所以純去標籤會得到
「A THANASIUS」這種東西——必須先把 <small> 併回去、再轉成正常大小寫。
"""
from __future__ import annotations

import html as _html
import re
import urllib.parse

# 首字母 + <small>其餘</small>，可連續多組（每個字一組）
_SMALLCAPS = re.compile(r'([A-Za-z’])<small>([^<]*)</small>')
_TAG = re.compile(r'<[^>]+>')
_WS = re.compile(r'[\s ]+')

BOOK_CODES = {'jeremiah': 'jer', 'lamentations': 'lam'}


def _clean(text: str) -> str:
    return _WS.sub(' ', _html.unescape(text)).strip()


def unsmallcaps(fragment: str) -> str:
    """把 `A<small>THANASIUS</small>` 還原成 `Athanasius`。

    ACCS 的小標與署名整段都是小型大寫，直接 strip 標籤會得到全大寫加空隙。
    這裡逐組把首字母與其餘接起來，其餘轉小寫；不在 <small> 裡的原樣保留。
    """
    def repl(m: re.Match) -> str:
        head, rest = m.group(1), m.group(2)
        trail = ' ' if rest.endswith(' ') else ''
        return head + rest.strip().lower() + trail
    return _SMALLCAPS.sub(repl, fragment)


def strip_tags(fragment: str) -> str:
    return _clean(_TAG.sub('', fragment))


def parse_passage_ref(h1_html: str) -> dict | None:
    """從章標題取經文範圍。優先讀 biblegateway 連結的 search 參數（最可靠），
    讀不到才退回標題文字。"""
    m = re.search(r'search=([^&"\']+)', h1_html)
    raw = urllib.parse.unquote_plus(m.group(1)) if m else None
    if not raw:
        txt = strip_tags(unsmallcaps(h1_html))
        m2 = re.search(r'((?:Jeremiah|Lamentations)\s+[\d:,\-–\s]+)$', txt, re.I)
        raw = m2.group(1) if m2 else None
    if not raw:
        return None
    m3 = re.match(r'\s*([A-Za-z ]+?)\s+(\d+):(\d+)(?:\s*[-–]\s*(?:\d+:)?(\d+))?', raw)
    if not m3:
        return None
    book = BOOK_CODES.get(m3.group(1).strip().lower())
    if not book:
        return None
    start = int(m3.group(3))
    return {'book_code': book, 'chapter': int(m3.group(2)),
            'verse_start': start, 'verse_end': int(m3.group(4) or start),
            'passage': raw.strip()}


def parse_subheading(h2_html: str) -> dict:
    """`2:1-4 <i>Israel Faithful in Its Youth</i>` → 節範圍與小節標題。"""
    txt = strip_tags(unsmallcaps(h2_html))
    m = re.match(r'\s*(\d+):(\d+)(?:\s*[-–]\s*(\d+))?\s*(.*)$', txt)
    if not m:
        return {'title': txt}
    return {'chapter': int(m.group(1)), 'verse_start': int(m.group(2)),
            'verse_end': int(m.group(3) or m.group(2)), 'title': m.group(4).strip()}


def parse_entry(p_html: str) -> dict | None:
    """一個 <p> → 一則總論或引文。

    總論：<b>Overview:</b> 起頭。
    引文：<b>小標.</b> 之後是 `教父名: 正文 … 作品名 章節號`。
    """
    inner = re.sub(r'^\s*<p[^>]*>|</p>\s*$', '', p_html.strip())
    text = unsmallcaps(inner)
    bold = re.match(r'\s*<b>(.*?)</b>(.*)$', text, re.S)
    if not bold:
        return None
    head = strip_tags(bold.group(1))
    rest_html = bold.group(2)
    rest = strip_tags(rest_html)

    if head.rstrip(': ').lower() == 'overview':
        return {'kind': 'overview', 'heading': 'Overview', 'father': '',
                'work': '', 'body': rest}

    # 署名：正文開頭到第一個冒號為止
    m = re.match(r'\s*([^:]{2,60}?):\s*(.*)$', rest, re.S)
    if not m:
        return {'kind': 'comment', 'heading': head.rstrip('. '), 'father': '',
                'work': '', 'body': rest}
    father, body = m.group(1).strip(), m.group(2).strip()

    # 出處在最末：作品名（原本是小型大寫）＋可有可無的章節號
    work = ''
    mw = re.search(r'([A-Z][A-Za-z’\'\- ]{3,}?)\s*([\d.:,\-–]*)\s*$', body)
    if mw and len(mw.group(1).split()) <= 12:
        cand = mw.group(1).strip()
        if cand and cand[0].isupper() and not cand.endswith(('.', '?', '!')):
            work = _clean(cand + (' ' + mw.group(2).strip() if mw.group(2).strip() else ''))
            work = work.rstrip('.')      # 出處在書上以句點收尾，欄位裡不留
            body = body[:mw.start()].strip()
    return {'kind': 'comment', 'heading': head.rstrip('. '), 'father': father,
            'work': work, 'body': body}


def parse_chapter(chapter_html: str) -> list[dict]:
    """一個章節檔 → 依序的條目清單，每則帶所屬經文範圍。"""
    body = re.search(r'<body[^>]*>(.*)</body>', chapter_html, re.S)
    src = body.group(1) if body else chapter_html
    ref: dict | None = None
    sub: dict | None = None
    out: list[dict] = []
    pericope = 0
    for chunk in re.finditer(
            r'<h1[^>]*class="chap_tit".*?</h1>|<h2[^>]*class="int_niv1".*?</h2>'
            r'|<p[^>]*class="txt_courant_ssalinea".*?</p>', src, re.S):
        frag = chunk.group(0)
        if frag.startswith('<h1'):
            ref = parse_passage_ref(frag)
            sub = None
            pericope += 1
            continue
        if frag.startswith('<h2'):
            sub = parse_subheading(frag)
            pericope += 1
            continue
        rec = parse_entry(frag)
        if not rec or not rec['body']:
            continue
        scope = sub if (sub and 'verse_start' in sub) else ref
        if not scope:
            continue
        rec.update({'book_code': (ref or {}).get('book_code'),
                    'chapter': scope.get('chapter'),
                    'verse_start': scope.get('verse_start'),
                    'verse_end': scope.get('verse_end'),
                    'pericope_order': pericope})
        out.append(rec)
    return out
