#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 自 PHI Greek Inscriptions 取銘文原文。

PHI（epigraphy.packhum.org）收錄幾乎全部已刊希臘銘文的原文，開放取用、無 API。
與 CGRN 分工：CGRN 只收祭儀規範（leges sacrae），本站取其餘各類——治癒銘文、
還願銘文、認罪碑、神諭銘文等（見 hellenika-epigraphy skill §1、§2）。

🚨 節流：無 rate limit 公告不代表可以連抓。預設每篇間隔 6 秒。
🚨 編號驗證：每筆帶 expect，抓下來比對頁面標題，對不上就不寫檔——
   坊間引用的編號常有誤（CGRN 那批就擋下過一次錯存）。

PHI 編號查法：站上 /search?patt=<不帶重音的希臘詞> 可查，結果頁含 /text/{id}。
瀏覽頁（/book/{n}）是 JS 驅動的，抓不到條目，別浪費時間。

用法：
    python scripts/hellenika_phi.py --list
    python scripts/hellenika_phi.py --fetch
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
OUT_DIR = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'phi')
BASE = 'https://epigraphy.packhum.org/text/{n}'
UA = 'know-graph-lab/1.0 (academic research; contact via github)'
DELAY = 6.0
LICENCE = ('PHI Greek Inscriptions (Packard Humanities Institute)，開放取用；'
           '引用請註明銘文編號與網址。')

# 埃庇道洛斯治癒銘文（Ἰάματα）四石。IG IV²,1 121 的 PHI id 由站上搜尋
# 「ιαματα」查得為 28551，其餘三石順序相鄰，逐一以 expect 驗證。
TARGETS = [
    {'n': 28551, 'zh': '埃庇道洛斯治癒銘文·第一石', 'stele': 'A',
     'volume': 'Ch', 'siglum': 'IG IV²,1 121', 'expect': ['IG IV²,1 121']},
    {'n': 28552, 'zh': '埃庇道洛斯治癒銘文·第二石', 'stele': 'B',
     'volume': 'Ch', 'siglum': 'IG IV²,1 122', 'expect': ['IG IV²,1 122']},
    {'n': 28553, 'zh': '埃庇道洛斯治癒銘文·第三石', 'stele': 'C',
     'volume': 'Ch', 'siglum': 'IG IV²,1 123', 'expect': ['IG IV²,1 123']},
    {'n': 28554, 'zh': '埃庇道洛斯治癒銘文·第四石', 'stele': 'D',
     'volume': 'Ch', 'siglum': 'IG IV²,1 124', 'expect': ['IG IV²,1 124']},
]


def fetch(n: int) -> str:
    r = requests.get(BASE.format(n=n), headers={'User-Agent': UA}, timeout=60)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r.text


# ─────────────────────── parsing ───────────────────────

def _plain(fragment: str) -> str:
    return htmllib.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', fragment))).strip()


def parse(page: str, n: int) -> dict:
    """PHI 正文結構：<div class="greek"><table class="grk">，每個 <tr> 一個石面行，
    <td class="id"> 放行號（每五行才出現一次），<span class="r"> 是補字（方括號已在
    內容裡），<em>v</em> 是 vacat（石面留白）。"""
    title = ''
    m = re.search(r'<title>(.*?)</title>', page, re.S)
    if m:
        title = _plain(m.group(1)).replace(' - PHI Greek Inscriptions', '')

    tm = re.search(r'<table class="grk">(.*?)</table>', page, re.S)
    if not tm:
        return {'phi': n, 'url': BASE.format(n=n), 'title_en': title,
                'header': '', 'lines': [], 'greek': '',
                'licence': LICENCE, 'fetched': time.strftime('%Y-%m-%d')}

    lines: list[dict] = []
    last = 0
    for row in re.findall(r'<tr>(.*?)</tr>', tm.group(1), re.S):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.S)
        if len(cells) < 2:
            continue
        num = _plain(cells[0])
        body = cells[1]
        body = re.sub(r'<em>\s*v\s*</em>', ' ⟨空⟩ ', body)      # vacat
        body = re.sub(r'<[^>]+>', '', body)
        body = htmllib.unescape(re.sub(r'[ 	]+', ' ', body)).strip()
        if not body:
            continue
        last = int(num) if num.isdigit() else last + 1
        lines.append({'line': last, 'text': body})

    head = ''
    hm = re.search(r'<div class="docref[^"]*">(.*?)</div>', page, re.S)
    if hm:
        head = _plain(hm.group(1))

    return {
        'phi': n,
        'url': BASE.format(n=n),
        'title_en': title,
        'header': head,
        'lines': lines,
        'greek': chr(10).join(f"{{{l['line']}}} {l['text']}" for l in lines),
        'licence': LICENCE,
        'fetched': time.strftime('%Y-%m-%d'),
    }


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
            path = os.path.join(OUT_DIR, f"phi-{t['n']}.json")
            print(f"  PHI {t['n']}  {t['siglum']:<14} {t['zh']:<22} "
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
            print(f"  ✗ PHI {t['n']}：抓取失敗 {e}", flush=True)
            bad += 1
            continue
        data = parse(page, t['n'])
        if not any(k in data['title_en'] for k in t['expect']):
            print(f"  ✗ PHI {t['n']} 對不上 {t['siglum']}，實得：{data['title_en'][:60]} — 不寫檔",
                  flush=True)
            bad += 1
            continue
        data.update({k: t[k] for k in ('zh', 'stele', 'volume', 'siglum')})
        data['title_zh'] = t['zh']
        path = os.path.join(OUT_DIR, f"phi-{t['n']}.json")
        io.open(path, 'w', encoding='utf-8').write(
            json.dumps(data, ensure_ascii=False, indent=1) + '\n')
        print(f"  ✓ PHI {t['n']} {t['siglum']}：{len(data['lines'])} 行、"
              f"希臘文 {len(data['greek'])} 字 "
              f"→ {os.path.relpath(path, ROOT)}", flush=True)
        ok += 1

    print(f'\n完成 {ok}，失敗 {bad}')


if __name__ == '__main__':
    main()
