#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""希臘羅馬大藏經 — 取《俄耳甫斯讚歌》87 首的希臘原文與公有領域英譯。

與 hellenika_text.py 分工：那支抓 Perseus 的標準 TEI，本篇**沒有 TEI**——
Perseus 與 First1KGreek 都查無 tlg1815，故另闢取源，但寫出**同一個 schema**
（見 hellenika-texts skill §3），一樣落在 sources/text/，一樣走
hellenika_text_align.py 翻譯。

## 取源（user 2026-08-30 定案，路線 C）

    希臘文  el.wikisource.org —— 該站的《Ὀρφικοὶ ὕμνοι》是逐頁校對後
            transclude 自 **Abel 1885《Orphica》** 的掃描本（頁面自陳
            「Προέλευση κειμένων: Eugen Abel επιμ. (1885)」）。等於拿到公有
            領域底本的現成校對成果，不必自己跑 Vision OCR。
    英譯    theoi.com —— Thomas Taylor 1792 全譯，公有領域。

被否決的兩條：hellenicgods.org 的希臘文底本是 Quandt 1941（版權灰色）；
archive.org 的 Abel 掃描本要逐首 Vision OCR，而 Wikisource 拿的正是同一個底本。

## 🚨 兩邊的編號差一號，照號碼對接必錯

Taylor 把〈致赫卡忒〉併進序詩〈致穆賽俄斯〉裡不另立篇，所以

    Taylor I（Prothyraia）＝ Quandt／Abel 第 2 首

一路差到底。若拿 theoi 的 N 去配 Wikisource 的 N，87 首會整批錯開一格，而且
頁面照樣渲染——正是「印得出來但配錯」那一類錯（見 feedback_reader_silent_failures）。
本腳本因此不靠編號對接，改靠下面 HYMNS 那張**人工核對過的表**：每一列自帶
`en_check`，抓下來的英譯標題對不上就報錯中止，不寫檔。

## 切段：一首一段

讚歌多半 6–30 行，Taylor 又把希臘文的兩行壓成英譯的一行，兩邊的行號**根本
對不起來**。故不切段：一首即一段，邊界取在篇界，這是唯一保證對得上的切法。
序詩 54 行同樣不切——與其在 Taylor 的連綿神名表裡猜邊界，不如整段送。

用法：
    python scripts/hellenika_orphic.py --list
    python scripts/hellenika_orphic.py --fetch 1-3 --out c:/tmp/hellenika/text
    python scripts/hellenika_orphic.py --fetch all
"""
from __future__ import annotations

import argparse
import html as htmlmod
import io
import json
import os
import re
import sys
import time
import urllib.parse

import lxml.html
import requests

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, 'data', 'hellenika', 'sources', 'text')

WS_API = 'https://el.wikisource.org/w/api.php'
WS_PAGE = 'Ορφικοί ύμνοι/%s'
WS_URL = 'https://el.wikisource.org/wiki/%s'
THEOI = 'https://www.theoi.com/Text/OrphicHymns%d.html'
UA = 'know-graph-lab/1.0 (academic research; contact via github)'
DELAY = 3.0

LICENCE = ('希臘原文取自希臘文 Wikisource 的《Ὀρφικοὶ ὕμνοι》，該站逐頁校對後'
           'transclude 自 Eugen Abel 編《Orphica》（Leipzig, 1885）之掃描本，'
           '底本已入公有領域；英譯為 Thomas Taylor, *The Mystical Initiations, or '
           'Hymns of Orpheus*（London, 1792），亦已入公有領域，取自 theoi.com 之'
           '排印本（該站於神名後方括號內補入希臘原名，一併保留）。')

PIVOT_NOTE_LINES = (
    'Taylor 1792 把希臘文的兩行壓成英譯的一行，兩邊行號對不起來，故一首即一段，'
    '不逐行對照；段內的希臘文行號另以行首數字標出。')

# ─────────────────────────────────────────────────────────────────────────
# 88 篇的對照表 —— 序詩 ＋ 87 首。
#
#   n        Quandt／Abel 編號（0 ＝ 序詩）
#   ws       希臘文 Wikisource 的子頁名
#   theoi    theoi.com 的錨點編號（Taylor 編號）；序詩與第 1 首共用 0，見 split
#   en_check 該篇英譯標題必含的字串，**對接的保險絲**，對不上即中止
#   zh       篇名中譯
#
# 🚨 theoi 那一欄一律是 n-1（第 2 首起），這不是筆誤，見上方說明。
HYMNS: list[tuple[int, str, int, str, str]] = [
    (0,  'Ευχή προς Μουσαίον',            0,  'MUS',            '序詩（致穆賽俄斯）'),
    (1,  'Εις Εκάτην',                    0,  'MUS',            '致赫卡忒'),
    (2,  'Προθυραίας',                    1,  'PROTHYR',        '致普羅提萊亞'),
    (3,  'Νυκτός',                        2,  'NIGHT',          '致倪克斯（夜）'),
    (4,  'Ουρανού',                       3,  'HEAVEN',         '致烏拉諾斯（天）'),
    (5,  'Αιθέρος',                       4,  'AITHER',         '致埃忒耳（清氣）'),
    (6,  'Πρωτογόνου',                    5,  'PROTOGONUS',     '致普洛托格諾斯（初生者）'),
    (7,  'Άστρων',                        6,  'STARS',          '致眾星'),
    (8,  'Ηλίου',                         7,  'SUN',            '致赫利俄斯（日）'),
    (9,  'Σελήνης',                       8,  'MOON',           '致塞勒涅（月）'),
    (10, 'Φύσεως',                        9,  'NATURE',         '致費西斯（自然）'),
    (11, 'Πανός',                         10, 'PAN',            '致潘'),
    (12, 'Ηρακλέους',                     11, 'HERCULES',       '致赫拉克勒斯'),
    (13, 'Κρόνου',                        12, 'SATURN',         '致克洛諾斯'),
    (14, 'Ρέας',                          13, 'RHEA',           '致瑞亞'),
    (15, 'Διός',                          14, 'JUPITER',        '致宙斯'),
    (16, 'Ήρας',                          15, 'JUNO',           '致赫拉'),
    (17, 'Ποσειδώνος',                    16, 'NEPTUNE',        '致波塞頓'),
    (18, 'Εις Πλούτωνα',                  17, 'PLUTO',          '致普魯托'),
    (19, 'Κεραύνιου Διός',                18, 'THUNDRING',      '致雷霆宙斯'),
    (20, 'Διός Αστραπίου',                19, 'LIGHTNING',      '致閃電宙斯'),
    (21, 'Νεφών',                         20, 'CLOUDS',         '致雲'),
    (22, 'Θαλάσσης',                      21, 'SEA',            '致塔拉薩（海）'),
    (23, 'Νηρέως',                        22, 'NEREUS',         '致涅柔斯'),
    (24, 'Νηρηίδων',                      23, 'NEREIDS',        '致涅柔斯眾女'),
    (25, 'Πρωτέως',                       24, 'PROTEUS',        '致普羅透斯'),
    (26, 'Γης',                           25, 'EARTH',          '致蓋婭（地）'),
    (27, 'Μητρός θεών',                   26, 'MOTHER OF THE GODS', '致眾神之母'),
    (28, 'Ερμού',                         27, 'MERCURY',        '致赫爾墨斯'),
    (29, 'Ύμνος Φερσεφόνης',              28, 'PROSERPINE',     '致珀耳塞福涅'),
    (30, 'Διονύσου',                      29, 'BACCHUS',        '致戴奧尼索斯'),
    (31, 'Ύμνος Κουρήτων',                30, 'CURETES',        '致庫瑞忒斯'),
    (32, 'Αθηνάς',                        31, 'PALLAS',         '致雅典娜'),
    (33, 'Νίκης',                         32, 'VICTORY',        '致尼刻（勝利）'),
    (34, 'Απόλλωνος',                     33, 'APOLLO',         '致阿波羅'),
    (35, 'Λητούς',                        34, 'LATONA',         '致勒托'),
    (36, 'Αρτέμιδος',                     35, 'DIANA',          '致阿爾忒彌斯'),
    (37, 'Τιτάνων',                       36, 'TITANS',         '致泰坦諸神'),
    (38, 'Κουρήτων',                      37, 'CURETES',        '致庫瑞忒斯（重出）'),
    (39, 'Κορύβαντος',                    38, 'CORYBAS',        '致科律巴斯'),
    (40, 'Δήμητρος Ελευσινίας',           39, 'CERES',          '致厄琉息斯的得墨忒耳'),
    (41, 'Μητρός Ανταίας',                40, 'MOTHER',         '致安泰亞母神'),
    (42, 'Μίσης',                         41, 'MISES',          '致彌塞'),
    (43, 'Ωρών',                          42, 'SEASONS',        '致荷萊（時序女神）'),
    (44, 'Σεμέλης',                       43, 'SEMELE',         '致塞墨勒'),
    (45, 'Διονύσου Βασσαρέως Τριετηρικού', 44, 'BASSAREUS',     '致三年祭的巴薩留斯‧戴奧尼索斯'),
    (46, 'Λικνίτου',                      45, 'LIKNITUS',       '致利克尼忒斯（簸箕中的酒神）'),
    (47, 'Περικιονίου',                   46, 'PERICIONIUS',    '致佩里基俄尼俄斯（繞柱者）'),
    (48, 'Σαβαζίου',                      47, 'SABASIUS',       '致薩巴齊俄斯'),
    (49, 'Ίππας',                         48, 'IPPA',           '致希帕'),
    (50, 'Λυσίου Ληναίου',                49, 'LYSIUS',         '致呂西俄斯‧勒奈俄斯'),
    (51, 'Νυμφών',                        50, 'NYMPHS',         '致寧芙'),
    (52, 'Τριετηρικού',                   51, 'TRIETERICUS',    '致特里厄忒里科斯（三年祭之神）'),
    (53, 'Αμφιετούς',                     52, 'AMPHIETUS',      '致安菲厄忒斯（周年祭之神）'),
    (54, 'Σιληνού Σατύρου Βακχών',        53, 'SILENUS',        '致西勒諾斯、薩堤爾與酒神女信眾'),
    (55, 'Εις Αφροδίτην',                 54, 'VENUS',          '致阿芙羅狄忒'),
    (56, 'Αδώνιδος',                      55, 'ADONIS',         '致阿多尼斯'),
    (57, 'Ερμού Χθονίου',                 56, 'TERRESTRIAL HERMES', '致冥府的赫爾墨斯'),
    (58, 'Έρωτος',                        57, 'CUPID',          '致厄洛斯'),
    (59, 'Μοιρών',                        58, 'FATES',          '致命運三女神'),
    (60, 'Χαρίτων',                       59, 'GRACES',         '致美惠三女神'),
    (61, 'Νεμέσεως',                      60, 'NEMESIS',        '致涅墨西斯'),
    (62, 'Δίκης',                         61, 'JUSTICE',        '致狄刻（正義）'),
    (63, 'Δικαιοσύνης',                   62, 'EQUITY',         '致狄開俄緒涅（公道）'),
    (64, 'Ύμνος Νόμου',                   63, 'LAW',            '致諾摩斯（律法）'),
    (65, 'Άρεος',                         64, 'MARS',           '致阿瑞斯'),
    (66, 'Ηφαίστου',                      65, 'VULCAN',         '致赫菲斯托斯'),
    (67, 'Ασκληπιού',                     66, 'ESCULAPIUS',     '致阿斯克勒庇俄斯'),
    (68, 'Υγείας',                        67, 'HEALTH',         '致許革亞（健康）'),
    (69, 'Εριννύων',                      68, 'FURIES',         '致厄里倪厄斯（復仇女神）'),
    (70, 'Ευμενίδων',                     69, 'EUMENIDES',      '致慈心女神'),
    (71, 'Μειλινόης',                     70, 'MELINOE',        '致梅利諾厄'),
    (72, 'Τύχης',                         71, 'FORTUNE',        '致提喀（機運）'),
    (73, 'Δαίμονος',                      72, 'DÆMON',          '致代蒙（守護靈）'),
    (74, 'Λευκοθέας',                     73, 'LEUCOTHEA',      '致琉科忒亞'),
    (75, 'Παλαίμονος',                    74, 'PAL',            '致帕萊蒙'),
    (76, 'Μουσών',                        75, 'MUSES',          '致繆斯'),
    (77, 'Μνημοσύνης',                    76, 'MNEMOSYNE',      '致謨涅摩緒涅（記憶）'),
    (78, 'Ηούς',                          77, 'AURORA',         '致厄俄斯（曙光）'),
    (79, 'Θέμιδος',                       78, 'THEMIS',         '致忒彌斯'),
    (80, 'Βορέου',                        79, 'NORTH WIND',     '致玻瑞阿斯（北風）'),
    (81, 'Ζεφύρου',                       80, 'WEST WIND',      '致澤費羅斯（西風）'),
    (82, 'Νότου',                         81, 'SOUTH WIND',     '致諾托斯（南風）'),
    (83, 'Ωκεανού',                       82, 'OCEAN',          '致俄刻阿諾斯'),
    (84, 'Εστίας',                        83, 'VESTA',          '致赫斯提亞'),
    (85, 'Ύπνου',                         84, 'SLEEP',          '致修普諾斯（睡眠）'),
    (86, 'Ονείρου',                       85, 'DREAMS',         '致俄涅伊洛斯（夢）'),
    (87, 'Θανάτου',                       86, 'DEATH',          '致塔納托斯（死）'),
]

# theoi 的第 0 塊裡，序詩與第 1 首之間沒有標題可切；Taylor 的赫卡忒頌自這一句起。
HEKATE_CUE = 'I call Einodian Hecate'

# 本篇專名定譯表。詞庫（/translation-glossary）的 deities 表只收了宙斯、赫拉、
# 波塞頓、雅典娜、阿波羅、阿瑞斯六條合用者，其餘皆查無；依既定規矩**不自行寫進
# 詞庫**，改依中文古典學界慣例定名、列入 data/hellenika/glossary-candidates-orphic.md
# 標【提】待校（見 feedback_glossary_ancient_name_priority）。
# 詞庫收有而本藏經另有定名者（赫爾墨斯／阿爾忒彌斯／得墨忒耳／阿芙羅狄忒）走
# hellenika_glossary.py 的 CORPUS_OVERRIDES，不在此重述。
NAMES = {
    'Musaeus': '穆賽俄斯', 'Orpheus': '俄耳甫斯',
    'Hecate': '赫卡忒', 'Einodian': '道途的（赫卡忒稱號）',
    'Prothyraea': '普羅提萊亞', 'Nyx': '倪克斯', 'Ouranos': '烏拉諾斯',
    'Aither': '埃忒耳', 'Protogonus': '普洛托格諾斯', 'Phanes': '法涅斯',
    'Ericapaeus': '厄里卡派俄斯', 'Priapus': '普里阿波斯',
    'Helios': '赫利俄斯', 'Selene': '塞勒涅', 'Physis': '費西斯',
    'Pan': '潘', 'Herakles': '赫拉克勒斯', 'Kronos': '克洛諾斯', 'Rhea': '瑞亞',
    'Plouton': '普魯托', 'Nephelai': '雲', 'Thalassa': '塔拉薩', 'Tethys': '忒堤斯',
    'Nereus': '涅柔斯', 'Nereids': '涅柔斯眾女', 'Proteus': '普羅透斯',
    'Meter Theon': '眾神之母', 'Kybele': '庫柏勒', 'Persephone': '珀耳塞福涅',
    'Kouretes': '庫瑞忒斯', 'Nike': '尼刻', 'Leto': '勒托', 'Titans': '泰坦諸神',
    'Korybas': '科律巴斯', 'Antaia': '安泰亞', 'Mise': '彌塞', 'Horai': '荷萊',
    'Semele': '塞墨勒', 'Bassareus': '巴薩留斯', 'Liknitos': '利克尼忒斯',
    'Perikionios': '佩里基俄尼俄斯', 'Sabazios': '薩巴齊俄斯', 'Hipta': '希帕',
    'Lysios': '呂西俄斯', 'Lenaios': '勒奈俄斯', 'Nymphs': '寧芙',
    'Trieterikos': '特里厄忒里科斯', 'Amphietos': '安菲厄忒斯',
    'Silenus': '西勒諾斯', 'Satyr': '薩堤爾', 'Bacchae': '酒神女信眾',
    'Adonis': '阿多尼斯', 'Eros': '厄洛斯', 'Moirai': '命運三女神',
    'Klotho': '克洛托', 'Lachesis': '拉刻西斯', 'Atropos': '阿特洛波斯',
    'Charites': '美惠三女神', 'Aglaia': '阿格萊亞', 'Thalia': '塔利亞',
    'Euphrosyne': '歐佛洛緒涅', 'Nemesis': '涅墨西斯', 'Dike': '狄刻',
    'Dikaiosyne': '狄開俄緒涅', 'Nomos': '諾摩斯', 'Hephaistos': '赫菲斯托斯',
    'Asklepios': '阿斯克勒庇俄斯', 'Hygeia': '許革亞', 'Erinyes': '厄里倪厄斯',
    'Tisiphone': '提西福涅', 'Allecto': '阿勒克托', 'Megaera': '墨該拉',
    'Eumenides': '慈心女神', 'Melinoe': '梅利諾厄', 'Tyche': '提喀',
    'Daimon': '代蒙', 'Leucothea': '琉科忒亞', 'Palaimon': '帕萊蒙',
    'Muses': '繆斯', 'Mnemosyne': '謨涅摩緒涅', 'Eos': '厄俄斯',
    'Themis': '忒彌斯', 'Boreas': '玻瑞阿斯', 'Zephyros': '澤費羅斯',
    'Notos': '諾托斯', 'Okeanos': '俄刻阿諾斯', 'Hestia': '赫斯提亞',
    'Hypnos': '修普諾斯', 'Oneiros': '俄涅伊洛斯', 'Thanatos': '塔納托斯',
    'Ino': '伊諾', 'Attis': '阿提斯', 'Adrastia': '阿德剌斯忒亞',
    'Eubouleus': '歐布勒俄斯', 'Iacchus': '伊阿科斯', 'Baubo': '包玻',
    'Eleusis': '厄琉息斯', 'Ida': '伊達山', 'Olympus': '奧林匹斯',
    'Fumigation': '焚香', 'Storax': '蘇合香', 'Myrrh': '沒藥',
    'Frankincense': '乳香', 'Manna': '乳香末', 'Saffron': '番紅花',
    'Aromatics': '香料', 'Poppies': '罌粟', 'Torches': '火炬',
}

# ────────────────────────────── 取源 ──────────────────────────────


def _get(url: str, **kw) -> requests.Response:
    """🚨 Wikisource 的 API 會節流：DELAY=1.5 秒連抓十頁就回 429。逐次退避重試，
    不要靠縮短間隔硬闖，也不要把 429 當成程式壞掉。"""
    wait = 5.0
    for attempt in range(6):
        r = requests.get(url, headers={'User-Agent': UA}, timeout=60, **kw)
        if r.status_code in (429, 502, 503) and attempt < 5:
            nap = float(r.headers.get('Retry-After') or wait)
            print('    …%d，等 %.0f 秒重試' % (r.status_code, nap), flush=True)
            time.sleep(nap)
            wait *= 2
            continue
        r.raise_for_status()
        return r
    raise RuntimeError('重試六次仍失敗：%s' % url)


def _strip(frag: str) -> str:
    """HTML 片段 → 純文字。保留 theoi 補入的方括號希臘名。"""
    t = re.sub(r'<[^>]+>', '', frag)
    return re.sub(r'\s+', ' ', htmlmod.unescape(t)).strip()


def wikisource(page: str) -> tuple[str, list[str]]:
    """回傳 (該篇希臘文標題（含焚香指示）, 詩行清單)。

    🚨 一首讚歌若橫跨 Abel 掃描本的兩頁，該頁就有**兩個以上** <div class="poem">。
    早先用 `<div class="poem">(.*?)</div>` 只吃到第一個，序詩靜默掉了三分之二
    （54 行只剩 22）——頁面照樣渲染，只是後半不見了。故改用 lxml 逐個收齊，
    並以 Wikisource 自己的行號標記（<span id="vN">，每 5 行一個）回頭驗行數。
    """
    q = {'action': 'parse', 'page': WS_PAGE % page, 'prop': 'text',
         'formatversion': '2', 'format': 'json'}
    d = _get(WS_API + '?' + urllib.parse.urlencode(q)).json()
    if 'parse' not in d:
        raise RuntimeError('Wikisource 查無此頁：%s' % page)
    h = d['parse']['text']

    m = re.search(r'<span id="ws-chapter">(.*?)</span>', h, flags=re.S)
    title = _strip(m.group(1)) if m else page

    # 頁上原有幾個行號標記。哨兵抽完後要對得上——**檢查本身失效必須報錯**，
    # 不能無聲變成不檢查。（起初哨兵用 \x00，lxml 會把 NUL 直接吃掉，於是
    # 下面整套行號核對一路空轉，看起來每篇都通過。這正是本專案最危險的錯法。）
    want_marks = len(re.findall(r'<span[^>]*id="v\d+"', h))

    tree = lxml.html.fromstring(h)
    divs = tree.find_class('poem')
    if not divs:
        raise RuntimeError('%s：找不到 <div class="poem">' % page)

    # 行號標記（<span id="vN">，每 5 行一個）不是詩的一部分，但**先換成哨兵**
    # 而不是直接丟掉：抽完之後拿它核對「第 N 行標記確實落在第 N 行」，
    # 跨頁沒收齊、重複收、順序錯亂都會當場現形。
    lines: list[str] = []
    for div in divs:
        for sp in div.xpath('.//span[starts-with(@id,"v")]'):
            mark = lxml.html.fromstring('<span>\ue000%s\ue000</span>' % sp.get('id')[1:])
            mark.tail = sp.tail          # 尾隨文字仍是詩的一部分，不可跟著換掉
            sp.getparent().replace(sp, mark)
        for bad in div.xpath('.//span[contains(@class,"pagenum")]'):
            bad.drop_tree()
        frag = lxml.html.tostring(div, encoding='unicode')
        frag = re.sub(r'<br\s*/?>', '\n', frag)
        for ln in re.sub(r'<[^>]+>', '', frag).split('\n'):
            ln = re.sub(r'[ \t]+', ' ', htmlmod.unescape(ln)).strip()
            if ln.strip('\ue0000123456789 '):
                lines.append(ln)
    if not lines:
        raise RuntimeError('%s：詩行為空' % page)

    got_marks = sum(len(re.findall(r'\ue000\d+\ue000', ln)) for ln in lines)
    if got_marks != want_marks:
        raise RuntimeError(
            '%s：頁上有 %d 個行號標記，抽出來卻只剩 %d 個。行號核對已經失效，'
            '在修好之前不要寫檔——否則跨頁截斷會一路無聲通過'
            % (page, want_marks, got_marks))

    top = 0
    for i, ln in enumerate(lines, 1):
        for m in re.finditer(r'\ue000(\d+)\ue000', ln):
            n = int(m.group(1))
            # 容差 ±1：Wikisource 的轉錄者偶爾把標記擺在鄰行（第 81 首 Ζεφύρου
            # 只有 6 行，v5 卻擺在末行）。要擋的是「整個 poem 區塊沒收齊」那種
            # 動輒偏移十幾行的錯，±1 擋得住，卻不會被排版習慣絆倒。
            if abs(n - i) > 1:
                raise RuntimeError(
                    '%s：頁上標為第 %d 行的那一行，抽出來卻排在第 %d 行。'
                    '跨頁的 poem 區塊沒收齊或收重了，先查清楚再寫檔' % (page, n, i))
            top = max(top, n)
    # 標記每 5 行一個，末尾未標的殘行至多 4 行；末行剛好逢五時該標記偶爾漏標，
    # 故容到 +5（第 29 首 Φερσεφόνης 即 20 行而只標到 v15）。
    if top and not top <= len(lines) <= top + 5:
        raise RuntimeError(
            '%s：抓到 %d 行，但行號標記到 v%d，應為 %d–%d 行'
            % (page, len(lines), top, top, top + 5))
    lines = [re.sub(r'\s*\ue000\d+\ue000\s*', '', ln).strip() for ln in lines]
    return title, lines


def theoi_blocks() -> dict[int, tuple[str, str, list[str]]]:
    """theoi 錨點編號 → (英譯標題, 焚香指示, 英譯行)。"""
    out: dict[int, tuple[str, str, list[str]]] = {}
    for n in (1, 2):
        h = _get(THEOI % n).text
        h = re.sub(r'<script.*?</script>', '', h, flags=re.S)
        marks = list(re.finditer(
            r'<a\b[^>]*(?:name|id)="(\d+)"\s*>\s*</a>\s*(?:\[\d+\])?\s*([^<]*)</h3>', h))
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(h)
            chunk = h[m.end():end]
            p = re.search(r'<p>(.*?)</p>', chunk, flags=re.S)
            if not p:
                raise RuntimeError('theoi %d：第 %s 塊找不到正文' % (n, m.group(1)))
            inner = p.group(1)
            fum = ''
            fm = re.match(r'\s*<em>(.*?)</em>\s*(?:<br\s*/?>)?', inner, flags=re.S)
            if fm:
                fum = _strip(fm.group(1))
                inner = inner[fm.end():]
                # Taylor 對八首沒有焚香指示的（如雅典娜、阿芙羅狄忒、諾摩斯）只寫
                # 「A Hymn.」佔位。那不是焚香，收進來只會在中譯欄頂上多一句
                # 「（一首讚歌）」的廢話，故不當焚香。
                if 'Fumigation' not in fum:
                    fum = ''
            rows = [_strip(x) for x in re.split(r'<br\s*/?>', inner)]
            out[int(m.group(1))] = (_strip(m.group(2)), fum,
                                    [x for x in rows if x])
        time.sleep(DELAY)
    return out


def split_proem(rows: list[str]) -> tuple[list[str], list[str]]:
    """theoi 第 0 塊 ＝ 序詩＋第 1 首（赫卡忒），中間沒有標題，按首句切開。"""
    for i, r in enumerate(rows):
        if HEKATE_CUE in r:
            return rows[:i], rows[i:]
    raise RuntimeError('theoi 第 0 塊裡找不到赫卡忒頌的起句「%s」，'
                       '該站排版可能已改，對接不可再照舊' % HEKATE_CUE)


def build(row: tuple[int, str, int, str, str],
          blocks: dict[int, tuple[str, str, list[str]]]) -> dict:
    n, ws_page, t_no, en_check, zh = row
    gtitle, glines = wikisource(ws_page)

    en_title, fum, en_rows = blocks[t_no]
    if en_check.upper() not in en_title.upper():
        raise RuntimeError(
            '第 %d 首對接失敗：theoi 第 %d 塊標題是「%s」，預期含「%s」。'
            '兩站的編號差一號，這道檢查就是防止整批錯位——先查清楚再改表。'
            % (n, t_no, en_title, en_check))
    if t_no == 0:                       # 序詩與赫卡忒共用一塊
        head, tail = split_proem(en_rows)
        en_rows = head if n == 0 else tail
        if n == 1:
            en_title, fum = 'I. TO HEKATE', ''

    greek = '\n'.join('%d\u3000%s' % (i, ln) for i, ln in enumerate(glines, 1))
    en = ('（%s）\n' % fum if fum else '') + '\n'.join(en_rows)
    slug = 'orphic-hymn-%02d' % n
    return {
        'source': 'wikisource',
        'siglum': 'Orph. H. %s' % ('proem' if n == 0 else n),
        'slug': slug,
        'url': WS_URL % urllib.parse.quote((WS_PAGE % ws_page).replace(' ', '_')),
        'title_zh': '俄耳甫斯詩頌 %s' % (zh if n == 0 else '第%d首（%s）' % (n, zh)),
        'title_en': ('Orphic Hymns, Proem: To Musaeus' if n == 0
                     else 'Orphic Hymn %d: %s' % (n, en_title)),
        'author': '託名俄耳甫斯',
        'volume': 'O',
        'licence': LICENCE,
        'pivot': 'taylor-eng',
        'pivot_note': PIVOT_NOTE_LINES,
        'lines_total': len(glines),
        'greek_title': gtitle,
        'names': NAMES,
        'segments': [{'line_from': 1, 'line_to': len(glines),
                      'greek': greek, 'en': en, 'zh': ''}],
    }


def parse_range(spec: str) -> list[int]:
    if spec == 'all':
        return [r[0] for r in HYMNS]
    out: list[int] = []
    for part in spec.split(','):
        if '-' in part:
            a, b = (int(x) for x in part.split('-'))
            out += list(range(a, b + 1))
        else:
            out.append(int(part))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', action='store_true')
    ap.add_argument('--fetch', help="'all'，或 '0-3'、'1,5,7' 這樣的編號")
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--force', action='store_true',
                    help='已抓過的也重抓（仍會沿用既有繁中）')
    a = ap.parse_args()

    if a.list or not a.fetch:
        for n, ws, t, _c, zh in HYMNS:
            print('  %-20s %-32s ← theoi #%d' % ('orphic-hymn-%02d' % n, zh, t))
        print('\n共 %d 篇（序詩 ＋ 87 首）' % len(HYMNS))
        return

    want = set(parse_range(a.fetch))
    todo = [r for r in HYMNS if r[0] in want]
    if not todo:
        sys.exit('編號 %s 不在 0–87 之內' % a.fetch)

    print('取 theoi 英譯…', flush=True)
    blocks = theoi_blocks()
    print('  %d 塊' % len(blocks), flush=True)

    os.makedirs(a.out, exist_ok=True)
    for row in todo:
        p = os.path.join(a.out, 'orphic-hymn-%02d.json' % row[0])
        old = json.load(io.open(p, encoding='utf-8')) if os.path.exists(p) else None
        if old and not a.force:
            print('  －  %-20s 已有，略過（要重抓加 --force）'
                  % os.path.basename(p), flush=True)
            continue
        doc = build(row, blocks)
        # 重抓不可洗掉譯文：希臘文一字未改就把既有繁中接回去
        if old:
            for i, seg in enumerate(doc['segments']):
                o = old['segments'][i] if i < len(old['segments']) else None
                if o and o.get('zh') and o.get('greek') == seg['greek']:
                    seg['zh'] = o['zh']
        io.open(p, 'w', encoding='utf-8', newline='\n').write(
            json.dumps(doc, ensure_ascii=False, indent=2) + '\n')
        print('  OK %-20s %-28s 希 %d 行／英 %d 行'
              % (doc['slug'], doc['title_zh'], doc['lines_total'],
                 len(doc['segments'][0]['en'].split('\n'))), flush=True)
        time.sleep(DELAY)


if __name__ == '__main__':
    main()
