# -*- coding: utf-8 -*-
"""把一門課的指定讀物排成一本 B5 讀本。

三本，一門課一本（2026-09-10 之前週一與週六是合成一本 877 頁的，使用者定案拆開）：

  `--reader mon1` / `mon2`  《宗教研究基本問題與研究方法》週一第 2 節 博1A．
      上冊 W02–W08（14 篇）、下冊 W10–W17（18 篇）。合併那本（731 頁）已作廢。
  `--reader sat`  《宗教學理論與方法（一）》單週六第 1 節 碩專1A．7 篇
  `--reader japanese` 《初階宗教學日文文獻選讀》週二第 1 節 碩1A．13 篇，
      內容是自訂十五週計畫的各週讀本，見 japanese_self_study_plan.py。

MacIntyre 與 Segal〈In Defense of Reductionism〉兩門課都指定，**兩本各收一份**。

版面（使用者定案）：**JIS B5（18.2×25.7cm）**、正文滿版、**行距 1.5 倍**
（＝字級的 1.8 倍行高，筆記寫在行間，不另闢筆記欄）、頁眉印「週次．篇名」、
頁碼在下。每篇正文之後附一頁**繁中閱讀導引**（摘要／重點／可討論的問題），
由 LLM 產生後快取，不會每次重跑重花額度。封面是滿版深色橫幅一課一色，
**上面只有課程名稱、學期、授課教師、學生姓名**。成品直接放該門課的資料夾（`--out` 可改）。

    python -X utf8 scripts/build_course_reader.py --reader mon1
    python -X utf8 scripts/build_course_reader.py --reader sat
    python -X utf8 scripts/build_course_reader.py --reader japanese
    python -X utf8 scripts/build_course_reader.py --reader sat --only 2   # 只出第 2 部，試版面
    python -X utf8 scripts/build_course_reader.py --reader mon2 --no-summary  # 先不叫 LLM
    python -X utf8 scripts/build_course_reader.py --mode facsimile   # 原頁面影印合本

## 三個踩過的坑

  1. **字型不能用 helv**。Base-14 的 Helvetica 是 Latin-1，編不了 `“ ” ’ —`，
     PyMuPDF 會替換成 `·`，於是滿頁「·religion·」「Smith·s」；更糟的是替換字比
     原字寬，換行是按原字量的，量得下、印出來卻爆出欄外。要嵌真正的 Unicode
     字型（Times），而且量寬要用 `fitz.Font`，`fitz.get_text_length` 不認自訂字型。
     CJK 也一樣要嵌（細明體／MS 明朝）：內建的 `china-t`／`japan` 量不到字寬，
     只能假設每字全形，數字括號拉丁字全被撐開，印成「W0 5」「（ こ ）」。
  2. **頁眉頁碼會混進內文**。用**座標**濾（頁面最上 6%／最下 6% 的區塊丟掉），
     不要用正則猜，正則會連正文第一行一起吃掉。
  3. **段落會被切在句子中間**。掃描本的 block 常在跨欄跨頁處斷開，直接當段落
     會出現「…seems to have no domain」「limits and therefore…」這種割裂。
     所以前一塊結尾不是句末標點、後一塊又是小寫開頭時，接回去。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_REPO = str(Path(__file__).resolve().parent.parent)
BASE = r"G:\我的雲端硬碟\玄奘\博一上\上課"
C_MON = "宗教研究基本問題與研究方法"      # 週一 第2節　博士班1A
C_SAT = "宗教學理論與方法(一)"            # 週六 第1節〔單週〕碩專班1A
C_JPN = "初階宗教學日文文獻選讀"          # 週二 第1節　碩士班1A

LATIN = r"C:\Windows\Fonts\times.ttf"
LATIN_BD = r"C:\Windows\Fonts\timesbd.ttf"

# JIS B5
PW, PH = 515.9, 728.5
M_TOP, M_BOT = 60.0, 54.0
BODY_X0, BODY_X1 = 48.0, 468.0            # 正文滿版

# 筆記寫在行與行之間，不另闢欄位——所以行距放到字級的 1.8 倍
# （＝文書處理軟體說的「1.5 倍行高」，因為單倍本身就是 1.2 倍字級）。
LEAD_FACTOR = 1.8
FS = 10.8
LEAD = FS * LEAD_FACTOR
INDENT = FS * 2          # 正文每段首行空兩格
# 小標要看得出是小標：比正文大一點再加粗（2026-09-12 使用者指出
# 〈The nineteenth century〉印成普通段落，分不出層次）。
HEAD_SCALE = 1.16

CJK_ZH = r"C:\Windows\Fonts\mingliu.ttc"    # 細明體，繁中正文
CJK_JA = r"C:\Windows\Fonts\msmincho.ttc"   # MS 明朝，日文正文

_F_REG = fitz.Font(fontfile=LATIN)
_F_BLD = fitz.Font(fontfile=LATIN_BD)

# 行首不該出現的標點（簡易禁則）。完整的 JIS X 4051 太過頭，擋住句讀與
# 收尾括號就解決九成難看的斷行。
NO_LINE_START = "。、，．・：；？！）」』】〉》”’%,.;:?!)]}"


# 封面欄位。使用者 2026-09-10 定案：封面上只有**課程名稱、學期、授課教師、學生
# 姓名**四樣，其他一律不放（課號、教室、學分、凡例都拿掉）。
#
# 三本並排時要一眼分得出是哪一門課，所以橫幅一課一色（沿用原文讀本那一套：
# 同一條深色橫幅、同一條亮色細線，只換顏色與字）。
SEMESTER = "115-1"

COVER = {
    "mon1": dict(title="宗教研究基本問題與研究方法", volume="上冊　第二至八週",
                 teacher="根瑟馬庫斯", student="張辰瑋", banner="1E3A5F", rule="C8A24A"),
    "mon2": dict(title="宗教研究基本問題與研究方法", volume="下冊　第十至十七週",
                 teacher="根瑟馬庫斯", student="張辰瑋", banner="1E3A5F", rule="C8A24A"),
    "sat": dict(title="宗教學理論與方法（一）", teacher="根瑟馬庫斯",
                student="張辰瑋", banner="5A2E36", rule="D9A566"),      # 深酒紅
    "japanese": dict(title="初階宗教學日文文獻選讀", teacher="倪杰",
                     student="張辰瑋", banner="3B4A26", rule="C7B87A"),  # 橄欖綠
}

# ── 讀本結構 ────────────────────────────────────────────────────────────
# 兩門課本來合成一本（877 頁），2026-09-10 使用者定案**拆成兩本、合本作廢**：
# 一門一本，帶去上課的就是那門課要用的那本。MacIntyre 與 Segal〈In Defense of
# Reductionism〉兩門都指定，兩本各收一份（不是漏了去重，是刻意的）。
MON_PARTS = [
    ("第一部　學科的成立與定位", "宗教學何以成為一門獨立學科，以及它與神學的分界。", [
        ("Alles_Study of Religion", "W02-04"),
        ("Sharpe_The Study of Religion in Historical", "W02-04"),
        ("Sharpe_Theology and Religious Studies", "W02-04"),
        ("Whaling_Introduction", "W02-04"),
        ("King_Orientalism", "W02-04"),
    ]),
    ("第二部　研究對象的定義", "「宗教」這個詞指什麼？定義本身就是理論主張。", [
        ("Braun_Religion", "W05"),
        ("Sharpe_The Question of Definition", "W05"),
        ("Arnal_Definition", "W05"),
    ]),
    ("第三部　理解、解釋與詮釋", "理解一個宗教，需不需要先相信它？後兩篇是內外部之爭的經典交鋒。", [
        ("Sharpe_Commitment and Understanding", "W06-08"),
        ("Green_Hermeneutics", "W06-08"),
        ("Penner_Interpretation", "W06-08"),
        ("Segal_Theories of Religion", "W06-08"),
        ("MacIntyre_Is Understanding Religion Compatible", "W06-08"),
        ("Segal_In Defense of Reductionism", "W06-08"),
    ]),
    ("第四部　現代主義與後現代主義", "學科的現代性處境。", [
        ("Wiebe_Modernism", "W10"),
        ("Wolfart_Postmodernism", "W10"),
        ("Campbell_Modernity and Postmodernity", "W10"),
    ]),
    ("第五部　歷史與比較", "宗教學的兩大方法：歷史研究與比較研究。", [
        ("King_Historical and Phenomenological Approaches (41-56)", "W11"),
        ("King_Historical and Phenomenological Approaches (84-164)", "W11"),
        ("Smith_Classification", "W12"),
        ("Martin_Comparison", "W12"),
        ("Allen_Phenomenology of Religion", "W13"),
        ("Ryba_Phenomenology of Religion", "W13"),
        ("Roscoe_The Comparative Method", "W13"),
        ("Paden_Comparative Religion", "W13"),
    ]),
    ("第六部　社會與文化", "權威、結構、神話與儀式。", [
        ("Gifford_Religious Authority", "W14"),
        ("Jensen_Structure", "W14"),
        ("Segal_Myth and Ritual", "W15"),
        ("Segal_Myth (Blackwell", "W16"),
        ("McCutcheon_Myth", "W16"),
        ("Grimes_Ritual", "W17"),
        ("Bell_Ritual", "W17"),
    ]),
]

SAT_PARTS = [
    ("第一部　釐清有關宗教學的基本問題", "從康德的〈答何謂啟蒙〉起手：學科的自我理解要從啟蒙談起。", [
        ("Kant_What is Enlightenment", "W02"),
    ]),
    ("第二部　宗教學的宗教概念", "海勒、奧托、馬林諾夫斯基三家原典選（Waardenburg 選集）。", [
        ("Heiler_Friedrich Heiler", "W04–W05"),
        ("Otto_Rudolf Otto", "W06–W07"),
        ("Malinowski_Bronislaw Malinowski", "W08–W09"),
    ]),
    ("第三部　宗教學的研究立場：內部與外部", "理解一個宗教，需不需要先相信它？三篇是這場爭論的經典交鋒。", [
        ("Eliade_A New Humanism", "W12"),
        ("MacIntyre_Is Understanding Religion Compatible", "W14"),
        ("Segal_In Defense of Reductionism", "W15–W16"),
    ]),
]

# 🚨 不分部，一路按週次排（使用者 2026-09-12 定案）。原本分五部，但那五部混了
# 三種標準——第一部按作者、第二三四部按文體、第五部按「同一作者的兩種文體」——
# 所以怎麼看都不合理。這本是跟著每週進度翻的，週次就是它唯一該有的順序；文體的
# 差別寫在各篇篇首的節錄說明裡，不另立部。
JAPANESE_PARTS = [
    ("", "", [
        ("W03_自訂_矢內原忠雄_キリスト教入門_序", "W03"),
        ("W04_自訂_矢內原忠雄_キリスト教入門_第一章上", "W04"),
        ("W05_自訂_矢內原忠雄_キリスト教入門_第一章下", "W05"),
        ("W06_自訂_文語訳_マタイ伝五章_八福", "W06"),
        ("W07_自訂_矢內原忠雄_キリスト教入門_第二章", "W07"),
        ("W08_自訂_文語訳_マタイ伝六章_主の祈り", "W08"),
        ("W10_自訂_內村鑑三_デンマルク国の話_導入", "W10"),
        ("W11_自訂_新渡戸稲造_イエスキリストの友誼", "W11"),
        ("W12_自訂_矢內原忠雄_帝大聖書研究会終講の辞", "W12"),
        ("W13_自訂_高楠順次郎訳_弘法大師と景教との関係", "W13"),
        ("W14_自訂_內村鑑三_後世への最大遺物_序_文語", "W14"),
        ("W14_自訂_內村鑑三_後世への最大遺物_講演冒頭_口語", "W14"),
        ("W15_自訂_古賀敬太_内村の無教会主義対植村の教会主義", "W15"),
    ]),
]

# 課綱刻意只讀一本書的某幾段時，那一段一定停在句子中間——而讀者看到的是
# 「到一半就沒了」，跟真的漏印長得一模一樣（使用者 2026-09-12 對 Alles 那篇的
# 反應就是這樣，那篇是真的壞了；King 這兩段則是課綱本來就跳頁）。所以在篇末印
# 一行說明，把「不是漏印」講出來。鍵是 `MON_PARTS`／`SAT_PARTS` 用的那個 key。
RANGE_NOTE = {
    "King_Historical and Phenomenological Approaches (41-56)":
        "〔課綱指定範圍至原書第 56 頁止，57–83 頁不在指定閱讀內，故末句未完；"
        "接續的 84–164 頁另見下一篇。〕",
    "King_Historical and Phenomenological Approaches (84-164)":
        "〔本篇自原書第 84 頁起，接續前一篇（41–56 頁）；中間 57–83 頁不在課綱"
        "指定閱讀內，故首句非該章起首。〕",
}


# OCR 把字母拆開的白名單。只修這幾組——通用規則會把「a book」接成「abook」。
SPLIT_FIX = [
    (r"\bo f\b", "of"), (r"\bi n\b", "in"), (r"\bi s\b", "is"), (r"\bi t\b", "it"),
    (r"\ba n\b", "an"), (r"\ba t\b", "at"), (r"\bt he\b", "the"), (r"\bth e\b", "the"),
    (r"\bt hat\b", "that"), (r"\bf or\b", "for"), (r"\ban d\b", "and"), (r"\bt o\b", "to"),
]
# 🚨 冒號分號不算句末。掃描本常在「…fifty ways (1998:」處換頁，下一塊是
#    「281). The problem of…」，把冒號當句末就會把一句割成兩段。
SENT_END = tuple('.?!”’")]')


# ── 取材 ────────────────────────────────────────────────────────────────
def index_pdfs(courses) -> dict[str, str]:
    found: dict[str, str] = {}
    for course in courses:
        croot = os.path.join(BASE, course)
        if not os.path.isdir(croot):
            continue
        for wk in sorted(os.listdir(croot)):
            d = os.path.join(croot, wk)
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if f.lower().endswith((".pdf", ".html")):
                    found.setdefault(f, os.path.join(d, f))
    return found


def locate(files: dict[str, str], key: str) -> str | None:
    for name, path in files.items():
        if key in name:
            return path
    return None


# 出處要印完整書目，不是檔名裡的縮寫——使用者 2026-09-12：「EoR 8761­8767 為何
# 不寫完整書名？」切片檔名裡只放得下代號，讀本印出來卻是要拿去引用的。
# 每一條的出版項都逐本翻過該書版權頁（`understanding` 那本是掃描檔，版權頁
# OCR 讀得出來），不是憑印象寫的。
BOOK_CITE = {
    "EoR": "Lindsay Jones, ed., Encyclopedia of Religion, 2nd ed. "
           "(Detroit: Macmillan Reference USA, 2005)",
    "Routledge Companion": "John R. Hinnells, ed., The Routledge Companion to the Study "
                           "of Religion (London: Routledge, 2005)",
    "Understanding Religion": "Eric J. Sharpe, Understanding Religion "
                              "(London: Gerald Duckworth, 1983)",
    "Theory and Method": "Frank Whaling, ed., Theory and Method in Religious Studies: "
                         "Contemporary Approaches to the Study of Religion "
                         "(Berlin: Mouton de Gruyter, 1995)",
    "Guide": "Willi Braun and Russell T. McCutcheon, eds., Guide to the Study of Religion "
             "(London: Cassell, 2000)",
    "Blackwell Companion": "Robert A. Segal, ed., The Blackwell Companion to the Study of "
                           "Religion (Malden, Mass.: Blackwell, 2006)",
    "Insider-Outsider": "Russell T. McCutcheon, ed., The Insider/Outsider Problem in the "
                        "Study of Religion: A Reader (London: Cassell, 1999)",
    "Classical Approaches": "Jacques Waardenburg, ed., Classical Approaches to the Study "
                            "of Religion: Aims, Methods and Theories of Research "
                            "(Berlin: Walter de Gruyter, 2017)",
}


def full_source(tag: str) -> str:
    """「EoR 8761-8767」→ 完整書目＋頁碼。認不出來的代號原樣留著，不亂編。"""
    tag = tag.strip()
    for abbr, cite in sorted(BOOK_CITE.items(), key=lambda kv: -len(kv[0])):
        if tag.startswith(abbr):
            rest = tag[len(abbr):].strip()
            pages = rest.replace("-", "–")
            return f"{cite}, pp. {pages}" if pages else cite
    return tag


def title_of_pdf(path: str) -> tuple[str, str, str]:
    stem = os.path.basename(path)[:-4]
    m = re.match(r"^W[\d\-]+_\d+_([^_]+)_(.+?)\s*\(([^)]*)\)$", stem)
    return (m.group(1), m.group(2), m.group(3)) if m else ("", stem, "")


def _size_tally(page: fitz.Page) -> dict[float, int]:
    tally: dict[float, int] = {}
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                tally[round(sp["size"], 1)] = tally.get(round(sp["size"], 1), 0) + len(sp["text"])
    return tally


def _dominant(tally: dict[float, int]) -> float | None:
    """本文字級。沒有一個字級佔得夠多就回 None——掃描本 OCR 出來的
    字級是連續抖動的（10.1／9.9／10.2／10.0 各佔兩成），那種書**不能**用字級認
    註腳，會把正文當成註挑走。"""
    if not tally:
        return None
    total = sum(tally.values())
    size, n = max(tally.items(), key=lambda kv: kv[1])
    return size if n / total >= 0.55 else None


def _columns(boxes: list[tuple[float, float]], page_w: float) -> list[int]:
    """每一塊屬於第幾欄。

    🚨 雙欄書不能按 y 排序。《宗教百科全書》一頁兩欄，照 (y, x) 排會把右欄的
    段落插進左欄段落中間——最後一頁因此變成「左欄正文→右欄下一條目→左欄書目」，
    於是 ①正文在半途斷掉 ②隔壁條目〈THE ACADEMIC STUDY OF RELIGION IN
    AUSTRALIA AND OCEANIA〉整段竄進來 ③書目排在竄進來的內容後面，`cut_bibliography`
    砍不到它前面那一段（2026-09-12 使用者指出）。兩欄要各自讀完再換欄。
    """
    mid = page_w / 2
    left = [i for i, (x0, x1) in enumerate(boxes) if x1 <= mid + 8]
    right = [i for i, (x0, x1) in enumerate(boxes) if x0 >= mid - 8]
    span = [i for i, (x0, x1) in enumerate(boxes) if x0 < mid - 8 < mid + 8 < x1]
    # 判成雙欄的條件從嚴：兩邊都要有幾塊，而且橫跨中線的（標題、表格）要夠少。
    if len(left) < 2 or len(right) < 2 or len(span) > max(1, 0.15 * len(boxes)):
        return [0] * len(boxes)
    cols = [0] * len(boxes)
    for i in right:
        cols[i] = 1
    for i in span:                      # 橫跨兩欄的當左欄處理，靠 y 落在該落的地方
        cols[i] = 0
    return cols


def page_paragraphs(page: fitz.Page, body_size: float | None = None,
                    size_known: bool = True) -> tuple[list[str], list[str]]:
    """回傳 (正文段落, 註腳段落)。

    註腳原本混在正文流裡——Waardenburg 選集那幾篇的頁底註就這樣夾進段落中間，
    印出來是「…finite being and infinite mystery.³² Friedrich von Hügel, ‘The three
    elements of religion’…」，句子被一條書目切斷（使用者 2026-09-10 指出）。

    認法：**字級明顯比本文小**（≥1pt）且在版心下半。位置不能單獨當判準（康德那篇
    有整頁都是譯者註），字級也不能單獨當判準（頁眉頁碼也比較小）。

    🚨 `body_size` 要用**整篇**的本文字級，不能用單頁的：康德那篇的譯者註自成一頁，
    用單頁字級去比，那一頁的註就是「本文」，一條都認不出來。

    🚨 而**整篇算不出本文字級時，就不要回頭用單頁的**（`size_known=False`）。
    Whaling 那本掃描檔的字級是連續抖動的（9.9／10.4／10.1 各佔兩三成），整篇
    `_dominant` 回 None，舊版就退回單頁字級——於是 King 那篇有 84 個「小標」，
    其中十行是被判成粗體小標的**正文**（「Hultkrantz also emphasizes that, ideally
    speaking, the phenomenolo-」），每行都吃掉 47pt，整頁只排得下十一行
    （2026-09-12 稽核抓到）。算不出來就只靠版面認小標，不猜字級。
    """
    h, w = page.rect.height, page.rect.width
    top_cut, bot_cut = h * 0.06, h * 0.94
    tally = _size_tally(page)
    if body_size is None and size_known:
        body_size = _dominant(tally)
    # 這一頁的中位字級（按字數加權）。抖動的掃描本算不出「主字級」，但中位數
    # 一樣穩，用來認「明顯比正文大」的小標。
    mid_size = None
    if tally:
        run, half = 0, sum(tally.values()) / 2
        for s in sorted(tally):
            run += tally[s]
            if run >= half:
                mid_size = s
                break
    body, notes = [], []
    raw: list[dict] = []
    for blk in page.get_text("dict")["blocks"]:
        lines = blk.get("lines", [])
        if not lines:
            continue
        # 🚨 行與行之間要補換行。直接把 span 串起來會把行尾的空白吃掉，整篇變成
        #    「Christendom,but」「ofmankind」「precise-ly」——看起來像 OCR 爛掉，
        #    其實是抽取時自己黏的（2026-09-10 踩過）。
        txt = "\n".join("".join(sp["text"] for sp in ln["spans"]) for ln in lines)
        if not txt.strip():
            continue
        x0, y0, x1, y1 = blk["bbox"]
        if y1 < top_cut or y0 > bot_cut:
            continue
        raw.append(dict(txt=txt, x0=x0, y0=y0, x1=x1, y1=y1, lines=lines))

    cols = _columns([(b["x0"], b["x1"]) for b in raw], w)
    for i, b in enumerate(raw):
        b["col"] = cols[i]
    order = sorted(range(len(raw)), key=lambda i: (raw[i]["col"], raw[i]["y0"], raw[i]["x0"]))

    # 欄寬：認「單獨成行的小標」要用同一欄的行寬當基準，不能用整頁寬。
    col_w: dict[int, float] = {}
    for b in raw:
        col_w[b["col"]] = max(col_w.get(b["col"], 0.0), b["x1"] - b["x0"])

    prev_bottom: dict[int, float] = {}
    for i in order:
        b = raw[i]
        txt, lines = b["txt"], b["lines"]
        size = max(sp["size"] for ln in lines for sp in ln["spans"])
        letters = [c for c in txt if c.isalpha()]
        shouty = letters and sum(c.isupper() for c in letters) / len(letters) > 0.7
        is_note = (body_size is not None and size <= body_size - 1.0
                   and b["y0"] / h > 0.10 and not (shouty and len(txt) < 90))
        # 🚨 小標不能只認「整串大寫」：這幾本的小標多半是 Title Case 或引號句
        #    （'The phenomenological method'），只認大寫的話 sat 那本 7 篇全掛零。
        #    改看來源的字級與粗體。
        bold = any("bold" in sp["font"].lower() for ln in lines for sp in ln["spans"])
        flat = " ".join(txt.split())
        # 🚨 掃描本沒有字型可認：Routledge Companion 的文字層是 GlyphLessFont，
        #    小標〈The nineteenth century〉跟正文同字級同字型，只有版面看得出來
        #    （單獨成行、只佔欄寬一半、上面空一截、不以句點收尾）。2026-09-12
        #    使用者指出這種小標被印成普通段落。
        gap_above = b["y0"] - prev_bottom.get(b["col"], b["y0"])
        line_h = (b["y1"] - b["y0"]) / max(1, len(lines))
        # 🚨 字數也要卡。掃描本會把一段的第一行單獨切成一塊，版面完全像小標
        #    （短、窄、上面空一截、不以句點收尾），印出來就是一行放大加粗的
        #    「A quite different attack on the animistic theory came from the Sco」。
        #    小標是短語不是句子：這批書真正的小標最長七個字（「3. The methodological
        #    debate since world war II」），所以八個字以上一律不是。
        standalone = (len(lines) == 1 and 4 < len(flat) < 90 and len(flat.split()) <= 8
                      and (b["x1"] - b["x0"]) < 0.62 * col_w.get(b["col"], w)
                      and gap_above > line_h * 1.25
                      and flat[:1].isupper() and not flat.endswith(SENT_END)
                      and not flat.endswith(","))
        # 字級認不出來時（size_known=False）不能用「粗體就是小標」——那條把
        # 正文整行判成小標。改用「**比這一頁的中位字級大 1pt 以上**的單行粗體」：
        # Whaling 那本真正的小標是 11.4pt／Constantia-Bold（頁面中位 9.9–10.4），
        # 而誤判的那幾行是 8.2pt，比中位**小**，這條擋得掉。
        # 同樣要卡字數：Routledge Companion 的 OCR 字級從 8.5 抖到 10.4，光看
        # 「比中位大 1pt」會把正文第一行也收進來（「A quite different attack on the
        # animistic theory came from the Scottis」，12 個字）。
        bigger = (mid_size is not None and size >= mid_size + 1.0
                  and len(lines) == 1 and len(flat.split()) <= 8
                  and not flat.endswith(SENT_END))
        by_size = body_size is not None and (
            size >= body_size + 0.6 or (bold and not flat.endswith(SENT_END)))
        is_head = (not is_note and 4 < len(flat) < 90 and (
            by_size or bigger or (shouty and len(flat) > 8) or standalone))
        (notes if is_note else body).append((txt, is_head))
        if not is_note:
            prev_bottom[b["col"]] = b["y1"]
    return body, [t for t, _ in notes]


# 🚨 私用區（PUA）字元。Waardenburg 那本的數字被字型對到 U+100000 一帶，
#    文字層裡根本不是數字——照抄就印成一整排「􀀀􀀀􀀀」豆腐格
#    （2026-09-10 使用者貼出來的那頁註就是）。數字救不回來（ToUnicode 壞的），
#    所以：整段 PUA 佔比高的直接丟（那種多半是書目與年份表），其餘把 PUA 清掉。
PUA = re.compile(r"[\ue000-\uf8ff\U000f0000-\U0010ffff]")


def pua_ratio(text: str) -> float:
    t = text.strip()
    return len(PUA.findall(t)) / len(t) if t else 0.0


def clean(text: str) -> str:
    text = re.sub(r"([a-z])-\s*\n\s*([a-z])", r"\1\2", text)   # 行末斷字，只接小寫
    text = re.sub(r"([a-z])-\s+([a-z])", r"\1\2", text)
    text = text.replace("\n", " ")
    for pat, rep in SPLIT_FIX:
        text = re.sub(pat, rep, text)
    text = PUA.sub("", text)
    # 來源文字層常在標點後掉空格（「…mystery.Valuable」「…religion,This」）。
    # 只補在標點後面，所以 McDonald、MacIntyre 這種姓氏不會被動到。
    text = re.sub(r"([a-z]{2})([.,;:])([A-Z][a-z])", r"\1\2 \3", text)
    # 句點後面直接接大寫字母＝來源掉了那個空白（「…and.Valuable」「…again.This」）。
    # 只補這一種：前面是小寫字母＋句讀，後面是大寫開頭的字，縮寫（U.S.A.）不受影響。
    text = re.sub(r"([a-z][.,;:])([A-Z][a-z])", r"\1 \2", text)
    return re.sub(r"\s+", " ", text).strip()


# 篇末書目的標題。使用者定案：印本不收書目（要查出處回頭看 Drive 上那份切片，
# 原檔一個字都沒動）。只認**獨立成行的短標題**，不然正文裡出現 "the references
# to..." 也會被當成書目起點，整篇後半就沒了。
BIBLIO_WORDS = ("bibliography", "references", "referencelist", "workscited",
                "furtherreading", "suggestedreading", "suggestionsforfurtherreading",
                "selectbibliography", "selectedbibliography", "worksconsulted",
                # 篇末註也在這裡收掉。康德那篇的註是掃描本的小字，字級認不出來，
                # 於是整批黏在正文最後一段後面印出來（「…their dignity.7 Königsberg,
                # Prussia September 30, 1784 Notes 2 . “Dare to know !”…」，還是
                # 拼錯的碎片）。註不印，所以看到標題就收（2026-09-12）。
                "notes", "note", "尾註", "註釋", "注釋",
                "參考書目", "徵引書目", "引用書目")


def _biblio_start(text: str) -> bool:
    """這一段是不是篇末書目的開頭。

    🚨 不能要求「整段只有標題」。掃描本的 OCR 常把標題跟第一筆書目黏成一段
    （「BIBLIOGRAPHY Alles, Gregory D. …」），字母之間還會被拆開
    （「B IBLIOGRAPHY」）——2026-09-10 使用者連講三次書目還在，就是卡在這。
    改成：**去掉空白之後看開頭**是不是那幾個詞。

    後面要接大寫、數字或結尾才算，否則正文裡的「References to the sacred…」
    也會中招，一中招就把整篇後半砍光。
    """
    flat = re.sub(r"[\s.:：]", "", text)[:60].lower()
    for w in BIBLIO_WORDS:
        if flat.startswith(w):
            rest = re.sub(r"[\s.:：]", "", text)[len(w):].lstrip()
            return not rest or rest[0].isupper() or rest[0].isdigit() or ord(rest[0]) > 0x2E00
    return False


# Waardenburg《Classical Approaches》每一篇前面都有編者寫的作者簡介（生平、
# 著作、這一段選文的來歷），固定以「The following fragment has been taken from…」
# 收尾。那段落在課綱指定的頁碼範圍內，切片沒切錯，但它不是要讀的正文
# （使用者 2026-09-10：「作者簡介也不應該出現在文本中」）。
EDITOR_INTRO_END = re.compile(
    r"^the following (fragment|extract|text|passage|selection)s?\b", re.I)
# 有些篇沒有那句收尾，導言就是一段「某某某 was born in 1892 in Munich…」的小傳。
EDITOR_BIO = re.compile(r"^[A-Z][\w.\-’' ]{2,60} was born (in|on)\b", re.I)


def cut_editor_intro(paras: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], int]:
    """把編者導言連同那句「以下選文取自……」一起砍掉。只找**前四分之一**，
    免得正文中間出現同樣句型時把半篇文章砍掉。"""
    for i, (_, t) in enumerate(paras):
        if i > len(paras) * 0.25:
            break
        if EDITOR_INTRO_END.match(t.strip()) or EDITOR_BIO.match(t.strip()):
            return paras[i + 1:], i + 1
    return paras, 0


def cut_bibliography(paras: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], int]:
    """砍掉篇末書目。回傳 (留下來的段落, 砍掉幾段)。

    只從**後三分之一**開始找：導論段落就寫過 "References" 這個詞，從頭找會把
    整篇正文砍掉——而砍掉不會報錯，印出來也像一篇完整的文章。
    """
    for i, (_, t) in enumerate(paras):
        if i > len(paras) * 0.35 and _biblio_start(t):
            return paras[:i], len(paras) - i
    return paras, 0


# 小標：一整串大寫字之後直接接一個正常大小寫的字。掃描本常把小標跟後面那段
# 黏成一塊（「THE EMERGENCE OF THE ACADEMIC STUDY OF RELIGION.According to a
# well-worn German cliché…」），拆出來才讀得出結構，也才能加粗。
HEAD_RUN = re.compile(r"^([A-Z][A-Z0-9 ,:;'\u2019\-\u2013&()/]{4,88}?)[.:]?\s*(?=[A-Z][a-z])")


def _trim_head(h: str) -> str:
    """小標尾巴的三四位數是頁碼（百科全書頁眉「… AND OCEANIA 8767」），剝掉。"""
    return re.sub(r"\s*\d{3,}\s*$", "", h).strip()


def split_heading(text: str) -> list[tuple[str, str]]:
    """一段 → [(kind, text)]，kind 是 'h'（小標）或 'p'（正文）。"""
    t = text.strip()
    letters = [c for c in t if c.isalpha()]
    if letters and len(t) < 90 and sum(c.isupper() for c in letters) / len(letters) > 0.8:
        return [("h", _trim_head(t.rstrip(".:")))]   # 整段就是小標
    m = HEAD_RUN.match(t)
    if m and len(m.group(1).split()) >= 2 and len(t) - m.end() > 40:
        return [("h", _trim_head(m.group(1).strip().rstrip(".:"))),
                ("p", t[m.end():].lstrip())]
    return [("p", t)]


def extract_pdf(path: str) -> tuple[list[tuple[str, str]], list[str]]:
    """回傳 (正文段落, 註腳)。註腳另外收，排在篇末，不再插進正文流。"""
    doc = fitz.open(path)
    tally: dict[float, int] = {}
    for page in doc:
        for k, v in _size_tally(page).items():
            tally[k] = tally.get(k, 0) + v
    body_size = _dominant(tally)

    pages = [page_paragraphs(page, body_size, size_known=body_size is not None)
             for page in doc]

    # 🚨 頁眉頁腳不能只靠邊界座標濾。《宗教百科全書》那一篇的頁眉離頂端超過 6%，
    #    於是「STUDY OF RELIGION: AN OVERVIEW 8766」每一頁都被當成正文收進去，
    #    還被接到下一段的句首（使用者 2026-09-10 指出）。改用**跨頁重複**認：
    #    把每頁最上與最下那一塊抽出來、去掉數字，重複到一半以上頁數的就是頁眉頁腳。
    def _head_key(t: str) -> str:
        return re.sub(r"\d+", "", clean(t)).strip().lower()[:60]

    # 頁數少的切片湊不到「一半以上的頁」那個門檻，所以資料庫套印再單獨認一次。
    # 這幾條都是實際出現在來源檔裡的字樣，不是憑空防守。
    stamp = re.compile(r"(brought to you by|^authenticated$|download date|downloaded on|"
                       r"this content downloaded|terms and conditions|all use subject to|"
                       r"digitized by the internet archive|bobst library)", re.I | re.M)

    # 🚨 而且不能只看每頁的頭尾兩塊。de Gruyter 那批（Whaling、Waardenburg、
    #    King 的兩份切片）每頁都蓋一條下載浮水印「Brought to you by | New York
    #    University Bobst Library Technical Services／Authenticated／Download Date
    #    | 2/23/16 3:52 PM」，它落在版心裡、既不是第一塊也不是最後一塊，於是
    #    整條印進正文，還讓 King 那兩篇的篇尾停在「…Library Technical Services」
    #    （使用者 2026-09-12 要求「轉錄時不要有頁緣的頁數和書名跑進來」）。
    #    改成**每一塊都算**：整篇有一半以上的頁都出現同一段文字的，就是版面套印。
    seen: dict[str, int] = {}
    for body_blocks, _ in pages:
        for cand in {b[0] for b in body_blocks}:
            k = _head_key(cand)
            if 0 < len(k) < 60:
                seen[k] = seen.get(k, 0) + 1
    threshold = max(3, int(len(pages) * 0.5))
    running = {k for k, v in seen.items() if v >= threshold}

    # 🚨 去數字還不夠。掃描本的頁眉每一頁 OCR 成不一樣的垃圾——「8 4 Ursula King」
    #    「né Ursula King」「Π4 Ursula King」「I20 Ursula King」——去掉數字之後
    #    每一條還是獨一無二，於是一條都去不掉，84 篇「小標」裡有一半是頁眉
    #    （2026-09-12 抓到）。所以再用**只留字母**的鍵數一次，整塊丟掉。
    def _alpha_key(t: str) -> str:
        return re.sub(r"[^a-z一-鿿]", "", clean(t).lower())[:60]

    seen_a: dict[str, int] = {}
    for body_blocks, _ in pages:
        for cand in {b[0] for b in body_blocks}:
            k = _alpha_key(cand)
            if 4 < len(k) < 60:
                seen_a[k] = seen_a.get(k, 0) + 1
    running_alpha = {k for k, v in seen_a.items() if v >= threshold}

    # 有些頁的頁眉跟正文黏在同一塊裡（「STUDY OF RELIGION: AN OVERVIEWUnlike
    # theology…」），整塊丟掉會連正文一起丟，所以改成把開頭那一段剝掉。
    head_pats = [re.compile(r"^\s*" + r"[\s\d]*".join(re.escape(w) for w in k.split())
                            + r"[\s\d]*", re.I) for k in running if k.split()]

    def _strip_head(t: str) -> str:
        for pat in head_pats:
            m = pat.match(t)
            if m and m.end() < len(t):
                return t[m.end():].lstrip()
        return t

    # 🚨 小標有三種假貨要擋，2026-09-11 實測全都出現過：
    #    ①文章自己的標題行（跟頁眉同字，字級也大）②Notes／Bibliography 這種
    #    「有標題沒內容」的段（註釋與書目都不印）③同一個頁眉在多頁被認成小標。
    _author, _title, _ = title_of_pdf(path)
    _own = re.sub(r"[\W_]+", "", (_author + _title)).lower()
    _skip = re.compile(r"^(notes?|references?|bibliography|index|"
                       r"acknowledge?ments?|further reading|works cited)\b", re.I)
    _seen: set[str] = set()

    def _head_ok(t: str) -> bool:
        flat = re.sub(r"[\W_]+", "", t).lower()
        if not flat or _skip.match(t.strip()):
            return False
        # 🚨 帶頁碼的不是小標，是頁眉：《宗教百科全書》每篇的頁眉是
        #    「STUDY OF RELIGION: … IN AUSTRALIA AND OCEANIA 8767」，切片尾端
        #    會夾到下一篇的那一行，只出現一次所以躲過了頁眉去重。
        if re.search(r"\b\d{3,}\b", t):
            return False
        # 只排除「整個篇名」，不排除篇名的一部分——Waardenburg 那本的篇名是
        # 「Friedrich Heiler (Prayer; The Scholarly Study of Religion)」，而
        # 'Prayer' 與 'The Scholarly Study of Religion' 正是書裡真的小標。
        if (flat in _own and len(flat) >= 0.6 * len(_own)) or _own in flat:
            return False
        if flat in _seen:
            return False                       # 重複＝多半是頁眉
        _seen.add(flat)
        return True

    paras: list[tuple[str, str]] = []
    notes: list[str] = []
    dropped_pua = 0
    for body_blocks, note_blocks in pages:
        # 🚨 套印要**逐行剝**，不能整塊丟。de Gruyter 那批的浮水印第一行
        #    「Brought to you by | … Bobst Library Technical Services」常跟正文
        #    最後一段黏在同一個 block 裡，整塊丟掉就連正文一起沒了——King 那篇
        #    41-56 的最後一段就這樣被吃掉，而讀本看起來完全正常（2026-09-12）。
        body_blocks = [("\n".join(ln for ln in t.split("\n") if not stamp.search(ln)), hd)
                       for t, hd in body_blocks]
        body_blocks = [b for b in body_blocks
                       if b[0].strip()
                       and _head_key(b[0]) not in running
                       and _alpha_key(b[0]) not in running_alpha]
        note_blocks = [b for b in note_blocks if not stamp.search(b)]
        body_blocks = [(_strip_head(t), hd) for t, hd in body_blocks]
        for raw in note_blocks:
            if pua_ratio(raw) > 0.12:      # 整段是壞掉的數字，救不回來就別印
                dropped_pua += 1
                continue
            t = clean(raw)
            if len(t) < 3:
                continue
            # 註腳欄裡一行就是一個 block，直接收會把一條註切成七八條半句
            # （「1. Ed. note. A part from the last note, which is Kant's, notes」
            #  「opening are those of the essay's translator...」）。所以只有看到
            # 註號才起新的一條，其餘接回上一條。
            if notes and not re.match(r"^(\d+\s*[.)]\s|[*†‡•])", t)                     and not notes[-1].endswith(SENT_END):
                notes[-1] += " " + t
            else:
                notes.append(t)
        for raw, is_head in body_blocks:
            if pua_ratio(raw) > 0.12:
                dropped_pua += 1
                continue
            t = clean(raw)
            if len(t) < 3:
                continue
            # 整行大寫又以頁碼收尾＝百科全書的頁眉，正文不要
            letters = [c for c in t if c.isalpha()]
            if (letters and sum(c.isupper() for c in letters) / len(letters) > 0.7
                    and re.search(r"\b\d{3,4}\s*$", t)):
                continue
            # 前一塊沒收尾 → 多半是同一段被跨欄跨頁切開了。但小標題也沒有句末
            # 標點（「“Religion” as Specter」），所以再看長度：夠長才是被切斷的
            # 正文，短的當標題，不接。
            prev = paras[-1][1] if paras else ""
            # 🚨 判斷「上一段收句了沒」要先剝掉行尾的註號。文字層裡的上標註號就是
            #    普通數字（「…in accordance with their dignity.7」），不剝就每一段
            #    帶註的都判成沒收尾，於是把篇末註整批接到正文最後一段（2026-09-12）。
            tail = re.sub(r"\d{1,3}$", "", prev)
            cont = (bool(prev) and paras[-1][0] == "p" and not tail.endswith(SENT_END)
                    and (len(prev) > 60 or t[:1].islower() or re.match(r"^\d+[).,]", t)))
            # 🚨 小標判定要讓位給「接回上一句」。掃描本會把一段的某一行單獨切成一塊，
            #    版面看起來就像小標（短、上面空一截、不以句點收尾），於是印出一行
            #    放大加粗的「A quite different attack on the animistic theory came
            #    from the S」，而且那一句從此被切成兩段。小標不會接在沒收句的句子
            #    後面，所以 `cont` 成立時一律不是小標（2026-09-12）。
            if is_head and not cont and len(t) < 90 and _head_ok(t):
                paras.append(("h", t.rstrip(".:")))
                continue
            if cont:
                paras[-1] = ("p", prev + " " + t)
            else:
                for kind, seg in split_heading(t):
                    # split_heading 也會吐小標，同樣要過閘：頁眉殘骸
                    # 就是從段首被切出來的，區塊層的過濾攔不到。
                    if kind == 'h' and not _head_ok(seg):
                        kind = 'p'
                    paras.append((kind, seg))
    doc.close()
    if dropped_pua:
        print(f"    · 丟掉 {dropped_pua} 段壞字元（來源字型把數字對到私用區）")
    return paras, notes


# 這幾個是真的單字，別把它們跟鄰居黏起來
SHORT_OK = {"a", "i", "an", "as", "at", "be", "by", "do", "go", "he", "if", "in",
            "is", "it", "me", "my", "no", "of", "on", "or", "so", "to", "up", "us",
            "we", "am", "and", "the", "for", "not", "but", "his", "her", "its",
            "our", "was", "are", "who", "all", "one", "two", "may", "can", "had",
            "has", "him", "she", "you", "out", "own", "too", "use", "way", "new"}


def drop_bad_headings(paras: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], int]:
    """剔掉假小標：帶頁碼的、以及重複的。

    🚨 這是**最後一道**，擺在排版前面。抽取那一層有三條路會產生小標（字型判定、
    整段大寫、段首大寫串），逐條堵過還是漏了《宗教百科全書》那行
    「STUDY OF RELIGION: … AND OCEANIA 8767」——它是下一篇的頁眉，被夾在切片尾端。
    與其繼續追是哪條路漏的，不如在出口統一擋：小標**不可能**帶三位數以上的頁碼，
    同一篇裡也不會有兩個一模一樣的小標（那是頁眉）。
    """
    seen: set[str] = set()
    out, dropped = [], 0
    for kind, t in paras:
        if kind == "h":
            key = re.sub(r"[\W\d_]+", "", t).lower()
            if re.search(r"\d{3,}", t) or not key or key in seen:
                dropped += 1
                continue
            seen.add(key)
        out.append((kind, t))
    return out, dropped


def repair_spacing(paras: list[tuple[str, str]]) -> tuple[list[tuple[str, str]], int]:
    """把掃描本 OCR 甩出來的單一字母黏回去：「W hat」→「What」、「m ethod」→「method」。

    🚨 這裡**只做一件最保守的事**，因為修錯比不修更糟：
      - 只接「落單的單一字母」與緊鄰的詞，而且接起來要是本篇出現過的字。
      - **兩個多字母的詞永遠不接**——逐對硬接會把「for th e」接成「forth e」，
        forth 剛好也是個字，於是偽造出一個看起來正常卻不存在的詞。
      - 標點一律不碰（連標點一起重排會把逗號與引號吃掉）。
    整段逐字母散開的（「c o lo n ia l p e o p le s」）救不回來，留著——那是來源
    掃描的破壞，看得見的雜訊好過看不見的偽造。要真的修只能重跑 Vision OCR。
    """
    text = " ".join(t for _, t in paras)
    vocab: dict[str, int] = {}
    for w in re.findall(r"[A-Za-z]{2,}", text):
        vocab[w.lower()] = vocab.get(w.lower(), 0) + 1
    fixed = 0

    def fix_line(t: str) -> str:
        nonlocal fixed
        toks = t.split(" ")
        out: list[str] = []
        i = 0
        while i < len(toks):
            a, b = toks[i], toks[i + 1] if i + 1 < len(toks) else ""
            # 單一字母 + 後面那個詞（W hat → What；a book 不會中，因為 a 是真字）
            if (re.fullmatch(r"[A-Za-z]", a) and a.lower() not in ("a", "i")
                    and re.fullmatch(r"[A-Za-z]{2,}", b)
                    and vocab.get((a + b).lower(), 0) >= 1):
                out.append(a + b)
                fixed += 1
                i += 2
                continue
            # 詞 + 落單的單一字母（rit u al 這種的後半）
            if (re.fullmatch(r"[A-Za-z]{2,}", a) and re.fullmatch(r"[A-Za-z]", b)
                    and b.lower() not in ("a", "i")
                    and vocab.get((a + b).lower(), 0) >= 2):
                out.append(a + b)
                fixed += 1
                i += 2
                continue
            out.append(a)
            i += 1
        return " ".join(out)

    return [(k, fix_line(t)) for k, t in paras], fixed


def extract_md(path: str) -> tuple[dict, list[str]]:
    """日文讀本的 html：回傳 (出處欄位, 本文段落)。

    這些檔案是 course_html 出的 HTML，先還原成它本來的 markdown 形狀再解析，
    下游就不必再養一套 HTML 解析。
    """
    from course_html import html_to_md
    raw = html_to_md(Path(path).read_text(encoding="utf-8"))
    meta = dict(re.findall(r"^- \*\*(.+?)\*\*：(.+)$", raw, re.M))
    h1 = re.search(r"^# (.+)$", raw, re.M)      # 篇名要用讀本檔的 H1，
    meta["_h1"] = h1.group(1).strip() if h1 else ""   # 用「作品」會讓四篇同名
    body = raw.split("## 本文", 1)[1] if "## 本文" in raw else raw
    paras = [p.strip() for p in body.split("\n") if p.strip() and not p.startswith(("#", ">"))]
    return meta, paras


# ── 排版 ────────────────────────────────────────────────────────────────
class Book:
    """B5 讀本排版器。

    🚨 中西文一律嵌真字型（細明體／MS 明朝／Times），不用 PyMuPDF 內建的
    china-t、japan——內建 CJK 字型量不到字寬，只能假設每個字都是全形，於是
    數字、括號、拉丁字全被撐開，印成「W0 5」「（ こ ）」那樣。
    """

    def __init__(self, lang: str = "zh", half_page: bool = False):
        self.doc = fitz.open()
        self.cjk_path = CJK_JA if lang == "ja" else CJK_ZH
        # 兩套 CJK 字型互為備援，逐字選。MS 明朝沒有繁體的「內」（U+5167），細明體
        # 沒有日文的「内」（U+5185）——這本讀本同一行裡就有「矢內原忠雄《キリスト教
        # 入門》」，只用一套字型，作者名一定缺字。缺字不會報錯，只會印成空白：
        # 2026-09-08 之前 24 頁裡有 19 頁的「內」是空的。
        self.alt_path = CJK_ZH if lang == "ja" else CJK_JA
        self.f_cjk = fitz.Font(fontfile=self.cjk_path)
        self.f_alt = fitz.Font(fontfile=self.alt_path)
        self._glyph_cache: dict[str, bool] = {}
        self.page = None
        self.y = 0.0
        self.head_l = ""
        self.head_r = ""
        self.marks: list[list] = []
        # 半頁模式：正文只排到頁面中線，下半頁留白給使用者寫翻譯。
        # 🚨 只有**日文原文**那些頁要留白。分部頁與繁中閱讀導引留半頁空白是浪費紙
        #    ——導引本來就是中文，沒有東西要翻（使用者 2026-09-10 指出）。所以
        #    `half_default` 記這本書要不要留白，`half_page` 逐段開關。
        self.half_default = half_page
        self.half_page = half_page
        self.entries: list[tuple[str, str, int]] = []   # (週次, 篇名, 內文頁序)

    @property
    def bottom(self) -> float:
        return (PH / 2 - 6) if self.half_page else (PH - M_BOT)

    # ── 量測與斷行 ──────────────────────────────────────────────────
    @staticmethod
    def _is_cjk(ch: str) -> bool:
        return ord(ch) > 0x2E00

    def _kind(self, ch: str) -> str:
        """latin / cjk（主字型）／cjk_alt（主字型沒有這個字，換備援）。"""
        if not self._is_cjk(ch):
            return "latin"
        have = self._glyph_cache.get(ch)
        if have is None:
            have = bool(self.f_cjk.has_glyph(ord(ch)))
            self._glyph_cache[ch] = have
        return "cjk" if have else "cjk_alt"

    def _runs(self, text: str):
        runs, cur, flag = [], "", None
        for ch in text:
            f = self._kind(ch)
            if flag is None or f == flag:
                cur += ch
            else:
                runs.append((cur, flag))
                cur = ch
            flag = f
        if cur:
            runs.append((cur, flag))
        return runs

    def _font(self, kind: str, bold: bool = False):
        if kind == "cjk":
            return self.f_cjk
        if kind == "cjk_alt":
            return self.f_alt
        return _F_BLD if bold else _F_REG

    def measure(self, text: str, size: float, bold: bool = False) -> float:
        return sum(self._font(kind, bold).text_length(run, size)
                   for run, kind in self._runs(text))

    def _tokens(self, text: str):
        """拉丁文以單字為單位斷行，CJK 逐字斷行。"""
        out, buf = [], ""
        for ch in text:
            if self._is_cjk(ch):
                if buf:
                    out.append(buf)
                    buf = ""
                out.append(ch)
            elif ch == " ":
                if buf:
                    out.append(buf)
                    buf = ""
                out.append(" ")
            else:
                buf += ch
        if buf:
            out.append(buf)
        return out

    def wrap(self, text: str, width: float, size: float, bold: bool = False,
             first_indent: float = 0.0) -> list[str]:
        lines, line = [], ""
        for tok in self._tokens(text):
            trial = line + tok
            room = width - (first_indent if not lines else 0)
            if line and self.measure(trial, size, bold) > room:
                if tok in NO_LINE_START:      # 句讀不留行首，往前一行擠
                    lines.append(line + tok)
                    line = ""
                    continue
                lines.append(line.rstrip())
                line = "" if tok == " " else tok
            else:
                line = trial
        if line.strip():
            lines.append(line.rstrip())
        return lines

    def draw(self, x: float, y: float, text: str, size: float, bold: bool = False,
             color=(0, 0, 0)) -> float:
        if not text:
            return x   # 封面有刻意留的空行；insert_text 吃空字串會炸
        for run, kind in self._runs(text):
            if not run:
                continue   # 空的 run 會讓 insert_text 在內部拋 max() on empty
            fn = {"cjk": "CJK", "cjk_alt": "CJK2"}.get(kind, "TNRB" if bold else "TNR")
            self.page.insert_text((x, y), run, fontname=fn, fontsize=size, color=color)
            x += self._font(kind, bold).text_length(run, size)
        return x

    # ── 頁面 ────────────────────────────────────────────────────────
    def new_page(self) -> None:
        self.page = self.doc.new_page(width=PW, height=PH)
        self.page.insert_font(fontname="TNR", fontfile=LATIN)
        self.page.insert_font(fontname="TNRB", fontfile=LATIN_BD)
        self.page.insert_font(fontname="CJK", fontfile=self.cjk_path)
        self.page.insert_font(fontname="CJK2", fontfile=self.alt_path)
        self.y = M_TOP
        if self.head_l or self.head_r:
            self.draw(BODY_X0, M_TOP - 20, self.head_l[:30], 7.6, color=(0.45,) * 3)
            hr = self.head_r[:70]
            self.draw(BODY_X1 - self.measure(hr, 7.6), M_TOP - 20, hr, 7.6, color=(0.45,) * 3)
            self.page.draw_line(fitz.Point(BODY_X0, M_TOP - 14), fitz.Point(BODY_X1, M_TOP - 14),
                                color=(0.8,) * 3, width=0.4)
        if self.half_page:
            mid = PH / 2
            self.page.draw_line(fitz.Point(BODY_X0, mid), fitz.Point(BODY_X1, mid),
                                color=(0.82,) * 3, width=0.5, dashes="[2 3] 0")
            self.draw(BODY_X0, mid + 16, "譯文", 8.4, color=(0.62,) * 3)

    def space(self, need: float) -> None:
        if self.page is None or self.y + need > self.bottom:
            self.new_page()

    def flow(self, text: str, size: float = FS, lead: float | None = None,
             gap: float = 6.0, bold: bool = False, x0: float = BODY_X0,
             x1: float = BODY_X1, color=(0, 0, 0), indent: float = 0.0) -> None:
        """`indent` 是**首行**縮排（正文每段空兩格，第二行起靠齊左界）。"""
        lead = size * LEAD_FACTOR if lead is None else lead
        if not text.strip():          # 空行就只是空一行
            self.space(lead)
            self.y += lead
            return
        lines = self.wrap(text, x1 - x0, size, bold, first_indent=indent)
        n, i = len(lines), 0
        while i < n:
            if self.page is None:
                self.new_page()
            room = int((self.bottom - self.y) // lead)      # 這一頁還放得下幾行
            if room <= 0:
                self.new_page()
                continue
            take = min(room, n - i)   # room 可能比剩下的行還多
            if n - i > take:                 # 這一段要跨頁——處理孤行與寡行
                if take < 2:                 # 這頁只塞得下一行，整段挪到下一頁
                    self.new_page()
                    continue
                if n - i - take == 1:        # 別讓最後一行孤零零落到下一頁
                    take -= 1
            for k in range(take):
                self.draw(x0 + (indent if i + k == 0 else 0), self.y,
                          lines[i + k], size, bold, color)
                self.y += lead
            i += take
            if i < n:
                self.new_page()
        self.y += gap

    def flow_paragraphs(self, paras: list[tuple[str, str]], size: float = FS,
                        gap: float = 6.0, indent: float = 0.0) -> None:
        """把一篇的正文**平均攤到各頁**，不是填滿一頁再換頁。

        貪心填滿的結果是每篇最後一頁只剩殘餘——日文讀本有一頁只有兩行，前一頁
        卻塞了十三行。所以先貪心算出這篇最少要幾頁，再照「每頁可用高度」等比例
        分配，各頁的份量就接近。

        🚨 攤平用的是**每一頁自己的可用高度**，不是一個共用的預算值。舊版拿
        「平均預算」減掉篇首標題塊的高度當第一頁的額度，標題塊一長，額度就變成
        負的——於是篇首那一頁只印得出標題，正文整批被擠到下一頁（日文讀本第 5、
        16 頁只有標題，第 9 頁只有兩行，使用者 2026-09-12 指出）。現在第一頁的
        額度是 `(bottom - y) * 填充率`，標題塊佔多少就少多少，不會反過來扣兩次。

        順帶擋掉孤行寡行，以及吊在頁尾的小標（小標一定跟著它的第一行正文走）。
        """
        if not paras:
            return
        lead = size * LEAD_FACTOR
        if self.page is None:
            self.new_page()

        # ── 攤成「行」。每一行記自己前面要空多少、後面要空多少 ──────────
        items: list[dict] = []
        for bi, (kind, text) in enumerate(paras):
            head = kind == "h"
            fs = size * HEAD_SCALE if head else size
            lines = self.wrap(text, BODY_X1 - BODY_X0, fs, head,
                              first_indent=0 if head else indent)
            lh = fs * LEAD_FACTOR if head else lead
            for li, ln in enumerate(lines):
                items.append(dict(
                    text=ln, kind=kind, size=fs, bold=head, h=lh, bi=bi,
                    li=li, n=len(lines),
                    indent=0 if head or li else indent,
                    pre=(lead * 0.75 if head and li == 0 else 0.0),
                    post=(gap + lead * 0.2 if head else gap) if li == len(lines) - 1 else 0.0,
                ))
        if not items:
            return

        first_avail = max(self.bottom - self.y, lead)
        full_avail = max(self.bottom - M_TOP, lead * 2)

        def cap(p: int) -> float:
            return first_avail if p == 0 else full_avail

        def back_off(page: list[int], nxt: int) -> int:
            """把斷點 `nxt` 往前挪，避開孤行、寡行與吊在頁尾的小標。"""
            first = page[0]
            it = items[nxt]
            if it["li"] > 0:                       # 斷在段落中間
                if it["li"] == 1:                  # 這頁只留得下第一行 → 整段挪走
                    nxt -= 1
                elif it["n"] - it["li"] == 1:      # 下一頁只剩最後一行 → 多帶一行走
                    nxt -= 1
            while nxt - 1 >= first and items[nxt - 1]["kind"] == "h":
                nxt -= 1                           # 小標不能落在頁尾
            return max(nxt, first + 1)

        def pack(ratio: float) -> list[list[int]]:
            pages: list[list[int]] = []
            cur: list[int] = []
            used, p, i = 0.0, 0, 0
            while i < len(items):
                it = items[i]
                need = it["pre"] + it["h"]
                if cur and used + need > cap(p) * ratio:
                    nxt = back_off(cur, i)
                    cur = cur[:nxt - cur[0]] if nxt - cur[0] < len(cur) else cur
                    i = nxt
                    pages.append(cur)
                    cur, used, p = [], 0.0, p + 1
                    continue
                cur.append(i)
                used += need + it["post"]
                i += 1
            if cur:
                pages.append(cur)
            return pages

        pages = pack(1.0)
        if len(pages) > 1:
            # 🚨 找「能塞進同樣頁數的最低填充率」要用二分搜尋，不能一格一格往上加。
            #    孤寡行與小標的回退每次會浪費一兩行，累積起來常讓理想填充率差一頁；
            #    舊版每次只加 4%，兩步就撞到 1.0 退回貪心，於是一篇的末頁又只剩
            #    十二行、前面每頁都三十三行（2026-09-12 稽核抓到三本各一頁）。
            floor = len(pages)
            total = sum(it["pre"] + it["h"] + it["post"] for it in items)
            room = first_avail + full_avail * (floor - 1)
            even = max(0.35, min(1.0, total / room))
            trial = pack(even)              # 理想填充率先試一次，塞得下就不必搜
            if len(trial) <= floor:
                pages = trial
            else:
                lo, hi = even, 1.0          # hi 已知可行（貪心就是 1.0）
                for _ in range(12):
                    mid = (lo + hi) / 2
                    t2 = pack(mid)
                    if len(t2) <= floor:
                        pages, hi = t2, mid
                    else:
                        lo = mid

        for pi, page_items in enumerate(pages):
            if pi:
                self.new_page()
            for idx in page_items:
                it = items[idx]
                self.y += it["pre"]
                self.draw(BODY_X0 + it["indent"], self.y, it["text"], it["size"], it["bold"])
                self.y += it["h"] + it["post"]

    # ── 結構 ────────────────────────────────────────────────────────
    def part_title(self, name: str, blurb: str) -> None:
        self.head_l = self.head_r = ""
        self.half_page = False          # 分部頁沒有東西要翻，不留譯文欄
        self.new_page()
        self.y = 230
        self.flow(name, size=17, gap=12)
        self.flow(blurb, size=10.2, color=(0.35,) * 3)
        self.marks.append([1, name, self.doc.page_count])

    def piece_title(self, week: str, author: str, title: str, source: str,
                    anchor: bool = True) -> None:
        # 眉標要在開頁「之前」設好：每一頁都得看得出這是第幾週的哪一篇，包含這一篇
        # 的首頁。先開頁再設，首頁就是空的——半本書的頁緣因此沒有字。
        self.head_l = week
        self.head_r = f"{author}, {title}" if author else title
        self.half_page = self.half_default   # 原文頁才留譯文欄
        self.new_page()
        label = (f"{author}, {title}" if author else title)[:88]
        if anchor:                      # 導引排在篇首時，錨點已經記在導引那一頁
            self.marks.append([1, label, self.doc.page_count])
            self.entries.append((week, label, self.doc.page_count))
        self.y = M_TOP + 8
        self.flow(week, size=9.6, gap=8, color=(0.4,) * 3)
        if author:
            self.flow(author.upper(), size=9.4, gap=2, bold=True)
        self.flow(title, size=14.2, gap=4, bold=True)
        if source:
            self.flow(source, size=9.0, gap=10, color=(0.35,) * 3)
        self.page.draw_line(fitz.Point(BODY_X0, self.y - 5), fitz.Point(BODY_X1, self.y - 5),
                            color=(0.75,) * 3, width=0.6)
        self.y += 8

    def endnotes(self, notes: list[str]) -> None:
        """篇末註。使用者要求：**要標明、要空行**，不能跟正文擠在一起。"""
        if not notes:
            return
        self.space(60)                      # 只剩幾行就別起頭，換頁再排
        self.y += 14
        self.page.draw_line(fitz.Point(BODY_X0, self.y - 6), fitz.Point(BODY_X0 + 120, self.y - 6),
                            color=(0.55,) * 3, width=0.7)
        self.y += 6
        self.flow("註（原書頁下註，依原書順序）", size=10.4, gap=8, color=(0.3,) * 3)
        # 不另外編號：原書的註號多半就在文字裡（「3. Ed. note. …」），再套一層
        # 我自己的序號會變成「7. 3. Ed. note.」。條與條之間空一行分開就夠。
        for n in notes:
            self.flow(n, size=9.2, gap=7, color=(0.2,) * 3, x0=BODY_X0 + 6)

    def guide_page(self, week: str, title: str, md: str, anchor: bool = False) -> None:
        """一篇的繁中閱讀導引，自成一頁。排在篇首時 `anchor=True`，書籤與目錄
        就指到這一頁（這一篇是從導引開始的）。"""
        self.head_l, self.head_r = week, "閱讀導引"
        self.half_page = False          # 導引本來就是中文，不留譯文欄
        self.new_page()
        if anchor:
            self.marks.append([1, title[:88], self.doc.page_count])
            self.entries.append((week, title[:88], self.doc.page_count))
        self.y = M_TOP + 6

        # 一篇的導引要**剛好一頁**：摘要、重點、可討論的問題三段一次看完，
        # 翻頁就失去它的用處（2026-09-10 使用者指出第三個問題老是掉到下一頁）。
        # 所以先量、再選一個放得下的縮放，不夠就縮字級與段距，不硬換頁。
        blocks = [("閱讀導引", 13.6, 4, BODY_X0, False),
                  (title, 9.2, 12, BODY_X0, False)]
        # 「可討論的問題」使用者說不用（問題他自己想），拿掉之後導引穩穩一頁。
        # 快取裡的舊導引還帶著那一段，所以在這裡截掉，不必重跑一輪 LLM。
        md = re.split(r"^##\s*可討論的問題", md, maxsplit=1, flags=re.M)[0]
        for ln in md.splitlines():
            ln = ln.strip()
            if not ln:
                blocks.append(("", 3.0, 0, BODY_X0, False))
            elif ln.startswith("## "):
                blocks.append(("", 6.0, 0, BODY_X0, False))
                blocks.append((ln[3:], 11.6, 5, BODY_X0, True))
            elif ln.startswith(("- ", "・")):
                blocks.append(("・" + ln.lstrip("-・ "), 10.4, 4, BODY_X0 + 8, False))
            elif re.match(r"^\d+[.\u3001]", ln):
                blocks.append((ln, 10.4, 4, BODY_X0 + 8, False))
            else:
                blocks.append((ln, 10.4, 5, BODY_X0, False))

        avail = (PH - M_BOT) - self.y
        scale, lf = 1.0, LEAD_FACTOR

        def height(try_scale: float, try_lf: float) -> float:
            h = 0.0
            for text, size, gap, bx0, bold in blocks:
                sz = size * try_scale
                if not text:
                    h += sz              # 空白區塊：本身就是間距
                    continue
                h += len(self.wrap(text, BODY_X1 - bx0, sz, bold)) * sz * try_lf
                h += gap * try_scale
            return h

        # 先縮字級，還塞不下就連行距一起縮。導引特別長的那幾篇（King 那篇的摘要
        # 就快兩頁）只縮字級救不回來，而導引**一定要一頁**才有用。
        for try_lf in (LEAD_FACTOR, LEAD_FACTOR * 0.86, LEAD_FACTOR * 0.75):
            for try_scale in (1.0, 0.96, 0.92, 0.88, 0.84, 0.8, 0.76, 0.72, 0.68, 0.64, 0.6):
                scale, lf = try_scale, try_lf
                if height(try_scale, try_lf) <= avail:
                    break
            else:
                continue
            break

        for text, size, gap, bx0, bold in blocks:
            if not text:
                self.y += size * scale
                continue
            grey = (0.4,) * 3 if text == title else (0.12,) * 3
            self.flow(text, size=size * scale, lead=size * scale * lf,
                      gap=gap * scale, bold=bold, x0=bx0,
                      color=(0, 0, 0) if bold else grey)




_DAY_ORDER = {"週一": 1, "週二": 2, "週三": 3, "週四": 4, "週五": 5, "週六": 6, "週日": 7}


def _week_key(entry) -> tuple:
    """把「週六 W04–W05」「週一 W06-08／週六 W14」這種標籤排成可比較的鍵。

    合本裡同一篇可能掛兩門課的週次，取最前面那個當排序依據。
    """
    week = entry[0]
    day = next((v for k, v in _DAY_ORDER.items() if k in week), 0)
    nums = re.findall(r"W(\d+)", week)
    return (day, int(nums[0]) if nums else 99)



def _rgb(hexstr: str) -> tuple[float, float, float]:
    return tuple(int(hexstr[i:i + 2], 16) / 255 for i in (0, 2, 4))


def draw_cover(bk: Book, meta: dict) -> None:
    """B5 封面：滿版深色橫幅＋一條亮色細線，橫幅裡是課名，下方是教師與學生。

    版式沿用原文讀本那一套（深色橫幅、白字、亮色細線），三本只換顏色，並排時
    看得出是一套。**封面上只有課程名稱、授課教師、學生姓名**，其他一律不放。
    橫幅是滿版出血，印的時候要選「實際大小」，縮放列印會留白邊。
    """
    banner = _rgb(meta.get("banner", "2C2A26"))
    rule = _rgb(meta.get("rule", "D4A653"))
    bk.new_page()
    page = bk.page
    page.draw_rect(fitz.Rect(0, 0, PW, 300), color=banner, fill=banner)
    page.draw_rect(fitz.Rect(0, 300, PW, 306), color=rule, fill=rule)

    # 課名長短差很多（六字到十二字），字級照寬度收，不讓它撞到版心邊
    size = 32.0
    while size > 18 and bk.measure(meta["title"], size) > BODY_X1 - BODY_X0:
        size -= 1.0
    bk.y = 150
    bk.draw(BODY_X0, bk.y, SEMESTER, 12, color=(0.86, 0.83, 0.78))
    bk.y = 196
    bk.draw(BODY_X0, bk.y, meta["title"], size, color=(1, 1, 1))
    if meta.get("volume"):
        bk.y = 232
        bk.draw(BODY_X0, bk.y, meta["volume"], 13, color=(0.88, 0.86, 0.82))

    bk.y = 400
    bk.draw(BODY_X0, bk.y, "授課教師", 11, color=(0.42,) * 3)
    bk.draw(BODY_X0 + 76, bk.y, meta["teacher"], 13, color=(0.13,) * 3)
    bk.y += 30
    bk.draw(BODY_X0, bk.y, "學　　生", 11, color=(0.42,) * 3)
    bk.draw(BODY_X0 + 76, bk.y, meta["student"], 13, color=(0.13,) * 3)


def cover_and_toc(lang: str, meta: dict, entries: list[tuple[str, str, int]]) -> Book:
    """做封面與目錄。

    🚨 目錄印的是**內文自己的頁碼**（正文第一頁是 1），不是 PDF 的絕對頁次。
    這兩個差了封面與目錄那幾頁：2026-09-10 之前印的是絕對頁次，於是目錄寫
    「6」的那一篇，翻到書上印著「2」的那一頁才是——整本目錄每一條都差 4，
    而書本身看起來完全正常（[[feedback_reader_silent_failures]]）。
    """
    bk = Book(lang=lang)
    draw_cover(bk, meta)

    bk.head_l, bk.head_r = "", ""
    bk.new_page()
    bk.y = M_TOP + 10
    bk.flow("目錄", size=18, gap=18)
    for week, label, page in entries:
        num = str(page)
        left = f"{week}　{label}"
        # 點線導引：先量左右兩端，中間用點填滿
        wl = bk.measure(left, 9.8)
        wr = bk.measure(num, 9.8)
        room = (BODY_X1 - BODY_X0) - wl - wr - 6
        dots = ""
        while bk.measure(dots + "·", 9.8) < room:
            dots += "·"
        bk.space(9.8 * LEAD_FACTOR)
        x = bk.draw(BODY_X0, bk.y, left, 9.8)
        bk.draw(x + 3, bk.y, dots, 9.8, color=(0.72,) * 3)
        bk.draw(BODY_X1 - wr, bk.y, num, 9.8)
        bk.y += 9.8 * LEAD_FACTOR

    # 週次一覽拿掉了。拆成一課一本之後，目錄每一行左邊本來就標著週次，再排一份
    # 按週次排序的清單就是第二份一模一樣的目錄（使用者 2026-09-10 退掉）。
    return bk


def stamp_numbers(doc: fitz.Document, first: int, cjk_path: str) -> None:
    """合併之後統一蓋頁碼——封面與目錄不蓋，正文從 1 開始。"""
    for i in range(first, doc.page_count):
        page = doc[i]
        page.insert_font(fontname="TNR", fontfile=LATIN)
        num = str(i - first + 1)
        w = _F_REG.text_length(num, 8.8)
        page.insert_text((PW / 2 - w / 2, PH - 32), num,
                         fontname="TNR", fontsize=8.8, color=(0.4,) * 3)


# ── 閱讀導引（LLM）──────────────────────────────────────────────────────
PROMPT = """你是宗教學研究所的助教。下面是一篇課堂指定讀物的全文（掃描 OCR，可能有錯字，請自行判讀）。
請用**繁體中文**寫一頁閱讀導引，嚴格照以下格式輸出，不要有任何其他文字、不要用 markdown 粗體。

🚨 **全篇必須是完整的繁體中文句子，不可中英夾雜**。不要寫「殖民 discourse」
「ontological 存在」這種半句英文——每個詞都要譯成中文。學術術語第一次出現時
寫成「中文（English）」，之後只用中文。人名地名一律用通行中譯。

## 摘要
（250 到 350 字。說明這篇在處理什麼問題、採取什麼路線、結論是什麼。不要抄開頭，要自己歸納。）

## 重點
- （五條，每條一句話，扣緊論證步驟，不要寫成內容大綱）

只要這兩段，**不要**寫「可討論的問題」——問題使用者自己想（2026-09-10 定案）。

篇名：{title}
出處：{source}

全文：
{body}
"""


# 🚨 Gemini 免費層是「每型號各自」每天每把 key 幾次，所以某一型號 429 不代表
#    Gemini 掛了，換個型號多半就通。2026-09-08 實測 gemini-2.5-flash 七把 key
#    全 429，但 3-flash-preview 與 2.5-flash-lite 都是一兩秒回。
#    同日 gemini-2.5-flash 對這批 key 已改回 404（型號下架），所以型號鏈裡
#    不要放它——先驗模型名還在不在，再怪額度。
GUIDE_MODELS = ["gemini-3-flash-preview", "gemini-2.5-flash-lite", "gemini-flash-latest"]


# 🚨 導引會被模型的自言自語污染：King 那兩篇的快取裡存的是
#    「We must not use markdown bold. Use hyphen and space?…」這種思考過程，
#    4,800～6,800 字，印出來就是導引跨兩頁、第二頁全是廢話。長度與這些字眼
#    一起當閘門，**快取讀出來也要驗**——壞的快取不驗就等於永遠壞下去。
GUIDE_META = ("markdown", "We must", "Use hyphen", "I need to", "Let me ",
              "as an AI", "字數要求", "格式要求")


def guide_ok(text: str) -> bool:
    return bool(text) and 300 <= len(text) <= 1800 and not any(m in text for m in GUIDE_META)


def make_guide(title: str, source: str, body: str) -> str | None:
    text = body[:30000]   # 摘要用不到全文，砍半可以把每篇的等待時間縮短一半
    prompt = PROMPT.format(title=title, source=source, body=text)
    try:
        import qianmian_llm
        for model in GUIDE_MODELS:
            try:
                out, _ = qianmian_llm.ask(prompt, model=model,
                                          temperature=0.4, max_tokens=8000, tries=3)
            except Exception as e:
                print(f"    · {model} 不通（{str(e)[-24:]}）")
                continue
            # 🚨 這裡有兩種會「看起來成功」的失敗，兩種都要擋：
            #    短的＝被截斷（thinking 吃光輸出額度），三段只出了一段；
            #    長的＝跑掉格式，把全文逐段翻譯或逐節註解都倒出來，塞爆那一頁。
            #    導引本來就設計成一頁，超出 2000 字必然不是導引。
            if out:
                full = all(h in out for h in ("## 摘要", "## 重點"))
                if full and guide_ok(out):
                    return out.strip()
                why = "缺段" if not full else ("太短" if len(out) < 350 else "暴長")
                print(f"    · {model} {why}（{len(out)} 字），換型號")
    except Exception as e:
        print(f"    · Gemini 整層失敗（{type(e).__name__}），改走 NVIDIA")
    try:
        import translate_ebook_to_zh as engines
        out = engines.nvidia_chat(prompt, max_tokens=2400)
        if out and "## 摘要" in out:
            return out.strip()
    except Exception as e:
        print(f"    · NVIDIA 也失敗（{type(e).__name__}）")
    return None


# reader 代號 → (章節結構, 成品要放進哪幾門課的資料夾, 語言, 檔名)
# 週一那本 754 頁、B5 雙面約 377 張、厚 3.8 公分，膠裝勉強而且每週要背著跑，
# 所以 2026-09-10 使用者定案**分上下冊**，切在期中考前後：
# 上冊 W02–W08（前三部）、下冊 W10–W17（後三部）。
MON1_PARTS = MON_PARTS[:3]
MON2_PARTS = MON_PARTS[3:]

READERS = {
    # 🚨 沒有未分冊的 "mon"：731 頁太厚，2026-09-11 使用者定案只出上下冊、
    #    合併那本刪掉。MON_PARTS 留著當上下冊的來源。
    "mon1": (MON1_PARTS, [C_MON], "zh", "宗教研究方法讀本_上冊"),
    "mon2": (MON2_PARTS, [C_MON], "zh", "宗教研究方法讀本_下冊"),
    "sat": (SAT_PARTS, [C_SAT], "zh", "宗教學理論讀本"),
    "japanese": (JAPANESE_PARTS, [C_JPN], "ja", "初階日文讀本"),
}


def load_cache(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8")) if os.path.exists(path) else {}


# ── 組本 ────────────────────────────────────────────────────────────────
def build(reader: str, mode: str, only: int | None, want_guide: bool,
          out: str = "") -> None:
    parts, courses, lang, stem = READERS[reader]
    # 成品就放那門課的資料夾本身，不另開子夾；`--out` 可以改放到別處
    # （雲端硬碟沒掛載時先出到本機，掛回來再放回課程資料夾）。
    out_dirs = [out] if out else [os.path.join(BASE, c) for c in courses]
    for d in out_dirs:
        os.makedirs(d, exist_ok=True)
    # 快取是中繼不是成品，留在 repo 的 output/（不進版控），不要擺到 Drive 課程夾裡
    cache_dir = os.path.join(ROOT_REPO, "output", "source-cache", "course-readers")
    os.makedirs(cache_dir, exist_ok=True)
    # 閱讀導引的快取鍵是「檔名＋內文雜湊」，跟哪一本讀本無關。週一與週六本來
    # 是一本（marcus），拆本後兩邊共用同一份快取，不要為了改代號重跑一輪 LLM。
    cache_path = os.path.join(
        cache_dir, f"{'marcus' if reader in ('mon', 'sat') else reader}-guides.json")
    cache = load_cache(cache_path)

    files = index_pdfs(courses)
    use = [parts[only - 1]] if only else parts
    missing: list[str] = []

    if mode == "facsimile":
        doc, marks = fitz.open(), []
        for name, _, items in use:
            marks.append([1, name, doc.page_count + 1])
            for key, weeks in items:
                path = locate(files, key)
                if not path or not path.lower().endswith(".pdf"):
                    missing.append(key)
                    continue
                author, title, _ = title_of_pdf(path)
                marks.append([2, f"{author}, {title}"[:88], doc.page_count + 1])
                with fitz.open(path) as src:
                    doc.insert_pdf(src)
        for i, page in enumerate(doc):
            page.insert_text((page.rect.width / 2 - 8, page.rect.height - 24), str(i + 1),
                             fontname="helv", fontsize=8.6, color=(0.4,) * 3)
        doc.set_toc(marks)
        for d in out_dirs:
            dst = os.path.join(d, f"{stem}_影印合本.pdf")
            doc.save(dst, deflate=True)
            print(f"✓ {dst}　{doc.page_count} 頁")
        return

    bk = Book(lang=lang, half_page=(reader == "japanese"))
    cut_total = 0
    # 分部頁拿掉了（使用者 2026-09-10：「不需要幫我分第一部第二部，盡量減少頁數」）。
    # 結構表留著，它決定收錄順序。
    for name, blurb, items in use:
        for key, weeks in items:
            path = locate(files, key)
            if not path:
                missing.append(key)
                continue

            # 先把內容取出來（還不畫），因為閱讀導引排在篇首、而導引是從內文產的
            if path.lower().endswith(".pdf"):
                author, title, tag = title_of_pdf(path)
                source = full_source(tag)
                raw_paras, notes = extract_pdf(path)
                raw_paras, spaced = repair_spacing(raw_paras)
                raw_paras, badhead = drop_bad_headings(raw_paras)
                raw_paras, intro_cut = cut_editor_intro(raw_paras)
                paras, cut = cut_bibliography(raw_paras)
                cut_total += cut
                body = "\n\n".join(t for _, t in paras)
                disp = f"{author}, {title}"
                meta = None
                note_n = len(notes)
            else:
                meta, paras = extract_md(path)
                author = ""
                title = meta.get("_h1") or meta.get("作品", os.path.basename(path))
                # 🚨 出處由下面那段連同「節錄」一起印，這裡留空；兩邊都印會在
                #    篇首連出兩行一模一樣的出處（使用者 2026-09-12 指出）。
                source = ""
                origin = f"{meta.get('初出', '')}／{meta.get('電子文本', '')}"
                body = "\n\n".join(paras)
                disp = title
                cut = intro_cut = spaced = badhead = 0
                notes, note_n = [], 0

            # 🚨 快取的鍵不能只用檔名。讀本的節錄範圍一改，檔名沒變但內容變了，
            #    用檔名當鍵就會配上一份講的是別段文字的導引——看起來完全正常。
            key_id = f"{os.path.basename(path)}#{hashlib.sha1(body.encode()).hexdigest()[:10]}"
            guide = ""
            if want_guide:
                # 內容沒變就別重跑 LLM。兩種舊鍵都認：最早只有檔名，後來是
                # 檔名＋雜湊——砍掉篇末書目會讓雜湊變，但導引講的是同一篇文章，
                # 沒必要為了少一份參考書目再燒一輪額度。
                if key_id not in cache:
                    legacy = next((k for k in (os.path.basename(path),) if k in cache), None) or \
                             next((k for k in cache if k.split("#")[0] == os.path.basename(path)), None)
                    if legacy:
                        cache[key_id] = cache[legacy]
                if key_id not in cache:
                    print(f"    · 產生閱讀導引：{disp[:44]}")
                    g = make_guide(disp, source, body)
                    if g:
                        cache[key_id] = g
                        Path(cache_path).write_text(
                            json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
                guide = cache.get(key_id, "")
                if guide and not guide_ok(guide):     # 壞快取當作沒有，重生一次
                    print(f"    · 快取的導引不合格（{len(guide)} 字），重生")
                    cache.pop(key_id, None)
                    guide = make_guide(disp, source, body) or ""
                    if guide_ok(guide):
                        cache[key_id] = guide
                        Path(cache_path).write_text(
                            json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
                    else:
                        guide = ""

            # 導引排在**篇首**：一翻到這一篇就先看得到摘要與重點，讀完再進正文。
            # （2026-09-10 之前排在篇末，使用者翻了十九頁沒看到，以為沒做。）
            if guide:
                bk.guide_page(f"{weeks}", disp, guide, anchor=True)
                bk.piece_title(f"{weeks}", author, title, source, anchor=False)
            else:
                bk.piece_title(f"{weeks}", author, title, source)

            if meta is None:
                # 課綱跳頁的那幾篇，篇末加一行說明為什麼沒講完。
                # 🚨 要**併進同一個 flow**，不能排完正文再單獨 flow 一次：正文剛好
                #    填滿末頁時，那一行就自己占掉一整頁（下冊多出一頁只有五行的
                #    145 頁，2026-09-12 稽核抓到）。
                bk.flow_paragraphs(
                    paras + ([("p", RANGE_NOTE[key])] if key in RANGE_NOTE else []),
                    size=FS, gap=6.0, indent=INDENT)
                # 註釋整批不印（2026-09-10 使用者定案）。重排之後正文裡的上標
                # 註號已經沒了，沒有錨點的篇末註等於廢紙；要查註回頭看 Drive
                # 上那份原始切片。抽出來的用途只剩一個：不讓它混進正文。
            else:
                bk.flow(f"出處：{origin}", size=9.0, gap=8, color=(0.35,) * 3)
                bk.flow(f"節錄：{meta.get('節錄範圍', '')}　實質 {meta.get('實質字數', '?')}",
                        size=9.0, gap=10, color=(0.35,) * 3)
                bk.flow_paragraphs([("p", re.sub(r"\*\*(\d+)\*\*　", r"\1　", t)) for t in paras],
                                   size=11.2, gap=8, indent=INDENT)
            print(f"  ✓ {disp[:52]}"
                  + (f"（接回散字 {spaced} 處）" if spaced else "")
                  + (f"（剔掉假小標 {badhead} 條）" if badhead else "")
                  + (f"（砍編者導言 {intro_cut} 段）" if intro_cut else "")
                  + (f"（砍書目 {cut} 段）" if cut else "")
                  + (f"（濾掉註 {note_n} 條）" if note_n else ""))

    if cut_total:
        print(f"\n篇末書目共砍掉 {cut_total} 段")

    front = cover_and_toc(lang, COVER[reader], bk.entries)

    book = fitz.open()
    book.insert_pdf(front.doc)
    book.insert_pdf(bk.doc)
    stamp_numbers(book, front.doc.page_count, bk.cjk_path)
    book.set_toc([[lvl, t, p + front.doc.page_count] for lvl, t, p in bk.marks])

    for d in out_dirs:
        dst = os.path.join(d, f"{stem}.pdf")
        book.save(dst, deflate=True)
        print(f"✓ {dst}　{book.page_count} 頁（封面目錄 {front.doc.page_count} 頁）")
    for k in missing:
        print(f"✗ 找不到：{k}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reader", choices=list(READERS), default="mon1")
    ap.add_argument("--mode", choices=["reflow", "facsimile"], default="reflow")
    ap.add_argument("--only", type=int, help="只出第 N 部（試版面用）")
    ap.add_argument("--no-summary", action="store_true", help="先不叫 LLM 產閱讀導引")
    ap.add_argument("--out", default="", help="成品改放這個資料夾（預設放該門課的 Drive 資料夾）")
    a = ap.parse_args()
    build(a.reader, a.mode, a.only, not a.no_summary, a.out)


if __name__ == "__main__":
    main()
