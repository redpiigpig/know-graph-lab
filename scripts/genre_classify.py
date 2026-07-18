#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文體判定（collected-works ingest 的「先判斷文體」步）。

回傳 CwGenre 之一：dialogue / verse / aphorism / quaestio / lecture /
diary-letters / narrative / essay / treatise（預設）。

用法：
  from genre_classify import classify_genre
  g = classify_genre(text, source_kind="tei"|"plain", hint=None)

先跑純函式啟發式（免 LLM、零成本）；不確定時呼叫端可再用 Haiku 覆核
（translate_ebook_to_zh.haiku_translate 之類），但多數經典靠結構訊號即可判定。
reader 依此 genre 切版面（見 pages/collected-works/[slug]/[work].vue）。
"""
from __future__ import annotations
import re

GENRES = ('dialogue', 'verse', 'aphorism', 'quaestio', 'lecture',
          'diary-letters', 'narrative', 'essay', 'treatise')

# 經院問答（神學大全）標記——中英拉皆認
_QUAESTIO = re.compile(
    r'\b(Objection\s+\d|On the contrary|I answer that|Reply to Objection'
    r'|Praeterea|Sed contra|Respondeo|Videtur quod)\b'
    r'|反對(意見|說)|正解曰|反之[，、]|答覆[一二三四五六七八九]|茲有異議', re.I)
# 對話錄講者行（大寫人名＋句點，或 TEI said/sp、或中文「甲：」）
_SPEAKER = re.compile(r'^[ \t]*(?:<said\b|<sp\b|[A-ZΑ-Ω][A-ZΑ-Ωa-zα-ω]{1,20}[.:：]|〔[^〕]{1,10}〕)')
# 詩／講義／書信
_VERSE_TEI = re.compile(r'<l\b|<lg\b|type="poem"|type="hymn"')
_LECTURE = re.compile(r'\bLecture\s+[IVXLl0-9]|第[一二三四五六七八九十]+講\b|Gifford Lecture', re.I)
_DATED = re.compile(r'^\s*(\d{4}[-/年.]\d{1,2}|[A-Z][a-z]+ \d{1,2},? \d{4}|明治|大正|昭和)', re.M)
_SALUT = re.compile(r'^\s*(Dear |My dear |敬啟|吾兄|My Lord)', re.M | re.I)


def _line_stats(text: str):
    lines = [ln.rstrip() for ln in text.splitlines()]
    non_empty = [ln for ln in lines if ln.strip()]
    if not non_empty:
        return 0, 0.0, 0.0
    short = sum(1 for ln in non_empty if len(ln.strip()) <= 45)
    # 「詩行」：短行且不以句末標點結束
    verse_like = sum(1 for ln in non_empty
                     if len(ln.strip()) <= 55 and not re.search(r'[.。!?！？；;:]$', ln.strip()))
    return len(non_empty), short / len(non_empty), verse_like / len(non_empty)


def classify_genre(text: str, source_kind: str = 'plain', hint: str | None = None) -> str:
    """啟發式文體判定。hint 命中合法 genre 直接採用（如 fetch manifest 已標）。"""
    if hint in GENRES:
        return hint
    t = text or ''
    head = t[:20000]  # 取樣前段即可

    # 結構性強訊號（TEI / 明確標記）優先
    if source_kind == 'tei':
        if _VERSE_TEI.search(head):
            return 'verse'
        said = len(re.findall(r'<said\b|<sp\b', head))
        if said >= 8:
            return 'dialogue'
    if _QUAESTIO.search(head) and len(_QUAESTIO.findall(t)) >= 3:
        return 'quaestio'

    # 純文字結構訊號較弱、易被目錄/索引騙 → 門檻放嚴，偏向 treatise；
    # 精準判定應由呼叫端傳 hint（fetch manifest 已標／Haiku 覆核），此處僅保守 fallback。
    lines = [ln for ln in head.splitlines() if ln.strip()]
    speaker_lines = sum(1 for ln in lines if _SPEAKER.match(ln))
    if lines and speaker_lines / len(lines) >= 0.30 and speaker_lines >= 15:
        return 'dialogue'

    if _LECTURE.search(head):
        return 'lecture'
    if _SALUT.search(head) or len(_DATED.findall(head)) >= 5:
        return 'diary-letters'

    n, short_ratio, verse_ratio = _line_stats(head)
    if n >= 20 and verse_ratio >= 0.72 and short_ratio >= 0.7:
        return 'verse'

    return 'treatise'


if __name__ == '__main__':
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else ''
    kind = sys.argv[2] if len(sys.argv) > 2 else 'plain'
    txt = open(src, encoding='utf-8', errors='ignore').read() if src else sys.stdin.read()
    print(classify_genre(txt, kind))
