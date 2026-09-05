# -*- coding: utf-8 -*-
"""Build Uchimura Kanzō's TWO ENGLISH ORIGINALS into en＋繁中 reader books.

Second wave of the 內村鑑三 collected-works case (first wave = the 11 Aozora
Bunko Japanese texts, see uchimura_build.py). Uchimura wrote two of his three
best-known books *in English* for a foreign readership — 《代表的日本人
Representative Men of Japan》(Keiseisha 1908) and 《我如何成為基督徒 How I
Became a Christian: Out of My Diary》(Keiseisha 1922, the author's own retitled
edition of the 1895 Revell 《The Diary of a Japanese Convert》). So this line is
en＋繁中 (`sources={"en":…}`), not ja＋繁中.

Source = archive.org djvu OCR text (both scans open, no access restriction), so
unlike the Aozora line the text must be reflowed: running heads and page numbers
dropped, end-of-line hyphenation rejoined, paragraphs healed across page breaks.
Running heads here ("38 REPRESENTATIVE" / "MEN OF JAPAN. 39") are OCR'd a dozen
different ways (KEPKESENTATIVE, BEPEESENTATIVB, MEN OF PA JAN…), so they are
matched not by spelling but by the one thing they never have: a lowercase
letter. Reflow itself is reused from mueller_build (same archive.org djvu shape).

Pure helpers locked by scripts/tests/test_uchimura_en_build.py; the translate /
build / upload loop is uchimura_auto.py --author uchimura-en.

  python scripts/uchimura_en_build.py --dry
  python scripts/uchimura_auto.py --author uchimura-en --list
  python scripts/uchimura_auto.py --author uchimura-en --run-queue --backend haiku
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import mueller_build as mb  # noqa: E402  (loads .env, reconfigures stdout; reflow reused)

CACHE_DIR = Path("c:/tmp/uchimura_cache")
SOURCE_LANG = "en"
AUTHOR_ZH = "內村鑑三"
AUTHOR_EN = "Uchimura Kanzō"
CATEGORY = "神學"
DATA_DIRNAME = "uchimura_en_data"

# ── Registry ─────────────────────────────────────────────────────────────────
# d0000000-… namespace continues the Aozora line (…0001–0006 are the 11 Aozora
# texts). Section boundaries are 1-based line ranges [start, end) into the djvu
# txt; the ALL-CAPS chapter title lines inside the range are dropped as junk by
# HEAD_RE, so each section supplies its own 繁中 title and English heading.
REGISTRY: dict[str, dict] = {
    "representative-men": {
        "ebook_id": "d0000000-0000-4000-8000-000000000007",
        "title": "代表的日本人",
        "original_title": "Representative Men of Japan",
        "subtitle": "內村以英文向世界介紹的五位日本人（英文原著＋繁中對照）",
        "year": 1908,
        "parent_volume": "英文著作",
        "txt": "representativeme00uchirich.txt",
        "sections": [
            {"title_zh": "序言", "heading": "PREFATORY NOTE", "start": 82, "end": 109},
            {"title_zh": "西鄉隆盛——新日本的奠基者",
             "heading": "SAIGO TAKAMORI — A FOUNDER OF NEW JAPAN", "start": 109, "end": 1608},
            {"title_zh": "上杉鷹山——一位封建領主",
             "heading": "UESUGI YOZAN — A FEUDAL LORD", "start": 1608, "end": 2880},
            {"title_zh": "二宮尊德——農民聖者",
             "heading": "NINOMIYA SONTOKU — A PEASANT SAINT", "start": 2880, "end": 4231},
            {"title_zh": "中江藤樹——鄉村教師",
             "heading": "NAKAE TOJU — A VILLAGE TEACHER", "start": 4231, "end": 5411},
            {"title_zh": "日蓮上人——一位佛教僧侶",
             "heading": "SAINT NICHIREN — A BUDDHIST PRIEST", "start": 5411, "end": 7023},
        ],
    },
    "how-i-became": {
        "ebook_id": "d0000000-0000-4000-8000-000000000008",
        "title": "我如何成為基督徒",
        "original_title": "How I Became a Christian: Out of My Diary",
        "subtitle": "英文原著日記體自傳（英文原著＋繁中對照）",
        "year": 1922,
        "parent_volume": "信仰三部作",
        "txt": "howibecamechrist00uchi.txt",
        # 71..126 is the preface; 126..170 is the CONTENTS list + half-title
        # (a page-number table — deliberately skipped, the reader has its own TOC).
        "sections": [
            {"title_zh": "自序", "heading": "PREFACE", "start": 71, "end": 126},
            {"title_zh": "緒論", "heading": "INTRODUCTION", "start": 170, "end": 207},
            # ch.1's title line "heathenism." is OCR'd lowercase → skip past it
            {"title_zh": "第一章　異教", "heading": "CHAPTER FIRST — HEATHENISM",
             "start": 211, "end": 475},
            {"title_zh": "第二章　初識基督教",
             "heading": "CHAPTER SECOND — INTRODUCTION TO CHRISTIANITY",
             "start": 475, "end": 838},
            {"title_zh": "第三章　初生的教會",
             "heading": "CHAPTER THIRD — THE INCIPIENT CHURCH", "start": 838, "end": 2207},
            {"title_zh": "第四章　新教會與平信徒講道",
             "heading": "CHAPTER FOURTH — A NEW CHURCH AND LAY-PREACHING",
             "start": 2207, "end": 2981},
            {"title_zh": "第五章　走入世界——感傷的基督教",
             "heading": "CHAPTER FIFTH — OUT INTO THE WORLD. SENTIMENTAL CHRISTIANITY",
             "start": 2981, "end": 3547},
            {"title_zh": "第六章　對基督教國的初印象",
             "heading": "CHAPTER SIXTH — THE FIRST IMPRESSIONS OF CHRISTENDOM",
             "start": 3547, "end": 4106},
            {"title_zh": "第七章　在基督教國——在慈善家之間",
             "heading": "CHAPTER SEVENTH — IN CHRISTENDOM. AMONG PHILANTHROPISTS",
             "start": 4106, "end": 5031},
            {"title_zh": "第八章　在基督教國——新英格蘭的大學生活",
             "heading": "CHAPTER EIGHTH — IN CHRISTENDOM. NEW ENGLAND COLLEGE LIFE",
             "start": 5031, "end": 6011},
            {"title_zh": "第九章　在基督教國——涉足神學",
             "heading": "CHAPTER NINTH — IN CHRISTENDOM. A DIP INTO THEOLOGY",
             "start": 6011, "end": 6613},
            {"title_zh": "第十章　對基督教國的總印象——歸國",
             "heading": "CHAPTER TENTH — THE NET IMPRESSIONS OF CHRISTENDOM. RETURN HOME",
             "start": 6613, "end": 7615},
        ],
    },
}

QUEUE = ["representative-men", "how-i-became"]

# ── OCR cleanup ──────────────────────────────────────────────────────────────
# Running heads / page numbers / plate junk never contain a lowercase letter;
# body lines practically always do. Cheaper and far more robust than trying to
# spell out every way the OCR mangled "REPRESENTATIVE".
HEAD_RE = re.compile(r"^[^a-z]*$")

# In the 1922 Keiseisha scan the opening double quote is read as a lowercase u
# (uO just tell us how…”). Only fire before a capital, so 'unusual' and the
# initial 'U.' are left alone.
_OCR_OPEN_QUOTE_RE = re.compile(r"(?<![A-Za-z0-9])u(?=[A-Z])")

# Essay subsections ("I.— The Japanese Revolution of 1868.") survive reflow as
# ordinary paragraphs; promote them to markdown headings for the reader.
_SUBHEAD_RE = re.compile(r"^[IVXL]+\s*[.\-—–]+\s*\S")


# Garbles worth correcting at source because no amount of context lets the engine
# recover them (the author signed his own name and the OCR ate it).
OCR_FIXES = {"IvAN.25 UCHIMURA": "KANZO UCHIMURA"}


def fix_ocr_quotes(text: str) -> str:
    for bad, good in OCR_FIXES.items():
        text = text.replace(bad, good)
    return _OCR_OPEN_QUOTE_RE.sub("\u201c", text)


def reflow_ocr(lines: list[str]) -> list[str]:
    """archive.org djvu OCR lines → clean paragraphs (mueller_build.reflow with
    the lowercase-letter test as the running-head matcher)."""
    return mb.reflow(lines, HEAD_RE)


def mark_subheads(paras: list[str]) -> list[str]:
    return [f"## {p}" if (len(p) < 80 and _SUBHEAD_RE.match(p)) else p for p in paras]


def split_long_paras_en(paras: list[str], max_chars: int = 1800) -> list[str]:
    """Split over-long paragraphs on sentence boundaries so each prompt stays
    bounded and zh rows stay 1:1 with the English rows."""
    out: list[str] = []
    for p in paras:
        if len(p) <= max_chars:
            out.append(p)
            continue
        buf = ""
        for part in re.split(r"(?<=[.!?\"\u201d\u2019])\s+", p):
            if buf and len(buf) + 1 + len(part) > max_chars:
                out.append(buf)
                buf = part
            else:
                buf = f"{buf} {part}" if buf else part
        if buf:
            out.append(buf)
    return out


def load_work_sections(slug: str, cache_dir: Path = CACHE_DIR) -> list[dict]:
    """Registry slug → [{heading, title_zh, paras}] ready for translation."""
    w = REGISTRY[slug]
    lines = (cache_dir / w["txt"]).read_text(encoding="utf-8", errors="replace").split("\n")
    secs = []
    for s in w["sections"]:
        paras = reflow_ocr(lines[s["start"] - 1:s["end"] - 1])
        paras = split_long_paras_en(mark_subheads([fix_ocr_quotes(p) for p in paras]))
        secs.append({"heading": s["heading"], "title_zh": s["title_zh"], "paras": paras})
    return secs


# ── translation engine ───────────────────────────────────────────────────────
UCHIMURA_EN_PROMPT_TMPL = """你是明治—大正時代日本基督教文獻的專業譯者，正在翻譯內村鑑三（Uchimura Kanzō, 1861–1930）**以英文親筆寫成**的著作。把下列英文原文翻成**繁體中文**。

原文取自 1900 年代排印本的掃描 OCR，可能有錯字、章首花體大寫字被誤認（如 \\X7HEN＝WHEN、DELIGION＝RELIGION、fS＝IS）、引號被誤認成 u 或 tc。請依上下文判讀，照原意翻譯，不要把 OCR 雜訊照抄或加註。

規則：
1. 嚴守繁體中文（禁簡體）；中間點用「‧」。
2. 只翻譯，不要加任何前言、說明、註解或原文回抄。
3. 語域：典雅而可讀的現代繁體中文書面語；內村英文帶維多利亞時代文風與強烈個人告白語氣，譯文須保留其莊重、熱切與偶爾的自嘲。引文中的聖經句子譯為和合本語體。
4. 保留 Markdown（`## ` 標題等）。日記體的日期標題（如 March 9, 1879.）譯為「一八七九年三月九日」。
5. 聖經人名地名書卷名依和合本。神學術語鎖死：Christendom→基督教國、heathen(ism)→異教（徒）、conversion→回心、convert→歸信者、providence→天意、Almighty→全能者、God→神、Christ→基督、the Gospel→福音、Scriptures→聖經、missionary→宣教師、church→教會、sect→宗派、denomination→教派、creed→信條、theology→神學、theologue→神學生、Sabbath→安息日、prayer-meeting→祈禱會、lay-preaching→平信徒講道、Redeemer→救主、grace→恩典、sin→罪。
6. 日本人名地名還原漢字：Saigo Takamori→西鄉隆盛、Uesugi Yozan→上杉鷹山、Yonezawa→米澤、Ninomiya Sontoku→二宮尊德、Nakae Toju→中江藤樹、Omi→近江、Nichiren→日蓮、Kamakura→鎌倉、Minobu→身延、Ikegami→池上、Sapporo→札幌、Kashiwagi→柏木、Takasaki→高崎、Tokio/Tokyo→東京、Yedo/Edo→江戶、Nippon/Japan→日本、Shinto→神道、Buddhism→佛教、bonze→僧、daimio→大名、samurai→武士、shogun→將軍、Mikado→天皇、sutra→經、Pundarika (Sutra)→《法華經》、Nirvana→涅槃、Tathagata→如來、Jodo→淨土宗、Zen→禪宗、Shingon→真言宗、Ritzu→律宗、Amherst→安默斯特、New England→新英格蘭、Elwyn→艾爾文。
7. 幕末維新語境的詞不可直譯：**imperialists→勤王派（絕非「帝國主義者」）**、the imperial cause→勤王大義、the Shogunate/Tokugawa government→幕府、Restoration→維新、clan→藩、clansman→藩士、retainer→家臣、feudal lord→藩主、Satsuma→薩摩、Choshu→長州、Aizu→會津、Tokugawa→德川、Kioto→京都、Corea→朝鮮、Formosa→臺灣、Loochoo→琉球。
8. 只輸出翻譯後的繁體中文。

英文原文：
{source}"""


def make_engine(backend: str = "auto"):
    """translate_para(en)->zh, same chain/cleanup as the Aozora line but with the
    English prompt (see uchimura_build.make_engine)."""
    import translate_ebook_to_zh as te
    import uchimura_build as ub
    te.PROMPT_TMPL = UCHIMURA_EN_PROMPT_TMPL

    def translate_para(en: str) -> str:
        src = (en or "").strip()
        if not src:
            return ""
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
                return out
        return out

    return translate_para


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--work", type=str, default=None)
    ap.add_argument("--sample", type=int, default=0, help="print N paragraphs of each section")
    args = ap.parse_args()
    for slug in ([args.work] if args.work else QUEUE):
        secs = load_work_sections(slug)
        w = REGISTRY[slug]
        total = sum(len(s["paras"]) for s in secs)
        chars = sum(len(p) for s in secs for p in s["paras"])
        print(f"{slug:20} {w['title']:10} sections={len(secs):2} paras={total:4} chars={chars:,}")
        if args.dry or args.sample:
            for i, s in enumerate(secs):
                print(f"  sec{i} 「{s['title_zh']}」 ¶={len(s['paras'])}")
                for p in s["paras"][:args.sample]:
                    print(f"      {p[:150]}")


if __name__ == "__main__":
    main()
