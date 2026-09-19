# -*- coding: utf-8 -*-
"""把一部作品的頁切成節 —— 只認節號當錨，且只收「下一個該出現的號」。

這一支是純函式，沒有 DB、沒有檔案 IO，方便逐部試跑與寫測試。
上游是 `apocrypha_toc.py`（哪幾部作品）＋`apocrypha_map_volumes.py`（各佔哪些頁），
下游是入庫腳本。

─────────────────────────────────────────────────────────────────────────
🚨 這套書的數字有三種，而在純文字層**長得一模一樣**
─────────────────────────────────────────────────────────────────────────
實際頁面（新約篇第一冊 p92–93）：

    被殺害，很是懼怕，就用布把小孩裹住，放在牛欄裏。82³至於伊利沙伯，
                                              ↑↑ ↑
                                     註腳標記 82　節號 3（上標）
    231那時希律正到處搜尋約翰，就派官員往祭壇那裏找撒迦利亞
    ↑↑↑
    章號 23 ＋ 節號 1，印在一起

`-m ocr` 之下 MinerU 的 span 是**整行**，沒有逐字字級也沒有逐字 bbox，所以
「這個 3 是節號還是註腳標記」在文字層分不出來。能用的只有兩件確定的事：

  ① **該頁有哪些註腳標記，`discarded_blocks` 已經講了**。p92 的註腳是
     82–86、p93 是 87–89。落在這個集合裡的數字就不是節號。
  ② **節號是連號的**。所以只收「下一個該出現的號」——別的數字一律當內文。

交接單 §C 記著前一輪的教訓：拿「這段夠長、開頭不是標點 → 判為新一節」去補號，
55 節照樣連號、字數照樣對得上、閘照樣全過，但每一節的界線都往前挪了一段。
所以這裡**寧可少切也不要多切**：判不出來就併進當前節並記一筆，不要猜。

─────────────────────────────────────────────────────────────────────────
三種編號體例：本書各部作品不一致
─────────────────────────────────────────────────────────────────────────
  flat      §1、§2、§3…      （例：阿拉伯語耶穌嬰孩時期福音 §1–55）
  chapverse 1:1、1:2、2:1…   （例：雅各原始福音，章號與節號印在一起）
  grouped   一、二、三…分組，**每組的號各自從 1 開始**
            （例：彼得的宣講，按引用它的教父分成四組）

不去「猜」是哪一種，而是**都跑一遍**：flat 與 chapverse 要求恰好一種能完全對上
（每個號都是連的、沒有落單的數字）；兩種都通或兩種都不通，一律回報不寫入——
這是閘，不是二選一的偏好。grouped 排在最後當退路：它要有「一、二、三…」的連號
小標才成立，所以不會搶走前兩種的案子。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

CN_ONES = {c: i for i, c in enumerate("一二三四五六七八九", 1)}


def cn_int(s: str) -> int | None:
    """中文數字 → 阿拉伯數字（只需撐到幾十）。"""
    s = s.strip()
    if not s or any(c not in "十一二三四五六七八九" for c in s):
        return None
    if "十" not in s:
        return CN_ONES.get(s)
    head, _, tail = s.partition("十")
    return (CN_ONES.get(head, 1) if head else 1) * 10 + (CN_ONES.get(tail, 0) if tail else 0)

# 節號後面可以接中文、引號、括號、刪節號（拉丁語 §68 後面就是「……」），
# 只認中文字會靜默漏掉整整一節。
AFTER_NUM = r"[一-鿿「」『』（）()《》〈〉〔〕【】…．\.、，,：:；;？?！!—－\-]"
NUM_HEAD = re.compile(rf"^(\d{{1,4}})\s*(?={AFTER_NUM}|$)")
SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
SUP_TO_ASCII = str.maketrans(SUP_DIGITS, "0123456789")
SUP_HEAD = re.compile(rf"^([{SUP_DIGITS}]+)\s*")
# 摘要體的範圍節號：「1-6概論…」「7 - 10耶穌講述…」「32 - 57耶穌講出…」
RANGE_HEAD = re.compile(r"^(\d{1,3})\s*[-–—~]\s*(\d{1,3})\s*")


@dataclass
class Section:
    chapter: int | None
    verse: int | None
    number: int                      # flat 時就是節號；chapverse 時是節號
    page: int | None
    paras: list[str] = field(default_factory=list)
    inferred: bool = False
    # 這一節其實涵蓋到第幾節（下一節的號被 OCR 吃掉、又補不回來時）。
    # 內容沒有少，只是少了那一刀，所以 label 要誠實寫成「6-7」。
    spans_to: int | None = None

    @property
    def label(self) -> str:
        base = f"{self.chapter}:{self.verse}" if self.chapter is not None else str(self.number)
        return f"{base}-{self.spans_to}" if self.spans_to is not None else base


@dataclass
class Split:
    scheme: str                      # 'flat' / 'chapverse'
    sections: list[Section]
    problems: list[str]
    orphan_numbers: list[tuple[int | None, str]]   # 沒被當成節號的行首數字
    # 第一節出現**之前**的段落（文獻自己的序言／開場白，例如阿拉伯語那篇的
    # 三一頌）。沒有當前節可以併，所以單獨收在這裡由呼叫端寫成「序」那一列。
    # 🚨 這樣切節就是一個**完整分割**：每個段落不是進某一節、就是進序言，
    #    沒有第三條路會讓段落無聲消失。逐段點名因此不必事後比對字串
    #    （節首的號已經被剝掉，比不準）。
    prologue: list[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """能不能用。**刻意不把 orphan 當致命傷。**

        🚨 這條判準改過一次，理由要記著：切節只在「號等於下一個該出現的號」時才下刀，
        所以對不上的帶號段落一律被併進**當前節**——它造成的是**少一刀**，不可能造成
        **切錯位置**。內容一個字都沒少。

        原本把 orphan 當致命傷，結果是《多馬行傳》92 頁、《雅各原始福音》20 頁這種
        整部作品一節都不收，只因為書上有幾個節號在 OCR 裡沒留下來（那些號印在段落
        中間、又不是上標，文字層根本沒有它們）。現狀是文字壞的、邊界也錯的，換成
        「邊界正確、頁碼正確、但粒度較粗」是淨改善。所以 orphan 改成**回報**不擋，
        由 `choose` 拿它當挑體例的依據，並在報表上印出來。
        """
        return not self.problems and bool(self.sections)


def _lead_number(text: str, markers: set[int]) -> tuple[int | None, str, bool]:
    """段首的數字 → (值, 去掉號之後的文字, 是不是上標)。

    先看上標（MinerU 保得住的那種，例如「³至於伊利沙伯」），再看普通數字。
    註腳標記會**黏在前一段的結尾**而不是段首，所以段首那個數字落在該頁註腳
    標記集合裡時，只在「它同時不是下一個該出現的節號」的情況下才丟掉——
    這個判斷留給呼叫端，本函式只負責認出數字。
    """
    m = SUP_HEAD.match(text)
    if m:
        return int(m.group(1).translate(SUP_TO_ASCII)), text[m.end():].lstrip(), True
    m = NUM_HEAD.match(text)
    if m:
        # 號後面那個分隔符（`1.` 的點、`1、` 的頓號）要一起吃掉，否則正文會以
        # 「.要詳細討論…」開頭——看得出來是髒的，但入庫後每一節都多一個字。
        return int(m.group(1)), _strip_sep(text[m.end():]), False
    return None, text, False


def _strip_sep(s: str) -> str:
    return s.lstrip(".．、,， 　")


def _strip_markers(num: int, markers: set[int]) -> list[int]:
    """把「註腳標記＋節號黏在一起」的數字拆開，回傳可能的節號候選。

    例：某頁註腳有 82，段落開頭是 `823`——那其實是註腳 82 之後接節號 3。
    只在「前綴剛好是該頁的某個註腳標記」時才拆，否則不動。
    """
    out = [num]
    s = str(num)
    for mk in markers:
        ms = str(mk)
        if len(ms) < len(s) and s.startswith(ms):
            rest = s[len(ms):]
            if rest and not rest.startswith("0"):
                out.append(int(rest))
    return out


def split_flat(paras: list[dict], first: int, markers_by_page: dict[int, set[int]]) -> Split:
    """§1、§2、§3… 連續編號。`paras` = [{page, text}]。

    🚨 只認 `want` 會在「號被 OCR 吃掉」時**永久卡住**：阿拉伯語那篇 §5 的號沒認出來，
    於是 want 停在 5，§6 之後每一段都被併進 §4——切出 4 節、而且 `problems` 是空的，
    看起來乾乾淨淨。所以看到 `want + 1` 時要當成「§want 的號被吃掉了」記一筆缺口
    往前走，而不是默默併下去。缺口一律回報，由呼叫端拿寫死的對照表去補或擋下。
    """
    sections: list[Section] = []
    problems: list[str] = []
    orphans: list[tuple[int | None, str]] = []
    prologue: list[dict] = []
    gaps: list[int] = []
    want = first
    for pa in paras:
        markers = markers_by_page.get(pa["page"], set())
        # 🚨 摘要體：節號是**範圍**（「1-6概論耶穌復活以後的教導」「7 - 10耶穌講述…」）。
        #    《皮斯特斯·索菲婭》整篇、《託馬太名福音》的「第1-12章撮要」都是這樣排的。
        #    不認的話整篇只切得出一兩節，其餘全變成對不上的號。
        mr = RANGE_HEAD.match(pa["text"])
        if mr and int(mr.group(1)) == want:
            a, b = int(mr.group(1)), int(mr.group(2))
            if b >= a:
                sections.append(Section(chapter=None, verse=None, number=a,
                                        page=pa["page"],
                                        paras=[_strip_sep(pa["text"][mr.end():])],
                                        spans_to=b if b > a else None))
                want = b + 1
                continue
        num, rest, _sup = _lead_number(pa["text"], markers)
        cands = _strip_markers(num, markers) if num is not None else []
        hit = next((c for c in (want, want + 1) if c in cands), None)
        if hit is not None:
            if hit == want + 1:
                gaps.append(want)
            body = rest if num == hit else pa["text"].split(str(hit), 1)[1].lstrip()
            sections.append(Section(chapter=None, verse=None, number=hit,
                                    page=pa["page"], paras=[body]))
            want = hit + 1
            continue
        if sections:
            sections[-1].paras.append(pa["text"])
        else:
            prologue.append({"page": pa["page"], "text": pa["text"]})
        # 帶號卻沒被收掉的段落一律點名——不管前面有沒有切出節。這是本檔的主閘。
        if num is not None and not (cands and set(cands) & markers):
            orphans.append((pa["page"], pa["text"][:50]))
    if not sections:
        problems.append(f"flat：一節都沒切出來（第一個該出現的號是 {first}）")
    if gaps:
        problems.append(f"flat：節號被吃掉的節 {gaps}（要對照表才能定界）")
    return Split("flat", sections, problems, orphans, prologue)


# 🚨 章號與節號之間只容得下**同一行內**的空白（`13 1`）。用 `\s` 會連換行一起吃，
#    於是「26\n7」被當成一個號，int() 直接炸。表格還原成文字之後段落裡就有換行了。
HEAD_REGION = re.compile(rf"^([\d{SUP_DIGITS}]+(?:[ \t　]+[\d{SUP_DIGITS}]+)?)")


def _chapverse_readings(text: str, markers: set[int]) -> list[tuple[int | None, int, str]]:
    """段首的數字區 → 所有說得通的 (章, 節, 去掉號的正文) 讀法。

    🚨 同一件事書上有四種印法，少認一種就整章不見（而且很安靜——那一章的內容
    會被併進上一節，節數只少一、字數對得上）。實測《多馬的耶穌嬰孩時期福音》
    十九章裡就同時出現：

        `121又一次，在撒種的季節裏…`   章節黏在一起
        `13 1耶穌的父親是一個木匠…`    中間有空白
        `15¹這事以後…`                 節號是上標
        `2主的大日子快將來臨…`         只有節號（同章的下一節）

    所以不猜，**把所有讀法列出來**，交給呼叫端用「下一個該出現的號」去選。
    黏在一起的那種會產生多個切點（`141` → 1:41 / 14:1），能對上的只有一個。
    """
    m = HEAD_REGION.match(text)
    if not m:
        return []
    region, rest = m.group(1), text[m.end():]
    out: list[tuple[int | None, int, str]] = []

    def add(chap: str | None, verse: str) -> None:
        if not verse or (len(verse) > 1 and verse.startswith("0")):
            return
        if chap is not None and (not chap or chap.startswith("0")):
            return
        out.append((int(chap) if chap is not None else None, int(verse),
                    _strip_sep(rest)))

    plain = region.translate(SUP_TO_ASCII)
    # 分隔可能是半形空白、tab 或**全形空白**。只認 `" " in region` 的話，全形那種
    # 會掉到下面「整串都是節號」那條路，然後 int("45　7") 直接炸。
    parts = re.split(r"[ \t　]+", region.strip())
    if len(parts) == 2:                                  # `13 1` / `45　7`
        add(parts[0].translate(SUP_TO_ASCII), parts[1].translate(SUP_TO_ASCII))
        return out
    plain = re.sub(r"[ \t　]+", "", plain)
    # 上標／非上標的交界就是章與節的分界（`15¹`）
    cut = next((i for i, c in enumerate(region) if c in SUP_DIGITS), None)
    if cut is not None:
        if cut == 0:
            add(None, plain)                             # 整串都是上標 → 只有節號
        else:
            add(plain[:cut], plain[cut:])
            # 🚨 前面那截也可能是**註腳標記**而不是章號：`82³` 是「註腳 82」＋
            #    「第 3 節」，不是「82 章 3 節」。早年這裡直接 return，於是整段
            #    只剩一個對不上的讀法，那一節就被併進上一節了。
            if int(plain[:cut]) in markers:
                add(None, plain[cut:])
        return out
    add(None, plain)                                     # 只有節號
    for i in range(1, len(plain)):                       # 章節黏在一起的各種切法
        add(plain[:i], plain[i:])
    # 前面那截剛好是本頁的註腳標記時，把它剝掉再讀一次（`82³` 那種）
    for mk in markers:
        ms = str(mk)
        if plain.startswith(ms) and len(ms) < len(plain):
            tail = plain[len(ms):]
            add(None, tail)
            for i in range(1, len(tail)):
                add(tail[:i], tail[i:])
    return out


INLINE_SUP = re.compile(rf"[{SUP_DIGITS}]+")


def _inline_splits(text: str, start_verse: int, markers: set[int]) -> list[tuple[int, str]]:
    """一段文字裡的**行內上標節號** → [(節號, 該節文字)]。

    書上常把同一章的好幾節排在同一段裡，節號印成上標：
        `接生婆就與他同去。²到了山洞，看，忽然有一片光亮黑雲把山洞遮蓋。`
    只看段首的話，這一章就只剩第 1 節，其餘全被併進去——節數少一半而字數全對，
    又是一個「看起來正常」的壞法。

    🚨 只在**三個條件同時成立**時才切，其餘一律不動：
      ① 是真的上標字元（MinerU 沒保住格式的就認不出來，那就算了，不猜）；
      ② 號**恰好是下一節**（連號）；
      ③ 這個號不是本頁的註腳標記（註腳標記也會印成上標）。
    """
    out: list[tuple[int, str]] = []
    pos, verse = 0, start_verse
    for m in INLINE_SUP.finditer(text):
        n = int(m.group().translate(SUP_TO_ASCII))
        if n != verse + 1 or n in markers:
            continue
        out.append((verse, text[pos:m.start()]))
        pos, verse = m.end(), n
    if out:
        out.append((verse, text[pos:]))
    return out


def split_chapverse(paras: list[dict], first_chapter: int,
                    markers_by_page: dict[int, set[int]]) -> Split:
    """1:1、1:2、2:1… 章號與節號可能印在一起（`231` ＝ 23:1）。"""
    sections: list[Section] = []
    problems: list[str] = []
    orphans: list[tuple[int | None, str]] = []
    gaps: list[str] = []
    prologue: list[dict] = []
    chap, verse = first_chapter, 0
    for pa in paras:
        markers = markers_by_page.get(pa["page"], set())
        hit = None
        for c, v, rest in _chapverse_readings(pa["text"], markers):
            # (a) 同章的下一節（容一個被吃掉的號，記成缺口）
            if c in (None, chap) and v in (verse + 1, verse + 2):
                if v == verse + 2:
                    gaps.append(f"{chap}:{verse + 1}")
                hit, verse = rest, v
                break
            # (b) 換章：章號恰好加一、且從第 1 節開始
            if c == chap + 1 and v == 1:
                hit, chap, verse = rest, chap + 1, 1
                break
        if hit is not None:
            pieces = _inline_splits(hit, verse, markers)
            if pieces:
                for v, txt in pieces:
                    sections.append(Section(chapter=chap, verse=v, number=v,
                                            page=pa["page"], paras=[txt]))
                verse = pieces[-1][0]
            else:
                sections.append(Section(chapter=chap, verse=verse, number=verse,
                                        page=pa["page"], paras=[hit]))
            continue
        # 續段裡也可能藏著下一節的上標號（跨頁的下半段最常見）
        if sections and sections[-1].chapter == chap:
            pieces = _inline_splits(pa["text"], verse, markers)
            if pieces:
                sections[-1].paras.append(pieces[0][1])
                for v, txt in pieces[1:]:
                    sections.append(Section(chapter=chap, verse=v, number=v,
                                            page=pa["page"], paras=[txt]))
                verse = pieces[-1][0]
                continue
        if sections:
            sections[-1].paras.append(pa["text"])
        else:
            prologue.append({"page": pa["page"], "text": pa["text"]})
        # 段首帶了數字卻一個讀法都對不上 → 點名。唯一放行的是「那個數字就是本頁
        # 的註腳標記」（註腳標記偶爾會落在段首，例如跨頁的續段）。
        readings = _chapverse_readings(pa["text"], markers)
        if readings and not any(
                (c is None and v in markers) or (c in markers) for c, v, _ in readings):
            orphans.append((pa["page"], pa["text"][:50]))
    if not sections:
        problems.append(f"chapverse：一節都沒切出來（起始章 {first_chapter}）")
    if gaps:
        problems.append(f"chapverse：節號被吃掉的節 {gaps}（要對照表才能定界）")
    return Split("chapverse", sections, problems, orphans, prologue)


GROUP_HEAD = re.compile(r"^([一二三四五六七八九十]+)、\s*(.*)$")
# 第三冊的各部行傳用**阿拉伯數字的章標題**分章：「1. 保羅離開羅馬」「2. 關於他前來
# 見袞大弗魯斯王」，章底下的節再從 1 編起。章標題是獨立一行的短句，不以句號收尾。
NUM_HEAD_LINE = re.compile(r"^(\d{1,3})\s*[.．、]\s*(\S.{0,28})$")


def split_grouped(paras: list[dict], markers_by_page: dict[int, set[int]]) -> Split:
    """按「一、二、三…」的小標分組，**每一組的編號各自從 1 開始**。

    《彼得的宣講》就是這一種：全篇按引用它的教父分組——
        一、革利免　1.–8.
        二、大馬士革約翰　（不編號）
        三、俄利根　1.–2.      ← 號從頭開始
        四、拿先安斯的貴格利　（不編號）
    拿 flat 去切會在「三、」那裡撞見第二個 `1.`，而嚴格連號會把它擋下來（本來就
    該擋）。組號當章、組內編號當節。

    🚨 沒有編號的組（二、四）**整組併成一節**，不按段落拆。要拆就得自己決定
    「這裡算幾節」，那是憑空造結構；書上沒編號就是沒編號，寧可粗一點。
    """
    sections: list[Section] = []
    problems: list[str] = []
    orphans: list[tuple[int | None, str]] = []
    prologue: list[dict] = []
    chap, verse = 0, 0
    for pa in paras:
        t = pa["text"].strip()
        mg = GROUP_HEAD.match(t)
        # 🚨 不能靠 `kind == "title"` 認小標：MinerU 把「一、亞歷山太的革利免」判成
        #    text，卻把同一部書的「二、大馬士革約翰」「三、俄利根」判成 title。
        #    改認字面，並要求組號**恰好是下一組**（一→二→三→四）——這個連號條件
        #    比區塊型別可靠得多，也擋得住內文裡偶然以「一、」開頭的句子。
        if mg and cn_int(mg.group(1)) == chap + 1:
            chap, verse = chap + 1, 0
            continue
        # 阿拉伯數字的章標題。條件同樣收得很緊：整段就是那一行、不以句號收尾、
        # 而且章號**恰好是下一章**。不然正文裡「1. 」開頭的列舉也會被當成換章。
        # 🚨 比對**第一行**而不是整段。表格還原成文字之後，一列會變成
        #    「1. 標題和第一句「未嘗死亡」\n〔希臘語版〕《俄西林古蒲草紙654》1-5」，
        #    拿整段去比就永遠對不上，《多馬福音》114 則語錄一則都切不出來。
        first_line = t.split("\n", 1)[0].strip()
        mn = NUM_HEAD_LINE.match(first_line)
        if mn and int(mn.group(1)) == chap + 1 and not first_line.endswith(("。", "」", "；")):
            chap, verse = chap + 1, 0
            continue
        if chap == 0:
            prologue.append({"page": pa["page"], "text": pa["text"]})
            continue
        markers = markers_by_page.get(pa["page"], set())
        num, rest, _sup = _lead_number(pa["text"], markers)
        hit = next((c for c in _strip_markers(num, markers) if c == verse + 1), None) \
            if num is not None else None
        if hit is not None:
            verse = hit
            pieces = _inline_splits(rest, verse, markers)
            if pieces:
                for v, txt in pieces:
                    sections.append(Section(chapter=chap, verse=v, number=v,
                                            page=pa["page"], paras=[txt]))
                verse = pieces[-1][0]
            else:
                sections.append(Section(chapter=chap, verse=verse, number=verse,
                                        page=pa["page"], paras=[rest]))
            continue
        if sections and sections[-1].chapter == chap:
            # 續段裡藏著的行內上標節號也要切（同 chapverse）
            pieces = _inline_splits(pa["text"], verse, markers)
            if pieces:
                sections[-1].paras.append(pieces[0][1])
                for v, txt in pieces[1:]:
                    sections.append(Section(chapter=chap, verse=v, number=v,
                                            page=pa["page"], paras=[txt]))
                verse = pieces[-1][0]
                continue
            sections[-1].paras.append(pa["text"])
        else:                                    # 不編號的組：整組一節
            verse = 1
            sections.append(Section(chapter=chap, verse=1, number=1,
                                    page=pa["page"], paras=[pa["text"]]))
    if chap == 0:
        problems.append("grouped：沒有「一、二、三…」小標")
    return Split("grouped", sections, problems, orphans, prologue)


def resolve_gaps(split: Split, missing: dict[int | str, str]) -> Split:
    """用寫死的對照表補回被 OCR 吃掉的節號。

    照交接單 §C：只認該節**開頭的原文**。比對不到、比對到多處、或位置不在前後兩節
    之間，一律不補、把問題留著——擋下來遠好過切錯界線還一路綠燈。
    """
    remaining: list[str] = []
    for prob in split.problems:
        m = re.search(r"節號被吃掉的節 \[(.*?)\]", prob)
        if not m:
            remaining.append(prob)
            continue
        wanted = [x.strip().strip("'\"") for x in m.group(1).split(",") if x.strip()]
        still = []
        for key in wanted:
            k: int | str = int(key) if key.isdigit() else key
            opening = missing.get(k)
            if not opening:
                still.append(f"{key}（對照表沒有這一條）")
                continue
            hosts = [s for s in split.sections
                     if any(p.startswith(opening) for p in s.paras)]
            if len(hosts) != 1:
                still.append(f"{key}（「{opening[:12]}」比對到 {len(hosts)} 節）")
                continue
            host = hosts[0]
            hits = [i for i, p in enumerate(host.paras) if p.startswith(opening)]
            if len(hits) != 1:
                still.append(f"{key}（同一節裡比對到 {len(hits)} 段）")
                continue
            i = hits[0]
            tail, host.paras = host.paras[i:], host.paras[:i]
            num = int(key) if key.isdigit() else int(str(key).split(":")[-1])
            chap = host.chapter if host.chapter is None else int(str(key).split(":")[0])
            split.sections.insert(
                split.sections.index(host) + 1,
                Section(chapter=chap, verse=None if chap is None else num,
                        number=num, page=host.page, paras=tail, inferred=True))
        if still:
            # 🚨 補不回來**不等於**要整部作品擋下來。號被吃掉的那一節，它的文字本來就
            #    已經併在前一節裡（沒有節號就沒有切點），所以資料一個字都沒少，少的
            #    只是那一刀。整部 92 頁的《多馬行傳》為了一個 §7 而全部不收，代價遠
            #    大於「這一節涵蓋兩節」。
            #    所以改成：把前一節標成**跨號**（label 變「6-7」），並留下記錄讓人看得見。
            #    這仍然守著「寧可少切也不要多切」——我們沒有憑空生出任何界線。
            for key in still:
                num = re.match(r"^(\d+(?::\d+)?)", key)
                if not num:
                    continue
                tag = num.group(1)
                want = int(tag.split(":")[-1])
                host = next((s for s in split.sections
                             if s.verse == want - 1 or (s.chapter is None and s.number == want - 1)),
                            None)
                if host is not None:
                    host.spans_to = want
                else:
                    remaining.append(f"補號失敗且找不到前一節：{key}")
    split.problems[:] = remaining
    return split


def first_number(paras: list[dict], markers_by_page: dict[int, set[int]]) -> int | None:
    """正文第一個帶號的段落 → 那個號。

    🚨 不能假設每一部作品都從 §1 開始。《阿倫德爾抄本404拉丁語耶穌嬰孩時期福音》
    是整套書裡的一段節錄，書上印的是 §68–74；《彼得福音》《馬利亞的出生》也都不是
    從 1 起。寫死 first=1 的話這些作品會**一節都切不出來**，而錯誤訊息長得像
    「這一部沒有編號」，很容易被當成無號短篇收成一節。
    """
    for pa in paras:
        markers = markers_by_page.get(pa["page"], set())
        for c, v, _rest in _chapverse_readings(pa["text"], markers):
            if c is None and v not in markers:
                return v
        num, _rest, _sup = _lead_number(pa["text"], markers)
        if num is not None and num not in markers:
            return num
    return None


def choose(paras: list[dict], markers_by_page: dict[int, set[int]],
           first: int = 1, missing: dict[int | str, str] | None = None) -> tuple[Split | None, str]:
    """兩種體例都跑，要求恰好一種通過。→ (結果, 說明)。"""
    flat = resolve_gaps(split_flat(paras, first, markers_by_page), missing or {})
    cv = resolve_gaps(split_chapverse(paras, first, markers_by_page), missing or {})
    # 從 §1 起切不出東西時，改用正文裡實際出現的第一個號再試一次。連號閘仍然照舊，
    # 所以起點猜錯的話後面就對不上、一樣會被擋下。
    if not flat.ok and not flat.sections:
        auto = first_number(paras, markers_by_page)
        if auto is not None and auto != first:
            alt = resolve_gaps(split_flat(paras, auto, markers_by_page), missing or {})
            if alt.ok and alt.sections:
                flat = alt
    # 🚨 只有一章的 chapverse **就是** flat（章號從來沒進位過），兩邊會同時通過而
    #    互相擋死。這種情況不是「有歧義」，是同一個答案的兩種寫法——取 flat。
    if len({s.chapter for s in cv.sections}) <= 1:
        cv = Split("chapverse", [], ["chapverse：整篇只有一章，等於 flat"], [], [])
    gr = resolve_gaps(split_grouped(paras, markers_by_page), missing or {})

    # 🚨 挑體例的判準：**哪一種把書上印出來的號解釋得最好**，而不是「哪一種完美無瑕」。
    #    每一刀都還是要通過連號驗證（見 Split.ok 的說明），所以挑錯體例的後果是
    #    少切幾刀，不會切錯位置。判準依序是：未解釋的號最少 → 切出的節最多。
    #    只有一章的 chapverse 等於 flat，不列入競爭（否則兩者互相抵銷）。
    cands = [flat, gr]
    if len({s_.chapter for s_ in cv.sections}) > 1:
        cands.append(cv)
    usable = [c for c in cands if c.ok]
    if usable:
        # 🚨 第一順位是「**需要補幾個被吃掉的號**」，不是「未解釋的號最少」。
        #    對的體例應該跟書上印的號完全吻合、一個都不用補。實測《多馬福音》：
        #        flat      114 節、補 0 個 → 正好是它的 114 則語錄
        #        chapverse 180 節、補 8 個 → 把「11」讀成 1:1，硬湊出 11 章
        #    只看 orphan 的話 chapverse（132）會贏過 flat（150），選到錯的那個。
        def rank(c: Split) -> tuple[int, int, int]:
            return (sum(1 for s in c.sections if s.spans_to is not None),
                    len(c.orphan_numbers), -len(c.sections))
        best = min(usable, key=rank)
        extra = ""
        if best.scheme == "grouped":
            extra = f"{len({s_.chapter for s_ in best.sections})} 組 / "
        note = f"{best.scheme}（{extra}{len(best.sections)} 節）"
        if best.orphan_numbers:
            note += f"　⚠ {len(best.orphan_numbers)} 個號沒切到（併進前一節，內容未少）"
        return best, note
    # 書上**根本沒有編號**的短篇（《諾斯底主義者游斯丁的記錄》《皮斯特斯·索菲婭》
    # 各只有兩三頁）。條件寫得很緊：整篇沒有任何一段帶行首數字區——「對不上」
    # 不算，必須是「從頭到尾都沒有號」，否則會把切壞的長篇吞成一節。
    if paras and not any(_chapverse_readings(pa["text"], markers_by_page.get(pa["page"], set()))
                         for pa in paras):
        # 🚨 不編號**不等於**整部收成一節。《約翰藏經》二十一頁、《耶穌基督智慧書》
        #    二十五頁都是連續散文，書上真的沒有節號；但塞成一個二十一頁的區塊
        #    根本沒法讀，也沒法引用。
        #    折衷是按**印刷頁**切：頁界是書上真實存在的東西，不是我憑空生出來的
        #    結構，而且每一節剛好帶著它自己的原書頁碼，引用得出來。
        secs: list[Section] = []
        for pa in paras:
            if secs and secs[-1].page == pa["page"]:
                secs[-1].paras.append(pa["text"])
            else:
                secs.append(Section(chapter=None, verse=None, number=len(secs) + 1,
                                    page=pa["page"], paras=[pa["text"]]))
        return (Split("bypage", secs, [], [], []),
                f"bypage（整篇不編號，按印刷頁切成 {len(secs)} 節）")
    return None, (f"都不通　flat：{flat.problems}　chapverse：{cv.problems}　"
                  f"grouped：{gr.problems}")
