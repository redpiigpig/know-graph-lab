#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 自 Perseus 標準 TEI 取「文獻」原文與公有領域英譯。

與既有兩支取源腳本分工（見 hellenika-epigraphy skill）：
    hellenika_cgrn.py / hellenika_phi.py  取**銘文**，切段單位是石面行號或案號
    本腳本                                 取**文獻**，切段單位是詩行號

🚨 不走 Scaife 的 CTS API（scaife-cts.perseus.org 目前連不上），改直接抓
   PerseusDL/canonical-greekLit 的標準 TEI 原始檔。那是同一批資料的上游，
   公有領域、無節流、行號完整，且不必解析 JS 頁面。

對齊原則：希臘文 TEI 每行一個 <l n="N">；Evelyn-White 英譯每五行下一個里程碑
（<l n="1">、<l n="5">、<l n="10">…），故**以英譯的里程碑為切段邊界**，再把
落在該區間的希臘文行併起來。這樣兩欄的邊界永遠對得上，不會出現半行對半行。

用法：
    python scripts/hellenika_text.py --list
    python scripts/hellenika_text.py --fetch theogony --lines 1-115   # 試跑
    python scripts/hellenika_text.py --fetch theogony                 # 全篇
    python scripts/hellenika_text.py --fetch all --out c:/tmp/hellenika/text
"""
from __future__ import annotations

import argparse
import io
import json
import os
import copy
import re
import sys
import time

import requests
from lxml import etree

TEI = '{http://www.tei-c.org/ns/1.0}'
# 散文英譯裡標行號用的哨兵。必須是正文絕不會出現的字元——用「空格＋數字＋空格」
# 會把譯文中每個獨立數字都當成行號切開，那是切錯而不是切不到，且看不出來。
MARK = '\ue000%s\ue000'
MARK_RE = r'\ue000(\d+)\ue000'

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'text')
RAW = ('https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/'
       'data/{grp}/{wk}/{urn}.xml')
UA = 'know-graph-lab/1.0 (academic research; contact via github)'
DELAY = 3.0
LICENCE = ('原文與英譯皆取自 Perseus Digital Library 的標準 TEI（PerseusDL/'
           'canonical-greekLit），CC BY-SA 3.0；英譯為 Hugh G. Evelyn-White '
           '(1914) 等已入公有領域之譯本。')
# 一段以多少「英譯里程碑」為度。里程碑間距 5 行，故 4 ＝ 每段約 20 行。
MILESTONES_PER_SEG = 4

TARGETS = [
    {'slug': 'theogony', 'zh': '神譜', 'en': 'Theogony', 'author': '赫西俄德',
     'volume': 'A', 'siglum': 'Hes. Th.',
     'grc': 'tlg0020.tlg001.perseus-grc2', 'eng': 'tlg0020.tlg001.perseus-eng2'},
    {'slug': 'works-and-days', 'zh': '工作與時日', 'en': 'Works and Days',
     'author': '赫西俄德', 'volume': 'B', 'siglum': 'Hes. Op.',
     'grc': 'tlg0020.tlg002.perseus-grc2', 'eng': 'tlg0020.tlg002.perseus-eng2'},
]
# 荷馬詩頌共 33 首，Perseus 各首獨立成篇（tlg0013.tlg001 … tlg033）。
HYMN_ZH = {
    1: '致戴奧尼索斯', 2: '致得墨忒耳', 3: '致阿波羅', 4: '致赫爾墨斯',
    5: '致阿芙羅狄忒',
}
for _i in range(1, 34):
    TARGETS.append({
        'slug': 'homeric-hymn-%02d' % _i,
        'zh': '荷馬詩頌 第%d首' % _i + ('（%s）' % HYMN_ZH[_i] if _i in HYMN_ZH else ''),
        'en': 'Homeric Hymn %d' % _i, 'author': '託名荷馬',
        'volume': 'O', 'siglum': 'Hom. Hymn %d' % _i,
        'grc': 'tlg0013.tlg%03d.perseus-grc2' % _i,
        'eng': 'tlg0013.tlg%03d.perseus-eng2' % _i,
    })


# 荷馬兩部史詩，各廿四卷。Perseus 一部一個 TEI 檔而**行號逐卷從 1 重來**，
# 故一卷一個 target（`book`），檔名 iliad-01…24／odyssey-01…24，與詩頌同慣例。
#
# 英譯取 A. T. Murray 的 Loeb 本（伊 1924–25、奧 1919，皆公有領域）。那是**散文**，
# 沒有 <l>，行號以 <milestone unit="line"/> 埋在段落裡，故走 prose_lines()。
# eng4（Butler 經 Power 與 Nagy 修訂）里程碑較疏且修訂本年代晚，不取。
LOEB = ('原文取自 Perseus Digital Library 的標準 TEI（PerseusDL/canonical-greekLit），'
        'CC BY-SA 3.0；英譯為 A. T. Murray 的 Loeb 本（《伊利亞特》1924–25、'
        '《奧德賽》1919），已入公有領域。')
CN = '一二三四五六七八九十'


def _cn(n: int) -> str:
    """1–24 的中文數字。卷次用中文數字，與書目「全 24 卷」的阿拉伯數字分工。"""
    if n <= 10:
        return CN[n - 1]
    return '十' + (CN[n - 11] if n > 10 and n % 10 else '') if n < 20 else         '二十' + (CN[n - 21] if n % 10 else '')


for _wk, _slug, _zh, _vol, _sig, _n in (
        (1, 'iliad', '伊利亞特', 'G', 'Hom. Il.', 24),
        (2, 'odyssey', '奧德賽', 'D', 'Hom. Od.', 24)):
    for _b in range(1, _n + 1):
        TARGETS.append({
            'slug': '%s-%02d' % (_slug, _b),
            'zh': '%s 卷%s' % (_zh, _cn(_b)),
            'en': '%s, Book %d' % (_zh == '伊利亞特' and 'Iliad' or 'Odyssey', _b),
            'author': '荷馬', 'volume': _vol, 'siglum': '%s %d' % (_sig, _b),
            'book': _b, 'licence': LOEB,
            'grc': 'tlg0012.tlg%03d.perseus-grc2' % _wk,
            'eng': 'tlg0012.tlg%03d.perseus-eng3' % _wk,
        })


_CACHE: dict[str, bytes | None] = {}


def fetch(urn):
    """史詩一部 TEI 兩三 MB，而 24 卷是 24 個 target，故同一次執行內只抓一次。"""
    if urn in _CACHE:
        return _CACHE[urn]
    grp, wk, _ = urn.split('.', 2)
    url = RAW.format(grp=grp, wk=wk, urn=urn)
    r = requests.get(url, headers={'User-Agent': UA}, timeout=180)
    _CACHE[urn] = None if r.status_code == 404 else (r.raise_for_status() or r.content)
    return _CACHE[urn]


def book_of(root, n):
    """取第 n 卷的 <div subtype="book">。🚨 史詩的行號**逐卷從 1 重來**，不分卷就會
    把二十四卷的第 1 行疊成同一行；grc 寫 Book、eng 寫 book，故不分大小寫比對。"""
    for d in root.iter(TEI + 'div'):
        if (d.get('subtype') or '').lower() == 'book' and d.get('n') == str(n):
            return d
    return None


def prose_lines(node):
    """散文英譯的行號取法。

    Murray 的 Loeb 譯本是散文，沒有 <l>，行號改以 <milestone n="N" unit="line"/>
    埋在段落中間。故把里程碑換成哨兵再按哨兵切開，切出來的 (行號, 該行號起的文字)
    與 <l> 那條路的回傳格式相同，下游不必分辨。Loeb 的 <note> 是編者註不是譯文，先剝掉。
    """
    node = copy.deepcopy(node)
    etree.strip_elements(node, TEI + 'note', with_tail=False)
    for ms in node.iter(TEI + 'milestone'):
        if ms.get('unit') == 'line' and (ms.get('n') or '').isdigit():
            ms.text = MARK % ms.get('n')
    parts = re.split(MARK_RE, ''.join(node.itertext()))
    raw = [(int(parts[i]), re.sub(r'\s+', ' ', parts[i + 1]).strip())
           for i in range(1, len(parts) - 1, 2)]

    # 🚨 上游 TEI 偶有行號筆誤：《奧德賽》十六的 275 與 285 之間夾了一個 n="580"
    # （顯然是 280 之誤）。放著不管，切段會排出 line_from 580 → line_to 299 這種
    # 倒置的段，而且希臘文那欄整段空掉——頁面照樣渲染。故凡「比前一個大、卻又比
    # 後一個大」的尖刺一律剔除，其文字併回前一段，一個字都不丟。
    out: list[tuple[int, str]] = []
    for i, (n, txt) in enumerate(raw):
        nxt = raw[i + 1][0] if i + 1 < len(raw) else None
        if out and (n <= out[-1][0] or (nxt is not None and n >= nxt)):
            print('    ! 行號 %d 不合序，併入第 %d 行那一段（上游 TEI 之誤）'
                  % (n, out[-1][0]), file=sys.stderr)
            out[-1] = (out[-1][0], (out[-1][1] + ' ' + txt).strip())
            continue
        out.append((n, txt))
    return out


def lines_of(xml, book=None):
    """取出 (行號, 文字)。行號非數字者跳過；book 有值時只取該卷。"""
    root = etree.fromstring(xml)
    scope = root if book is None else book_of(root, book)
    if scope is None:
        return []
    out = []
    for el in scope.iter(TEI + 'l'):
        n = el.get('n')
        if not n or not n.isdigit():
            continue
        txt = re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()
        out.append((int(n), txt))
    return out or prose_lines(scope)


def segment(grc, eng, lo, hi):
    """以英譯里程碑為邊界切段；英譯缺席時退回固定行數。"""
    gmap = {n: t for n, t in grc}
    emap = {n: t for n, t in eng}
    marks = [n for n, _ in eng]
    if not marks:                      # 無英譯：每 20 行一段
        ns = sorted(gmap)
        marks = ns[::5] or [1]
    segs = []
    for i in range(0, len(marks), MILESTONES_PER_SEG):
        block = marks[i:i + MILESTONES_PER_SEG]
        start = block[0]
        j = i + MILESTONES_PER_SEG
        end = (marks[j] - 1) if j < len(marks) else (max(gmap) if gmap else start)
        if lo and end < lo:
            continue
        if hi and start > hi:
            break
        g = '\n'.join(gmap[n] for n in range(start, end + 1) if gmap.get(n))
        e = ' '.join(emap[n] for n in block if emap.get(n)).strip()
        if not g and not e:
            continue
        segs.append({'line_from': start, 'line_to': end,
                     'greek': g, 'en': e, 'zh': ''})
    return segs


def build(t, lo, hi):
    gx = fetch(t['grc'])
    if gx is None:
        print('  X %s：希臘文 TEI 不存在（%s）' % (t['slug'], t['grc']))
        return None
    time.sleep(DELAY)
    ex = fetch(t['eng'])
    book = t.get('book')
    grc = lines_of(gx, book)
    eng = lines_of(ex, book) if ex else []
    if not grc:
        print('  X %s：TEI 裡沒有帶數字行號的 <l>，需個別處理' % t['slug'])
        return None
    segs = segment(grc, eng, lo, hi)
    grp, wk = t['grc'].split('.')[0], t['grc'].split('.')[1]
    return {
        'source': 'perseus', 'siglum': t['siglum'], 'slug': t['slug'],
        'url': RAW.format(grp=grp, wk=wk, urn=t['grc']),
        'title_zh': t['zh'], 'title_en': t['en'], 'author': t['author'],
        'volume': t['volume'], 'licence': t.get('licence', LICENCE),
        'pivot': 'perseus-eng' if eng else 'none',
        'pivot_note': None if eng else '無公有領域英譯可依據，繁中須直接譯自希臘原文。',
        'lines_total': max(n for n, _ in grc),
        'names': {},
        'segments': segs,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--fetch')
    ap.add_argument('--lines', help='只取此行段，如 1-115')
    ap.add_argument('--out', default=DEFAULT_OUT)
    a = ap.parse_args()

    if a.list or not a.fetch:
        for t in TARGETS:
            print('  %-22s %s（%s 卷）' % (t['slug'], t['zh'], t['volume']))
        print('\n共 %d 篇' % len(TARGETS))
        return

    lo = hi = None
    if a.lines:
        lo, hi = (int(x) for x in a.lines.split('-'))
    todo = TARGETS if a.fetch == 'all' else [t for t in TARGETS if t['slug'] == a.fetch]
    if not todo:
        sys.exit('找不到 %s' % a.fetch)
    os.makedirs(a.out, exist_ok=True)
    for t in todo:
        doc = build(t, lo, hi)
        if not doc:
            time.sleep(DELAY)
            continue
        p = os.path.join(a.out, '%s.json' % t['slug'])
        io.open(p, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
        print('  OK %-22s %d 段／%d 行｜英譯 %s → %s'
              % (t['slug'], len(doc['segments']), doc['lines_total'],
                 '有' if doc['pivot'] == 'perseus-eng' else '無', p))
        time.sleep(DELAY)


if __name__ == '__main__':
    main()
