# -*- coding: utf-8 -*-
"""城中教會主日崇拜週報解析器 v2。

只讀 public/content/chengzhong-bulletins/<年>/<slug>.json 的 full_text，
從「本週崇拜程序」抽出講員、講題、經課、詩歌、服事人員。

與 v1（scripts/cz_parse.py）的差別：
- 講員以程序裡「證道／信息」那一行為準，找不到才退回表頭的「主禮/證道：」；
  不再讀週報後段的「下週主日事奉／服事人員表」。
- 程序範圍＝表頭之後、「報告事項」之前；下週經課、讀經進度、講章整理等段落不進來。
- 標籤允許字間空白（「福 音 書」「經 課 一」「回 應 詩」）。
- 2003–2007 的「聯91「復活良辰」」「【「…」《普天頌讚》637首】」「獻詩 標題 城中詩班」都認。
- 經課標題後若緊接印出經文本文，而本文節號與標題章節對不上 → warn（不改卷名）。
  同章不同卷（如 2005-02-27 印創世記 17 卻是出埃及記 17）要靠跨週報語料比對，在 main 第二輪做。

用法：python scripts/cz_parse_v2.py            # 全批輸出 output/cz_bulletins_v2.jsonl ＋ 逐年覆蓋率
      python scripts/cz_parse_v2.py 2005-03-13  # 印單份結果
"""
import sys, os, re, json, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "public", "content", "chengzhong-bulletins")
OUT = os.path.join(ROOT, "output", "cz_bulletins_v2.jsonl")

# ---------------------------------------------------------------- 基本工具
_FW = str.maketrans("０１２３４５６７８９：～－，；", "0123456789:~-,;")
CJK = r"一-鿿"


_HANGUL = re.compile("[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]+")


def norm_line(s):
    s = s.replace("\u3000", " ").replace("\xa0", " ").replace("\u2002", " ")
    s = _HANGUL.sub("", s)  # 2007 韓語雙語週報：「經 課 一 성경봉독1： 以賽亞書이사야서 1:1」
    return s.rstrip()


def squash(s):
    return re.sub(r"\s+", "", s)


def spaced(word):
    """把「福音書」變成允許字間空白的 regex：福\\s*音\\s*書"""
    return r"\s*".join(map(re.escape, word))


# ---------------------------------------------------------------- 聖經卷名
BOOKS = ["創世記", "出埃及記", "利未記", "民數記", "申命記", "約書亞記", "士師記", "路得記",
         "撒母耳記上", "撒母耳記下", "列王紀上", "列王紀下", "歷代志上", "歷代志下", "以斯拉記",
         "尼希米記", "以斯帖記", "約伯記", "詩篇", "箴言", "傳道書", "雅歌", "以賽亞書", "耶利米書",
         "耶利米哀歌", "以西結書", "但以理書", "何西阿書", "約珥書", "阿摩司書", "俄巴底亞書",
         "約拿書", "彌迦書", "那鴻書", "哈巴谷書", "西番雅書", "哈該書", "撒迦利亞書", "瑪拉基書",
         "馬太福音", "馬可福音", "路加福音", "約翰福音", "使徒行傳", "羅馬書", "哥林多前書",
         "哥林多後書", "加拉太書", "以弗所書", "腓立比書", "歌羅西書", "帖撒羅尼迦前書",
         "帖撒羅尼迦後書", "提摩太前書", "提摩太後書", "提多書", "腓利門書", "希伯來書", "雅各書",
         "彼得前書", "彼得後書", "約翰一書", "約翰二書", "約翰三書", "猶大書", "啟示錄",
         # 次經（聖週、諸聖日偶見）
         "智慧篇", "所羅門智訓", "便西拉智訓", "德訓篇", "巴錄書", "多俾亞傳", "瑪加伯上", "瑪加伯下"]
BOOK_ALIAS = {
    "創世紀": "創世記", "出埃及": "出埃及記", "約書亞": "約書亞記", "撒母耳上": "撒母耳記上",
    "撒母耳下": "撒母耳記下", "列王記上": "列王紀上", "列王記下": "列王紀下", "列王上": "列王紀上",
    "列王下": "列王紀下", "歷代上": "歷代志上", "歷代下": "歷代志下", "哀歌": "耶利米哀歌",
    "瑪垃基書": "瑪拉基書", "約翰壹書": "約翰一書", "約翰貳書": "約翰二書", "約翰參書": "約翰三書",
    "約翰福音書": "約翰福音", "馬太福音書": "馬太福音", "馬可福音書": "馬可福音", "路加福音書": "路加福音",
    "帖撒羅尼加前書": "帖撒羅尼迦前書", "帖撒羅尼加後書": "帖撒羅尼迦後書", "詩": "詩篇",
    "以賽亞": "以賽亞書", "耶利米": "耶利米書", "以西結": "以西結書", "使徒行轉": "使徒行傳",
    "歌林多前書": "哥林多前書", "歌林多後書": "哥林多後書", "腓利比書": "腓立比書", "尼西米記": "尼希米記", "雅歌書": "雅歌",
}
GOSPELS = {"馬太福音", "馬可福音", "路加福音", "約翰福音"}
_book_names = sorted(set(BOOKS) | set(BOOK_ALIAS), key=len, reverse=True)
_book_names.remove("詩")  # 「詩」單字只在「詩篇」語境用，避免吃到「詩班」
# 單字縮寫只在緊接數字時認（「路1:47-55」「詩95:1-11」）
ABBR1 = {"詩": "詩篇", "路": "路加福音", "太": "馬太福音", "可": "馬可福音", "約": "約翰福音", "徒": "使徒行傳",
         "賽": "以賽亞書", "創": "創世記", "出": "出埃及記", "羅": "羅馬書", "撒上": "撒母耳記上", "撒下": "撒母耳記下",
         "林前": "哥林多前書", "林後": "哥林多後書", "來": "希伯來書", "啟": "啟示錄"}
BOOK_ALIAS.update(ABBR1)
BOOK_RE = ("(" + "|".join(spaced(b) for b in _book_names) + "|"
           + "|".join(r"(?<![" + CJK + r"])" + re.escape(a) + r"(?=\s*\d)" for a in sorted(ABBR1, key=len, reverse=True)) + ")")
# 章節：130篇：1～8 / 8:1-4; 22-31 / 12:12~31上 / 1:1; 2:1-10 / 25:1-10, 13
VERSE_SPEC = r"\s*(\d{1,3}(?:\s*[篇章])?(?:\s*[:：]\s*\d{1,3}[上下abc]?)?(?:\s*(?:[-~～－–—,，、;；]|及|和)\s*[:：]?\s*\d{1,3}(?:\s*[:：]\s*\d{1,3})?[上下abc]?)*)"
REF_RE = re.compile(BOOK_RE + r"\s*[:：]?" + VERSE_SPEC)


def canon_book(b):
    b = squash(b)
    return BOOK_ALIAS.get(b, b)


def norm_ref(book, spec):
    s = spec.translate(_FW)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[篇章]", "", s)
    s = re.sub(r"[~–—]", "-", s)
    s = s.replace("、", ",").replace("，", ",").replace("；", ";").replace("及", ",").replace("和", ",")
    s = re.sub(r"([,;-]):", r"\1", s)  # 「23：1-9、：16～17」
    s = s.replace(";", "; ").replace(",", ", ")
    s = re.sub(r"[-,; ]+$", "", s)
    return f"{canon_book(book)} {s}".strip()


def find_refs(text):
    out = []
    t = text.translate(_FW)
    for m in REF_RE.finditer(t):
        out.append(norm_ref(m.group(1), m.group(2)))
    return out


# ---------------------------------------------------------------- 程序標籤
READING_LABELS = {
    "經課一": "經課一", "經課二": "經課二", "經課三": "經課三", "經課四": "經課四",
    "第一經課": "經課一", "第二經課": "經課二", "第三經課": "經課三",
    "讀經一": "經課一", "讀經二": "經課二", "讀經三": "經課三",
    "舊約經課": "舊約", "新約經課": "新約", "書信經課": "書信", "福音經課": "福音書",
    "啟應文": "啟應文", "啟應經文": "啟應文", "交互讀經": "啟應文", "應啟文": "啟應文",
    "福音書": "福音書", "福音": "福音書", "舊約": "舊約", "新約": "新約", "書信": "書信",
    "使徒書信": "書信", "詩篇": "詩篇", "證道經文": "證道經文", "講道經文": "證道經文",
    "經文": "經文", "經課": "經課",
}
HYMN_LABELS = {
    "安靜頌": "安靜頌", "頌讚": "頌讚", "頌榮": "頌榮", "詩歌": "詩歌", "唱詩": "唱詩",
    "回應詩": "回應詩", "回應詩歌": "回應詩", "詩歌回應": "回應詩", "奉獻詩": "奉獻詩",
    "奉獻": "奉獻", "差遣詩": "差遣詩", "差遣": "差遣", "獻詩": "獻詩", "特別獻詩": "獻詩",
    "獻唱": "獻詩", "獻樂": "獻樂", "詩班獻詩": "獻詩", "退殿曲": "退殿曲", "退堂詩": "退殿曲",
    "福音前禱": "福音前禱", "福音前頌": "福音前禱", "主禱文": "主禱文", "阿們頌": "阿們頌",
    "三一頌": "三一頌", "榮耀頌": "榮耀頌", "開會詩": "開會詩", "入堂詩": "入堂詩",
    "聖餐詩": "聖餐詩", "平安頌": "平安頌", "會前詩歌": "會前詩歌", "始禮詩": "始禮詩",
    "點燭": "點燭", "哈利路亞": "哈利路亞", "讚美": "頌讚", "序詩": "序詩",
    "默禱詩": "默禱詩", "求主憐憫": "求主憐憫", "聖詩": "詩歌", "進殿曲": "進殿詩", "進殿詩": "進殿詩",
    "馬槽捐": "奉獻", "福音書前禱": "福音前禱",
}
SERMON_LABELS = {"證道": "證道", "講道": "證道", "信息": "證道", "宣道": "證道", "證道信息": "證道"}
ROLE_SLOT = {"讀經": "讀經", "祝福": "祝福", "牧禱": "牧禱", "報告": "報告", "詩歌領唱": "領唱",
             "會前領唱": "領唱", "聖餐禮": "聖餐", "聖餐": "聖餐", "差遣禮": "差遣", "默想音樂": "默想音樂",
             "序樂": "司琴", "序曲": "司琴", "殿樂": "司琴", "宣召": "司會", "祈禱": "祈禱",
             "洗禮": "洗禮", "入會禮": "入會禮", "按立禮": "按立禮", "婚禮": "婚禮"}
OTHER_LABELS = ["信仰告白", "始禮文", "祈光禱文", "禮成", "問安", "邀請文", "心中潔淨文", "認罪文",
                "安慰文", "召喚", "靜默", "會前音樂", "入殿禮", "預備禮", "聖道禮", "懺悔禮",
                "報告事項", "詩歌練唱", "讀經進度", "本週讀經進度", "聖詩背景介紹", "會前領唱練唱"]

ALL_LABELS = {}
for d, kind in ((READING_LABELS, "reading"), (HYMN_LABELS, "hymn"), (SERMON_LABELS, "sermon"),
                (ROLE_SLOT, "role")):
    for k in d:
        ALL_LABELS.setdefault(k, kind)
for k in OTHER_LABELS:
    ALL_LABELS.setdefault(k, "other")
ALL_LABELS["讀經"] = "reading_role"      # 讀經 行可能帶經課或只有讀經人
_labels_sorted = sorted(ALL_LABELS, key=len, reverse=True)
# 標籤後必須接：行尾／空白／冒號／點線／括號引號，或（經課類）直接接卷名
_BOUND = r"(?=$|[\s：:\.．…‥·•\-—─【「『（(<＜\[﹝*/／]|" + BOOK_RE + r"|聯\s*\d|新普|普天|世紀頌讚|《)"
LABEL_RE = re.compile(r"^[\s*﹝\[【]*(" + "|".join(spaced(k) for k in _labels_sorted) + r")\s*[﹞\]】]?" + _BOUND)

# 程序開始（表頭結束）的標記
START_LABELS = ["序樂", "序曲", "安靜頌", "宣召", "預備禮", "入殿禮", "會前音樂", "詩歌領唱", "默想音樂",
                "頌讚", "始禮文", "會前詩歌", "點燭", "序詩", "開會詩", "入堂詩"]
START_RE = re.compile(r"^[\s*]*(" + "|".join(spaced(k) for k in START_LABELS) + r")(?![" + CJK + r"])")
END_RE = re.compile(r"^[\s*＊]*(報\s*告\s*事\s*項|活\s*動\s*消\s*息|代\s*禱\s*關\s*懷|代\s*禱\s*事\s*項|"
                    r"下\s*週\s*主\s*日|下\s*主\s*日|本\s*週\s*讀\s*經|聖\s*詩\s*背\s*景|詩\s*歌\s*練\s*唱|"
                    r"各\s*項\s*聚\s*會|奉\s*獻\s*明\s*細|服\s*事\s*人\s*員|牧\s*區\s*消\s*息|"
                    r"為我們所在的土地)")

HONOR = ("牧師|弟兄|姊妹|姐妹|傳道師|傳道|會督|長老|執事|先生|女士|博士|教授|老師|神父|修女|師母|同工|"
         "主教|院長|宣教士|牧者|神學生|實習生|小姐|師丈|法師|主任|總幹事|秘書|會長|教士")
PERSON_RE = re.compile(r"^(?:[" + CJK + r"]{2,5}(?:" + HONOR + r")|[" + CJK + r"]{2,5}\s*(?:" + HONOR + r")"
                       r"|[A-Za-z .]{3,40}(?:牧師|博士|教授)?)(?:\s*[、,，/／及與和]\s*"
                       r"[" + CJK + r"]{2,5}\s*(?:" + HONOR + r")?)*$")
GROUP_RE = re.compile(r"(詩班|團契|敬拜團|詩歌班|合唱團|重唱|樂團|小組|全體|姊妹會|青年團|主日學|兒童|牧區|"
                      r"執事|同工|幼稚園|教師|會眾|家庭|夫婦|手鐘|樂器|獨唱|二重唱|四重唱)$")
NAME_TAIL_RE = re.compile(r"([" + CJK + r"]{2,4}\s*(?:" + HONOR + r"))\s*$")
INSTR_RE = re.compile(r"^(?:(?:眾|會眾|全體|會)\s*[（(]?\s*[立坐]\s*[）)]?.{0,6}|[（(]\s*[立坐]\s*[）)].{0,6}|"
                      r"司\s*會.{0,10}|司\s*琴|主\s*禮.{0,8}|領唱.{0,10}|會眾.{0,8}|全體|眾樂意|眾肅靜|"
                      r"[（(]\s*[主司]\s*[禮會琴]\s*[）)].{0,4}|執事|會\s*[（(][立坐][）)]\s*眾|牧師)$")
SPLIT_RE = re.compile(r"\t+|[\.．…‥·•]{2,}[\.．…‥·•\s]*|\s{2,}|…")


def is_person(s):
    s = s.strip().strip("、,，。.；;:：")
    if not s or len(s) > 40:
        return False
    if GROUP_RE.search(s) and len(s) <= 12:
        return True
    return bool(PERSON_RE.match(s))


def name_stem(s):
    return re.sub(r"(義務)?(" + HONOR + r")", "", squash(s)).strip("：:")


def pieces(rest):
    rest = re.sub(r"(主|司|會)\s+(禮|會|琴|眾)", r"\1\2", rest)
    return [p.strip(" 　:：") for p in SPLIT_RE.split(rest) if p and p.strip(" 　:：.．…")]


def match_label(line):
    m = LABEL_RE.match(line)
    if not m:
        return None, None, line
    key = squash(m.group(1))
    return key, ALL_LABELS[key], line[m.end():]


# ---------------------------------------------------------------- 詩歌
HYMNBOOKS = [
    ("新普天頌讚", "新普頌"), ("新普頌", "新普頌"), ("新普", "新普頌"), ("普天頌讚", "普天頌讚"),
    ("普頌", "普天頌讚"), ("舊普頌", "普天頌讚"), ("聯合衛理公會詩集", "聯合衛理公會詩集"), ("聯合崇拜詩集", "聯合崇拜詩集"),
    ("聯合詩選", "聯合詩選"), ("聯", "聯合詩選"), ("世紀頌讚", "世紀頌讚"), ("聖徒詩歌", "聖徒詩歌"),
    ("頌主新歌", "頌主新歌"), ("青年聖歌", "青年聖歌"), ("讚美之泉", "讚美之泉"), ("生命聖詩", "生命聖詩"),
    ("泰澤", "泰澤"), ("泰", "泰澤"), ("台語聖詩", "台語聖詩"), ("聖詩華語版", "聖詩華語版"), ("聖詩", "聖詩"), ("讚美詩", "讚美詩"),
]
_hb = "|".join(re.escape(a) for a, _ in HYMNBOOKS)
HB_MAP = dict(HYMNBOOKS)
Q_OPEN, Q_CLOSE = "「『“<＜〈", "」』”>＞〉"
TITLE = r"[「『“<＜〈]\s*([^」』”>＞〉\n]{1,40}?)\s*[」』”>＞〉]"
# 【「你的話是我腳前的燈」《普天頌讚》637首】／「三疊阿們」《聯合詩選》第247首
H_BRACKET = re.compile(TITLE + r"\s*《\s*([^》\d]{2,12}?)\s*(?:第\s*)?(\d{1,3}[A-Za-z]?)?\s*首?\s*》\s*(?:第\s*)?(\d{1,3}[A-Za-z]?)?\s*首?")
# 《聯合詩選28 》你的信實廣大 ／《新普天頌讚》第39首「…」
H_BOOKFIRST = re.compile(r"《\s*([^》\d]{2,12}?)\s*(?:第\s*)?(\d{1,3}[A-Za-z]?)?\s*首?\s*》\s*(?:第\s*)?(\d{1,3}[A-Za-z]?)?\s*首?\s*(?:" + TITLE + r"|([^\t…\.\s（(]{1,20}))?")
# 聯91「復活良辰」／新普頌784「主在聖殿中」／新普天頌讚詩103B首「我靈頌主」／新普天頌讚第436首
H_TITLE_FIRST = re.compile(TITLE + r"\s*[＜<〈(（]\s*(" + _hb + r")\s*第?\s*(\d{1,3}[A-Za-z]?)\s*首?\s*[＞>〉)）]")
# 「聯合詩選70」 願神賜君歡喜快樂
H_QBOOK = re.compile(r"[「『]\s*(" + _hb + r")\s*第?\s*(\d{1,3}[A-Za-z]?)\s*首?\s*[」』]\s*([^	…\.\s（(]{1,20})?")
H_ABBR = re.compile(r"(?<![" + CJK + r"])(" + _hb + r")\s*(?:第\s*)?(?:詩)?\s*(?:第\s*)?#?\s*(\d{1,3}[A-Za-z]?)\s*(?:首)?\s*(?:" + TITLE + r"|(?<=[\s首])([^\t…\.「」（(\[\d\s）)】\]＞>〉][^\t…\.「」（(\[）)】\]]{0,19}))?")
# 普世萬民齊來  (#63)
H_HASH = re.compile(r"([^\t…\.（(]{2,24}?)\s*[（(]\s*#\s*(\d{1,3})\s*[）)]")
H_TITLE_ONLY = re.compile(TITLE)
H_NOBOOK = re.compile(r"^\s*[:：]?\s*(\d{1,3})\s*(?:首\s*|\s+)([^\t…\.\d\s][^\t…\.]{0,19})")
HYMN_NOISE = re.compile(r"^(?:[眾會全].*[立坐].*|.*同頌|.*肅靜|.*頌讚|眾樂意|司會.*|領唱.*|請參.*|參.*頁.*|第\d.*節.*)$")


def book_name(raw):
    raw = squash(raw)
    for a, b in HYMNBOOKS:
        if raw == a or raw.startswith(a):
            return b
    return raw


def parse_hymns(slot, rest, nextline=None):
    """回傳 [(book,no,title)]"""
    t = rest.translate(_FW)
    out, used = [], []

    def take(m):
        used.append(m.span())

    def free(m):
        return all(m.end() <= a or m.start() >= b for a, b in used)

    for m in H_TITLE_FIRST.finditer(t):
        out.append((m.start(), HB_MAP.get(m.group(2), m.group(2)), m.group(3), m.group(1).strip())); take(m)
    for m in H_BRACKET.finditer(t):
        out.append((m.start(), book_name(m.group(2)), m.group(3) or m.group(4) or "", m.group(1).strip())); take(m)
    for m in H_BOOKFIRST.finditer(t):
        if not free(m):
            continue
        no = m.group(2) or m.group(3) or ""
        if not no:
            continue
        title = (m.group(4) or m.group(5) or "").strip()
        out.append((m.start(), book_name(m.group(1)), no, title)); take(m)
    for m in H_QBOOK.finditer(t):
        if not free(m):
            continue
        out.append((m.start(), HB_MAP.get(m.group(1), m.group(1)), m.group(2), (m.group(3) or "").strip())); take(m)
    for m in H_ABBR.finditer(t):
        if not free(m):
            continue
        ti = (m.group(3) or "").strip()
        if not ti and m.group(4):
            ti = re.sub(r"\s*(三次|四次|兩次|二次|x\d|×\d).*$", "", m.group(4)).strip()
            if HYMN_NOISE.match(ti) or INSTR_RE.match(ti) or re.search(r"[╱/／]|同頌|肅靜|參", ti):
                ti = ""
        out.append((m.start(), HB_MAP.get(m.group(1), m.group(1)), m.group(2), ti)); take(m)
    for m in H_HASH.finditer(t):
        if not free(m):
            continue
        title = m.group(1).strip(" 　「」")
        out.append((m.start(), "", m.group(2), title)); take(m)
    m = H_NOBOOK.match(t)
    if m and not out:
        out.append((m.start(), "", m.group(1), m.group(2).strip())); take(m)
    for m in H_TITLE_ONLY.finditer(t):
        if not free(m):
            continue
        title = m.group(1).strip()
        if slot in ("主禱文",) or not title:
            continue
        out.append((m.start(), "", "", title)); take(m)
    out.sort()
    res = []
    for _, b, n, ti in out:
        m = re.match(r"^(\d{1,3}[A-Za-z]?)\s+(\S.*)$", ti)
        if m and not n:
            n, ti = m.group(1), m.group(2)
        res.append((b, n, ti))
    if not res and slot in ("獻詩", "詩歌", "唱詩", "回應詩", "奉獻詩", "差遣詩", "獻樂", "退殿曲", "頌讚",
                            "開會詩", "聖餐詩"):
        ps = [p for p in pieces(rest) if p]
        cand = ""
        if ps:
            p0 = re.sub(r"[（(][^）)]*[）)]", "", ps[0]).strip(" —-─。.「」『』<>＜＞")
            if p0 and not is_person(p0) and not HYMN_NOISE.match(p0) and not INSTR_RE.match(p0) \
                    and len(p0) <= 50 and not re.search(r"[，。；]", p0):
                cand = p0
        if not cand and slot in ("獻詩", "獻樂") and nextline:
            nl = nextline.strip()
            m = re.match(r"^[<＜〈「『]\s*([^>＞〉」』]{1,30})[>＞〉」』]", nl)
            if m:
                cand = m.group(1).strip()
            elif 1 < len(nl) <= 16 and not re.search(r"[，。：:；！？,!?]|^\d|^[啟應合]", nl):
                cand = nl
        if cand:
            res.append(("", "", cand))
    return res


# ---------------------------------------------------------------- 表頭服事人員
HEAD_LABEL = re.compile(r"^([" + CJK + r"/／\s]{1,14}?)\s*[：:]\s*(.*)$")
ROLE_NORM = {"主理": "主禮", "講員": "證道", "司奉": "司獻", "愛宴庶務": "愛筵庶務", "愛宴": "愛筵",
             "兒童主日：學": "兒童主日學", "會前領唱": "領唱", "詩歌領唱": "領唱", "主日學": "兒童主日學", "司數": "司數", "奉獻獻詩": "奉獻獻詩"}


def parse_header_roles(lines):
    roles = {}
    cells = []
    for l in lines:
        for _ in range(3):  # 「主   禮：龐君華牧師」「獨    唱：陳麟先生」→ 先把標籤字間空白收掉
            l = re.sub(r"(?<=[" + CJK + r"])\s+(?=[" + CJK + r"]\s*[：:])", "", l)
        cells.extend(c.strip() for c in re.split(r"\t+|\s{3,}", l) if c.strip())
    i = 0
    while i < len(cells):
        c = cells[i]
        # 同一格可能是「主禮/證道：龐君華牧師 司會：…」→ 以「X：」再切
        sub = [s for s in re.split(r"(?<=[^：:\s])\s+(?=[" + CJK + r"/／]{2,8}[：:])", c) if s]
        consumed_next = False
        for s in sub:
            m = HEAD_LABEL.match(s)
            if not m:
                continue
            labs = [squash(x) for x in re.split(r"[/／]", m.group(1)) if squash(x)]
            val = m.group(2).strip()
            if not val and i + 1 < len(cells) and not HEAD_LABEL.match(cells[i + 1]):
                val = cells[i + 1]; consumed_next = True
            val = val.strip("、,，。 /／：:")
            if not labs or not val or len(val) > 40:
                continue
            if not (is_person(val) or re.search(r"(團契|詩班|辦公室|牧區|全體|弟兄姊妹)", val)):
                continue
            for lab in labs:
                lab = ROLE_NORM.get(lab, lab)
                if 1 < len(lab) <= 6:
                    roles.setdefault(lab, val)
        i += 2 if consumed_next else 1
    return roles


# ---------------------------------------------------------------- 程序區塊
def find_blocks(lines):
    """回傳 [(start,end)]：每段崇拜程序的行號範圍。"""
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        if START_RE.match(lines[i]):
            s = i
            j = i + 1
            while j < n and not END_RE.match(lines[j]):
                j += 1
            blocks.append((s, j))
            i = j + 1
            continue
        i += 1
    # 只留含「證道」或經課標籤的區塊
    good = []
    for s, e in blocks:
        kinds = [match_label(lines[k])[1] for k in range(s, e)]
        prog = sum(1 for x in kinds if x in ("sermon", "reading", "reading_role", "hymn"))
        if ("sermon" in kinds or "reading" in kinds) and prog >= 3:
            good.append((s, e))
    return good


# 一行擠了兩個程序項目：「證 道 成長中的道 ……龐君華牧師 回 應 詩 新普頌第171首…」
_MERGE_LABELS = ["回應詩", "信仰告白", "證道", "福音書", "經課一", "經課二", "經課三", "啟應文", "奉獻", "牧禱", "祝福", "三一頌",
                 "阿們頌", "報告", "獻詩", "榮耀頌"]
MERGED_RE = re.compile(r"((?:" + HONOR + r"|同頌|肅靜|眾立|會眾立|眾樂意|詩班|[）)]))\s+(?=(?:"
                       + "|".join(spaced(k) for k in _MERGE_LABELS) + r")\s+\S)")
H_HASH_LINE = re.compile(r"^\s*([^\t：:（(#]{2,30}?)\s*[（(]\s*[#＃]\s*(\d{1,3})\s*[）)]")
GOSPEL_SAID = re.compile(r"(?:福音是|的經過[，,]?)記載在\s*[:：]?\s*" + BOOK_RE + VERSE_SPEC)
SERVICE_HINT = re.compile(r"(早堂|午堂|晚堂|黃昏崇拜|黃昏禮拜|朝陽崇拜|英語崇拜)")
HYMN_CONT_RE = re.compile(r"^\s*(?:聯\s*\d|新普頌\s*\d|新普天頌讚\s*第?\s*\d|普天頌讚\s*第?\s*\d|世紀頌讚\s*第?\s*\d|【\s*「)")
VERSE_LINE = re.compile(r"^\s*(\d{1,3})\s*[:：]\s*(\d{1,3})\s*(\S.*)$")


def parse_block(lines, s, e):
    readings, hymns, roles, warn, probes = [], [], {}, [], []
    preacher, title = None, None
    by_presider = False
    last_label = None
    last_hymn = (None, -9)  # (slot, 行號)：詩歌標籤下一行續寫的「聯237「向主獻呈歌」」歸同一格
    for k in range(s, e):
        line = lines[k]
        key, kind, rest = match_label(line)
        if not key:
            if last_hymn[0] and k - last_hymn[1] <= 2 and HYMN_CONT_RE.match(line):
                for b, no, ti in parse_hymns(last_hymn[0], line):
                    hymns.append({"slot": last_hymn[0], "book": b, "no": no, "title": ti})
                last_hymn = (last_hymn[0], k)
            continue
        last_hymn = (HYMN_LABELS[key], k) if kind == "hymn" else (None, -9)
        if kind == "other":
            last_label = key
            continue
        ps = pieces(rest)
        tail = ps[-1] if ps else ""
        person = tail if tail and is_person(tail) and not INSTR_RE.match(tail) else None
        if kind == "sermon":
            body = [p for p in ps if p is not person]
            if person is None and body:
                m = NAME_TAIL_RE.search(body[-1])
                if m and len(body[-1]) > len(m.group(1)):
                    person = m.group(1)
                    body[-1] = body[-1][:m.start()].strip()
                elif body and is_person(body[-1]):
                    person = body.pop()
            t = " ".join(p for p in body if p and not INSTR_RE.match(p))
            t = t.strip(" 「」『』“”<>＜＞")
            if preacher is None and person:
                preacher = re.sub(r"\s+", "", person)
            elif person is None and ps and re.fullmatch(r"主\s*禮", ps[-1]):
                by_presider = True
            if title is None and t and not find_refs(t):
                title = t
            continue
        if kind in ("reading", "reading_role"):
            inner = rest
            lab = READING_LABELS.get(key, "讀經")
            # 「讀 經  經課一：創世記…」→ 內層再認一次標籤
            k2, kind2, rest2 = match_label(rest.lstrip(" \t：:"))
            if k2 and kind2 == "reading" and not re.match(BOOK_RE, rest.lstrip(" 	：:").translate(_FW)):
                lab, inner = READING_LABELS[k2], rest2
            refs = find_refs(inner)
            if not refs and key != "讀經":
                for j in range(k + 1, min(k + 3, e)):
                    nl = lines[j].strip()
                    if re.match(BOOK_RE, nl.translate(_FW)):
                        refs = find_refs(nl)[:1]
                        break
                    if nl and not nl.startswith(("【", "(", "（", "*", "＊")):
                        break
            if key == "讀經" and person:
                roles.setdefault("讀經", re.sub(r"\s+", " ", person))
            if refs:
                if lab == "經課" and len(refs) > 1:
                    continue  # 「經課：列王記下5:1-14；哥林多前書…」是摘要行，不是程序
                ref = refs[0] if lab not in ("啟應文", "詩篇", "讀經", "經文") else "; ".join(refs)
                readings.append({"label": lab, "ref": ref})
                if person and lab.startswith("經課"):
                    roles.setdefault("讀經", re.sub(r"\s+", " ", person))
                # 印出的經文本文：看接下來 3 行內第一個節號
                for j in range(k + 1, min(k + 4, e)):
                    vm = VERSE_LINE.match(lines[j])
                    if vm:
                        ctx = []  # 首三節本文，供卷名線索比對
                        for jj in range(j, min(j + 6, e)):
                            m3 = VERSE_LINE.match(lines[jj])
                            if m3:
                                ctx.append(m3.group(3))
                            if len(ctx) >= 3:
                                break
                        probes.append({"label": lab, "ref": ref, "ch": int(vm.group(1)),
                                       "v": int(vm.group(2)), "text": vm.group(3)[:80],
                                       "ctx": " ".join(ctx)[:240]})
                        break
                    if lines[j].strip() and not lines[j].strip().startswith(("*", "＊", "司會", "主禮", "會眾")):
                        break
            last_label = key
            continue
        if kind == "hymn":
            if HYMN_LABELS[key] in ("哈利路亞", "福音前禱"):
                g = [x for x in find_refs(rest) if x.split(" ")[0] in GOSPELS]
                if g:
                    readings.append({"label": "福音書", "ref": g[0]})
            nxt = lines[k + 1] if k + 1 < e else None
            for b, no, ti in parse_hymns(HYMN_LABELS[key], rest, nxt):
                hymns.append({"slot": HYMN_LABELS[key], "book": b, "no": no, "title": ti})
            if person:
                slot = HYMN_LABELS[key]
                if slot == "獻詩":
                    roles.setdefault("獻詩", person)
                elif slot in ("奉獻", "奉獻詩"):
                    roles.setdefault("奉獻獻詩", person)
            continue
        if kind == "role" and person:
            roles.setdefault(ROLE_SLOT[key], re.sub(r"\s+", " ", person))
    # 泰澤祈禱：「等待上主  (#63)」獨立成行
    for k in range(s, e):
        if not match_label(lines[k])[0]:
            m = H_HASH_LINE.match(lines[k])
            if m:
                hymns.append({"slot": "詩歌", "book": "", "no": m.group(2), "title": m.group(1).strip()})
    # 福音書標籤漏印卷名時，用「主耶穌基督的福音是記載在 X」補
    if not any(x["label"] == "福音書" for x in readings):
        for k in range(s, e):
            m = GOSPEL_SAID.search(lines[k].translate(_FW))
            if m and canon_book(m.group(1)) in GOSPELS:
                readings.append({"label": "福音書", "ref": norm_ref(m.group(1), m.group(2))})
                break
    if preacher is None and not any(match_label(lines[k])[1] == "sermon" for k in range(s, e)):
        warn.append("程序中沒有證道項目（特殊聚會）")
    # warn：節號章與標題章不合
    for p in probes:
        m = re.search(r"\s(\d{1,3})(?::(\d{1,3}))?", p["ref"])
        if not m:
            continue
        ch = int(m.group(1)); v = int(m.group(2)) if m.group(2) else None
        if p["ch"] != ch:
            warn.append(f"{p['label']}印「{p['ref']}」，但下方經文本文從 {p['ch']}:{p['v']} 開始（章數不符）")
    refs_seen = {x["ref"] for x in readings if x["label"] != "經文"}
    readings = [x for x in readings if not (x["label"] == "經文" and x["ref"] in refs_seen)]
    return {"preacher": preacher, "by_presider": by_presider, "sermon_title": title, "readings": dedupe(readings),
            "hymns": dedupe(hymns), "roles": roles, "warn": warn, "_probes": probes}


def dedupe(xs):
    seen, out = set(), []
    for x in xs:
        k = json.dumps(x, ensure_ascii=False, sort_keys=True)
        if k not in seen:
            seen.add(k); out.append(x)
    return out


def parse(full_text):
    """純函式：週報全文 → {"services":[{service_hint, preacher, sermon_title, readings, hymns, roles, warn}]}"""
    lines = []
    for l in full_text.split("\n"):
        lines.extend(MERGED_RE.sub(r"\1\n", norm_line(l)).split("\n"))
    blocks = find_blocks(lines)
    if not blocks:
        # 無「序樂／宣召」開頭的特殊聚會（泰澤祈禱、輪值通知單）：取到第一個段落結束標記為止
        e = next((i for i, l in enumerate(lines) if i > 3 and END_RE.match(l)), len(lines))
        if any(match_label(l)[1] in ("reading", "sermon") or H_HASH_LINE.match(l) for l in lines[:e]):
            blocks = [(0, e)]
    services = []
    for bi, (s, e) in enumerate(blocks):
        head_from = blocks[bi - 1][1] if bi else 0
        head = lines[max(head_from, s - 60):s] or lines[:min(e, 12)]
        hroles = parse_header_roles(head)
        r = parse_block(lines, s, e)
        hint = None
        for l in reversed(lines[max(head_from, s - 60):s]):
            m = SERVICE_HINT.search(l)
            if m:
                hint = m.group(1); break
        roles = dict(hroles)
        for k, v in r["roles"].items():
            roles.setdefault(k, v)
        preacher = r["preacher"]
        src = "程序"
        if not preacher:
            preacher = hroles.get("證道") or hroles.get("信息")
            src = "表頭"
            if not preacher and r["by_presider"] and hroles.get("主禮"):
                preacher, src = hroles["主禮"], "表頭主禮（程序證道欄印「主禮」）"
        r["warn"] = list(r["warn"])
        if preacher and hroles.get("證道") and name_stem(hroles["證道"]) != name_stem(preacher):
            r["warn"].append(f"表頭證道「{hroles['證道']}」與程序證道「{preacher}」不同，取程序")
        if r["preacher"]:
            roles["證道"] = r["preacher"]
        services.append({"service_hint": hint, "preacher": preacher, "preacher_src": src if preacher else None,
                         "sermon_title": r["sermon_title"], "readings": r["readings"], "hymns": r["hymns"],
                         "roles": roles, "warn": r["warn"], "_probes": r["_probes"], "_span": [s, e]})
    if not services:
        hroles = parse_header_roles(lines[:60])
        services.append({"service_hint": None, "preacher": hroles.get("證道"), "preacher_src": "表頭",
                         "sermon_title": None, "readings": [], "hymns": [], "roles": hroles,
                         "warn": ["找不到崇拜程序"], "_probes": [], "_span": None})
    return {"services": services}


# ---------------------------------------------------------------- 語料比對：同章不同卷
_KEY_STRIP = re.compile(r"[^" + CJK + r"]|上帝|神|上主|祂|他|她|它|牠|裏|裡")


def vkey(text):
    return _KEY_STRIP.sub("", text)


def similar(a, b):
    import difflib
    n = min(len(a), len(b), 40)
    if n < 8:
        return False
    return difflib.SequenceMatcher(None, a[:n], b[:n]).ratio() >= 0.95


# 卷名線索：只當「互相矛盾時的仲裁」與少數絕對規則用
PENTATEUCH_LATER = {"出埃及記", "利未記", "民數記", "申命記", "約書亞記"}
CUE_GEN = re.compile(r"約瑟|亞伯蘭|亞伯拉罕|撒拉|以撒|雅各|挪亞|亞當|夏娃|該隱|羅得|利百加|拉結|以掃")
CUE_EXO = re.compile(r"摩西|法老|亞倫|埃及|西奈|何烈")
NT = set(BOOKS[BOOKS.index("馬太福音"):BOOKS.index("啟示錄") + 1])
OT = set(BOOKS[:BOOKS.index("瑪拉基書") + 1])


def cue_ok(book, ctx):
    """True＝本文線索支持此卷；False＝線索與此卷矛盾；None＝看不出來"""
    if book in OT and re.search(r"耶穌|基督", ctx):
        return False
    if book in GOSPELS and "保羅" in ctx:
        return False
    if book == "創世記":
        if "摩西" in ctx or "西奈" in ctx:
            return False  # 創世記全書沒有摩西
        if CUE_GEN.search(ctx):
            return True
    if book in PENTATEUCH_LATER and CUE_EXO.search(ctx):
        return True
    return None


def cross_book_check(records):
    """同章同節、不同卷的誤植（章節號對得上，前一道檢查抓不到）。
    例：2005-02-27 印「創世記 17:1-7」，本文卻是出埃及記 17（摩西擊磐出水）。
    作法：同一段本文（首節逐字比對 ≥95%）在不同週報被標成不同卷名 → 卷名互相矛盾；
    再用本文線索（創世記人物／摩西、埃及…）判哪一邊錯，判不出就兩邊都 warn。
    沒有對照的單份週報，只套絕對規則（創世記出現摩西、舊約出現耶穌…）。"""
    probes = []
    for ri, r in enumerate(records):
        for p in r["_probes"]:
            probes.append((ri, p["ref"].split(" ")[0], p["ch"], p["v"], vkey(p["text"]), p))
    by_cv = collections.defaultdict(list)
    for x in probes:
        by_cv[(x[2], x[3])].append(x)
    for ri, book, ch, v, key, p in probes:
        ctx = p.get("ctx") or p["text"]
        verdict = cue_ok(book, ctx)
        peers = [y for y in by_cv[(ch, v)] if y[0] != ri and similar(key, y[4])]
        other_books = collections.Counter(y[1] for y in peers if y[1] != book)
        msg = None
        if other_books:
            ob = other_books.most_common(1)[0][0]
            if verdict is False:
                msg = (f"{p['label']}印「{p['ref']}」，但下方本文 {ch}:{v}「{p['text'][:16]}…」與其他週報所印"
                       f"{ob} {ch}:{v} 相同，本文內容也不合{book}，疑卷名印錯（未更動）")
            elif verdict is None and cue_ok(ob, ctx) is True:
                msg = (f"{p['label']}印「{p['ref']}」，但下方本文 {ch}:{v}「{p['text'][:16]}…」與其他週報所印"
                       f"{ob} {ch}:{v} 相同，本文線索也指向{ob}，疑卷名印錯（未更動）")
            elif verdict is None:
                msg = (f"{p['label']}印「{p['ref']}」；同一段本文 {ch}:{v}「{p['text'][:16]}…」在其他週報被標為"
                       f"{ob}，卷名互相矛盾，待人工核對（未更動）")
        elif verdict is False:
            msg = (f"{p['label']}印「{p['ref']}」，但下方本文「{p['text'][:16]}…」的內容不合{book}，"
                   f"疑卷名印錯（未更動）")
        if msg:
            records[ri]["warn"].append(msg)


# ---------------------------------------------------------------- 批次
def load_all():
    for f in sorted(glob.glob(os.path.join(SRC, "*", "*.json"))):
        yield os.path.splitext(os.path.basename(f))[0], json.load(open(f, encoding="utf-8"))


def build_records(slug, d):
    res = parse(d.get("full_text") or "")
    svcs = res["services"]
    out = []
    for i, s in enumerate(svcs):
        service = d.get("service") or "主日崇拜"
        if len(svcs) > 1:
            service = s["service_hint"] or (service if i == 0 else f"{service}#{i + 1}")
        out.append({"date": d.get("date"), "service": service, "slug": slug,
                    "preacher": s["preacher"], "sermon_title": s["sermon_title"],
                    "readings": s["readings"], "hymns": s["hymns"], "roles": s["roles"],
                    "warn": s["warn"], "preacher_src": s["preacher_src"], "_probes": s["_probes"]})
    return out


def has_gospel(r):
    return any(x["label"] == "福音書" or x["ref"].split(" ")[0] in GOSPELS for x in r["readings"])


def is_special(r):
    """程序裡根本沒有證道項目的聚會（泰澤祈禱、復活節朝陽、輪值通知單）"""
    return any("沒有證道項目" in w for w in r["warn"])


def coverage(records):
    """逐年覆蓋率。講員*／含福音* 的分母排除「程序中沒有證道項目」的特殊聚會。"""
    by = collections.defaultdict(list)
    for r in records:
        by[(r["date"] or "????")[:4]].append(r)
    cols = [("講員", "p"), ("講員*", "ps"), ("講題", "t"), ("經課", "r"), ("含福音", "g"), ("含福音*", "gs"),
            ("詩歌", "h"), ("服事", "o")]
    rows = [f"{'年':4} {'份數':>4} {'特殊':>4} " + " ".join(f"{h:>7}" for h, _ in cols) + f" {'warn':>4}"]
    tot = collections.Counter()

    def line(label, c):
        n, ns = c["n"], c["n"] - c["sp"]
        out = []
        for _, k in cols:
            den = ns if k.endswith("s") else n
            out.append(f"{100 * c[k] / den:6.1f}%" if den else "     -")
        return f"{label:4} {n:>4} {c['sp']:>4} " + " ".join(f"{x:>7}" for x in out) + f" {c['w']:>4}"

    for y in sorted(by):
        c = collections.Counter()
        for r in by[y]:
            sp = is_special(r)
            c["n"] += 1; c["sp"] += sp
            c["p"] += bool(r["preacher"]); c["ps"] += bool(r["preacher"]) and not sp
            c["t"] += bool(r["sermon_title"]); c["r"] += bool(r["readings"])
            c["g"] += has_gospel(r); c["gs"] += has_gospel(r) and not sp
            c["h"] += bool(r["hymns"]); c["o"] += bool(r["roles"]); c["w"] += bool(r["warn"])
        tot.update(c)
        rows.append(line(y, c))
    rows.append(line("合計", tot))
    return "\n".join(rows)


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8")
    if argv:
        for slug in argv:
            d = json.load(open(os.path.join(SRC, slug[:4], slug + ".json"), encoding="utf-8"))
            for r in build_records(slug, d):
                r.pop("_probes", None)
                print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    records = []
    for slug, d in load_all():
        records.extend(build_records(slug, d))
    cross_book_check(records)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fo:
        for r in records:
            r = {k: v for k, v in r.items() if not k.startswith("_")}
            fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"寫出 {len(records)} 行 → {OUT}")
    print(coverage(records))


if __name__ == "__main__":
    main(sys.argv[1:])
