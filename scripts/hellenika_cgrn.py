#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 自 CGRN 取祭儀法原文。

CGRN（Collection of Greek Ritual Norms, http://cgrn.ulg.ac.be）開放取用，
每篇提供希臘原文（Leiden 符號以 CSS class 編碼）＋英譯＋法譯＋年代／出土地／
載體／書目／註解。是 Κ 祭儀法卷的首選來源（見 hellenika-epigraphy skill §1）。

🚨 只走 http：cgrn.ulg.ac.be 的 https 連不上（2026-08-19 實測）。
🚨 節流：學術站點沒有 rate limit 公告不代表可以連抓。預設每篇間隔 6 秒。

Leiden 符號還原（見 hellenika-epigraphy §4）：
    class="supplied" → [ ]     編者補字
    class="lost"     → [ ]     石面已缺
    class="underdot" → 原字保留  字母殘存不確定
    <br/>            → 換行     以石面行為單位，行號即引用基礎

用法：
    python scripts/hellenika_cgrn.py --list          # 只列對照表與驗證結果
    python scripts/hellenika_cgrn.py --fetch         # 抓取並存檔
    python scripts/hellenika_cgrn.py --fetch --only 13
"""
from __future__ import annotations

import argparse
import html as htmllib
import io
import json
import os
import re
import sys
import time

import requests

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'cgrn')
BASE = 'http://cgrn.ulg.ac.be/file/{n}/'
UA = 'know-graph-lab/1.0 (academic research; contact via github)'
DELAY = 6.0

# 本藏經條目 → CGRN 編號。`expect` 是驗證關鍵字，抓下來若標題對不上就報錯不寫檔，
# 避免編號記錯而默默存進錯的文本。
TARGETS = [
    {'n': 13,  'zh': '塞利農特淨罪法',   'volume': 'K', 'expect': ['Selinous']},
    {'n': 181, 'zh': '古利奈淨罪法',     'volume': 'K', 'expect': ['Cyrene', 'Kyrene']},
    {'n': 52,  'zh': '埃爾希亞祭曆',     'volume': 'K', 'expect': ['Erchia']},
    {'n': 222, 'zh': '安達尼亞祕儀規章', 'volume': 'K', 'expect': ['Andania']},
    {'n': 86,  'zh': '科斯祭曆與祭司法', 'volume': 'K', 'expect': ['Kos', 'Coan']},
]


def fetch(n: int) -> str:
    r = requests.get(BASE.format(n=n), headers={'User-Agent': UA}, timeout=60)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r.text


# ─────────────────────── parsing ───────────────────────

def _text(fragment: str) -> str:
    """剝標籤取純文字。"""
    t = re.sub(r'<[^>]+>', '', fragment)
    return htmllib.unescape(re.sub(r'\s+', ' ', t)).strip()


def _greek(fragment: str) -> str:
    """把標記過的希臘文還原成帶 Leiden 符號的純文字。"""
    t = fragment
    # 補字與缺字 → 方括號
    t = re.sub(r'<span[^>]*class="[^"]*\b(?:supplied|lost)\b[^"]*"[^>]*>(.*?)</span>',
               r'[\1]', t, flags=re.S)
    # 行號 → 行首標記
    t = re.sub(r'<span[^>]*class="line-number"[^>]*>(.*?)</span>', r'{\1}', t, flags=re.S)
    t = re.sub(r'<br\s*/?>', '\n', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = htmllib.unescape(t)
    t = re.sub(r'[ \t]+', ' ', t)
    t = re.sub(r'\n\s*', '\n', t)
    # 合併相鄰方括號（同一補字被跨 span 切開）
    t = re.sub(r'\]\s*\[', '', t)
    # supplied 有時巢狀（外層 word-container 內層 supplied），會疊成 [[…]]，收成單層
    t = re.sub(r'\[{2,}', '[', t)
    t = re.sub(r'\]{2,}', ']', t)
    return t.strip()


def _section(page: str, heading: str) -> str:
    """取某個 h4 標題之後、下一個 h4 之前的區塊原始 HTML。"""
    m = re.search(rf'<h4[^>]*>(?:<span[^>]*></span>)?\s*{re.escape(heading)}\s*(?:&nbsp;)?:?\s*</h4>',
                  page, re.I)
    if not m:
        return ''
    rest = page[m.end():]
    nxt = re.search(r'<h4[^>]*>', rest)
    return rest[:nxt.start()] if nxt else rest[:20000]


def parse(page: str, n: int) -> dict:
    title = _text(re.search(r'<h3[^>]*>(.*?)</h3>', page, re.S).group(1)) \
        if re.search(r'<h3[^>]*>(.*?)</h3>', page, re.S) else ''

    text_block = _section(page, 'Text')
    faces = []
    for fm in re.finditer(r'<h5[^>]*>(.*?)</h5>(.*?)(?=<h5[^>]*>|$)', text_block, re.S):
        faces.append({'label': _text(fm.group(1)), 'greek': _greek(fm.group(2))})
    if not faces:
        faces = [{'label': '', 'greek': _greek(text_block)}]

    return {
        'cgrn': n,
        'url': BASE.format(n=n),
        'title_en': title,
        'date': _text(_section(page, 'Date')),
        'provenance': _text(_section(page, 'Provenance')),
        'support': _text(_section(page, 'Support')),
        'layout': _text(_section(page, 'Layout')),
        'bibliography': _text(_section(page, 'Bibliography')),
        'text': faces,
        'translation_en': _text(_section(page, 'Translation')),
        'commentary': _text(_section(page, 'Commentary')),
        'licence': 'CGRN — Collection of Greek Ritual Norms (Université de Liège), 開放取用；'
                   '引用請註明 CGRN 編號與網址。',
        'fetched': time.strftime('%Y-%m-%d'),
    }


# ─────────────────────── run ───────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--fetch', action='store_true')
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--only', type=int)
    ap.add_argument('--delay', type=float, default=DELAY)
    args = ap.parse_args()

    targets = [t for t in TARGETS if args.only is None or t['n'] == args.only]

    if args.list and not args.fetch:
        for t in targets:
            path = os.path.join(OUT_DIR, f"cgrn-{t['n']}.json")
            print(f"  CGRN {t['n']:>4}  {t['zh']:<12} 卷 {t['volume']:<3} "
                  f"{'已存' if os.path.exists(path) else '待抓'}")
        return

    if not args.fetch:
        ap.print_help()
        return

    os.makedirs(OUT_DIR, exist_ok=True)
    ok = bad = 0
    for i, t in enumerate(targets):
        if i:
            time.sleep(args.delay)
        try:
            page = fetch(t['n'])
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ CGRN {t['n']} {t['zh']}：抓取失敗 {e}", flush=True)
            bad += 1
            continue

        data = parse(page, t['n'])
        blob = f"{data['title_en']} {data['provenance']}"
        if not any(k.lower() in blob.lower() for k in t['expect']):
            print(f"  ✗ CGRN {t['n']} 對不上「{t['zh']}」（期待 {t['expect']}）"
                  f"，實得：{data['title_en'][:70]} — 不寫檔", flush=True)
            bad += 1
            continue

        data['title_zh'] = t['zh']
        data['volume'] = t['volume']
        path = os.path.join(OUT_DIR, f"cgrn-{t['n']}.json")
        io.open(path, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1) + '\n')
        greek_len = sum(len(f['greek']) for f in data['text'])
        print(f"  ✓ CGRN {t['n']:>4} {t['zh']}：希臘文 {greek_len} 字、"
              f"英譯 {len(data['translation_en'])} 字 → {os.path.relpath(path, ROOT)}", flush=True)
        ok += 1

    print(f'\n完成 {ok}，失敗 {bad}')


if __name__ == '__main__':
    main()
