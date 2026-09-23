# -*- coding: utf-8 -*-
"""譯文裡的聖經引文一律用《和合本修訂版》（2010）——把經文**查出來交給模型**，不靠它背。

使用者 2026-09-23：「聖經引文除特別的就採用和合本2010」。
光在 prompt 寫「用和合本修訂版」不夠：模型憑記憶寫，會混進和合本（1919）、
思高本或它自己的意譯，而且每段不一樣，讀者看不出來。所以翻譯每一段之前：
  1. 從原文辨認經文出處（明治日文卷名「馬太傳六章一節より四節迄」、
     現代日文片假名「マタイ五・四八」、英文「Matt. 5:48」都認）；
  2. 從經文庫（R2 bible-verses，同 course_quote_bible）取回那幾節的和修經文；
  3. 組成一段提示塞進 prompt，要模型引用處逐字照錄。

「除特別的」＝原文刻意用了別的譯法（作者自譯、在比較譯本差異）時，prompt 讓模型
照原文意思譯，不硬套和修。這個判斷交給模型，因為那要讀上下文。

🚨 和修的**詩體經文在語料裡只存了對句前半**（見 course_quote_bible 頂端說明）：
那種節查出來會被判殘缺，這裡就**不給**經文（寧可讓模型照規則譯，也不要餵半句）。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# (代碼, 各種寫法)。寫法由長到短比對，所以「約翰第一書」要排在「約翰」之前（下面會排序）。
_BOOKS = [
    ("gen", "創世記 創世紀 創世 Gen Genesis"), ("exo", "出埃及記 出エジプト記 出埃及 Exod Ex Exodus"),
    ("lev", "利未記 レビ記 Lev"), ("num", "民數紀略 民數記 民数記 Num"), ("deu", "申命記 Deut Deuteronomy"),
    ("jos", "約書亞記 ヨシュア記 Josh"), ("jdg", "士師記 Judg"), ("rut", "路得記 ルツ記 Ruth"),
    ("1sa", "撒母耳前書 撒母耳記上 サムエル記上 サムエル前書 1Sam"), ("2sa", "撒母耳後書 撒母耳記下 サムエル記下 サムエル後書 2Sam"),
    ("1ki", "列王紀略上 列王紀上 列王記上 1Kings"), ("2ki", "列王紀略下 列王紀下 列王記下 2Kings"),
    ("1ch", "歷代志略上 歷代志上 歴代誌上"), ("2ch", "歷代志略下 歷代志下 歴代誌下"),
    ("ezr", "以斯拉書 以斯拉記 エズラ記"), ("neh", "尼希米記 ネヘミヤ記"), ("est", "以斯帖記 エステル記"),
    ("job", "約百記 約伯記 ヨブ記 Job"), ("psa", "詩篇 詩編 Ps Psa Psalm Psalms"),
    ("pro", "箴言 Prov Proverbs"), ("ecc", "傳道之書 傳道書 伝道の書 伝道者の書 コヘレト Eccl"),
    ("sng", "雅歌 Song"), ("isa", "以賽亞書 以賽亞 イザヤ書 イザヤ Isa Isaiah"),
    ("jer", "耶利米記 耶利米書 エレミヤ書 エレミヤ Jer Jeremiah"), ("lam", "耶利米哀歌 哀歌 Lam"),
    ("ezk", "以西結書 エゼキエル書 エゼキエル Ezek"), ("dan", "但以理書 ダニエル書 Dan"),
    ("hos", "何西阿書 ホセア書 ホセア Hos"), ("jol", "約耳書 ヨエル書"), ("amo", "阿摩司書 アモス書 アモス Amos"),
    ("oba", "阿巴底亞書 俄巴底亞書 オバデヤ書"), ("jon", "約拿書 ヨナ書 Jonah"), ("mic", "米迦書 ミカ書 Mic"),
    ("nam", "那鴻書 ナホム書"), ("hab", "哈巴谷書 ハバクク書 Hab"), ("zep", "西番雅書 ゼパニヤ書"),
    ("hag", "哈基書 哈該書 ハガイ書"), ("zec", "撒加利亞書 撒迦利亞書 ゼカリヤ書 Zech"), ("mal", "馬拉基書 マラキ書 Mal"),
    ("mat", "馬太傳福音書 馬太福音書 馬太福音 馬太傳 馬太 マタイ傳 マタイ福音書 マタイによる福音書 マタイ Matt Mt Matthew"),
    ("mrk", "馬可傳福音書 馬可福音書 馬可福音 馬可傳 マルコ傳 マルコ福音書 マルコによる福音書 マルコ Mark Mk"),
    ("luk", "路加傳福音書 路加福音書 路加福音 路加傳 ルカ傳 ルカ福音書 ルカによる福音書 ルカ Luke Lk"),
    ("jhn", "約翰傳福音書 約翰福音書 約翰福音 約翰傳 ヨハネ傳 ヨハネ福音書 ヨハネによる福音書 John Jn"),
    ("act", "使徒行傳 使徒行録 使徒言行録 使徒行伝 Acts"), ("rom", "羅馬書 ロマ書 ローマ書 ロマ ローマ Rom Romans"),
    ("1co", "哥林多前書 コリント前書 コリント人への第一の手紙 1Cor"), ("2co", "哥林多後書 コリント後書 コリント人への第二の手紙 2Cor"),
    ("gal", "加拉太書 ガラテヤ書 ガラテヤ Gal"), ("eph", "以弗所書 エペソ書 エフェソ書 エペソ Eph"),
    ("php", "腓立比書 ピリピ書 フィリピ書 ピリピ Phil"), ("col", "哥羅西書 歌羅西書 コロサイ書 Col"),
    ("1th", "帖撒羅尼迦前書 テサロニケ前書 1Thess"), ("2th", "帖撒羅尼迦後書 テサロニケ後書 2Thess"),
    ("1ti", "提摩太前書 テモテ前書 1Tim"), ("2ti", "提摩太後書 テモテ後書 2Tim"), ("tit", "提多書 テトス書 Titus"),
    ("phm", "腓利門書 ピレモン書 Philem"), ("heb", "希伯來書 希伯来書 ヘブル書 ヘブライ書 ヘブル Heb"),
    ("jas", "雅各書 ヤコブ書 Jas James"), ("1pe", "彼得前書 ペテロ前書 1Pet"), ("2pe", "彼得後書 ペテロ後書 2Pet"),
    ("1jn", "約翰第一書 約翰一書 ヨハネ第一書 ヨハネの第一の手紙 1John"), ("2jn", "約翰第二書 約翰二書 ヨハネ第二書 2John"),
    ("3jn", "約翰第三書 約翰三書 ヨハネ第三書 3John"), ("jud", "猶大書 ユダ書 Jude"),
    ("rev", "約翰默示錄 默示錄 黙示録 啓示録 啟示錄 ヨハネの黙示録 Rev Revelation"),
]
_NAME = sorted(((n, code) for code, names in _BOOKS for n in names.split()), key=lambda x: -len(x[0]))
_CODE_OF = {n: c for n, c in _NAME}
_CN_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn_num(s: str) -> int | None:
    """「四十八」「卅二」「廿」「一二〇」「48」→ 整數。"""
    s = s.strip().translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    if s.isdigit():
        return int(s)
    s = s.replace("卅", "三十").replace("廿", "二十").replace("卌", "四十")
    if s and all(c in _CN_DIGIT for c in s):               # 一二〇
        return int("".join(str(_CN_DIGIT[c]) for c in s))
    total, cur = 0, 0
    for c in s:
        if c in _CN_DIGIT:
            cur = _CN_DIGIT[c]
        elif c == "百":
            total += (cur or 1) * 100
            cur = 0
        elif c == "十":
            total += (cur or 1) * 10
            cur = 0
        else:
            return None
    return (total + cur) or None


_NUM = r"[0-9０-９〇零一二三四五六七八九十百廿卅]+"
_NAMES_RE = "|".join(re.escape(n) for n, _ in _NAME)
# 日文／中文：書名 第?N 章|篇 第?M 節? ( (より|至|乃至|—|–|〜|~|、|,|・) 第?K 節? )* (迄|まで)?
_JA = re.compile(rf"({_NAMES_RE})\s*第?\s*({_NUM})\s*[章篇]\s*第?\s*({_NUM})\s*節?"
                 rf"((?:\s*(?:より|至|乃至|—|–|〜|~|、|,|・|及び|及)\s*第?\s*{_NUM}\s*節?)*)")
# 現代日文縮寫「マタイ五・四八」「ロマ八・三二」
_JA_DOT = re.compile(rf"({_NAMES_RE})\s*({_NUM})\s*[・:：]\s*({_NUM})((?:\s*[—–〜~\-、,]\s*{_NUM})*)")
# 英文「Matt. 5:48」「Rom. 8:32-35」
_EN = re.compile(rf"\b({_NAMES_RE})\.?\s*(\d+)\s*:\s*(\d+)((?:\s*[-–—,]\s*\d+)*)")


def find_refs(text: str) -> list[tuple[str, int, int, int]]:
    """原文 → [(書卷代碼, 章, 起節, 迄節)]（去重、保留出現順序）。"""
    out = []
    for rx in (_JA, _JA_DOT, _EN):
        for m in rx.finditer(text or ""):
            code = _CODE_OF.get(m.group(1))
            ch, v1 = cn_num(m.group(2)), cn_num(m.group(3))
            if not (code and ch and v1):
                continue
            tail = m.group(4) or ""
            rest = [x for x in (cn_num(t) for t in re.findall(_NUM, tail)) if x]
            if rest and re.search(r"[、,，・及]", tail):
                # 「八章卅二、卅六節」是兩節分開引，不是 32–36；逐節各給一筆
                items = [(code, ch, v, v) for v in [v1] + rest]
            else:
                v2 = max([v1] + rest) if rest else v1
                if v2 - v1 > 12:                # 一次引十幾節多半是讀錯範圍，不給
                    v2 = v1
                items = [(code, ch, v1, v2)]
            for item in items:
                if item not in out:
                    out.append(item)
    return out


# 內村那一代讀的是文語訳（明治元訳舊約／大正改訳新約）。他引的是那份日文的字句，
# 接著往往就拿那幾個字來講；套和修會跟他的解說對不上。所以日文原著的引文改用
# 本站照文語訳逐節直譯的中文（scripts/japanese_bible.py → jbungo_zh），和修只當後備。
# 使用者 2026-09-23：「在經典的那一邊，新增一個當時他們使用的日文聖經……再進行翻譯」。
JBUNGO_ZH_DIR = Path(__file__).resolve().parent.parent / "output" / "source-cache" / "bible-repair" / "jbungo_zh"

HEAD = {
    "jbungo_zh": ("【本段引用的經文——本站依作者當年所讀的《文語譯聖經》逐節直譯的中文，引用處請照錄，"
                  "不要改用和合本或自行改寫；若作者明顯是自己另譯、改動字句或在比較譯本，才照作者的日文譯】"),
    "cuv2010": ("【本段引用的經文——《和合本修訂版》原文，引用處請逐字照錄，不要自行翻譯或改寫；"
                "若作者明顯是刻意用了不同譯法（自譯、比較譯本），才照原文意思譯】"),
}


def _jbungo_zh(code: str, ch: int, v1: int, v2: int) -> list[tuple[int, str]]:
    f = JBUNGO_ZH_DIR / code / f"{ch}.json"
    if not f.exists():
        raise LookupError(f"{code} {ch} 還沒譯")
    d = json.loads(f.read_text(encoding="utf-8"))
    got = [(v, d[str(v)]) for v in range(v1, v2 + 1) if d.get(str(v))]
    if len(got) != v2 - v1 + 1:
        raise LookupError(f"{code} {ch}:{v1}-{v2} 缺節")
    return got


def verse_hint(text: str, prefer: str = "cuv2010", limit: int = 4) -> str:
    """給翻譯 prompt 的經文提示；原文沒有經文出處（或查不到）就回空字串。

    prefer="jbungo_zh"：先用文語譯直譯；那一處還沒譯（或缺節）就退回和修。
    同一段裡兩種來源並存時各自標出處，不混成一段。"""
    refs = find_refs(text)[:limit]
    if not refs:
        return ""
    try:
        import course_quote_bible as cqb
    except Exception:  # noqa: BLE001
        return ""
    lines: dict[str, list[str]] = {}
    for code, ch, v1, v2 in refs:
        order = ["jbungo_zh", "cuv2010"] if prefer == "jbungo_zh" else ["cuv2010"]
        for ver in order:
            try:                                       # 和修詩體殘缺會丟 LookupError
                vs = _jbungo_zh(code, ch, v1, v2) if ver == "jbungo_zh" else cqb.verses(code, ch, v1, v2)
            except Exception:  # noqa: BLE001 — 查不到或殘缺就換下一個，都沒有就照規則譯
                continue
            name = cqb.BOOKS.get(code) or code
            rng = f"{v1}" if v1 == v2 else f"{v1}–{v2}"
            lines.setdefault(ver, []).append(f"{name} {ch}:{rng}：" + "".join(t for _, t in vs))
            break
    return "\n\n".join(HEAD[ver] + "\n" + "\n".join(ls) for ver, ls in lines.items())


def cuv2010_hint(text: str, limit: int = 4) -> str:
    return verse_hint(text, "cuv2010", limit)


def with_hint(prompt_tmpl: str, source: str, prefer: str = "cuv2010") -> str:
    """把經文提示插在 prompt 的「原文：」標頭之前。回傳可再 .format(source=...) 的模板。"""
    hint = verse_hint(source, prefer)
    if not hint:
        return prompt_tmpl
    hint = hint.replace("{", "{{").replace("}", "}}")
    head, sep, tail = prompt_tmpl.rpartition("\n\n")
    return f"{head}\n\n{hint}{sep}{tail}" if sep else prompt_tmpl + "\n\n" + hint
