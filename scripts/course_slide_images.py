# -*- coding: utf-8 -*-
"""課堂簡報用圖：從維基共享資源抓圖並記錄出處。

課堂投影要用的圖必須是公有領域或 CC 授權，且要標出處——本腳本只收
Commons 上授權明確的圖，把作者、授權、檔案頁一併寫進 manifest，
渲染時自動產生「圖片出處」頁。

圖檔與 manifest 放 Drive（成品不進 git）：
  G:\\我的雲端硬碟\\資料\\知識圖工作室\\教學\\115-1_世界宗教文化導論\\簡報\\圖片\\

用法：
  python scripts/course_slide_images.py            # 抓 IMAGES 裡還沒抓的
  python scripts/course_slide_images.py --recheck  # 連已抓的也重新查授權
"""
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TEACH = Path(r'G:\我的雲端硬碟\資料\知識圖工作室\教學')
FOLDERS = {'wr': '115-1_世界宗教文化導論', 'sl': '宗教系國文講義',
           'ch': '115-2_基督宗教概論'}
OUT = TEACH / FOLDERS['wr'] / '簡報' / '圖片'
MANIFEST = OUT / '_manifest.json'
UA = 'know-graph-lab-course-slides/1.0 (teaching material; contact via redpiigpig.com)'

# 可接受的授權（公有領域與各式 CC）；其餘一律跳過
OK_LICENSE = re.compile(r'public domain|cc[ -]?(by|zero|0)|cc0|pd-', re.I)

# key -> Commons 搜尋詞。key 會成為投影片裡引用的名稱。
IMAGES = {
    # ── 第 1 次：宗教是什麼、八個向度 ──
    'durkheim': 'Émile Durkheim portrait',
    'otto-rudolf': 'Rudolf Otto theologian',
    'eliade': 'Mircea Eliade portrait',
    'william-james': 'William James psychologist portrait',
    'quaker-meeting': 'Quaker meeting house interior plain',
    'theravada-temple': 'Temple of the Tooth Kandy interior',
    'catholic-cathedral': 'Cathedral interior baroque altar',
    'wangye-temple': 'Taiwanese temple Wang Ye',
    'max-muller': 'Friedrich Max Müller',

    # ── 第 2 次：信仰體制與範疇、分類 ──
    'talmud-page': 'Talmud page Vilna edition',
    'ifa-divination': 'Ifa divination board Yoruba',
    'sadhu-india': 'Sadhu Varanasi India',
    'kaaba-crowd': 'Kaaba Masjid al-Haram pilgrims',

    # ── 第 3 次：泛神論 ──
    'amis-harvest': 'Amis people harvest festival Taiwan',
    'paiwan-ritual': 'Paiwan Maleveq festival',
    'siraya-jar': 'Siraya Alizu kong-kai',
    'yoruba-orisha': 'Orisha Yoruba shrine',
    'navajo-sandpainting': 'Navajo sandpainting',
    'lakota-sundance': 'Sun Dance Lakota',
    'aboriginal-art': 'Australian Aboriginal rock art',
    'siberian-shaman': 'Buryat shaman ritual',
    'spinoza': 'Baruch Spinoza portrait',
    'whirling-dervishes': 'Whirling dervishes Mevlevi ceremony',
    'kabbalah-tree': 'Sefirot',
    'mount-athos': 'Mount Athos monastery',

    # ── 第 4 次：多神論 ──
    'enuma-elish': 'Enuma Elish tablet British Museum',
    'ziggurat-ur': 'Great Ziggurat of Ur',
    'weighing-heart': 'Hunefer Book of the Dead judgement scene',
    'ugarit-tablet': 'Ugarit cuneiform tablet Baal',
    'rigveda-manuscript': 'Rigveda manuscript',
    'parthenon': 'Parthenon Athens',
    'roman-sacrifice-relief': 'Roman relief sacrifice suovetaurilia',
    'thor-hammer': 'Mjolnir pendant Viking',
    'chichen-itza': 'El Castillo Chichen Itza',
    'templo-mayor': 'Templo Mayor Tenochtitlan model',
    'machu-picchu': 'Machu Picchu',
    'hindu-temple-gopuram': 'Meenakshi Temple gopuram',
    'sanqing': 'Three Pure Ones',
    'mazu-pilgrimage': 'Mazu pilgrimage Taiwan',
    'torii-gate': 'Fushimi Inari torii',

    # ── 第 5 次：一神論 ──
    'akhenaten': 'Akhenaten statue Amarna',
    'aten-relief': 'Aten relief Akhenaten family',
    'isaiah-scroll': 'Great Isaiah Scroll Dead Sea Scrolls',
    'western-wall': 'Western Wall Jerusalem prayer',
    'torah-scroll': 'Torah scroll open',
    'christ-pantocrator': 'Christ Pantocrator Sinai icon',
    'st-peters': 'St Peters Basilica interior',
    'quran-manuscript': 'Kufic Quran manuscript',
    'blue-mosque': 'Sultan Ahmed Mosque interior',
    'fire-temple': 'Zoroastrian fire temple Yazd',
    'golden-temple': 'Harmandir Sahib Golden Temple Amritsar',
    'lalish': 'Lalish Yazidi temple',

    # ── 第 6 次：實用神論（上）──
    'confucius-portrait': 'Confucius',
    'confucian-temple-rite': 'Confucius Temple ceremony Taiwan',
    'buddha-preaching': 'Buddha first sermon Sarnath sculpture',
    'buddhist-monks-alms': 'Buddhist monks alms round Thailand',
    'tibetan-debate': 'Sera Monastery monks debating',
    'gommateshwara': 'Gommateshwara statue Shravanabelagola',
    'jain-monk': 'Jain monk Digambara',

    # ── 第 7 次：現代世界的宗教 ──
    'darwin': 'Charles Darwin portrait',
    'nietzsche': 'Friedrich Nietzsche portrait',
    'jefferson-bible': 'Jefferson Bible',
    'vatican-ii': 'Second Vatican Council',
    'gandhi': 'Mahatma Gandhi portrait',
    'mlk': 'Martin Luther King Jr 1964',
    'pentecostal-worship': 'Pentecostal worship service',

    # ── 第 8 次：臺灣宗教 ──
    'taiwan-indigenous': 'Bunun people harvest ritual',
    'wangchuan-burning': 'Wang Yeh worship boat Taiwan',
    'mackay-george': 'George Leslie Mackay',
    'taiwan-presbyterian-church': 'Presbyterian church Taiwan historic',
    'taipei-mosque': 'Taipei Grand Mosque',
    'longshan-temple': 'Lungshan Temple Taipei',
    'jingu-shrine-remains': 'Taoyuan Shinto Shrine Taiwan',
}


def get(url, timeout=60, tries=5):
    """帶退避的取用。Commons 對連續請求會回 429／503，必須退避重試而不是放棄。"""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            return urllib.request.urlopen(req, timeout=timeout).read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503, 500) and i < tries - 1:
                wait = float(e.headers.get('Retry-After') or 0) or (2 ** i) * 3
                time.sleep(wait + random.random())
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if i < tries - 1:
                time.sleep((2 ** i) * 2)
                continue
            raise


def api(params):
    url = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(params)
    return json.loads(get(url, timeout=40))


def strip_html(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


# 只取搜尋第一筆會出事：查「Rudolf Otto」得到他的墓碑、查「Siraya」得到西拉雅大道的
# 紅綠燈、查「秤心審判」得到歐西里斯像。這是「看起來成功卻配錯內容」的典型。
# 因此改為對候選評分：標題要對得上查詢詞，並排除下列反樣式。
BAD = ('grave', 'grab ', 'tomb', 'cemetery', 'memorial', 'monument', 'plaque',
       'stamp', 'coin', 'banknote', 'logo', 'flag', 'map of', 'street', 'road',
       'traffic', 'signpost', 'award ceremony', 'exhibition', 'book cover',
       'title page', 'bust of', 'statue of confucius')


def score(title, query):
    t = title.lower()
    toks = [w for w in re.split(r'[^A-Za-zÀ-ÿ]+', query.lower()) if len(w) > 2]
    hit = sum(2 for w in toks if w in t)
    if any(b in t for b in BAD):
        hit -= 6
    return hit


def search(query, want=8):
    d = api({'action': 'query', 'format': 'json', 'generator': 'search',
             'gsrsearch': f'filetype:bitmap {query}', 'gsrnamespace': 6,
             'gsrlimit': want, 'prop': 'imageinfo',
             'iiprop': 'url|extmetadata|size', 'iiurlwidth': 1600})
    pages = list((d.get('query') or {}).get('pages', {}).values())
    # generator search 不保證順序，依 index 還原
    pages.sort(key=lambda p: p.get('index', 99))
    out = []
    for p in pages:
        ii = (p.get('imageinfo') or [None])[0]
        if not ii:
            continue
        meta = ii.get('extmetadata', {})
        lic = strip_html(meta.get('LicenseShortName', {}).get('value'))
        if not lic or not OK_LICENSE.search(lic):
            continue
        if ii.get('width', 0) < 700:          # 太小的不要，投影會糊
            continue
        out.append({
            'title': p['title'],
            'url': ii.get('thumburl') or ii['url'],
            'page': ii.get('descriptionurl'),
            'license': lic,
            'author': strip_html(meta.get('Artist', {}).get('value'))[:120],
            '_score': score(p['title'][5:], query),
        })
    out = [h for h in out if h['_score'] > 0]      # 對不上查詢詞就別用
    out.sort(key=lambda h: -h['_score'])
    return out


# 冷門題材（台灣民間信仰、原住民祭儀、少見學者肖像）搜尋評分救不了：
# 「王船」在 Commons 叫 Ong-tsun、「西拉雅祀壺」叫 Huan-á-ùn Kong-kài，
# 英文查詢詞永遠對不上。這幾張直接指名檔案，不走搜尋。
EXACT = {
    'otto-rudolf': 'File:RudolfOtto.jpg',
    'siraya-jar': 'File:Huan-á-ùn Kong-kài，in Tshit-kóo District.jpg',
    'wangchuan-burning': 'File:Ong-tsun Taiwan.jpg',
    'taiwan-indigenous': 'File:Puyuma Ritual House (Formosan Aboriginal Culture Village).JPG',
    'paiwan-ritual': 'File:2016-10-10 PaiwanWedding.jpg',
    'confucius-portrait': 'File:Portrait of Confucius by Michinobu Kano.jpg',
}


def exact(title):
    d = api({'action': 'query', 'format': 'json', 'titles': title,
             'prop': 'imageinfo', 'iiprop': 'url|extmetadata|size', 'iiurlwidth': 1600})
    for p in (d.get('query') or {}).get('pages', {}).values():
        ii = (p.get('imageinfo') or [None])[0]
        if not ii:
            return None
        meta = ii.get('extmetadata', {})
        lic = strip_html(meta.get('LicenseShortName', {}).get('value'))
        if not lic or not OK_LICENSE.search(lic):
            return None
        return {'title': p['title'], 'url': ii.get('thumburl') or ii['url'],
                'page': ii.get('descriptionurl'), 'license': lic,
                'author': strip_html(meta.get('Artist', {}).get('value'))[:120]}
    return None


def fetch(key, query, manifest, recheck=False):
    if key in manifest and not recheck:
        f = OUT / manifest[key]['file']
        if f.exists():
            return 'skip'
    if key in EXACT:
        h = exact(EXACT[key])
        if not h:
            return 'none'
    else:
        hits = search(query)
        if not hits:
            return 'none'
        h = {k: v for k, v in hits[0].items() if not k.startswith('_')}
    ext = Path(urllib.parse.urlparse(h['url']).path).suffix.lower() or '.jpg'
    if ext not in ('.jpg', '.jpeg', '.png'):
        ext = '.jpg'
    fname = f'{key}{ext}'
    (OUT / fname).write_bytes(get(h['url']))
    h['file'] = fname
    h['query'] = query
    manifest[key] = h
    return 'ok'


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    recheck = '--recheck' in sys.argv
    course = next((a.split('=')[1] for a in sys.argv[1:]
                   if a.startswith('--course=')), 'wr')
    if course != 'wr':
        OUT = TEACH / FOLDERS[course] / '簡報' / '圖片'
        MANIFEST = OUT / '_manifest.json'
        if course == 'sl':
            from course_slide_images_sl import IMAGES_SL as I, EXACT_SL as E
        else:
            from course_slide_images_ch import IMAGES_CH as I, EXACT_CH as E
        IMAGES = I
        EXACT = E
    only = [a for a in sys.argv[1:] if not a.startswith('--')]
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {}
    ok = skip = fail = 0
    for key, query in IMAGES.items():
        if only and key not in only:
            continue
        if only:
            manifest.pop(key, None)              # 指名重抓就先清掉舊的
        try:
            r = fetch(key, query, manifest, recheck)
        except urllib.error.HTTPError as e:         # 單張失敗不要中斷整批
            r = f'HTTP {e.code}'
        except Exception as e:
            r = f'err {type(e).__name__}'
        if r == 'ok':
            ok += 1
            # 逐張存檔：只在結尾寫 manifest 的話，中途被中斷就整批白做
            MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1),
                                encoding='utf-8')
            print(f'✔ {key:26} {manifest[key]["license"]:16} {manifest[key]["title"][5:60]}')
        elif r == 'skip':
            skip += 1
        else:
            fail += 1
            print(f'✘ {key:26} {r}　（查詢：{query}）')
        time.sleep(1.2 if r == 'ok' else 0.3)        # 對 Commons 客氣一點
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n新抓 {ok}／沿用 {skip}／失敗 {fail}　共 {len(manifest)} 張')
