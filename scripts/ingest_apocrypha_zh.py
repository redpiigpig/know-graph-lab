"""
Map 基督教典外文獻 (王曉朝主編) ebook_chunks → apocrypha_sections (cct_zh version).

Strategy:
1. Pull all chunks from the 10 main ebooks (OT 1-6 + NT 1-4).
2. For each chunk, classify by:
   a. Matching chapter_path against a slug-keyword table (handles OCR variants:
      默示錄/敵示錄/歐示錄/毆示錄/敵示／敵自／敵錄/敏示錄, etc.).
   b. If no chapter_path match, fall back to content[:200] keyword scan.
3. Skip pure 目錄 / 版權 / 英中對照 chunks (filtered by chapter_path / content).
4. Group consecutive chunks of the same slug to assign sequential order_index.
5. Bulk insert into apocrypha_sections.

Run:  python -X utf8 scripts/ingest_apocrypha_zh.py [--dry-run]
"""

from __future__ import annotations
import os, sys, json, re, argparse
import requests
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ['SUPABASE_URL']
PROJECT_REF = SUPABASE_URL.split('//')[1].split('.')[0]
ACCESS_TOKEN = os.environ['SUPABASE_ACCESS_TOKEN']
SERVICE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

# ── Source: 10 main 王曉朝 books ───────────────────────────────────────────
EBOOKS = {
    '基督教典外文獻-舊約篇-第1冊': 'b1fbff1b-cbf1-45b6-a9cd-cf0e9f943c57',
    '基督教典外文獻-舊約篇-第2冊': 'd5e5df29-2428-4dca-9f79-5ca21587d073',
    '基督教典外文獻-舊約篇-第3冊': 'af50523d-b206-447d-8060-78d4e366ced4',
    '基督教典外文獻-舊約篇-第4冊': 'a96b524b-464e-419e-8d78-b302d28302d3',
    '基督教典外文獻-舊約篇-第5冊': '05f4b0a5-f5ba-4a33-8187-34f9c9abbff3',
    '基督教典外文獻-舊約篇-第6冊': '6aaa0ffe-e8ad-41d2-943e-49d7fd6125d2',
    '基督教典外文獻-新約篇-第1冊': '425f2664-e967-4fc0-b053-d79bc1ac106d',
    '基督教典外文獻-新約篇-第2冊': '0a1b2977-3d3c-4a47-96cd-0bee1bad17f1',
    '基督教典外文獻-新約篇-第3冊': '12156219-cf9c-4610-a84c-5d5358c22817',
    '基督教典外文獻-新約篇-第4冊': '677c5e16-5b19-4f9b-9499-ee44d5c3eb01',
}

# ── Slug → OCR-tolerant keywords (case-insensitive matching against chapter_path
# and chunk content head). Order matters: longer/more-specific keywords first.
SLUG_KEYWORDS: list[tuple[str, list[str]]] = [
    # OT vol 1 — Enoch trilogy
    ('1-enoch',          ['以諾一書']),
    ('2-enoch',          ['以諾二書']),
    ('3-enoch',          ['以諾三書']),
    # OT vol 2 — Apocalyptic
    ('sibylline-oracles',['西卜神諭', '西卡神諭', '西何申諭', '西卅申諭', '囚西卡', '西卡神論',
                          '西卜神論', '西卜林神', '西卩神', '西卜神', '西何神諭']),
    ('vision-ezra',      ['以斯拉異象']),
    ('questions-ezra',   ['以斯拉題問', '以斯拉題間']),
    ('greek-ezra-apoc',  ['希臘語以斯拉', '希臘語以斯拉', '希瞋語以斯拉', '希隱語以斯拉']),
    ('4-ezra',           ['以斯拉默示錄', '以斯拉敵示錄', '以斯拉歐示錄', '以斯拉毆示錄', '以斯拉敏示錄']),
    ('sedrach-apoc',     ['塞德拉克', '寒德拉克']),
    ('abraham-apoc',     ['亞伯拉罕默示錄', '亞伯拉罕敵示錄', '亞伯拉罕歐示錄', '亞伯拉罕毆示錄',
                          '亞伯拉罕鼠示錄', '亞伯拉罕敏示錄']),
    ('adam-apoc',        ['亞當默示錄', '亞當敵示錄', '亞當顧示錄', '亞當歐示錄', '亞當毆示錄', '亞當鼠示錄']),
    ('elijah-apoc',      ['以利亞默示錄', '以利亞敵示錄', '以利亞歐示錄', '以利E敵示錄', '以幹1m敵',
                          '以平1m敵', '以利亞毆', '以平1m歐']),
    ('daniel-apoc',      ['但以理默示錄', '但以理敵示錄', '但以理歐示錄', '但以理毆示錄']),
    ('zephaniah-apoc',   ['西番雅默示錄', '西番雅敵示錄', '西番雅歐示錄', '西番雅毆示錄']),
    ('shem-treatise',    ['閃的論說']),
    ('ezekiel-apoc',     ['以西結偽經', '以西結聽經', '以西結蔽經']),
    # OT vol 3 — Misc legends/letters/testaments
    ('2-baruch',         ['巴錄二書']),
    ('3-baruch',         ['巴錄三書']),
    ('4-baruch',         ['巴錄四書']),
    ('aristeas',         ['阿立斯蒂亞書信', '阿立斯蒂', '間立斯蒂', '問立斯蒂', '何立斯蒂']),
    ('joseph-aseneth',   ['約瑟與亞西納', '約瑟與E西納', '約瑟與E商納']),
    ('life-adam-eve',    ['亞當和夏娃生平']),
    ('pseudo-philo',     ['託斐羅', '託斐纏', '託斐釋', '託斐罐']),
    ('lives-prophets',   ['先知生平']),
    ('rechab-history',   ['利甲人歷史', '利申人歷史']),
    # OT vol 4 — Testaments
    ('test-12-patriarchs',['十二族長遺訓', '十二接長', '十二族長遺自', '十二族長遺言']),
    ('test-job',         ['約伯遺訓', '約伯遺劃']),
    ('test-3-patriarchs',['三族長遺訓', '三族長遣', '三族長遠訓', '三族長遺']),
    ('test-moses',       ['摩西遺訓', '摩茵遺訓']),
    ('test-solomon',     ['所羅門遺訓', '所羅門還訓', '所羅門遺言']),
    ('test-adam',        ['亞當遺訓']),
    ('jubilees',         ['禧年書', '禱年書']),
    ('jacob-ladder',     ['雅各天梯']),
    ('jannes-jambres',   ['雅尼和佯庇', '雅尼和佯鹿', '雅店和佯', '雅店和佯庇']),
    ('joseph-history',   ['約瑟歷史']),
    # OT vol 4 — Wisdom (note 王曉朝 vol 5 卷四 actually contains 智訓)
    ('wisdom-solomon',   ['所羅門智訓', '所羅門智劃', '所羅門智割', '所羅門智司', '所羅門智自',
                          '所羅門智富']),
    # OT vol 5 — Deuterocanon (Catholic / Orthodox)
    ('tobit',            ['多比傳']),
    ('judith',           ['猶滴傳']),
    ('esther-additions', ['以斯帖補篇', '以斯帖稽篇']),
    ('sirach',           ['便西拉智訓', '便西拉智劃', '便西拉智割', '便西拉智自', '便西拉智司',
                          '便西拉智富', '便西拉智白', '便西拉智訪', '便西拉管自', '便西拉智副',
                          '便商拉', '便古拉', '便茜拉', '便茵拉', '便哥拉', '使西拉智']),
    ('letter-jeremiah',  ['耶利米書信']),
    ('prayer-manasseh',  ['瑪拿西禱詞']),
    ('1-esdras',         ['以斯拉上']),
    # OT vol 6 — Wisdom + Maccabees + Qumran
    ('1qs',              ['崑蘭社群規章', '昆蘭社群規章']),
    ('1-maccabees',      ['馬加比一書', '罵加比一書', '馬加上t一書', '馬加上t一書', '罵加上t一書']),
    ('2-maccabees',      ['馬加比二書', '罵加比二書', '白馬加比二書', '馬加上t二書', '馬加上七二書']),
    ('3-maccabees',      ['馬加比三書', '罵加比三書', '馬加上t三書']),
    ('4-maccabees',      ['馬加比四書', '罵加比四書', '馬加上t四書', '馬加上七四書']),
    ('ahiqar',           ['亞希誇', '直希誇']),
    ('philo-poet',       ['史詩詩人斐羅']),
    ('demetrius-chron',  ['年代學家底米丟', '底米丟']),
    ('eupolemus',        ['尤波利蒙']),
    ('theodotus',        ['塞奧多圖']),
    ('phocylides',       ['託福西萊德']),
    ('orphica',          ['奧菲卡']),
    ('menander-syr',     ['敘利亞語門安德', '敘利E語門安德', '敘利E語門安德', '教利亞語門安德']),
    ('hecataeus',        ['託赫卡泰烏', '託赫卡泰鳥']),
    ('artapanus',        ['阿塔帕納']),
    ('psalms-solomon',   ['所羅門詩篇']),
    ('odes-solomon',     ['所羅門頌詩', '所羅門頌藹', '所羅門頒詩', '所羅鬥頌詩']),
    ('joseph-prayer',    ['約瑟禱文', '約瑟疇文']),
    # NT vol 1 — Gospels & papyri
    ('protoevangelium-james', ['雅各原始福音', '雅各原蛤福音']),
    ('q-secret-mark',    ['馬可的神秘福音']),
    ('p-oxy-840',        ['俄西林古蒲草紙840', '俄西林古蒲草紙 840']),
    ('logia-unknown',    ['獨立存留的耶穌語錄', '獨立存留的耶鯨語錄']),
    ('infancy-thomas',   ['多馬的耶穌嬰孩', '多罵的耶穌嬰孩', '多馬的耶鯨嬰孩', '多罵的耶鯨嬰孩']),
    ('gthom',            ['多馬福音', '多篤福音', '多馬屆音', '多馬禧音', '多馬語音', '多馬書']),
    ('gtruth',           ['真理的福音', '真理福音']),
    ('ghebrews',         ['希伯來人福音', '希伯來福音']),
    ('aristobulus',      ['亞里斯多布', '亞理斯多布']),
    ('gnazarenes',       ['拿撒勒派人福音', '拿撤勒派人福音']),
    ('gebionites',       ['伊便尼派人福音']),
    ('gegyptians',       ['埃及人福音']),
    ('gpet',             ['彼得福音']),
    ('infancy-arabic',   ['阿拉伯語耶穌嬰孩', '阿拉伯語耶鯨嬰孩']),
    ('infancy-latin',    ['阿倫德爾抄本404', '拉T語耶穌嬰孩']),
    ('p-strasbourg',     ['斯特拉斯堡蒲草紙']),
    ('gmatthias',        ['託罵太名福音', '託馬太名福音', '馬提亞福音']),
    ('gbart',            ['巴多羅買福音']),
    ('q-peter-preaching',['彼得的宣講']),
    ('p-berlin-11710',   ['柏林蒲草紙11710', '柏林蒲草紙 11710']),
    ('p-berlin-16388',   ['柏林蒲草紙16388', '柏林蒲草紙 16388']),
    ('john-baptist-life',['施洗者約翰生平']),
    ('joseph-carpenter', ['木匠約瑟']),
    ('p-merton-51',      ['默頓蒲草紙51', '默頓蒲草紙 51']),
    ('birth-mary',       ['馬利亞的出生', '馬利巨的出生']),
    ('abgar',            ['亞伯加傳記']),
    ('faiyum',           ['費爾語錄']),
    ('p-egerton-2',      ['伊吉頓蒲草紙2', '伊吉頓蒲草紙 2']),
    ('pistis-sophia',    ['皮斯特斯', '皮斯特斯', '皮斯特斯', '皮斯特斯﹒索菲', '皮斯特斯·索菲']),
    # NT vol 2 — Various
    ('gnicodemus',       ['尼哥德慕福音']),
    ('soph-jesus',       ['耶穌基督智慧書', '耶魯軍基督智慧書', '耶穌基督智慧書']),
    ('epistula-apostolorum',['使徒書信', '使佳書信']),
    ('pilate-claudius',  ['彼拉多給革老丟']),
    ('pilate-tiberius',  ['彼拉多給提庇留']),
    ('pilate-herod',     ['彼拉多與希律']),
    ('two-books-jeu',    ['論約伊的兩本書', '論約翰的兩本書', '論約iI的兩本書']),
    ('john-apocryphon',  ['約翰藏經', '約翰聽經', '約翰蔽經', '約串串藏經', '約翰歐']),
    ('apoc-james-1',     ['雅各默示錄壹', '雅各敵示錄壹', '雅各歐示錄壹', '雅各毆示錄壹', '雅各廠示錄壹']),
    ('apoc-james-2',     ['雅各默示錄貳', '雅各敵示錄貳', '雅各歐示錄貳']),
    ('joseph-arimathea', ['亞利馬太約瑟']),
    ('memoria-apostolorum',['使徒回憶錄']),
    ('peter-philip',     ['彼得給腓力', '彼得給僻力', '彼得給排力', '彼得給辦力', '彼得給麟力']),
    ('seventy-elders',   ['七十長老福音']),
    ('dialogue-savior',  ['與救主的對話']),
    ('vengeance-savior', ['救主的伸冤']),
    ('gphilip',          ['腓力福音', '僻力福音', '瞬力福音', '排力福音', '聯力福音', '脫力措音']),
    ('q-mani',           ['摩尼福音']),
    # NT vol 3 — (most chunks missing; skip)
    # NT vol 4 — Letters & Apocalypses
    ('5-6-ezra',         ['以斯拉五書及以斯拉六書']),
    ('isaiah-ascension', ['以賽亞昇天記', '以賽亞升天記', '以賽E昇天記', '以賽直升天記']),
    ('q-laodicea',       ['老底嘉書']),
    ('clement-romance',  ['革利免', '草利兔', '革幸IJ兔', '輩利兔', '革利兔']),
    ('apoc-paul-cop',    ['科普替語諾斯底的保羅']),
    ('apoc-paul',        ['保羅默示錄', '保羅敵示錄', '保羅歐示錄', '保羅毆示錄']),
    ('christian-sibyl',  ['基督教西卜', '基督教西卡', '基督教西卅', '基督教西何', '基督教西卩']),
    ('seneca-paul',      ['辛尼加與保羅', '幸尼加與保羅', '塞尼加與保羅']),
    ('pseudo-titus',     ['託提多名書']),
    ('apoc-peter-cop',   ['科普替語諾斯底的彼得']),
    ('apoc-peter',       ['彼得默示錄', '彼得敵示錄', '彼得歐示錄', '彼得毆示錄', '彼得宣讀', '彼得宣講集']),
    ('apoc-thomas',      ['多馬默示錄', '多馬gJ', '多馬歇示錄']),
]

# Tokens / chunks we never want to map (skip explicitly).
SKIP_CP_EQ = {'目錄', '附錄'}
SKIP_CP_SUBSTR = ['英中對照', '版權', '出版說明']

# ── Text cleanup regexes ────────────────────────────────────────────────
# The Wang Xiaochao 王曉朝 typesetting bleeds three kinds of noise into the
# PDF text-extract output:
#   1. Section header reprinted on every page break: 第N部分:卷X{文獻名}{副題}
#   2. Right-margin column line-numbers (2-8 alone on lines): "\n2\n3\n4\n5\n"
#   3. Running header on alternating pages: 基督教典外文獻[新舊]約篇第N冊

_RE_PREFIX_SECTION = re.compile(
    r'^[\s　]*第[一二三四五六七八九十囚]+部分[:：][^\n]{1,40}\n+'
)
_RE_RUNNING_HEADER = re.compile(
    r'基督教典外文獻[\s—一]*[新舊]約篇[\s—一]*第[一二三四五六七八九十]+冊'
)
_RE_RUNNING_HEADER_LOOSE = re.compile(
    r'基督教典外文獻[新舊]約[^\n。，]{0,20}冊'
)
_RE_COL_NUMBERS = re.compile(
    r'(?:^|\n)(?:[ \t]*\d{1,3}[ \t　]*\n){3,}'
)
_RE_CONSEC_NUMBER_LINE = re.compile(
    r'(?:^|\n)[ \t]*(?:\d{1,3}[ \t　]*){4,}\n'
)
# Page numbers / line numbers on standalone lines (single digit, often noise)
_RE_LONE_NUMBER_LINE = re.compile(r'\n[ \t]*\d{1,3}[ \t]*\n')
_RE_MULTI_NEWLINE = re.compile(r'\n{3,}')
_RE_LEADING_BLANK = re.compile(r'^[\s　\n]+')

# Verse-marker detection — patterns like "1 45" / "12 1" or "11 5" surrounded by content
_RE_VERSE_MARKER = re.compile(r'(?:^|\n|\s)(\d{1,2})\s+(\d{1,3})(?=\s+[一-鿿])')


# ── Line-level garble detection ─────────────────────────────────────────
_RE_SINGLE_LATIN_LINE = re.compile(r'^[A-Za-z··]{1,2}$')
_RE_SYMBOL_RUN = re.compile(r'^[\*\-—_=\.·•─━]{3,}$')
_RE_OCR_PART_HEADER = re.compile(
    r'^第[一二三四五六七八九十囚IVXivx伊切]+[部冊]?分?[:：]?[~。\.\-]?$'
)
_RE_LEADING_PAGE_NUM = re.compile(r'^[ \t]*\d{1,3}[ \t]*$')
_RE_VERSE_NUM_LINE = re.compile(r'^[ \t]*(\d{1,3})[ \t]*$')

# Common OCR garble patterns that prefix section subtitles. The full set
# encountered in 王曉朝 PDFs: 毛手.Æ / 第伊都~. / 第切都~. / T可看生命 /
# 第切都. / 第切都~ / 第伊都. / 第伊都~ / 第切部. / 毛手. / 毛手~ etc.
_RE_GARBLED_SUBTITLE_OPENING = re.compile(
    r'^[第伊切都囚部冊~。\.\-Æ§¶毛手TJI\s]{1,10}[\.~。Æ§¶]\s*\n',
    re.MULTILINE,
)
_RE_GARBLED_CHARS = re.compile(r'[Æ§¶◊◆●]')


def _is_garbled_subtitle(line: str) -> bool:
    """Heuristic: line is a 1-15 char OCR-garbled subtitle, not real prose."""
    s = line.strip()
    if not s or len(s) > 15:
        return False
    # Contains obvious garble chars
    if _RE_GARBLED_CHARS.search(s):
        return True
    # Tilde + period combo (王曉朝 subtitle marker noise)
    if '~' in s and ('.' in s or '。' in s):
        return True
    # Single Latin cap (T/J/I) prefix + short CJK — e.g. "T可看生命"
    if re.match(r'^[TJIL][一-鿿]{2,6}$', s):
        return True
    return False


def _is_cjk(c: str) -> bool:
    return ('一' <= c <= '鿿') or ('㐀' <= c <= '䶿')


def _is_noise_line(line: str, is_first: bool = False) -> bool:
    """Decide whether a single line (already stripped) is OCR noise.

    is_first: when True, allow slightly more lenient stripping of leading
    page-number / part-header / garbled-subtitle lines.
    """
    s = line.strip()
    if not s:
        return False  # empty handled by collapsing
    if _RE_SINGLE_LATIN_LINE.match(s):
        return True
    if _RE_SYMBOL_RUN.match(s):
        return True
    if _RE_OCR_PART_HEADER.match(s):
        return True
    if is_first and _RE_LEADING_PAGE_NUM.match(s):
        # Drop the standalone page-number line that 王曉朝 PDFs print at the
        # very top of every page (e.g. "145 \n" before the first verse).
        return True
    return False


def _merge_verse_marker_with_text(t: str) -> str:
    """Pattern '2\n歪念能使...' → '2 歪念能使...' so verse N + body sit on
    one line and read naturally. Only fires when the standalone digit is
    followed by a CJK character on the next line."""
    return re.sub(
        r'\n([ \t]*\d{1,3})[ \t]*\n([一-鿿])',
        lambda m: '\n' + m.group(1).strip() + ' ' + m.group(2),
        t,
    )


def clean_text(raw: str) -> str:
    """Strip OCR-typesetting bleed-through from chunk content."""
    t = raw

    # Drop the section-header prefix when present (handles 第N部分:卷X{...}\n)
    t = _RE_PREFIX_SECTION.sub('', t)

    # Drop the running-header references (occur mid-text on page breaks)
    t = _RE_RUNNING_HEADER.sub('', t)
    t = _RE_RUNNING_HEADER_LOOSE.sub('', t)

    # Drop the typesetting column-number runs ("2\n3\n4\n5\n6\n7\n8\n").
    t = _RE_COL_NUMBERS.sub('\n', t)
    t = _RE_CONSEC_NUMBER_LINE.sub('\n', t)

    # Drop garbled subtitle openings ("第伊都~.\n", "毛手.Æ\n", "T可看生命\n")
    t = _RE_GARBLED_SUBTITLE_OPENING.sub('', t)

    # Line-by-line noise filter.
    lines = t.split('\n')
    out_lines: list[str] = []
    seen_real_content = False
    for raw_line in lines:
        # is_first scope = before we've encountered our first real CJK line
        if _is_noise_line(raw_line, is_first=not seen_real_content):
            continue
        # Garbled subtitle: skip whether at top or anywhere
        if _is_garbled_subtitle(raw_line):
            continue
        # Detect if this line has CJK content (≥ 1 chars) → real content
        if any(_is_cjk(c) for c in raw_line):
            seen_real_content = True
        out_lines.append(raw_line)
    t = '\n'.join(out_lines)

    # Merge "verse_num\nchinese..." lines together so display reads as
    # 「1 地上的王...」 instead of split.
    t = _merge_verse_marker_with_text(t)

    # Also merge "ch verse\ntext" form: "1 2 \n他們" → "1 2 他們"
    t = re.sub(
        r'\n([ \t]*\d{1,2}[ \t]+\d{1,3})[ \t]*\n([一-鿿])',
        lambda m: '\n' + m.group(1).strip() + ' ' + m.group(2),
        t,
    )

    # Collapse 3+ newlines to 2; strip leading whitespace.
    t = _RE_MULTI_NEWLINE.sub('\n\n', t)
    t = _RE_LEADING_BLANK.sub('', t)

    return t.strip()


def parse_chapter(text: str) -> int | None:
    """Extract the first chapter number from a cleaned chunk's content.

    Looks for `(chapter)\s+(verse)` two-number markers surrounding Chinese text.
    Returns None if no plausible marker found.
    """
    m = _RE_VERSE_MARKER.search(text)
    if not m:
        return None
    ch = int(m.group(1))
    # Wisdom of Solomon / Sirach / 1 Enoch never exceed ~150 chapters; sanity bound.
    if 1 <= ch <= 250:
        return ch
    return None

# Filter the OCR-noise that pollutes the front-matter pages of every volume.
_TOPMATTER_REGEXES = [
    re.compile(r'天主教在線向您鄭重提醒'),
    re.compile(r'Chinese Christian Literature Council'),
    re.compile(r'^\s*The (?:Old|New) Testament Pseudepigrapha'),
    re.compile(r'^\s*基督教典外文獻[新舊]約篇[\s\S]{0,40}$'),
]


def is_frontmatter(content: str) -> bool:
    for r in _TOPMATTER_REGEXES:
        if r.search(content):
            return True
    return False


def classify_basic(chunk: dict) -> str | None:
    """Single-chunk classification — chapter_path first, then content head."""
    cp = chunk.get('chapter_path') or ''
    content = chunk.get('content') or ''
    content_head = content[:300]   # widen window

    if cp in SKIP_CP_EQ:
        return None
    for sub in SKIP_CP_SUBSTR:
        if sub in cp:
            return None
    if is_frontmatter(content):
        return None

    haystack = cp + ' ' + content_head
    for slug, kws in SLUG_KEYWORDS:
        for kw in kws:
            if kw in haystack:
                return slug

    # Wider content scan (entire chunk) as last resort
    for slug, kws in SLUG_KEYWORDS:
        for kw in kws:
            if kw in content:
                return slug
    return None


def classify_with_inheritance(chunks: list[dict]) -> list[str | None]:
    """
    Two-pass:
      1. classify_basic each chunk.
      2. For unmapped chunks, inherit from the nearest preceding MAPPED chunk
         within the same 'cluster' (continuous unmapped block <= 30 chunks long).
         If the next mapped chunk after the unmapped run is different, we cap
         inheritance halfway between them, so we don't bleed across documents.
    """
    n = len(chunks)
    slugs: list[str | None] = [classify_basic(c) for c in chunks]

    # Mark frontmatter / 目錄 / 英中對照 chunks so they don't inherit
    blocked = [False] * n
    for i, c in enumerate(chunks):
        cp = c.get('chapter_path') or ''
        content = c.get('content') or ''
        if cp in SKIP_CP_EQ or any(s in cp for s in SKIP_CP_SUBSTR) or is_frontmatter(content):
            blocked[i] = True

    # Pass A: fill from previous mapped chunk
    last_slug: str | None = None
    last_pos: int = -1
    for i in range(n):
        if blocked[i]:
            last_slug = None
            last_pos = -1
            continue
        if slugs[i] is not None:
            last_slug = slugs[i]
            last_pos = i
            continue
        # Search forward for next mapped chunk (within 30 ahead)
        next_slug = None
        next_pos = -1
        for j in range(i + 1, min(i + 31, n)):
            if blocked[j]:
                break
            if slugs[j] is not None:
                next_slug = slugs[j]
                next_pos = j
                break

        if last_slug is None and next_slug is None:
            continue   # can't infer

        if last_slug is None:
            # Only forward neighbor — inherit from it
            slugs[i] = next_slug
        elif next_slug is None:
            # Only backward neighbor — inherit from it (if within 30)
            if i - last_pos <= 30:
                slugs[i] = last_slug
        elif last_slug == next_slug:
            # Same on both sides — clearly part of same doc
            slugs[i] = last_slug
        else:
            # Boundary: split at midpoint
            mid = (last_pos + next_pos) // 2
            slugs[i] = last_slug if i <= mid else next_slug

    return slugs


def fetch_chunks(ebook_id: str) -> list[dict]:
    """Pull all chunks via Management API in pages of 500."""
    rows = []
    offset = 0
    while True:
        sql = f"""
SELECT id::text AS id, chunk_index, page_number, chapter_path, content
FROM ebook_chunks
WHERE ebook_id = '{ebook_id}'
ORDER BY chunk_index
LIMIT 1000 OFFSET {offset}
"""
        r = requests.post(
            f'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query',
            headers={'Authorization': f'Bearer {ACCESS_TOKEN}', 'Content-Type': 'application/json'},
            json={'query': sql},
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < 1000:
            break
        offset += 1000
    return rows


def upload_sections(rows: list[dict]) -> int:
    """POST to PostgREST /rest/v1/apocrypha_sections."""
    if not rows:
        return 0
    url = f"{SUPABASE_URL}/rest/v1/apocrypha_sections"
    headers = {
        'apikey': SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
    }
    inserted = 0
    BATCH = 500
    for i in range(0, len(rows), BATCH):
        batch = rows[i:i + BATCH]
        r = requests.post(url, headers=headers, data=json.dumps(batch))
        if r.status_code not in (200, 201, 204):
            print(f'  ERROR batch {i}: {r.status_code} {r.text[:400]}', flush=True)
            r.raise_for_status()
        inserted += len(batch)
    return inserted


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--clear-existing', action='store_true',
                    help='DELETE all cct_zh rows before ingest')
    args = ap.parse_args()

    if args.clear_existing and not args.dry_run:
        print('Clearing existing cct_zh rows...', flush=True)
        r = requests.post(
            f'https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query',
            headers={'Authorization': f'Bearer {ACCESS_TOKEN}', 'Content-Type': 'application/json'},
            json={'query': "DELETE FROM apocrypha_sections WHERE version_code = 'cct_zh'"},
        )
        print(f'  cleared: {r.status_code}', flush=True)

    # Build all rows across all books, then upload in one go
    all_rows: list[dict] = []
    slug_chunk_count: dict[str, int] = {}
    unmapped: dict[str, int] = {}  # book_title → count
    order_counter: dict[str, int] = {}  # per-slug order_index counter

    for title, eid in EBOOKS.items():
        print(f'\n=== {title} ===', flush=True)
        chunks = fetch_chunks(eid)
        print(f'  fetched {len(chunks)} chunks', flush=True)
        slugs = classify_with_inheritance(chunks)
        book_unmapped = 0

        for ch, slug in zip(chunks, slugs):
            content_raw = (ch.get('content') or '').strip()
            if not content_raw or len(content_raw) < 5:
                continue
            if not slug:
                book_unmapped += 1
                continue
            # Clean the OCR noise from text before storing
            content = clean_text(content_raw)
            if len(content) < 8:
                # Cleaned chunk too short — was probably pure noise
                continue
            chapter = parse_chapter(content)

            order_counter.setdefault(slug, 0)
            slug_chunk_count[slug] = slug_chunk_count.get(slug, 0) + 1

            all_rows.append({
                'doc_slug': slug,
                'version_code': 'cct_zh',
                'order_index': order_counter[slug],
                'section_label': ch.get('chapter_path'),
                'source_chunk_id': ch['id'],
                'page_number': ch.get('page_number'),
                'text': content,
                'char_count': len(content),
                'chapter': chapter,
            })
            order_counter[slug] += 1

        unmapped[title] = book_unmapped
        print(f'  unmapped: {book_unmapped}', flush=True)

    print('\n\n──── Summary ────')
    print(f'Total rows to upload: {len(all_rows)}')
    print(f'\nPer-slug counts (top 30):')
    for s, n in sorted(slug_chunk_count.items(), key=lambda x: -x[1])[:30]:
        print(f'  {s:30s} {n:5d}')
    print(f'\nDocuments hit: {len(slug_chunk_count)} / 132')
    print(f'Unmapped per book:')
    for t, n in unmapped.items():
        print(f'  {t}: {n}')

    if args.dry_run:
        print('\n[dry-run] skipping upload.')
        return

    print(f'\nUploading {len(all_rows)} rows…', flush=True)
    n = upload_sections(all_rows)
    print(f'Uploaded {n} rows.', flush=True)


if __name__ == '__main__':
    main()
