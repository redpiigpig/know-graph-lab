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


def lines_to_paras(lines: list[dict]) -> list[str]:
    """版面行 → 段落。縮排或引文起訖＝斷段；行尾連字號接回；引文加 `> `。"""
    paras: list[list[str]] = []
    kinds: list[bool] = []
    prev_quote: bool | None = None
    for ln in lines:
        if not keep_line(ln):
            continue
        text = ln["text"].strip()
        quote = _is_quote(ln)
        indented = INDENT_LO <= ln["x0"] <= INDENT_HI
        starts = (not paras) or quote != prev_quote or (not quote and indented)
        if starts:
            paras.append([text])
            kinds.append(quote)
        else:
            buf = paras[-1]
            if buf[-1].endswith("-"):
                buf[-1] = buf[-1][:-1] + text
            else:
                buf.append(text)
        prev_quote = quote

    out = []
    for parts, quote in zip(paras, kinds):
        s = re.sub(r"\s{2,}", " ", " ".join(parts)).strip()
        if s:
            out.append(f"> {s}" if quote else s)
    return out


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
    return sorted(lines, key=lambda l: (round(l["y"] / 3), l["x0"]))


def split_long(paras: list[str], max_chars: int = 1800) -> list[str]:
    """連續的引文段落之間沒有縮排可分（引文行 x0 全是 46），所以會黏成一大段——
    最長的一段有近九千字。按句界切開，`> ` 標記每一片都要帶著。"""
    import uchimura_en_build as ueb
    out: list[str] = []
    for p in paras:
        quoted = p.startswith("> ")
        body = p[2:] if quoted else p
        for piece in ueb.split_long_paras_en([body], max_chars=max_chars):
            out.append(f"> {piece}" if quoted else piece)
    return out


def load_work_sections(slug: str, pdf_path: Path = PDF_PATH) -> list[dict]:
    import fitz
    doc = fitz.open(pdf_path)
    secs = []
    for s in REGISTRY[slug]["sections"]:
        lines: list[dict] = []
        for pno in range(s["start"], s["end"]):
            lines.extend(page_lines(doc[pno - 1]))
        secs.append({"heading": s["heading"], "title_zh": s["title_zh"],
                     "paras": split_long(lines_to_paras(lines))})
    doc.close()
    return secs


# ── translation engine ───────────────────────────────────────────────────────
HOWES_PROMPT_TMPL = """你是日本近代基督教史的專業譯者，正在翻譯豪斯（John F. Howes）的學術評傳《Japan's Modern Prophet: Uchimura Kanzō, 1861–1930》。把下列英文原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
2. 只翻譯，不要加任何前言、說明、譯註或原文回抄。
3. 語域：學術評傳的敘事散文——準確、清晰、可讀；不要譯得像教科書條目，也不要加原文沒有的文采。作者的判斷語氣（推測、保留、反諷）要如實保留。
4. 保留 Markdown：以 `> ` 開頭的是引文區塊，譯完仍以 `> ` 開頭；`## ` 標題照留。
5. 人名地名一律還原漢字，不音譯：Uchimura Kanzô→內村鑑三（單稱 Kanzô→鑑三、Uchimura→內村）、Nitobe Inazô→新渡戶稻造、Miyabe Kingo→宮部金吾、Niijima Jô→新島襄、Uemura Masahisa→植村正久、Ebina Danjô→海老名彈正、Tokutomi Sohô→德富蘇峰、Yanaihara Tadao→矢內原忠雄、Nanbara Shigeru→南原繁、Tsukamoto Toraji→塚本虎二、Fujii Takeshi→藤井武、Kurosaki Kôkichi→黑崎幸吉、Kanamori Tsûrin→金森通倫、Ônishi Hajime→大西祝、Inoue Tetsujirô→井上哲次郎、Sapporo→札幌、Hakodate→函館、Yokosuka→橫須賀、Yokohama→橫濱、Takasaki→高崎、Kashiwagi→柏木、Kyôto→京都、Ôsaka→大阪、Edo→江戶。
6. 西方人名依教會史通用譯名：William S. Clark→克拉克、M.C. Harris→哈里斯、Julius H. Seelye→席利、Luther→路德、Calvin→加爾文、Carlyle→卡萊爾、Emerson→愛默生、Amherst (College)→安默斯特（學院）、Hartford→哈特福、New England→新英格蘭、Elwyn→艾爾文。
7. **專名層——一對一，不可改**：mukyôkai / Non-Church / No-Church→無教會（主義）、Sapporo Agricultural College→札幌農學校、Imperial Rescript on Education→教育敕語、the disrespect incident / lèse-majesté incident→不敬事件、First Higher School→第一高等中學校、Yorozu chôhô→《萬朝報》、Seisho no kenkyû / Biblical Study→《聖書之研究》、Second Coming movement→再臨運動、pacifism / non-war→非戰論、Sino-Japanese War→甲午戰爭、Russo-Japanese War→日俄戰爭、Meiji／Taishô／Shôwa→明治／大正／昭和、Diet→帝國議會、shogunate→幕府、Restoration→維新、han / clan→藩、samurai→武士、daimyô→大名、mission board→差會、missionary→宣教士（**不可用「傳教士」，也不可用日式的「宣教師」**）。
8. **概念層——給你候選，按語境擇一，不要一詞一譯到底**。挑哪一個由「這一句在講什麼」決定，不是由哪個常見決定；同一段裡語意不同就可以用不同譯法：
   ‧ Christendom→基督教世界（指西方基督教文明、諸基督教國家的整體）／基督教國度（指一個統轄性的政教秩序，尤其與「神的國」對舉時）
   ‧ church→教會（信仰共同體或機構）／教堂（指建築物）／大公教會（大寫 the Church 指普世教會）
   ‧ conversion→回心（內心轉變的過程，內村自己的用語）／歸信（改信基督教這件事）；convert (n.)→歸信者／信主的人
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
