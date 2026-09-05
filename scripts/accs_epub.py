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

# 英文書名 → 站上 bible_books.code。次經那七卷是 ACCS 卷十五的收錄範圍
# （友弟德傳與瑪加伯上下不在該卷，那是出版社的範圍不是漏收）。
# 🚨 Song of the Three Young Men 對到 aza：三青年之歌與阿撒里雅禱詞在希臘文
#    但以理補篇裡是同一段連續文字（達 3:24–90），站上以一個 aza 涵蓋。
BOOK_CODES = {
    'jeremiah': 'jer', 'lamentations': 'lam',
    'sirach': 'sir', 'wisdom': 'wis', 'wisdom of solomon': 'wis',
    'tobit': 'tob', 'baruch': 'bar', 'susanna': 'sus',
    'bel and the dragon': 'bel',
    'song of the three young men': 'aza', 'prayer of azariah': 'aza',
}


def _clean(text: str) -> str:
    return _WS.sub(' ', _html.unescape(text)).strip()


# 小型大寫偶爾掉在 </b> 外面：<b>O</b><small>VERVIEW:</small>
# 這樣一來首字母與其餘之間隔了個標籤，_SMALLCAPS 比對不到，結果小標只剩「O」、
# 署名變成「VERVIEW」，整則概述被誤判成引文。先把跨 </b> 的那一組接回去。
_SMALLCAPS_ACROSS_B = re.compile(r'([A-Za-z’])</b>\s*<small>([^<]*)</small>')


def unsmallcaps(fragment: str) -> str:
    """把 `A<small>THANASIUS</small>` 還原成 `Athanasius`。

    ACCS 的小標與署名整段都是小型大寫，直接 strip 標籤會得到全大寫加空隙。
    這裡逐組把首字母與其餘接起來，其餘轉小寫；不在 <small> 裡的原樣保留。
    """
    def repl(m: re.Match) -> str:
        head, rest = m.group(1), m.group(2)
        trail = ' ' if rest.endswith(' ') else ''
        return head + rest.strip().lower() + trail
    # 先接回跨 </b> 的那一組，接完再走一般的還原
    fragment = _SMALLCAPS_ACROSS_B.sub(
        lambda m: m.group(1) + m.group(2).strip().lower() + '</b>', fragment)
    return _SMALLCAPS.sub(repl, fragment)


def strip_tags(fragment: str) -> str:
    return _clean(_TAG.sub('', fragment))


def parse_passage_ref(h1_html: str) -> dict | None:
    """從章標題取經文範圍。優先讀 biblegateway 連結的 search 參數（最可靠），
    讀不到才退回標題文字。"""
    m = re.search(r'search=([^&"\']+)', h1_html)
    raw = urllib.parse.unquote_plus(m.group(1)) if m else None
    if not raw:
        # 退路：標題文字。書名清單直接從 BOOK_CODES 長出來，長的排前面才不會讓
        # 「Wisdom」先吃掉「Wisdom of Solomon」。
        txt = strip_tags(unsmallcaps(h1_html))
        alt = '|'.join(re.escape(b) for b in sorted(BOOK_CODES, key=len, reverse=True))
        m2 = re.search(rf'((?:{alt})\s+[\d:,\-–\s]+)$', txt, re.I)
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
    # 🚨 換頁錨點會把單字從中間切開：
    #     <b>O</b><a id="page_82"/><b><small>VERVIEW: </small></b>
    #   錨點本身沒有內容，但它一插進來，首字母與其餘就不再相鄰，小型大寫還原
    #   比對不到，結果小標只剩「O」、署名變成「VERVIEW」，整則概述被誤判成引文。
    #   先拿掉錨點，再把因此相鄰的 </b><b> 併回去 —— 這兩步對沒有錨點的卷是 no-op。
    inner = re.sub(r'<a\b[^>]*\bid="page_[^"]*"[^>]*/>', '', inner)
    inner = re.sub(r'</b>\s*<b>', '', inner)
    text = unsmallcaps(inner)
    # 🚨 卷十五（次經）把小型大寫多包了一層 <span class="mev3/mev4">：
    #     耶利米卷            <b>O<small>VERVIEW:</small></b>
    #     次經卷  <span class="mev3"><b>O<small>VERVIEW:</small></b></span>
    #   下面那個 re.match 要求 <b> 在字串開頭，被那層 span 一擋就整段解析不出來
    #   （實測整卷 221 個章節檔只撈到 3 則，署名還全是碎片）。span 不帶語意，
    #   unsmallcaps 也已經跑完，直接剝掉；對沒有這層的卷是 no-op。
    text = re.sub(r'</?span[^>]*>', '', text)
    # 🚨 小標可能被拆成連續多段 <b>，因為經文引詞用斜體另起一段：
    #     <b><i>Heaven</i></b><b> AND </b><b><i>Firmament</i></b><b> Are Not the Same. </b>Ambrose: …
    #   只吃第一段的話，剩下的「AND Firmament Are Not the Same. Ambrose」會整串被
    #   當成署名（署名是取到第一個冒號為止）。所以要把開頭連續的 bold 段全部吃掉。
    bold = re.match(r'\s*((?:<b>.*?</b>\s*)+)(.*)$', text, re.S)
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
    # 小標的收尾標點偶爾會落到署名這一側（"…Are Not the Same." → ". Ambrose"），
    # 署名不該以標點開頭，一律削掉；不然詞庫比對必然落空。
    father, body = m.group(1).strip(' .,:;“”"'), m.group(2).strip()

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

# ---------------------------------------------------------------------------
# Calibre 拆檔式 EPUB（ACCS Vol 9 箴言‧傳道書‧雅歌）
#
# 跟 Vol 12 那本的包裝完全不同：整本被 Calibre 打散成三千多個 index_split_NNN.html
# （絕大多數是註腳），正文只在前十四檔，而且改用 blockNN / text_N 這組 class。
# 好消息是欄位是「明講」的，不必像 parse_entry 那樣靠正則猜署名與作品名邊界：
#   <h2 class="block_33">  段落層： 2:8–17 SONGS AT THE BREAK OF SPRING
#   <p  class="block_32">  概述：  <span class="text_5">Overview:</span> …
#   <h3 class="block_40">  逐節層： 2:8 The Leaping Lord
#   <p  class="block_41">  具名註釋：text_5=小標、第一個 text_=教父、最後一個 text_=作品名
# ---------------------------------------------------------------------------

_SUP_RE = re.compile(r'<sup\b.*?</sup>', re.S)
_SPAN_RE = re.compile(r'<span\b([^>]*)>(.*?)</span>', re.S)


def _join_spans(parts: list[str]) -> str:
    """概述把教父名放在括號裡、各自獨立成 span，用空白接起來會變成
    「present already but not yet ( Cyril of Alexandria )」。把括號與標點貼回去。"""
    s = _clean(' '.join(parts))
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'\s+\)', ')', s)
    return re.sub(r'\s+([,.;:])', r'\1', s)


def _drop_footnotes(html: str) -> str:
    """🚨 註腳是 <sup> 包的數字，直接 strip_tags 會把編號黏進正文
    （"…in the Jordan.32322 8 Hence the bride says…"）。先整段拿掉。"""
    return _SUP_RE.sub('', html)


def parse_ref_calibre(heading_html: str) -> dict | None:
    """`2:8–17 SONGS AT…` / `4:9–5:1 THE ENCLOSED GARDEN` → 章節範圍與標題。

    範圍可以跨章（4:9–5:1）。跨章時 verse_end 取結束章的節，chapter 仍記起始章
    —— 與資料庫既有的做法一致（一則註釋只掛在起始章上）。"""
    txt = strip_tags(unsmallcaps(_drop_footnotes(heading_html))).strip()
    m = re.match(r'^(\d+):(\d+)(?:\s*[-–—]\s*(?:(\d+):)?(\d+))?\s*(.*)$', txt)
    if not m:
        return None
    ch, vs = int(m.group(1)), int(m.group(2))
    ve = int(m.group(4)) if m.group(4) else vs
    return {'chapter': ch, 'verse_start': vs, 'verse_end': ve,
            'end_chapter': int(m.group(3)) if m.group(3) else ch,
            'title': m.group(5).strip()}


def parse_entry_calibre(p_html: str) -> dict | None:
    """一個 <p class="block_32|block_41"> → 一則概述或具名引文。"""
    html = _drop_footnotes(p_html)
    spans = [(a, strip_tags(v)) for a, v in _SPAN_RE.findall(html)]
    if not spans:
        return None
    head_i = next((i for i, (a, _) in enumerate(spans) if 'text_5' in a), None)
    if head_i is None:
        return None
    head = spans[head_i][1].strip()

    if head.rstrip(': ').lower() == 'overview':
        body = _join_spans([v for _, v in spans[head_i + 1:]])
        return {'kind': 'overview', 'heading': 'Overview', 'father': '',
                'work': '', 'body': body} if body else None

    # text_5 之後的 text_ span：第一個是教父，最後一個是作品名（只有一個時就是教父）
    marked = [i for i, (a, _) in enumerate(spans)
              if i > head_i and 'text_5' not in a and re.search(r'class="[^"]*\btext_\b', a)]
    # 小標偶爾把句點留在下一個 span（"…in Christ" + ". Bede"），署名前後的
    # 標點一律削掉，否則詞庫比對會整個對不上。
    father = spans[marked[0]][1].strip(' .,:;') if marked else ''
    work = spans[marked[-1]][1].strip() if len(marked) > 1 else ''

    body_parts = []
    for i, (_, v) in enumerate(spans):
        if i <= head_i or i in (marked[:1] + marked[-1:] if marked else []):
            continue
        body_parts.append(v)
    body = _join_spans(body_parts).lstrip(': ').strip()
    # 作品名後面常跟章節號（"Commentary on the Song of Songs 5.3"），併進 work
    if work:
        m = re.match(r'^([\d.:,\-–\s]+)(.*)$', body[::-1])
        del m  # 章節號在 body 尾端不好切，交給下面統一處理
        mtail = re.search(r'([\d]+(?:[.:][\d]+)*)\s*\.?\s*$', body)
        if mtail and len(mtail.group(1)) <= 12:
            work = f'{work} {mtail.group(1)}'.strip()
            body = body[:mtail.start()].strip()
    if not body:
        return None
    return {'kind': 'comment', 'heading': head.rstrip('. '), 'father': father,
            'work': work.rstrip('.'), 'body': body}


def parse_chapter_calibre(chapter_html: str, book_code: str) -> list[dict]:
    """一個 index_split_NNN.html → 依序的條目清單。

    book_code 必須由呼叫端指定：這種包裝沒有把卷名寫進正文檔，卷界是靠檔案編號
    （Vol 9：000–005 箴言、006–007 傳道書、008–011 雅歌）判斷的。
    """
    body = re.search(r'<body[^>]*>(.*)</body>', chapter_html, re.S)
    src = body.group(1) if body else chapter_html
    scope: dict | None = None
    out: list[dict] = []
    pericope = 0
    for chunk in re.finditer(
            r'<h2[^>]*class="block_33".*?</h2>|<h3[^>]*class="block_40".*?</h3>'
            r'|<p[^>]*class="block_3[02]".*?</p>|<p[^>]*class="block_41".*?</p>', src, re.S):
        frag = chunk.group(0)
        if frag.startswith('<h2') or frag.startswith('<h3'):
            ref = parse_ref_calibre(frag)
            if ref:
                scope = ref
                pericope += 1
            continue
        rec = parse_entry_calibre(frag)
        if not rec or not scope:
            continue
        rec.update({'book_code': book_code,
                    'chapter': scope['chapter'],
                    'verse_start': scope['verse_start'],
                    'verse_end': scope['verse_end'],
                    'pericope_order': pericope})
        out.append(rec)
    return out
