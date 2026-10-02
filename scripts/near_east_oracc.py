#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""古近東大藏經 —— 從 ORACC 取轉寫與英譯，逐段對齊成 reader 用的 JSON。

ORACC（Open Richly Annotated Cuneiform Corpus，CC BY-SA）每篇的 html 頁一列一行：
  <td class="lnum"> 原書行號（o i 1'）／<td class="tlit"> 轉寫／<td class="xtr"> 英譯
英譯跨數行時，後續列沒有 xtr 格。所以一段＝「一格英譯＋它涵蓋的轉寫行」，
段號照抄 ORACC 的行號（「o i 1'–o i 5'」），不自編。

🚨 ORACC 的 json 下載包（json/<project>.zip）**只有轉寫**，英譯一定要抓 html 頁。

  python -X utf8 scripts/near_east_oracc.py            # 跑 ENTRIES 全部
  python -X utf8 scripts/near_east_oracc.py --only assyrian-prophecies
"""
from __future__ import annotations

import argparse
import html
import io
import json
import pathlib
import re
import time
import zipfile

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / 'output' / 'near-east' / 'oracc'
OUT = ROOT / 'data' / 'near-east' / 'sources' / 'text'
MANIFEST = ROOT / 'data' / 'near-east' / 'sources' / 'manifest.json'
UA = {'User-Agent': 'Mozilla/5.0 (know-graph-lab research)'}

# slug → (ORACC 專案, 要收的 SAA／RINAP 編號；None＝整個專案依目錄順序)
ENTRIES = {
    'assyrian-prophecies': ('saao/saa09', None),
    'underworld-vision': ('saao/saa03', ['SAA 03 032']),
}


def get(url: str, cache_name: str, binary: bool = False):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / cache_name
    if f.exists() and f.stat().st_size > 1000:
        return f.read_bytes() if binary else f.read_text(encoding='utf-8')
    for attempt in range(3):
        try:
            # 🚨 oracc.museum.upenn.edu 的 HTTPS 憑證鏈缺中繼憑證，requests 驗證失敗（curl 走 Windows 憑證庫才過），
            #    HTTP 又會被轉回 HTTPS。這裡只抓公開學術文本，對此站關閉驗證。
            r = requests.get(url, headers=UA, timeout=120, verify=False)
            r.raise_for_status()
            f.write_bytes(r.content)
            time.sleep(1.0)
            return r.content if binary else r.content.decode('utf-8')
        except requests.RequestException as e:
            print(f'    重試 {url}：{e}')
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f'抓不到 {url}')


def catalogue(project: str) -> dict:
    zb = get(f'http://oracc.museum.upenn.edu/json/{project.replace("/", "-")}.zip', project.replace('/', '-') + '.zip', binary=True)
    z = zipfile.ZipFile(io.BytesIO(zb))
    return json.loads(z.read(f'{project}/catalogue.json'))['members']


def text_of(fragment: str) -> str:
    s = re.sub(r'<sup[^>]*>([^<]*)</sup>', r'{\1}', fragment)
    s = re.sub(r'<span class="xlabel[^"]*">.*?</span>', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def parse(page: str):
    """回傳 (segments, 頁上轉寫行數)。"""
    body = page[page.find('class="transliteration"'):]
    rows = re.findall(r'<tr id="P\d+\.\d+" class="([^"]*)"[^>]*>(.*?)</tr>', body, re.S)
    segs, n_lines = [], 0
    for cls, row in rows:
        if cls.startswith('h '):
            continue  # 「Obverse」「Column i」這類標題列
        lab = re.search(r'<span class="xlabel[^"]*">([^<]*)</span>', row)
        label = lab.group(1).replace(' ', ' ').strip() if lab else ''
        if cls != 'l':
            label = ''  # 「殘缺約十行」這類非正文列的標籤不算行號，否則分子會多於頁上行數
        tlit_m = re.search(r'<td class="tlit">(.*?)</td>', row, re.S) or re.search(r'class="nonlbody">(.*?)</td>', row, re.S)
        tlit = text_of(tlit_m.group(1)) if tlit_m else ''
        xtr_m = re.search(r'<td class="t1 xtr"[^>]*>(.*?)</td>', row, re.S)
        tr = text_of(re.sub(r'<span class="xtr-label">[^<]*</span>', '', xtr_m.group(1))) if xtr_m else None
        if cls == 'l':
            n_lines += 1
        if tr is not None and (tr or not segs):
            segs.append({'labels': [label] if label else [], 'orig': [tlit] if tlit else [], 'en': tr})
        elif segs:
            if label:
                segs[-1]['labels'].append(label)
            if tlit:
                segs[-1]['orig'].append(tlit)
    out = []
    for s in segs:
        if not s['orig'] and not s['en']:
            continue
        ref = s['labels'][0] + ('–' + s['labels'][-1] if len(s['labels']) > 1 else '') if s['labels'] else '—'
        out.append({'ref': ref, 'orig': '\n'.join(s['orig']), 'orig_lines': s['labels'], 'en': s['en']})
    return out, n_lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    a = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {}
    for slug, (project, want) in ENTRIES.items():
        if a.only and slug != a.only:
            continue
        cat = catalogue(project)
        members = sorted(cat.items(), key=lambda kv: kv[1].get('designation', ''))
        if want:
            members = [kv for kv in members if kv[1].get('designation') in want]
        comps, lines_total, lines_in = [], 0, 0
        for pnum, meta in members:
            page = get(f'http://oracc.museum.upenn.edu/{project}/{pnum}/html', f'{project.replace("/", "-")}-{pnum}.html')
            segs, n = parse(page)
            lines_total += n
            lines_in += sum(len(s['orig_lines']) for s in segs)
            if sum(len(s['orig_lines']) for s in segs) != n:
                print(f'    ⚠ {meta.get("designation", pnum)}：歸段行號 {sum(len(s["orig_lines"]) for s in segs)}／頁上 {n}')
            comps.append({'num': meta.get('designation', pnum), 'title_en': meta.get('title', ''), 'segments': segs})
        nseg = sum(len(c['segments']) for c in comps)
        print(f"  {slug:24} {len(comps):>2} 篇 {nseg:>4} 段  有行號的轉寫行 {lines_in}/{lines_total}")
        if not nseg:
            print('  ✗ 0 段，不寫檔'); continue
        doc = {'slug': slug, 'source': 'ORACC', 'siglum': ', '.join(c['num'] for c in comps),
               'source_url': f'https://oracc.museum.upenn.edu/{project}/', 'license': 'ORACC（CC BY-SA 3.0）',
               'compositions': comps}
        (OUT / f'{slug}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
        manifest[slug] = {'source': 'ORACC', 'segments': nseg, 'orig': 'ready', 'en': 'ready', 'zh': 'none'}
    MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
