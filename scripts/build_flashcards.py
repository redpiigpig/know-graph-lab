#!/usr/bin/env python3
"""Build a printable vocabulary flashcard deck: Hebrew, or Greek volume 1 or 2.

The sheet follows the English tutoring deck already in use: A4 landscape, eight
cards to a page, front sheet then back sheet, duplex.  Two things differ.

No cutting lines are printed.  A hairline that prints a millimetre off shows up
on the finished card as a crooked edge, so instead the grid is even and the
cover sheet gives the two measurements a guillotine needs.

The back sheet mirrors the column order (4-3-2-1 instead of 1-2-3-4).  Printed
duplex, that is what puts each meaning behind its own word; without it every
card would carry a neighbour's translation.

Pictures are optional by design: a card with no honest picture prints without
one rather than borrowing an approximate image.

The Hebrew master carries a part of speech per word.  The Greek master carries
none, so it is worked out in ``flashcard_pos`` and left blank where the citation
form is ambiguous — a blank line costs nothing, a wrong label is learned as fact.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_ALIGN_VERTICAL, WD_ROW_HEIGHT_RULE, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flashcard_pos import greek_part_of_speech  # noqa: E402

# The Latin deck reads the identity and the part of speech the reader's own
# builders already worked out, rather than deriving either a second time here.
import latin_source_texts as _latin_text  # noqa: E402
from build_latin_full_reader import short_pos as latin_pos  # noqa: E402


def latin_key(entry: dict) -> str:
    return _latin_text.fold(entry.get("forms") or entry["headword"])

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "output/source-cache"
IMAGE_DIR = CACHE / "flashcards/openmoji-618"
OUTPUT_DIR = ROOT / "output/flashcards"

PAGE_W_MM = 297.0
PAGE_H_MM = 210.0
COLS = 4
ROWS = 2
CARD_W_MM = PAGE_W_MM / COLS      # 74.25
# Both figures are measured, not derived.  The renderer reserves more vertical
# space than the declared margins account for, and it moves the second row to a
# page of its own well before the arithmetic says the rows should stop fitting;
# a 10 mm margin fails where 5 mm holds, and 97 mm rows fail where 94 mm hold.
CARD_H_MM = 94.0
MARGIN_V_MM = 5.0

FONT_ZH = "MingLiU"
FONT_UI = "MingLiU"
INK = "1B1B1B"
MUTED = "8A8A8A"

POS_PT = 12
LESSON_PT = 10
IMAGE_MM = 32

# The glosses run from two characters to twenty-seven, so the meaning line is
# sized to fit the card rather than set at one size and allowed to overflow.
ZH_STEPS = ((6, 24), (10, 20), (16, 16), (22, 13), (99, 11))

POS_ZH = {
    "noun": "名詞",
    "verb": "動詞",
    "adjective": "形容詞",
    "adverb": "副詞",
    "pronoun": "代名詞",
    "preposition": "介系詞",
    "conjunction": "連接詞",
    "particle": "質詞",
    "proper_name": "專名",
    "particle_or_preposition": "質詞／介系詞",
    "interrogative_particle": "疑問質詞",
    "prepositional_phrase": "介系詞片語",
    "adverbial_phrase": "副詞片語",
    "conjunction_phrase": "連接詞片語",
}

# The Latin master already labels its own parts of speech, one character each;
# the card prints the two-character form the other decks use.
POS_LATIN = {
    "名": "名詞", "動": "動詞", "形": "形容詞", "副": "副詞", "介": "介系詞",
    "連": "連接詞", "代": "代名詞", "數": "數詞", "嘆": "感嘆詞", "不變": "不變詞",
}

DECKS: dict[str, dict] = {
    "hbo": {
        "title": "聖經希伯來文單字卡",
        "vocab": ROOT / "data/originalReaders/vocabulary/hebrew-1000.json",
        "glosses": CACHE / "original-readers/hebrew-full/hebrew-gloss-zh-reviewed-by-lemma.json",
        "images": CACHE / "flashcards/hebrew-card-images.json",
        "output": "hebrew-flashcards-1000.docx",
        "font": "Noto Serif Hebrew",
        "rtl": True,
        "headword_pt": 54,
        "sources": [
            "詞表：Pratico–Van Pelt《Basics of Biblical Hebrew》2/e 詞序，其後接語料頻率延伸。",
            "原文與出現次數：Westminster Leningrad Codex（OSHB）。",
            "人名、地名與民族國名不在本套卡內，另收於讀本的分類專名表。",
        ],
    },
    "grc1": {
        "title": "通用希臘文單字卡・上冊",
        "vocab": ROOT / "data/originalReaders/vocabulary/greek-2000.json",
        "glosses": CACHE / "original-readers/greek-full/greek-2000-gloss-zh-by-lemma.json",
        "images": CACHE / "flashcards/greek-card-images.json",
        "output": "greek-flashcards-volume-1.docx",
        "font": "Palatino Linotype",
        "rtl": False,
        "headword_pt": 34,
        "volume": 1,
        "sources": [
            "詞表：Mounce《Basics of Biblical Greek》詞序，其後接新約與七十士譯本語料頻率延伸。",
            "正面為字典引用形，附詞尾與冠詞。",
        ],
    },
    "grc2": {
        "title": "通用希臘文單字卡・下冊",
        "vocab": ROOT / "data/originalReaders/vocabulary/greek-2000.json",
        "glosses": CACHE / "original-readers/greek-full/greek-2000-gloss-zh-by-lemma.json",
        "images": CACHE / "flashcards/greek-card-images.json",
        "output": "greek-flashcards-volume-2.docx",
        "font": "Palatino Linotype",
        "rtl": False,
        "headword_pt": 34,
        "volume": 2,
        "sources": [
            "詞表：教父希臘文語料頻率延伸，與上冊不重複。",
            "正面為字典引用形，附詞尾與冠詞。",
        ],
    },
    "lat1": {
        "title": "教會拉丁文單字卡・上冊",
        "vocab": ROOT / "data/originalReaders/vocabulary/latin-2000.json",
        "images": CACHE / "flashcards/latin-card-images.json",
        "output": "latin-flashcards-volume-1.docx",
        "font": "Noto Serif",
        "rtl": False,
        "headword_pt": 30,
        "volumeName": "上冊",
        "sources": [
            "詞表：Collins《A Primer of Ecclesiastical Latin》原書詞序。",
            "正面為字典引用形，動詞列四個主要部分，名詞列主格、屬格與性。",
            "長音符號依原書標示；發音為羅馬式教會發音。",
        ],
    },
    "lat2": {
        "title": "教會拉丁文單字卡・下冊",
        "vocab": ROOT / "data/originalReaders/vocabulary/latin-2000.json",
        "images": CACHE / "flashcards/latin-card-images.json",
        "output": "latin-flashcards-volume-2.docx",
        "font": "Noto Serif",
        "rtl": False,
        "headword_pt": 30,
        "volumeName": "下冊",
        "sources": [
            "詞表：教父、中世紀與近現代教廷語料詞頻，與上冊不重複。",
            "詞形主要部分取自 Whitaker's WORDS。",
            "正面為字典引用形；發音為羅馬式教會發音。",
        ],
    },
}


def set_rfonts(run, font: str) -> None:
    """Pin every Word script slot so the headword never falls back to a UI font."""

    r_pr = run._element.get_or_add_rPr()
    fonts = r_pr.rFonts
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        r_pr.insert(0, fonts)
    for slot in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn(f"w:{slot}"), font)
    for theme in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        fonts.attrib.pop(qn(f"w:{theme}"), None)


def write(paragraph, text: str, font: str, size: float, *, color: str = INK,
          bold: bool = False, rtl: bool = False):
    run = paragraph.add_run(text)
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)
    set_rfonts(run, font)
    if rtl:
        r_pr = run._element.get_or_add_rPr()
        mark = OxmlElement("w:rtl")
        mark.set(qn("w:val"), "1")
        r_pr.append(mark)
        p_pr = paragraph._p.get_or_add_pPr()
        bidi = OxmlElement("w:bidi")
        bidi.set(qn("w:val"), "1")
        p_pr.append(bidi)
    return run


def blank(cell, points: float) -> None:
    paragraph = cell.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(0)
    write(paragraph, "", FONT_UI, points)


def strip_borders(table) -> None:
    """Print no rules at all; the cut is measured, not traced."""

    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "none")
        element.set(qn("w:sz"), "0")
        element.set(qn("w:space"), "0")
        borders.append(element)
    table._tbl.tblPr.append(borders)


def new_grid(document: Document):
    table = document.add_table(rows=ROWS, cols=COLS)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    strip_borders(table)
    for row in table.rows:
        # One height declaration only.  Setting row.height and then appending a
        # second w:trHeight leaves two competing rules in the XML.
        row.height = Mm(CARD_H_MM)
        row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
        for cell in row.cells:
            cell.width = Mm(CARD_W_MM)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            margins = OxmlElement("w:tcMar")
            for edge, value in (("top", 170), ("start", 140), ("bottom", 170), ("end", 140)):
                node = OxmlElement(f"w:{edge}")
                node.set(qn("w:w"), str(value))
                node.set(qn("w:type"), "dxa")
                margins.append(node)
            cell._tc.get_or_add_tcPr().append(margins)
    return table


def clear(cell) -> None:
    first = cell.paragraphs[0]._p
    first.getparent().remove(first)


def zh_size(gloss: str) -> float:
    for limit, size in ZH_STEPS:
        if len(gloss) <= limit:
            return size
    return ZH_STEPS[-1][1]


def headword_size(deck: dict, text: str) -> float:
    """Greek citation forms are long (ἄγγελος, -ου, ὁ); shrink so they fit."""

    base = deck["headword_pt"]
    # Latin citation forms are longer than any other deck's -- four principal
    # parts run past forty characters -- so they get their own ladder and are
    # allowed to wrap rather than being shrunk to illegibility.
    if deck.get("volumeName"):
        for limit, factor in ((12, 1.0), (20, 0.80), (28, 0.66), (38, 0.55), (99, 0.46)):
            if len(text) <= limit:
                return base * factor
    if len(text) <= 8:
        return base
    if len(text) <= 14:
        return base * 0.78
    if len(text) <= 20:
        return base * 0.62
    return base * 0.52


def fill_front(cell, card: dict, deck: dict) -> None:
    clear(cell)
    paragraph = cell.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(0)
    write(paragraph, card["headword"], deck["font"],
          headword_size(deck, card["headword"]), rtl=deck["rtl"])
    blank(cell, 20)
    footer = cell.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.space_after = Pt(0)
    write(footer, f"第 {card['lesson']} 課", FONT_UI, LESSON_PT, color=MUTED)


def fill_back(cell, card: dict, picture: Path | None) -> None:
    clear(cell)
    if picture:
        paragraph = cell.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.add_run().add_picture(str(picture), width=Mm(IMAGE_MM))
    else:
        blank(cell, 20)
    meaning = cell.add_paragraph()
    meaning.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meaning.paragraph_format.space_after = Pt(3)
    write(meaning, card["glossZh"], FONT_ZH, zh_size(card["glossZh"]))
    if card["pos"]:
        pos = cell.add_paragraph()
        pos.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pos.paragraph_format.space_after = Pt(0)
        write(pos, card["pos"], FONT_UI, POS_PT, color=MUTED)
    blank(cell, 10)
    footer = cell.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.space_after = Pt(0)
    write(footer, f"第 {card['lesson']} 課", FONT_UI, LESSON_PT, color=MUTED)


def configure(document: Document) -> None:
    section = document.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Mm(PAGE_W_MM)
    section.page_height = Mm(PAGE_H_MM)
    for attribute in ("left_margin", "right_margin", "header_distance", "footer_distance", "gutter"):
        setattr(section, attribute, Mm(0))
    section.top_margin = Mm(MARGIN_V_MM)
    section.bottom_margin = Mm(MARGIN_V_MM)
    style = document.styles["Normal"]
    style.font.name = FONT_UI
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.line_spacing = 1.0


def page_break(document: Document) -> None:
    """A full-height paragraph here would push the bottom row onto its own page."""

    spacer = document.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    spacer.paragraph_format.line_spacing = Pt(1)
    run = spacer.add_run()
    run.font.size = Pt(1)
    run.add_break(WD_BREAK.PAGE)


def add_cover(document: Document, deck: dict, total: int, sheets: int, with_picture: int) -> None:
    """One sheet of instructions, then a blank back so the duplex pairing holds."""

    cuts_h = "、".join(f"{MARGIN_V_MM + CARD_H_MM * index:.0f}" for index in range(3))
    cuts_v = "、".join(f"{CARD_W_MM * index:.2f}".rstrip("0").rstrip(".") for index in range(1, 4))
    lines = [
        (deck["title"], 30, INK, 14),
        (f"{total} 張・{sheets} 組雙面・每頁 8 張", 13, MUTED, 22),
        ("列印：A4 橫式，雙面列印選「沿長邊翻頁」，縮放設為 100%（不要選「符合頁面大小」）。", 11, INK, 6),
        (f"裁切：不印裁切線。自紙張上緣量，橫向切在 {cuts_h} mm；自左緣量，縱向切在 {cuts_v} mm。"
         f"成品每張 {CARD_W_MM:.2f}×{CARD_H_MM:.0f} mm。", 11, INK, 6),
        ("正面：原文與課次。背面：繁體中文詞義、詞性與課次。", 11, INK, 6),
        (f"插圖：{with_picture} 張有圖，其餘留白。多義詞取最常見的義項；找不到誠實對應的圖就不放，"
         "不以近似圖充數。", 11, INK, 22),
        ("圖片來源：OpenMoji 17.0.0（openmoji.org），CC BY-SA 4.0。", 9.5, MUTED, 4),
    ]
    lines.extend((text, 9.5, MUTED, 4) for text in deck["sources"])
    for text, size, color, after in lines:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(after)
        paragraph.paragraph_format.space_before = Pt(0)
        write(paragraph, text, FONT_UI, size, color=color, bold=size >= 30)
    page_break(document)
    note = document.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    write(note, "（此頁留白，供雙面列印對齊）", FONT_UI, 9.5, color=MUTED)


def load_cards(deck: dict) -> list[dict]:
    entries = json.loads(deck["vocab"].read_text(encoding="utf-8"))
    gloss_payload = (json.loads(deck["glosses"].read_text(encoding="utf-8"))
                     if "glosses" in deck else {})
    images = json.loads(deck["images"].read_text(encoding="utf-8"))["images"]
    cards: list[dict] = []

    if "volumeName" in deck:  # Latin
        rows = [item for item in entries["entries"] if item["volume"] == deck["volumeName"]]
        for entry in sorted(rows, key=lambda item: item["ordinal"]):
            gloss = (entry.get("glossZh") or "").strip()
            if not gloss:
                raise SystemExit(f"{entry['headword']} 缺繁中詞義")
            printed = (entry.get("forms") or entry["headword"]).strip()
            record = images.get(latin_key(entry))
            cards.append({
                "headword": printed,
                "glossZh": gloss,
                "pos": POS_LATIN.get(latin_pos(entry), ""),
                "lesson": entry["lesson"],
                "picture": IMAGE_DIR / record["file"] if record else None,
            })
        return cards

    if "volume" in deck:  # Greek
        entries = [item for item in entries["entries"] if item["volume"] == deck["volume"]]
        glosses = {lemma: record["glossZh"] for lemma, record in gloss_payload["glosses"].items()}
        for entry in sorted(entries, key=lambda item: item["ordinal"]):
            gloss = glosses.get(entry["lemma"], "").strip()
            if not gloss:
                raise SystemExit(f"{entry['lemma']} 缺繁中詞義")
            record = images.get(entry["lemma"])
            cards.append({
                "headword": entry.get("printedEntry") or entry["lemma"],
                "glossZh": gloss,
                "pos": greek_part_of_speech(entry, gloss),
                "lesson": entry["lesson"],
                "picture": IMAGE_DIR / record["file"] if record else None,
            })
        return cards

    glosses = {
        (item["strong"], item["pointed"]): item["glossZh"]
        for item in gloss_payload["items"]
    }
    for entry in sorted(entries, key=lambda item: item["ordinal"]):
        key = (entry["strong"], entry["pointed"])
        if key not in glosses:
            raise SystemExit(f"{entry['pointed']} 缺繁中詞義")
        record = images.get(f"{entry['strong']}|{entry['pointed']}")
        cards.append({
            "headword": entry["pointed"],
            "glossZh": glosses[key],
            "pos": POS_ZH.get(entry["partOfSpeech"], entry["partOfSpeech"]),
            "lesson": entry["lesson"],
            "picture": IMAGE_DIR / record["file"] if record else None,
        })
    return cards


def build(deck: dict, cards: list[dict]) -> Path:
    document = Document()
    configure(document)
    sheets = -(-len(cards) // (COLS * ROWS))
    with_picture = sum(1 for card in cards if card["picture"])
    add_cover(document, deck, len(cards), sheets, with_picture)

    for start in range(0, len(cards), COLS * ROWS):
        page = cards[start : start + COLS * ROWS]
        for side in ("front", "back"):
            page_break(document)
            table = new_grid(document)
            for index, card in enumerate(page):
                row, column = divmod(index, COLS)
                # Duplex alignment: the back sheet runs right to left.
                target = table.cell(row, column if side == "front" else COLS - 1 - column)
                if side == "front":
                    fill_front(target, card, deck)
                else:
                    fill_back(target, card, card["picture"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / deck["output"]
    document.save(path)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="產生單字卡（A4 橫式、每頁 8 張、雙面）")
    parser.add_argument("--deck", choices=sorted(DECKS), default="hbo")
    parser.add_argument("--limit", type=int, default=0, help="只做前 N 張（試印用）")
    args = parser.parse_args()

    deck = DECKS[args.deck]
    cards = load_cards(deck)
    if args.limit:
        cards = cards[: args.limit]
    path = build(deck, cards)

    sheets = -(-len(cards) // (COLS * ROWS))
    with_picture = sum(1 for card in cards if card["picture"])
    no_pos = sum(1 for card in cards if not card["pos"])
    print(f"  {deck['title']}：{len(cards)} 張，正反共 {sheets * 2} 頁"
          f"（每頁 8 張，{CARD_W_MM:.2f}×{CARD_H_MM:.0f} mm）")
    print(f"  有圖 {with_picture}，留白 {len(cards) - with_picture}；未標詞性 {no_pos}")
    print(path)


if __name__ == "__main__":
    main()
