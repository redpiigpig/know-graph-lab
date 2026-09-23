# -*- coding: utf-8 -*-
"""J-STAGE 論文 PDF 的文字層 → 按原書版面接回的段落（帶真頁碼）。

J-STAGE 替舊期刊掃描本加的文字層**字是對的、順序是壞的**：
直排（縦書き）的頁面，`page.get_text()` 回來是一字一行，
而且《日本の神学》這類刊物是**上下兩段排**（每行 28 字、上段讀完才讀下段），
逐行串起來會把上下兩段交錯在一起。所以這裡不信任文字層的閱讀順序，
改用每個字的座標自己重排：

  直排：字 → 依 x 中心分「直行」→ 直行內依 y 缺口切「段」（上段／下段）
        → 段別（tier）由上而下、同一段內直行由右而左。
  橫排：字 → 依 y 分「橫行」→ 由上而下、行內由左而右。

分段規則（兩種排版共用同一個道理）：
  * 行首比同段其他行低一字（縮排）→ 新段落開始。
  * 上一行提早結束（沒排滿）→ 上一段在那裡結束。
兩條都要：只有縮排會把「標題＋下一行正文」黏成一段，只有提早結束會漏掉
「最後一行剛好排滿」的段落。

頁碼：J-STAGE 的 PDF 從該文起始頁開始，第 i 頁＝`start_page + i`。
寫進每段的 `page`，是該段**開始**那一頁（跨頁段落記起頭那頁，引用慣例如此）。
"""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass

_DIGITS = re.compile(r"^[\s0-9０-９一二三四五六七八九十〇・\-—–()（）]*$")


@dataclass
class Ch:
    x0: float
    y0: float
    x1: float
    y1: float
    c: str
    size: float

    @property
    def xc(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def yc(self) -> float:
        return (self.y0 + self.y1) / 2


def page_chars(page) -> tuple[list[Ch], bool]:
    """回傳 (字列表, 是否直排)。直排判準：多數字所在的 line 方向是 (0,1)。"""
    chars: list[Ch] = []
    vert = horiz = 0
    for b in page.get_text("rawdict")["blocks"]:
        for ln in b.get("lines", []):
            dx, dy = ln.get("dir", (1, 0))
            n = sum(len(s["chars"]) for s in ln["spans"])
            if abs(dy) > abs(dx):
                vert += n
            else:
                horiz += n
            for s in ln["spans"]:
                for c in s["chars"]:
                    if c["c"].strip():
                        x0, y0, x1, y1 = c["bbox"]
                        chars.append(Ch(x0, y0, x1, y1, c["c"], s["size"]))
    # 一字一行的 line 通常 dir 仍是 (1,0)——所以再看幾何：多數 line 只有一個字就是直排。
    if vert <= horiz:
        one = sum(1 for b in page.get_text("rawdict")["blocks"] for ln in b.get("lines", [])
                  if sum(len(s["chars"]) for s in ln["spans"]) == 1)
        allines = sum(1 for b in page.get_text("rawdict")["blocks"] for ln in b.get("lines", []))
        is_vert = allines > 20 and one / max(allines, 1) > 0.6
    else:
        is_vert = True
    return chars, is_vert


def _cluster(values: list[float], tol: float) -> list[list[int]]:
    """把一維座標按間距分群，回傳各群的索引（依座標遞增）。"""
    order = sorted(range(len(values)), key=lambda i: values[i])
    groups: list[list[int]] = []
    last = None
    for i in order:
        if last is None or values[i] - last > tol:
            groups.append([i])
        else:
            groups[-1].append(i)
        last = values[i]
    return groups


@dataclass
class Line:
    text: str
    start: float    # 直排＝行頂 y；橫排＝行首 x
    end: float      # 直排＝行底 y；橫排＝行尾 x
    tier: int = 0
    page: int = 0
    spaced: bool = False    # 字距拉開的署名／標題：前後都強制斷段


def _segments(chars: list[Ch], h: float, w: float) -> list[tuple[float, list[Ch]]]:
    segs: list[tuple[float, list[Ch]]] = []
    for g in _cluster([c.xc for c in chars], tol=w * 0.45):
        col = sorted((chars[i] for i in g), key=lambda c: c.y0)
        cur = [col[0]]
        for c in col[1:]:
            if c.y0 - cur[-1].y1 > h * 1.6:
                segs.append((statistics.mean(x.xc for x in cur), cur))
                cur = [c]
            else:
                cur.append(c)
        segs.append((statistics.mean(x.xc for x in cur), cur))
    return segs


def body_frame(chars: list[Ch]) -> list[Ch]:
    """只留版心裡的字。

    書眉（篇名、評者姓氏、頁碼）印在版心外的角落，而它跟最近的正文直行 x 幾乎
    一樣，分行時會被併進那一行的行尾——結果段落結尾多出一個「望」「並」「西」
    （實測 399 個「句尾不完整」的段落多半是這個）。版心由**長直行**決定：
    取長度 ≥10 字的直行，它們頂／底的分位數就是版心上下緣。"""
    if len(chars) < 40:
        return chars
    h = statistics.median(c.y1 - c.y0 for c in chars) or 7
    w = statistics.median(c.x1 - c.x0 for c in chars) or 7
    long = [cs for _, cs in _segments(chars, h, w) if len(cs) >= 10]
    if len(long) < 3:
        return chars
    tops = sorted(cs[0].y0 for cs in long)
    bots = sorted(cs[-1].y1 for cs in long)
    xs = sorted(statistics.mean(c.xc for c in cs) for cs in long)
    ymin, ymax = tops[len(tops) // 10] - h * 0.8, bots[len(bots) * 9 // 10] + h * 0.8
    xmin, xmax = xs[0] - w * 2, xs[-1] + w * 2
    return [c for c in chars if ymin <= c.yc <= ymax and xmin <= c.xc <= xmax]


def tier_separators(chars: list[Ch], h: float, w: float | None = None) -> list[float]:
    """上下段排的分界 y。

    不能要求「整頁橫向都是空白」：只要有一個標題或署名跨在兩段之間（1996 年那組
    書評的「Ⅳ諸書 秋吉輝雄」），那條空白帶就不存在，上段與下段的直行會被接成
    同一行（實測「…の最終巻である『」是上段行尾接下段行頭）。
    改成**投票**：各直行自己的缺口（>1.2 字）落在哪個 y；三成以上的直行
    在同一個 y 都有缺口，那裡就是分界。"""
    w = w or (statistics.median(c.x1 - c.x0 for c in chars) if chars else 7)
    cols = []
    for g in _cluster([c.xc for c in chars], tol=w * 0.45):
        col = sorted((chars[i] for i in g), key=lambda c: c.y0)
        if len(col) >= 6:
            cols.append([(a.y1, b.y0) for a, b in zip(col, col[1:]) if b.y0 - a.y1 > h * 1.2])
    if len(cols) < 4:
        return []
    cands = sorted({round((a + b) / 2) for gaps in cols for a, b in gaps})
    need = max(3, int(len(cols) * 0.3))
    hits = [y for y in cands if sum(any(a <= y <= b for a, b in gaps) for gaps in cols) >= need]
    seps: list[float] = []
    for y in hits:                                   # 相鄰的候選併成一條
        if seps and y - seps[-1][-1] <= h * 2:
            seps[-1].append(y)
        else:
            seps.append([y])
    return [statistics.mean(g) for g in seps]


def column_separators(chars: list[Ch], w: float, h: float) -> list[float]:
    """橫排雙欄（《新約学研究》）的欄界 x：與 tier_separators 對稱，
    各橫行自己的缺口（>1.5 字）投票。"""
    rows = []
    for g in _cluster([c.yc for c in chars], tol=h * 0.45):
        row = sorted((chars[i] for i in g), key=lambda c: c.x0)
        if len(row) >= 6:
            rows.append([(a.x1, b.x0) for a, b in zip(row, row[1:]) if b.x0 - a.x1 > w * 1.5])
    if len(rows) < 6:
        return []
    cands = sorted({round((a + b) / 2) for gaps in rows for a, b in gaps})
    need = max(4, int(len(rows) * 0.4))
    hits = [x for x in cands if sum(any(a <= x <= b for a, b in gaps) for gaps in rows) >= need]
    seps: list[list[float]] = []
    for x in hits:
        if seps and x - seps[-1][-1] <= w * 2:
            seps[-1].append(x)
        else:
            seps.append([x])
    return [statistics.mean(g) for g in seps]


def vertical_lines(chars: list[Ch]) -> list[Line]:
    if not chars:
        return []
    chars = body_frame(chars)
    h = statistics.median(c.y1 - c.y0 for c in chars) or 7
    w = statistics.median(c.x1 - c.x0 for c in chars) or 7
    seps = tier_separators(chars, h, w)
    segs: list[tuple[float, list[Ch]]] = []          # (x 中心, 字)
    spaced_ids: set[int] = set()
    for g in _cluster([c.xc for c in chars], tol=w * 0.45):
        col = sorted((chars[i] for i in g), key=lambda c: c.y0)
        pieces: list[list[Ch]] = [[col[0]]]
        for c in col[1:]:
            if c.y0 - pieces[-1][-1].y1 > h * 1.6:
                pieces.append([c])
            else:
                pieces[-1].append(c)
        # 字距拉開排的署名／標題（「並　木　浩　一」）：每個字都被缺口切開，
        # 成了一串一兩字的碎片。整串併回一行並標成獨立段落——否則那個字會
        # 黏到上一段的結尾（實測「…位置並」「…根時」）。
        if len(pieces) >= 2 and all(len(pp) <= 2 for pp in pieces):
            spaced_ids.add(len(segs))
            segs.append((statistics.mean(x.xc for x in col), col))
            continue
        # 只在「上下段分界」切直行。行內的缺口（橫躺的拉丁字、空格、夾註）不算：
        # 那裡一切，後半截的行頂就比版心低，被當成縮排而另起一段
        # （實測「…その信仰と学」｜「こへ」）。
        parts: list[list[Ch]] = [[]]
        for c in col:
            if parts[-1] and any(parts[-1][-1].yc < sep < c.yc for sep in seps):
                parts.append([])
            parts[-1].append(c)
        for pp in parts:
            segs.append((statistics.mean(x.xc for x in pp), pp))
    # 段別：以段頂 y 分群（上段 y≈76、下段 y≈317 那種）
    tops = [s[1][0].y0 for s in segs]
    tiers = _cluster(tops, tol=h * 6)
    tier_of = {}
    for t, g in enumerate(tiers):
        for i in g:
            tier_of[i] = t
    lines = []
    for i, (xc, cs) in enumerate(segs):
        lines.append(Line("".join(c.c for c in cs), cs[0].y0, cs[-1].y1, tier_of[i],
                          spaced=i in spaced_ids))
        lines[-1]._x = xc  # type: ignore[attr-defined]
    lines.sort(key=lambda ln: (ln.tier, -ln._x))     # type: ignore[attr-defined]
    return lines


def horizontal_lines(chars: list[Ch]) -> list[Line]:
    """橫排：先依欄界分欄（左欄讀完才讀右欄），欄內依 y 分行、行內由左而右。"""
    if not chars:
        return []
    h = statistics.median(c.y1 - c.y0 for c in chars) or 9
    w = statistics.median(c.x1 - c.x0 for c in chars) or 6
    seps = column_separators(chars, w, h)
    bands: list[list[Ch]] = [[] for _ in range(len(seps) + 1)]
    for c in chars:
        bands[sum(c.xc > x for x in seps)].append(c)
    out = []
    for col_i, band in enumerate(bands):
        if not band:
            continue
        for g in _cluster([c.yc for c in band], tol=h * 0.45):
            row = sorted((band[i] for i in g), key=lambda c: c.x0)
            txt = ""
            for a, b in zip([None] + row[:-1], row):
                if a is not None and b.x0 - a.x1 > (b.x1 - b.x0) * 0.25 and not ("　" <= b.c <= "鿿"):
                    txt += " "
                txt += b.c
            out.append(Line(txt, row[0].x0, row[-1].x1, col_i))
    return out


def body_filter(lines: list[Line], vertical: bool) -> list[Line]:
    """丟掉頁碼、書眉這類極短的孤行（只剩數字／符號）。"""
    return [ln for ln in lines if not (len(ln.text) <= 4 and _DIGITS.match(ln.text))]


def paragraphs(pages: list[tuple[list[Line], bool]], start_page: int) -> list[tuple[str, int]]:
    """把各頁的行接成段落。回傳 [(段落文字, 起始頁碼)]。"""
    out: list[tuple[str, int]] = []
    cur, cur_page = "", None
    prev_short = True
    for pi, (lines, vertical) in enumerate(pages):
        if not lines:
            continue
        # 每個 tier 各自的行頂／行底基準（取眾數附近：多數行都排滿）
        by_tier: dict[int, list[Line]] = {}
        for ln in lines:
            by_tier.setdefault(ln.tier, []).append(ln)
        base = {}
        for t, ls in by_tier.items():
            starts = sorted(l.start for l in ls)
            ends = sorted(l.end for l in ls)
            base[t] = (starts[len(starts) // 4], ends[len(ends) * 3 // 4])
        unit = statistics.median(
            (l.end - l.start) / max(len(l.text), 1) for l in lines if len(l.text) > 5) if any(
            len(l.text) > 5 for l in lines) else 8
        for ln in lines:
            s0, e0 = base[ln.tier]
            indented = ln.start - s0 > unit * 0.6
            if (indented or prev_short or ln.spaced) and cur:
                out.append((cur, cur_page))
                cur, cur_page = "", None
            if not cur:
                cur_page = start_page + pi
            joiner = " " if (not vertical and cur and re.search(r"[A-Za-z,.;:]$", cur)) else ""
            if not vertical and cur.endswith("-") and re.match(r"[a-zäöü]", ln.text):
                cur = cur[:-1]
                joiner = ""
            cur += joiner + ln.text
            prev_short = ln.spaced or e0 - ln.end > unit * 1.5
    if cur:
        out.append((cur, cur_page))
    return out


def _norm(t: str) -> str:
    return re.sub(r"[\s0-9０-９一二三四五六七八九十〇.,・\-—–ー()（）!！|｜]", "", t)


def drop_running_heads(pages: list[tuple[list[Line], bool]]) -> list[tuple[list[Line], bool]]:
    """書眉＝在兩頁以上重複出現的短行（去掉數字後相同）。

    《日本學士院紀要》每頁都印著篇名＋頁碼，不拿掉就會插在跨頁的句子中間，
    把一段話切成兩段（實測：「…一番内容のある山本正」｜書眉｜「雄…」）。
    OCR 對同一個書眉每頁讀得不太一樣（ユーモア→ユ!モア），所以比對的是
    去掉數字與雜符號之後的字串。"""
    from collections import Counter
    cnt: Counter = Counter()
    for lines, _ in pages:
        for k in {_norm(ln.text) for ln in lines if len(ln.text) <= 40}:
            if len(k) >= 3:
                cnt[k] += 1
    heads = {k for k, n in cnt.items() if n >= 2}
    return [([ln for ln in lines if not (len(ln.text) <= 40 and _norm(ln.text) in heads)], v)
            for lines, v in pages]


def merge_spaced_titles(paras: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """字距拉開排的標題（「旧　約　学」）每個字自成一行，會變成一字一段。連續的
    一兩字段落併回一段。"""
    out: list[tuple[str, int]] = []
    for t, pg in paras:
        if out and len(t) <= 2 and len(out[-1][0]) <= 12 and out[-1][1] == pg and not re.search(r"[。．.」）)]$", out[-1][0]):
            out[-1] = (out[-1][0] + t, pg)
        else:
            out.append((t, pg))
    return out


_END = re.compile(r"[。．.」）)』!?？！:：｡｣]$")
_HEADLIKE = re.compile(r"^(註|注|\(?[0-9０-９]+\)|[一二三四五六七八九十]+[、　 ]|[IVXⅠⅡⅢⅣⅤ]+[.\s　]|§)")


def join_broken(paras: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """正文段落幾乎一定以句號收尾。長段落（≥60 字）沒有句尾、下一段又不像
    標題或註號開頭 → 是被版面切斷的同一段，接回去。

    分段規則在直行中夾著橫躺的拉丁字、上下段交界、換頁時仍會誤切；這一道是
    最後的保險。短段落（標題、署名、書目）不動，它們本來就沒有句號。"""
    out: list[tuple[str, int]] = []
    for t, pg in paras:
        if out and len(out[-1][0]) >= 60 and not _END.search(out[-1][0]) and not _HEADLIKE.match(t):
            prev, ppg = out[-1]
            sep = " " if re.search(r"[A-Za-z]$", prev) and re.match(r"[A-Za-z]", t) else ""
            out[-1] = (prev + sep + t, ppg)
        else:
            out.append((t, pg))
    return out


def extract(pdf_path: str, start_page: int) -> list[tuple[str, int]]:
    import fitz
    doc = fitz.open(pdf_path)
    pages = []
    for pg in doc:
        chars, vert = page_chars(pg)
        lines = vertical_lines(chars) if vert else horizontal_lines(chars)
        pages.append((body_filter(lines, vert), vert))
    pages = drop_running_heads(pages)
    return join_broken(merge_spaced_titles(paragraphs(pages, start_page)))
