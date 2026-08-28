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

# 大正藏 T56–T84（日本撰述部）CBETA 未收錄 XML，故下列部類必然為空。
# 保留區間定義以求分類完整，但目錄頁不列出（凡例須說明「非本站遺漏」）。
CBETA_MISSING_VOLS = set(range(56, 85))

def division_of(canon: str, work_no: int, vol: int = 0) -> str:
    """T 按經號分部，N 按冊號分部（N 的經號只是冊內序號，不可拿來分部）。"""
    if canon == "T":
        table, n = TAISHO_DIVISIONS, work_no
    else:
        table, n = NANCHUAN_DIVISIONS, vol
    for key, _label, lo, hi in table:
        if lo <= n <= hi:
            return key
    return "other"


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

    # 作品 id：T 的經號跨冊唯一（T0099 即通行引用式）；
    # N 的經號只是冊內序號（N01n0001 ≠ N02n0001），必須帶冊號才唯一。
    wid = f"{canon}{no:04d}{sfx}" if canon == "T" else f"{canon}{vol:02d}n{no:04d}{sfx}"
    return {
        "id": wid,
        "canon": canon,
        "vol": vol,
        "work_no": no,
        "work_suffix": sfx,
        "title_zh": _title("m", True) or _title("m", False),
        "byline": byline,
        "dynasty": bl["dynasty"],
        "translator": bl["translator"],
        "author": bl["author"],
        "lost_translator": bl["lost_translator"],
        "roles": bl["roles"],
        "extent": extent,
        "juan_count": juan,
        "division_key": division_of(canon, no, vol),
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
