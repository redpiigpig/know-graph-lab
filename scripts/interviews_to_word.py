"""口述訪談紀錄 → Word (.docx) 匯出工具（編輯排版版本）

讀取 public/content/interviews/*.txt 並轉成 .docx。
樣式參考：~/Desktop/nonchurch-nuxt/stores/無境界者雜誌/ 的編輯排版
  - B5 紙張、頁邊 2cm
  - 棕色 【口述訪談】 tag（文鼎中行書 14pt 靠右）
  - 主標 24pt 華康中黑體 bold 置中
  - 受訪者／時間／地點 文鼎中行書 11pt 靠右深灰
  - 章節 14pt NSimSun bold；子章節 12pt bold
  - 內文 12pt Times New Roman + NSimSun eastAsia，行距 1.25，無首行縮排
  - 筆者／受訪者 棕／灰色 label，無底色塊
  - footnote [N] 上標

用法：
  python scripts/interviews_to_word.py                # 全部
  python scripts/interviews_to_word.py 釋昭慧         # 模糊比對
  python scripts/interviews_to_word.py --out D:/x     # 自訂輸出
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Mm

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "public" / "content" / "interviews"
DEFAULT_OUT = Path("c:/tmp/interviews-docx")

# ── 字型 ───────────────────────────────────────────────
FONT_TITLE = "華康中黑體"
FONT_DECO = "文鼎中行書"
FONT_CN = "NSimSun"
FONT_EN = "Times New Roman"

# ── 顏色 ───────────────────────────────────────────────
COLOR_ACCENT = RGBColor(0x83, 0x3C, 0x0B)   # 棕色
COLOR_LABEL = RGBColor(0x59, 0x59, 0x59)
COLOR_BODY = RGBColor(0x11, 0x11, 0x11)
COLOR_MUTED = RGBColor(0x59, 0x59, 0x59)

# ── 解析 ───────────────────────────────────────────────
FOOTNOTE_PATTERN = re.compile(r"\[(\d+)\]\(#footnote\d+\)")
ANSWER_PATTERN = re.compile(
    r"^([一-鿿]{1,5}(?:法師|教授|主教|和尚|居士|博士|老師|牧師|女士|先生|主任|院長|住持))：(.+)$"
)
META_PATTERN = re.compile(r"^(受訪者|訪問者|訪問時間|訪問地點|訪談時間|訪談地點|採訪者|採訪時間|採訪地點)：")
SECTION_PATTERN = re.compile(r"^[一二三四五六七八九十]+、")
SUBSECTION_PATTERN = re.compile(r"^（[一二三四五六七八九十]+）")
NUMBERED_SUB_PATTERN = re.compile(r"^\d+\.\s+\S")


def _set_run_font(run, *, size_pt: float, color: RGBColor,
                  font_en: str = FONT_EN, font_cn: str = FONT_CN,
                  bold: bool = False, italic: bool = False,
                  superscript: bool = False) -> None:
    run.font.size = Pt(size_pt)
    run.font.color.rgb = color
    run.font.name = font_en
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), font_en)
    rFonts.set(qn("w:hAnsi"), font_en)
    rFonts.set(qn("w:eastAsia"), font_cn)
    rFonts.set(qn("w:cs"), font_en)
    if bold:
        run.bold = True
    if italic:
        run.italic = True
    if superscript:
        run.font.superscript = True


def add_body_runs(paragraph, text: str, *, size_pt: float, color: RGBColor,
                  bold: bool = False, italic: bool = False,
                  font_en: str = FONT_EN, font_cn: str = FONT_CN) -> None:
    cursor = 0
    for m in FOOTNOTE_PATTERN.finditer(text):
        if m.start() > cursor:
            run = paragraph.add_run(text[cursor:m.start()])
            _set_run_font(run, size_pt=size_pt, color=color,
                          bold=bold, italic=italic,
                          font_en=font_en, font_cn=font_cn)
        sup = paragraph.add_run(f"[{m.group(1)}]")
        _set_run_font(sup, size_pt=9, color=color, superscript=True,
                      font_en=font_en, font_cn=font_cn)
        cursor = m.end()
    if cursor < len(text):
        run = paragraph.add_run(text[cursor:])
        _set_run_font(run, size_pt=size_pt, color=color,
                      bold=bold, italic=italic,
                      font_en=font_en, font_cn=font_cn)


# ── 段落 ───────────────────────────────────────────────
def add_tag(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    _set_run_font(run, size_pt=14, color=COLOR_ACCENT,
                  font_en=FONT_DECO, font_cn=FONT_DECO)


def add_title(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(12)
    run = p.add_run(text)
    _set_run_font(run, size_pt=24, color=COLOR_BODY, bold=True,
                  font_en=FONT_TITLE, font_cn=FONT_TITLE)


def add_meta(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(text)
    _set_run_font(run, size_pt=11, color=COLOR_MUTED,
                  font_en=FONT_DECO, font_cn=FONT_DECO)


def add_section(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.3
    run = p.add_run(text)
    _set_run_font(run, size_pt=14, color=COLOR_BODY, bold=True,
                  font_en=FONT_CN, font_cn=FONT_CN)


def add_subsection(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.25
    run = p.add_run(text)
    _set_run_font(run, size_pt=12, color=COLOR_BODY, bold=True,
                  font_en=FONT_CN, font_cn=FONT_CN)


def add_para(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.25
    add_body_runs(p, text, size_pt=12, color=COLOR_BODY)


def add_question(doc: Document, body: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.25
    label = p.add_run("筆者　")
    _set_run_font(label, size_pt=12, color=COLOR_ACCENT, bold=True,
                  font_en=FONT_CN, font_cn=FONT_CN)
    add_body_runs(p, body, size_pt=12, color=COLOR_BODY)


def add_answer(doc: Document, label_text: str, body: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.25
    label = p.add_run(f"{label_text}　")
    _set_run_font(label, size_pt=12, color=COLOR_LABEL, bold=True,
                  font_en=FONT_CN, font_cn=FONT_CN)
    add_body_runs(p, body, size_pt=12, color=COLOR_BODY)


def add_blank(doc: Document) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0


# ── 主流程 ─────────────────────────────────────────────
def render(doc: Document, raw: str) -> None:
    lines = raw.splitlines()
    title_done = False
    add_tag(doc, "【口述訪談】")
    for line in lines:
        t = line.strip()
        if not t:
            if title_done:
                add_blank(doc)
            continue
        if not title_done:
            title_done = True
            add_title(doc, t)
            continue
        if META_PATTERN.match(t):
            add_meta(doc, t)
            continue
        if SECTION_PATTERN.match(t):
            add_section(doc, t)
            continue
        if SUBSECTION_PATTERN.match(t) or NUMBERED_SUB_PATTERN.match(t):
            add_subsection(doc, t)
            continue
        if t.startswith("筆者："):
            add_question(doc, t[len("筆者："):])
            continue
        m = ANSWER_PATTERN.match(t)
        if m:
            add_answer(doc, m.group(1), m.group(2))
            continue
        if len(t) <= 25 and not re.search(r"[。，、；：？！…]$", t) \
                and not t.startswith(("[", "【", "（", "〔")):
            add_section(doc, t)
            continue
        add_para(doc, t)


def configure_document(doc: Document) -> None:
    for section in doc.sections:
        section.page_height = Mm(257)
        section.page_width = Mm(182)
        section.top_margin = Mm(20)
        section.bottom_margin = Mm(20)
        section.left_margin = Mm(20)
        section.right_margin = Mm(20)
    style = doc.styles["Normal"]
    style.font.name = FONT_EN
    style.font.size = Pt(12)
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), FONT_EN)
    rFonts.set(qn("w:hAnsi"), FONT_EN)
    rFonts.set(qn("w:eastAsia"), FONT_CN)
    rFonts.set(qn("w:cs"), FONT_EN)


def convert_one(src: Path, out_dir: Path) -> Path:
    raw = src.read_text(encoding="utf-8")
    doc = Document()
    configure_document(doc)
    render(doc, raw)
    out_path = out_dir / f"{src.stem}.docx"
    doc.save(out_path)
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description="把 /thesis 口述訪談紀錄轉成 Word (編輯排版)")
    ap.add_argument("filter", nargs="?", default="",
                    help="檔名片段（模糊匹配），不給就轉全部")
    ap.add_argument("--out", default=str(DEFAULT_OUT),
                    help=f"輸出目錄（預設 {DEFAULT_OUT}）")
    ap.add_argument("--src", default=str(SRC_DIR),
                    help=f"來源目錄（預設 {SRC_DIR}）")
    args = ap.parse_args()

    src_dir = Path(args.src)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not src_dir.exists():
        print(f"[ERROR] 找不到來源目錄：{src_dir}", file=sys.stderr)
        return 1

    files = sorted(src_dir.glob("*.txt"))
    if args.filter:
        needle = args.filter.lower()
        files = [f for f in files if needle in f.name.lower()]
    if not files:
        print("[WARN] 沒有符合的檔案。", file=sys.stderr)
        return 1

    print(f"[INFO] 將轉換 {len(files)} 篇 → {out_dir}")
    for src in files:
        try:
            out = convert_one(src, out_dir)
            print(f"  [OK]   {src.name}  ->  {out.name}")
        except Exception as e:  # noqa: BLE001
            print(f"  [FAIL] {src.name}: {e}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
