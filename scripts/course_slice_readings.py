# -*- coding: utf-8 -*-
"""115-1 四門課的每週資料夾與指定讀物。

三件事：

  1. 依課程大綱建每一堂的資料夾（`W01 主題/`），並在每夾寫 `指定閱讀.md`；
  2. 整本 PDF → 各週資料夾裡的單篇 PDF；
  3. 開放取用的網路讀物抓下來存成 PDF。

課程大綱指定讀物有兩種寫法，**這支兩種都吃**：

  - `mode="print"` —— 按**印刷頁碼**（「Blackwell Companion 91-122」）。整本電子檔前面
    還有封面、版權頁、目錄，兩者一定對不上。硬套位移會切錯章，而切錯章不會報錯
    ——檔案大小正常、頁數正常、打開也真的是一篇論文，只是不是指定的那一篇
    （[[feedback_reader_silent_failures]]）。所以逐頁讀頁眉／頁腳上真正印著的
    數字，取眾數當位移（不是猜、不是手填）。
  - `mode="pdf"` —— 按 **PDF 頁序**，取自書本身的內嵌目錄。有內嵌目錄就別投票，
    目錄是作者給的，投票是我猜的。

兩種都會驗首頁含不含篇名關鍵字，驗不過就不寫檔，列進待辦。

    python -X utf8 scripts/course_slice_readings.py             # 全做
    python -X utf8 scripts/course_slice_readings.py --folders   # 只建夾＋寫清單
    python -X utf8 scripts/course_slice_readings.py --offsets   # 只報位移
    python -X utf8 scripts/course_slice_readings.py --audit     # 只列各片首頁，肉眼複核

原書留在電子圖書館，這支只讀不搬。
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import textwrap
import urllib.request
from collections import Counter
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from course_html import write_html  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = r"G:\我的雲端硬碟\玄奘\博一上\上課"
LIB = r"G:\我的雲端硬碟\資料\知識圖工作室\電子圖書館"
TRIPITAKA = r"G:\我的雲端硬碟\資料\知識圖工作室\_tripitaka"

# 書代號 → (在電子圖書館的路徑, 書名簡稱，寫進切片檔名裡)
BOOKS = {
    "guide": (rf"{LIB}\宗教學\Braun, Willi, 1954- McCutcheon, Russell T. etc.，Guide to the study of religion.pdf", "Guide"),
    "routledge": (rf"{LIB}\_待審分類\Hinnells, John R，The Routledge companion to the study of religion.pdf", "Routledge Companion"),
    "understanding": (rf"{LIB}\_待審分類\Understanding religion (Sharpe，Eric J. (Eric John), 1933-2000).pdf", "Understanding Religion"),
    "theory": (rf"{LIB}\_待審分類\Frank Whaling，Theory and Method in Religious Studies Contemporary Approaches to the Study of Religion.pdf", "Theory and Method"),
    "blackwell": (rf"{LIB}\_待審分類\Robert A. Segal，The Blackwell Companion to the Study of Religion.pdf", "Blackwell Companion"),
    "insider": (rf"{LIB}\_待審分類\Russell T. McCutcheon，The InsiderOutsider Problem in the Study of Religion A Reader.pdf", "Insider-Outsider"),
    "waardenburg": (rf"{LIB}\_待審分類\Jacques Waardenburg Russell T. McCutcheon，Classical Approaches to the Study of Religion Aims, Methods, and Theories of Research. Introduction and Anthology.pdf", "Classical Approaches"),
}


def S(seq, author, title, book, p1, p2, kw, mode="print"):
    """整本書切一片。"""
    return dict(kind="slice", seq=seq, author=author, title=title,
                book=book, p1=p1, p2=p2, kw=kw, mode=mode)


def W(seq, title, url, cite=""):
    """網路上開放取用的讀物。"""
    return dict(kind="web", seq=seq, title=title, url=url, cite=cite)


def L(seq, title, url, cite=""):
    """只是連結（線上測驗、JS 產生的說明頁），不下載。"""
    return dict(kind="link", seq=seq, title=title, url=url, cite=cite)


def G(seq, title, cite="", why=""):
    """拿不到的：只寫進清單，說明卡在哪。"""
    return dict(kind="gap", seq=seq, title=title, cite=cite, why=why)


def T(seq, title, filename, cite=""):
    """老師已在 I-Learn 給的檔案，從課程根目錄複製進該週。"""
    return dict(kind="teacher", seq=seq, title=title, filename=filename, cite=cite)


def C(seq, title, start, end, cite=""):
    """CBETA 大正藏切一品（用 _tripitaka 的 jsonl）。"""
    return dict(kind="cbeta", seq=seq, title=title, start=start, end=end, cite=cite)


# ── 課程一：宗教研究基本問題與研究方法（博1A，倪杰）──────────────────────
# 大綱按主題分區不按週，週次夾沿用既有命名，不重編。
C1 = "宗教研究基本問題與研究方法"
C1_WEEKS = [
    ("W01 導論", "導論", []),
    ("W02-04 歷史背景與學科定位", "A. 學科本身與研究對象／歷史背景與學科定位", [
        G(1, "Alles, Study of Religion: An Overview", "Encyclopedia of Religion 8761-8767", "已切好；EoR 未進圖書館，無法重切"),
        S(2, "Sharpe", "The Study of Religion in Historical Perspective", "routledge", 21, 45, "Historical Perspective"),
        S(3, "Sharpe", "Theology and Religious Studies", "understanding", 1, 17, "Theology"),
        S(4, "Whaling", "Introduction", "theory", 1, 39, "Introduction"),
        S(5, "King", "Orientalism and the Study of Religion", "routledge", 275, 290, "Orientalism"),
    ]),
    ("W05 研究對象的定義", "研究對象的定義", [
        S(1, "Braun", "Religion", "guide", 3, 18, "Religion"),
        S(2, "Sharpe", "The Question of Definition", "understanding", 33, 48, "Definition"),
        S(3, "Arnal", "Definition", "guide", 21, 34, "Definition"),
    ]),
    ("W06-08 理解、解釋、詮釋的問題", "理解、解釋、詮釋的問題", [
        S(1, "Sharpe", "Commitment and Understanding", "understanding", 18, 32, "Commitment"),
        S(2, "Green", "Hermeneutics", "routledge", 392, 406, "Hermeneutics"),
        S(3, "Penner", "Interpretation", "guide", 57, 66, "Interpretation"),
        S(4, "Segal", "Theories of Religion", "routledge", 49, 60, "Theories of Religion"),
        S(5, "Segal", "In Defense of Reductionism", "insider", 150, 174, "Reductionism", mode="pdf"),
        S(6, "MacIntyre", "Is Understanding Religion Compatible With Believing", "insider", 48, 60, "Compatible", mode="pdf"),
    ]),
    ("W09 報告與討論", "報告與討論", []),
    ("W10 現代主義、後現代主義", "現代主義、後現代主義", [
        S(1, "Wiebe", "Modernism", "guide", 351, 364, "Modernism"),
        S(2, "Wolfart", "Postmodernism", "guide", 380, 395, "Postmodernism"),
        S(3, "Campbell", "Modernity and Postmodernity", "blackwell", 309, 320, "Postmodernity"),
    ]),
    ("W11 歷史與比較（一）", "B. 研究途徑與主題／歷史與比較", [
        # 大綱寫 41-176，括號註明實際只讀 41-56 與 84-164 兩段，所以切兩檔
        S(1, "King", "Historical and Phenomenological Approaches (41-56)", "theory", 41, 56, "Phenomenological"),
        S(2, "King", "Historical and Phenomenological Approaches (84-164)", "theory", 84, 164, ""),
    ]),
    ("W12 歷史與比較（二）", "歷史與比較", [
        S(1, "Smith", "Classification", "guide", 35, 44, "Classification"),
        S(2, "Martin", "Comparison", "guide", 45, 56, "Comparison"),
    ]),
    ("W13 歷史與比較（三）", "歷史與比較", [
        S(1, "Allen", "Phenomenology of Religion", "routledge", 182, 207, "Phenomenology"),
        S(2, "Ryba", "Phenomenology of Religion", "blackwell", 91, 122, "Phenomenology"),
        S(3, "Roscoe", "The Comparative Method", "blackwell", 25, 46, "Comparative Method"),
        S(4, "Paden", "Comparative Religion", "routledge", 208, 225, "Comparative Religion"),
    ]),
    ("W14 社會與文化（一）", "社會與文化", [
        S(1, "Gifford", "Religious Authority - Scripture, Tradition, Charisma", "routledge", 379, 391, "Religious Authority"),
        S(2, "Jensen", "Structure", "guide", 314, 333, "Structure"),
    ]),
    ("W15 社會與文化（二）", "社會與文化", [
        S(1, "Segal", "Myth and Ritual", "routledge", 355, 378, "Myth and Ritual"),
    ]),
    ("W16 社會與文化（三）", "社會與文化", [
        S(1, "Segal", "Myth", "blackwell", 337, 356, "Myth"),
        S(2, "McCutcheon", "Myth", "guide", 190, 208, "Myth"),
    ]),
    ("W17 社會與文化（四）", "社會與文化", [
        S(1, "Grimes", "Ritual", "guide", 259, 270, "Ritual"),
        S(2, "Bell", "Ritual", "blackwell", 397, 411, "Ritual"),
    ]),
    ("W18 報告與討論", "報告與討論", []),
]

# ── 課程二：宗教學理論與方法(一)（碩職1A）───────────────────────────────
# 頁碼取自兩本書的內嵌目錄，是 PDF 頁序，不是印刷頁碼。
# 🚨 Waardenburg 這本有兩個 Otto：Rudolf Otto（p457）與 Walter F. Otto（p644）。
#    大綱指定的是前者。
C2 = "宗教學理論與方法(一)"
C2_WEEKS = [
    ("W01 釐清有關宗教學的基本問題", "釐清有關宗教學的基本問題", []),
    ("W02 釐清有關宗教學的基本問題", "釐清有關宗教學的基本問題", [
        S(1, "Kant", "What is Enlightenment", "insider", 144, 149, "Enlightenment", mode="pdf"),
    ]),
    ("W03 釐清有關宗教學的基本問題", "釐清有關宗教學的基本問題", []),
    ("W04 宗教學的宗教概念", "宗教學的宗教概念", [
        S(1, "Heiler", "Friedrich Heiler (Prayer; The Scholarly Study of Religion)", "waardenburg", 485, 504, "Heiler", mode="pdf"),
    ]),
    ("W05 宗教學的宗教概念", "宗教學的宗教概念", [
        S(1, "Heiler", "Friedrich Heiler (Prayer; The Scholarly Study of Religion)", "waardenburg", 485, 504, "Heiler", mode="pdf"),
    ]),
    ("W06 宗教學的宗教概念", "宗教學的宗教概念", [
        S(1, "Otto", "Rudolf Otto (The Idea of the Holy; Religious History)", "waardenburg", 457, 484, "Otto", mode="pdf"),
    ]),
    ("W07 宗教學的宗教概念", "宗教學的宗教概念", [
        S(1, "Otto", "Rudolf Otto (The Idea of the Holy; Religious History)", "waardenburg", 457, 484, "Otto", mode="pdf"),
    ]),
    ("W08 宗教學的宗教概念", "宗教學的宗教概念", [
        S(1, "Malinowski", "Bronislaw Malinowski (The Study of Primitive Man and His Religion)", "waardenburg", 569, 583, "Malinowski", mode="pdf"),
    ]),
    ("W09 宗教學的宗教概念", "宗教學的宗教概念", [
        S(1, "Malinowski", "Bronislaw Malinowski (The Study of Primitive Man and His Religion)", "waardenburg", 569, 583, "Malinowski", mode="pdf"),
    ]),
    ("W10 宗教學的宗教概念", "宗教學的宗教概念", []),
    ("W11 宗教學的研究立場", "宗教學的研究立場", []),
    ("W12 宗教學的研究立場", "宗教學的研究立場", [
        S(1, "Eliade", "A New Humanism", "insider", 106, 114, "Humanism", mode="pdf"),
    ]),
    ("W13 宗教學的研究立場", "宗教學的研究立場", []),
    ("W14 宗教學的研究立場", "宗教學的研究立場", [
        S(1, "MacIntyre", "Is Understanding Religion Compatible With Believing", "insider", 48, 60, "Compatible", mode="pdf"),
    ]),
    ("W15 討論「宗教學的研究立場」", "討論「宗教學的研究立場」", [
        S(1, "Segal", "In Defense of Reductionism", "insider", 150, 174, "Reductionism", mode="pdf"),
    ]),
    ("W16 討論「宗教學的研究立場」", "討論「宗教學的研究立場」", [
        S(1, "Segal", "In Defense of Reductionism", "insider", 150, 174, "Reductionism", mode="pdf"),
    ]),
    ("W17 討論「宗教學的研究立場」", "討論「宗教學的研究立場」", []),
    ("W18 綜合探討", "綜合探討", []),
]

# ── 課程三：初階宗教學日文文獻選讀（碩1A，倪杰）─────────────────────────
C3 = "初階宗教學日文文獻選讀"
C3_WEEKS = [
    ("W01 課程介紹．目標設定", "課程介紹、目標設定（SMART／WOOP／CEFR）", [
        L(1, "用SMART原則設定明確目標", "https://www.managertoday.com.tw/glossary/view/193"),
        L(2, "About the Common European Framework of Reference (CEFR)", "https://www.cambridgeenglish.org/tw/exams-and-tests/cefr/"),
        L(3, "目標設定完全指南（VoiceTube 影片）", "https://www.voicetube.com/videos/116609"),
    ]),
    ("W02 個別化自學", "依個人日文程度客製化學習；British Council 線上分級測驗", [
        L(1, "British Council 線上英文分級測驗", "https://www.britishcouncil.org/english/level-test"),
    ]),
    ("W03 與老師個別討論課程目標", "CEFR Academic Reader；繳交個人課程目標", [
        T(1, "石井隆之《日本の宗教の知識と英語を身につける》第一章", "石井隆之，日本の宗教の知識と英語を身につける2010第一章.pdf"),
    ]),
    ("W04 個別化自學", "依個人日文程度客製化學習", []),
    ("W05 個別化自學", "Josephson, The Invention of Religion in Japan", [
        G(1, "Josephson, The Invention of Religion in Japan (2012), Conclusion",
          "Chicago: University of Chicago Press, 2012", "電子圖書館與 Drive 都沒有這本，需下載"),
    ]),
    ("W06 個別化自學", "印度教節慶的宗教與社會意義", [
        W(1, "Babu, The Religious and Social Significance of Hindu Festivals",
          "https://jnrid.org/", "Journal of Novel Research and Innovative Development 3(1), 2025"),
    ]),
    ("W07 個別化自學", "藏傳佛教如來藏之爭", [
        G(1, "Wangchuk, Dolpopa and Gyaltsab Debate Tathāgatagarbha",
          "Religion Compass 4(11): 669-678, 2010. doi:10.1111/j.1749-8171.2010.00248.x",
          "Wiley 付費牆，校內 IP 或圖書館代理才拿得到"),
    ]),
    ("W08 個別化自學", "依個人日文程度客製化學習", []),
    ("W09 與老師個別討論課程目標進度", "期中檢視個人目標進度", []),
    ("W10 個別化自學", "依個人日文程度客製化學習", []),
    ("W11 個別化自學", "依個人日文程度客製化學習", []),
    ("W12 個別化自學", "四聖諦作為行動方案", [
        W(1, "Willis, The Four Noble Truths Are a Plan of Action",
          "https://www.lionsroar.com/four-noble-truths-plan-of-action/", "Lion's Roar, 2022-01-20"),
    ]),
    ("W13 個別化自學", "依個人日文程度客製化學習", []),
    ("W14 個別化自學", "達賴喇嘛傳記；學術誠信與生成式 AI", [
        W(1, "The 14th Dalai Lama, Birth to Exile",
          "https://www.dalailama.com/the-dalai-lama/biography-and-daily-life/birth-to-exile"),
        T(2, "國立中山大學學生學術誠信指引（中英對照）",
          "國立中山大學學生學術誠信指引NSYSU Student Academic Integrity Guidelines Bilingual-中英對照2026.02.23.pdf"),
        T(3, "臺灣教育倫理中心：生成式AI用於學術研究的6個關鍵",
          "台灣教育倫理中心，留意生成式人工智慧用於學術與研究活動時的6個關鍵於2025.11.30下載.jpg"),
    ]),
    ("W15 個別化自學", "依個人日文程度客製化學習", []),
    ("W16 個別化自學", "依個人英文級別客製化全班學習與個別化自學", []),
    ("W17 自我評估", "期末自我評估、個別討論、教學評量", []),
    ("W18 自我評估", "期末自我評估、個別討論、教學評量", []),
]

# ── 課程四：唯識思想專題研討（博1A，昭慧法師）───────────────────────────
# 大綱不編週次，逐單元排；《解深密經》四品從 CBETA T16n0676 切出。
C4 = "唯識思想專題研討"
C4_WEEKS = [
    ("W01 緒論", "談個人研究唯識學之困境與突破；評量說明", []),
    ("W02 研究方法論", "傳統研究法／現代佛教學研究法／印順導師「以佛法研究佛法」", []),
    ("W03 唯識學的重要經論", "唯識學派之工具書、基礎六經、重要論典", []),
    ("W04 當代學術研究成果", "中文學界研究成果／外文學界研究成果", []),
    ("W05 根本佛法與唯識學（一）", "原始經教的根本義理──緣起；《阿含經》中的緣起法；緣起論與唯識學", [
        T(1, "初期唯識學說系統理論之建立", "040117初期唯識學說系統理論之建立.pptx"),
    ]),
    ("W06 根本佛法與唯識學（二）", "十二緣起與唯識學", [
        T(1, "初期唯識思想概論", "初期唯識思想概論-100916昭修.pptx"),
        T(2, "孟子與告子有關「人性善惡」的譬喻", "孟子與告子有關「人性善惡」的譬喻.docx"),
    ]),
    ("W07 根本佛法與唯識學（三）", "綜論心為主導性", []),
    ("W08 簡述唯識思想史", "印度與中國之唯識學派", []),
    ("W09 無常、無我之問題探索", "常見與我見之對治；「諸行無常」「諸法無我」的疑惑與解答", []),
    ("W10 部派思想與唯識學（一）", "四個探索方向；細心相續", []),
    ("W11 部派思想與唯識學（二）", "種習熏生；境相非實", []),
    ("W12 部派思想與唯識學（三）", "瑜伽禪觀", []),
    ("W13 性空大乘與唯識學（上）", "菩薩願行與唯識思想", []),
    ("W14 性空大乘與唯識學（下）", "空性思想與唯識學", []),
    ("W15 唯識根本經典（一）", "《解深密經》心意識相品第三", [
        T(1, "解深密經簡介", "解深密經簡介-150825.pdf"),
        T(2, "解深密經 卷1-5", "解深密經 卷1-5.pdf"),
        C(3, "解深密經 心意識相品第三", 53, 64, "大正藏 T16n0676，玄奘譯"),
    ]),
    ("W16 唯識根本經典（二）", "《解深密經》一切法相品第四", [
        C(1, "解深密經 一切法相品第四", 65, 77, "大正藏 T16n0676，玄奘譯"),
    ]),
    ("W17 唯識根本經典（三）", "《解深密經》無自性相品第五", [
        C(1, "解深密經 無自性相品第五", 78, 123, "大正藏 T16n0676，玄奘譯"),
    ]),
    ("W18 唯識根本經典（四）", "《解深密經》分別瑜伽品第六", [
        C(1, "解深密經 分別瑜伽品第六", 124, 258, "大正藏 T16n0676，玄奘譯"),
    ]),
]

COURSES = [(C1, C1_WEEKS), (C2, C2_WEEKS), (C3, C3_WEEKS), (C4, C4_WEEKS)]

_PAGENO = re.compile(r"(\d{1,4})")


def find_offset(doc: fitz.Document) -> int:
    """PDF 頁序(1-based) − 印刷頁碼。逐頁投票取眾數。

    只掃中段：前面是羅馬數字的前言、後面是索引，兩頭都會污染投票。
    """
    votes: Counter[int] = Counter()
    lo, hi = int(doc.page_count * 0.15), int(doc.page_count * 0.85)
    for i in range(lo, hi):
        lines = [ln.strip() for ln in doc[i].get_text().splitlines() if ln.strip()]
        for cand in lines[:2] + lines[-2:]:
            m = _PAGENO.fullmatch(cand)
            if m:
                votes[i + 1 - int(m.group(1))] += 1
    if not votes:
        raise RuntimeError("讀不到任何頁碼——這本可能沒有文字層，要先 OCR")
    (best, n), rest = votes.most_common(1)[0], votes.most_common(3)[1:]
    runner = rest[0][1] if rest else 0
    # 眾數要壓倒性領先才可信。差距不大代表頁眉抓到的是別的數字（年份、註號），
    # 這時候寧可停下來，也不要切出一堆錯章。
    if n < 20 or n < runner * 5:
        raise RuntimeError(f"位移投票不夠乾淨：{votes.most_common(3)}")
    return best


def safe(s: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "-", s).strip().rstrip(".")


_OPENED: dict[str, tuple] = {}


def get_book(key: str):
    """開書，順便算好印刷頁碼位移（算不出來就記 None，print 模式才會用到）。"""
    if key in _OPENED:
        return _OPENED[key]
    path, short = BOOKS[key]
    if not os.path.exists(path):
        _OPENED[key] = None
        return None
    doc = fitz.open(path)
    try:
        off = find_offset(doc)
    except RuntimeError as e:
        off = None
        print(f"[位移算不出] {key}：{e}")
    _OPENED[key] = (doc, off, short)
    return _OPENED[key]


# ── 網路讀物 → PDF ──────────────────────────────────────────────────────
_TAG_BREAK = re.compile(r"</(p|div|li|tr|h[1-6])>|<br\s*/?>", re.I)


def html_to_text(html_bytes: bytes) -> str:
    t = html_bytes.decode("utf-8", errors="replace")
    t = re.sub(r"<(script|style|nav|footer|header|form)\b.*?</\1>", " ", t, flags=re.S | re.I)
    t = _TAG_BREAK.sub("\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    import html as _h
    t = _h.unescape(t)
    t = re.sub(r"[ \t\u00a0]+", " ", t)
    lines = [ln.strip() for ln in t.split("\n")]
    # 導覽列殘骸多半是很短的單行，連續一堆；只留有實質長度的段落
    keep, blank = [], 0
    for ln in lines:
        if not ln:
            blank += 1
            continue
        if blank:
            keep.append("")
            blank = 0
        keep.append(ln)
    return "\n".join(keep).strip()


def text_to_pdf(title: str, body: str, cite: str, url: str, dst: str) -> None:
    doc = fitz.open()
    margin, width, lead = 56, 595, 14.5
    wrapper = textwrap.TextWrapper(width=92, break_long_words=False)
    lines = [title, "", cite, url, "─" * 60, ""]
    for para in body.split("\n"):
        lines.extend(wrapper.wrap(para) or [""])
    page = y = None
    for ln in lines:
        if page is None or y > 842 - margin:
            page = doc.new_page(width=width, height=842)
            y = margin
        page.insert_text((margin, y), ln, fontname="china-s", fontsize=10)
        y += lead
    doc.save(dst)
    doc.close()


def fetch_web(item: dict, dst_dir: str, week: str) -> tuple[bool, str]:
    name = f"{week}_{item['seq']}_{safe(item['title'])}.pdf"
    dst = os.path.join(dst_dir, name)
    if os.path.exists(dst):
        return True, name + "（已存在）"
    req = urllib.request.Request(item["url"], headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            raw = r.read()
            ctype = r.headers.get("Content-Type", "")
    except Exception as e:
        return False, f"{item['title']}：抓不到（{e}）"
    if "pdf" in ctype.lower() or raw[:4] == b"%PDF":
        with open(dst, "wb") as f:
            f.write(raw)
        return True, name
    body = html_to_text(raw)
    if len(body) < 400:
        return False, f"{item['title']}：抓到的內文太短（{len(body)} 字），可能被擋"
    text_to_pdf(item["title"], body, item.get("cite", ""), item["url"], dst)
    return True, name


# ── CBETA 一品 → md ────────────────────────────────────────────────────
def cbeta_chapter(item: dict, dst_dir: str, week: str) -> tuple[bool, str]:
    src = os.path.join(TRIPITAKA, "T0676.jsonl")
    name = f"{week}_{item['seq']}_{safe(item['title'])}.html"
    dst = os.path.join(dst_dir, name)
    if os.path.exists(dst):
        return True, name + "（已存在）"
    if not os.path.exists(src):
        return False, f"{item['title']}：找不到 {src}"
    rows = [json.loads(ln) for ln in open(src, encoding="utf-8")]
    out = [f"# {item['title']}", "", f"- 出處：{item['cite']}", "- 段號＝大正藏頁欄行，未自編", ""]
    for r in rows[item["start"]: item["end"] + 1]:
        s = r["sources"]
        s = ast.literal_eval(s) if isinstance(s, str) else s
        txt = (s or {}).get("lzh", "").strip()
        if not txt:
            continue
        if r["kind"] == "head":
            out += ["", f"## {txt}", ""]
        else:
            out.append(f"**{r['uid']}**　{txt}")
            out.append("")
    write_html(dst, item["title"], "\n".join(out))
    return True, name


# ── 指定閱讀清單 ────────────────────────────────────────────────────────
def write_manifest(course: str, week: str, topic: str, items: list, dst_dir: str) -> None:
    out = [f"# {week}", "", f"**授課重點**：{topic}", ""]
    if not items:
        out += ["本週大綱未列指定閱讀。", ""]
    else:
        out += ["## 指定閱讀", ""]
        for it in sorted(items, key=lambda x: x["seq"]):
            if it["kind"] == "slice":
                short = BOOKS[it["book"]][1]
                pages = f"{short} {it['p1']}-{it['p2']}" + ("（PDF 頁序）" if it["mode"] == "pdf" else "")
                out.append(f"{it['seq']}. {it['author']}, 〈{it['title']}〉，{pages}")
            elif it["kind"] == "web":
                out.append(f"{it['seq']}. {it['title']}" + (f"（{it['cite']}）" if it["cite"] else ""))
                out.append(f"   - {it['url']}")
            elif it["kind"] == "link":
                out.append(f"{it['seq']}. {it['title']}（線上使用，不另存檔）")
                out.append(f"   - {it['url']}")
            elif it["kind"] == "teacher":
                out.append(f"{it['seq']}. {it['title']}　※老師於 I-Learn 提供")
            elif it["kind"] == "cbeta":
                out.append(f"{it['seq']}. {it['title']}（{it['cite']}）")
            elif it["kind"] == "gap":
                out.append(f"{it['seq']}. ⚠ {it['title']}" + (f"（{it['cite']}）" if it["cite"] else ""))
                out.append(f"   - **尚未取得**：{it['why']}")
        out.append("")
    out += ["---", "", f"課程：{course}　｜　依 I-Learn 課程大綱建立，改大綱後重跑 `scripts/course_slice_readings.py`。"]
    write_html(os.path.join(dst_dir, "指定閱讀.html"),
               f"{week}　指定閱讀", "\n".join(out))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--folders", action="store_true", help="只建夾＋寫清單，不切片不下載")
    ap.add_argument("--offsets", action="store_true", help="只報各書的頁碼位移")
    ap.add_argument("--audit", action="store_true", help="只列已切好的各片首頁，肉眼複核")
    a = ap.parse_args()

    if a.offsets:
        for key in BOOKS:
            got = get_book(key)
            if not got:
                print(f"{key:14s} 缺書")
                continue
            doc, off, _ = got
            print(f"{key:14s} {doc.page_count:5d} 頁  位移 {off if off is not None else '算不出'}")
        return

    if a.audit:
        for course, weeks in COURSES:
            for folder, _, _ in weeks:
                d = os.path.join(BASE, course, folder)
                if not os.path.isdir(d):
                    continue
                for f in sorted(os.listdir(d)):
                    if not f.lower().endswith(".pdf"):
                        continue
                    with fitz.open(os.path.join(d, f)) as doc:
                        head = [ln.strip() for ln in doc[0].get_text().splitlines() if ln.strip()]
                    print(f"{f[:60]:62s} | 首頁: {' / '.join(head[:4])[:78]}")
        return

    ok, bad = 0, []
    for course, weeks in COURSES:
        print("=" * 66)
        print(course)
        croot = os.path.join(BASE, course)
        for folder, topic, items in weeks:
            dst_dir = os.path.join(croot, folder)
            os.makedirs(dst_dir, exist_ok=True)
            write_manifest(course, folder, topic, items, dst_dir)
            if a.folders:
                continue
            week = folder.split()[0]
            for it in sorted(items, key=lambda x: x["seq"]):
                if it["kind"] == "link":
                    continue
                if it["kind"] == "gap":
                    bad.append((course, folder, it["title"], it["why"]))
                    continue

                if it["kind"] == "teacher":
                    src = os.path.join(croot, it["filename"])
                    dst = os.path.join(dst_dir, it["filename"])
                    if not os.path.exists(src):
                        bad.append((course, folder, it["title"], f"課程根目錄找不到 {it['filename']}"))
                    elif os.path.exists(dst):
                        pass
                    else:
                        with open(src, "rb") as fi, open(dst, "wb") as fo:
                            fo.write(fi.read())
                        ok += 1
                        print(f"  ✓ {folder} / {it['filename'][:52]}")
                    continue

                if it["kind"] == "web":
                    good, msg = fetch_web(it, dst_dir, week)
                    (print(f"  ✓ {folder} / {msg[:56]}") if good else bad.append((course, folder, it["title"], msg)))
                    ok += good
                    continue

                if it["kind"] == "cbeta":
                    good, msg = cbeta_chapter(it, dst_dir, week)
                    (print(f"  ✓ {folder} / {msg[:56]}") if good else bad.append((course, folder, it["title"], msg)))
                    ok += good
                    continue

                # slice
                got = get_book(it["book"])
                if not got:
                    bad.append((course, folder, it["title"], f"缺書 {it['book']}"))
                    continue
                doc, off, short = got
                if it["mode"] == "pdf":
                    lo, hi = it["p1"] - 1, it["p2"] - 1
                else:
                    if off is None:
                        bad.append((course, folder, it["title"], "印刷頁碼位移算不出來"))
                        continue
                    lo, hi = it["p1"] + off - 1, it["p2"] + off - 1
                if lo < 0 or hi >= doc.page_count:
                    bad.append((course, folder, it["title"], f"頁碼超出範圍 {lo}-{hi}/{doc.page_count}"))
                    continue
                head = doc[lo].get_text() + (doc[lo + 1].get_text() if lo + 1 < doc.page_count else "")
                if it["kw"] and it["kw"].lower() not in head.lower():
                    bad.append((course, folder, it["title"], f"首頁驗不到「{it['kw']}」"))
                    continue
                dst = os.path.join(
                    dst_dir,
                    f"{week}_{it['seq']}_{safe(it['author'])}_{safe(it['title'])} ({short} {it['p1']}-{it['p2']}).pdf")
                if os.path.exists(dst):
                    continue
                out = fitz.open()
                out.insert_pdf(doc, from_page=lo, to_page=hi)
                out.save(dst)
                out.close()
                ok += 1
                print(f"  ✓ {folder} / {os.path.basename(dst)[:56]}  ({hi - lo + 1}p)")

    print()
    for course, folder, title, why in bad:
        print(f"✗ {course} / {folder} / {title[:44]} —— {why}")
    print(f"\n完成 {ok} 項，待辦 {len(bad)} 項")


if __name__ == "__main__":
    main()
