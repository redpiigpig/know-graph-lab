"""佛教大藏經 /tripitaka —— CBETA TEI P5 → 目錄 rows ＋ 逐段 JSONL。

《大正新脩大藏經》(canon T, 2,920 部) 與《漢譯南傳大藏經》(canon N, 元亨寺版)
的漢文層。原文（梵／巴／藏）由 tripitaka_parallels.py 另行掛上，本檔只管漢文。

切段規則（使用者定調 2026-08-28）：
  段的鍵 = 該段第一行的**大正藏行號**，如 `T09n0262_p0008a13`。不自編段號。
  段的邊界 = CBETA 新式標點本的 <p>／<lg>（編輯判斷，非原典自帶，凡例須註明）。

結構層級（見 .claude/skills/scripture-tripitaka/SKILL.md「對齊軸」一節）：
  L1 卷   <milestone unit="juan"> / <cb:juan>
  L2 品   <cb:div type="pin">          ← 跨語言主對齊層（梵 parivarta／藏 le'u）
  L3 經   <cb:div type="jing">          ← 阿含專用，雜阿含 1,355 經
     頌   <lg>/<l>                      ← 論頌專用，梵藏漢頌號共通
  L4 行號 <pb>/<lb>                     ← 引用座標，本檔用作段鍵

另從 <cb:div type="equiv-notes"> 抽出**大正藏原編的巴利對應註**
（雜阿含每經都掛了 "S. 22. 12-14." 這種 Saṃyutta Nikāya 相應編號），
這是漢巴對照最權威的一層骨架，不是我自己比對出來的。

純函式（parse_work / extract_text / resolve_gaiji / division_of…）零 network/DB，
由 scripts/tests/test_tripitaka_cbeta.py 鎖定。

  python scripts/tripitaka_cbeta.py --inspect T/T02/T02n0099.xml
  python scripts/tripitaka_cbeta.py --catalog            # 掃全藏 → 目錄 JSON
  python scripts/tripitaka_cbeta.py --build T0262        # 單部 → JSONL
  python scripts/tripitaka_cbeta.py --build-all --canon T
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

_ENV_PATH = SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    for _l in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

TEI = "http://www.tei-c.org/ns/1.0"
CB = "http://www.cbeta.org/ns/1.0"
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

# CBETA XML 本機快取（sparse clone of cbeta-org/xml-p5，T + N）。
# 這是可重下的快取，不進 git、不進 Drive。
CBETA_ROOT = Path(os.environ.get("CBETA_XML_DIR", "C:/tmp/cbeta/xml-p5"))
GAIJI_PATH = Path(os.environ.get("CBETA_GAIJI", "C:/tmp/cbeta/gaiji.json"))

# 逐段 JSONL 落地處（比照 EBOOK_CHUNKS_DIR，Drive 為正本、R2 為線上後備）
OUT_DIR = Path(os.environ.get(
    "TRIPITAKA_DIR",
    str(Path(os.environ.get("EBOOK_CHUNKS_DIR", "C:/tmp/cbeta/out")).parent / "_tripitaka"),
))


# ─────────────────────────────────────────────────────────────
# 大正藏部門（31 部類）。邊界依大正藏原編經號區間。
# --catalog 會驗證：無重疊、無空隙、每部至少一部經。
# ─────────────────────────────────────────────────────────────
TAISHO_DIVISIONS: list[tuple[str, str, int, int]] = [
    ("agama",      "阿含部",   1,    151),
    ("benyuan",    "本緣部",   152,  219),
    ("prajna",     "般若部",   220,  261),
    ("fahua",      "法華部",   262,  277),
    ("huayan",     "華嚴部",   278,  309),
    ("baoji",      "寶積部",   310,  373),
    ("niepan",     "涅槃部",   374,  396),
    ("daji",       "大集部",   397,  424),
    ("jingji",     "經集部",   425,  847),
    ("mijiao",     "密教部",   848,  1420),
    ("lu",         "律部",     1421, 1504),
    ("shijinglun", "釋經論部", 1505, 1535),
    ("pitan",      "毘曇部",   1536, 1563),
    ("zhongguan",  "中觀部",   1564, 1578),
    ("yuqie",      "瑜伽部",   1579, 1627),
    ("lunji",      "論集部",   1628, 1692),
    ("jingshu",    "經疏部",   1693, 1803),
    ("lushu",      "律疏部",   1804, 1815),
    ("lunshu",     "論疏部",   1816, 1850),
    ("zhuzong",    "諸宗部",   1851, 2025),
    ("shizhuan",   "史傳部",   2026, 2120),
    ("shihui",     "事彙部",   2121, 2136),
    ("waijiao",    "外教部",   2137, 2144),
    ("mulu",       "目錄部",   2145, 2184),
    # ── 以下為日本撰述部 ──
    ("xu-jingshu", "續經疏部", 2185, 2247),
    ("xu-lushu",   "續律疏部", 2248, 2252),
    ("xu-lunshu",  "續論疏部", 2253, 2308),
    ("xu-zhuzong", "續諸宗部", 2309, 2700),
    ("xitan",      "悉曇部",   2701, 2731),
    ("guyi",       "古逸部",   2732, 2864),
    ("yisi",       "疑似部",   2865, 2920),
]
JAPANESE_FROM = 2185  # 2185 起為日本撰述部

# 漢譯南傳大藏經（元亨寺版）N 部分部 —— **按冊號**，不是按經號。
# N 的經號是「冊內序號」（N01n0001 與 N02n0001 是兩部書），所以分部只能看冊。
# 以下邊界由實掃 70 冊 <title level="m"> 定出，非推測；見 SKILL.md「南傳分部」。
NANCHUAN_DIVISIONS: list[tuple[str, str, int, int]] = [
    ("n-vinaya",     "律藏",   1,  5),   # 經分別・犍度・附隨
    ("n-digha",      "長部",   6,  8),
    ("n-majjhima",   "中部",   9,  12),
    ("n-samyutta",   "相應部", 13, 18),
    ("n-anguttara",  "增支部", 19, 25),
    ("n-khuddaka",   "小部",   26, 47),  # 小誦…譬喻・本生・無礙解道・大小義釋
    ("n-abhidhamma", "論藏",   48, 62),  # 七論 ＋ 論事
    ("n-outside",    "藏外",   63, 70),  # 彌蘭王問・史書・清淨道論・攝義論・阿育王刻文
]

# ─────────────────────────────────────────────────────────────
# 卍新纂大日本續藏經 X 部（88 冊）。
#
# 🚨 部類邊界**不是憑記憶寫的**，是抓 CBETA 站方的「原書目錄」樹：
#     https://cbdata.dila.edu.tw/stable/catalog_entry?q=orig-X
#   （2026-08-31 取；第一層 7 部類、第二層 109 子類，經號區間由站方標明）
#   X 的 teiHeader 裡**沒有任何分類欄位**（<title level="s"> 一律是藏經名），
#   所以分部資訊只能外求，不能像南傳那樣實掃卷首標題。
#
# 第一層的經號區間連續覆蓋 1–1671，故可沿用 T 那套「按經號分部」。
# 第二層有三個子類的經號是**交錯不連續**的（史傳部的雜傳／感應神異傳／
# 居士善女傳），所以子類一律用「多段區間」表示，不可假設連續。
#
# ⚠ CBETA 收的是**選錄**（站方自書「卍新纂續藏經選錄」）：經號到 1671，
#   但實際只有 1,230 部有 XML。缺的不是本站漏抓，凡例須註明。
# ─────────────────────────────────────────────────────────────
XUZANG_DIVISIONS: list[tuple[str, str, int, int]] = [
    ("x-india", "印度撰述", 1, 207),  # X01-02
    ("x-jingshu", "大小乘釋經部", 208, 675),  # X03-37
    ("x-lushu", "大小乘釋律部", 676, 751),  # X38-44
    ("x-lunshu", "大小乘釋論部", 752, 862),  # X45-53
    ("x-zhuzong", "諸宗著述部", 863, 1458),  # X54-73
    ("x-lichan", "禮懺部", 1459, 1507),  # X74
    ("x-shizhuan", "史傳部", 1508, 1671),  # X75-88
]

XUZANG_SUBDIVISIONS: list[tuple[str, str, list[tuple[int, int]]]] = [
    # ── X01-02 印度撰述 ──
    ("x-india-001", "經部", [(1, 45)]),
    ("x-india-002", "律部", [(46, 51)]),
    ("x-india-003", "論集部", [(52, 58)]),
    ("x-india-004", "密經儀軌部", [(59, 207)]),
    # ── X03-37 大小乘釋經部 ──
    ("x-jingshu-001", "華嚴部疏", [(208, 242)]),
    ("x-jingshu-002", "方等部疏", [(243, 447)]),
    ("x-jingshu-003", "般若部疏", [(448, 576)]),
    ("x-jingshu-004", "法華部疏", [(577, 652)]),
    ("x-jingshu-005", "涅槃部疏", [(653, 664)]),
    ("x-jingshu-006", "小乘經並聖賢集疏", [(665, 675)]),
    # ── X38-44 大小乘釋律部 ──
    ("x-lushu-001", "大乘律疏", [(676, 706)]),
    ("x-lushu-002", "小乘律疏", [(707, 749)]),
    ("x-lushu-003", "疑似雜偽律疏", [(750, 751)]),
    # ── X45-53 大小乘釋論部 ──
    ("x-lunshu-001", "淨土論疏", [(752, 752)]),
    ("x-lunshu-002", "十地經論疏", [(753, 753)]),
    ("x-lunshu-003", "起信論疏", [(754, 769)]),
    ("x-lunshu-004", "釋摩訶衍論疏", [(770, 776)]),
    ("x-lunshu-005", "金剛頂菩提心論疏", [(777, 777)]),
    ("x-lunshu-006", "三論部疏", [(778, 783)]),
    ("x-lunshu-007", "四論部疏", [(784, 784)]),
    ("x-lunshu-008", "法界無差別論疏", [(785, 787)]),
    ("x-lunshu-009", "掌珍論疏", [(788, 788)]),
    ("x-lunshu-010", "法華論疏", [(789, 790)]),
    ("x-lunshu-011", "般若論疏", [(791, 792)]),
    ("x-lunshu-012", "瑜伽論疏", [(793, 795)]),
    ("x-lunshu-013", "雜集論疏", [(796, 796)]),
    ("x-lunshu-014", "中邊論疏", [(797, 798)]),
    ("x-lunshu-015", "百法並百法明門論疏", [(799, 805)]),
    ("x-lunshu-016", "唯識論疏", [(806, 829)]),
    ("x-lunshu-017", "觀所緣緣論疏", [(830, 833)]),
    ("x-lunshu-018", "俱舍並順正論疏", [(834, 843)]),
    ("x-lunshu-019", "異部宗輪論疏", [(844, 844)]),
    ("x-lunshu-020", "遺教經論疏", [(845, 846)]),
    ("x-lunshu-021", "因明論疏", [(847, 862)]),
    # ── X54-73 諸宗著述部 ──
    ("x-zhuzong-001", "三論宗", [(863, 880)]),
    ("x-zhuzong-002", "法相宗", [(881, 902)]),
    ("x-zhuzong-003", "天台宗", [(903, 980)]),
    ("x-zhuzong-004", "華嚴宗", [(981, 1033)]),
    ("x-zhuzong-005", "真言宗", [(1034, 1084)]),
    ("x-zhuzong-006", "戒律宗", [(1085, 1139)]),
    ("x-zhuzong-007", "淨土宗", [(1140, 1216)]),
    ("x-zhuzong-008", "禪宗雜著", [(1217, 1294)]),
    ("x-zhuzong-009", "禪宗語錄通集", [(1295, 1319)]),
    ("x-zhuzong-010", "禪宗語錄別集", [(1320, 1458)]),
    # X74 禮懺部：站方未再分子類（列的是逐部經），不設子類
    # ── X75-88 史傳部 ──
    ("x-shizhuan-001", "釋迦傳", [(1508, 1511)]),
    ("x-shizhuan-002", "編年通史", [(1512, 1521)]),
    ("x-shizhuan-003", "諸宗通傳", [(1522, 1527)]),
    ("x-shizhuan-004", "華嚴宗", [(1528, 1534)]),
    ("x-shizhuan-005", "天台宗", [(1535, 1542)]),
    ("x-shizhuan-006", "淨土宗", [(1543, 1552)]),
    ("x-shizhuan-007", "禪宗", [(1553, 1622)]),
    ("x-shizhuan-008", "法相宗", [(1651, 1651)]),
    ("x-shizhuan-009", "真言宗", [(1652, 1654)]),
    ("x-shizhuan-010", "戒律宗", [(1655, 1655)]),
    ("x-shizhuan-011", "雜傳", [(1623, 1628), (1640, 1645), (1647, 1650), (1656, 1656), (1658, 1659), (1666, 1667)]),
    ("x-shizhuan-012", "感應神異傳", [(1629, 1639), (1660, 1661)]),
    ("x-shizhuan-013", "居士善女傳", [(1646, 1646), (1657, 1657)]),
    ("x-shizhuan-014", "古剎傳", [(1662, 1665)]),
    ("x-shizhuan-015", "剌麻教", [(1668, 1668)]),
    ("x-shizhuan-016", "朝鮮僧史", [(1669, 1671)]),
]


# 大正藏 T56–T84（日本撰述部）CBETA 未收錄 XML，故下列部類必然為空。
# 保留區間定義以求分類完整，但目錄頁不列出（凡例須說明「非本站遺漏」）。
CBETA_MISSING_VOLS = set(range(56, 85))

def division_of(canon: str, work_no: int, vol: int = 0) -> str:
    """T／X 按經號分部，N 按冊號分部（N 的經號只是冊內序號，不可拿來分部）。

    🚨 原本寫成「不是 T 就套南傳表」，加 X 進來時那個 else 會把整部續藏
    默默按冊號丟進南傳的八個分部裡 —— 每一部都會拿到一個看起來正常的
    division_key（X01 → n-vinaya…），目錄頁完全不會報錯。故改成明列。
    """
    if canon == "T":
        table, n = TAISHO_DIVISIONS, work_no
    elif canon == "X":
        table, n = XUZANG_DIVISIONS, work_no
    elif canon == "N":
        table, n = NANCHUAN_DIVISIONS, vol
    else:
        raise ValueError(f"未知的藏經代號 {canon!r}：要先為它定義部類表，"
                         f"不可沿用別藏的表")
    for key, _label, lo, hi in table:
        if lo <= n <= hi:
            return key
    return "other"


def subdivision_of(canon: str, work_no: int) -> str:
    """X 的第二層子類（宗派／經疏類目）。只有 X 有；其餘藏回空字串。

    子類的經號**可能交錯不連續**（史傳部的雜傳散在 1623-1628、1640-1645…），
    所以是多段區間比對，不是單一 lo..hi。
    """
    if canon != "X":
        return ""
    for key, _label, spans in XUZANG_SUBDIVISIONS:
        for lo, hi in spans:
            if lo <= work_no <= hi:
                return key
    return ""


def is_japanese_compilation(canon: str, work_no: int) -> bool:
    """日本撰述部（T2185 起）—— 目錄上另立一區，不與漢譯／中土撰述混列。"""
    return canon == "T" and work_no >= JAPANESE_FROM


# ─────────────────────────────────────────────────────────────
# 缺字（gaiji）
# ─────────────────────────────────────────────────────────────
_GAIJI: dict | None = None


def load_gaiji() -> dict:
    global _GAIJI
    if _GAIJI is None:
        _GAIJI = json.loads(GAIJI_PATH.read_text(encoding="utf-8")) if GAIJI_PATH.exists() else {}
    return _GAIJI


def resolve_gaiji(cb_id: str, table: dict | None = None) -> str:
    """CB 缺字碼 → 可顯示字元。

    優先序：Unicode 正字 → 通用歸正字 → 組字式（[肄-聿+欠]）→ 原碼。
    組字式是 CBETA 的標準退路，讀者看得懂，不可丟。
    """
    table = load_gaiji() if table is None else table
    e = table.get(cb_id)
    if not e:
        return f"[{cb_id}]"
    return (e.get("uni_char") or e.get("norm_big5_char")
            or e.get("composition") or f"[{cb_id}]")


# ─────────────────────────────────────────────────────────────
# 取文
# ─────────────────────────────────────────────────────────────
def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _clean(s: str) -> str:
    """折行不插空格（漢文接行），收斂多餘空白，保留全形空格。"""
    s = re.sub(r"[ \t]*\n[ \t\n]*", "", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def extract_text(el: ET.Element, gaiji: dict | None = None) -> str:
    """遞迴取純文字。大藏經與現代散文不同，規則較細：

      <note place="inline">  夾註 → 保留，加圓括號（原書就是雙行小字夾註）
      <note>（其餘 foot）     校勘／對應註 → 剝除，另存 notes
      <app>                  異文 → 取 <lem> 正字，丟 <rdg> 異讀
      <g ref="#CB00001"/>    缺字 → 查表還原
      <lb>/<pb>/<anchor>     邊碼 → 不入文
      <space>                → 一個空格
      <l>                    偈頌單行 → 由 parse 層處理換行，此處僅取字
    """
    gaiji = load_gaiji() if gaiji is None else gaiji
    tag = _local(el.tag)

    if tag == "note":
        if el.get("place") == "inline":
            inner = "".join(_child_text(c, gaiji) for c in _walk_children(el))
            inner = _clean((el.text or "") + inner)
            return f"（{inner}）" if inner else ""
        return ""
    if tag in ("lb", "pb", "anchor", "milestone", "rdg", "orig", "sic"):
        return ""
    if tag == "space":
        return " "
    if tag == "g":
        return resolve_gaiji((el.get("ref") or "").lstrip("#"), gaiji)
    if tag == "app":
        lem = el.find(f"{{{TEI}}}lem")
        base = extract_text(lem, gaiji) if lem is not None else (el.text or "")
        return base + "".join(c.tail or "" for c in el if _local(c.tag) == "lem")
    if tag == "tt":
        # <cb:tt> 是漢／梵／巴詞條對照組。少數出現在正文中（多為悉曇字替換），
        # 若把三種語言一起串進來，正文會變成「長阿含經Dīrgha-āgamaDīgha-nikāya」。
        # 正文只取漢文那一支，外語形另由 parse_terms() 收成詞條層。
        zh = [c for c in el if _local(c.tag) == "t"
              and (c.get(XML_LANG) or "").startswith("zh")]
        pick = zh[0] if zh else next((c for c in el if _local(c.tag) == "t"), None)
        return extract_text(pick, gaiji) if pick is not None else ""

    parts = [el.text or ""]
    for child in el:
        parts.append(extract_text(child, gaiji))
        parts.append(child.tail or "")
    return "".join(parts)


def _walk_children(el: ET.Element):
    return list(el)


def _child_text(c: ET.Element, gaiji: dict) -> str:
    return extract_text(c, gaiji) + (c.tail or "")


def collect_notes(el: ET.Element, gaiji: dict | None = None) -> list[dict]:
    """段內的腳註（校勘／大正藏原註），保留註號以便回貼行號。"""
    gaiji = load_gaiji() if gaiji is None else gaiji
    out = []
    for n in el.iter(f"{{{TEI}}}note"):
        if n.get("place") == "inline":
            continue
        txt = _clean("".join(extract_text(c, gaiji) + (c.tail or "") for c in n)
                     + "" if False else extract_text(n, gaiji) or _raw_note_text(n, gaiji))
        if txt:
            out.append({"n": n.get("n"), "type": n.get("type") or "corr", "text": txt})
    return out


def _raw_note_text(n: ET.Element, gaiji: dict) -> str:
    parts = [n.text or ""]
    for c in n:
        parts.append(extract_text(c, gaiji))
        parts.append(c.tail or "")
    return _clean("".join(parts))


# ─────────────────────────────────────────────────────────────
# 解析一部經
# ─────────────────────────────────────────────────────────────
SKIP_DIV_TYPES = {"apparatus", "cbeta-notes", "taisho-notes", "add-notes",
                  "rest-notes", "equiv-notes", "orig-notes"}


_SPLIT_SUFFIX = re.compile(r"[（(]第\d+卷-第\d+卷[）)]$")


def _norm_title(title: str) -> str:
    """剝掉拆檔書名尾巴的「(第1卷-第44卷)」。

    那是 CBETA 為「同一部書拆成兩個 XML 檔」加的卷範圍註記，不是書名的一部分；
    留著會讓同一部書的上下半在目錄上看起來是兩本不同的書。
    全 X 部只有 12 個檔（＝6 部書 × 2）帶這個式樣，實掃確認過。
    ⚠ 只剝這個確切式樣：「華嚴經論〔卷十〕」「四家語錄卷一」那類的「卷」
    是書名本身，剝掉就改了書名。
    """
    return _SPLIT_SUFFIX.sub("", title).strip()


def work_meta(root: ET.Element) -> dict:
    """teiHeader → 目錄欄位。"""
    def _title(level: str, zh: bool) -> str:
        for t in root.iter(f"{{{TEI}}}title"):
            if t.get("level") != level:
                continue
            lang = (t.get(XML_LANG) or "")
            if zh and not lang.startswith("zh"):
                continue
            if not zh and lang.startswith("zh"):
                continue
            if (t.text or "").strip():
                return t.text.strip()
        return ""

    idno = {i.get("type"): (i.text or "").strip()
            for i in root.iter(f"{{{TEI}}}idno") if i.get("type")}
    author_el = root.find(f".//{{{TEI}}}titleStmt/{{{TEI}}}author")
    byline = _clean(author_el.text or "") if author_el is not None else ""
    extent_el = root.find(f".//{{{TEI}}}extent")
    extent = _clean(extent_el.text or "") if extent_el is not None else ""

    canon = idno.get("canon", "")
    vol = int(idno.get("vol") or 0)
    # 經號偶有字母後綴（T2917A／T2917B 是同號兩本），int() 會直接炸
    m_no = re.match(r"(\d+)([A-Za-z]*)", idno.get("no") or "0")
    no, sfx = int(m_no.group(1)), m_no.group(2)
    bl = parse_byline(byline)
    juan = 0
    m = re.match(r"(\d+)", extent)
    if m:
        juan = int(m.group(1))

    # 作品 id：T 與 X 的經號跨冊唯一（T0099、X0240 即通行引用式）；
    # N 的經號只是冊內序號（N01n0001 ≠ N02n0001），必須帶冊號才唯一。
    # ⚠ X 有 6 部書因印本跨冊而被切成兩個 XML 檔（華嚴綱要 X08+X09 等），
    #   兩檔同經號 —— 那是**同一部書的上下半**，不是兩部書。id 取經號即可，
    #   但建置時必須把兩檔接起來，否則後一檔會把前一檔整個蓋掉（見 split_works）。
    wid = (f"{canon}{no:04d}{sfx}" if canon in ("T", "X")
           else f"{canon}{vol:02d}n{no:04d}{sfx}")
    return {
        "id": wid,
        "canon": canon,
        "vol": vol,
        "work_no": no,
        "work_suffix": sfx,
        "title_zh": _norm_title(_title("m", True) or _title("m", False)),
        "byline": byline,
        "dynasty": bl["dynasty"],
        "translator": bl["translator"],
        "author": bl["author"],
        "lost_translator": bl["lost_translator"],
        "roles": bl["roles"],
        "extent": extent,
        "juan_count": juan,
        "division_key": division_of(canon, no, vol),
        "subdivision_key": subdivision_of(canon, no),
        "japanese": is_japanese_compilation(canon, no),
    }


_DYNASTIES = ["後秦", "姚秦", "苻秦", "前秦", "西秦", "劉宋", "蕭齊", "南齊", "北涼", "北魏",
              "東魏", "西魏", "北齊", "北周", "曹魏", "東晉", "西晉", "後漢", "東漢", "後漢",
              "吳", "魏", "晉", "宋", "齊", "梁", "陳", "隋", "唐", "周", "五代", "後周",
              "元", "明", "清", "漢", "秦", "日本", "高麗", "新羅"]


# 署名的職事後綴。順序即優先序（長的先比，"共譯" 要贏過 "譯"）。
_ROLES = ["共譯", "等譯", "重譯", "合譯", "奉詔譯", "譯", "造", "撰", "述", "集",
          "說", "記", "抄", "編", "註", "注", "疏", "釋", "解", "校", "勘", "治定"]
# 一部經常見的複合署名：'龍樹菩薩造 梵志青目釋 姚秦 鳩摩羅什譯'
_ROLE_ALIAS = {"共譯": "譯", "等譯": "譯", "重譯": "譯", "合譯": "譯", "奉詔譯": "譯",
               "註": "注", "解": "注", "疏": "注"}


def parse_byline(byline: str) -> dict:
    """大正藏署名 → 結構化職事。

    署名格式不統一：有的只有譯者、有的作者／註者／譯者三段、有的「失譯」。
    朝代可能單獨成一段夾在中間（'…青目釋 姚秦 鳩摩羅什譯'），所以要
    「遇到裸朝代就記著，掛給下一個職事」，不能只看開頭。
    對不上任何職事後綴的整串留在 raw，不硬拆。
    """
    s = re.sub(r"[　\s]+", " ", (byline or "").strip())
    if not s:
        return {"dynasty": "", "translator": "", "author": "",
                "lost_translator": False, "roles": [], "raw": ""}

    lost = bool(re.search(r"失譯|闕譯|不載譯人|附.{0,4}錄", s))
    roles: list[dict] = []
    pending_dyn = ""
    for tok in s.split(" "):
        tok = tok.strip()
        if not tok:
            continue
        if tok in _DYNASTIES:            # 裸朝代，掛給下一個職事
            pending_dyn = tok
            continue
        dyn = pending_dyn
        for d in sorted(_DYNASTIES, key=len, reverse=True):
            if tok.startswith(d) and len(tok) > len(d):
                dyn, tok = d, tok[len(d):]
                break
        hit = next((r for r in _ROLES if tok.endswith(r)), "")
        name = tok[: -len(hit)] if hit else tok
        # '佛陀耶舍共竺佛念' = 二人合譯，拆成名單（首位為主名）
        names = [n for n in re.split(r"[共及與]|等", name.strip()) if n]
        roles.append({"role": _ROLE_ALIAS.get(hit, hit) or "?",
                      "name": name.strip(), "names": names, "dynasty": dyn})
        if dyn:
            pending_dyn = ""

    def pick(*want: str) -> dict | None:
        for w in want:
            for r in roles:
                if r["role"] == w:
                    return r
        return None

    tr = pick("譯")
    au = pick("造", "撰", "述", "集", "說")
    # 朝代以譯者那一段為準（漢譯佛典的斷代看的是譯出年代，不是著作年代）
    dynasty = (tr or au or {}).get("dynasty", "") or next(
        (r["dynasty"] for r in roles if r["dynasty"]), "")
    return {
        "dynasty": dynasty,
        "translator": "" if lost and not tr else (tr or {}).get("name", ""),
        "author": (au or {}).get("name", ""),
        "lost_translator": lost,
        "roles": roles,
        "raw": s,
    }


def split_byline(byline: str) -> tuple[str, str]:
    b = parse_byline(byline)
    return b["dynasty"], b["translator"] or b["author"]


def parse_work(xml_text: str) -> tuple[dict, list[dict], list[dict]]:
    """CBETA TEI → (meta, segments, equivalents)。

    segments 每筆 = 一個 <p> 或一個 <lg>（偈頌整組），鍵為該段首行的大正藏行號。
    """
    gaiji = load_gaiji()
    root = ET.fromstring(xml_text)
    meta = work_meta(root)

    body = root.find(f".//{{{TEI}}}body")
    segs: list[dict] = []
    if body is None:
        return meta, segs, equivalents

    state = {"juan": 0, "page": "", "line": "", "idx": 0, "line_use": {}}
    toc: list[dict] = []          # 結構樹（卷/品/經），供 reader 側欄
    toc_key: dict[tuple, int] = {}
    anchor_seg: dict[str, str] = {}   # anchor xml:id → 所屬段，供詞條層回貼
    wid = meta["id"]
    vol = meta["vol"]
    canon = meta["canon"]

    pfx = f"{canon}{vol:02d}n{meta['work_no']:04d}{meta['work_suffix']}"

    def cite(line: str) -> str:
        return f"{pfx}_p{line}" if line else ""

    def toc_index(path: list[dict], first_uid: str) -> int:
        """把 div 路徑登記進目錄樹，回傳最深一層的索引（-1 = 不在任何 div 內）。"""
        parent = -1
        for depth, node in enumerate(path):
            if not node.get("head"):
                continue
            key = (depth, node["head"], parent)
            if key not in toc_key:
                toc_key[key] = len(toc)
                toc.append({"i": len(toc), "depth": depth, "type": node["type"],
                            "head": node["head"], "n": node.get("n"),
                            "parent": parent, "uid": first_uid,
                            "juan": state["juan"]})
            parent = toc_key[key]
        return parent

    def emit(el: ET.Element, kind: str, path: list[dict]):
        """一個 <p>/<lg>/<head> → 一筆 segment。"""
        first_line = _first_line_in(el) or state["line"]
        if kind == "verse":
            lines = [_clean(extract_text(l, gaiji))
                     for l in el.iter(f"{{{TEI}}}l")]
            text = "\n".join(x for x in lines if x)
        else:
            text = _clean(extract_text(el, gaiji))
        if not text:
            return
        state["idx"] += 1
        seg_id = f"{pfx}_p{first_line}" if first_line else f"{wid}#{state['idx']}"
        # 🚨 行號不唯一：同一行可以起頭好幾段（全藏 6.5%、672 部）。
        # seg 是引用式（照使用者定調，就是大正藏行號，允許重複），
        # uid 才是鍵 —— 對照、詞條、DOM anchor 全掛 uid，否則同行的段會互相串。
        seen = state["line_use"][seg_id] = state["line_use"].get(seg_id, 0) + 1
        uid = seg_id if seen == 1 else f"{seg_id}.{seen}"
        # 記下段內每個 anchor 落在哪一段 —— <cb:tt> 的漢梵巴詞條用
        # from="#beg0001011" 指回正文，靠這張表才貼得回去
        for a in el.iter(f"{{{TEI}}}anchor"):
            aid = a.get("{http://www.w3.org/XML/1998/namespace}id")
            if aid:
                anchor_seg[aid] = uid
        segs.append({
            "i": state["idx"],
            "uid": uid,
            "seg": seg_id,
            "juan": state["juan"] or None,
            "d": toc_index(path, uid),   # 目錄樹索引，非整串路徑（省 95 萬段的重複）
            "kind": kind,
            "sources": {"lzh": text},
            "notes": collect_notes(el, gaiji) or None,
        })

    def walk(el: ET.Element, path: list[dict]):
        for child in el:
            t = _local(child.tag)
            if t == "milestone" and child.get("unit") == "juan":
                state["juan"] = int(child.get("n") or 0)
            elif t == "juan" and child.get("fun") == "open":
                try:
                    state["juan"] = int(child.get("n") or 0)
                except ValueError:
                    pass
            elif t == "pb":
                state["page"] = child.get("n") or ""
            elif t == "lb":
                state["line"] = child.get("n") or ""
            elif t == "div":
                dtype = child.get(f"{{{CB}}}type") or child.get("type") or ""
                if dtype in SKIP_DIV_TYPES:
                    continue
                head = _div_head(child, gaiji)
                walk(child, path + [{"type": dtype, "head": head,
                                     "n": _div_n(child)}])
            elif t in ("head", "jhead"):
                # cb:jhead＝卷首標題；漏收會讓整批目錄部的經只剩空殼
                emit(child, "head", path)
            elif t in ("byline", "jl_byline"):
                emit(child, "byline", path)
            elif t == "p":
                emit(child, "prose", path)
            elif t == "lg":
                emit(child, "verse", path)
            elif t == "item":
                # 目錄部的經錄條目寫成 <item><title>經名</title></item>，
                # 底下沒有 <p>。只遞迴不 emit 的話整部經會解析成 0 段。
                if any(_local(c.tag) in ("p", "lg", "list", "div") for c in child):
                    walk(child, path)
                else:
                    emit(child, "item", path)
            elif t in ("list", "table", "cell", "row", "quote"):
                walk(child, path)

    walk(body, [])
    meta["toc"] = toc
    meta["terms"] = parse_terms(root, anchor_seg, gaiji)
    # 對應註要在 walk 之後才解析：註號靠正文裡的 anchor 才貼得回段落
    equivalents = parse_equivalents(root, anchor_seg, gaiji)
    return meta, segs, equivalents


# 詞條對照的語言碼：CBETA 用 xml:lang，本站統一成 sa / pi / sa-Sidd
_TERM_LANGS = {"sa": "sa", "san": "sa", "san-tr": "sa", "sa-x-rj": "sa",
               "pi": "pi", "pli": "pi", "sa-Sidd": "sa-Sidd", "zh-x-yy": "zh-alt"}


def parse_terms(root: ET.Element, anchor_seg: dict[str, str] | None = None,
                gaiji: dict | None = None) -> list[dict]:
    """<cb:tt> → 漢／梵／巴詞條對照（全藏 30,702 組，143 部）。

        <cb:tt from="#beg0001011">
          <cb:t xml:lang="zh-Hant">長阿含經</cb:t>
          <cb:t xml:lang="sa">Dīrgha-āgama</cb:t>
          <cb:t xml:lang="pi">Dīgha-nikāya</cb:t>
        </cb:tt>

    這是大正藏／CBETA 編者自己做的對照，不是我比對出來的 —— 資料來源要
    在 UI 標明，別和本站自行對齊的段落混為一談。
    """
    gaiji = load_gaiji() if gaiji is None else gaiji
    anchor_seg = anchor_seg or {}
    out = []
    for tt in root.iter():
        if _local(tt.tag) != "tt":
            continue
        zh, forms = "", {}
        for t in tt:
            if _local(t.tag) != "t":
                continue
            lang = t.get(XML_LANG) or ""
            txt = _clean(extract_text(t, gaiji))
            if not txt:
                continue
            if lang.startswith("zh") and lang != "zh-x-yy":
                zh = zh or txt
            else:
                key = _TERM_LANGS.get(lang, lang)
                forms.setdefault(key, txt)
        if not zh or not forms:
            continue
        anchor = (tt.get("from") or "").lstrip("#")
        out.append({"zh": zh, "forms": forms,
                    "uid": anchor_seg.get(anchor), "anchor": anchor or None})
    return out


def _div_n(div: ET.Element) -> str | None:
    for mulu in div:
        if _local(mulu.tag) == "mulu":
            return mulu.get("n")
    return div.get("n")


def _div_head(div: ET.Element, gaiji: dict) -> str:
    for child in div:
        if _local(child.tag) == "head":
            txt = _clean(extract_text(child, gaiji))
            if txt:
                return txt
    for child in div:
        if _local(child.tag) == "mulu":
            txt = _clean(extract_text(child, gaiji))
            if txt:
                return txt
    return ""


def _first_line_in(el: ET.Element) -> str:
    for lb in el.iter(f"{{{TEI}}}lb"):
        n = lb.get("n")
        if n:
            return n
    return ""


def parse_equivalents(root: ET.Element, anchor_seg: dict[str, str] | None = None,
                      gaiji: dict | None = None) -> list[dict]:
    """<cb:div type="equiv-notes"> → 大正藏原編的巴利對應。

    note n="0001001" 的前 4 碼是頁、後 3 碼是該頁註序 —— 這是回貼位置的鍵。
    文字如 "S. 22. 12-14. Anicca, etc." 再交給 tripitaka_parallels.py 正規化。
    """
    gaiji = load_gaiji() if gaiji is None else gaiji
    anchor_seg = anchor_seg or {}
    out = []
    # 注意：這個 div 在 cb: 命名空間下（<cb:div type="equiv-notes">），
    # 不是 tei:div —— 用 local name 比對，別寫死 {TEI}div。
    for div in root.iter():
        if _local(div.tag) != "div":
            continue
        if (div.get(f"{{{CB}}}type") or div.get("type")) != "equiv-notes":
            continue
        for n in div.iter(f"{{{TEI}}}note"):
            txt = _raw_note_text(n, gaiji)
            if txt:
                nn = n.get("n")
                out.append({"n": nn, "ref": txt,
                            "uid": anchor_seg.get(f"nkr_note_equivalent_{nn}")})
    return out


# ─────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────
def xml_files(canon: str) -> list[Path]:
    root = CBETA_ROOT / canon
    return sorted(root.glob(f"{canon}*/{canon}*n*.xml"))


_FILE_RE = re.compile(r"^([A-Z]+)(\d+)n(\d+)([A-Za-z]*)\.xml$")


def work_groups(canon: str) -> list[list[Path]]:
    """檔案 → 依「作品 id」分組，一組就是一部書。

    🚨 X 部有 6 部書因印本跨冊被切成兩個 XML 檔（華嚴綱要 X08n0240＋X09n0240、
    五燈全書 X81n1571＋X82n1571 …）。逐檔建置會讓後一檔把前一檔**整個蓋掉**
    （檔名都是 X0240.jsonl），華嚴綱要就只剩卷 45–80 而頁面完全正常 ——
    少掉的是前 44 卷。故一律先分組再建。
    T／N 沒有這種情形，每組就一個檔，行為不變。
    """
    groups: dict[str, list[Path]] = {}
    for p in xml_files(canon):
        m = _FILE_RE.match(p.name)
        if not m:
            groups.setdefault(p.name, []).append(p)
            continue
        cn, vol, no, sfx = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4)
        key = (f"{cn}{no:04d}{sfx}" if cn in ("T", "X")
               else f"{cn}{vol:02d}n{no:04d}{sfx}")
        groups.setdefault(key, []).append(p)
    return [sorted(v) for _k, v in sorted(groups.items())]


def merge_parts(parts: list[tuple[dict, list[dict], list[dict]]]
                ) -> tuple[dict, list[dict], list[dict]]:
    """把同一部書的數個 XML 檔接成一部。

    段的 `i` 與目錄節點的 `i`／`parent`，以及段指向目錄的 `d`，都是**檔內索引**，
    直接串接會讓後半部的目錄父子鏈指到前半部的節點上 —— 側欄看起來有東西、
    但層級全錯。故一律位移。段的 uid／seg 帶冊號（X09n0240_p0611a02），
    跨檔本來就不會撞，詞條與對應註引用的是 uid，不必動。
    """
    if len(parts) == 1:
        return parts[0]
    meta = dict(parts[0][0])
    segs: list[dict] = []
    toc: list[dict] = []
    terms: list[dict] = []
    equivs: list[dict] = []
    for m, s, e in parts:
        seg_off, toc_off = len(segs), len(toc)
        for node in m.get("toc", []):
            n2 = dict(node)
            n2["i"] += toc_off
            n2["parent"] = n2["parent"] + toc_off if n2["parent"] >= 0 else -1
            toc.append(n2)
        for x in s:
            x2 = dict(x)
            x2["i"] += seg_off
            x2["d"] = x2["d"] + toc_off if x2["d"] >= 0 else -1
            segs.append(x2)
        terms.extend(m.get("terms", []))
        equivs.extend(e)
    meta["toc"] = toc
    meta["terms"] = terms
    # 卷數是各檔相加（華嚴綱要 44 卷＋36 卷＝80 卷）；extent 改寫成合計
    total_juan = sum(m.get("juan_count") or 0 for m, _, _ in parts)
    meta["juan_count"] = total_juan
    meta["extent"] = f"{total_juan}卷" if total_juan else meta.get("extent", "")
    meta["xml_parts"] = len(parts)
    return meta, segs, equivs


def build_one(path: Path, *, write: bool) -> dict:
    meta, segs, equivs = parse_work(path.read_text(encoding="utf-8"))
    chars = sum(len(x["sources"]["lzh"]) for x in segs)
    toc = meta.pop("toc", [])
    terms = meta.pop("terms", [])
    langs = sorted({k for t in terms for k in t["forms"]} - {"zh-alt"})
    meta.update({"seg_count": len(segs), "char_count": chars,
                 "equiv_count": len(equivs), "toc_count": len(toc),
                 "term_count": len(terms), "term_langs": langs,
                 "xml_path": str(path.relative_to(CBETA_ROOT)).replace("\\", "/")})
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with (OUT_DIR / f"{meta['id']}.jsonl").open("w", encoding="utf-8") as f:
            for x in segs:
                f.write(json.dumps({k: v for k, v in x.items() if v is not None},
                                   ensure_ascii=False) + "\n")
        # 目錄樹與巴利對應另存：reader 側欄與對照建置不必讀完整段落檔
        (OUT_DIR / f"{meta['id']}.toc.json").write_text(
            json.dumps({"meta": meta, "toc": toc}, ensure_ascii=False), encoding="utf-8")
        if equivs:
            (OUT_DIR / f"{meta['id']}.equiv.json").write_text(
                json.dumps(equivs, ensure_ascii=False), encoding="utf-8")
        if terms:
            (OUT_DIR / f"{meta['id']}.terms.json").write_text(
                json.dumps(terms, ensure_ascii=False), encoding="utf-8")
    return meta


def cmd_inspect(rel: str):
    p = CBETA_ROOT / rel if not Path(rel).exists() else Path(rel)
    meta, segs, equivs = parse_work(p.read_text(encoding="utf-8"))
    toc = meta.pop("toc", [])
    terms = meta.pop("terms", [])
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"\n段 {len(segs)}　字 {sum(len(x['sources']['lzh']) for x in segs):,}"
          f"　目錄節點 {len(toc)}　巴利對應註 {len(equivs)}　漢梵巴詞條 {len(terms)}")
    if terms:
        print("詞條（前 4）:", json.dumps(terms[:4], ensure_ascii=False))

    def crumb(d: int) -> str:
        out = []
        while d >= 0:
            out.append(toc[d]["head"])
            d = toc[d]["parent"]
        return " › ".join(reversed(out))

    for x in segs[:6] + segs[len(segs) // 2: len(segs) // 2 + 4]:
        print(f"\n[{x['seg']}] 卷{x['juan']} {x['kind']} {crumb(x['d'])}")
        print("   " + x["sources"]["lzh"][:120].replace("\n", "\n   "))
    if equivs:
        print("\n巴利對應（前 5）:", json.dumps(equivs[:5], ensure_ascii=False))


def cmd_catalog(canons: list[str], out_path: Path):
    rows = []
    for canon in canons:
        files = xml_files(canon)
        print(f"{canon}: {len(files)} XML", flush=True)
        for i, p in enumerate(files, 1):
            try:
                rows.append(build_one(p, write=False))
            except Exception as e:  # noqa: BLE001
                print(f"  ⚠ {p.name}: {type(e).__name__} {e}", flush=True)
            if i % 200 == 0:
                print(f"  … {i}/{len(files)}", flush=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✓ {len(rows)} 部 → {out_path}")
    _report_divisions(rows)


def _report_divisions(rows: list[dict]):
    from collections import Counter
    c = Counter(r["division_key"] for r in rows)
    labels = {k: l for k, l, _, _ in TAISHO_DIVISIONS + NANCHUAN_DIVISIONS}
    for k, n in sorted(c.items(), key=lambda kv: -kv[1]):
        print(f"  {labels.get(k, k):8s} {n:5d} 部")
    if c.get("other"):
        print("  ⚠ 有 other，部門區間需修")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", type=str, help="單檔檢視（相對 CBETA_XML_DIR）")
    ap.add_argument("--catalog", action="store_true", help="掃全藏建目錄")
    ap.add_argument("--canon", type=str, default="T,N")
    ap.add_argument("--build", type=str, help="單部 id，如 T0262")
    ap.add_argument("--build-all", action="store_true")
    ap.add_argument("--out", type=str, default="C:/tmp/cbeta/catalog.json")
    a = ap.parse_args()

    canons = [c.strip() for c in a.canon.split(",") if c.strip()]
    if a.inspect:
        cmd_inspect(a.inspect)
    elif a.catalog:
        cmd_catalog(canons, Path(a.out))
    elif a.build:
        canon = a.build[0]
        no = int(a.build[1:])
        hit = [p for p in xml_files(canon) if f"n{no:04d}." in p.name]
        if not hit:
            sys.exit(f"找不到 {a.build}")
        m = build_one(hit[0], write=True)
        print(json.dumps(m, ensure_ascii=False))
    elif a.build_all:
        for canon in canons:
            files = xml_files(canon)
            for i, p in enumerate(files, 1):
                try:
                    m = build_one(p, write=True)
                    if i % 100 == 0:
                        print(f"  {canon} {i}/{len(files)} … {m['id']} {m['title_zh']}", flush=True)
                except Exception as e:  # noqa: BLE001
                    print(f"  ⚠ {p.name}: {type(e).__name__} {e}", flush=True)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
