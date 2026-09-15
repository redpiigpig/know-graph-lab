"""佛教大藏經 /tripitaka —— 德格版甘珠爾（藏文大藏經前半）TEI → 逐部段落資料。

藏經代號 **DK**（Derge Kangyur）。CBETA 那邊已佔用 T/X/N/A/B/C/CC/D/F/G/GA/GB/
I/J/K/L/LC/M/P/Q/R/S/TX/U/Y/YP/Z/ZS/ZW，DK 不與其中任何一個相撞。

產出與 CBETA 那條管線（scripts/tripitaka_cbeta.py）同構：
每部一個 `<id>.jsonl`（逐段）＋ `<id>.toc.json`（後設資料與節structure），
另出一份 `DK.catalog.json` 列全部的部。寫到 Drive `_tripitaka_tibetan/`
（**不碰既有的 `_tripitaka/`**）。

────────────────────────────────────────────────────────────────
來源
────────────────────────────────────────────────────────────────
`G:/我的雲端硬碟/資料/知識圖工作室/_corpus/tibetan-canon/src/
 derge-kangyur-UT4CZ5369-200106.zip`（39.4 MB，解壓 298 MB）
＝ Esukhia/derge-kangyur 的 TEI 版（UVA＋BDRC OCR＋ACIP＋Adarsha 併校，
2012–2018 Esukhia 校讀）。103 個 XML，一冊一檔。解壓到本機快取
`C:/tmp/derge/`（可重下，不進 git 不進 Drive）。

⚠ 站上另有一層 84000 的藏文對照（`scripts/tripitaka_tibetan.py`，3 部，
  來源是 84000 的 TMX 翻譯記憶）。**那是另一層，本檔不碰它**：
  那邊是「藏文掛到漢譯品上」的對照層，這邊是德格版全帙的獨立藏經層。

────────────────────────────────────────────────────────────────
標記結構（實測，非推測）
────────────────────────────────────────────────────────────────
    <tei:p n="2" data-orig-n="1b">          一個**葉面**（1a／1b ＝正背面）
      <tei:milestone unit="line" n="1"/>    葉面內的**行**
      <tei:milestone unit="text" toh="1"/>  **某一部經的起點**（切部的唯一依據）
      <tei:milestone unit="text" toh="1-1"/>  子編號＝該部底下的節，不是獨立的部
      ༄༅༅། །རྒྱ་གར་སྐད་དུ། …                正文
    </tei:p>

  `n` 是檔內流水號，`data-orig-n` 才是原書葉碼。冊號取 teiHeader 的
  `<tei:title>… [1]`。全帙：103 冊・65,983 葉面・460,539 行・
  1,208 個 text milestone（1,125 主編號＋75 子編號）・藏文字元 96,957,132。

段的定址＝**冊＋葉碼＋行**（藏學界慣例，例：`DKtoh0001_v1_1b1`）。
一段＝一行。藏文原典沒有標點分段，行是唯一的原書結構，也是引用式本身。
🚨 絕不自編流水號當段號（本 repo 硬規矩：假頁碼比沒有更糟）。

────────────────────────────────────────────────────────────────
🚨 六個會靜默做錯的地方（每一條都對應下面的程式碼）
────────────────────────────────────────────────────────────────
1. **一部經會跨冊。** milestone 只在起點出現一次，正文可延續好幾冊
   （般若部 Toh 8 橫跨十二冊）。26 冊完全沒有 milestone，整冊都是前一冊
   那部的續文。故解析必須是**跨冊的單一串流**，逐檔各自為政會讓長經
   只拿到第一冊那一截，而檔案看起來完全正常。→ `stream_volumes()`

2. **`toh="1-1"` 不是獨立的一部**，是 Toh 1 底下的節。照它切部會生出
   75 個假的「部」。只用**不含連字號**的 toh 切部；子編號記進 toc。
   → `parse_toh()` / `Builder.on_text_milestone()`

3. **帶字母的 Toh 是真的獨立條目**（7a・359a・460a・505a・539a–539h・
   673a・841a・842a・846a・1059a 共 17 個），不可當髒資料丟，
   `int()` 硬轉會爆。排序鍵一律 (數字, 字母)。→ `toh_key()`

4. **書名不在 TEI 裡。** `<tei:title>` 只有冊名（「འདུལ་བ་ཀ་བཞུགས་སོ།」＝
   律部第 KA 函），沒有逐部書名。書名要從每部正文開頭的梵藏對照題名句式
   抽：`རྒྱ་གར་སྐད་དུ།`（梵語云）…`བོད་སྐད་དུ།`（藏語云）…。
   🚨 抽不到就留空並在 `title_source` 標記，**絕不用冊名去填** ——
   那會讓一千多部裡一大半掛著同一個假書名而且看起來很正常。
   → `extract_title()`

5. **字數對帳閘。** 所有部的藏文字元加總 ＋ 冊題（每冊首葉 1a 的架上題）
   ＋ teiHeader ＝ 原檔總字元 96,957,132。對不上就不宣告完成。
   → `reconcile()`

6. 站上既有的 84000 藏文對照層（`tripitaka_tibetan.py`）**不動**，見上。

🚨 第七、第八個（實跑才現形，不在原清單裡；兩個都出在第 103 冊）：

7. **第 103 冊是目錄（dkar chag），它裡面的 milestone 是「目錄提到某部經」
   不是「某部經從這裡開始」。** 全帙 1,208 個 milestone 的 toh 值在文件
   順序上嚴格遞增，只有第 103 冊 147b 那 10 個例外（1108 → 538 → 539 →
   539a…539h，全擠在同一葉的兩行內）。照收的話目錄會被腰斬成九截，
   而 Toh 539h 會默默吞掉目錄後面四十幾葉 —— 每個檔案都看起來完全正常。
   故定規：**toh 值比當前作用中的部還小的 milestone ＝回溯提及**，
   在無 Toh 號的目錄裡則一律視為提及；記成 `mentions`，不切部、不換部、
   不靜默丟。→ `Builder.on_text_milestone()` 的 back-reference 分支
   （副作用：539g／539h 只在目錄裡被提到，全帙無正文，故部數是 1,123
    不是 1,125；`--audit` 會明列，不是漏抓。）

8. **目錄冊沒有自己的 milestone —— 它會被併進 Toh 1108。**
   最後一個 milestone 是第 102 冊 278a 的 Toh 1108，其後整整一冊目錄
   （469,657 字）都落在它名下。但 Toh 1108 是《三寶吉祥偈》
   （梵題 ratna-tri-svasti-gāthā，抽出來的題名可證），全帙最後一部短偈，
   自己只有九百多字。不處理的話：Toh 1108「很長」、目錄「不存在」，
   而兩邊都看不出異狀。故目錄獨立成一筆 `DKkarchag`，**不給 Toh 號**
   （這份 TEI 沒給它編號，不自編）。→ `NON_TOH_VOLUMES`

────────────────────────────────────────────────────────────────
用法
────────────────────────────────────────────────────────────────
    python scripts/tripitaka_derge.py --audit          # 全掃不寫檔，印對帳
    python scripts/tripitaka_derge.py --build          # 寫 JSONL＋toc＋catalog
    python scripts/tripitaka_derge.py --build --restart  # 不續跑，從頭來
    python scripts/tripitaka_derge.py --inspect 1      # 看某部（Toh 號）
    python scripts/tripitaka_derge.py --unzip          # 從 Drive 解壓來源

--build 可中斷續跑（這台筆電會通勤休眠）：每寫完一部就把
「下一部從哪一冊哪一個葉面開始」記進 `C:/tmp/derge/_state.json`，
重跑時跳回該點續寫。檢查點一律落在**部與部的交界**，所以不會有寫到一半
的半截檔。
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

_ENV_PATH = SCRIPT_DIR.parent / ".env"
if _ENV_PATH.exists():
    for _l in _ENV_PATH.read_text(encoding="utf-8").splitlines():
        if "=" in _l and not _l.strip().startswith("#"):
            _k, _v = _l.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

TEI = "http://www.tei-c.org/ns/1.0"

CANON = "DK"           # Derge Kangyur。與 CBETA 已用的代號全數不衝突
CANON_LABEL = "德格版甘珠爾"

# 來源 zip（Drive 正本）與本機解壓快取（可重下，不進 git 不進 Drive）
SRC_ZIP = Path(os.environ.get(
    "DERGE_KANGYUR_ZIP",
    "G:/我的雲端硬碟/資料/知識圖工作室/_corpus/tibetan-canon/src/"
    "derge-kangyur-UT4CZ5369-200106.zip"))
XML_ROOT = Path(os.environ.get("DERGE_XML_DIR", "C:/tmp/derge")) / "UT4CZ5369-200106"
STATE_PATH = Path(os.environ.get("DERGE_XML_DIR", "C:/tmp/derge")) / "_state.json"

# 產出落地處：Drive `_tripitaka_tibetan/`。
# ⚠ 刻意與既有的 `_tripitaka/`（CBETA 漢文層）分開，不混在一起。
OUT_DIR = Path(os.environ.get(
    "TRIPITAKA_TIBETAN_DIR",
    "G:/我的雲端硬碟/資料/知識圖工作室/_tripitaka_tibetan"))

# 原檔藏文字元總數（實測 2026-09-15，含 teiHeader 的 2,674）。對帳閘的分母。
RAW_TIBETAN_CHARS = 96_957_132
VOL_COUNT = 103

TIB_CHAR = re.compile(r"[\u0f00-\u0fff]")


# ─────────────────────────────────────────────────────────────
# 部類（德格版甘珠爾的分部）
#
# 🚨 不從冊題硬抽：冊題的部類名有異體（ཕལ་པོ་ཆེ／ཕལ་ཆེན、
#    དཀོན་བརྩེགས／དཀོན་བརྩེཊ），第 103 冊的冊題還是壞的
#    （'བཔཱུརཱུཔཾམདྷྱེདྭིགཎཛལ་ནིདྷྱབྲྀཏརུཙིཾ'，OCR 殘留）。
#    改用冊號區間 —— 區間本身由實掃 103 冊冊題定出，
#    `--audit` 會把每一部類的冊題列出來供人工核對（`_report_divisions`）。
# 一部的部類 ＝ 它**起始冊**的部類。
# ─────────────────────────────────────────────────────────────
DERGE_DIVISIONS: list[tuple[str, str, str, int, int]] = [
    # key,            繁中,       藏文,              起冊, 迄冊
    ("dk-dulwa",     "律部",     "འདུལ་བ",           1,   13),
    ("dk-sherphyin", "般若部",   "ཤེར་ཕྱིན",         14,  34),
    ("dk-phalchen",  "華嚴部",   "ཕལ་ཆེན",           35,  38),
    ("dk-konzek",    "寶積部",   "དཀོན་བརྩེགས",      39,  44),
    ("dk-dode",      "經部",     "མདོ་སྡེ",           45,  76),
    ("dk-gyu",       "續部",     "རྒྱུད་འབུམ",        77,  96),
    ("dk-nyinggyu",  "舊譯續部", "རྙིང་རྒྱུད",        97,  99),
    ("dk-dukhor",    "時輪釋",   "དུས་འཁོར་འགྲེལ་བཤད", 100, 100),
    ("dk-zungdu",    "陀羅尼集", "གཟུངས་འདུས",        101, 102),
    ("dk-karchag",   "目錄",     "དཀར་ཆག",           103, 103),
]


# 🚨 第 103 冊（dkar chag ＝德格版甘珠爾的目錄，司徒·卻吉迥乃編）在這份 TEI 裡
#   **沒有自己的 text milestone**，前一個 milestone 是第 102 冊 278a 的 Toh 1108。
#   照「milestone 到下一個 milestone」切，整整一冊目錄（469,699 字）會被併進
#   Toh 1108 —— 而 Toh 1108 是《三寶吉祥偈》（梵題 རཏྣ་ཏྲི་སྭ་སྟི་གཱ་ཐཱ ＝
#   ratna-tri-svasti-gāthā），全帙最後一部短偈，自己只有 884 字。
#   兩邊的檔案都會看起來完全正常：Toh 1108 「很長」，目錄「不存在」。
#   故目錄冊獨立成一筆、且**不給 Toh 號**（這份 TEI 沒給它編號，不自編）。
NON_TOH_VOLUMES: dict[int, tuple[str, str]] = {
    103: (f"{CANON}karchag", "德格版甘珠爾目錄（dkar chag）"),
}


def division_of(vol: int) -> str:
    for key, _, _, lo, hi in DERGE_DIVISIONS:
        if lo <= vol <= hi:
            return key
    raise ValueError(f"冊號 {vol} 不在任何部類區間內")


DIVISION_LABEL = {k: zh for k, zh, _, _, _ in DERGE_DIVISIONS}
DIVISION_BO = {k: bo for k, _, bo, _, _ in DERGE_DIVISIONS}


# ─────────────────────────────────────────────────────────────
# Toh 編號
# ─────────────────────────────────────────────────────────────
_TOH_RE = re.compile(r"^(\d+)([a-z]*)$")


def parse_toh(raw: str) -> tuple[str, str | None]:
    """milestone 的 toh 值 → (主編號, 子編號 or None)。

    '1'    → ('1', None)
    '1-7'  → ('1', '1-7')      子編號不是獨立的部（踩坑 2）
    '539a' → ('539a', None)    帶字母是真的獨立條目（踩坑 3）
    """
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("空的 toh")
    if "-" in raw:
        return raw.split("-", 1)[0], raw
    return raw, None


def toh_key(toh: str) -> tuple[int, str]:
    """排序／比大小用。🚨 int(toh) 會在 '539a' 上直接炸（踩坑 3）。"""
    m = _TOH_RE.match(toh)
    if not m:
        raise ValueError(f"看不懂的 Toh 號：{toh!r}")
    return int(m.group(1)), m.group(2)


def work_id(toh: str) -> str:
    """Toh 號 → 作品 id。`1` → `DKtoh0001`；`539a` → `DKtoh0539a`。"""
    no, sfx = toh_key(toh)
    return f"{CANON}toh{no:04d}{sfx}"


def sort_key(meta: dict) -> tuple:
    """排序鍵。沒有 Toh 號的（目錄冊）一律排在最後。"""
    if not meta.get("toh"):
        return (10 ** 6, "", meta["id"])
    no, sfx = toh_key(meta["toh"])
    return (no, sfx, meta["id"])


def _merge_kept(fresh: dict, old: dict | None) -> dict:
    """本次解析的欄位為準，舊目錄裡「別的腳本併進來的」欄位原樣留著。

    見 Builder.PARSED_FIELDS 的註解：不這樣做，`--catalog-only` 會把
    84000 的梵／英題名與東北目錄的漢譯對照整批洗成沒有，而輸出看起來正常。
    """
    out = {k: fresh[k] for k in Builder.PARSED_FIELDS}
    for k, v in (old or {}).items():
        if k not in Builder.PARSED_FIELDS:
            out[k] = v
    for k, v in fresh.items():          # 舊目錄沒有的，用本次的預設值補上
        out.setdefault(k, v)
    return out


def seg_id(wid: str, vol: int, folio: str, line: int) -> str:
    """段的定址＝冊＋葉碼＋行（藏學界慣例）。例 `DKtoh0001_v1_1b1`。

    🚨 葉碼原樣保留，不轉數字：全帙有 8 個「重出葉」（33xa／33xb／
    93xa／93xb／354xa/b／355xa/b），`int()` 會爆，重編會造出假葉碼。
    """
    return f"{wid}_v{vol}_{folio}{line}"


# ─────────────────────────────────────────────────────────────
# 文字
# ─────────────────────────────────────────────────────────────
def clean(s: str) -> str:
    return re.sub(r"[ \t\r\n\u00a0]+", " ", s or "").strip()


def tib_len(s: str) -> int:
    """只數藏文字元（U+0F00–U+0FFF）。對帳閘的口徑，與原檔同一把尺。"""
    return len(TIB_CHAR.findall(s or ""))


# ─────────────────────────────────────────────────────────────
# 書名（踩坑 4）
#
# 每部正文開頭的梵藏對照題名句式：
#   ༄༅༅། །རྒྱ་གར་སྐད་དུ། བི་ན་ཡ་བསྟུ། བོད་སྐད་དུ། འདུལ་བ་གཞི། བམ་པོ་དང་པོ། …
#            └─ 梵語云 ─┘ └ 梵文題名 ┘ └─ 藏語云 ─┘ └ 藏文題名 ┘
# 譯自漢文／于闐文的經另作 རྒྱ་ནག་སྐད་དུ།／ལི་ཡུལ་སྐད་དུ།，故來源語不寫死。
# ─────────────────────────────────────────────────────────────
SHAD = "།༎༏༐༑"
_BOD_MARK = re.compile(r"བོད་སྐད་དུ")
_SRC_MARK = re.compile(r"([\u0f40-\u0fbc\u0f71-\u0f84་]{2,24}?)སྐད་དུ")
_STRIP_HEAD = re.compile(r"^[\u0f01-\u0f14\s" + SHAD + r"]+")

# 題名標記：藏文書名幾乎都以這些詞收尾（「…之經」「…陀羅尼」「…儀軌」…）。
# 退路取題名時，沒有任一標記就留空 —— 寧可留空，也不要拿一句禮敬文當書名。
_TITLE_MARKERS = ("ཞེས་བྱ་བ", "མདོ", "གཟུངས", "རྒྱུད", "ལེའུ", "སྙིང་པོ",
                  "བསྟན་པ", "ཆོས་ཀྱི་རྣམ་གྲངས", "འཕགས་པ", "རྟོག་པ",
                  "སྒྲུབ་ཐབས", "ཆོ་ག", "བསྟོད་པ", "རྒྱལ་པོ", "ཕན་ཡོན")
# 這些是卷次語／架上題，整段出現就不是書名
_TITLE_REJECT = ("བམ་པོ", "བཞུགས་སོ")
# 🚨 禮敬文「…ལ་ཕྱག་འཚལ་ལོ」常常**和書名連寫、中間沒有 shad**：
#     བོད་སྐད་དུ། དཔལ་ཡེ་ཤེས་འབར་བའི་རྒྱུད་ཀྱི་རྒྱལ་པོ་|དཔལ་ཀུན་ཏུ་བཟང་པོ་ལ་ཕྱག་འཚལ་ལོ།
#   一律排除含「ཕྱག་འཚལ」者會把這一大批書名整批丟掉（實測 186 部留空裡佔一半），
#   但照收又會把禮敬文接在書名後面。故：只有**結尾**是禮敬文時才切，
#   切在禮敬文之前最後一個題名標記上；找不到標記就留空，不硬猜。
#   ⚠ 反例：《二十一度母禮讚》的書名本身就有「ཕྱག་འཚལ」
#     （སྒྲོལ་མ་ལ་ཕྱག་འཚལ་ཉི་ཤུ་རྩ་གཅིག་གིས་བསྟོད་པ…），所以不能看「含不含」。
_HOMAGE_TAIL = re.compile(r"ལ་ཕྱག་འཚལ་(?:ལོ|བ)?[ོ་]*$")
_HOMAGE_ANY = re.compile(r"ལ་ཕྱག་འཚལ་(?:ལོ|བ)")
# 卷尾題：「…ཞེས་བྱ་བའི་གཟུངས་རྫོགས་སོ།」。短的陀羅尼開頭多半只有禮敬文，
# 書名只出現在卷尾，故加這第三個取法（title_source='colophon'，來源分得開）。
_COLOPHON = re.compile(r"(?:རྫོགས་ས[྄ོ]*|རྫོགསོ)")
# 卷尾題後面跟的是譯師題記，那不是書名
_COLOPHON_REJECT = ("བསྒྱུར", "ལོ་ཙཱ", "ལོ་ཙྪ", "མཁན་པོ", "ཞུས་ཏེ", "གཏན་ལ་ཕབ")


def _first_unit(s: str) -> str:
    """取到第一個 shad 為止。"""
    for i, ch in enumerate(s):
        if ch in SHAD:
            return s[:i]
    return s


def _strip_homage_tail(title: str) -> str:
    """書名尾巴黏著禮敬文時，切在禮敬文之前最後一個題名標記上。切不掉就回空字串。"""
    if not _HOMAGE_TAIL.search(title):
        return title
    m = _HOMAGE_ANY.search(title)
    cut = m.start() if m else len(title)
    best = -1
    for k in _TITLE_MARKERS:
        i = title.rfind(k, 0, cut)
        if i >= 0:
            best = max(best, i + len(k))
    return title[:best].strip("་ ") if best > 0 else ""


def extract_title(head_text: str, tail_text: str = "") -> dict:
    """一部經的開頭（與卷尾）→ 書名。

    🚨 抽不到就留空並在 title_source 標記，**絕不用冊名去填**（檔頭踩坑 4）。
    三個取法，來源逐部記錄，不混為一談：
      bilingual-formula  正文開頭的梵藏對照題名句式（最可靠）
      opening-title      開頭直接就是藏文題名（無對照句式）
      colophon           卷尾題「…ཞེས་བྱ་བ…རྫོགས་སོ།」（短陀羅尼多屬此類）
    """
    out = {"title_bo": "", "title_src": "", "src_lang": "", "title_source": ""}
    head = (head_text or "")[:900]

    m = _BOD_MARK.search(head)
    if m:
        tail = head[m.end():].lstrip(SHAD + " ་")
        title = _strip_homage_tail(clean(_first_unit(tail)).strip("་ "))
        if title and not any(b in title for b in _TITLE_REJECT):
            out["title_bo"] = title
            out["title_source"] = "bilingual-formula"
            # 來源語題名：往前找最後一個 「…སྐད་དུ」
            prev = None
            for sm in _SRC_MARK.finditer(head[:m.start()]):
                prev = sm
            if prev is not None:
                out["src_lang"] = clean(prev.group(1)).strip("་ ")
                src = head[prev.end():m.start()].lstrip(SHAD + " ་")
                out["title_src"] = clean(src).strip(SHAD + " ་")
            return out

    # 退路一：開頭直接就是藏文題名（品／章單獨成部者多屬此類）
    cand = _strip_homage_tail(
        clean(_first_unit(_STRIP_HEAD.sub("", head))).strip("་ "))
    if (6 <= len(cand) <= 160
            and any(k in cand for k in _TITLE_MARKERS)
            and not any(b in cand for b in _TITLE_REJECT)):
        out["title_bo"] = cand
        out["title_source"] = "opening-title"
        return out

    # 退路二：卷尾題
    t = (tail_text or "")[-900:]
    mc = None
    for x in _COLOPHON.finditer(t):
        mc = x
    if mc:
        seg = t[:mc.start()]
        cut = max((seg.rfind(ch) for ch in SHAD), default=-1)
        cand2 = clean(seg[cut + 1:]).strip("་ ")
        if (6 <= len(cand2) <= 160
                and any(k in cand2 for k in _TITLE_MARKERS)
                and not any(b in cand2 for b in _TITLE_REJECT)
                and not any(b in cand2 for b in _COLOPHON_REJECT)):
            out["title_bo"] = cand2
            out["title_source"] = "colophon"
    return out


# ─────────────────────────────────────────────────────────────
# 逐冊串流（踩坑 1：跨冊必須是單一串流）
# ─────────────────────────────────────────────────────────────
def volume_files() -> list[tuple[int, Path]]:
    """→ [(冊號, 路徑)]，**按冊號排序**。

    目錄名（UT4CZ5369-I1KG9127…9229）剛好也是遞增的，但冊號以
    teiHeader `<title>… [n]` 為準，不靠檔名推。
    """
    out = []
    for p in sorted(XML_ROOT.glob("*/*.xml")):
        head = p.read_text(encoding="utf-8")[:2000]
        m = re.search(r"<tei:title>(.*?)</tei:title>", head, re.S)
        title = clean(m.group(1)) if m else ""
        mv = re.search(r"\[(\d+)\]", title)
        if not mv:
            raise ValueError(f"{p.name} 的冊題沒有 [n] 冊號：{title!r}")
        out.append((int(mv.group(1)), p, title))
    out.sort(key=lambda x: x[0])
    vols = [v for v, _, _ in out]
    if vols != list(range(1, len(vols) + 1)):
        raise ValueError(f"冊號不連續：{vols}")
    return out


class Piece:
    """一行（或一行被 milestone 切開後的一截）的正文。"""
    __slots__ = ("vol", "folio", "line", "text")

    def __init__(self, vol: int, folio: str, line: int, text: str):
        self.vol, self.folio, self.line, self.text = vol, folio, line, text


def iter_page_pieces(p: ET.Element, vol: int):
    """一個葉面 → 依文件順序 yield ('text', Piece) / ('toh', (raw, line))。

    milestone 可以出現在**行中**（一部經從某行的中間開始），所以文字要
    照子節點順序逐段收，不能整葉 itertext() 之後再切。
    🚨 toh 事件必須自己帶行號：text milestone 常常緊跟在 line milestone
       後面、中間一個字都沒有，靠「最後一筆正文的行號」回推會拿到**上一行**。
    """
    folio = p.get("data-orig-n") or p.get("n") or ""
    line = 0
    buf: list[str] = []

    def flush():
        nonlocal buf
        if not buf:
            return None
        t = clean("".join(buf))
        buf = []
        return Piece(vol, folio, line, t) if t else None

    if p.text:
        buf.append(p.text)
    for c in p:
        tag = c.tag.split("}")[-1]
        if tag == "milestone":
            unit = c.get("unit")
            if unit == "line":
                pc = flush()
                if pc is not None:
                    yield ("text", pc)
                try:
                    line = int(c.get("n") or 0)
                except ValueError:
                    line = 0
            elif unit == "text":
                pc = flush()
                if pc is not None:
                    yield ("text", pc)
                yield ("toh", (c.get("toh") or "", line))
            else:
                yield ("unknown", f"milestone unit={unit}")
        elif tag in ("lb", "pb"):
            pass
        else:
            # 沒預期的標籤 —— 不靜默吞掉，往上報
            yield ("unknown", tag)
            if c.text:
                buf.append(c.text)
        if c.tail:
            buf.append(c.tail)
    pc = flush()
    if pc is not None:
        yield ("text", pc)


def stream_volumes(start_vol: int = 1, start_p: int = 0):
    """跨冊單一串流。yield 事件：

        ('vol', 冊號, 冊題, 葉面數)
        ('front', Piece)          每冊首葉 1a 的架上冊題（不屬於任何一部）
        ('page', 冊號, 葉碼)
        ('blank', 冊號, 葉碼)     印本的空白葉（無正文、無行 milestone）
        ('toh', raw, vol, folio, line, p_index)
        ('text', Piece)
        ('odd', 說明)

    🚨 每冊首葉（p n="1" data-orig-n="1a"）是**架上冊題**（「律部第 KA 函」），
       不是任何一部經的正文。實掃 103 冊全部符合：都是 1a、都沒有 milestone、
       都 ≤60 字。不符合的會報 'odd' 而不是靜默併進正文。
    """
    for vol, path, vtitle in volume_files():
        if vol < start_vol:
            continue
        root = ET.parse(str(path)).getroot()
        body = root.find(f".//{{{TEI}}}body")
        if body is None:
            yield ("odd", f"冊{vol} 沒有 body")
            continue
        pages = body.findall(f".//{{{TEI}}}p")
        yield ("vol", vol, vtitle, len(pages))
        for pi, p in enumerate(pages):
            if vol == start_vol and pi < start_p:
                continue
            folio = p.get("data-orig-n") or ""
            if pi == 0:
                ms = [c for c in p if c.tag.split("}")[-1] == "milestone"]
                raw = clean("".join(p.itertext()))
                if folio != "1a" or ms:
                    yield ("odd", f"冊{vol} 首葉不是乾淨的冊題頁："
                                  f"葉={folio} milestone={len(ms)}")
                yield ("front", Piece(vol, folio, 0, raw))
                continue
            yield ("page", vol, folio)
            line_seen = False
            for kind, val in iter_page_pieces(p, vol):
                if kind == "toh":
                    raw_toh, line = val
                    yield ("toh", raw_toh, vol, folio, line, pi)
                elif kind == "text":
                    line_seen = line_seen or val.line > 0
                    yield ("text", val)
                else:
                    yield ("odd", f"冊{vol} 葉{folio} 未預期的節點：{val}")
            if not line_seen:
                # 全帙有 24 個這樣的葉面，實測**全部是空白葉**（印本的空頁，
                # 藏文字元 0）。沒有正文就沒有段，也就不會生出 line=0 的假行號。
                # 有字卻沒有行 milestone 才是真的問題，那時才報。
                raw = clean("".join(p.itertext()))
                if tib_len(raw):
                    yield ("odd", f"冊{vol} 葉{folio} 有正文 {tib_len(raw)} 字"
                                  "卻沒有行 milestone —— 行號會變成 0（假行號）")
                else:
                    yield ("blank", vol, folio)


# ─────────────────────────────────────────────────────────────
# 建置
# ─────────────────────────────────────────────────────────────
class Work:
    def __init__(self, toh: str | None, vol: int, folio: str, line: int,
                 division: str, wid: str | None = None, label: str = ""):
        self.toh = toh                       # None ＝這份 TEI 沒給它 Toh 號
        self.id = wid or work_id(toh)
        self.label = label
        self.division = division
        self.segs: list[dict] = []
        self.toc: list[dict] = []
        self.spans: list[dict] = []
        self.vols: list[int] = []
        self.mentions: list[dict] = []
        self.cur_sub = -1          # 目前所在的子編號在 toc 中的索引
        self.chars = 0
        self.line_use: dict[str, int] = {}
        self.head_buf: list[str] = []      # 開頭 900 字，供抽書名
        self.tail_buf: list[str] = []      # 結尾 900 字，供抽卷尾題
        self.open_span(vol, folio, line)

    def open_span(self, vol: int, folio: str, line: int):
        self.spans.append({"vol": vol, "folio_start": folio, "line_start": line,
                           "folio_end": folio, "line_end": line, "chars": 0})

    def add(self, pc: Piece):
        n = tib_len(pc.text)
        if not n:
            return
        if not self.spans:
            self.open_span(pc.vol, pc.folio, pc.line)
        sp = self.spans[-1]
        if sp["vol"] != pc.vol:
            # 跨冊：同一部經延續到下一冊，開新的 span（踩坑 1）
            self.spans.append({"vol": pc.vol, "folio_start": pc.folio,
                               "line_start": pc.line, "folio_end": pc.folio,
                               "line_end": pc.line, "chars": 0})
            sp = self.spans[-1]
        sp["folio_end"], sp["line_end"] = pc.folio, pc.line
        sp["chars"] += n
        if pc.vol not in self.vols:
            self.vols.append(pc.vol)
        self.chars += n
        key = seg_id(self.id, pc.vol, pc.folio, pc.line)
        # 同一「冊＋葉＋行」理論上一部經只會出現一次；萬一被子編號切成兩截，
        # 比照 CBETA 那邊的規矩：seg 是引用式（可重複），uid 加 .2 才是鍵。
        seen = self.line_use[key] = self.line_use.get(key, 0) + 1
        uid = key if seen == 1 else f"{key}.{seen}"
        self.segs.append({
            "i": len(self.segs) + 1,
            "uid": uid,
            "seg": key,
            "vol": pc.vol,
            "folio": pc.folio,
            "line": pc.line,
            "d": self.cur_sub,
            "kind": "line",
            "sources": {"bo": pc.text},
        })
        if sum(len(x) for x in self.head_buf) < 900:
            self.head_buf.append(pc.text)
        self.tail_buf.append(pc.text)
        while len(self.tail_buf) > 2 and sum(len(x) for x in self.tail_buf[1:]) >= 900:
            self.tail_buf.pop(0)

    def add_sub(self, raw: str, vol: int, folio: str, line: int):
        self.toc.append({
            "i": len(self.toc), "depth": 0, "type": "sub",
            "head": "", "n": raw, "parent": -1,
            "uid": seg_id(self.id, vol, folio, line),
            "vol": vol, "folio": folio, "line": line,
        })
        self.cur_sub = len(self.toc) - 1

    def meta(self) -> dict:
        title = extract_title("".join(self.head_buf), "".join(self.tail_buf))
        no, sfx = toh_key(self.toh) if self.toh else (None, "")
        return {
            "id": self.id,
            "canon": CANON,
            "canon_label": CANON_LABEL,
            "toh": self.toh,
            "toh_no": no,
            "toh_suffix": sfx,
            "label_zh": self.label,
            "vol": self.vols[0] if self.vols else None,
            "vols": self.vols,
            "cross_volume": len(self.vols) > 1,
            "title_bo": title["title_bo"],
            "title_src": title["title_src"],
            "src_lang": title["src_lang"],
            "title_source": title["title_source"],
            "title_zh": "",          # 漢譯書名另立一層，本輪不做，留空不臆造
            "division_key": self.division,
            "division_label": DIVISION_LABEL[self.division],
            "division_bo": DIVISION_BO[self.division],
            "folio_start": self.spans[0]["folio_start"] if self.spans else "",
            "folio_end": self.spans[-1]["folio_end"] if self.spans else "",
            "spans": self.spans,
            "sub_count": len(self.toc),
            "subs": [t["n"] for t in self.toc],
            "mentions": self.mentions,
            "seg_count": len(self.segs),
            "char_count": self.chars,
            "toc_count": len(self.toc),
            "source": "Esukhia/derge-kangyur TEI (UT4CZ5369-200106)",
        }


class Builder:
    def __init__(self, write: bool):
        self.write = write
        self.cur: Work | None = None
        self.works: list[dict] = []          # 已完成的 meta
        self.front_chars = 0
        self.front_pages = 0
        self.odd: list[str] = []
        self.backrefs: list[dict] = []
        self.orphan_chars = 0                # 沒有作用中的部時出現的正文
        self.toh_seen: list[str] = []
        self.max_key: tuple[int, str] | None = None
        self.sub_parent_mismatch: list[str] = []
        self.pages = 0
        self.blank_pages = 0
        self.lines = 0
        self.vol_titles: dict[int, str] = {}
        self.resume_point: tuple[int, int] | None = None
        self.written = 0
        # 續跑時，檢查點那一葉會從頭重讀一次；milestone 之前的那截正文屬於
        # 上一部（已寫出、字數已記在 state 裡），要丟掉且**不可**算成無主正文
        self.resuming = False

    # ── milestone ────────────────────────────────────────────
    def on_text_milestone(self, raw: str, vol: int, folio: str, line: int,
                          p_index: int):
        main, sub = parse_toh(raw)
        k = toh_key(main)
        self.toh_seen.append(raw)
        self.resuming = False

        # 🚨 回溯提及：toh 值比當前作用中的部還小 ＝ 目錄冊在「提到」那部經，
        #    不是那部經從這裡開始（第 103 冊 dkar chag，見檔頭踩坑七）。
        #    不切部、不換部，記成 cross-reference。
        #    在目錄本身（無 Toh 號的那一筆）裡，**任何** milestone 都是提及。
        if self.cur is not None and (self.cur.toh is None
                                     or k < toh_key(self.cur.toh)):
            ref = {"toh": raw, "vol": vol, "folio": folio, "line": line,
                   "in_work": self.cur.toh}
            self.cur.mentions.append(ref)
            self.backrefs.append(ref)
            return

        if sub:
            # 子編號：不是獨立的部（踩坑 2）
            if self.cur is None or self.cur.toh is None or self.cur.toh != main:
                # 子編號的母部還沒出現過 —— 當成該部的起點，但要報出來
                self.sub_parent_mismatch.append(
                    f"{raw} 出現時作用中的部是 "
                    f"{self.cur.toh if self.cur else 'None'}")
                self._start(main, vol, folio, line, p_index)
            self.cur.add_sub(raw, vol, folio, line)
            return

        if self.cur is not None and self.cur.toh == main:
            # 同一部的 milestone 又出現（不倒退）＝ 續標，不另起
            return
        self._start(main, vol, folio, line, p_index)

    def _start(self, main: str, vol: int, folio: str, line: int, p_index: int):
        # ⚠ 順序要緊：先把檢查點移到「新的這一部的起點」，再寫出上一部。
        #   反過來的話 state 記的會是剛寫完那一部的起點，續跑時它會被重做一次
        #   並在 works 裡出現第二筆 —— 目錄會多出一部而檔案完全正常。
        self.resume_point = (vol, p_index)
        self._flush()
        self.cur = Work(main, vol, folio, line, division_of(vol))
        self.max_key = max(self.max_key, toh_key(main)) if self.max_key else toh_key(main)
        if self.write and len(self.works) % 20 == 0:
            self._save_state()

    def start_non_toh(self, vol: int):
        """目錄冊這種「有正文但這份 TEI 沒給 Toh 號」的，在冊界處獨立成一筆。"""
        wid, label = NON_TOH_VOLUMES[vol]
        self.resume_point = (vol, 0)
        self._flush()
        self.cur = Work(None, vol, "1a", 0, division_of(vol), wid=wid, label=label)
        # 冊首葉（架上題）不進正文，故起點等第一個有字的葉面到來時才會定下來
        self.cur.spans.clear()
        self.cur.vols.clear()

    # ── 正文 ─────────────────────────────────────────────────
    def on_text(self, pc: Piece):
        self.lines += 1
        if self.cur is None:
            if self.resuming:
                return       # 檢查點那一葉重讀到的上一部尾巴，已計過帳
            self.orphan_chars += tib_len(pc.text)
            if tib_len(pc.text):
                self.odd.append(f"冊{pc.vol} 葉{pc.folio} 行{pc.line}"
                                f" 在任何 milestone 之前就有正文（{tib_len(pc.text)} 字）")
            return
        self.cur.add(pc)

    def on_front(self, pc: Piece):
        self.front_pages += 1
        self.front_chars += tib_len(pc.text)

    # ── 落地 ─────────────────────────────────────────────────
    def _flush(self):
        if self.cur is None:
            return
        w, self.cur = self.cur, None
        meta = w.meta()
        self.works.append(meta)
        if self.write:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            tmp = OUT_DIR / f"{meta['id']}.jsonl.tmp"
            with tmp.open("w", encoding="utf-8") as f:
                for s in w.segs:
                    f.write(json.dumps(s, ensure_ascii=False) + "\n")
            tmp.replace(OUT_DIR / f"{meta['id']}.jsonl")
            tmp2 = OUT_DIR / f"{meta['id']}.toc.json.tmp"
            tmp2.write_text(json.dumps({"meta": meta, "toc": w.toc},
                                       ensure_ascii=False), encoding="utf-8")
            tmp2.replace(OUT_DIR / f"{meta['id']}.toc.json")
            self.written += 1

    def _save_state(self):
        if not self.write or self.resume_point is None:
            return
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps({
            "next_vol": self.resume_point[0],
            "next_p": self.resume_point[1],
            "works": self.works,
            "front_pages": self.front_pages,
            "front_chars": self.front_chars,
            "pages": self.pages,
            "blank_pages": self.blank_pages,
            "lines": self.lines,
            "backrefs": self.backrefs,
            "odd": self.odd[:200],
            "toh_seen": self.toh_seen,
            "vol_titles": {str(k): v for k, v in self.vol_titles.items()},
            "sub_parent_mismatch": self.sub_parent_mismatch,
        }, ensure_ascii=False), encoding="utf-8")

    def load_state(self) -> tuple[int, int]:
        if not STATE_PATH.exists():
            return 1, 0
        st = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        self.works = st.get("works", [])
        self.front_pages = st.get("front_pages", 0)
        self.front_chars = st.get("front_chars", 0)
        self.pages = st.get("pages", 0)
        self.blank_pages = st.get("blank_pages", 0)
        self.lines = st.get("lines", 0)
        self.backrefs = st.get("backrefs", [])
        self.odd = st.get("odd", [])
        self.toh_seen = st.get("toh_seen", [])
        self.vol_titles = {int(k): v for k, v in st.get("vol_titles", {}).items()}
        self.sub_parent_mismatch = st.get("sub_parent_mismatch", [])
        if self.works:
            self.max_key = max((toh_key(w["toh"]) for w in self.works
                                if w["toh"]), default=None)
        return st.get("next_vol", 1), st.get("next_p", 0)

    # ── 主迴圈 ───────────────────────────────────────────────
    def run(self, start_vol: int = 1, start_p: int = 0, quiet: bool = False):
        self.resuming = start_vol > 1 or start_p > 0
        for ev in stream_volumes(start_vol, start_p):
            tag = ev[0]
            if tag == "vol":
                _, vol, vtitle, npages = ev
                self.vol_titles[vol] = vtitle
                if not quiet:
                    print(f"  冊 {vol:>3}/{VOL_COUNT}  {npages} 葉  "
                          f"{vtitle[:34]}", flush=True)
                if vol in NON_TOH_VOLUMES:
                    self.start_non_toh(vol)
            elif tag == "page":
                self.pages += 1
            elif tag == "blank":
                self.blank_pages += 1
            elif tag == "front":
                self.pages += 1
                self.on_front(ev[1])
            elif tag == "toh":
                self.on_text_milestone(ev[1], ev[2], ev[3], ev[4], ev[5])
            elif tag == "text":
                self.on_text(ev[1])
            elif tag == "odd":
                self.odd.append(ev[1])
        self._flush()
        if self.write:
            self._write_catalog()

    # 本檔重跑就算得回來的欄位。這些以本次解析為準，舊值不留。
    PARSED_FIELDS = (
        "id", "toh", "toh_no", "toh_suffix", "label_zh", "vol", "vols",
        "cross_volume", "title_bo", "title_src", "src_lang", "title_source",
        "division_key", "division_label", "folio_start",
        "folio_end", "sub_count", "seg_count", "char_count")
    # title_zh 不在上面：本檔只會把它寫成空字串，真正的值是
    # tripitaka_derge_zh.py 從東北目錄併進來的，重跑算不回來。

    def _write_catalog(self):
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        rows = sorted(self.works, key=sort_key)
        # 🚨 下面的 works 是「本次解析算得出來的欄位」白名單。後面還有別的腳本
        #    往同一份目錄裡併東西——tripitaka_derge_titles.py 補 title_sa／
        #    title_en／translator_en／title_bo_short（84000），
        #    tripitaka_derge_zh.py 補 title_zh／zh_parallels／title_zh_source
        #    （東北目錄）。那些欄位重跑本檔是算不回來的，白名單一濾就沒了，
        #    而且目錄照樣完整、部數照樣 1,124，從輸出上完全看不出來。
        #    所以重出前先把舊目錄讀進來，非本次產出的欄位一律原樣帶回去。
        keep: dict[str, dict] = {}
        old = OUT_DIR / f"{CANON}.catalog.json"
        if old.exists():
            try:
                for m in json.loads(old.read_text(encoding="utf-8"))["works"]:
                    keep[m["id"]] = m
            except (ValueError, KeyError):
                pass
        cat = {
            "canon": CANON,
            "canon_label": CANON_LABEL,
            "source": "Esukhia/derge-kangyur TEI (UT4CZ5369-200106)",
            "volumes": [{"vol": v, "title_bo": t,
                         "division_key": division_of(v),
                         "division_label": DIVISION_LABEL[division_of(v)]}
                        for v, t in sorted(self.vol_titles.items())],
            "divisions": [{"key": k, "label": zh, "label_bo": bo,
                           "vol_from": lo, "vol_to": hi,
                           "work_count": sum(1 for r in rows
                                             if r["division_key"] == k)}
                          for k, zh, bo, lo, hi in DERGE_DIVISIONS],
            "work_count": len(rows),
            "works": [_merge_kept(m, keep.get(m["id"])) for m in rows],
        }
        tmp = OUT_DIR / f"{CANON}.catalog.json.tmp"
        tmp.write_text(json.dumps(cat, ensure_ascii=False, indent=1),
                       encoding="utf-8")
        tmp.replace(OUT_DIR / f"{CANON}.catalog.json")


# ─────────────────────────────────────────────────────────────
# 對帳（踩坑 5）
# ─────────────────────────────────────────────────────────────
def header_chars() -> int:
    """103 個 teiHeader 的藏文字元（冊題也在裡面）。"""
    tot = 0
    for _, p, _ in volume_files():
        root = ET.parse(str(p)).getroot()
        h = root.find(f".//{{{TEI}}}teiHeader")
        if h is not None:
            tot += tib_len("".join(h.itertext()))
    return tot


def reconcile(b: Builder) -> dict:
    works_chars = sum(w["char_count"] for w in b.works)
    hdr = header_chars()
    accounted = works_chars + b.front_chars + hdr + b.orphan_chars
    return {
        "works_chars": works_chars,
        "front_chars": b.front_chars,
        "front_pages": b.front_pages,
        "header_chars": hdr,
        "orphan_chars": b.orphan_chars,
        "accounted": accounted,
        "raw": RAW_TIBETAN_CHARS,
        "diff": RAW_TIBETAN_CHARS - accounted,
    }


def report(b: Builder):
    rows = sorted(b.works, key=sort_key)
    if not rows:
        print("❌ 一部都沒有解出來 —— 先跑 --inspect 看串流有沒有走到")
        return {"diff": -1}
    r = reconcile(b)
    nos = sorted({m["toh_no"] for m in rows if m["toh_no"] is not None})
    non_toh = [m for m in rows if m["toh"] is None]
    gaps = [n for n in range(nos[0], nos[-1] + 1) if n not in set(nos)] if nos else []
    lettered = [m["toh"] for m in rows if m["toh_suffix"]]
    cross = [m for m in rows if m["cross_volume"]]
    titled = [m for m in rows if m["title_bo"]]
    by_formula = [m for m in rows if m["title_source"] == "bilingual-formula"]
    by_opening = [m for m in rows if m["title_source"] == "opening-title"]
    by_colophon = [m for m in rows if m["title_source"] == "colophon"]
    empty = [m for m in rows if not m["title_bo"]]
    subs = sum(m["sub_count"] for m in rows)
    segs = sum(m["seg_count"] for m in rows)

    print("\n" + "═" * 64)
    print(f"  {CANON_LABEL}（{CANON}）對帳")
    print("═" * 64)
    print(f"  部數          {len(rows):>12,}"
          f"（Toh 主編號 {len(nos)} 個數字 ＋ {len(lettered)} 個帶字母"
          + (f" ＋ {len(non_toh)} 個無 Toh 號" if non_toh else "") + "）")
    for m in non_toh:
        print(f"    無 Toh 號：{m['id']}　{m['label_zh']}　冊 {m['vols']}"
              f"　{m['char_count']:,} 字（這份 TEI 沒給它編號，不自編）")
    print(f"  Toh 數字範圍  {nos[0]}–{nos[-1]}"
          f"　{'連續零斷號' if not gaps else f'斷號 {gaps[:20]}'}")
    print(f"  帶字母        {', '.join(lettered)}")
    print(f"  段數          {segs:>12,}（一段＝一行）")
    print(f"  節（子編號）  {subs:>12,}")
    print(f"  葉面          {b.pages:>12,}"
          f"（其中空白葉 {b.blank_pages}，印本原就是空頁）")
    print(f"  藏文字元      {r['works_chars']:>12,}")
    print("\n  ── 字數對帳 ──")
    print(f"    各部合計        {r['works_chars']:>12,}")
    print(f"    ＋冊題（{r['front_pages']} 冊首葉）{r['front_chars']:>8,}")
    print(f"    ＋teiHeader     {r['header_chars']:>12,}")
    if r["orphan_chars"]:
        print(f"    ＋無主正文      {r['orphan_chars']:>12,}  ⚠")
    print(f"    ＝              {r['accounted']:>12,}")
    print(f"    原檔總計        {r['raw']:>12,}")
    print(f"    差額            {r['diff']:>12,}"
          + ("  ✓ 完全對上" if r["diff"] == 0 else "  ❌ 對不上，不可宣告完成"))
    print("\n  ── 書名 ──")
    print(f"    有書名          {len(titled):>6}/{len(rows)}"
          f"  ({len(titled) / len(rows) * 100:.1f}%)")
    print(f"      梵藏對照句式  {len(by_formula):>6}"
          f"  ({len(by_formula) / len(rows) * 100:.1f}%)")
    print(f"      開頭即題名    {len(by_opening):>6}"
          f"  ({len(by_opening) / len(rows) * 100:.1f}%)")
    print(f"      卷尾題        {len(by_colophon):>6}"
          f"  ({len(by_colophon) / len(rows) * 100:.1f}%)")
    print(f"    留空（已標記）  {len(empty):>6}"
          f"  ({len(empty) / len(rows) * 100:.1f}%)  ← 未用冊名填充")
    print("\n  ── 跨冊 ──")
    print(f"    跨冊的部        {len(cross):>6} 部"
          f"（最長 {max((len(m['vols']) for m in cross), default=0)} 冊）")
    if cross:
        top = sorted(cross, key=lambda m: -len(m["vols"]))[:5]
        for m in top:
            print(f"      {m['id']}  冊 {m['vols'][0]}–{m['vols'][-1]}"
                  f"（{len(m['vols'])} 冊）{m['char_count']:>10,} 字"
                  f"  {m['title_bo'][:24]}")
    print("\n  ── 部類 ──")
    for k, zh, bo, lo, hi in DERGE_DIVISIONS:
        n = sum(1 for m in rows if m["division_key"] == k)
        c = sum(m["char_count"] for m in rows if m["division_key"] == k)
        print(f"    {zh:<5}{bo:<22} 冊{lo:>3}–{hi:<3} {n:>5} 部 {c:>12,} 字")
    if b.backrefs:
        print(f"\n  ── 回溯提及（不切部，記成 cross-reference）{len(b.backrefs)} 筆 ──")
        for x in b.backrefs[:12]:
            print(f"    冊{x['vol']} 葉{x['folio']} 行{x['line']}"
                  f"  提到 Toh {x['toh']}（正文屬 Toh {x['in_work']}）")
        only = sorted({x["toh"] for x in b.backrefs}
                      - {m["toh"] for m in rows}, key=toh_key)
        if only:
            print(f"    ⚠ 只在目錄冊被提到、全帙無正文的 Toh：{', '.join(only)}")
    if b.sub_parent_mismatch:
        print(f"\n  ⚠ 子編號的母部對不上 {len(b.sub_parent_mismatch)} 筆：")
        for x in b.sub_parent_mismatch[:10]:
            print("    " + x)
    if b.odd:
        print(f"\n  ⚠ 異常 {len(b.odd)} 筆（前 10）：")
        for x in b.odd[:10]:
            print("    " + x)
    else:
        print("\n  異常：無")
    print("═" * 64)
    return r


def _report_divisions(b: Builder):
    """把每一部類實際涵蓋的冊題列出來，供人工核對區間表有沒有寫錯。"""
    print("\n  部類區間 vs 實際冊題（人工核對用）")
    for k, zh, bo, lo, hi in DERGE_DIVISIONS:
        ts = [b.vol_titles.get(v, "") for v in range(lo, hi + 1)]
        print(f"    {zh}（冊{lo}–{hi}）")
        print(f"      首 {ts[0][:40]}")
        if len(ts) > 1:
            print(f"      末 {ts[-1][:40]}")


# ─────────────────────────────────────────────────────────────
# 指令
# ─────────────────────────────────────────────────────────────
def cmd_unzip():
    import zipfile
    dst = XML_ROOT.parent
    if not SRC_ZIP.exists():
        sys.exit(f"❌ 找不到來源：{SRC_ZIP}\n   先確認 G: 掛著"
                 "（Test-Path 'G:\\我的雲端硬碟'）")
    dst.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(SRC_ZIP) as z:
        z.extractall(dst)
    print(f"✓ 解壓到 {dst}　{len(list(XML_ROOT.glob('*/*.xml')))} 個 XML")


def cmd_catalog_only():
    """只重出目錄：讀 OUT_DIR 既有的 *.toc.json，不重新解析 103 冊 XML。
    改了目錄欄位但正文沒變時用這個，免得把 368 MB 重寫一次上 Drive。"""
    b = Builder(write=True)
    metas = []
    for p in sorted(OUT_DIR.glob(f"{CANON}*.toc.json")):
        metas.append(json.loads(p.read_text(encoding="utf-8"))["meta"])
    if not metas:
        sys.exit(f"❌ {OUT_DIR} 裡沒有 toc.json，先跑 --build")
    b.works = metas
    for vol, _, title in volume_files():
        b.vol_titles[vol] = title
    b._write_catalog()
    print(f"✓ 目錄重出：{len(metas)} 部 → {OUT_DIR / (CANON + '.catalog.json')}")


def cmd_inspect(toh: str):
    b = Builder(write=False)
    target = toh_key(toh)
    for ev in stream_volumes():
        if ev[0] == "vol":
            b.vol_titles[ev[1]] = ev[2]
        elif ev[0] == "toh":
            b.on_text_milestone(ev[1], ev[2], ev[3], ev[4], ev[5])
            last = b.works[-1] if b.works else None
            if last and last["toh"] and toh_key(last["toh"]) == target:
                break
        elif ev[0] == "text":
            b.on_text(ev[1])
        elif ev[0] == "front":
            b.on_front(ev[1])
    last = b.works[-1] if b.works else None
    if not last or not last["toh"] or toh_key(last["toh"]) != target:
        b._flush()
    hit = [m for m in b.works if m["toh"] and toh_key(m["toh"]) == target]
    if not hit:
        sys.exit(f"找不到 Toh {toh}")
    m = hit[-1]
    print(json.dumps(m, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description="德格版甘珠爾 TEI → 逐部段落資料")
    ap.add_argument("--unzip", action="store_true", help="從 Drive 解壓來源到本機快取")
    ap.add_argument("--audit", action="store_true", help="全掃不寫檔，只印對帳")
    ap.add_argument("--build", action="store_true", help="寫 JSONL＋toc＋catalog")
    ap.add_argument("--restart", action="store_true", help="不續跑，從第一冊重來")
    ap.add_argument("--catalog-only", action="store_true",
                    help="只重出 DK.catalog.json（讀既有 toc.json，不重解析）")
    ap.add_argument("--inspect", type=str, help="看某部（Toh 號，如 1 或 539a）")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if a.unzip:
        cmd_unzip()
        return
    if not XML_ROOT.exists():
        sys.exit(f"❌ 找不到解壓後的 XML：{XML_ROOT}\n"
                 "   先跑 python scripts/tripitaka_derge.py --unzip")
    if a.catalog_only:
        cmd_catalog_only()
        return
    if a.inspect:
        cmd_inspect(a.inspect)
        return
    if not (a.audit or a.build):
        ap.print_help()
        return

    b = Builder(write=bool(a.build))
    sv, sp = 1, 0
    if a.build and not a.restart:
        sv, sp = b.load_state()
        if sv > 1 or sp:
            print(f"↻ 續跑：從冊 {sv} 第 {sp} 葉起（已完成 {len(b.works)} 部）")
    elif a.build and a.restart and STATE_PATH.exists():
        STATE_PATH.unlink()

    print(f"來源 {XML_ROOT}")
    if a.build:
        print(f"產出 {OUT_DIR}")
    b.run(sv, sp, quiet=a.quiet)
    r = report(b)
    _report_divisions(b)
    if a.build:
        print(f"\n✓ 本輪寫出 {b.written} 部 → {OUT_DIR}")
        print(f"  目錄 {OUT_DIR / (CANON + '.catalog.json')}")
        if r["diff"] == 0:
            STATE_PATH.unlink(missing_ok=True)
        else:
            print("  ❌ 字數對不上，state 保留供重跑")


if __name__ == "__main__":
    main()
