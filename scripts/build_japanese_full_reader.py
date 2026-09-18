#!/usr/bin/env python3
"""Typeset the Japanese religious-studies reader as JIS B5 print masters.

The fourth reader in the series, and the first whose target language is modern.
Everything about the page is imported from the Hebrew builder and the Greek
interlinear renderer, because four books on one shelf have to look like one
series; what differs is only what the language forces:

* Japanese runs left to right and is set in MS Mincho — a conventional TTC that
  LibreOffice resolves without substituting, unlike the variable Noto builds.
* The vocabulary table keeps a pitch column, which Greek dropped: 重音 cannot be
  read off the kana, so it has to be printed. What is printed is u-biq's own
  break marking (は・や・い), not an accent number — the source carries the break
  positions, and the number would be an inference nobody could check.
* The content is in two halves — modern prose and 文語 with 舊字舊假名 — which the
  owner named 第一冊／第二冊, never 上下冊. Since 2026-09-18 each half fits in one
  bound volume (346 and 354 pages), so the two halves are the two books.

    python -X utf8 scripts/build_japanese_full_reader.py
    python -X utf8 scripts/build_japanese_full_reader.py --book 1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Mm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_greek_full_reader as G  # noqa: E402  - the interlinear renderer
import build_hebrew_full_reader as H  # noqa: E402  - the shared page

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
READINGS = CACHE / "readings.json"
INTERLINEAR = CACHE / "interlinear.json"
SENSE = CACHE / "unit-sense.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"
EXERCISES = CACHE / "exercise-set.json"
FORMULAS = ROOT / "data/originalReaders/vocabulary/japanese-formulas.json"
NAMES = ROOT / "data/originalReaders/vocabulary/japanese-proper-names.json"
CORPUS_TABLES = ROOT / "data/originalReaders/vocabulary/japanese-appendices.json"
OUT_DIR = ROOT / "output/original-readers"

FONT_JA = "MS Mincho"
FONT_JA_FILE = r"C:\Windows\Fonts\msmincho.ttc"
JA_PT = 13.5
EXERCISE_PT = 12
JA_TITLE_PT = 15
# 🚨 擁有者 2026-09-17：「字都不可以小於 12。」正文、生詞表、逐詞對譯的中文義、
# 整句中譯、練習——凡是要讀的字一律 ≥12pt。只有頁眉與頁碼維持小字，那是版口
# 標示不是閱讀內容。改這幾個數字會直接改變每頁容納的份量，讀文上限要跟著重算。
GLOSS_PT = 12

# 印刷冊次與內容分半本來是兩件事：2026-09-08 的版面下兩半各自 744 與 657 頁，
# 一本不得超過 500 頁，所以印成四本。2026-09-18 一課壓到八頁之後兩半只有 346 與
# 354 頁，兩件事重合了——內容的第一冊／第二冊就是實體的第一冊／第二冊。
# 冊名照擁有者 2026-08-27 定的「第一冊／第二冊」，不叫上下冊。
BOOK_LABELS = ("第一冊", "第二冊")

VOLUMES = {
    1: {
        "subtitle": "現代語・宗教學與宗教史",
        "motto": "宗教學の日本語",
        "blurb": "五十篇現代日文的宗教學與宗教史散文，逐詞繁中對譯。",
    },
    2: {
        "subtitle": "文語・舊字舊假名",
        "motto": "文語のよみかた",
        "blurb": "五十篇文語讀物：文語訳聖書、使徒信經、萬葉集與戰前無教會主義的文章。",
    },
}

# 🚨 切點的存在理由只有一個：一本裝訂實體不得超過 500 頁（2026-09-08）。
# 2026-09-18 一課壓到八頁、讀文按版面預算節錄之後，各半只有 320–480 頁，上限不再
# 逼人，所以擁有者裁示並冊——回到「內容的一半＝一本實體書」。課次編號不動。
PARTS = [
    {"book": 1, "source": 1, "first": 1, "last": 50, "appendix": True},
    {"book": 2, "source": 2, "first": 1, "last": 50, "appendix": True},
]

_metrics = None


def part_label(part: dict) -> str:
    return BOOK_LABELS[part["book"] - 1]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def ja_width_mm(text: str, size_pt: float) -> float:
    """量寬用真的字體檔；逐詞排版是照量出來的寬度切行的。"""
    global _metrics
    if _metrics is None:
        from PIL import ImageFont

        _metrics = ImageFont.truetype(FONT_JA_FILE, 1000)
    return _metrics.getlength(text) / 1000 * size_pt / 72 * 25.4


def ja_run(paragraph, text: str, size_pt: float) -> None:
    H.set_run_font(paragraph.add_run(text), FONT_JA, size_pt, color=H.INK)


def accent_marks(entry: dict) -> str:
    """u-biq 用斷詞位置標重音；把它還原成「は・や・い」。

    抓下來的 `accentBreaks` 前面幾段加起來剛好等於假名長度，後面還跟著一個與
    詞無關的數字（頁面上另一個欄位的長度）。取到湊滿為止，多的丟掉——湊不滿就
    什麼都不印，不要硬切：切錯的重音比沒有重音更糟。
    """
    kana = entry.get("kana") or ""
    breaks = entry.get("accentBreaks") or []
    parts, index = [], 0
    for size in breaks:
        if index + size > len(kana):
            break
        parts.append(kana[index : index + size])
        index += size
        if index == len(kana):
            return "・".join(parts) if len(parts) > 1 else ""
    return ""


def add_vocabulary(document: Document, rows: list[dict]) -> None:
    H.compact_heading(document.add_heading(f"生詞　{len(rows)} 個", level=2),
                      before=H.SECTION_HEADING_SPACE_BEFORE_PT,
                      after=H.SECTION_HEADING_SPACE_AFTER_PT, line_spacing=1.0)
    table = document.add_table(rows=1, cols=5)
    # 🚨 編號欄要放得下兩位數。字級提到 12pt 之後，「14」需要 8.4mm 再加 cell 邊距，
    # 原本的 8mm 放不下，Word 就把它拆成上下兩行——書上印出來是「1」換行「4」。
    # 🚨 欄寬不足會折行，折一次就多一列——二十個詞因此排不進一頁。假名欄放得下
    # 「エ・レベ・ーター」這種長片假名，中文欄縮一點補回來。
    widths = [12, 33, 38, 16, 42]
    H.set_table_geometry(table, widths)
    H.set_borders(table)
    header = table.rows[0]
    H.set_repeat_header(header)
    for cell, title in zip(header.cells, ["#", "詞", "假名・重音", "詞類", "繁體中文"]):
        H.shade(cell, H.ACCENT_DARK)
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.space_after = Pt(0)
        H.set_run_font(paragraph.add_run(title), H.FONT_UI, 7.5, bold=True, color="FFFFFF")
    for index, entry in enumerate(rows, start=1):
        cells = table.add_row().cells
        H.prevent_row_split(table.rows[-1])
        written = entry.get("kanji") or entry.get("kana") or ""
        values = [
            (str(index), H.FONT_UI, H.TABLE_SIZE_PT, H.MUTED),
            (written, FONT_JA, H.TABLE_SIZE_PT + 1.4, H.INK),
            (accent_marks(entry) or entry.get("kana") or "", FONT_JA, H.TABLE_SIZE_PT, H.MUTED),
            (entry.get("pos") or "", H.FONT_UI, H.TABLE_SIZE_PT - 0.6, H.MUTED),
            (entry.get("glossZh") or "", H.FONT_ZH, H.TABLE_SIZE_PT, H.INK),
        ]
        for cell, (text, font, size, color) in zip(cells, values):
            H.set_cell_margins(cell, top=H.VOCAB_CELL_PAD_DXA,
                               bottom=H.VOCAB_CELL_PAD_DXA,
                               start=H.VOCAB_CELL_SIDE_PAD_DXA,
                               end=H.VOCAB_CELL_SIDE_PAD_DXA)
            H.tighten_cell(cell)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            H.add_mixed_script_text(paragraph, text, font, size, color=color)


def add_interlinear_unit(document: Document, unit: dict, tokens: list[dict], *, lead: str = "") -> None:
    if not tokens:
        H.add_body(document, unit["text"], size=H.TRANSLATION_PT)
        return
    G.add_interlinear(
        document,
        tokens,
        lead=lead,
        sense=unit.get("senseZh", ""),
        greek_pt=JA_PT,
        available_mm=H.USABLE_WIDTH_MM,
        measure=ja_width_mm,
        render=ja_run,
    )


def exercise_blocks(vocabulary: list[dict]) -> dict[tuple[int, int], dict]:
    """本書的十題練習，照（冊次、課次）收好。

    綁定用的是詞彙序號，不是練習檔自己寫的課次編號：練習檔數的是 1–100 的通編，
    書上印的是每冊 1–50，兩套編號之間換算一次就是一個出錯的機會，而換錯了每一頁
    看起來都還是對的。兩邊真正共有的是那兩千個詞——每一題都記下它練到的詞的序號
    與詞條，就照那個綁，詞條對不上就報錯。希伯來、拉丁、希臘那三本同一條規則。
    """
    if not EXERCISES.exists():
        raise SystemExit(
            f"缺 {EXERCISES.name}；先跑 scripts/assemble_japanese_exercises.py --write"
        )
    payload = json.loads(EXERCISES.read_text(encoding="utf-8"))
    if payload.get("direction") != "original-to-chinese":
        raise SystemExit(f"{EXERCISES.name} 的 direction 不是 original-to-chinese")
    by_ordinal = {
        entry["ordinal"]: (entry["volume"], entry["readerLesson"], headword_of(entry))
        for entry in vocabulary
    }
    bound: dict[tuple[int, int], dict] = {}
    for block in payload["lessons"]:
        hosts: set[tuple[int, int]] = set()
        for item in block["items"]:
            for word in item.get("targetWords") or []:
                found = by_ordinal.get(word["ordinal"])
                if found is None:
                    raise SystemExit(f"練習題的第 {word['ordinal']} 詞不在詞表內")
                volume, lesson, headword = found
                hosts.add((volume, lesson))
                if word["headword"] != headword:
                    raise SystemExit(
                        f"練習題的第 {word['ordinal']} 詞寫作 {word['headword']}，"
                        f"詞表寫作 {headword}：兩邊對的不是同一個詞"
                    )
        if len(hosts) != 1:
            raise SystemExit(f"練習題第 {block['lesson']} 課橫跨課次 {sorted(hosts)}")
        host = hosts.pop()
        if host in bound:
            raise SystemExit(f"第 {host[0]} 冊第 {host[1]} 課被兩組練習題認領")
        bound[host] = block
    return bound


def headword_of(entry: dict) -> str:
    return (entry.get("kanji") or "").strip() or (entry.get("kana") or "").strip()


def add_exercises(document: Document, block: dict | None, lesson: dict) -> None:
    """十題翻譯練習，站在原本背誦句的位置。

    只印日文。題旁若有中譯，就等於把答案印在題目旁邊，所以引用題印出處、
    自撰題只印題號，兩種都不印譯文。見 references/exercise-sets.md。
    """
    if block is None:
        raise SystemExit(
            f"第 {lesson['volume']} 冊第 {lesson['lesson']} 課沒有練習題："
            "exercise-set 對不上本課詞表"
        )
    H.compact_heading(
        document.add_heading(f"本課翻譯練習（{len(block['items'])}題）", level=2),
        before=H.SECTION_HEADING_SPACE_BEFORE_PT,
        after=H.SECTION_HEADING_SPACE_AFTER_PT, line_spacing=1.0)
    intro = H.add_body(
        document,
        "把每一句譯成繁體中文。標有出處的句子引自原典。",
        size=H.CAPTION_PT, color=H.MUTED,
    )
    intro.paragraph_format.space_after = Pt(3)
    H.set_keep(intro, next_paragraph=True)
    for item in block["items"]:
        head = document.add_paragraph()
        head.paragraph_format.space_before = Pt(H.EXERCISE_ITEM_SPACE_BEFORE_PT)
        head.paragraph_format.space_after = Pt(H.EXERCISE_ITEM_SPACE_AFTER_PT)
        head.paragraph_format.line_spacing = Pt(H.EXERCISE_LABEL_LINE_PT)
        H.set_run_font(head.add_run(f"{item['no']:02d}"), H.FONT_UI, H.LABEL_PT,
                       bold=True, color=H.ACCENT)
        if item["kind"] == "quoted":
            H.add_mixed_script_text(head, "　" + item["ref"], H.FONT_ZH, H.CAPTION_PT,
                                    color=H.MUTED)
        H.set_keep(head, next_paragraph=True)
        line = document.add_paragraph()
        line.paragraph_format.left_indent = Mm(4)
        line.paragraph_format.space_after = Pt(H.EXERCISE_TEXT_SPACE_AFTER_PT)
        line.paragraph_format.line_spacing = H.EXERCISE_TEXT_LINE_SPACING
        ja_run(line, item["text"], EXERCISE_PT)
        H.set_keep(line, next_paragraph=True)
        answer = document.add_paragraph(" ")
        # 作答線留一行寫得下中文就夠；原本每題連留白佔 28.8mm，十題排掉一頁半。
        answer.paragraph_format.space_after = Pt(H.EXERCISE_ANSWER_SPACE_AFTER_PT)
        answer.paragraph_format.line_spacing = Pt(H.EXERCISE_ANSWER_LINE_PT)
        H.paragraph_rule(answer, color=H.RULE, size="3", space="1")


def add_reading(document: Document, lesson: dict, interlinear: dict) -> None:
    # 讀本自己起一頁：生詞與練習題是預備，讀本才是這一課。
    # 🚨 用段落的 page_break_before，不要用 document.add_page_break()。後者會插入
    # 一個「帶分頁符的空段落」，接著這個 label 與標題的 keep-with-next 又把整組
    # 推到下一頁——中間夾出一張全空白的紙。第一冊 257 頁裡有 29 頁是這樣來的，
    # 剛好每課一頁，而且稽核只看「課次與題數」不看空白頁，一路都沒報。
    H.add_label(document, "Reading", page_break_before=True)
    document.add_heading("讀本", level=1)
    heading = document.add_heading(lesson["title"], level=2)
    H.paragraph_rule(heading, color=H.GOLD, size="8")
    for unit in lesson["units"]:
        tokens = (interlinear.get(unit["id"]) or {}).get("tokens") or []
        add_interlinear_unit(document, unit, tokens, lead=unit.get("label") or "")


def add_lesson(document: Document, lesson: dict, interlinear: dict, spec: dict,
               exercises: dict, *, page_break_before: bool = True) -> None:
    H.add_label(document, f"Lesson {lesson['lesson']:02d}  ·  {spec['subtitle']}",
                page_break_before=page_break_before)
    number = H.mark_running_tag(document.add_paragraph())
    number.paragraph_format.space_after = Pt(0)
    number.paragraph_format.line_spacing = Pt(H.LESSON_NUMBER_LINE_PT)
    H.set_run_font(number.add_run(f"第 {lesson['lesson']:02d} 課"), H.FONT_UI, 11,
                   bold=True, color=H.ACCENT)
    heading = H.compact_heading(document.add_heading(lesson["title"], level=1),
                                before=H.LESSON_TITLE_SPACE_BEFORE_PT,
                                after=H.LESSON_TITLE_SPACE_AFTER_PT,
                                line_spacing=H.LESSON_TITLE_LINE_SPACING)
    H.paragraph_rule(heading, color=H.GOLD, size="14")
    source = document.add_paragraph()
    source.paragraph_format.space_after = Pt(2)
    H.add_mixed_script_text(
        source,
        f"{lesson['author']}　{lesson['extent']}　{lesson['orthography']}",
        H.FONT_ZH, H.CAPTION_PT, color=H.MUTED,
    )
    add_vocabulary(document, lesson["vocabulary"])
    add_exercises(document, exercises.get((lesson["volume"], lesson["lesson"])), lesson)
    add_reading(document, lesson, interlinear)


def add_cover(document: Document, spec: dict, part: dict, counts: dict) -> None:
    table = document.add_table(rows=1, cols=1)
    H.set_table_geometry(table, [H.USABLE_WIDTH_MM])
    H.set_borders(table, outside=False, inside=False)
    cell = table.cell(0, 0)
    H.set_cell_margins(cell, top=500, bottom=500, start=350, end=350)
    palette = H.cover_colors("ja")
    H.shade(cell, palette["banner"])

    eyebrow = cell.paragraphs[0]
    eyebrow.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.set_run_font(eyebrow.add_run("ORIGINAL-LANGUAGE READER"), H.FONT_UI, 8,
                   color=palette["rule"], bold=True)
    name = cell.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.add_mixed_script_text(name, "日文宗教學讀本", H.FONT_ZH, 25, bold=True, color="FFF8ED")
    motto = cell.add_paragraph()
    motto.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.set_run_font(motto.add_run(spec["motto"]), FONT_JA, 18, color="FFF8ED")

    document.add_paragraph().paragraph_format.space_after = Pt(26)
    line = document.add_paragraph()
    line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.add_mixed_script_text(
        line, f"{part_label(part)}　第 {part['first']:02d}–{part['last']:02d} 課",
        H.FONT_ZH, 12, bold=True, color=H.INK)
    blurb = H.add_body(document, spec["blurb"], size=10.5, color=H.ACCENT)
    blurb.alignment = WD_ALIGN_PARAGRAPH.CENTER

    document.add_paragraph().paragraph_format.space_after = Pt(26)
    spec_line = document.add_paragraph()
    spec_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.paragraph_rule(spec_line, color=palette["rule"], size="24")
    counts_line = H.add_body(
        document,
        f"{counts['lessons']} 課．{counts['words']} 詞．翻譯練習 {counts['exercises']} 題．"
        f"讀本 {counts['chars']:,} 字",
        size=H.CAPTION_PT, color=H.MUTED)
    counts_line.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_front_matter(document: Document, spec: dict, part: dict, lessons: list[dict]) -> None:
    counts = {
        "lessons": len(lessons),
        "words": sum(len(l["vocabulary"]) for l in lessons),
        "exercises": len(lessons) * 10,
        "chars": sum(l["chars"] for l in lessons),
    }
    add_cover(document, spec, part, counts)
    H.page_break(document)
    document.add_heading("體例與來源", level=1)
    for line in (
        "詞序依《大家的日本語》課次；專名不佔課內詞額，另立附錄專名表。",
        "重音欄印的是假名的斷點（は・や・い）。",
        "讀本一律取宗教學、宗教史或宗教典籍：詞照課本次序，文照領域選材。",
        "聖書用文語訳（明治元訳舊約、大正改訳新約）。",
        "逐詞對譯以本課詞表的譯法為準；一個詞在該處沒有確定的譯法時留白。",
    ):
        H.add_body(document, line, size=H.CAPTION_PT, color=H.INK)
    H.page_break(document)
    H.add_contents(
        document,
        [(f"{l['lesson']:02d}", l["title"], l["author"]) for l in lessons],
        title=f"{part_label(part)}目錄",
        accent=H.cover_colors("ja")["accent"],
    )


def add_formula_appendix(document: Document, formulas: dict) -> None:
    """聖經・佛經・神道的常用語句。

    合約點名要收，而它們不是靠抓的：同一句在不同宗派與譯本寫法不同，錯一個字就
    是另一個傳統。這張表是人工策展的，逐條記出處與傳統，所以照原表印。
    """
    H.add_label(document, "Appendix  ·  formulas")
    heading = document.add_heading("附錄一　聖經・佛經・神道常用語句", level=1)
    H.paragraph_rule(heading, color=H.GOLD, size="14")
    H.add_body(document, formulas["rights"], size=H.CAPTION_PT, color=H.MUTED)
    for group in formulas["groups"]:
        document.add_heading(f"{group['title']}　{len(group['entries'])} 條", level=2)
        H.add_body(document, group["tradition"], size=H.CAPTION_PT, color=H.MUTED)
        for entry in group["entries"]:
            line = document.add_paragraph()
            line.paragraph_format.space_after = Pt(1)
            H.add_mixed_script_text(line, entry["ja"], FONT_JA, H.TABLE_SIZE_PT + 1.6)
            reading = document.add_paragraph()
            reading.paragraph_format.space_after = Pt(0)
            H.add_mixed_script_text(reading, entry.get("kana", ""), FONT_JA,
                                    H.CAPTION_PT, color=H.MUTED)
            zh = document.add_paragraph()
            zh.paragraph_format.space_after = Pt(5)
            H.add_mixed_script_text(zh, entry.get("zh", "（中文待補）"), H.FONT_ZH,
                                    H.TABLE_SIZE_PT, color=H.INK)
            H.add_mixed_script_text(zh, f"　{entry.get('source', '')}", H.FONT_ZH,
                                    H.CAPTION_PT - 0.6, color=H.MUTED)


def add_name_appendix(document: Document, names: dict) -> None:
    H.add_label(document, "Appendix  ·  proper names", page_break_before=True)
    heading = document.add_heading("附錄二　專名表", level=1)
    H.paragraph_rule(heading, color=H.GOLD, size="14")
    H.add_body(document, names["note"], size=H.CAPTION_PT, color=H.MUTED)
    buckets: dict[str, list[dict]] = {}
    for item in names["items"]:
        buckets.setdefault(item.get("category") or "待歸類", []).append(item)
    for category, items in buckets.items():
        document.add_heading(f"{category}　{len(items)} 條", level=2)
        for item in items:
            row = document.add_paragraph()
            row.paragraph_format.space_after = Pt(1)
            H.add_mixed_script_text(row, item.get("kanji") or item["kana"], FONT_JA,
                                    H.TABLE_SIZE_PT + 1.2)
            if item.get("kanji"):
                H.add_mixed_script_text(row, f"（{item['kana']}）", FONT_JA,
                                        H.CAPTION_PT, color=H.MUTED)
            H.add_mixed_script_text(row, f"　{item.get('zh') or '（中文待補）'}",
                                    H.FONT_ZH, H.TABLE_SIZE_PT, color=H.INK)


CORPUS_TABLE_COLUMNS = {
    "kyujitai": (("form", "舊字"), ("modern", "新字"), ("count", "次"), ("lessons", "見於")),
    "kyukana": (("form", "舊假名"), ("modern", "現代"), ("example", "例"), ("count", "次")),
    "function_words": (("form", "機能語"), ("count", "次"), ("lessons", "見於")),
    "counters": (("form", "助数詞"), ("example", "例"), ("count", "次"), ("lessons", "見於")),
    "era_calendar": (("form", "詞"), ("kind", "類"), ("zh", "繁中"), ("count", "次")),
    # 兩傳統譯名只有詞庫裁定過的才有字。空著代表《翻譯定名》沒收這個詞，
    # 不代表兩邊講法一樣——這一欄留白是有意義的資訊。
    "christian": (("form", "詞"), ("zh", "繁中"), ("variants", "新教／天主教"), ("count", "次")),
}
CORPUS_TABLE_DEFAULT = (("form", "詞"), ("zh", "繁中"), ("count", "次"), ("lessons", "見於"))
# 欄寬要跟著欄位走：基督教那張第三欄是兩傳統譯名，不是次數，照預設寬度會被擠成三行。
CORPUS_TABLE_WIDTHS = {"christian": [26, 28, 66, 21]}
# 舊字舊假名與文語助動詞只對文語那兩冊有用；現代語那兩冊印了是浪費紙。
CLASSICAL_ONLY = {"kyujitai", "kyukana"}


def add_corpus_appendix(document: Document, payload: dict, *, classical: bool) -> None:
    """把讀本正文自己長出來的那幾張表印出來。

    每一列都帶「次」與「見於」：這不是一張通用術語表，是這一本書的索引，讀者查到
    一個詞可以翻回它出現的那一課。
    """
    for table in payload["tables"]:
        if table["id"] in CLASSICAL_ONLY and not classical:
            continue
        if not table["entries"]:
            continue
        H.add_label(document, "Appendix  ·  from the corpus", page_break_before=True)
        heading = document.add_heading(table["title"], level=1)
        H.paragraph_rule(heading, color=H.GOLD, size="14")
        H.add_body(document, table["note"], size=H.CAPTION_PT, color=H.MUTED)
        columns = CORPUS_TABLE_COLUMNS.get(table["id"], CORPUS_TABLE_DEFAULT)
        widths = CORPUS_TABLE_WIDTHS.get(
            table["id"], {3: [46, 25, 70], 4: [34, 34, 16, 57]}[len(columns)])
        grid = document.add_table(rows=1, cols=len(columns))
        H.set_table_geometry(grid, widths)
        H.set_borders(grid)
        header = grid.rows[0]
        H.set_repeat_header(header)
        for cell, (_, title) in zip(header.cells, columns):
            H.shade(cell, H.ACCENT_DARK)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            H.set_run_font(paragraph.add_run(title), H.FONT_UI, 7.5, bold=True, color="FFFFFF")
        for entry in table["entries"]:
            cells = grid.add_row().cells
            H.prevent_row_split(grid.rows[-1])
            for cell, (field, _) in zip(cells, columns):
                value = entry.get(field)
                text = "" if value is None else str(value)
                font = FONT_JA if field in ("form", "modern", "example") else H.FONT_ZH
                size = H.TABLE_SIZE_PT + (1.2 if field == "form" else 0)
                color = H.INK if field in ("form", "modern", "zh") else H.MUTED
                H.set_cell_margins(cell)
                H.tighten_cell(cell)
                paragraph = cell.paragraphs[0]
                paragraph.paragraph_format.space_after = Pt(0)
                H.add_mixed_script_text(paragraph, text, font, size, color=color)


def add_auxiliary_appendix(document: Document) -> None:
    """文語助動詞表：合約附錄二點名的那一批，第二冊每一頁都在用。"""
    import build_japanese_interlinear as I

    wanted = ["き", "けり", "つ", "ぬ", "たり", "り", "べし", "ず", "む", "らむ",
              "けむ", "なり", "ごとし", "しむ", "る", "らる", "まし", "めり", "たし"]
    H.add_label(document, "Appendix  ·  classical auxiliaries", page_break_before=True)
    heading = document.add_heading("附錄三　文語助動詞", level=1)
    H.paragraph_rule(heading, color=H.GOLD, size="14")
    H.add_body(document,
               "第二冊的讀物是文語，這一批助動詞在每一頁上。逐詞對譯欄印的就是這裡的說法，"
               "全書一致。", size=H.CAPTION_PT, color=H.MUTED)
    for form in wanted:
        gloss = I.CLOSED_CLASS.get(form, "")
        row = document.add_paragraph()
        row.paragraph_format.space_after = Pt(1)
        H.add_mixed_script_text(row, form, FONT_JA, H.TABLE_SIZE_PT + 1.6)
        H.add_mixed_script_text(row, f"　{gloss}", H.FONT_ZH, H.TABLE_SIZE_PT, color=H.INK)


def attach_sense(lessons: list[dict], sense: dict[str, str]) -> int:
    """整句中譯照文字的雜湊接上去，不照課次或序號。

    課次會動、切段會重切，序號一改就會把某一句的譯文配到另一句底下——那是這一
    系列踩過最貴的一種錯，而且印出來完全正常。
    """
    import hashlib

    attached = 0
    for lesson in lessons:
        for unit in lesson["units"] + lesson["memoryUnits"]:
            key = hashlib.sha256(unit["text"].encode("utf-8")).hexdigest()[:16]
            if key in sense:
                unit["senseZh"] = sense[key]
                attached += 1
    return attached


def lessons_for(part: dict, readings: dict, vocabulary: list[dict]) -> list[dict]:
    volume = next(v for v in readings["volumes"] if v["volume"] == part["source"])
    rows = []
    for lesson in volume["lessons"]:
        if not (part["first"] <= lesson["lesson"] <= part["last"]):
            continue
        words = [
            entry for entry in vocabulary
            if entry["volume"] == part["source"] and entry["readerLesson"] == lesson["lesson"]
        ]
        rows.append({**lesson, "volume": part["source"], "vocabulary": words})
    return rows


def build(book: int) -> Path:
    part = next((p for p in PARTS if p["book"] == book), None)
    if part is None:
        raise SystemExit(f"沒有第 {book} 冊")
    spec = VOLUMES[part["source"]]
    readings = load(READINGS)
    vocabulary = load(VOCAB)["entries"]
    interlinear = load(INTERLINEAR)["units"] if INTERLINEAR.exists() else {}
    sense = load(SENSE) if SENSE.exists() else {}
    lessons = lessons_for(part, readings, vocabulary)
    exercises = exercise_blocks(vocabulary)
    attached = attach_sense(lessons, sense)
    # 🚨 分母要扣掉不是句子的段。原文用「＊」「×」分場、用「一」「二」「１」
    # 「２」起章節，它們自成一段是原書的排法，但沒有東西可譯。算進分母，統計就
    # 永遠停在 826／832，每次看到都要重新判斷一次那六段是不是真的漏譯。
    # 🚨 分子分母要算同一批。只從分母扣記號段，分子還帶著有譯文的那幾段，
    # 第一冊就報成 817／813——分子大於分母。
    every = [u for l in lessons for u in l["units"] + l["memoryUnits"]]
    marks = [u for u in every if not any(ch.isalpha() for ch in u["text"])]
    body = [u for u in every if any(ch.isalpha() for ch in u["text"])]
    done = sum(1 for u in body if (u.get("senseZh") or "").strip())
    print(f"  整句中譯 {done:,}／{len(body):,} 段"
          + (f"（另有 {len(marks)} 段是分場記號或章節序號，不譯）" if marks else ""),
          flush=True)

    document = Document()
    H.configure(document)
    running = f"日文宗教學讀本　{part_label(part)}"
    H.write_running_head(document.sections[0], running)
    document.core_properties.title = f"日文宗教學讀本：{part_label(part)}"
    document.core_properties.subject = spec["subtitle"]
    document.core_properties.language = "ja"

    add_front_matter(document, spec, part, lessons)
    H.start_section(document, running, lesson_tag=True)
    for index, lesson in enumerate(lessons):
        add_lesson(document, lesson, interlinear, spec, exercises,
                   page_break_before=index > 0)

    if part["appendix"]:
        H.start_section(document, f"{running}　附錄")
        add_formula_appendix(document, load(FORMULAS))
        add_name_appendix(document, load(NAMES))
        if part["source"] == 2:
            add_auxiliary_appendix(document)
        if CORPUS_TABLES.exists():
            add_corpus_appendix(document, load(CORPUS_TABLES), classical=part["source"] == 2)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"japanese-original-reader-vol{book}.docx"
    document.save(path)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="排版日文宗教學讀本 B5 DOCX")
    parser.add_argument("--book", type=int, choices=tuple(p["book"] for p in PARTS))
    args = parser.parse_args()
    for book in ([args.book] if args.book else [p["book"] for p in PARTS]):
        path = build(book)
        print(f"{BOOK_LABELS[book - 1]} -> {path.relative_to(ROOT)}  "
              f"{path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
