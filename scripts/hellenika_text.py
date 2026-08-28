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
import re
import sys
import time

import requests
from lxml import etree

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


def fetch(urn):
    grp, wk, _ = urn.split('.', 2)
    url = RAW.format(grp=grp, wk=wk, urn=urn)
    r = requests.get(url, headers={'User-Agent': UA}, timeout=60)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.content


def lines_of(xml):
    """取出 (行號, 該 <l> 的全部文字)。行號非數字者跳過。"""
    root = etree.fromstring(xml)
    out = []
    for el in root.iter('{http://www.tei-c.org/ns/1.0}l'):
        n = el.get('n')
        if not n or not n.isdigit():
            continue
        txt = re.sub(r'\s+', ' ', ''.join(el.itertext())).strip()
        out.append((int(n), txt))
    return out


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
    grc = lines_of(gx)
    eng = lines_of(ex) if ex else []
    if not grc:
        print('  X %s：TEI 裡沒有帶數字行號的 <l>，需個別處理' % t['slug'])
        return None
    segs = segment(grc, eng, lo, hi)
    grp, wk = t['grc'].split('.')[0], t['grc'].split('.')[1]
    return {
        'source': 'perseus', 'siglum': t['siglum'], 'slug': t['slug'],
        'url': RAW.format(grp=grp, wk=wk, urn=t['grc']),
        'title_zh': t['zh'], 'title_en': t['en'], 'author': t['author'],
        'volume': t['volume'], 'licence': LICENCE,
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
