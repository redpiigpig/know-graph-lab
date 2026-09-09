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
  owner named 第一冊／第二冊, never 上下冊. Neither half fits in one bound volume,
  so they print as four: 第一–二冊 modern, 第三–四冊 文語.

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
from docx.shared import Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_greek_full_reader as G  # noqa: E402  - the interlinear renderer
import build_hebrew_full_reader as H  # noqa: E402  - the shared page

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache/original-readers/japanese-full"
READINGS = CACHE / "readings.json"
INTERLINEAR = CACHE / "interlinear.json"
SENSE = CACHE / "unit-sense.json"
VOCAB = ROOT / "data/originalReaders/vocabulary/japanese-2000.json"
FORMULAS = ROOT / "data/originalReaders/vocabulary/japanese-formulas.json"
NAMES = ROOT / "data/originalReaders/vocabulary/japanese-proper-names.json"
CORPUS_TABLES = ROOT / "data/originalReaders/vocabulary/japanese-appendices.json"
OUT_DIR = ROOT / "output/original-readers"

FONT_JA = "MS Mincho"
FONT_JA_FILE = r"C:\Windows\Fonts\msmincho.ttc"
JA_PT = 13.5
JA_TITLE_PT = 15
GLOSS_PT = 9.4

# 印刷冊次與內容分半是兩件事。合約把內容分成「第一冊＝現代語／第二冊＝文語」，
# 但一本不得超過 500 頁，這兩半各自 744 與 657 頁，所以印成四本。冊號照使用者
# 2026-09-08 對希臘與拉丁的裁定連續編（第一–四冊），現代語與文語的分野改由封面
# 副標題說明。
BOOK_LABELS = ("第一冊", "第二冊", "第三冊", "第四冊")

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

# 切點由 2026-09-08 的實測版面算出（現代語那半 744 頁、文語那半 657 頁），四冊
# 329–377 頁。切點只落在課與課之間，課次編號不動，附錄只印在該半的最後一分冊。
PARTS = [
    {"book": 1, "source": 1, "first": 1, "last": 30, "appendix": False},   # 約 374 頁
    {"book": 2, "source": 1, "first": 31, "last": 50, "appendix": True},   # 約 377 頁
    {"book": 3, "source": 2, "first": 1, "last": 32, "appendix": False},   # 約 329 頁
    {"book": 4, "source": 2, "first": 33, "last": 50, "appendix": True},   # 約 335 頁
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
    document.add_heading(f"本課 {len(rows)} 詞", level=2)
    table = document.add_table(rows=1, cols=5)
    widths = [8, 34, 34, 18, 47]
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
            H.set_cell_margins(cell)
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


def add_memory(document: Document, lesson: dict, interlinear: dict) -> None:
    units = lesson.get("memoryUnits") or []
    if not units:
        return
    document.add_heading(f"背誦 {len(units)} 句", level=2)
    for index, unit in enumerate(units, start=1):
        unit_id = f"v{lesson['volume']}-l{lesson['lesson']:02d}-m{index:03d}"
        tokens = (interlinear.get(unit_id) or {}).get("tokens") or []
        add_interlinear_unit(document, unit, tokens, lead=unit.get("label") or str(index))


def add_reading(document: Document, lesson: dict, interlinear: dict) -> None:
    # 讀文自己起一頁：生詞與背誦是預備，讀文才是這一課。
    H.page_break(document)
    H.add_label(document, "Reading")
    heading = document.add_heading(lesson["title"], level=2)
    H.paragraph_rule(heading, color=H.GOLD, size="8")
    for unit in lesson["units"]:
        tokens = (interlinear.get(unit["id"]) or {}).get("tokens") or []
        add_interlinear_unit(document, unit, tokens, lead=unit.get("label") or "")


def add_lesson(document: Document, lesson: dict, interlinear: dict, spec: dict,
               *, page_break_before: bool = True) -> None:
    H.add_label(document, f"Lesson {lesson['lesson']:02d}  ·  {spec['subtitle']}",
                page_break_before=page_break_before)
    number = H.mark_running_tag(document.add_paragraph())
    number.paragraph_format.space_after = Pt(1)
    H.set_run_font(number.add_run(f"第 {lesson['lesson']:02d} 課"), H.FONT_UI, 11,
                   bold=True, color=H.ACCENT)
    heading = document.add_heading(lesson["title"], level=1)
    H.paragraph_rule(heading, color=H.GOLD, size="14")
    source = document.add_paragraph()
    source.paragraph_format.space_after = Pt(6)
    H.add_mixed_script_text(
        source,
        f"{lesson['author']}　{lesson['extent']}　{lesson['orthography']}　{lesson['chars']} 字",
        H.FONT_ZH, H.CAPTION_PT, color=H.MUTED,
    )
    add_vocabulary(document, lesson["vocabulary"])
    add_memory(document, lesson, interlinear)
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
    H.set_run_font(spec_line.add_run("JIS B5  182 × 257 mm  ·  私人研讀"), H.FONT_UI,
                   8.5, color=H.MUTED)
    counts_line = H.add_body(
        document,
        f"{counts['lessons']} 課．{counts['words']} 詞．背誦 {counts['memory']} 句．"
        f"讀文 {counts['chars']:,} 字",
        size=H.CAPTION_PT, color=H.MUTED)
    counts_line.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_front_matter(document: Document, spec: dict, part: dict, lessons: list[dict]) -> None:
    counts = {
        "lessons": len(lessons),
        "words": sum(len(l["vocabulary"]) for l in lessons),
        "memory": sum(len(l["memoryUnits"]) for l in lessons),
        "chars": sum(l["chars"] for l in lessons),
    }
    add_cover(document, spec, part, counts)
    H.page_break(document)
    document.add_heading("體例與來源", level=1)
    for line in (
        "詞序依《大家的日本語》課次，經 u-biq 逐課頁重建；專名不佔課內詞額，另立附錄專名表。",
        "重音欄印的是來源頁面自己的斷點（は・や・い），不是重音型編號——斷點是抓得到的事實，編號是推論。",
        "讀文與背誦一律取宗教學、宗教史或宗教典籍；詞照課本，文照領域。",
        "聖書用文語訳（明治元訳舊約、大正改訳新約，公有領域），不用口語訳或新共同訳。",
        "逐詞對譯：本課詞表的譯法優先，其次是助詞助動詞表，再其次才是模型；查不到的留白，不用別的語言頂替。",
        "佛典尚未收入。素材抓得到，但訓読者與年份查不到，且混著漢文與梵文轉寫；依合約寧缺勿濫。",
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
}
CORPUS_TABLE_DEFAULT = (("form", "詞"), ("zh", "繁中"), ("count", "次"), ("lessons", "見於"))
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
        widths = {3: [46, 25, 70], 4: [34, 34, 16, 57]}[len(columns)]
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
    attached = attach_sense(lessons, sense)
    units = sum(len(l["units"]) + len(l["memoryUnits"]) for l in lessons)
    print(f"  整句中譯 {attached:,}／{units:,} 段", flush=True)

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
        add_lesson(document, lesson, interlinear, spec, page_break_before=index > 0)

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
