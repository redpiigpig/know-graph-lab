# -*- coding: utf-8 -*-
"""把一門課的指定讀物排成一本 B5 讀本。

三本，一門課一本（2026-09-10 之前週一與週六是合成一本 877 頁的，使用者定案拆開）：

  `--reader mon1` / `mon2`  《宗教研究基本問題與研究方法》週一第 2 節 博1A．
      上冊 W02–W08（14 篇）、下冊 W10–W17（18 篇）。合併那本（731 頁）已作廢。
  `--reader sat`  《宗教學理論與方法（一）》單週六第 1 節 碩專1A．7 篇
  `--reader japanese` 《初階宗教學日文文獻選讀》週二第 1 節 碩1A．12 篇，
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

JAPANESE_PARTS = [
    ("第一部　現代日文：矢內原忠雄", "戰後刊行，新字新假名，「である」體——無教會第二代裡最接近現代日文的人。", [
        ("W03_自訂_矢內原忠雄_キリスト教入門_序", "W03"),
        ("W04_自訂_矢內原忠雄_キリスト教入門_第一章上", "W04"),
        ("W05_自訂_矢內原忠雄_キリスト教入門_第一章下", "W05"),
        ("W07_自訂_矢內原忠雄_キリスト教入門_第二章", "W07"),
    ]),
    ("第二部　文語入門：文語訳聖書", "全文附振假名，漢字讀音不必查；經文內容本來就熟，是最省力的文語入口。", [
        ("W06_自訂_文語訳_マタイ伝五章_八福", "W06"),
        ("W08_自訂_文語訳_マタイ伝六章_主の祈り", "W08"),
    ]),
    ("第三部　講演體：內村鑑三", "「〜であります」的演說口語，是內村最好讀的一批文字。", [
        ("W10_自訂_內村鑑三_デンマルク国の話_導入", "W10"),
        ("W11_自訂_內村鑑三_デンマルク国の話_結論", "W11"),
    ]),
    ("第四部　論說：矢內原忠雄〈帝大聖書研究会終講の辞〉", "1937 年被迫辭去東大教職前後的一篇，無教會史上的關鍵文獻。", [
        ("W12_自訂_矢內原忠雄_帝大聖書研究会終講の辞_上", "W12"),
        ("W13_自訂_矢內原忠雄_帝大聖書研究会終講の辞_下", "W13"),
    ]),
    ("第五部　同一作者的兩種文體", "《後世への最大遺物》的序是文語、講演本體是口語，並排讀就看得出分界線。", [
        ("W14_自訂_內村鑑三_後世への最大遺物_序_文語", "W14"),
        ("W14_自訂_內村鑑三_後世への最大遺物_講演冒頭_口語", "W14"),
    ]),
]

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


def page_paragraphs(page: fitz.Page, body_size: float | None = None) -> tuple[list[str], list[str]]:
    """回傳 (正文段落, 註腳段落)。

    註腳原本混在正文流裡——Waardenburg 選集那幾篇的頁底註就這樣夾進段落中間，
    印出來是「…finite being and infinite mystery.³² Friedrich von Hügel, ‘The three
    elements of religion’…」，句子被一條書目切斷（使用者 2026-09-10 指出）。

    認法：**字級明顯比本文小**（≥1pt）且在版心下半。位置不能單獨當判準（康德那篇
    有整頁都是譯者註），字級也不能單獨當判準（頁眉頁碼也比較小）。

    🚨 `body_size` 要用**整篇**的本文字級，不能用單頁的：康德那篇的譯者註自成一頁，
    用單頁字級去比，那一頁的註就是「本文」，一條都認不出來。
    """
    h = page.rect.height
    top_cut, bot_cut = h * 0.06, h * 0.94
    if body_size is None:
        body_size = _dominant(_size_tally(page))
    body, notes = [], []
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
        x0, y0, _, y1 = blk["bbox"]
        if y1 < top_cut or y0 > bot_cut:
            continue
        size = max(sp["size"] for ln in lines for sp in ln["spans"])
        letters = [c for c in txt if c.isalpha()]
        shouty = letters and sum(c.isupper() for c in letters) / len(letters) > 0.7
        is_note = (body_size is not None and size <= body_size - 1.0
                   and y0 / h > 0.10 and not (shouty and len(txt) < 90))
        (notes if is_note else body).append((round(y0, 1), x0, txt))
    body.sort(key=lambda t: (t[0], t[1]))
    notes.sort(key=lambda t: (t[0], t[1]))
    return [t[2] for t in body], [t[2] for t in notes]


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


def split_heading(text: str) -> list[tuple[str, str]]:
    """一段 → [(kind, text)]，kind 是 'h'（小標）或 'p'（正文）。"""
    t = text.strip()
    letters = [c for c in t if c.isalpha()]
    if letters and len(t) < 90 and sum(c.isupper() for c in letters) / len(letters) > 0.8:
        return [("h", t.rstrip(".:"))]        # 整段就是小標
    m = HEAD_RUN.match(t)
    if m and len(m.group(1).split()) >= 2 and len(t) - m.end() > 40:
        return [("h", m.group(1).strip().rstrip(".:")), ("p", t[m.end():].lstrip())]
    return [("p", t)]


def extract_pdf(path: str) -> tuple[list[tuple[str, str]], list[str]]:
    """回傳 (正文段落, 註腳)。註腳另外收，排在篇末，不再插進正文流。"""
    doc = fitz.open(path)
    tally: dict[float, int] = {}
    for page in doc:
        for k, v in _size_tally(page).items():
            tally[k] = tally.get(k, 0) + v
    body_size = _dominant(tally)

    pages = [page_paragraphs(page, body_size) for page in doc]

    # 🚨 頁眉頁腳不能只靠邊界座標濾。《宗教百科全書》那一篇的頁眉離頂端超過 6%，
    #    於是「STUDY OF RELIGION: AN OVERVIEW 8766」每一頁都被當成正文收進去，
    #    還被接到下一段的句首（使用者 2026-09-10 指出）。改用**跨頁重複**認：
    #    把每頁最上與最下那一塊抽出來、去掉數字，重複到一半以上頁數的就是頁眉頁腳。
    def _head_key(t: str) -> str:
        return re.sub(r"\d+", "", clean(t)).strip().lower()[:60]

    seen: dict[str, int] = {}
    for body_blocks, _ in pages:
        for cand in ({body_blocks[0]} if body_blocks else set()) | (
                {body_blocks[-1]} if len(body_blocks) > 1 else set()):
            k = _head_key(cand)
            if 0 < len(k) < 60:
                seen[k] = seen.get(k, 0) + 1
    threshold = max(3, int(len(pages) * 0.5))
    running = {k for k, v in seen.items() if v >= threshold}

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

    paras: list[tuple[str, str]] = []
    notes: list[str] = []
    dropped_pua = 0
    for body_blocks, note_blocks in pages:
        body_blocks = [b for b in body_blocks if _head_key(b) not in running]
        body_blocks = [_strip_head(b) for b in body_blocks]
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
        for raw in body_blocks:
            if pua_ratio(raw) > 0.12:
                dropped_pua += 1
                continue
            t = clean(raw)
            if len(t) < 3:
                continue
            # 前一塊沒收尾 → 多半是同一段被跨欄跨頁切開了。但小標題也沒有句末
            # 標點（「“Religion” as Specter」），所以再看長度：夠長才是被切斷的
            # 正文，短的當標題，不接。
            prev = paras[-1][1] if paras else ""
            cont = (bool(prev) and paras[-1][0] == "p" and not prev.endswith(SENT_END)
                    and (len(prev) > 60 or t[:1].islower() or re.match(r"^\d+[).,]", t)))
            if cont:
                paras[-1] = ("p", prev + " " + t)
            else:
                paras.extend(split_heading(t))
    doc.close()
    if dropped_pua:
        print(f"    · 丟掉 {dropped_pua} 段壞字元（來源字型把數字對到私用區）")
    return paras, notes


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
        卻塞了十三行（使用者 2026-09-10 指出）。所以先算這篇需要幾頁，再把總高
        除以頁數當每頁的預算，各頁的份量就接近。

        順帶擋掉孤行寡行：一段只剩一行落到下一頁、或一頁只放得下這段的第一行，
        都往下一頁挪。
        """
        if not paras:
            return
        lead = size * LEAD_FACTOR
        blocks = [(kind, self.wrap(t, BODY_X1 - BODY_X0, size, kind == "h",
                                   first_indent=0 if kind == "h" else indent))
                  for kind, t in paras]
        h_total = sum(len(b) * lead + gap + (8 if k == "h" else 0) for k, b in blocks)
        if self.page is None:
            self.new_page()
        first_avail = self.bottom - self.y
        full_avail = max(self.bottom - M_TOP, lead * 2)
        pages = 1 if h_total <= first_avail else \
            1 + int(-(-(h_total - first_avail) // full_avail))
        # 每頁預算：把「總高＋第一頁少掉的那塊」攤平，上限是滿頁
        budget = min(full_avail, (h_total + (full_avail - first_avail)) / pages)
        page_top = self.y - (full_avail - first_avail)      # 第一頁的虛擬起點

        for kind, lines in blocks:
            if kind == "h":
                self.y += 8                      # 小標前多空一點，看得出分段
            n, i = len(lines), 0
            while i < n:
                room = int(min(self.bottom - self.y, page_top + budget - self.y) // lead)
                if room <= 0:
                    self.new_page()
                    page_top = self.y
                    continue
                take = min(room, n - i)   # room 可能比剩下的行還多
                if n - i > take:
                    if take < 2:                  # 這頁只塞得下一行 → 整段挪下一頁
                        self.new_page()
                        page_top = self.y
                        continue
                    if n - i - take == 1:         # 別讓最後一行孤零零落到下一頁
                        take -= 1
                for k in range(take):
                    off = 0 if kind == "h" else (indent if i + k == 0 else 0)
                    self.draw(BODY_X0 + off, self.y, lines[i + k], size, kind == "h")
                    self.y += lead
                i += take
                if i < n:
                    self.new_page()
                    page_top = self.y
            self.y += gap

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
                author, title, source = title_of_pdf(path)
                raw_paras, notes = extract_pdf(path)
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
                source = f"{meta.get('初出', '')}／{meta.get('電子文本', '')}"
                body = "\n\n".join(paras)
                disp = title
                cut = intro_cut = 0
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
                bk.flow_paragraphs(paras, size=FS, gap=6.0, indent=INDENT)
                # 註釋整批不印（2026-09-10 使用者定案）。重排之後正文裡的上標
                # 註號已經沒了，沒有錨點的篇末註等於廢紙；要查註回頭看 Drive
                # 上那份原始切片。抽出來的用途只剩一個：不讓它混進正文。
            else:
                bk.flow(f"出處：{source}", size=9.0, gap=8, color=(0.35,) * 3)
                bk.flow(f"節錄：{meta.get('節錄範圍', '')}　實質 {meta.get('實質字數', '?')}",
                        size=9.0, gap=10, color=(0.35,) * 3)
                bk.flow_paragraphs([("p", re.sub(r"\*\*(\d+)\*\*　", r"\1　", t)) for t in paras],
                                   size=11.2, gap=8, indent=INDENT)
            print(f"  ✓ {disp[:52]}"
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
