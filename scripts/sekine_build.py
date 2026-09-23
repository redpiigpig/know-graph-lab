# -*- coding: utf-8 -*-
"""關根正雄（1912–2000）—— J-STAGE 論文 PDF → ja／de／fr＋繁中的 registry 模組。

供 `uchimura_auto.py --author sekine` 使用（翻譯、checkpoint、上架都在那支）。

來源：J-STAGE 上開放下載的 47 篇（2026-09-23 下載到 Drive
`全集\\神學\\關根正雄\\論文（J-STAGE）`、`研究文獻（J-STAGE）`），篇目中繼資料在
`.claude/skills/ebook-collected-works/sekine_data/jstage_articles.json`。
個人研究用，不受版權限制（使用者 2026-09-23 指示）。

分成三卷：
  sekine-papers-ja   他本人的日文論文、書評、序跋（20 篇）
  sekine-papers-west 西文論文（法文 1、德文 4）
  sekine-studies     別人評他的書評與論評（22 篇）——作者欄不是關根

取文字兩條路：
  * 有文字層的（43 篇，多為直排、上下兩段排）→ `jstage_pdf_text.extract`，
    照字元座標重排，頁碼＝該文起始頁＋PDF 頁序。
  * 沒有文字層的（AJBI 德文四篇）→ 先用 `mineru_ocr.py --lang latin` OCR 成逐頁 JSONL，
    放在 `sekine_data/ocr/`，這裡只讀。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_DATA = SCRIPT_DIR.parent / ".claude" / "skills" / "ebook-collected-works"
META = _SKILL_DATA / "sekine_data" / "jstage_articles.json"
OCR_DIR = _SKILL_DATA / "sekine_data" / "ocr"
DRIVE = Path(r"G:\我的雲端硬碟\資料\知識圖工作室\全集\神學\關根正雄")

SOURCE_LANG = "ja"
AUTHOR_ZH = "關根正雄"
AUTHOR_EN = "Sekine Masao"
CATEGORY = "神學"
DATA_DIRNAME = "sekine_data"

REGISTRY: dict[str, dict] = {
    "sekine-papers-ja": {
        "ebook_id": "5ec10000-0000-4000-8000-000000000001",
        "title": "關根正雄日文論文集（J-STAGE 所收）",
        "original_title": "関根正雄論文集",
        "subtitle": "《日本の神学》《言語研究》《日本學士院紀要》《オリエント》所收 1956–1992（日文原文＋繁中對照）",
        "year": 1956,
        "parent_volume": "論文集",
    },
    "sekine-papers-west": {
        "ebook_id": "5ec10000-0000-4000-8000-000000000002",
        "title": "關根正雄西文論文集（J-STAGE 所收）",
        "original_title": "Aufsätze",
        "subtitle": "Orient／Annual of the Japanese Biblical Institute 所收 1960–1988（德法文原文＋繁中對照）",
        "year": 1960,
        "parent_volume": "論文集",
    },
    "sekine-studies": {
        "ebook_id": "5ec10000-0000-4000-8000-000000000003",
        "title": "關根正雄研究文獻：書評與論評（J-STAGE 所收）",
        "original_title": "関根正雄著作書評集",
        "subtitle": "《日本の神学》《新約学研究》所收 1965–1997（日文原文＋繁中對照）",
        "year": 1965,
        "parent_volume": "研究文獻",
        "author": "中沢洽樹、並木浩一、左近淑 等",
        "author_en": "various",
    },
}
QUEUE = ["sekine-papers-ja", "sekine-studies", "sekine-papers-west"]

_WEST = re.compile(r"LITERATURSOZIOLOGISCHE|ELIAS VERZWEIFLUNG|Der \"Bruch\"|Wort, Name und Geist|Théodicée")


def _is_west(r: dict) -> bool:
    return bool(_WEST.search(r["title"]))


def ja_title(title: str) -> str:
    """J-STAGE 題名常是「英文題名   日文題名」並排，取日文那半。"""
    parts = [p.strip() for p in re.split(r"\s{3,}", title) if p.strip()]
    for p in reversed(parts):
        if re.search(r"[\u3040-\u30ff\u4e00-\u9fff]", p):
            return p
    return parts[-1] if parts else title


def author_name(author: str) -> str:
    """J-STAGE 作者欄是「K. Namiki       並木 浩一」這種中英並排；多位作者再並排下去。
    取所有漢字姓名（1991 年那篇論評是加藤善治、井上大衞、佐藤研三人合寫）。"""
    names = [p.strip().replace(" ", "") for p in re.split(r"\s{3,}", author)
             if re.search(r"[一-鿿]", p)]
    return "、".join(names) if names else author.strip()


def real_year(r: dict) -> int:
    y = int(r["year"])
    if y > 2020 and "ajbi" in r.get("cd", ""):      # J-STAGE 把數位化年當出版年
        return {"1": 1975, "3": 1977}.get(r["vol"], y)
    return y


def articles(slug: str) -> list[dict]:
    d = json.loads(META.read_text(encoding="utf-8"))
    if slug == "sekine-studies":
        rows = d["about"]
    else:
        rows = [r for r in d["by"] if _is_west(r) == (slug == "sekine-papers-west")]
    return sorted(rows, key=lambda r: (real_year(r), r["title"]))


def pdf_path(slug: str, r: dict) -> Path:
    """Drive 上的檔名是下載時組的：`{年}_{評者}_{題名前 60 字}.pdf`（本人論文沒有評者）。

    🚨 只比對題名前綴會撞：1996 年那五篇書評的英文題名都是
    「Sekine, New Translation of the Old Testament …」，前 12 字一模一樣，
    結果五節讀到同一個檔。評者名放進比對鍵才分得開。"""
    sub = "研究文獻（J-STAGE）" if slug == "sekine-studies" else "論文（J-STAGE）"
    y = str(real_year(r))
    title = re.sub(r"\s+", " ", re.sub(r'[\\/:*?"<>|]', "_", r["title"]))[:60].strip()
    who = "" if slug != "sekine-studies" else re.split(r"\s{2,}", r["author"])[-1].replace(" ", "") + "_"
    f = DRIVE / sub / f"{y}_{who}{title}.pdf"
    if not f.exists():
        raise FileNotFoundError(str(f))
    return f


def _key(t: str, n: int = 20) -> str:
    import unicodedata
    t = unicodedata.normalize("NFKC", ja_title(t))
    t = re.sub(r"^(書評|論評|Review)[:：\s(（―-]*", "", t)
    return re.sub(r"[^\w]|_", "", t)[:n]


def _find(paras: list[str], key: str, idx: list[int]) -> int | None:
    import unicodedata
    for n in (len(key), 12, 8):
        k = key[:n]
        if len(k) < 6:
            continue
        hits = [i for i in idx if k in re.sub(r"[^\w]|_", "", unicodedata.normalize("NFKC", paras[i]))]
        if len(hits) == 1 or (hits and n == len(key)):
            return hits[0]
    return None


ANCHORS = _SKILL_DATA / "sekine_data" / "trim_anchors.json"


def _norm_head(t: str) -> str:
    import unicodedata
    return re.sub(r"\s", "", unicodedata.normalize("NFKC", t))


def trim_neighbors(r: dict, paras: list[tuple[str, int]]) -> tuple[list[tuple[str, int]], list[str]]:
    """切掉 PDF 首頁上半的前一篇、末頁下半的下一篇（見 sekine_jstage_neighbors.py）。

    切點是**人工看過之後寫進 trim_anchors.json 的段首文字**，不是自動比對標題：
    頁面上印的標題和 J-STAGE 登錄的題名常對不上（1996 年那組書評在頁面上只印
    「Ⅱ歴史書」），自動比對實測會切錯地方（中沢那篇把自己的第一段切掉了）。
    有同頁鄰篇卻還沒人看過的，回報 ⚠，不切。"""
    notes: list[str] = []
    a = json.loads(ANCHORS.read_text(encoding="utf-8")).get(r["doi"])
    if a is None:
        if r.get("prev_title") or r.get("next_title"):
            notes.append("⚠ 有同頁鄰篇但 trim_anchors.json 還沒這一篇，沒切")
        return paras, notes
    heads = [_norm_head(t) for t, _ in paras]
    if a.get("end_before"):
        k = next((i for i, h in enumerate(heads) if h.startswith(_norm_head(a["end_before"]))), None)
        if k is None:
            notes.append(f"⚠ 找不到 end_before 錨點：{a['end_before']}")
        else:
            notes.append(f"末尾切掉 {len(paras) - k} 段")
            paras, heads = paras[:k], heads[:k]
    if a.get("start_at"):
        k = next((i for i, h in enumerate(heads) if h.startswith(_norm_head(a["start_at"]))), None)
        if k is None:
            notes.append(f"⚠ 找不到 start_at 錨點：{a['start_at']}")
        else:
            notes.append(f"開頭切掉 {k} 段")
            paras = paras[k:]
    return paras, notes


# 文字層不能用、改走 MinerU OCR 的篇目（DOI → sekine_data/ocr/ 下的檔名）。
# AJBI 四篇根本沒有文字層；法文那篇有，但順序整個是亂的（字散在頁面各處）。
OCR_FILES = {
    "10.57389/ajbi.1.0_39": "ajbi_1.jsonl",
    "10.57389/ajbi.3.0_52": "ajbi_3.jsonl",
    "10.57389/ajbi.11.0_3": "ajbi_11.jsonl",
    "10.57389/ajbi.14.0_3": "ajbi_14.jsonl",
    "10.5356/orient1960.1.23": "orient_1.jsonl",
}


def _ocr_paras(r: dict) -> list[tuple[str, int]]:
    f = OCR_DIR / OCR_FILES[r["doi"]]
    if not f.exists():
        raise FileNotFoundError(f"{f} —— 先跑 mineru_ocr.py --lang latin")
    start = int(r["sp"])
    out: list[tuple[str, int]] = []
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines()):
        ch = json.loads(line)
        # MinerU 從書眉讀出的印刷頁碼優先；讀不到才用「起始頁＋頁序」推。
        pp = ch.get("printed_page")
        page = int(pp) if isinstance(pp, int) or (isinstance(pp, str) and pp.isdigit()) else start + i
        for para in re.split(r"\n\s*\n", ch.get("content") or ""):
            para = re.sub(r"-\n(?=[a-zäöü])", "", para)
            para = re.sub(r"\s*\n\s*", " ", para).strip()
            if para and not re.fullmatch(r"[\d\s—\-]+", para):
                out.append((para, page))
    return out


TRIM_LOG: list | None = None     # 設成 [] 就會收集切邊紀錄（稽核用）


def load_work_sections(slug: str) -> list[dict]:
    """一篇論文＝一節。heading 用日文題名（書評另冠評者），pages 與 paras 等長。"""
    import jstage_pdf_text as J
    secs = []
    for r in articles(slug):
        if r["doi"] in OCR_FILES:
            paras = _ocr_paras(r)
            lang = "fr" if r["title"].startswith("Théodicée") else "de"
        else:
            paras = J.extract(str(pdf_path(slug, r)), int(r["sp"]))
            paras, notes = trim_neighbors(r, paras)
            if notes and TRIM_LOG is not None:
                TRIM_LOG.append((r["title"][:30], notes))
            lang = "fr" if r["title"].startswith("Théodicée") else "ja"
        head = ja_title(r["title"]) if lang == "ja" else r["title"]
        if slug == "sekine-studies":
            head = f"{author_name(r['author'])}〈{head}〉"
        secs.append({"heading": head, "paras": [t for t, _ in paras],
                     "pages": [p for _, p in paras], "lang": lang,
                     "year": real_year(r), "venue": r["journal"], "doi": r["doi"]})
    return secs


SEKINE_PROMPT_JA = """你是日本聖經學與無教會史的專業譯者，正在翻譯舊約學者關根正雄（1912–2000）
相關的學術文章（論文、書評、學會報告）。把下列日文原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。只翻譯，不要加前言、說明、譯註或回抄原文。
2. 語域：現代學術白話文。不要用句末的「也／矣／乎／哉」，不要拿「之」當「的」。
3. **書名照原漢字、只翻假名部分**：『旧約聖書文学史』→《舊約聖書文學史》、
   『イスラエルの思想と言語』→《以色列的思想與語言》、『聖書の信仰と思想』→《聖經的信仰與思想》（已有郭維租、鄭廷憲中譯本，用中譯本書名）。
   期刊名照原名：《日本の神学》《新約学研究》《聖書学論集》。
4. 正文用語照中文聖經學慣例：旧約→舊約、聖書学→聖經學、予言者／預言者→先知、
   ヤハウィスト→耶典作者（J）、エロヒスト→伊典作者（E）、申命記史家→申命記史家、
   第二イザヤ→第二以賽亞、知恵文学→智慧文學、神義論→神義論、救済史→救恩史、
   様式史→形式批判、伝承史→傳統史、編集史→編修史、七十人訳→七十士譯本。
5. 人名：西方學者用通行中譯並在首次出現時附原名（馮拉德 G. von Rad、諾特 M. Noth、
   艾希羅特 W. Eichrodt、韋伯 M. Weber）；日本學者照漢字原名（並木浩一、左近淑、木田献一）。
6. 引用的聖經章節照中文和合本卷名（イザヤ書→以賽亞書、エレミヤ書→耶利米書、ヨブ記→約伯記、
   コーヘレト→傳道書）。
7. **西文詞句（德、拉丁、希伯來轉寫、希臘文）原樣保留**，必要時在後面括號加中譯。
8. 純書目式的註（作者‧書名‧卷期‧頁）照原樣保留，不要改寫。
9. 西元年份用阿拉伯數字（一九七八年→1978 年）；年號、頁數、章節數字照原文。

日文原文：
{source}"""

SEKINE_PROMPT_WEST = """你是聖經學的專業譯者，正在翻譯日本舊約學者關根正雄（1912–2000）
以德文或法文發表的學術論文。把下列原文翻成**繁體中文**。

規則：
1. 嚴守繁體中文（禁簡體）；只翻譯，不要加前言、說明、譯註或回抄原文。
2. 語域：現代學術白話文。
3. 希伯來文、希臘文、拉丁文詞語與轉寫原樣保留，必要時在後面括號加中譯。
4. 聖經書卷用和合本卷名（Jesaja→以賽亞書、Hiob→約伯記、Könige→列王紀）。
5. 學者名用通行中譯並附原名（馮拉德 G. von Rad、諾特 M. Noth、韋爾豪森 J. Wellhausen）。
6. 術語：Heilsgeschichte→救恩史、Theodizee→神義論、Formgeschichte→形式批判、
   Überlieferungsgeschichte→傳統史、Deuteronomist→申命記史家、Jahwist→耶典作者。
7. 純書目式的註照原樣保留。

原文：
{source}"""


def _is_japanese(s: str) -> bool:
    return bool(re.search(r"[\u3040-\u30ff]", s)) or len(re.findall(r"[\u4e00-\u9fff]", s)) > len(s) * 0.3


_JUNK = re.compile(r"[Ͱ-Ͽ←-⋿①-⓿㈀-㋿§¶]")
_KANA = re.compile(r"[぀-ヿ]")


def is_ocr_junk(src: str) -> bool:
    """J-STAGE 的日文 OCR 把註釋裡的西文書目認成亂碼（「ρ↓冨一ωω①p>茜自§28」）。
    特徵是希臘字母、箭頭與數學符號、圈號字大量夾雜，而假名很少。這種段落送去翻
    只會得到編出來的東西，所以不翻、原樣留著。

    門檻：怪字元 ≥15% 且假名 <15%。真的希臘文引文（λόγος）夾在日文句子裡時假名多，
    不會被誤判。"""
    n = max(len(src), 1)
    return len(_JUNK.findall(src)) / n >= 0.15 and len(_KANA.findall(src)) / n < 0.15


def needs_translation(src: str) -> bool:
    """只剩數字、符號或極短碎片的段落，以及 OCR 亂碼段，不送引擎。"""
    return len(re.sub(r"[\s\d\W_]", "", src)) >= 2 and not is_ocr_junk(src)


def make_engine(backend: str = "auto"):
    import translate_ebook_to_zh as te
    import uchimura_build as ub

    def translate_para(src: str) -> str:
        src = (src or "").strip()
        if not src:
            return ""
        te.PROMPT_TMPL = SEKINE_PROMPT_JA if _is_japanese(src) else SEKINE_PROMPT_WEST
        pieces = te.split_oversized(src)

        def piece(p: str) -> str:
            if backend == "haiku":
                return te.haiku_translate(p)
            if backend == "gemini":
                return te.gemini_translate(p)
            if backend == "nvidia":
                return te.nvidia_translate(p)
            return te.gemini_with_nvidia_fallback(p)

        global ENGINE_ERRORS
        out = ""
        for _ in range(3):
            try:
                out = ub.clean_zh_output(" ".join(piece(p) for p in pieces))
            except Exception as e:  # noqa: BLE001
                # 引擎整條斷掉（NVIDIA 連線錯誤、全部 key 503）時不可以讓例外往上冒：
                # 驅動會把整卷放棄。留空白，下一輪（fleet keeper 每 30 分重拉）再補。
                # 品質閘擋下（output gate：未翻譯、推理外洩…）是這一段本身的問題，
                # 重跑也一樣；只有連線／服務類錯誤才算引擎壞了、要讓 lane 繼續活著。
                if "output gate" not in str(e):
                    ENGINE_ERRORS += 1
                print(f"    ⚠ engine error: {str(e)[:120]}", flush=True)
                return ""
            if out:
                break
        return out

    return translate_para


# 本輪引擎出錯次數。uchimura_auto 用它判斷「沒有進展」是因為引擎壞了
# （要再跑）還是剩下的段落真的翻不出來（可以收工）。
ENGINE_ERRORS = 0
STRICT_COMPLETE = True
