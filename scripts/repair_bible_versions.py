#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""聖經語料修補 —— 和合本修訂版的詩體截斷、淺文理的夾註混入、東正教譯本補齊。

## 背景（2026-09-16 稽核）

| 版本 | 狀況 |
|---|---|
| `cuv2010` 和合本修訂版 | **7,208 節被截斷（23.3%）**；詩篇 88.5%、箴言 91.0%、約伯 80.0%、以賽亞 78.1% |
| `cuv1919` 官話和合本 | 良好 |
| `cuv1919w` 文理和合本 | 良好（夾註僅 1 處） |
| `cuv1919e` 淺文理 | **3,156 節（10.2%）夾註混入正文** |
| 東正教中文譯本 | **完全沒有** |

### cuv2010 為什麼會缺

`ingest_bible_verses.CUV_BV_PAIR` 寫成 `<b>(\d+)</b>\s*<span>(.*?)</span>`，
只吃得到節號後**第一個** `<span>`。而 rcuv.hkbs.org.hk 的詩體是這樣排的：

    <p class="p1"><b>1</b><span>耶和華是我的牧者，</span></p>
    <p class="p2"><span>我必不致缺乏。</span></p>      ← 沒有 <b>，整行被丟掉

散文每節只有一個 `<span>`，所以散文書卷幾乎沒事（2–4%），詩體書卷就垮了。
🚨 這是典型「看起來正常的失敗」：節數對得上、版面正常、稽核全過，只有半句經文不見了。

## 資料流

經文本體不在 Supabase（2026-07-08 超量救援搬走，**大表禁止搬回**），
正本是 R2 `bible-verses/{book}.json.gz`。所以修補一律：
    R2 下載 → 本機 output/source-cache/bible-verses/ → 就地修補 → 傳回 R2。

## 用法

    python scripts/repair_bible_versions.py audit          # 盤點各版本缺損
    python scripts/repair_bible_versions.py rcuv           # 重抓和合本修訂版
    python scripts/repair_bible_versions.py orthodox       # 抓東正教三譯本
    python scripts/repair_bible_versions.py merge <版本>    # 併進本機卷檔
    python scripts/repair_bible_versions.py upload         # 推回 R2
"""
from __future__ import annotations

import gzip
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / 'output' / 'source-cache' / 'bible-verses'      # R2 卷檔的本機副本
STAGE = ROOT / 'output' / 'source-cache' / 'bible-repair'      # 重抓下來的版本
R2_PREFIX = 'bible-verses/'

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def env():
    out = {}
    for ln in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
        if '=' in ln and not ln.strip().startswith('#'):
            k, _, v = ln.partition('=')
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


ENV = env()


def r2():
    import boto3
    return boto3.client(
        's3', region_name='auto', endpoint_url=ENV['R2_ENDPOINT'],
        aws_access_key_id=ENV['R2_ACCESS_KEY'],
        aws_secret_access_key=ENV['R2_SECRET_KEY'])


# ════════════════════════════════════════════════════════════════════════
# 和合本修訂版（rcuv.hkbs.org.hk）
# ════════════════════════════════════════════════════════════════════════

RCUV_BASE = 'https://rcuv.hkbs.org.hk/bb/info/RCUV2'   # RCUV2＝上帝版、RCUV1＝神版
RCUV_BOOKS = {
    'gen': 'GEN', 'exo': 'EXO', 'lev': 'LEV', 'num': 'NUM', 'deu': 'DEU',
    'jos': 'JOS', 'jdg': 'JDG', 'rut': 'RUT',
    '1sa': '1SA', '2sa': '2SA', '1ki': '1KI', '2ki': '2KI',
    '1ch': '1CH', '2ch': '2CH', 'ezr': 'EZR', 'neh': 'NEH', 'est': 'EST',
    'job': 'JOB', 'psa': 'PSA', 'pro': 'PRO', 'ecc': 'ECC', 'sng': 'SNG',
    'isa': 'ISA', 'jer': 'JER', 'lam': 'LAM', 'ezk': 'EZK', 'dan': 'DAN',
    'hos': 'HOS', 'jol': 'JOL', 'amo': 'AMO', 'oba': 'OBA', 'jon': 'JON',
    'mic': 'MIC', 'nam': 'NAM', 'hab': 'HAB', 'zep': 'ZEP', 'hag': 'HAG',
    'zec': 'ZEC', 'mal': 'MAL',
    'mat': 'MAT', 'mrk': 'MRK', 'luk': 'LUK', 'jhn': 'JHN', 'act': 'ACT',
    'rom': 'ROM', '1co': '1CO', '2co': '2CO', 'gal': 'GAL', 'eph': 'EPH',
    'php': 'PHP', 'col': 'COL', '1th': '1TH', '2th': '2TH', '1ti': '1TI',
    '2ti': '2TI', 'tit': 'TIT', 'phm': 'PHM', 'heb': 'HEB', 'jas': 'JAS',
    '1pe': '1PE', '2pe': '2PE', '1jn': '1JN', '2jn': '2JN', '3jn': '3JN',
    'jud': 'JUD', 'rev': 'REV',
}

# 分段標題與詩題不是經文，先整塊拿掉；<sup> 是註腳標記，也拿掉。
RCUV_DROP = re.compile(r'<h[1-6][^>]*>.*?</h[1-6]>|<sup[^>]*>.*?</sup>|<sup[^>]*/?>',
                       re.DOTALL)
# 🚨 節號可能是**範圍**：RCUV 把合併處理的經節印成 `<b>18-19</b>`
#    （詩篇 116 結尾就是）。只認 `<b>(\d+)</b>` 的話，那一段既不會建立第 18 節，
#    也不會被當成新節的開頭——整段文字就默默黏到第 17 節尾巴去。
#    實測全書 65 章、100 節中招。合併節一律掛在**範圍的第一個節號**上。
RCUV_VNUM = re.compile(r'<b>(\d+)(?:[-–](\d+))?</b>')


def rcuv_parse(html):
    """把一章的 HTML 解析成 {節號: 經文}。

    🚨 **關鍵**：從 `<b>N</b>` 一路吃到下一個 `<b>M</b>`，把中間所有 `<span>`
       都收進來——詩體的續行是獨立的 `<p class="p2"><span>…</span></p>`，
       沒有自己的節號。舊版只取第一個 `<span>`，所以整段對句只留下第一行。
    """
    html = RCUV_DROP.sub('', html)
    marks = list(RCUV_VNUM.finditer(html))
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(html)
        chunk = html[m.end():end]
        # 取這一段裡的每一個 <span> 內容（詩體一行一個），依序接起來
        parts = re.findall(r'<span[^>]*>(.*?)</span>', chunk, re.DOTALL)
        text = ''.join(parts) if parts else chunk
        text = re.sub(r'</?i>', '', text)          # <i> 是專名，保留內文
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            out[int(m.group(1))] = text
    return out


def scrape_rcuv(only=None):
    STAGE.mkdir(parents=True, exist_ok=True)
    out_f = STAGE / 'cuv2010.json'
    got = json.loads(out_f.read_text(encoding='utf-8')) if out_f.exists() else {}
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5.0 (research; Bible parallel study)'
    # 章數直接看本機卷檔，不必再問 DB
    for code, hk in RCUV_BOOKS.items():
        if only and code != only:
            continue
        f = CACHE / f'{code}.json.gz'
        if not f.exists():
            print(f'  ! 本機沒有 {code}，略過', file=sys.stderr)
            continue
        n_ch = len(json.loads(gzip.decompress(f.read_bytes()))['chapters'])
        book = got.setdefault(code, {})
        for ch in range(1, n_ch + 1):
            if str(ch) in book:
                continue
            try:
                r = sess.get(f'{RCUV_BASE}/{hk}/{ch}/', timeout=30)
            except Exception as e:
                print(f'    ✗ {code} {ch}: {e}', file=sys.stderr)
                continue
            if r.status_code != 200:
                print(f'    ✗ {code} {ch}: HTTP {r.status_code}', file=sys.stderr)
                continue
            body = r.text
            i = body.find('<')
            verses = rcuv_parse(body[i:]) if i >= 0 else {}
            if not verses:
                print(f'    ✗ {code} {ch}: 解析到 0 節', file=sys.stderr)
                continue
            book[str(ch)] = {str(k): v for k, v in sorted(verses.items())}
            time.sleep(0.25)
        out_f.write_text(json.dumps(got, ensure_ascii=False), encoding='utf-8')
        n = sum(len(c) for c in book.values())
        print(f'  ✔ {code} {n_ch} 章 / {n} 節', flush=True)
    return out_f


# ════════════════════════════════════════════════════════════════════════
# 恢復本（line.twgbr.org）
#
# 🚨 **舊資料整本 31,081 節都是亂碼（100%）。** 根因兩層：
#    1. 來源站回 `Content-Type: text/html` **沒有 charset**，requests 依 HTTP
#       規範退回 ISO-8859-1，於是 UTF-8 位元組被逐一解成拉丁字元。
#    2. 接著 `re.sub(r'\s+', ' ')` 又把其中的 0xA0 與 0x85 位元組換成空白——
#       Python 的 `\s` 連 NBSP 與 NEL 都吃。連續兩個還會併成一個。
#    所以**不能用程式還原**：0x20 到底原本是 0xA0 還是 0x85 已經分不出來，
#    硬還原會產出「恩堸」這種看起來像字、其實錯字的結果（實測只救得回 98%）。
#    → 一律重抓，而且 `resp.encoding` 要**明講**，不要讓 requests 去猜。
# ════════════════════════════════════════════════════════════════════════

RCV_BASE = 'https://line.twgbr.org/recoveryversion/bible'
RCV_BOOKS = [  # 檔名是 01..66，順序即新教正典順序
    'gen', 'exo', 'lev', 'num', 'deu', 'jos', 'jdg', 'rut', '1sa', '2sa',
    '1ki', '2ki', '1ch', '2ch', 'ezr', 'neh', 'est', 'job', 'psa', 'pro',
    'ecc', 'sng', 'isa', 'jer', 'lam', 'ezk', 'dan', 'hos', 'jol', 'amo',
    'oba', 'jon', 'mic', 'nam', 'hab', 'zep', 'hag', 'zec', 'mal',
    'mat', 'mrk', 'luk', 'jhn', 'act', 'rom', '1co', '2co', 'gal', 'eph',
    'php', 'col', '1th', '2th', '1ti', '2ti', 'tit', 'phm', 'heb', 'jas',
    '1pe', '2pe', '1jn', '2jn', '3jn', 'jud', 'rev',
]
RCV_CHAPTER = re.compile(r'<h3\s+id="C(\d+)\w*">', re.DOTALL)
RCV_PARA = re.compile(r'<p\s+class="calibre2">(.*?)</p>', re.DOTALL)
RCV_VERSE = re.compile(r'<sup>(\d+)</sup>(.*?)(?=<sup>\d+</sup>|$)', re.DOTALL)


def scrape_rcv(only=None):
    STAGE.mkdir(parents=True, exist_ok=True)
    out_f = STAGE / 'rcv_zh.json'
    got = json.loads(out_f.read_text(encoding='utf-8')) if out_f.exists() else {}
    sess = requests.Session()
    sess.headers['User-Agent'] = 'Mozilla/5.0 (research; Bible parallel study)'
    for idx, code in enumerate(RCV_BOOKS, start=1):
        if only and code != only:
            continue
        if code in got:
            continue
        try:
            r = sess.get(f'{RCV_BASE}/{idx:02d}.html', timeout=60)
        except Exception as e:
            print(f'  ✗ {code}: {e}', file=sys.stderr)
            continue
        if r.status_code != 200:
            print(f'  ✗ {code}: HTTP {r.status_code}', file=sys.stderr)
            continue
        # 🚨 就是這一行。不指定的話 requests 會退回 ISO-8859-1，整本變亂碼。
        r.encoding = 'utf-8'
        html = r.text
        marks = list(RCV_CHAPTER.finditer(html))
        if not marks:
            print(f'  ✗ {code}: 找不到章標記', file=sys.stderr)
            continue
        book = {}
        for i, m in enumerate(marks):
            ch = m.group(1)
            seg = html[m.end():(marks[i + 1].start() if i + 1 < len(marks) else len(html))]
            verses = {}
            for para in RCV_PARA.finditer(seg):
                for vm in RCV_VERSE.finditer(para.group(1)):
                    txt = re.sub(r'<[^>]+>', '', vm.group(2))
                    # 🚨 只收斂**真正的** ASCII 空白，別再碰 \s（那會吃掉 NBSP）
                    txt = re.sub(r'[ \t\r\n]+', ' ', txt).strip()
                    if txt:
                        verses[vm.group(1)] = txt
            if verses:
                book[ch] = verses
        got[code] = book
        out_f.write_text(json.dumps(got, ensure_ascii=False), encoding='utf-8')
        n = sum(len(c) for c in book.values())
        print(f'  ✔ {code} {len(book)} 章 / {n} 節', flush=True)
        time.sleep(0.3)
    return out_f


# ════════════════════════════════════════════════════════════════════════
# 信望愛（bible.fhl.net）—— 中文譯本最齊全的開放 JSON 來源，87 個版本。
#
# 這一支一次補齊三類本來缺的東西：
#   淺文理：`ssewb` 施約瑟淺文理譯本（全書）、`cuwve` 淺文理和合本（僅新約）
#   東正教：`nt1864` 新遺詔聖經、`orthdox` 俄羅斯正教文理譯本、`cogorw` 高連茨基聖詠經
#   天主教：思高以外的十餘種歷史譯本
#
# 🚨 **書卷一定要用 `chineses=` 參數，不可以用 `engs=`。**
#    實測 `engs=Matt&version=nt1864` 會**靜靜回傳羅馬書**（回應裡的 chineses 欄是「羅」），
#    HTTP 200、status success、節數也像模像樣。照這樣抓，整本書卷全錯而且看不出來。
#    所以每一次回應都要核對 `record[0]['chineses']` 是不是我們要的那一卷，不符就中止。
# ════════════════════════════════════════════════════════════════════════

FHL_API = 'https://bible.fhl.net/json/qb.php'
# 我們的代碼 → 信望愛的中文簡稱
FHL_BOOKS = {
    'gen': '創', 'exo': '出', 'lev': '利', 'num': '民', 'deu': '申',
    'jos': '書', 'jdg': '士', 'rut': '得', '1sa': '撒上', '2sa': '撒下',
    '1ki': '王上', '2ki': '王下', '1ch': '代上', '2ch': '代下',
    'ezr': '拉', 'neh': '尼', 'est': '斯', 'job': '伯', 'psa': '詩',
    'pro': '箴', 'ecc': '傳', 'sng': '歌', 'isa': '賽', 'jer': '耶',
    'lam': '哀', 'ezk': '結', 'dan': '但', 'hos': '何', 'jol': '珥',
    'amo': '摩', 'oba': '俄', 'jon': '拿', 'mic': '彌', 'nam': '鴻',
    'hab': '哈', 'zep': '番', 'hag': '該', 'zec': '亞', 'mal': '瑪',
    'mat': '太', 'mrk': '可', 'luk': '路', 'jhn': '約', 'act': '徒',
    'rom': '羅', '1co': '林前', '2co': '林後', 'gal': '加', 'eph': '弗',
    'php': '腓', 'col': '西', '1th': '帖前', '2th': '帖後',
    '1ti': '提前', '2ti': '提後', 'tit': '多', 'phm': '門', 'heb': '來',
    'jas': '雅', '1pe': '彼前', '2pe': '彼後', '1jn': '約一', '2jn': '約二',
    '3jn': '約三', 'jud': '猶', 'rev': '啟',
}
NT_BOOKS = [c for c in FHL_BOOKS if c in (
    'mat', 'mrk', 'luk', 'jhn', 'act', 'rom', '1co', '2co', 'gal', 'eph',
    'php', 'col', '1th', '2th', '1ti', '2ti', 'tit', 'phm', 'heb', 'jas',
    '1pe', '2pe', '1jn', '2jn', '3jn', 'jud', 'rev')]


def fhl_chapter(version, code, ch, sess):
    """抓一章。回傳 {節號: 經文}；書卷對不上就丟例外。"""
    zh = FHL_BOOKS[code]
    r = sess.get(FHL_API, params={'chineses': zh, 'chap': ch,
                                  'version': version}, timeout=45)
    d = json.loads(r.text)
    if d.get('status') != 'success':
        return {}
    recs = d.get('record') or []
    if not recs:
        return {}
    got = recs[0].get('chineses')
    if got and got != zh:
        raise RuntimeError(
            f'信望愛回錯書卷：要 {zh}（{code}）卻回 {got}。'
            f'這是 engs/chineses 參數那個坑，不要照收。')
    out = {}
    for x in recs:
        t = x.get('bible_text') or ''
        # 🚨 有些版本（高連茨基聖詠經）的 bible_text 裡夾著 <p>/<h1> 標籤與
        #    章題，不剝掉會把標記當經文存進去。
        t = re.sub(r'<[^>]+>', ' ', t)
        # 只收斂真正的 ASCII 空白，不要用 \s——那會連 NBSP 一起吃掉，
        # 正是恢復本整本壞掉的第二層原因。
        t = re.sub(r'[ \t\r\n]+', ' ', t).strip()
        if t:
            out[str(x['sec'])] = t
    return out


def scrape_fhl(version, our_code, nt_only=False, books=None):
    """把信望愛某個版本抓成 STAGE/{our_code}.json。"""
    STAGE.mkdir(parents=True, exist_ok=True)
    out_f = STAGE / f'{our_code}.json'
    got = json.loads(out_f.read_text(encoding='utf-8')) if out_f.exists() else {}
    sess = requests.Session()
    sess.headers['User-Agent'] = 'know-graph-lab (course + study corpus)'
    targets = books or (NT_BOOKS if nt_only else list(FHL_BOOKS))
    for code in targets:
        if code in got:
            continue
        f = CACHE / f'{code}.json.gz'
        if not f.exists():
            continue
        n_ch = max(int(c) for c in
                   json.loads(gzip.decompress(f.read_bytes()))['chapters'])
        book, miss = {}, 0
        for ch in range(1, n_ch + 1):
            try:
                verses = fhl_chapter(version, code, ch, sess)
            except RuntimeError:
                raise
            except Exception as e:
                print(f'    ✗ {code} {ch}: {e}', file=sys.stderr)
                continue
            if verses:
                book[str(ch)] = verses
            else:
                miss += 1
                if miss > 3 and not book:
                    break          # 這一卷這個版本沒有，早點收手
            time.sleep(0.2)
        got[code] = book
        out_f.write_text(json.dumps(got, ensure_ascii=False), encoding='utf-8')
        n = sum(len(c) for c in book.values())
        print(f'  ✔ {code} {len(book)} 章 / {n} 節', flush=True)
    return out_f


# ════════════════════════════════════════════════════════════════════════
# 新世界譯本（wol.jw.org，繁體中文）
#
# 信望愛沒有這一部（守望台自行發行、不授權第三方散布），所以直接讀 WOL。
# 書卷用聖經卷序 1..66（40＝馬太），與我們的順序一致。
#
# 🚨 解析**不能**用 `<span class="v">(.*?)</span>` 非貪婪抓——經文裡有巢狀
#    `<span class="underline">耶和華</span>`，非貪婪會停在那個 `</span>`，
#    詩篇 23:1 就變成「耶和華我必一無所缺」（少了「是我的牧人」），
#    馬太五章還會整整少掉兩節。跟和合本修訂版踩的是同一個坑：
#    **要切到下一個節錨點，不要停在第一個結束標籤。**
# 🚨 一節可能被拆成好幾個 `v{b}-{c}-{v}-1..n`（詩體一行一個），要接起來。
# ════════════════════════════════════════════════════════════════════════

NWT_URL = 'https://wol.jw.org/cmn-Hant/wol/b/r24/lp-ch/nwt/{book}/{ch}'
NWT_END = '<!-- Root element of lightbox -->'   # 正文容器到此為止，之後是頁面框架
NWT_DROP_A = re.compile(
    r'<a[^>]*class="[^"]*\b(?:vl|vx|vp|fn|b|cl)\b[^"]*"[^>]*>.*?</a>', re.S)
NWT_ORDER = [  # 我們的代碼，依聖經卷序 1..66
    'gen', 'exo', 'lev', 'num', 'deu', 'jos', 'jdg', 'rut', '1sa', '2sa',
    '1ki', '2ki', '1ch', '2ch', 'ezr', 'neh', 'est', 'job', 'psa', 'pro',
    'ecc', 'sng', 'isa', 'jer', 'lam', 'ezk', 'dan', 'hos', 'jol', 'amo',
    'oba', 'jon', 'mic', 'nam', 'hab', 'zep', 'hag', 'zec', 'mal',
    'mat', 'mrk', 'luk', 'jhn', 'act', 'rom', '1co', '2co', 'gal', 'eph',
    'php', 'col', '1th', '2th', '1ti', '2ti', 'tit', 'phm', 'heb', 'jas',
    '1pe', '2pe', '1jn', '2jn', '3jn', 'jud', 'rev',
]


def nwt_parse(html, book_no, ch):
    cut = html.find(NWT_END)
    if cut > 0:
        html = html[:cut]
    marks = list(re.finditer(
        r'<span id="v%d-%d-(\d+)-\d+" class="v">' % (book_no, ch), html))
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(html)
        s = NWT_DROP_A.sub('', html[m.end():end])
        s = re.sub(r'<[^>]+>', '', s)
        s = re.sub(r'[ \t\r\n]+', ' ', s).strip('   ')
        if s:
            n = int(m.group(1))
            out[n] = (out.get(n, '') + s).strip()
    return out


def scrape_nwt(only=None):
    STAGE.mkdir(parents=True, exist_ok=True)
    out_f = STAGE / 'nwt_zh.json'
    got = json.loads(out_f.read_text(encoding='utf-8')) if out_f.exists() else {}
    sess = requests.Session()
    sess.headers.update({
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/120.0 Safari/537.36'),
        'Accept-Language': 'zh-TW,zh;q=0.9'})
    for no, code in enumerate(NWT_ORDER, start=1):
        if only and code != only:
            continue
        if code in got:
            continue
        f = CACHE / f'{code}.json.gz'
        if not f.exists():
            continue
        n_ch = max(int(c) for c in
                   json.loads(gzip.decompress(f.read_bytes()))['chapters'])
        book = {}
        for ch in range(1, n_ch + 1):
            try:
                r = sess.get(NWT_URL.format(book=no, ch=ch), timeout=45)
                r.encoding = 'utf-8'
            except Exception as e:
                print(f'    ✗ {code} {ch}: {e}', file=sys.stderr)
                continue
            if r.status_code != 200:
                continue
            verses = nwt_parse(r.text, no, ch)
            if verses:
                book[str(ch)] = {str(k): v for k, v in sorted(verses.items())}
            time.sleep(0.35)
        got[code] = book
        out_f.write_text(json.dumps(got, ensure_ascii=False), encoding='utf-8')
        n = sum(len(c) for c in book.values())
        print(f'  ✔ {code} {len(book)} 章 / {n} 節', flush=True)
    return out_f


# ════════════════════════════════════════════════════════════════════════
# 高連茨基聖詠經（東正教，信望愛 `cogorw`）—— 七十士編號要轉成希伯來編號
#
# 🚨 **不轉會整本錯位一篇。** 東正教聖詠經照七十士編號，與我們庫裡（希伯來／
#    新教編號）差一號：問它第 23 篇，回來的內容是和合本的詩篇 24。
#    照收的話，每一篇都跟隔壁對照，而且看起來完全正常——沒有人會發現。
#
# 對照表是固定的，各段的節數都拿實際抓到的筆數驗過：
#    LXX 1–8     → Heb 1–8        （相同）
#    LXX 9       → Heb 9 ＋ Heb 10  （38 節 ＝ 20＋18 ✔）
#    LXX 10–112  → Heb 11–113     （＋1）
#    LXX 113     → Heb 114 ＋ 115   （26 節 ＝ 8＋18 ✔）
#    LXX 114     → Heb 116:1–9    （9 節 ✔）
#    LXX 115     → Heb 116:10–19  （10 節 ✔）
#    LXX 116–145 → Heb 117–146    （＋1）
#    LXX 146     → Heb 147:1–11   （11 節 ✔）
#    LXX 147     → Heb 147:12–20  （9 節 ✔）
#    LXX 148–150 → Heb 148–150    （相同）
#    LXX 151     → 次經，保留原號
# ════════════════════════════════════════════════════════════════════════

# 每篇第一節前面會有信望愛加的編號對照與篇題（「114,115 第一百十三聖詠 …」、
# 「第二分」是誦讀單元 kathisma），那些不是經文，要剝掉。
PSALTER_HEAD = re.compile(
    r'^[\d,:；;\-–—\s]*'
    r'(?:第[一二三四五六七八九十百零]+分\s*)?'
    r'(?:第[一二三四五六七八九十百零]+聖詠\s*)?')


# 拆篇處：七十士的一篇對到希伯來的兩篇，前一篇有幾節就在哪裡斷。
# 節數取自本機和合本，不寫死——版本間若有出入，以我們庫裡的為準。
SPLIT = {9: (9, 10), 113: (114, 115)}


def lxx_to_heb(ch, body_v, heb_len):
    """七十士篇號＋**本文節序**（已扣掉詩題）→ 希伯來篇號／節號。

    🚨 `body_v` 不是頁面上的節號。東正教聖詠經**把詩題算成經節**，和合本不算，
       而且各篇詩題長短不一（詩 9 佔 1 節、詩 50 佔 2 節、詩 113 佔 0 節）。
       所以偏移要用該篇實際的起始節號推算，不能寫死一個數字——
       寫死的話詩 10 會整篇差一節，而兩邊都像模像樣，看不出來。
    """
    if ch in SPLIT:
        a, b = SPLIT[ch]
        n = heb_len(a)
        return (a, body_v) if body_v <= n else (b, body_v - n)
    if ch <= 8:
        return ch, body_v
    if ch <= 112:
        return ch + 1, body_v
    if ch == 114:
        return 116, body_v
    if ch == 115:
        return 116, body_v + 9
    if ch <= 145:
        return ch + 1, body_v
    if ch == 146:
        return 147, body_v
    if ch == 147:
        return 147, body_v + 11
    return ch, body_v          # 148–150 相同；151 是次經，保留原號


def heb_lengths():
    """本機和合本的詩篇各篇節數，給拆篇與驗證用。"""
    doc = json.loads(gzip.decompress((CACHE / 'psa.json.gz').read_bytes()))
    out = {}
    for ch, vs in doc['chapters'].items():
        n = [v['v'] for v in vs if (v['t'].get('cuv1919') or '').strip()]
        if n:
            out[int(ch)] = max(n)
    return out


def scrape_psalter():
    """抓高連茨基聖詠經，轉成希伯來編號存成 STAGE/orth_psalter.json。

    轉完會**逐篇比對節數**——對不上就印出來。這是唯一靠得住的驗證：
    編號錯位之後兩邊都還是「一篇一篇的經文」，只有節數與內容對得起來才算數。
    """
    STAGE.mkdir(parents=True, exist_ok=True)
    out_f = STAGE / 'orth_psalter.json'
    sess = requests.Session()
    sess.headers['User-Agent'] = 'know-graph-lab (course + study corpus)'
    lens = heb_lengths()
    heb = {}
    for lxx in range(1, 152):
        try:
            raw = fhl_chapter('cogorw', 'psa', lxx, sess)
        except Exception as e:
            print(f'  ✗ LXX {lxx}: {e}', file=sys.stderr)
            continue
        if not raw:
            continue
        keys = sorted(int(k) for k in raw)
        # 🚨 偏移＝這一篇少掉的前幾節（詩題）。用實際起始節號推，不要寫死。
        offset = keys[0] - 1
        for k in keys:
            t = raw[str(k)]
            if k == keys[0]:
                t = PSALTER_HEAD.sub('', t)
            t = t.strip()
            if not t:
                continue
            hc, hv = lxx_to_heb(lxx, k - offset, lambda c: lens.get(c, 0))
            heb.setdefault(str(hc), {})[str(hv)] = t
        time.sleep(0.2)
        if lxx % 25 == 0:
            print(f'  … LXX {lxx} 篇', flush=True)
    out_f.write_text(json.dumps({'psa': heb}, ensure_ascii=False),
                     encoding='utf-8')
    bad = [(c, len(vs), lens.get(int(c), 0)) for c, vs in sorted(heb.items(), key=lambda x: int(x[0]))
           if int(c) <= 150 and len(vs) != lens.get(int(c), 0)]
    print(f'  ✔ 聖詠經 {len(heb)} 篇 / '
          f'{sum(len(c) for c in heb.values())} 節（已轉希伯來編號）')
    if bad:
        print(f'  ⚠ 節數與和合本不符的篇：{len(bad)} 篇')
        for c, a, b in bad[:20]:
            print(f'     第 {c} 篇：聖詠經 {a} 節 vs 和合本 {b} 節')
    else:
        print('  ✔ 一百五十篇節數全部與和合本一致')
    return out_f


# ════════════════════════════════════════════════════════════════════════
# 併回卷檔 / 上傳
# ════════════════════════════════════════════════════════════════════════

def merge(version):
    """把 STAGE/{version}.json 併進本機卷檔（覆蓋同版本既有文字）。"""
    src = json.loads((STAGE / f'{version}.json').read_text(encoding='utf-8'))
    changed = added = 0
    for code, chapters in src.items():
        f = CACHE / f'{code}.json.gz'
        if not f.exists():
            print(f'  ! 沒有卷檔 {code}', file=sys.stderr)
            continue
        doc = json.loads(gzip.decompress(f.read_bytes()))
        for ch, verses in chapters.items():
            rows = doc['chapters'].setdefault(ch, [])
            by_v = {r['v']: r for r in rows}
            for vs, text in verses.items():
                v = int(vs)
                if v in by_v:
                    old = by_v[v]['t'].get(version)
                    if old != text:
                        by_v[v]['t'][version] = text
                        changed += 1
                else:
                    rows.append({'v': v, 't': {version: text}})
                    added += 1
            rows.sort(key=lambda r: r['v'])
        f.write_bytes(gzip.compress(
            json.dumps(doc, ensure_ascii=False).encode('utf-8'), 9))
    print(f'  併入 {version}：改寫 {changed:,} 節、新增 {added:,} 節')


def upload(only=None):
    cl = r2()
    n = 0
    for f in sorted(CACHE.glob('*.json.gz')):
        code = f.stem.replace('.json', '')
        if only and code != only:
            continue
        cl.put_object(Bucket=ENV['R2_BUCKET'], Key=f'{R2_PREFIX}{code}.json.gz',
                      Body=f.read_bytes(), ContentType='application/gzip')
        n += 1
    print(f'  上傳 {n} 卷回 R2')


# ════════════════════════════════════════════════════════════════════════
# 稽核
# ════════════════════════════════════════════════════════════════════════

def audit():
    import collections
    trunc = collections.Counter()
    tot = collections.Counter()
    note = collections.Counter()
    for f in sorted(CACHE.glob('*.json.gz')):
        doc = json.loads(gzip.decompress(f.read_bytes()))
        code = doc['book_code']
        for vs in doc['chapters'].values():
            for v in vs:
                t = v['t']
                a, b = t.get('cuv2010', '').strip(), t.get('cuv1919', '').strip()
                if a and b:
                    tot[code] += 1
                    if len(a) < len(b) * 0.62:
                        trunc[code] += 1
                e = t.get('cuv1919e', '').strip()
                if e:
                    note['total'] += 1
                    if '原文作' in e or '或作' in e:
                        note['note'] += 1
    T, N = sum(trunc.values()), sum(tot.values())
    print(f'cuv2010 疑似截斷 {T:,}/{N:,} = {T/max(N,1):.1%}')
    for c in ('psa', 'pro', 'job', 'isa', 'lam', 'sng', 'mat', 'gen'):
        if tot[c]:
            print(f'   {c:4} {trunc[c]:5,}/{tot[c]:5,} = {trunc[c]/tot[c]:6.1%}')
    print(f"cuv1919e 夾註混入 {note['note']:,}/{note['total']:,}")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'audit'
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == 'audit':
        audit()
    elif cmd == 'rcuv':
        scrape_rcuv(arg)
    elif cmd == 'rcv':
        scrape_rcv(arg)
    elif cmd == 'psalter':
        scrape_psalter()
    elif cmd == 'nwt':
        scrape_nwt(arg)
    elif cmd == 'fhl':
        # 用法：fhl <信望愛版本> <我方代碼> [nt]
        nt = len(sys.argv) > 4 and sys.argv[4] == 'nt'
        scrape_fhl(arg, sys.argv[3], nt_only=nt)
    elif cmd == 'merge':
        merge(arg or 'cuv2010')
    elif cmd == 'upload':
        upload(arg)
    else:
        raise SystemExit(f'不認得的指令：{cmd}')
