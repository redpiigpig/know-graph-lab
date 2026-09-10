# -*- coding: utf-8 -*-
"""把一門課的指定讀物排成一本 B5 讀本。

三本，一門課一本（2026-09-10 之前週一與週六是合成一本 877 頁的，使用者定案拆開）：

  `--reader mon`  《宗教研究基本問題與研究方法》週一第 2 節 博1A．32 篇
  `--reader sat`  《宗教學理論與方法（一）》單週六第 1 節 碩專1A．7 篇
  `--reader japanese` 《初階宗教學日文文獻選讀》週二第 1 節 碩1A．12 篇，
      內容是自訂十五週計畫的各週讀本，見 japanese_self_study_plan.py。

MacIntyre 與 Segal〈In Defense of Reductionism〉兩門課都指定，**兩本各收一份**。

版面（使用者定案）：**JIS B5（18.2×25.7cm）**、正文滿版、**行距 1.5 倍**
（＝字級的 1.8 倍行高，筆記寫在行間，不另闢筆記欄）、頁眉印「週次．篇名」、
頁碼在下。每篇正文之後附一頁**繁中閱讀導引**（摘要／重點／可討論的問題），
由 LLM 產生後快取，不會每次重跑重花額度。封面是滿版深色橫幅一課一色，
**上面只有課程名稱、學期、授課教師、學生姓名**。成品直接放該門課的資料夾（`--out` 可改）。

    python -X utf8 scripts/build_course_reader.py --reader mon
    python -X utf8 scripts/build_course_reader.py --reader sat
    python -X utf8 scripts/build_course_reader.py --reader japanese
    python -X utf8 scripts/build_course_reader.py --reader sat --only 2   # 只出第 2 部，試版面
    python -X utf8 scripts/build_course_reader.py --reader mon --no-summary  # 先不叫 LLM
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
    "mon": dict(title="宗教研究基本問題與研究方法", teacher="根瑟馬庫斯",
                student="張辰瑋", banner="1E3A5F", rule="C8A24A"),      # 深藍
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


def page_paragraphs(page: fitz.Page) -> list[str]:
    h = page.rect.height
    top_cut, bot_cut = h * 0.06, h * 0.94
    out = []
    for b in page.get_text("blocks"):
        y0, x0, y1, txt = b[1], b[0], b[3], b[4]
        if txt.strip() and not (y1 < top_cut or y0 > bot_cut):
            out.append((round(y0, 1), x0, txt))
    out.sort(key=lambda t: (t[0], t[1]))
    return [t[2] for t in out]


def clean(text: str) -> str:
    text = re.sub(r"([a-z])-\s*\n\s*([a-z])", r"\1\2", text)   # 行末斷字，只接小寫
    text = re.sub(r"([a-z])-\s+([a-z])", r"\1\2", text)
    text = text.replace("\n", " ")
    for pat, rep in SPLIT_FIX:
        text = re.sub(pat, rep, text)
    return re.sub(r"\s+", " ", text).strip()


def extract_pdf(path: str) -> list[str]:
    doc = fitz.open(path)
    paras: list[str] = []
    for page in doc:
        for raw in page_paragraphs(page):
            t = clean(raw)
            if len(t) < 3:
                continue
            # 前一塊沒收尾 → 多半是同一段被跨欄跨頁切開了。但小標題也沒有句末
            # 標點（「“Religion” as Specter」），所以再看長度：夠長才是被切斷的
            # 正文，短的當標題，不接。
            prev = paras[-1] if paras else ""
            cont = bool(prev) and not prev.endswith(SENT_END) and (
                len(prev) > 60 or t[:1].islower() or re.match(r"^\d+[).,]", t))
            if cont:
                paras[-1] += " " + t
            else:
                paras.append(t)
    doc.close()
    return paras


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
        # 半頁模式：正文只排到頁面中線，下半頁留白給使用者寫翻譯
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

    def wrap(self, text: str, width: float, size: float, bold: bool = False) -> list[str]:
        lines, line = [], ""
        for tok in self._tokens(text):
            trial = line + tok
            if line and self.measure(trial, size, bold) > width:
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
             x1: float = BODY_X1, color=(0, 0, 0)) -> None:
        lead = size * LEAD_FACTOR if lead is None else lead
        if not text.strip():          # 空行就只是空一行
            self.space(lead)
            self.y += lead
            return
        for ln in self.wrap(text, x1 - x0, size, bold):
            self.space(lead)
            self.draw(x0, self.y, ln, size, bold, color)
            self.y += lead
        self.y += gap

    # ── 結構 ────────────────────────────────────────────────────────
    def part_title(self, name: str, blurb: str) -> None:
        self.head_l = self.head_r = ""
        self.new_page()
        self.y = 230
        self.flow(name, size=17, gap=12)
        self.flow(blurb, size=10.2, color=(0.35,) * 3)
        self.marks.append([1, name, self.doc.page_count])

    def piece_title(self, week: str, author: str, title: str, source: str) -> None:
        # 眉標要在開頁「之前」設好：每一頁都得看得出這是第幾週的哪一篇，包含這一篇
        # 的首頁。先開頁再設，首頁就是空的——半本書的頁緣因此沒有字。
        self.head_l = week
        self.head_r = f"{author}, {title}" if author else title
        self.new_page()
        label = (f"{author}, {title}" if author else title)[:88]
        self.marks.append([2, label, self.doc.page_count])
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

    def guide_page(self, week: str, title: str, md: str) -> None:
        """一篇的繁中閱讀導引，自成一頁。"""
        self.head_l, self.head_r = week, "閱讀導引"
        self.new_page()
        self.y = M_TOP + 6
        self.flow("閱讀導引", size=13.6, gap=4)
        self.flow(title, size=9.2, gap=12, color=(0.4,) * 3)
        for ln in md.splitlines():
            ln = ln.strip()
            if not ln:
                self.y += 3
            elif ln.startswith("## "):
                self.y += 6
                self.flow(ln[3:], size=11.6, gap=5, bold=True)
            elif ln.startswith(("- ", "・")):
                self.flow("・" + ln.lstrip("-・ "), size=10.4, gap=4,
                          x0=BODY_X0 + 8)
            elif re.match(r"^\d+[.\u3001]", ln):
                self.flow(ln, size=10.4, gap=4, x0=BODY_X0 + 8)
            else:
                self.flow(ln, size=10.4, gap=5)




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

    # 目錄照書的順序（分部），頁碼才會遞增；但要回答「第幾週讀什麼」得另外
    # 按週次排一份。兩份都要，各自解決一個問題。
    bk.y += 18
    bk.flow("週次一覽", size=13, gap=10)
    for week, label, page in sorted(entries, key=_week_key):
        num = str(page)
        left = f"{week}　{label}"
        wl, wr = bk.measure(left, 9.4), bk.measure(num, 9.4)
        room = (BODY_X1 - BODY_X0) - wl - wr - 6
        dots = ""
        while bk.measure(dots + "·", 9.4) < room:
            dots += "·"
        bk.space(9.4 * LEAD_FACTOR)
        x = bk.draw(BODY_X0, bk.y, left, 9.4)
        bk.draw(x + 3, bk.y, dots, 9.4, color=(0.72,) * 3)
        bk.draw(BODY_X1 - wr, bk.y, num, 9.4)
        bk.y += 9.4 * LEAD_FACTOR
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

## 可討論的問題
1. （三題。要能在課堂上引起爭辯，不要是查得到答案的事實題。）

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
                full = all(h in out for h in ("## 摘要", "## 重點", "## 可討論的問題"))
                if full and 350 <= len(out) <= 2000:
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
READERS = {
    "mon": (MON_PARTS, [C_MON], "zh", "宗教研究方法讀本"),
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
    for name, blurb, items in use:
        bk.part_title(name, blurb)
        for key, weeks in items:
            path = locate(files, key)
            if not path:
                missing.append(key)
                continue
            if path.lower().endswith(".pdf"):
                author, title, source = title_of_pdf(path)
                paras = extract_pdf(path)
                bk.piece_title(f"{weeks}", author, title, source)
                for p in paras:
                    bk.flow(p)
                body = "\n\n".join(paras)
                disp = f"{author}, {title}"
            else:
                meta, paras = extract_md(path)
                title = meta.get("_h1") or meta.get("作品", os.path.basename(path))
                source = f"{meta.get('初出', '')}／{meta.get('電子文本', '')}"
                bk.piece_title(f"{weeks}", "", title, "")
                bk.flow(f"出處：{source}", size=9.0, gap=8, color=(0.35,) * 3)
                bk.flow(f"節錄：{meta.get('節錄範圍', '')}　實質 {meta.get('實質字數', '?')}",
                       size=9.0, gap=10, color=(0.35,) * 3)
                for p in paras:
                    bk.flow(re.sub(r"\*\*(\d+)\*\*　", r"\1　", p), size=11.2, gap=8)
                body = "\n\n".join(paras)
                disp = title

            # 🚨 快取的鍵不能只用檔名。讀本的節錄範圍一改，檔名沒變但內容變了，
            #    用檔名當鍵就會配上一份講的是別段文字的導引——看起來完全正常。
            key_id = f"{os.path.basename(path)}#{hashlib.sha1(body.encode()).hexdigest()[:10]}"
            if want_guide:
                # 舊版的鍵只有檔名。內容沒變的話沒必要重跑一輪 LLM，
                # 沿用舊值並就地改成新鍵。
                legacy = os.path.basename(path)
                if key_id not in cache and legacy in cache:
                    cache[key_id] = cache.pop(legacy)
                if key_id not in cache:
                    print(f"    · 產生閱讀導引：{disp[:44]}")
                    g = make_guide(disp, source, body)
                    if g:
                        cache[key_id] = g
                        Path(cache_path).write_text(
                            json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
                if cache.get(key_id):
                    bk.guide_page(f"{weeks}", disp, cache[key_id])
            print(f"  ✓ {disp[:52]}")

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
    ap.add_argument("--reader", choices=["mon", "sat", "japanese"], default="mon")
    ap.add_argument("--mode", choices=["reflow", "facsimile"], default="reflow")
    ap.add_argument("--only", type=int, help="只出第 N 部（試版面用）")
    ap.add_argument("--no-summary", action="store_true", help="先不叫 LLM 產閱讀導引")
    ap.add_argument("--out", default="", help="成品改放這個資料夾（預設放該門課的 Drive 資料夾）")
    a = ap.parse_args()
    build(a.reader, a.mode, a.only, not a.no_summary, a.out)


if __name__ == "__main__":
    main()
