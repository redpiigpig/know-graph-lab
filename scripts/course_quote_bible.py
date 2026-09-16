# -*- coding: utf-8 -*-
r"""課堂簡報用的經文取源 —— 和合本修訂版（cuv2010）＋思高本（sigao）。

🚨 **經文不靠背誦。** 投影在課堂上的引文若錯一個字，學生不會發現，我也不會發現，
   下一次重出還是錯的——這正是 [[feedback_reader_silent_failures]] 說的
   「印出正常頁面卻配錯內容」。所以一律從版本庫逐節取回。

經文本體 2026-07-08 起不在 Supabase（超量救援），存成每卷一檔的 gz JSON：
  R2 `bible-verses/{code}.json.gz`（正本；server/utils/bible-verses.ts 同一份）
  格式 {book_code, chapters: {"1": [{v: 1, t: {cuv2010: "…", sigao: "…"}}]}}
🚨 nuxt.config 的本機預設路徑 `G:/我的雲端硬碟/資料/聖經/_verses` **現在不存在**，
   別照那條路徑找，會得到「查無此卷」而不是報錯。

取回的原文快取到 output/source-cache/course-quotes/（不進版控），
真正進版控的是 build_course_quotes.py 產出的 course_slides_quotes.py——
文字烘進去之後重出簡報不需要網路，也不會因為我改寫而漂移。

用法（作為模組）：
    from course_quote_bible import passage
    lines = passage('mrk', 1, 14, 15)            # 和修
    lines = passage('mrk', 1, 14, 15, 'sigao')   # 思高
"""
import gzip
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / 'output' / 'source-cache' / 'course-quotes'

# 本課程只用這兩個譯本（使用者 2026-09-16 定）：和合本修訂版為主，
# 講到天主教／東正教傳統的段落並列思高本。
MAIN, ALT = 'cuv2010', 'sigao'
ALT_LABEL = '思高本'

# 🚨 **和合本修訂版（cuv2010）的詩體經文在語料裡是殘的。**
#    2026-09-16 量過：凡有對句的節只存了第一行——詩篇 88.5%、箴言 91.0%、
#    以賽亞 78.1% 的節都短於和合本；散文書卷只有 2–4%。
#    例：詩篇 23:1 只有「耶和華是我的牧者，」，少了「我必不致缺乏。」
#        馬太 5:3 只有「心靈貧窮的人有福了！」，少了「因為天國是他們的。」
#    其他中文譯本（cuv1919／sigao／lzz／peking）都是完整的，所以這是
#    cuv2010 這一版的匯入問題，不是語料整體的問題。
#    → 取文時逐節比對和合本長度，疑似被截斷就**丟例外**，逼我換版本；
#      印半句經文上投影片是典型「看起來正常的失敗」，沒有人會發現。
CHECK = 'cuv1919'
TRUNC_RATIO = 0.62

# 書卷代碼＝R2 上的檔名（三字母）。只列課程會用到的。
BOOKS = {
    'gen': '創世記', 'exo': '出埃及記', 'deu': '申命記', 'psa': '詩篇',
    'isa': '以賽亞書', 'jer': '耶利米書', 'ezk': '以西結書', 'dan': '但以理書',
    'mat': '馬太福音', 'mrk': '馬可福音', 'luk': '路加福音', 'jhn': '約翰福音',
    'act': '使徒行傳', 'rom': '羅馬書', '1co': '哥林多前書', '2co': '哥林多後書',
    'gal': '加拉太書', 'eph': '以弗所書', 'php': '腓立比書', 'col': '歌羅西書',
    'phm': '腓利門書', 'heb': '希伯來書', 'jas': '雅各書', '1pe': '彼得前書',
    '1jn': '約翰一書', 'rev': '啟示錄', '2ma': '瑪加伯下', 'sir': '德訓篇',
}

_docs = {}


def _env():
    for ln in (ROOT / '.env').read_text(encoding='utf-8').splitlines():
        if '=' in ln and not ln.strip().startswith('#'):
            k, _, v = ln.partition('=')
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def _load(code):
    """一卷的全部經文。先讀本機快取，沒有才去 R2 抓並落快取。"""
    if code in _docs:
        return _docs[code]
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f'{code}.json'
    if f.exists():
        doc = json.loads(f.read_text(encoding='utf-8'))
    else:
        _env()
        import boto3
        s3 = boto3.client(
            's3', region_name='auto', endpoint_url=os.environ['R2_ENDPOINT'],
            aws_access_key_id=os.environ['R2_ACCESS_KEY'],
            aws_secret_access_key=os.environ['R2_SECRET_KEY'])
        raw = s3.get_object(Bucket=os.environ['R2_BUCKET'],
                            Key=f'bible-verses/{code}.json.gz')['Body'].read()
        doc = json.loads(gzip.decompress(raw))
        # 只留課程要用的兩個譯本，快取才不會一卷好幾 MB
        for ch in doc['chapters'].values():
            for v in ch:
                v['t'] = {k: t for k, t in v['t'].items()
                          if k in (MAIN, ALT, CHECK)}
        f.write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
    _docs[code] = doc
    return doc


def verses(code, chapter, start, end=None, version=MAIN):
    """回傳 [(節號, 經文), ...]。

    🚨 查無此節就**丟例外**，不要回空的。回空的話投影片會印出一片空白的引文框，
       版面正常、稽核全過，只有內容不見了。
    """
    end = end or start
    doc = _load(code)
    got = [(v['v'], v['t'].get(version, '').strip())
           for v in doc['chapters'].get(str(chapter), [])
           if start <= v['v'] <= end and v['t'].get(version)]
    want = end - start + 1
    if len(got) != want:
        raise LookupError(
            f'{code} {chapter}:{start}-{end}（{version}）取到 {len(got)} 節、'
            f'應有 {want} 節——書卷代碼或節號有誤')
    if version == MAIN:
        check = {v['v']: v['t'].get(CHECK, '')
                 for v in doc['chapters'].get(str(chapter), [])}
        bad = [n for n, t in got
               if check.get(n) and len(t) < len(check[n]) * TRUNC_RATIO]
        if bad:
            raise LookupError(
                f'{code} {chapter}:{start}-{end} 的第 {bad} 節在和合本修訂版裡'
                f'疑似只存了詩體的第一行（見本檔頂的說明）。'
                f'這一段改用 version="cuv1919"（和合本）或 "sigao"（思高本），'
                f'不要照 cuv2010 印半句經文上投影片。')
    return got


def ref(code, chapter, start, end=None, version=MAIN):
    """人看的出處字串：『馬可福音 1:14–15（和合本修訂版）』。"""
    label = {MAIN: '和合本修訂版', ALT: '思高本', CHECK: '和合本'}[version]
    rng = f'{start}' if not end or end == start else f'{start}–{end}'
    return f'{BOOKS[code]} {chapter}:{rng}（{label}）'


def passage(code, chapter, start, end=None, version=MAIN, numbers=False):
    """把一段經文排成投影片要的行。

    numbers=True 會在每節前加上節號（長段落才需要，短引文加了反而吵）。
    """
    out = []
    for n, t in verses(code, chapter, start, end, version):
        out.append(f'{n}　{t}' if numbers else t)
    return out


# 退版紀錄：哪幾段因為和修殘缺而改用和合本。build_course_quotes 會印出來，
# 這樣「為什麼這張投影片標的是和合本」永遠有帳可查，不是靜靜換掉。
FELL_BACK = []


def bible(code, chapter, start, end=None, numbers=False):
    """取一段經文，回傳 (行, 出處)。

    先用和合本修訂版；該段若踩到詩體殘缺就退回和合本，並記進 FELL_BACK。
    🚨 退版是**看得見的**——出處行會照實印「（和合本）」，投影片上分得出來。
    """
    try:
        return (passage(code, chapter, start, end, MAIN, numbers),
                ref(code, chapter, start, end, MAIN))
    except LookupError as e:
        if '詩體' not in str(e):
            raise
        FELL_BACK.append(ref(code, chapter, start, end, MAIN))
        return (passage(code, chapter, start, end, CHECK, numbers),
                ref(code, chapter, start, end, CHECK))
