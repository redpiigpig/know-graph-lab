"""Pure core for the 「翻譯定名」glossary (/translation-glossary, promoted to a
top-level card). Domain taxonomy + the 名根一致性 (name-root consistency) rule +
variant parsing. No DB / no network — tested by tests/test_glossary_naming.py.

Architecture (user decision 2026-06-03): keep the two theology tables, ADD one
table per new domain. A `name_root` (canonical Chinese root substring, e.g.
「塞琉」/「密特」/「亞歷山」) ties together names derived from the same source root
so their Chinese renderings stay consistent — every entry tagged with a root
must contain that root string in its recommended translation.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable


# ── Domain taxonomy ──────────────────────────────────────────────────────────
# `is_page` marks the static 翻譯原則 page (no table). Everything else is a tab
# backed by a DB table. theology tables are kept as-is; the rest are new.
DOMAINS: list[dict] = [
    {"key": "principles",        "label_zh": "翻譯原則",       "is_page": True,  "table": None,                "order": 0},
    {"key": "biblical_people",   "label_zh": "聖經人物",       "table": "theologians",        "filter": {"role": "聖經人物"}, "order": 10},
    {"key": "theologians",       "label_zh": "教父與神學家",   "table": "theologians",        "order": 20},
    {"key": "theological_terms", "label_zh": "神學名詞",       "table": "theological_terms",  "order": 30},
    {"key": "philosophers",      "label_zh": "哲學家",         "table": "philosophers",       "order": 40},
    {"key": "scientists",        "label_zh": "科學家",         "table": "scientists",         "order": 50},
    {"key": "rulers",            "label_zh": "歷代帝王",       "table": "historical_rulers",  "order": 60},
    {"key": "places",            "label_zh": "國名與城市",     "table": "place_names",        "order": 70},
    {"key": "deities",           "label_zh": "神祇與宗教名詞", "table": "deities",            "order": 80},
    {"key": "offices",           "label_zh": "官制與行政區",   "table": "official_titles",    "order": 90},
]

DOMAIN_BY_KEY = {d["key"]: d for d in DOMAINS}


# ── Admin register map (制對應) ───────────────────────────────────────────────
# The 官制與行政區 domain's novel layer: a foreign polity is mapped by *political-
# development stage & gestalt* (社會發展階段＋政治氣質, NOT calendar date) to a Han
# administrative *register*, and its offices / divisions are rendered from that
# register's vocabulary — instead of flattening everything to 總督/行省 (which is only
# the 明清 register). Small, conceptual, rarely-changing → lives here as pure data,
# not a DB table (mirrors DOMAINS). The map is a DEFAULT the user ratifies per
# feedback_glossary_ancient_name_priority; the seed sets `register` explicitly per row
# and check_register_matches_polity() guards typos / cross-era mistags. A polity may
# span two registers (Rome: 漢制 early / 魏晉制 late) — values may be str or list.
# 8 development-stage buckets, derived from offices_register_blueprint.md.
ADMIN_REGISTERS: list[dict] = [
    {"key": "shang_zhou", "label_zh": "商周制", "source": "《尚書‧周官》六卿、殷周金文",
     "central": ["太宰", "卿士", "三公", "六卿", "司徒", "司馬", "司空", "司寇"],
     "local": ["方國", "侯", "伯", "牧", "州伯", "方伯"],
     "note": "青銅神權城邦聯盟。阿卡德、古埃及、蘇美。"},
    {"key": "chunqiu", "label_zh": "春秋制", "source": "列國霸業、成文法典、南方巫覡",
     "central": ["相", "令尹", "大尹", "上卿"],
     "local": ["畿", "牧", "大尹"],
     "note": "霸業立法期（漢摩拉比≈齊桓）、商業神權（巴比倫≈楚/吳越）。古巴比倫、新巴比倫。"},
    {"key": "zhanguo_qin", "label_zh": "戰國秦制", "source": "郡縣、守尉、軍國",
     "central": ["丞相", "御史大夫", "太尉"],
     "local": ["鎮", "鎮監", "郡", "郡守", "郡尉", "守", "縣", "州", "州伯"],
     "note": "軍國擴張、廢封建置郡縣。新亞述（軍事鎮）、希臘化王國（郡尉）、波斯（州/州伯）。"},
    {"key": "han", "label_zh": "漢制", "source": "州郡縣＋郡國並行、都護、封侯",
     "central": ["皇帝", "三公", "九卿", "尚書台"],
     "local": ["行省", "牧", "都護", "郡", "太守", "都尉", "大尹", "屬國", "諸侯王"],
     "note": "廣域帝國＋郡國並行。羅馬共和/帝國早期（元老院行省牧／皇帝行省都護）。"},
    {"key": "weijin", "label_zh": "魏晉制", "source": "行臺—州—郡三級科層",
     "central": ["行臺尚書令"],
     "local": ["大區行臺", "行臺令", "州", "刺史", "郡", "太守"],
     "note": "帝國晚期權力切碎、層層節制。羅馬帝國晚期（戴克里先改革後三級制）。"},
    {"key": "tang", "label_zh": "唐制", "source": "道州縣、節度使軍鎮、經略安撫使",
     "central": ["宰相", "三省", "六部"],
     "local": ["道", "軍道", "節度使", "經略使", "都護", "都督", "州", "府", "縣", "留守"],
     "note": "軍區/藩鎮與邊疆經營。東羅馬軍區（軍道節度使）、阿拉伯-阿拔斯哈里發（道經略使）。"},
    {"key": "song", "label_zh": "宋制", "source": "路—州縣、監司(漕憲帥倉)、知州通判、二府三司",
     "central": ["中書門下", "樞密院", "三司", "參知政事"],
     "local": ["路", "知州", "知府", "知縣", "轉運使", "安撫使", "提點刑獄", "通判", "監司", "三司使"],
     "note": "中央集權文官＋商業繁盛＋強幹弱枝。官僚成熟的 civil 行政層。東羅馬晚期中央文官（知州/三司使）。"},
    {"key": "liao_jin_yuan", "label_zh": "遼金元制", "source": "南北面官、行中書省、達魯花赤、萬戶千戶百戶、猛安謀克",
     "central": ["可汗", "大汗", "北面官", "南面官", "中書省"],
     "local": ["行省", "達魯花赤", "萬戶", "千戶", "百戶", "猛安", "謀克", "斡魯朵", "招討使"],
     "note": "征服王朝／游牧帝國：南北面雙軌治農牧、十進位軍事編制。安息(帕提亞)、塞爾柱、蒙古諸汗國、帖木兒。"},
    {"key": "ming_qing", "label_zh": "明清制", "source": "督撫、布政使、府州縣、八旗、土司",
     "central": ["內閣", "六部", "大學士"],
     "local": ["總督", "巡撫", "副王", "提督", "布政使", "旗", "旗主", "道臺", "府", "州", "縣", "土司"],
     "note": "近世火藥帝國＋殖民督撫；「總督/行省/副王」在此 register 才恰當。鄂圖曼、蒙兀兒、俄羅斯、近世殖民帝國。"},
    {"key": "zhou_feudal", "label_zh": "周封建五等爵", "source": "《周禮》公侯伯子男",
     "central": [],
     "local": ["公", "侯", "伯", "子", "男"],
     "note": "封建領主制；中世紀西歐 duke公/marquis侯/count伯/viscount子/baron男（此組傳統譯已 register-正確）。"},
]

REGISTER_BY_KEY = {r["key"]: r for r in ADMIN_REGISTERS}
REGISTER_LABELS = {r["label_zh"] for r in ADMIN_REGISTERS}

# Default polity → register label(s). DEFAULT per offices_register_blueprint.md; keys
# align with the 王朝-民族帝國 naming used in place_names / historical_rulers. A list
# value = a polity that legitimately spans registers by period.
REGISTER_BY_POLITY: dict[str, str | list[str]] = {
    "阿卡德帝國": "商周制", "古埃及": "商周制", "蘇美": "商周制",
    "古巴比倫": "春秋制", "新巴比倫帝國": "春秋制",
    "新亞述帝國": "戰國秦制", "阿契美尼德-波斯帝國": "戰國秦制",
    "塞琉古-希臘帝國": "戰國秦制", "托勒密-埃及": "戰國秦制",
    "羅馬共和國": "漢制", "羅馬帝國": ["漢制", "魏晉制"],
    "拜占庭帝國": ["唐制", "宋制"], "阿拔斯-阿拉伯帝國": "唐制",
    "安息-帕提亞帝國": "遼金元制", "塞爾柱-突厥帝國": "遼金元制",
    "蒙古帝國": "遼金元制", "伊兒汗國": "遼金元制", "金帳汗國": "遼金元制", "帖木兒帝國": "遼金元制",
    "鄂圖曼-土耳其帝國": "明清制", "蒙兀兒帝國": "明清制", "俄羅斯帝國": "明清制",
    "中世紀西歐封建": "周封建五等爵",
}


def registers_for_polity(polity: str | None) -> list[str]:
    """Return the default register label(s) for a polity ([] if unmapped)."""
    if not polity:
        return []
    v = REGISTER_BY_POLITY.get(polity.strip())
    if v is None:
        return []
    return [v] if isinstance(v, str) else list(v)


def register_for_polity(polity: str | None) -> str | None:
    """The single default register for a polity (first, if it spans several)."""
    regs = registers_for_polity(polity)
    return regs[0] if regs else None


def check_register_valid(entries: Iterable[dict]) -> list[dict]:
    """Flag office entries whose `register` is not one of the defined registers
    (guards against typos like 「漢代制」). Entries with no register are ignored."""
    bad: list[dict] = []
    for e in entries:
        reg = (e.get("register") or "").strip()
        if reg and reg not in REGISTER_LABELS:
            bad.append(e)
    return bad


def check_register_matches_polity(entries: Iterable[dict]) -> list[dict]:
    """Flag office entries whose `register` is not among the register(s) its `polity`
    maps to (e.g. a Roman office tagged 唐制 when Rome is 漢制/魏晉制). Same spirit as
    check_root_consistency. Entries whose polity is unmapped, or which carry no
    register, are ignored — override intentionally by leaving polity blank."""
    bad: list[dict] = []
    for e in entries:
        reg = (e.get("register") or "").strip()
        allowed = registers_for_polity(e.get("polity"))
        if reg and allowed and reg not in allowed:
            bad.append({**e, "_expected_register": "／".join(allowed)})
    return bad


# ── Variant parsing ──────────────────────────────────────────────────────────
_VARIANT_SEP = re.compile(r"[；;]")


def split_variants(value: str | None) -> list[str]:
    """Split a 「；」/「;」-separated variant string into trimmed, non-empty parts."""
    if not value:
        return []
    return [p.strip() for p in _VARIANT_SEP.split(value) if p.strip()]


# ── Name-root consistency ────────────────────────────────────────────────────
def root_key(root: str | None) -> str:
    """Normalize a name_root for grouping (trim; ascii roots case-folded)."""
    if not root:
        return ""
    r = root.strip()
    # ascii (romanized) roots compare case-insensitively; CJK roots stay as-is
    return r.lower() if r.isascii() else r


def group_by_root(entries: Iterable[dict]) -> dict[str, list[dict]]:
    """Bucket entries by normalized name_root. Rootless entries are dropped."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        k = root_key(e.get("name_root"))
        if k:
            groups[k].append(e)
    return dict(groups)


def check_root_consistency(entries: Iterable[dict]) -> list[dict]:
    """Flag entries whose recommended translation does NOT honour their name_root.

    The rule (user 2026-06-03): names sharing a root render that root the same
    way — every entry tagged name_root=R must contain R in name_recommended.
    塞琉古/塞琉西亞 (root 塞琉) ✓; 西流基 ✗.  Returns the offending entries with
    their root attached. Rootless entries are ignored.
    """
    bad: list[dict] = []
    for e in entries:
        root = (e.get("name_root") or "").strip()
        if not root:
            continue
        rec = e.get("name_recommended") or ""
        if root not in rec:
            bad.append({**e, "name_root": root})
    return bad
