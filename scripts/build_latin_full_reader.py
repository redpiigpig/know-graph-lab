#!/usr/bin/env python3
"""Lay out the two Latin volumes as JIS-B5 DOCX.

The page geometry, type ladder, table rhythm and palette are the Hebrew
reader's, imported rather than re-specified, so the three readers in this series
sit on a shelf as one set. What differs is what a Latin page has to carry: no
right-to-left runs, no pointing, but a vocabulary table whose first column is a
full set of principal parts rather than a single form, and a reading column that
alternates between verse-numbered scripture and the versicle-and-response of the
Mass.

Each lesson prints the same four things in the same order -- twenty words, ten
translation exercises, the reading, and the reading's Chinese -- because a
reader that reorders itself between lessons cannot be used as a reference.  The
exercises stand where two memory units used to; the units are still in the data
master and still served online, they just no longer print.

Nothing here is generated. Every string comes from the frozen data masters, and
where a master has a gap the page says so rather than leaving a silent blank:
a reading still awaiting its Chinese prints 〔中譯待補〕, which is a thing the
owner can see and act on.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Mm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import latin_source_texts as L  # noqa: E402
import build_hebrew_full_reader as H
import reader_page_budget as budget
import build_greek_full_reader as G
from proper_name_categories import PRINT_ORDER  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output" / "source-cache" / "original-readers" / "latin-full"
OUT_DIR = ROOT / "output" / "original-readers"

VOCABULARY = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-2000.json"
APPENDICES = ROOT / "data" / "originalReaders" / "vocabulary" / "latin-appendices.json"
SCRIPTURE = CACHE / "scripture-plan.json"
SIGAO = CACHE / "sigao-zh.json"
CHURCH = CACHE / "church-plan.json"
LITURGY = CACHE / "liturgy.json"
READINGS_ZH = CACHE / "readings-zh.json"
MEMORY = CACHE / "memory-units.json"
INTERLINEAR_PATH = CACHE / "interlinear.json"
GAP_ZH = CACHE / "reading-gap-zh.json"

# 🚨 這一句是給編者的：「付印前請對照《感恩祭典》核對」是製作待辦，印在課本上
# 就成了註記。禮儀譯文的身分由版權頁交代一次即可，不在每一課重複。
# 這條待辦改由 verify_latin_reader 報（它本來就在報）。
LITURGY_NOTE = ""

FONT_LA = "Times New Roman"
# 🚨 擁有者 2026-09-17：「字都不可以小於 12。」正文、生詞表、逐詞對譯的中文義、
# 整句中譯、練習——凡是要讀的字一律 ≥12pt。只有頁眉與頁碼維持小字，那是版口
# 標示不是閱讀內容。改這幾個數字會直接改變每頁容納的份量，讀文上限要跟著重算。
LATIN_PT = 12
# 練習題的句子設得比正文小一級：一頁要放十句，每句底下還有一條作答橫線，
# 而且是一句一句讀，不是連續讀下去。
EXERCISE_PT = 12
GLOSS_PT = 12

VOLUMES = {
    "上冊": {
        "subtitle": "武加大譯本",
        # 🚨 上冊自 2026-09-18 起也按節裁到篇幅上限，不能再說「完整」。
        "blurb": "十篇禮儀短經，四十章武加大經文選讀，中文並列思高譯本。",
        "appendix": "upper",
    },
    "下冊": {
        "subtitle": "從教父到教廷",
        "blurb": "五十篇教父、中世紀與教廷文獻，終卷為常年期主日彌撒經文全文。",
        "appendix": "lower",
    },
}

# 印製分冊：一本印刷實體不得超過 500 頁（2026-09-08 使用者定案）。切點只落在課與
# 課之間，課次編號不動（線上讀本與音檔靠它對應）。
# 歷史：2026-09-08 的版面下上冊 456 頁、下冊 840 頁，印成三冊；2026-09-18 一課壓到
# 八頁、讀文按版面預算節錄之後上冊 349 頁、下冊 324 頁，兩半各自進得去一本。
# 🚨 切點的存在理由只有一個：一本裝訂實體不得超過 500 頁（2026-09-08）。
# 2026-09-18 一課壓到八頁、讀文按版面預算節錄之後，各半只有 320–480 頁，上限不再
# 逼人，所以擁有者裁示並冊——回到「內容的一半＝一本實體書」。課次編號不動。
# 2026-09-25：行距放寬、作答線加高後上冊 511 頁、下冊 501 頁（目錄換頁補回來之後），
# 各切成兩本；附錄只印在各半的後一本。實測：上冊 252／261、下冊約 254／252。
PARTS = [
    {"book": 1, "source": "上冊", "first": 1, "last": 30, "appendix": False},
    {"book": 2, "source": "上冊", "first": 31, "last": 50, "appendix": True},
    {"book": 3, "source": "下冊", "first": 1, "last": 28, "appendix": False},
    {"book": 4, "source": "下冊", "first": 29, "last": 50, "appendix": True},
]
BOOK_LABELS = ("上冊（一）", "上冊（二）", "下冊（一）", "下冊（二）")

COLOPHON = [
    ("拉丁文本", "武加大譯本用 Clementine Vulgate（eBible.org latVUC 轉錄，公有領域）；"
                 "教父與中世紀文本取自 The Latin Library；教廷文獻取自本專案既有拉丁文檔；"
                 "彌撒經文取自 Collins《A Primer of Ecclesiastical Latin》讀本部分所印之現行彌撒常規。"),
    ("中文", "聖經章節用思高譯本（思高聖經學會）。其餘篇章的中文為研讀用譯文，"
             "非教會核准之禮儀譯本；中文彌撒經文以《感恩祭典》為準。"),
    ("詞彙", "上冊一千詞依 Collins《A Primer of Ecclesiastical Latin》原書順序；"
             "下冊一千詞依教父／中世紀與近現代教廷語料詞頻，與上冊互斥。"
             "詞形主要部分取自 Whitaker's WORDS。"),
    # 擁有者 2026-09-25：發音與著作權兩段不印。
]


def gap_fill() -> dict[str, str]:
    """The self-translated lines that fill what no register could supply.

    Keyed volume:lesson:index, the position of the line inside its lesson, which
    is stable because it is the position in the printed reading itself -- not a
    lesson number that a sort can move.
    """
    if not GAP_ZH.exists():
        return {}
    store = json.loads(GAP_ZH.read_text(encoding="utf-8"))
    return {key: row["zh"] for key, row in store["lines"].items() if row.get("zh")}


def apply_gaps(rows: dict[int, dict], volume: int) -> dict[int, dict]:
    filled = gap_fill()
    if not filled:
        return rows
    for lesson, row in rows.items():
        row["pairs"] = [
            (latin, zh or filled.get(f"v{volume}:l{lesson}:{index}", ""))
            for index, (latin, zh) in enumerate(row["pairs"])
        ]
    return rows


def load(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# page furniture
# --------------------------------------------------------------------------

# 字級 -> Word 大綱層級。走 Heading 樣式而非自畫的粗體段落，PDF 才有目錄書籤，
# 字級也只在 build_hebrew_full_reader 定義一次，三本書不會各飄各的。
HEADING_LEVEL = {H.TITLE_SIZE_PT: 0, H.H1_SIZE_PT: 1, H.H2_SIZE_PT: 2, H.H3_SIZE_PT: 3}


def heading(document, text: str, size: float, *, color=None, space_before=10,
            space_after=6, align=WD_ALIGN_PARAGRAPH.LEFT):
    level = HEADING_LEVEL.get(size)
    if level is None:
        paragraph = document.add_paragraph()
    else:
        paragraph = document.add_heading("", level=level)
    paragraph.alignment = align
    paragraph.paragraph_format.space_before = Pt(space_before)
    paragraph.paragraph_format.space_after = Pt(space_after)
    H.add_mixed_script_text(paragraph, text, H.FONT_ZH, size, bold=True,
                            color=color or H.ACCENT_DARK)
    return paragraph


def body(document, text: str, size=H.BODY_SIZE_PT, *, font=H.FONT_ZH, color=H.INK,
         italic=False, space_after=4, indent_mm=0.0):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(space_after)
    paragraph.paragraph_format.line_spacing = H.BODY_LINE_MULTIPLE
    if indent_mm:
        paragraph.paragraph_format.left_indent = Mm(indent_mm)
    H.add_mixed_script_text(paragraph, text, font, size, italic=italic, color=color)
    return paragraph


def page_break(document):
    document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# 封面上的拉丁題辭，一冊一句。
COVER_LATIN = {"上冊": "VULGATA ET LITURGIA", "下冊": "PATRES ET DOCTORES"}
VOLUME_NUMBER = {"上冊": 1, "下冊": 2}


def load_interlinear() -> dict:
    """逐詞對譯層。沒有就回空的——書照樣印得出來，只是沒有那一層。"""

    if not INTERLINEAR_PATH.exists():
        return {}
    return json.loads(INTERLINEAR_PATH.read_text(encoding="utf-8")).get("units", {})


def title_page(document, volume: str, spec: dict, part: dict):
    """深色橫幅封面，與希伯來、希臘那兩本同一個版式。"""
    table = document.add_table(rows=1, cols=1)
    H.set_table_geometry(table, [H.USABLE_WIDTH_MM])
    H.set_borders(table, outside=False, inside=False)
    cell = table.cell(0, 0)
    H.set_cell_margins(cell, top=500, bottom=500, start=350, end=350)
    palette = H.cover_colors("la")
    H.shade(cell, palette["banner"])

    eyebrow = cell.paragraphs[0]
    eyebrow.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.set_run_font(eyebrow.add_run("ORIGINAL-LANGUAGE READER"), H.FONT_UI, 8,
                   color=palette["rule"], bold=True)
    name = cell.add_paragraph()
    name.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.add_mixed_script_text(name, "教會拉丁文原文讀本", H.FONT_ZH, 25, bold=True,
                            color="FFF8ED")
    motto = cell.add_paragraph()
    motto.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.set_run_font(motto.add_run(COVER_LATIN[volume]), FONT_LA, 18, color="FFF8ED")

    document.add_paragraph().paragraph_format.space_after = Pt(26)
    line = document.add_paragraph()
    line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.add_mixed_script_text(
        line,
        f"{part_label(part)}　第 {part['first']:02d}–{part['last']:02d} 課　{spec['subtitle']}",
        H.FONT_ZH, 12, bold=True, color=H.INK)
    para = body(document, spec["blurb"], 10.5, color=H.ACCENT)
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    document.add_paragraph().paragraph_format.space_after = Pt(26)
    spec_line = document.add_paragraph()
    spec_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    H.paragraph_rule(spec_line, color=palette["rule"], size="24")
    # 擁有者 2026-09-25：封面不印「N 課．N 詞．讀本 N 詞（…）」那行規格。
    page_break(document)

    heading(document, "凡例", H.H1_SIZE_PT)
    for label, text in COLOPHON:
        heading(document, label, H.H3_SIZE_PT, space_before=8, space_after=2)
        body(document, text, H.TRANSLATION_PT, color=H.MUTED)
    page_break(document)


def vocabulary_table(document, rows: list[dict]):
    H.compact_heading(
        heading(document, f"生詞　{len(rows)} 個", H.H2_SIZE_PT),
        before=H.SECTION_HEADING_SPACE_BEFORE_PT,
        after=H.SECTION_HEADING_SPACE_AFTER_PT, line_spacing=1.0)
    table = document.add_table(rows=1, cols=3)
    # 欄寬是量出來的，而且是**兩個方向都試過**的。主要部分（forms）的字數中位數
    # 22、第九十百分位 39（12pt 下約 78mm）；繁中詞義中位數 7 個字、第九十百分位
    # 12 個字（約 50mm）。兩欄都給到第九十百分位就超出版心 141mm，只能取捨。
    # 🚨 把 forms 放寬到 56%、詞義縮到 32% 反而更糟：第二冊二十九課裡跨頁的從 13
    # 課變成 19 課，整冊多了六頁。詞義欄折行的代價跟 forms 欄一樣是多一整列，而
    # 詞義的分佈比 forms 集中得多，縮它等於讓更多列折行。要讓就讓詞類欄——它印的
    # 是「形」「動」「片語」，兩個字就夠。
    widths = [H.USABLE_WIDTH_MM * 0.46, H.USABLE_WIDTH_MM * 0.12, H.USABLE_WIDTH_MM * 0.42]
    H.set_table_geometry(table, widths)
    H.set_borders(table)
    header = table.rows[0]
    for cell, label in zip(header.cells, ("拉丁文", "詞類", "繁體中文")):
        H.shade(cell, H.PALE)
        H.set_cell_margins(cell, top=H.VOCAB_CELL_PAD_DXA,
                           bottom=H.VOCAB_CELL_PAD_DXA,
                           start=H.VOCAB_CELL_SIDE_PAD_DXA,
                           end=H.VOCAB_CELL_SIDE_PAD_DXA)
        H.tighten_cell(cell)
        paragraph = cell.paragraphs[0]
        H.add_mixed_script_text(paragraph, label, H.FONT_ZH, H.LABEL_PT, bold=True,
                                color=H.ACCENT_DARK)
    H.set_repeat_header(header)
    for entry in rows:
        row = table.add_row()
        # Keep a vocabulary row whole.  A row that splits across a page break
        # leaves what looks like an empty first row at the top of the next page,
        # which reads as a missing word rather than as a continuation.
        H.prevent_row_split(row)
        cells = row.cells
        H.set_cell_margins(cells[0], top=H.VOCAB_CELL_PAD_DXA,
                           bottom=H.VOCAB_CELL_PAD_DXA,
                           start=H.VOCAB_CELL_SIDE_PAD_DXA,
                           end=H.VOCAB_CELL_SIDE_PAD_DXA)
        H.tighten_cell(cells[0])
        H.add_mixed_script_text(cells[0].paragraphs[0], entry.get("forms") or entry["headword"],
                                FONT_LA, H.TABLE_SIZE_PT)
        H.set_cell_margins(cells[1], top=H.VOCAB_CELL_PAD_DXA,
                           bottom=H.VOCAB_CELL_PAD_DXA,
                           start=H.VOCAB_CELL_SIDE_PAD_DXA,
                           end=H.VOCAB_CELL_SIDE_PAD_DXA)
        H.tighten_cell(cells[1])
        H.add_mixed_script_text(cells[1].paragraphs[0], short_pos(entry), H.FONT_ZH,
                                H.LABEL_PT, color=H.MUTED)
        H.set_cell_margins(cells[2], top=H.VOCAB_CELL_PAD_DXA,
                           bottom=H.VOCAB_CELL_PAD_DXA,
                           start=H.VOCAB_CELL_SIDE_PAD_DXA,
                           end=H.VOCAB_CELL_SIDE_PAD_DXA)
        H.tighten_cell(cells[2])
        H.add_mixed_script_text(cells[2].paragraphs[0], entry.get("glossZh") or "",
                                H.FONT_ZH, H.TABLE_SIZE_PT)
    document.add_paragraph().paragraph_format.space_after = Pt(2)


POS_ZH = {"N": "名", "V": "動", "ADJ": "形", "ADV": "副", "PREP": "介", "CONJ": "連",
          "PRON": "代", "NUM": "數", "INTERJ": "嘆",
          "NOUN": "名", "VERB": "動", "PROPN": "名", "ADP": "介",
          "CCONJ": "連", "SCONJ": "連", "DET": "限", "AUX": "動", "INTJ": "嘆"}

GRAM_HINTS = (
    ("prep", "介"), ("conj", "連"), ("adv", "副"), ("pron", "代"),
    ("num", "數"), ("interj", "嘆"), ("indecl", "不變"),
)


# 讀不出來的四十八條：三詞尾以外的形容詞（memor、vetus、dīves 只給屬格）、
# 片語（in aeternum、grātiās agere）、不規則或缺位動詞（ait、inquam、fore）、
# 以及兩個希臘文禮儀用語。讀規則讀不出來，就一條一條寫，不要留白也不要猜。
BY_FORMS_POS = {
    "in saecula (saeculōrum)": "片語", "in aeternum": "片語", "grātiās agere": "片語",
    "in prīmīs": "片語", "male habeō": "片語", "sicut .. et": "片語", "aut . . aut": "片語",
    "factum est": "片語", "necesse est": "片語",
    "noster, nostra, nostrum": "形", "sacer, sacra, sacrum": "形",
    "plēnus, -a, -um (+ abl.)": "形", "salūtifer, salūtifera, salūtiferum": "形",
    "vester, vestra, vestrum": "形", "quidam, quaedam, quoddam": "形",
    "ruber, rubra, rubrum": "形", "ācer, ācris, ācre": "形", "liber, libera, liberum": "形",
    "dexter, dextera, dexterum": "形", "alius, alia, aliud": "形",
    "alter, altera, alterum": "形", "vīcīnus, vīcīna, vīcīnum": "形", "intentus": "形",
    "memor": "形", "clēmēns": "形", "vetus": "形", "dīves": "形",
    "pauper, gen., pauperis": "形", "compār, gen., comparis": "形",
    "dispār, gen., disparis": "形", "pār, gen., paris": "形",
    "-plēre, -plēvi, -plētus": "動", "videor, vidērī, — vīsus sum": "動",
    "ait; aiunt": "動", "quaesō/quaesumus": "動", "fore": "動", "inquam": "動",
    "nōlī/nōlite": "動", "placet": "動", "eléison": "動",
    "fulgor, fulgōris, —": "名", "peregrīnantis, gen., peregrīnantis": "名", "Kyrie": "名",
    "-ne": "質", "ūsque": "副", "avē!": "嘆", "salvē": "嘆",
    "satis (+ partitive gen.)": "副",
}


def short_pos(entry: dict) -> str:
    """Say what part of speech this is, reading the dictionary line if need be.

    Collins does not label his nouns and verbs: the gender abbreviation at the
    end of a noun entry and the four principal parts of a verb entry *are* the
    labels.  Taking the label only from an explicit field leaves the column
    empty for most of the book, which is what the first print run did.
    """
    by_forms = BY_FORMS_POS.get((entry.get("forms") or "").strip())
    if by_forms:
        return by_forms
    for key in ("gram", "pos"):
        value = (entry.get(key) or "").strip()
        if value in POS_ZH:
            return POS_ZH[value]
    gram = (entry.get("gram") or "").lower()
    for needle, label in GRAM_HINTS:
        if needle in gram:
            return label
    forms = (entry.get("forms") or "").strip()
    parts = [p.strip() for p in forms.split(",")]
    if re.search(r"(^|[, ])(m|f|n|c)\.$", forms):
        return "名"
    if re.search(r"-(a|ae), -(um|a)$|-is, -e$|, -a, -um$", forms):
        return "形"
    if len(parts) >= 4 or re.search(r"(are|ēre|ere|īre|ire)$", parts[1] if len(parts) > 1 else ""):
        return "動"
    if len(parts) == 2 and parts[1]:
        return "名"
    return ""


def exercise_blocks(volume_number: int) -> dict[int, dict]:
    """This volume's ten-item exercises, keyed by the lesson they belong to.

    Bound by vocabulary ordinal, never by the lesson number the exercise file
    carries: the reading plan sorts by difficulty, so a lesson number is an
    output of that sort and a resort would move every block one lesson without
    changing a single count.  Same rule and same reason as the Hebrew reader.
    """
    path = CACHE / f"exercise-set-v{volume_number}.json"
    if not path.exists():
        raise SystemExit(
            f"缺 {path.name}；先跑 scripts/assemble_latin_exercises.py "
            f"--volume {volume_number} --write"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("direction") != "original-to-chinese":
        raise SystemExit(f"{path.name} 的 direction 不是 original-to-chinese")
    entries = load(VOCABULARY)["entries"]
    wanted = "上冊" if volume_number == 1 else "下冊"
    lesson_of = {
        entry["ordinal"]: entry["lesson"]
        for entry in entries
        if entry["volume"] == wanted
    }
    bound: dict[int, dict] = {}
    for block in payload["lessons"]:
        hosts = {
            lesson_of[word["ordinal"]]
            for item in block["items"]
            for word in item.get("targetWords") or []
            if word["ordinal"] in lesson_of
        }
        if len(hosts) != 1:
            raise SystemExit(f"練習題第 {block['lesson']} 課橫跨課次 {sorted(hosts)}")
        host = hosts.pop()
        if host in bound:
            raise SystemExit(f"第 {host} 課被兩組練習題認領")
        bound[host] = block
    return bound


def exercise_section(document, block: dict | None, lesson: int) -> None:
    """The ten translation exercises, where the memory units used to stand.

    Only the Latin is printed.  A Chinese line beside the sentence would be the
    answer to the question the exercise asks, so an anchored item prints its
    reference and a composed one prints nothing but its number; neither prints a
    translation.  See skills/…/references/exercise-sets.md.
    """
    if block is None:
        raise SystemExit(f"第 {lesson} 課沒有練習題：exercise-set 對不上本課詞表")
    exercise_heading = H.compact_heading(
        heading(document, f"本課翻譯練習（{len(block['items'])}題）", H.H2_SIZE_PT),
        before=H.SECTION_HEADING_SPACE_BEFORE_PT,
        after=H.SECTION_HEADING_SPACE_AFTER_PT, line_spacing=1.0)
    exercise_heading.paragraph_format.page_break_before = True
    intro = body(document, "把每一句譯成繁體中文。標有出處的句子引自原典。",
                 H.CAPTION_PT, color=H.MUTED, space_after=2)
    intro.paragraph_format.line_spacing = Pt(H.EXERCISE_INTRO_LINE_PT)
    H.set_keep(intro, next_paragraph=True)
    for item in block["items"]:
        head = document.add_paragraph()
        head.paragraph_format.space_before = Pt(H.EXERCISE_ITEM_SPACE_BEFORE_PT)
        head.paragraph_format.space_after = Pt(H.EXERCISE_ITEM_SPACE_AFTER_PT)
        head.paragraph_format.line_spacing = Pt(H.EXERCISE_LABEL_LINE_PT)
        H.set_run_font(head.add_run(f"{item['no']:02d}"), H.FONT_UI, H.LABEL_PT,
                       bold=True, color=H.ACCENT)
        if item["kind"] == "quoted":
            H.set_run_font(head.add_run("　"), H.FONT_UI, H.CAPTION_PT, color=H.MUTED)
            # 🚨 上冊的出處是 EST.4.12 這種書卷代碼，下冊的是《本篤十六：天主是愛》
            # 這種中文篇名。整串設成轉寫字體，漢字就全部回退到 LibreOffice 自己
            # 挑的字型——實測是沒有內嵌的 NotoSansJP-Thin，送印會被換掉。按字種分。
            for piece in re.split(r"([　-鿿＀-￯]+)", item["ref"]):
                if not piece:
                    continue
                cjk = bool(re.match(r"[　-鿿＀-￯]", piece))
                H.set_run_font(head.add_run(piece),
                               H.FONT_ZH if cjk else H.FONT_TRANSLIT,
                               H.CAPTION_PT, color=H.MUTED)
        H.set_keep(head, next_paragraph=True)
        latin = body(document, item["text"], EXERCISE_PT, font=FONT_LA,
                     space_after=H.EXERCISE_TEXT_SPACE_AFTER_PT, indent_mm=4)
        latin.paragraph_format.line_spacing = H.EXERCISE_TEXT_LINE_SPACING
        H.set_keep(latin, next_paragraph=True)
        H.add_answer_lines(document)


_LATIN_METRICS = None
FONT_FILES = (
    "C:/Windows/Fonts/NotoSerif-Regular.ttf",
    "C:/Windows/Fonts/pala.ttf",
    "C:/Windows/Fonts/times.ttf",
)


def latin_width_mm(text: str, size_pt: float) -> float:
    """一個拉丁詞印出來有多寬。

    量寬要用真的字體檔，不能用字數乘係數——逐詞排版是照量出來的寬度切行的。
    系統沒有 Noto Serif 就退回 Palatino：都是襯線體，寬度差得有限，而且差的
    後果只是某一行少排一個詞，不是排錯。
    """

    global _LATIN_METRICS
    if _LATIN_METRICS is None:
        from PIL import ImageFont

        for candidate in FONT_FILES:
            if Path(candidate).exists():
                _LATIN_METRICS = ImageFont.truetype(candidate, 1000)
                break
    return _LATIN_METRICS.getlength(text) / 1000 * size_pt / 72 * 25.4


def latin_run(paragraph, text: str, size_pt: float) -> None:
    H.set_run_font(paragraph.add_run(text), FONT_LA, size_pt, color=H.INK)


def add_latin_interlinear(document, tokens: list, *, sense: str = "") -> None:
    """逐詞對譯：拉丁在上、繁中在下，整句中譯收在後面。

    版式與希臘那本同一支函式，只換量寬與印字的字體——兩本並排時逐詞區塊要
    長得一樣，那是同一套書的一部分。
    """

    G.add_interlinear(
        document,
        tokens,
        sense=sense,
        greek_pt=LATIN_PT,
        available_mm=H.USABLE_WIDTH_MM,
        measure=latin_width_mm,
        render=latin_run,
    )

def reading_block(document, title: str, pairs: list[tuple[str, str]], note: str = "",
                  *, key: str = "", interlinear: dict | None = None):
    # 每一課的讀物另起一頁：詞表與練習題是準備，讀物是這一課的正事。
    page_break(document)
    heading(document, f"讀本　{title}", H.H2_SIZE_PT, space_before=0, space_after=3)
    if note:
        body(document, note, H.CAPTION_PT, color=H.MUTED, space_after=4)
    for index, (latin, chinese) in enumerate(pairs, start=1):
        tokens = (interlinear or {}).get(f"reading:{key}:{index}", {}).get("tokens")
        if tokens:
            add_latin_interlinear(document, tokens, sense=chinese or "")
            continue
        # 還沒有逐詞層的行照舊整行印，缺就要看得出來缺。
        body(document, latin, LATIN_PT, font=FONT_LA, space_after=1)
        body(document, chinese or "", H.TRANSLATION_PT, color=H.MUTED,
             space_after=5)


# --------------------------------------------------------------------------
# content assembly
# --------------------------------------------------------------------------

def upper_readings() -> dict[int, dict]:
    plan = load(SCRIPTURE)
    chinese = load(SIGAO, {"chapters": []})
    translated = load(READINGS_ZH, {"units": {}})
    liturgy = {row["id"]: row for row in load(LITURGY, {"formulas": []})["formulas"]}
    zh_by_chapter = {(c["book"], c["latinChapter"]): c for c in chinese["chapters"]}
    verses = L.vulgate_chapters()

    out: dict[int, dict] = {}
    for row in plan["chapters"]:
        if row["kind"] == "liturgy":
            source = liturgy.get(row["id"], {})
            unit = translated["units"].get(f"formula:{row['id']}", {})
            zh_lines = [z for segment in unit.get("segments", []) for z in segment["zh"]]
            pairs = list(zip(source.get("lines", []), zh_lines + [""] * len(source.get("lines", []))))
            # The liturgical Chinese is deliberately absent, not merely late:
            # a machine rendering of a formula the congregation knows by heart
            # is an error the label 自譯 does not cover.
            note = "　".join(x for x in (row.get("note"), LITURGY_NOTE) if x)
            pairs, note = clip_reading(pairs, note, unit="行")
            out[row["lesson"]] = {"title": f"{row['title']}　{row['latinTitle']}",
                                  "pairs": pairs, "note": note}
            continue
        chapter_zh = zh_by_chapter.get((row["book"], row["chapter"]))
        zh_by_verse = {v["verse"]: v["text"] for v in chapter_zh["verses"]} if chapter_zh else {}
        pairs = [(f"{number}　{text}", zh_by_verse.get(number, ""))
                 for number, text in sorted(verses[(row["book"], row["chapter"])].items())]
        # 🚨 alignmentNote（「拉丁 25 節，中文 26 節，需逐節核對」）是給維護者的，
        # 留在 scripture-plan 裡給驗證器看；印上紙本就是課本裡的校對便條。
        note = row.get("note") or ""
        # 武加大一章的自然單位是節，所以裁的單位是節，不是詞。
        pairs, note = clip_reading(pairs, note, unit="節")
        out[row["lesson"]] = {"title": row["title"], "pairs": pairs, "note": note}
    return apply_gaps(out, 1)


SECTION_NUMBER = re.compile(r"^\s*(\d{1,3})\s*[.、]")
# The number is not always tight against its point: Dignitatis Humanae
# prints "2 . Haec Vaticana Synodus declarat", and a pattern that demands
# the two be adjacent finds no sections at all and silently pairs nothing.


def chinese_by_section(path: str) -> dict[int, str]:
    """Index a published translation by the section numbers it prints.

    Pairing the two sides by paragraph index is what this replaced, and it was
    wrong every time: Sacrosanctum Concilium has 362 Latin paragraphs against
    11 Chinese ones, so paragraph five of each is five different places in the
    document.  Where both sides number their sections, the number is the join.
    """
    latin = ROOT / path
    chinese = latin.with_name(latin.name.replace("-latin.txt", "-chinese.txt"))
    if not chinese.exists():
        return {}
    raw = chinese.read_text(encoding="utf-8", errors="replace")
    body = re.sub(r"^#.*$", "", raw, flags=re.M)
    sections: dict[int, list[str]] = {}
    current = 0
    for line in body.splitlines():
        match = SECTION_NUMBER.match(line)
        if match:
            current = int(match.group(1))
        if current and line.strip():
            sections.setdefault(current, []).append(line.strip())
    return {number: " ".join(rows) for number, rows in sections.items()}


# 一課的讀文能收多長，由共用的版面預算決定：scripts/reader_page_budget.py。
# 那裡不是一個詞數上限，而是一個量出來的版面模型——「這麼長、這麼多單元，排出來
# 會不會超過八頁」。單元數那一項不能省：同樣五百詞，分五段與分五十段厚度差很多。
#
# 擁有者 2026-09-17：「一課最多不能超過 8 頁」「大約抓個 500-800 字左右就好」
# 「但要是自然段落的選集喔，不要是語意沒講完就中斷」。所以裁的單位是文本自己的
# 分段（節、段、章），不是詞數切點。

def clip_reading(pairs: list, note: str, *, unit: str = "段") -> tuple[list, str]:
    """超過上限就從篇首連續取整節／整段；回傳（段落、註記）。

    🚨 裁過一定要在 note 講出來。本系列的停止條件之一就是「宣告為全篇的讀文
    其實是節錄」：裁了卻不說，書上看起來一切正常，讀者以為自己讀完了一整章。
    """
    def weight(pair) -> int:
        return len(L.words(pair[0]))

    total = sum(weight(pair) for pair in pairs)
    if budget.fits("lat", total, len(pairs)):
        return pairs, note
    kept = budget.clip(pairs, weight, "lat")
    # 🚨 來源的 note 可能已經寫著「（完整，共 21 節）」；裁過之後把那句話留著，
    # 同一行就會同時宣告完整與節錄。取代，不要附加。
    base = note.replace("（完整，", "（").replace("（完整）", "").strip()
    extent = f"取前 {len(kept)} {unit}（全文 {len(pairs)} {unit}）"
    return kept, f"{base}　{extent}".strip() if base else extent


def lower_readings() -> dict[int, dict]:
    plan = load(CHURCH)
    translated = load(READINGS_ZH, {"units": {}})
    out: dict[int, dict] = {}
    for row in plan["readings"]:
        import translate_latin_readings_zh as translator
        key = translator.reading_key(row)
        unit = translated["units"].get(key)
        if unit:
            pairs = [(segment["latin"][0], segment["zh"][0])
                     for segment in unit["segments"]]
            # 🚨 translationNote（「自譯（研讀用，非教會核准禮儀譯本）」）不印在
            # 每一篇讀文底下：版權頁已經講過一次，45 篇各印一次就成了註記。
            note = row["excerptRule"]
        else:
            # Cut with the same rule the plan measured: whole divisions of the
            # work, never part of one.  Re-splitting on blank lines here instead
            # would print sixteen thousand words of Vincent of Lerins, because
            # several Latin Library files contain no blank line at all.
            import build_latin_church_plan as plan_module
            latin_text = (ROOT / row["sourcePath"]).read_text(encoding="utf-8", errors="replace")
            if row.get("section"):
                latin_text = plan_module.section(latin_text, tuple(row["section"]))
            if row["extent"] == "excerpt":
                latin_text, _, _ = plan_module.complete_unit(latin_text)
            paragraphs = [translator.clean_paragraph(part)
                          for part in latin_text.split(chr(10) * 2) if part.strip()]
            paragraphs = [part for part in paragraphs if part]
            chinese = (chinese_by_section(row["sourcePath"])
                       if row["chineseParallel"] == "repo-aligned-by-number" else {})
            pairs = []
            for paragraph in paragraphs:
                match = SECTION_NUMBER.match(paragraph)
                zh = chinese.get(int(match.group(1)), "") if match else ""
                pairs.append((paragraph, zh))
            note = row["excerptRule"]

        pairs, note = clip_reading(pairs, note, unit="段")
        out[row["lesson"]] = {
            "title": f"{row['title']}　{row['latinTitle']}", "pairs": pairs, "note": note,
        }
    return apply_gaps(out, 2)


def appendix_groups(table: dict) -> list[tuple[str, list[dict]]]:
    """把一張附錄表切成印得出來的小節。

    專名表用 `category`（九類，見 scripts/proper_name_categories.py），其餘的表用
    資料裡本來就有的 `group`；沒有分組欄位的整張當一節。次序照 PRINT_ORDER。
    """
    field = "category" if any(e.get("category") for e in table["entries"]) else "group"
    buckets: dict[str, list[dict]] = {}
    for entry in table["entries"]:
        buckets.setdefault((entry.get(field) or "").strip(), []).append(entry)
    if len(buckets) <= 1:
        return [("", table["entries"])]
    known = [n for n in PRINT_ORDER if n in buckets]
    return [(n, buckets[n]) for n in known + [n for n in buckets if n not in known]]


def appendix_section(document, tables: dict, *, page_break_before=True):
    if page_break_before:
        page_break(document)
    H.add_label(document, "Appendix  ·  reference tables")
    top = heading(document, "附錄", H.H1_SIZE_PT)
    H.paragraph_rule(top, color=H.GOLD, size="14")
    for table in tables.values():
        entries = table["entries"]
        heading(document, f"{table['title']}（{len(entries)} 條）", H.H2_SIZE_PT,
                space_before=10, space_after=4)
        for group, rows in appendix_groups(table):
            if group:
                heading(document, f"{group}　{len(rows)} 條", H.H3_SIZE_PT,
                        space_before=6, space_after=2)
            # 全印。先前截在 200 條是為了控頁數，但一本查不到東西的附錄不值那些紙：
            # 上冊專名表 585 條裡有 385 條就是這樣沒印出來的。
            for row in rows:
                latin = row.get("forms") or row.get("headword", "")
                # 不退到 glossEn。退而求其次的預設值會把缺口藏起來：這幾張表建的
                # 時候只帶英文釋義，於是一本繁體中文讀本的附錄印出整頁
                # 「mother's brother」「the day before the Kalends」，而且看不出
                # 那是缺中文還是本來就這樣。缺就該看得出來缺。
                zh = (row.get("zh") or row.get("glossZh") or "").strip()
                paragraph = document.add_paragraph()
                paragraph.paragraph_format.space_after = Pt(1)
                H.add_mixed_script_text(paragraph, latin + "　", FONT_LA, H.TABLE_SIZE_PT)
                if zh:
                    H.add_mixed_script_text(paragraph, zh, H.FONT_ZH, H.TABLE_SIZE_PT,
                                            color=H.MUTED)
                else:
                    H.add_mixed_script_text(paragraph, "（中文待補）", H.FONT_ZH,
                                            H.CAPTION_PT, color=H.MUTED)


def part_label(part: dict) -> str:
    return BOOK_LABELS[part["book"] - 1]


def running_title(part: dict) -> str:
    return f"教會拉丁文原文讀本　{part_label(part)}"


def relabel(document, volume: str, spec: dict, part: dict) -> None:
    """Put this book's name in the running head.

    The layout is imported from the Hebrew reader, and so is its running header;
    left alone, every page of the Latin volumes says 聖經希伯來文原文讀本.
    """
    H.write_running_head(document.sections[0], running_title(part))
    document.core_properties.title = f"教會拉丁文原文讀本：{part_label(part)}"
    document.core_properties.subject = (
        f"{spec['subtitle']}　第 {part['first']:02d}–{part['last']:02d} 課")


def build(book_number: int) -> Path:
    part = next((item for item in PARTS if item["book"] == book_number), None)
    if part is None:
        raise SystemExit(f"沒有第 {book_number} 冊")
    volume = part["source"]
    spec = VOLUMES[volume]
    lesson_range = range(part["first"], part["last"] + 1)
    vocabulary = load(VOCABULARY)["entries"]
    appendices = load(APPENDICES, {})
    readings = upper_readings() if volume == "上冊" else lower_readings()

    per_lesson: dict[int, list[dict]] = {}
    for entry in vocabulary:
        if entry["volume"] == volume:
            per_lesson.setdefault(entry["lesson"], []).append(entry)
    exercises = exercise_blocks(VOLUME_NUMBER[volume])

    document = Document()
    H.configure(document)
    relabel(document, volume, spec, part)
    title_page(document, volume, spec, part)
    interlinear = load_interlinear()
    volume_number = VOLUME_NUMBER[volume]
    H.add_contents(
        document,
        [
            (
                f"{lesson:02d}",
                readings.get(lesson, {}).get("title") or "　",
                "武加大經文" if volume == "上冊" else "教父與教廷文獻",
            )
            for lesson in lesson_range
        ],
        title=f"{part_label(part)}目錄",
        accent=H.cover_colors("la")["accent"],
    )

    H.start_section(document, running_title(part), lesson_tag=True)
    for index, lesson in enumerate(lesson_range):
        reading = readings.get(lesson, {"title": "", "pairs": [], "note": ""})
        # 眉標 → 課次 → 課題 → 金線，與希伯來那本逐項對齊。
        H.add_label(document, f"Lesson {lesson:02d}  ·  {spec['subtitle']}",
                    page_break_before=index > 0)
        number = H.mark_running_tag(document.add_paragraph())
        number.paragraph_format.space_after = Pt(0)
        number.paragraph_format.line_spacing = Pt(H.LESSON_NUMBER_LINE_PT)
        H.set_run_font(number.add_run(f"第 {lesson:02d} 課"), H.FONT_UI, 11,
                       bold=True, color=H.ACCENT)
        opener = heading(document, reading["title"] or "　", H.H1_SIZE_PT,
                         space_before=H.LESSON_TITLE_SPACE_BEFORE_PT,
                         space_after=H.LESSON_TITLE_SPACE_AFTER_PT)
        opener.paragraph_format.line_spacing = H.LESSON_TITLE_LINE_SPACING
        H.paragraph_rule(opener, color=H.GOLD, size="14")
        key = f"v{volume_number}-{lesson}"
        vocabulary_table(document, per_lesson.get(lesson, []))
        exercise_section(document, exercises.get(lesson), lesson)
        if reading["pairs"]:
            reading_block(document, reading["title"], reading["pairs"], reading["note"],
                          key=key, interlinear=interlinear)

    if part["appendix"]:
        H.start_section(document, f"{running_title(part)}　附錄")
        appendix_section(document, appendices.get(spec["appendix"], {}), page_break_before=False)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"latin-original-reader-vol{book_number}.docx"
    # 換頁前的空段落會印出只有眉標的一頁；存檔前掃掉。
    H.drop_spacer_before_break(document)
    document.save(path)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description="排版教會拉丁文讀本 B5 DOCX（兩冊，每冊不超過 500 頁）")
    ap.add_argument("--book", type=int, choices=tuple(part["book"] for part in PARTS),
                    help="只排某一冊")
    args = ap.parse_args()
    for number in ([args.book] if args.book else [part["book"] for part in PARTS]):
        path = build(number)
        print(f"{BOOK_LABELS[number - 1]} -> {path.relative_to(ROOT)}  "
              f"{path.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
