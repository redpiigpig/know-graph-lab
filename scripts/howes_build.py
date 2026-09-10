# -*- coding: utf-8 -*-
"""Build the standard Uchimura BIOGRAPHY into an en＋繁中 reader book.

John F. Howes, 《Japan's Modern Prophet: Uchimura Kanzō, 1861–1930》
(UBC Press, Asian Religions and Society series, 2005; 465pp) —— 五十年研究的成果，
2006 年 Canada-Japan Literary Award、Choice Outstanding Academic Title。這是內村
研究的英文定本，也是本 repo 第一本「寫內村的書」而非「內村寫的書」。

⚠️ 2005 年出版，**仍在著作權內**（私人站，沿用 [[feedback_jung_nonpd_english_first]]
的姿態）。譯前已查：**沒有任何內村傳記的中譯本**（REFERENCE-first 走完，查無），
所以自譯。掛在 /collected-works 的內村 hub 底下，category「傳記與研究（他人著作）」。

來源是原生 PDF（Acrobat Distiller，有真的文字層，**不需要 OCR**），所以分段不是靠
空行，而是靠版面幾何：

  * 正文 x0≈37，段落首行縮排到 x0≈46   → 縮排＝新段落
  * 引文區塊字級 8.5（正文 9.0）        → 字級變化＝引文起訖，加 `> ` 標記
  * 書眉 8.0（y≈36）、章名 18.0、"This page intentionally left blank" 12.0 → 丟
  * 尾註號是 superscript span（flags bit 0，字級 5.2）→ 丟，不然會混進譯文

只譯正文（序言→結論，PDF p12–417）。**Notes／Selected Bibliography／Index 不譯**
（是檢索用的裝置，不是散文）；Chronology／Glossary 是兩欄表格，內村 hub 自己已有
年表，一併略過。

純函式鎖在 scripts/tests/test_howes_build.py；translate/build/upload 沿用
uchimura_auto.py --author howes。

  python scripts/howes_build.py --dry
  python scripts/uchimura_auto.py --author howes --run-queue --backend haiku
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import uchimura_build as ub  # noqa: E402  (loads .env, reconfigures stdout; clean_zh_output reused)

PDF_PATH = Path("c:/tmp/uchimura_cache/howes_japans_modern_prophet.pdf")
SOURCE_LANG = "en"
AUTHOR_ZH = "約翰‧F‧豪斯"
AUTHOR_EN = "John F. Howes"
CATEGORY = "神學"
DATA_DIRNAME = "howes_data"

# ── Registry ─────────────────────────────────────────────────────────────────
# Page ranges are 1-based PDF pages [start, end) taken from the PDF's own
# embedded TOC. Part title pages (34–35, 176–177, 274–275) fall between sections
# and are simply not covered by any range.
REGISTRY: dict[str, dict] = {
    "howes-prophet": {
        "ebook_id": "d0000000-0000-4000-8000-000000000009",
        "title": "日本的現代先知：內村鑑三 1861–1930",
        "original_title": "Japan's Modern Prophet: Uchimura Kanzō, 1861–1930",
        "subtitle": "豪斯的內村鑑三評傳‧英文定本（英文原著＋繁中對照）",
        "year": 2005,
        "parent_volume": "傳記與研究",
        "sections": [
            {"title_zh": "序言與致謝", "heading": "Preface and Acknowledgments",
             "start": 12, "end": 20},
            {"title_zh": "導論", "heading": "Introduction", "start": 20, "end": 34},
            # Part 1: I Refuse（我拒絕）
            {"title_zh": "第一章　一個明治武士的教育",
             "heading": "1 Education of a Meiji Samurai", "start": 36, "end": 63},
            {"title_zh": "第二章　初任文官", "heading": "2 Budding Civil Servant",
             "start": 63, "end": 95},
            {"title_zh": "第三章　一個作家的誕生", "heading": "3 Birth of a Writer",
             "start": 95, "end": 121},
            {"title_zh": "第四章　為己辯護，也為國辯護",
             "heading": "4 Justification of Self and of Nation", "start": 121, "end": 154},
            {"title_zh": "第五章　走入世界", "heading": "5 Out into the World",
             "start": 154, "end": 176},
            # Part 2: The Pact with God（與神立約）
            {"title_zh": "第六章　由路德主持", "heading": "6 With Luther Presiding",
             "start": 178, "end": 200},
            {"title_zh": "第七章　受教的人", "heading": "7 The Taught", "start": 200, "end": 222},
            {"title_zh": "第八章　所教之道：基督教與聖經",
             "heading": "8 The Teaching: Christianity and the Bible", "start": 222, "end": 238},
            {"title_zh": "第九章　所教之道：制度與個人",
             "heading": "9 The Teaching: Institutions and Individuals", "start": 238, "end": 256},
            {"title_zh": "第十章　最後的機會", "heading": "10 The Last Chance",
             "start": 256, "end": 274},
            # Part 3: I Am Not（我不是）
            {"title_zh": "第十一章　基督將要再臨", "heading": "11 Christ Is Coming",
             "start": 276, "end": 299},
            {"title_zh": "第十二章　聖經與日本", "heading": "12 The Bible and Japan",
             "start": 299, "end": 328},
            {"title_zh": "第十三章　賢者", "heading": "13 The Sage", "start": 328, "end": 339},
            {"title_zh": "第十四章　數落西方", "heading": "14 Telling Off the West",
             "start": 339, "end": 364},
            {"title_zh": "第十五章　長成的毒蛇", "heading": "15 Maturing Vipers",
             "start": 364, "end": 382},
            {"title_zh": "第十六章　何謂無教會？", "heading": "16 What Is Mukyôkai?",
             "start": 382, "end": 400},
            {"title_zh": "結論：歷史中的內村鑑三",
             "heading": "Conclusion: Uchimura Kanzô in History", "start": 400, "end": 418},
        ],
    },
}

QUEUE = ["howes-prophet"]

# ── PDF line geometry ────────────────────────────────────────────────────────
BODY_SIZE = 9.0      # 正文
QUOTE_SIZE = 8.5     # 引文區塊
# 正文行的 x0 只有三個值：36.7 續行／45.7 段落首行／48.7 編號清單的懸掛縮排續行。
# 只差 3pt，但意思相反——把 48.7 當成「縮排＝新段落」會把一整段編號清單炸成一行一段
# （第九章那份 précis 就是這樣壞掉的）。所以是一個區間，不是一個門檻。
INDENT_LO, INDENT_HI = 43.0, 47.0
DROP_SIZES = {8.0, 12.0, 18.0}  # 書眉／空白頁註記／章名（章名我們自己給）
MIN_SPAN_SIZE = 6.5  # 小於此＝上標尾註號
# 書中六十處裝飾字元在字型裡對到 U+0001，get_text 就原樣吐出來
_CTRL_RE = re.compile("[\x00-\x1f\x7f]")


# 印刷頁碼（folio）。書眉那一行是 size 8.0、y≈36、緊貼版心外緣，內容不是章名就是
# 頁碼；純數字（正文 1–398）或純羅馬數字（前言 vii–xvi）才算。
# 🚨 章首頁按慣例不印書眉，所以**抓不到頁碼是常態不是例外**，要由前一頁遞推。
_FOLIO_RE = re.compile(r"^(?:\d{1,3}|[ivxlcdm]{1,7})$", re.I)
HEAD_Y_MAX = 50.0    # 書眉的 y 上限（正文首行 y≈78）


def folio_of(lines: list[dict]) -> str | None:
    """一頁的版面行 → 印刷頁碼字串（'21'／'xii'），沒印就 None。"""
    for ln in lines:
        if ln.get("y", 999) > HEAD_Y_MAX or round(ln.get("size", 0), 1) != 8.0:
            continue
        t = (ln.get("text") or "").strip()
        if _FOLIO_RE.match(t):
            return t
    return None


def folio_int(folio: str | None) -> int | None:
    """'21'→21；'xii'→None（羅馬頁碼進不了 page_number 這個整數欄，寧可留 None
    也不要換算成阿拉伯數字——前言的 xii 跟正文的 12 是**不同的兩頁**）。"""
    return int(folio) if folio and folio.isdigit() else None


def spans_to_text(spans: list[dict]) -> str:
    """一行的 spans → 文字，丟掉上標尾註號（flags bit 0＝superscript）。
    註號不丟的話會變成句中的裸數字，翻譯時被當成年份或數量譯出來。"""
    return _CTRL_RE.sub("", "".join(
        s["text"] for s in spans
        if not (s.get("flags", 0) & 1) and s.get("size", 9.0) >= MIN_SPAN_SIZE))


def keep_line(line: dict) -> bool:
    return bool(line["text"].strip()) and round(line["size"], 1) not in DROP_SIZES


def _is_quote(line: dict) -> bool:
    return abs(line["size"] - QUOTE_SIZE) < 0.2


# ── 表格 ─────────────────────────────────────────────────────────────────────
#
# 🚨 表格的字級跟引文一樣是 8.5，所以原本被 `_is_quote` 當成引文，整張表的每一列
#    再被 `paras_with_pages` 併成**一個段落**——出來就是
#    「> 表1 … > 《基督徒的慰藉》…一八九三年一月 > 《哥倫布功績》…」這種一長串。
#    表沒有了，只剩一堆大於號。
#
# 認表格的判準是**第二欄**：豪斯這本的表格右欄一律落在 x0≈271，正文與引文最右
# 只到 x0≈55。所以「8.5pt 且 x0 ≥ TABLE_COL_X」＝某一列的右欄；它跟左欄同屬一列
# （y 差在 ROW_Y_TOL 內，PDF 裡兩者只差 0.3）。
#
# 全書（序言→結論）只有兩張表：PDF p107 的「Table 1 主要著作年表」與 p218。
TABLE_COL_X = 200.0
ROW_Y_TOL = 3.0
# 同一個儲存格內換行的行距（實測 10.8）比列與列之間（16）小，比表題到首列
# （20.7）更小。往前收左欄時就用這個門檻收手——不然表題會被吃進第一列的左欄，
# 變成「Table 1 Major works published… Consolations of a Christian | January 1893」。
CELL_LINE_GAP = 13.0


def table_runs(lines: list[dict]) -> list[tuple[int, int]]:
    """回傳 [(起, 迄)] ——每一段連續的表格行在 lines 裡的區間（迄不含）。

    起點取**該表第一列左欄**那一行，不是表題：表題與說明行在第一個右欄出現之前，
    照樣當普通段落走。"""
    runs = []
    i = 0
    while i < len(lines):
        if lines[i].get("x0", 0) >= TABLE_COL_X and _is_quote(lines[i]):
            floor = runs[-1][1] if runs else 0
            start = i
            while start - 1 >= floor and _is_quote(lines[start - 1]) and \
                    lines[start - 1].get("x0", 0) < TABLE_COL_X and \
                    abs(lines[start].get("y", 0) - lines[start - 1].get("y", 0)) < CELL_LINE_GAP:
                start -= 1
            j = i
            while j < len(lines) and _is_quote(lines[j]):
                j += 1
            runs.append((start, j))
            i = j
        else:
            i += 1
    return runs


def rows_from_lines(lines: list[dict]) -> list[tuple[str, str]]:
    """一段表格行 → [(左欄, 右欄)]。左欄可跨行（書名太長會折到下一行）。"""
    rows: list[tuple[str, str]] = []
    buf: list[str] = []
    for ln in lines:
        t = (ln.get("text") or "").strip()
        if not t:
            continue
        if ln.get("x0", 0) >= TABLE_COL_X:
            rows.append((" ".join(buf).strip(), t))
            buf = []
        else:
            buf.append(t)
    if buf:                       # 收尾沒有右欄的殘行（表註）自成一列
        rows.append((" ".join(buf).strip(), ""))
    return rows


_MONTHY = re.compile(r"\b(January|February|March|April|May|June|July|August|"
                     r"September|October|November|December)\b.*\d{4}|\d{4}", re.I)


def retable(flat: str, n_rows: int) -> str:
    """把被壓成一行的譯文表格還原成多行。

    🚨 引擎會把 markdown 表格回成**一整行**（`| 著作 | 時間 | | --- | --- | | … |`），
    而下游的 `clean_zh_output` 也會把換行收成空白。表格內容其實是對的，壞的只有
    換行——所以不必重譯，切回去就好。

    切法：整串以 `|` 分開之後，第一個元素是行首的空字串，其餘**每三個一組**
    （儲存格一、儲存格二、列與列之間那個空字串）。列數對不上就原樣退回——
    寧可留著一行難看的表，也不要切出一張錯位的表。"""
    if chr(10) in (flat or ""):
        return flat                      # 引擎有保留換行，不必動
    toks = (flat or "").split("|")
    if len(toks) < 4:
        return flat
    cells = [t.strip() for t in toks[1:]]
    rows = [cells[i:i + 2] for i in range(0, len(cells), 3)]
    rows = [r for r in rows if len(r) == 2]
    if len(rows) != n_rows:
        return flat
    return chr(10).join(f"| {a} | {b} |" for a, b in rows)


def table_markdown(rows: list[tuple[str, str]]) -> str:
    """[(左, 右)] → markdown 表格。

    原表沒有表頭列，所以表頭要自己判：右欄多半是年月＝著作年表，給
    「著作｜時間」；否則留空（例：第七章那首和歌的英譯／羅馬字對照，
    給它「條目｜時間」會變成錯的標籤）。"""
    dated = sum(1 for _l, r in rows if r and _MONTHY.search(r))
    head = ("| 著作 | 時間 |" if rows and dated >= len(rows) * 0.5
            else "|  |  |")
    out = [head, "| --- | --- |"]
    for left, right in rows:
        out.append(f"| {left.replace('|', '｜')} | {right.replace('|', '｜')} |")
    return chr(10).join(out)


def paras_with_pages(lines: list[dict]) -> list[tuple[str, str | None]]:
    """版面行 → [(段落, 該段起始的印刷頁碼)]。

    縮排或引文起訖＝斷段；行尾連字號接回；引文加 `> `。頁碼取**段落第一行所在的頁**
    ——跨頁的段落算在它開始的那一頁，這是引註的通例（"pp. 21-22" 由讀者自己補）。"""
    kept = [ln for ln in lines if keep_line(ln)]
    runs = table_runs(kept)
    in_run = {}
    for a, b in runs:
        for k in range(a, b):
            in_run[k] = (a, b)

    paras: list[list[str]] = []
    kinds: list[bool] = []
    pages: list[str | None] = []
    ready: list[str | None] = []      # 已成形的段落（表格）就直接放這裡
    prev_quote: bool | None = None
    i = 0
    while i < len(kept):
        if i in in_run and in_run[i][0] == i:
            a, b = in_run[i]
            md = table_markdown(rows_from_lines(kept[a:b]))
            paras.append([md])
            kinds.append(False)       # 表格不加 `> `
            ready.append(md)
            pages.append(kept[a].get("page"))
            prev_quote = None
            i = b
            continue
        ln = kept[i]
        text = ln["text"].strip()
        quote = _is_quote(ln)
        indented = INDENT_LO <= ln["x0"] <= INDENT_HI
        starts = (not paras) or ready[-1] is not None or \
            quote != prev_quote or (not quote and indented)
        if starts:
            paras.append([text])
            kinds.append(quote)
            ready.append(None)
            pages.append(ln.get("page"))
        else:
            buf = paras[-1]
            if buf[-1].endswith("-"):
                buf[-1] = buf[-1][:-1] + text
            else:
                buf.append(text)
        prev_quote = quote
        i += 1

    out: list[tuple[str, str | None]] = []
    for parts, quote, pg, done in zip(paras, kinds, pages, ready):
        if done is not None:
            out.append((done, pg))    # 表格原樣輸出，不可壓成一行
            continue
        s = re.sub(r"\s{2,}", " ", " ".join(parts)).strip()
        if s:
            out.append((f"> {s}" if quote else s, pg))
    return out


def lines_to_paras(lines: list[dict]) -> list[str]:
    """`paras_with_pages` 只取段落文字的舊介面。"""
    return [t for t, _pg in paras_with_pages(lines)]


def page_lines(page) -> list[dict]:
    """PyMuPDF page → [{x0,y,size,text}]，依閱讀順序（先 y 後 x；章名區塊在 PDF
    裡不一定排在正文之前，不排就會把章名插到頁中間）。"""
    lines = []
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b["lines"]:
            if not ln["spans"]:
                continue
            lines.append({"x0": ln["bbox"][0], "y": ln["bbox"][1],
                          "size": ln["spans"][0]["size"],
                          "text": spans_to_text(ln["spans"])})
    lines.sort(key=lambda l: (round(l["y"] / 3), l["x0"]))
    folio = folio_of(lines)
    for ln in lines:
        ln["page"] = folio
    return lines


def fill_folios(raw: list[str | None]) -> list[str | None]:
    """章首頁沒印書眉 → 頁碼是 None。由鄰頁遞推補回（只推阿拉伯數字）。

    先順推再逆推：逆推那一趟是為了**該節第一頁**——它多半就是章首頁，前面沒有東西
    可以推，只能由下一頁減一。羅馬頁碼不做算術（vii+1 不是 viii 這種事交給前一頁
    自己印的字），推不出來就留 None——[[feedback_transcribe_page_numbers]]：
    沒有真頁碼寧可 null，不可捏。"""
    out = list(raw)
    for i in range(1, len(out)):
        if out[i] is None and out[i - 1] and out[i - 1].isdigit():
            out[i] = str(int(out[i - 1]) + 1)
    for i in range(len(out) - 2, -1, -1):
        if out[i] is None and out[i + 1] and out[i + 1].isdigit() and int(out[i + 1]) > 1:
            out[i] = str(int(out[i + 1]) - 1)
    return out


def split_long_pairs(pairs: list[tuple[str, str | None]],
                     max_chars: int = 1800) -> list[tuple[str, str | None]]:
    """連續的引文段落之間沒有縮排可分（引文行 x0 全是 46），所以會黏成一大段——
    最長的一段有近九千字。按句界切開，`> ` 標記與頁碼每一片都要帶著。"""
    import uchimura_en_build as ueb
    out: list[tuple[str, str | None]] = []
    for p, pg in pairs:
        quoted = p.startswith("> ")
        body = p[2:] if quoted else p
        for piece in ueb.split_long_paras_en([body], max_chars=max_chars):
            out.append((f"> {piece}" if quoted else piece, pg))
    return out


def split_long(paras: list[str], max_chars: int = 1800) -> list[str]:
    """`split_long_pairs` 只取段落文字的舊介面。"""
    return [t for t, _pg in split_long_pairs([(p, None) for p in paras], max_chars)]


def load_work_sections(slug: str, pdf_path: Path = PDF_PATH) -> list[dict]:
    import fitz
    doc = fitz.open(pdf_path)
    secs = []
    for s in REGISTRY[slug]["sections"]:
        per_page = [page_lines(doc[pno - 1]) for pno in range(s["start"], s["end"])]
        folios = fill_folios([(pl[0]["page"] if pl else None) for pl in per_page])
        lines: list[dict] = []
        for pl, folio in zip(per_page, folios):
            for ln in pl:
                ln["page"] = folio
            lines.extend(pl)
        pairs = split_long_pairs(paras_with_pages(lines))
        secs.append({"heading": s["heading"], "title_zh": s["title_zh"],
                     "paras": [t for t, _ in pairs],
                     "pages": [pg for _, pg in pairs]})
    doc.close()
    return secs


# ── translation engine ───────────────────────────────────────────────────────
HOWES_PROMPT_TMPL = """你是日本近代基督教史的專業譯者，正在翻譯豪斯（John F. Howes）的學術評傳《Japan's Modern Prophet: Uchimura Kanzō, 1861–1930》。把下列英文原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
2. 只翻譯，不要加任何前言、說明、譯註或原文回抄。
3. 語域：學術評傳的敘事散文——準確、清晰、可讀；不要譯得像教科書條目，也不要加原文沒有的文采。作者的判斷語氣（推測、保留、反諷）要如實保留。
4. 保留 Markdown：以 `> ` 開頭的是引文區塊，譯完仍以 `> ` 開頭；`## ` 標題照留。
4b. **表格**：以 `|` 開頭的是 markdown 表格。**逐格翻譯，列數與欄數一格都不可增減**，
   `| --- | --- |` 那一行原樣照抄，每一列都要以 `|` 開頭與結尾。表頭若是空的（`|  |  |`）
   就保持空的。年月（January 1893）譯成「一八九三年一月」。
   🚨 **羅馬字轉寫的日文原文那一欄原樣保留，不要翻譯**（`Hitomaru ya`、
   `Uta wa uta nari hitokokoro`——那是和歌的原文，一翻就沒有原文可對照了）。
5. 人名地名一律還原漢字，不音譯：Uchimura Kanzô→內村鑑三（單稱 Kanzô→鑑三、Uchimura→內村）、Nitobe Inazô→新渡戶稻造、Miyabe Kingo→宮部金吾、Niijima Jô→新島襄、Uemura Masahisa→植村正久、Ebina Danjô→海老名彈正、Tokutomi Sohô→德富蘇峰、Yanaihara Tadao→矢內原忠雄、Nanbara Shigeru→南原繁、Tsukamoto Toraji→塚本虎二、Fujii Takeshi→藤井武、Kurosaki Kôkichi→黑崎幸吉、Kanamori Tsûrin→金森通倫、Ônishi Hajime→大西祝、Inoue Tetsujirô→井上哲次郎、Sapporo→札幌、Hakodate→函館、Yokosuka→橫須賀、Yokohama→橫濱、Takasaki→高崎、Kashiwagi→柏木、Kyôto→京都、Ôsaka→大阪、Edo→江戶。
6. 西方人名依教會史通用譯名：William S. Clark→克拉克、M.C. Harris→哈里斯、Julius H. Seelye→席利、Luther→路德、Calvin→加爾文、Carlyle→卡萊爾、Emerson→愛默生、Amherst (College)→安默斯特（學院）、Hartford→哈特福、New England→新英格蘭、Elwyn→艾爾文。
7. **專名層——一對一，不可改**：mukyôkai / Non-Church / No-Church→無教會（主義）、Sapporo Agricultural College→札幌農學校、Imperial Rescript on Education→教育敕語、the disrespect incident / lèse-majesté incident→不敬事件、First Higher School→第一高等中學校、Yorozu chôhô→《萬朝報》、Seisho no kenkyû / Biblical Study→《聖書之研究》、Second Coming movement→再臨運動、pacifism / non-war→非戰論、Sino-Japanese War→甲午戰爭、Russo-Japanese War→日俄戰爭、Meiji／Taishô／Shôwa→明治／大正／昭和、Diet→帝國議會、shogunate→幕府、Restoration→維新、han / clan→藩、samurai→武士、daimyô→大名、mission board→差會、missionary→宣教士（**不可用「傳教士」，也不可用日式的「宣教師」**）。
7b. **內村自己的著作——書名要譯回日文原書名，不可照英文再意譯一次**。英文書名本來就是從日文譯過去的。
   通則：**原題本來就有的漢字照原漢字，只有假名（平假名／片假名）的部分才另外翻**。
   例：『基督信徒のなぐさめ』的「基督信徒」是漢字，照留；「なぐさめ」是假名，譯作「慰藉」→《基督信徒的慰藉》。
   ‧ Consolations of a Christian / Kirisuto shinto no nagusame→**《基督信徒的慰藉》**（不作「基督徒的安慰」「基督教徒的慰藉」）
   ‧ Search after Peace / Kyûanroku→**《求安錄》**（**不可作「尋求和平」「求和平」**）
   ‧ The Earth and Man / Chijinron→**《地人論》**（不作「地球與人類」）
   ‧ “The Greatest Legacy for Succeeding Generations” / Kôsei e no saidai ibutsu→**《留給後世的最大遺產》**
   ‧ How I Became a Christian→**《我如何成為基督徒》**；The Book of Ruth / Rutsuki→**《路得記》**
   ‧ Japan and the Japanese→**《日本及日本人》**（1894 初版）；Representative Men of Japan→**《代表的日本人》**（1908 改題）——**這兩個是同一本書的兩個書名，不可互換也不可合併**
   ‧ Seisho no kenkyû / Biblical Study→**《聖書之研究》**；Yorozu chôhô→**《萬朝報》**
   ‧ 日本文學術語同理：I Novel / watakushi shôsetsu→**「私小說」**（**不可作「我小說」「自我小說」**）
8. **概念層——給你候選，按語境擇一，不要一詞一譯到底**。挑哪一個由「這一句在講什麼」決定，不是由哪個常見決定；同一段裡語意不同就可以用不同譯法：
   ‧ Christendom→基督教世界（指西方基督教文明、諸基督教國家的整體）／基督教國度（指一個統轄性的政教秩序，尤其與「神的國」對舉時）
   ‧ church→教會（信仰共同體或機構）／教堂（指建築物）／大公教會（大寫 the Church 指普世教會）
   ‧ conversion→**歸信**（一律用此，含「宗教歸信」「歸信的經過」）；convert (n.)→**歸信者**；
     convert (v.t.，使某人信教)→使…歸信、帶領…歸信。
     **不可用「回心」**——那是日文基督教譯 conversion 的詞（かいしん），中文基督教界不用，
     讀者會誤讀成「悔改」。「皈依」只留給明確的天主教語境（皈依天主教會、入修會）。
   ‧ providence→天意／神的護理（神學論述中）
   ‧ grace→恩典／恩寵（天主教語境）
   ‧ sect→宗派／教派；帶貶義時→小宗派、宗門
   ‧ denomination→教派／宗派
   ‧ lay / layman→平信徒／在俗（與聖職相對時）
   ‧ evangelist→佈道家（以此為業者）／傳福音的人（泛指）
   ‧ Bible study meeting→聖經研究會（內村柏木聚會這類固定團體）／查經聚會（泛指）
   ‧ heathen→異教徒／外邦人（聖經語體中）
   ‧ deshi→弟子／門人／門下（依語氣）；sensei→先生（保留日式稱謂）／老師
   ‧ the West→西方／西洋（明治語境）
   ‧ independence→獨立／自立（講經濟上不靠人時）
9. **日本事物的專有譯法——用錯就是史實錯誤，優先於其他規則**：
   ‧ 日本君主一律「**天皇**」，**絕不可作「皇帝」**（Emperor Meiji→明治天皇、the Emperor→天皇）。
     只有中國、羅馬、俄國、德意志等的君主才譯「皇帝」。
   ‧ Crown Prince→皇太子（不作「太子」）；imperial court→朝廷；imperial household→皇室；
     imperial portrait→御真影。
   ‧ 佛教的 temple→**寺院／寺**；神道的 shrine→**神社**。兩者都**不作「廟」「寺廟」「廟宇」**
     （那是漢人民間信仰的用語，用在日本會失真）。僧侶→僧；住持→住持。
   ‧ daimyo／feudal lord→**大名**（不作「封建領主」）；藩主家臣之長→**家老**（不作「宰相」）；
     內閣總理大臣→**首相**（不作「宰相」）。
   ‧ 日本的**中央部會**才用「省」（文部省／外務省／內務省／農商務省／商工省）；
     Ministry of Education→**文部省**，不可作「教育省」。日本的**地方行政區是「縣」不是「省」**；
     provincial town→地方城市（不作「省城」）。
   ‧ 其他照日本原詞：元老、華族、士族、藩士、廢藩置縣、帝國議會、貴族院、樞密院、
     大政奉還、王政復古、御雇外國人。
10. 聖經人名地名書卷名依和合本；引用聖經的句子譯為和合本語體。
11. 只輸出翻譯後的繁體中文。

英文原文：
{source}"""


def make_engine(backend: str = "auto"):
    """translate_para(en)->zh；引擎鏈與清理沿用 uchimura_build，只換 prompt。"""
    import translate_ebook_to_zh as te
    te.PROMPT_TMPL = HOWES_PROMPT_TMPL

    def translate_para(en: str) -> str:
        src = (en or "").strip()
        if not src:
            return ""
        quoted = src.startswith("> ")
        pieces = te.split_oversized(src)

        def translate_piece(piece: str) -> str:
            if backend == "haiku":
                return te.haiku_translate(piece)
            if backend == "gemini":
                return te.gemini_translate(piece)
            if backend == "nvidia":
                return te.nvidia_translate(piece)
            return te.gemini_with_nvidia_fallback(piece)

        out = ""
        for _ in range(4):  # retry-on-empty
            out = ub.clean_zh_output(" ".join(translate_piece(p) for p in pieces))
            if out:
                break
        # 引文標記偶爾會被引擎吃掉；欄位對齊靠段落數，標記靠這裡補回來
        if quoted and out and not out.startswith("> "):
            out = f"> {out.lstrip('> ')}"
        # 表格的換行一定會被壓掉（引擎回一行，clean_zh_output 又收空白），切回去
        if src.startswith("|") and out.startswith("|"):
            out = retable(out, len(src.split(chr(10))))
        return out

    return translate_para


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--sample", type=int, default=0)
    args = ap.parse_args()
    secs = load_work_sections("howes-prophet")
    total = sum(len(s["paras"]) for s in secs)
    chars = sum(len(p) for s in secs for p in s["paras"])
    print(f"howes-prophet  sections={len(secs)} paras={total} chars={chars:,}")
    if args.dry or args.sample:
        for i, s in enumerate(secs):
            q = sum(1 for p in s["paras"] if p.startswith("> "))
            print(f"  sec{i:2} 「{s['title_zh']}」 ¶={len(s['paras']):3} 引文={q}")
            for p in s["paras"][:args.sample]:
                print(f"      {p[:150]}")


if __name__ == "__main__":
    main()
