#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""古近東大藏經・蘇美藏 —— 從牛津 ETCSL 取轉寫與英譯，逐段對齊成 reader 用的 JSON。

不用 LLM。對齊鍵是 ETCSL 自己給的：英譯頁每段 <a name='t111.p3'>，轉寫頁每一行都帶
lineid=t111.p3 的連結指回它屬於哪一段。所以一段＝「英譯一段＋所有指回這段的轉寫行」，
段號照抄 ETCSL 的行號範圍（如「11–16」），不自編（見 skill scripture-near-east §1）。

  python -X utf8 scripts/near_east_etcsl.py              # 蘇美藏全部有 ETCSL 編號的條目
  python -X utf8 scripts/near_east_etcsl.py --only enki-ninhursag
  python -X utf8 scripts/near_east_etcsl.py --check      # 只印對齊統計，不寫檔

產物：data/near-east/sources/text/<slug>.json、data/near-east/sources/manifest.json
快取：output/near-east/etcsl/（HTML 原頁，不進版控）

🚨 驗證分母取自原頁本身：轉寫頁的總行數、英譯頁的總段數。任何一行沒歸到段、
   任何一段沒有轉寫，都要印出來——「配對率很漂亮但收不全」是摩尼教那支踩過的坑。
ETCSL 授權：非商業學術使用（本站私人、需登入）。
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / 'output' / 'near-east' / 'etcsl'
OUT = ROOT / 'data' / 'near-east' / 'sources' / 'text'
MANIFEST = ROOT / 'data' / 'near-east' / 'sources' / 'manifest.json'
BASE = 'https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text='
UA = {'User-Agent': 'Mozilla/5.0 (know-graph-lab research)'}

SUB = str.maketrans('0123456789x', '₀₁₂₃₄₅₆₇₈₉ₓ')
# 🚨 ETCSL 轉寫頁不論 charenc 參數一律輸出 ASCII 轉寫：c＝š、j＝ĝ、h＝ḫ（大寫同理）。
#    蘇美語轉寫沒有單純的 c／j／h，所以整欄直接換回標準符號；英譯欄不可套用。
ASCII2STD = str.maketrans('cjhCJH', 'šĝḫŠĜḪ')


def get(key: str) -> str:
    """t.1.1.1 / c.1.1.1 / c.4.13* 。有快取就讀快取。"""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (key.replace('*', '_star') + '.html')
    if f.exists() and f.stat().st_size > 500:
        return f.read_text(encoding='utf-8')
    for attempt in range(3):
        try:
            r = requests.get(BASE + key, headers=UA, timeout=60)
            r.raise_for_status()
            f.write_text(r.text, encoding='utf-8')
            time.sleep(1.0)
            return r.text
        except requests.RequestException as e:
            print(f'    重試 {key}：{e}')
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f'抓不到 {key}')


def plain(fragment: str) -> str:
    s = re.sub(r'<sub>([^<]*)</sub>', lambda m: m.group(1).translate(SUB), fragment)
    s = re.sub(r'<sup>([^<]*)</sup>', r'{\1}', s)   # 限定符：dilmun{ki}
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def title_of(page: str) -> str:
    m = re.search(r'<h2>(.*?)</h2>', page, re.S)
    return plain(m.group(1)) if m else ''


def parse_translation(page: str):
    """回傳 [(pid, 行號範圍, 英文)]。
    🚨 哀歌的段落標記（「第一 kirugu」）在 <p> 與 <a> 之間夾了 &nbsp; 縮排；第一版沒認到，
       烏爾哀歌有 21 行轉寫因此找不到歸屬段落。"""
    out = []
    for m in re.finditer(r"<p>(?:\s|&nbsp;)*<a href='[^']*'>([^<]*)</a><a name='([^']+)'></a>(.*?)</p>", page, re.S):
        rng, pid, body = m.group(1).strip().rstrip('.'), m.group(2), plain(m.group(3))
        out.append((pid, rng, body))
    return out


def parse_transliteration(page: str):
    """回傳 [(行號, 所屬 pid, 轉寫)]。"""
    out = []
    for m in re.finditer(r"<tr><td[^>]*><a href='[^']*lineid=([^'&]+)'>([^<]*)</a><a name='[^']+'></a></td><td>(.*?)</td></tr>", page, re.S):
        pid, line, body = m.group(1), m.group(2).strip().rstrip('.'), plain(m.group(3))
        out.append((line, pid, body.translate(ASCII2STD)))
    return out


def parse_catalogue(page: str):
    """古代書目（0.x）只有轉寫頁，行號不帶連結：<td ...>12.</a><a name='c011.12'>。
    🚨 第一版改用 enumerate 自己數，段號雖碰巧一樣，卻是自編流水號，違反「段號照抄」。"""
    out = []
    for m in re.finditer(r"<tr><td[^>]*>([^<]*)</a><a name='c[^']+'></a></td><td>(.*?)</td></tr>", page, re.S):
        out.append((m.group(1).strip().rstrip('.'), plain(m.group(2)).translate(ASCII2STD)))
    return out


def total_rows(page: str) -> int:
    """分母：轉寫頁上所有帶行號錨點的列，不經過上面那支 regex。"""
    return len(re.findall(r"<a name='c[\d.]+[^']*'></a>", page))


def align(num: str):
    t = get(f't.{num}')
    c = get(f'c.{num}')
    paras = parse_translation(t)
    lines = parse_transliteration(c)
    by_pid: dict[str, list[tuple[str, str]]] = {}
    for line, pid, body in lines:
        by_pid.setdefault(pid, []).append((line, body))
    segs, orphan_paras = [], 0
    for pid, rng, en in paras:
        ls = by_pid.pop(pid, [])
        if not ls:
            orphan_paras += 1
        segs.append({'ref': rng.replace('-', '–'), 'orig': '\n'.join(b for _, b in ls),
                     'orig_lines': [l for l, _ in ls], 'en': en})
    orphan_lines = sum(len(v) for v in by_pid.values())
    stat = {'paras': len(paras), 'lines': len(lines), 'rows_on_page': total_rows(c),
            'orphan_paras': orphan_paras, 'orphan_lines': orphan_lines}
    return {'num': num, 'title_en': title_of(t), 'segments': segs}, stat


def vkey(n: str):
    # 數字與字母編號（2.4.2.a）混排：數字在前、字母在後，避免 int 與 str 互比擲錯
    return [(0, int(x), '') if x.isdigit() else (1, 0, x) for x in n.split('.')]


def expand(siglum: str) -> list[str]:
    """'ETCSL 1.8.1.5；1.8.1.5.1' / 'ETCSL 4.13.01–4.13.11' → 編號清單。"""
    s = siglum.replace('ETCSL', '').strip()
    nums = []
    for part in re.split(r'[；;]', s):
        part = part.strip()
        if not part:
            continue
        if '–' in part or '-' in part:
            a, b = [x.strip() for x in re.split(r'[–-]', part)]
            # 分類頁取兩端編號的共同前綴（6.1.01–6.2.5 → c.6*），只取前兩節會漏掉跨節的那一半
            pa, pb = a.split('.'), b.split('.')
            common = []
            for x, y in zip(pa, pb):
                if x != y:
                    break
                common.append(x)
            cat = get(f"c.{'.'.join(common or pa[:1])}*")
            # 分類頁去掉標籤後每篇一行「4.13.01 A balbale to Suen」。第一版要求編號後緊跟 < 或 :，
            # 五個合集全部展開成 0 篇——不報錯，只是那幾條默默沒有正文。
            text = html.unescape(re.sub(r'<[^>]+>', '\n', cat))
            cands = sorted(set(re.findall(r'(?m)^\s*(\d+(?:\.[\da-z]+)+)\s', text)), key=vkey)
            cands = [x for x in cands if vkey(a) <= vkey(x) <= vkey(b)]
            nums += cands
        else:
            nums.append(part)
    return nums


def sumer_entries():
    """從 data/near-east/sumer.ts 讀 slug 與 ETCSL 編號。一條一行的寫法，regex 足夠。"""
    src = (ROOT / 'data' / 'near-east' / 'sumer.ts').read_text(encoding='utf-8')
    out = []
    for m in re.finditer(r"slug: '([^']+)'[^\n]*?siglum: '(ETCSL [^']+)'", src):
        out.append((m.group(1), m.group(2)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    entries = sumer_entries()
    if a.only:
        entries = [e for e in entries if e[0] == a.only]
    print(f'蘇美藏有 ETCSL 編號的條目 {len(entries)} 條')
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {}
    bad = 0
    for slug, sig in entries:
        nums = expand(sig)
        if not nums:
            print(f'  ✗ {slug}：{sig} 展開為 0 篇'); bad += 1; continue
        comps, tot = [], {'paras': 0, 'lines': 0, 'rows_on_page': 0, 'orphan_paras': 0, 'orphan_lines': 0}
        for n in nums:
            if n.startswith('0.'):
                # 古代書目只有轉寫，沒有英譯頁
                c = get(f'c.{n}')
                ls = parse_catalogue(c)
                if len(ls) != total_rows(c):
                    print(f'  ⚠ {n}：書目頁解析 {len(ls)} 行，頁上 {total_rows(c)} 行'); bad += 1
                comps.append({'num': n, 'title_en': title_of(c), 'segments': [{'ref': l, 'orig': b, 'orig_lines': [l], 'en': ''} for l, b in ls if b]})
                continue
            comp, st = align(n)
            comps.append(comp)
            for k in tot:
                tot[k] += st[k]
        segs = sum(len(c['segments']) for c in comps)
        flag = '✓' if tot['orphan_lines'] == 0 and tot['lines'] == tot['rows_on_page'] else '⚠'
        if flag == '⚠':
            bad += 1
        print(f"  {flag} {slug:28} {len(nums):>2} 篇 {segs:>4} 段  轉寫 {tot['lines']}/{tot['rows_on_page']} 行  "
              f"無轉寫段 {tot['orphan_paras']}  無歸屬行 {tot['orphan_lines']}")
        if a.check:
            continue
        doc = {'slug': slug, 'source': 'ETCSL', 'siglum': sig,
               'source_url': f"https://etcsl.orinst.ox.ac.uk/cgi-bin/etcsl.cgi?text=t.{nums[0]}",
               'license': 'ETCSL（Oxford）轉寫與英譯，非商業學術使用', 'compositions': comps}
        (OUT / f'{slug}.json').write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
        has_en = any(s['en'] for c in comps for s in c['segments'])
        manifest[slug] = {'source': 'ETCSL', 'segments': segs, 'orig': 'ready', 'en': 'ready' if has_en else 'none', 'zh': 'none'}
    if not a.check:
        MANIFEST.write_text(json.dumps(dict(sorted(manifest.items())), ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'manifest {len(manifest)} 條 → {MANIFEST}')
    print(f'有問題 {bad} 條')


if __name__ == '__main__':
    main()
