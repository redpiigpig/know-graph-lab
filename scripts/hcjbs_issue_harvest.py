# -*- coding: utf-8 -*-
"""從宗教與文化學系站（ird）把某幾期《玄奘佛學研究》的完整篇目讀下來，含**英文篇名**。

為什麼不用 `public/content/Hsuan_Chuang_Studies/issues.json`：那份是模擬站用的，
`strip_en` 把每篇尾端的英譯裁掉了；但臺灣佛教研究中心站的每期頁面是**中英篇名並列**，
要照那個格式上稿就得回頭取英譯。

🚨 純讀取：只 GET 宗教系的公開頁面，不動那個站的任何內容。

用法：
    python -X utf8 scripts/hcjbs_issue_harvest.py 44 45            # 出 JSON
    python -X utf8 scripts/hcjbs_issue_harvest.py 44 45 --pdf      # 並把 PDF 下載到 c:/tmp/hcu-cms/pdf/
"""
import html
import json
import re
import sys
from pathlib import Path

import requests

BASE = 'https://www.hcu.edu.tw'
LIST = f'{BASE}/ird/ird/zh-tw/religious-journal/'
OUT = Path('c:/tmp/hcu-cms')
UA = {'User-Agent': 'Mozilla/5.0'}

ZH_NUM = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def zh_issue_no(text):
    """「第四十四期玄奘佛學研究學報」→ 44"""
    m = re.search(r'第([一二三四五六七八九十]+)期', text)
    if not m:
        return None
    s = m.group(1)
    if '十' in s:
        a, _, b = s.partition('十')
        return (ZH_NUM.get(a, 1) if a else 1) * 10 + (ZH_NUM.get(b, 0) if b else 0)
    return ZH_NUM.get(s)


def strip_tags(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


CJK = re.compile(r'[　-〿㐀-鿿＀-￯]')


def split_zh_en(title):
    """中英篇名黏在同一格，要切成兩段。

    🚨 不可用「遇到空白就切」——中文篇名裡本來就有空白（破折號前後）。
    🚨 也不可用「尾端全是 ASCII 字母」的正則：英譯裡有 (Saṃsāra) 的 ṃ、
       China1949-1967 的數字、Loka 的全形冒號，任一個都會讓比對停在英文中間，
       切出「ra) of the World of Buddhist Ethics ?」這種半截英譯。
    做法：找**最早**的那個 ASCII 字母位置，使得從它往後的字串幾乎不含中日文字
    （CJK 比例 < 8%），那裡就是英譯的起點。
    """
    for m in re.finditer(r'[A-Za-z]', title):
        rest = title[m.start():]
        if len(rest) < 12:
            break
        cjk = len(CJK.findall(rest))
        if cjk / len(rest) < 0.08:
            return title[:m.start()].strip(' -—–　'), rest.strip()
    return title.strip(), ''


def issue_index():
    """回 {期號: 該期頁面 URL}"""
    r = requests.get(LIST, headers=UA, timeout=60)
    r.raise_for_status()
    out = {}
    for href, txt in re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S):
        t = strip_tags(txt)
        n = zh_issue_no(t)
        if n and 'religious-journal' in href:
            out.setdefault(n, BASE + href if href.startswith('/') else href)
    return out


def parse_issue(url):
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    h = r.text
    title = strip_tags(re.search(r'<title>(.*?)</title>', h, re.S).group(1))
    i = h.find('篇名')
    seg = h[max(0, i - 3000):]
    m = re.search(r'<table[^>]*>.*?</table>', seg, re.S)
    if not m:
        raise SystemExit(f'找不到篇目表：{url}')
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(0), re.S)

    items = []
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S)
        texts = [strip_tags(c) for c in cells]
        if not any(texts):
            continue
        if texts[0] in ('篇名',):            # 表頭
            continue
        if len(cells) == 1 or (len(texts) > 1 and not texts[1] and not texts[-1]):
            t = texts[0]
            if t:
                items.append({'kind': 'section', 'label': t.lstrip('❖').strip()})
            continue
        pdf = re.search(r'href="([^"]+)"', cells[0])
        zh, en = split_zh_en(texts[0])
        items.append({
            'kind': 'article',
            'title_zh': zh,
            'title_en': en,
            'author': texts[1] if len(texts) > 1 else '',
            'page': texts[2] if len(texts) > 2 else '',
            'pdf': (BASE + pdf.group(1)) if pdf and pdf.group(1).startswith('/') else (pdf.group(1) if pdf else ''),
        })
    # 出版日期：只認標題後面那個「2025.11.05( 週三. )」的格式。
    # 🚨 別拿「第一個看起來像日期的字串」——頁面上還有最後更新日期、圖片路徑裡的
    #    2026-01/2026010715… 等等，抓錯會把顯示日期設成無關的日子。
    d = re.search(r'(\d{4})\.(\d{2})\.(\d{2})\s*\(\s*週', h)
    date = f'{d.group(1)}-{d.group(2)}-{d.group(3)}' if d else ''
    return {'page_title': title, 'url': url, 'date': date, 'items': items}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    want = [int(a) for a in args] or [44, 45]
    idx = issue_index()
    OUT.mkdir(parents=True, exist_ok=True)

    result = {}
    for n in want:
        if n not in idx:
            print(f'❌ 第 {n} 期不在列表頁')
            continue
        data = parse_issue(idx[n])
        arts = [x for x in data['items'] if x['kind'] == 'article']
        secs = [x for x in data['items'] if x['kind'] == 'section']
        no_en = [x['title_zh'] for x in arts if not x['title_en']]
        no_pdf = [x['title_zh'] for x in arts if not x['pdf'].startswith('http')]
        print(f"第{n}期 {data['page_title']}  日期={data['date']}  "
              f"篇數={len(arts)} 專輯標={len(secs)} 缺英譯={len(no_en)} 缺PDF={len(no_pdf)}")
        for t in no_en:
            print(f'   ⚠ 無英文篇名：{t[:40]}')
        for t in no_pdf:
            print(f'   ⚠ 無 PDF：{t[:40]}')
        result[n] = data

    fp = OUT / 'issues-harvest.json'
    fp.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'→ {fp}')

    if '--pdf' in sys.argv:
        pdir = OUT / 'pdf'
        pdir.mkdir(exist_ok=True)
        fallback = load_fallbacks()
        for n, data in result.items():
            for k, a in enumerate([x for x in data['items'] if x['kind'] == 'article'], 1):
                # 🚨 宗教系站上有些連結被貼成編輯者的 file:///C:/… 本機路徑。
                #    那**不代表檔案不存在**——第 45 期五篇就是這樣，檔案其實都在，
                #    只是頁面上的檔名跟實際的不一樣。先往後備來源找。
                url = a['pdf'] if a['pdf'].startswith('http') else None
                local = None
                if not url:
                    url, local = pick_fallback(fallback, n, k, a['title_zh'])
                    if url or local:
                        print(f"  ↩ 頁面連結壞掉，改用{'本機 Drive' if local else ' issues.json'}："
                              f"{a['title_zh'][:24]}")
                if local:
                    name = f"{n}-{k}{a['title_zh']}"[:90].replace('/', '／') + '.pdf'
                    dest = pdir / name
                    if not (dest.exists() and dest.stat().st_size > 10000):
                        dest.write_bytes(Path(local).read_bytes())
                    print(f"  ✔ {name[:46]}  {dest.stat().st_size // 1024} KB（本機）")
                    a['local'] = str(dest)
                    continue
                if not url:
                    print(f"  ❌ 三個來源都沒有：{a['title_zh'][:30]}")
                    continue
                a['pdf'] = url
                name = f"{n}-{k}{a['title_zh']}"[:90].replace('/', '／') + '.pdf'
                dest = pdir / name
                if dest.exists() and dest.stat().st_size > 10000:
                    print(f'  已有 {name}')
                    a['local'] = str(dest)
                    continue
                rr = requests.get(a['pdf'], headers=UA, timeout=180)
                ok = rr.ok and rr.content[:4] == b'%PDF'
                print(f"  {'✔' if ok else '❌'} {name}  {len(rr.content)//1024} KB")
                if ok:
                    dest.write_bytes(rr.content)
                    a['local'] = str(dest)
        fp.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'→ {fp}（已補 local 路徑）')


if __name__ == '__main__':
    main()
