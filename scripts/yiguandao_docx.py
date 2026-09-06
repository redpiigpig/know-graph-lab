# -*- coding: utf-8 -*-
"""把一貫道研究助理這一批材料與成果出成 Drive 上的 Word 檔。

    python -X utf8 scripts/yiguandao_docx.py

去處：G:\\我的雲端硬碟\\玄奘\\博一上\\研究助理\\
    01_研究報告／02_年表／03_檔案清單／04_引用書目／05_檔案全文／00_進度

排版沿用 build_proposal_docx.build()（A4、12pt 新細明體、行距 1.5、首行縮排兩字、
`<!-- 封面結束 -->` 之前算封面），所以除了兩份逐字全文之外，一律先組成 markdown
再轉檔——不要各寫各的排版。

🚨 **兩份檔案全文（捕鼠案、敵偽組織及活動案）標「勿外傳」。** 出成 Word 是為了在
   Drive 上讀與檢索，檔名保留「勿外傳」字樣；不進 git、不上 R2 以外的任何地方。

🚨 逐字全文那兩份的來源 txt 每一行是一個表格列，欄位用「｜」分隔，而且**同一段
   正文會在同一列裡重複好幾次**（原檔的合併儲存格所致）。轉 Word 時逐列去重，
   否則一段話會連印四五遍。
"""
import json
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_proposal_docx import build as md_to_docx  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "public/content/research-data/yiguandao"
DEST = Path(r"G:/我的雲端硬碟/玄奘/博一上/研究助理")
TRANSCRIPTS = Path(r"G:/我的雲端硬碟/資料/知識圖工作室/研究資料/國家檔案調閱/國史館/_轉出文字")
TMP = ROOT / "output/yiguandao-docx"          # 中繼 markdown，不進版控

COVER = """玄奘大學宗教與文化學系博士班

{title}

{subtitle}

張辰瑋

中華民國一一五年九月

<!-- 封面結束 -->

"""


def write_docx(name: str, markdown: str) -> Path:
    TMP.mkdir(parents=True, exist_ok=True)
    md_path = TMP / f"{name}.md"
    md_path.write_text(markdown, encoding="utf-8")
    out = DEST / f"{name}.docx"
    md_to_docx(md_path, out)
    print(f"  {out.name}")
    return out


# ────────────────────────────── 02 年表 ──────────────────────────────
def timeline_md() -> str:
    data = json.loads((CONTENT / "timeline.json").read_text(encoding="utf-8"))
    phases = {p["id"]: p for p in data["phases"]}
    parts = [COVER.format(title="一貫道歷史與政教關係史年表",
                          subtitle="民國十九年至八十七年（1930–1998）")]
    parts.append("## 凡例\n")
    parts.append(data["note"] + "\n")
    parts.append(data["caution"] + "\n")
    parts.append("## 分期\n")
    for p in data["phases"]:
        parts.append(f"### {p['range']}　{p['title']}\n")
        parts.append(p["summary"] + "\n")
    parts.append("## 年表\n")
    current = None
    for e in data["events"]:
        if e["phase"] != current:
            current = e["phase"]
            ph = phases[current]
            parts.append(f"### {ph['range']}　{ph['title']}\n")
        head = f"**{e['year']}**"
        if e.get("roc"):
            head += f"（{e['roc']}）"
        parts.append(f"{head}　{e['title']}　〔{e['src']}〕\n")
        if e.get("detail"):
            parts.append(f"> {e['detail']}\n")
    return "\n".join(parts)


# ──────────────────────────── 03 檔案清單 ────────────────────────────
def inventory_md() -> str:
    d = json.loads((CONTENT / "inventory.json").read_text(encoding="utf-8"))
    parts = [COVER.format(title="一貫道國家檔案清單",
                          subtitle=f"已取得 {d['caseCount']} 案 {d['pageCount']:,} 張；"
                                   f"待下載 {len(d['pending'])} 筆 {d['pendingPages']:,} 頁")]
    parts.append("## 說明\n")
    parts.append(d["note"] + "\n")
    parts.append(f"來源：{d['source']}\n")
    parts.append(f"🚨 案卷層與件層當初各下載一次，件層影像是案卷層的同一批（已比對 md5 確認）。"
                 f"資料夾張數合計 {d['folderPageCount']:,} 張，扣除重複後**實得 {d['pageCount']:,} 張**，"
                 f"下表按實得計。\n")

    parts.append("## 一、已下載\n")
    parts.append("| 張數 | 檔號 | 全宗 | 起訖 | 案由 |")
    parts.append("| --- | --- | --- | --- | --- |")
    for c in d["cases"]:
        parts.append(f"| {c['totalPages']:,} | {c['archiveNo']} | {c['fonds']} | "
                     f"{c['dateRange'] or '—'} | {c['title'].replace('|', '／')} |")
    parts.append("")

    parts.append("## 二、逐件明細\n")
    for c in d["cases"]:
        if not c["files"]:
            continue
        parts.append(f"### {c['title']}（{c['archiveNo']}，{len(c['files'])} 件）\n")
        for f in c["files"]:
            label = f["title"].split("/", 1)[-1].replace("|", "／")
            parts.append(f"- {f['pages']:>3} 張　{label}　（{f['archiveNo']}）")
        parts.append("")

    parts.append("## 三、可線上閱覽、尚未下載\n")
    parts.append("| 頁數 | 檔號 | 全宗 | 案由 |")
    parts.append("| --- | --- | --- | --- |")
    for p in d["pending"]:
        parts.append(f"| {p['pages']:,} | {p['archiveNo']} | {p['fonds']} | {p['title'].replace('|', '／')} |")
    parts.append("")

    parts.append("## 四、檔案年度分佈\n")
    parts.append("🚨 這條曲線量的是國家的注意力，不是一貫道的活動。民國 42–48 年幾乎空白，"
                 "是那幾年的公文尚未解密或尚未編目，不是查禁停了。\n")
    parts.append("| 民國 | 件數 | | 民國 | 件數 |")
    parts.append("| --- | --- | --- | --- | --- |")
    years = d["years"]
    half = (len(years) + 1) // 2
    for left, right in zip(years[:half], years[half:] + [None] * half):
        row = f"| {left['roc']} | {left['count']} | |"
        row += f" {right['roc']} | {right['count']} |" if right else "  |  |"
        parts.append(row)
    return "\n".join(parts)


# ──────────────────────────── 04 引用書目 ────────────────────────────
def biblio_md() -> str:
    d = json.loads((CONTENT / "biblio-zhong.json").read_text(encoding="utf-8"))
    parts = [COVER.format(title="鍾雲鶯〈敵偽、附匪與邪教？〉引用書目",
                          subtitle=f"《民俗曲藝》231 期（2026 年 3 月），頁 61–107；共 {d['count']} 筆")]
    parts.append("## 說明\n")
    parts.append(d["source"] + "\n")
    parts.append(d["note"] + "\n")
    parts.append("## 徵引書目\n")
    for b in sorted(d["items"], key=lambda x: (x.get("kind", ""), x.get("author", ""))):
        bits = [b.get("author", ""), b.get("year", ""), f"〈{b['title']}〉"
                if b.get("journal") or b.get("container") else f"《{b['title']}》"]
        if b.get("editor"):
            bits.append(b["editor"])
        if b.get("container"):
            bits.append(f"收入《{b['container']}》")
        if b.get("journal"):
            bits.append(f"《{b['journal']}》{b.get('vol', '')}")
        if b.get("pub"):
            bits.append(b["pub"])
        if b.get("pages"):
            bits.append(f"頁 {b['pages']}")
        line = "，".join(x for x in bits if x) + "。"
        if b.get("verify"):
            line += "〔待核〕"
        if b.get("note"):
            line += f"　{b['note']}"
        parts.append(line + "\n")
    return "\n".join(parts)


# ──────────────────────────── 05 檔案全文 ────────────────────────────
def transcript_docx(src: Path, title: str, meta: list[str]) -> None:
    """逐字全文 → Word。不走 markdown：這批是公文的表格列，沒有標題階層可言。"""
    doc = Document()
    section = doc.sections[0]
    section.page_height, section.page_width = Cm(29.7), Cm(21.0)
    section.top_margin = section.bottom_margin = Cm(2.0)
    section.left_margin = section.right_margin = Cm(2.0)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "新細明體")

    def para(text, *, size=10.5, bold=False, align=None, space=4):
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        p.paragraph_format.space_after = Pt(space)
        if align is not None:
            p.alignment = align
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)
        run.font.name = "Times New Roman"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "新細明體")
        return p

    para(title, size=16, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space=8)
    for line in meta:
        para(line, size=10, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
    para("", space=10)

    page = re.compile(r"^0?\d{4,5}$")
    recent: list[str] = []          # 最近幾列出現過的長段，用來壓跨列重複
    for raw in src.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        # 🚨 合併儲存格的正文會重複兩次：同一列裡重複（欄位彼此相同），以及
        #    連續數列都重複（同一份公文橫跨數列，每列都帶著整段正文）。實測
        #    「據密報榆林一貫道盛行⋯」那一段連著出現五列。兩種都要壓，否則
        #    一段話印五遍，讀的人根本找不到下一份公文從哪裡開始。
        #    只壓 30 字以上的長段，短欄位（「由事」「密」「附件」）原樣留著；
        #    比對範圍限最近 12 列，隔遠了再出現就當成真的重複引用，照印。
        seen, cells = set(), []
        for cell in (c.strip() for c in line.split("｜")):
            if not cell or cell in seen:
                continue
            seen.add(cell)
            if len(cell) >= 30 and cell in recent:
                continue
            cells.append(cell)
        for cell in seen:
            if len(cell) >= 30:
                recent.append(cell)
        del recent[:-60]
        if not cells:
            continue
        text = "｜".join(cells)
        if page.fullmatch(text):                      # 頁緣戳記自成一行，便於對頁
            para(f"— {text} —", size=9, align=WD_ALIGN_PARAGRAPH.CENTER, space=6)
            continue
        para(text)

    out = DEST / "05_檔案全文" / f"{src.stem}.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    print(f"  {out.parent.name}/{out.name}")


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    print(f"→ {DEST}")

    # 每月進度：markdown 進版控（progress/YYYY-MM.md），Word 出到 Drive。
    # 一次出全部，改過舊月份也會重出。
    for md in sorted((CONTENT / "progress").glob("*.md")):
        out = DEST / f"00_{md.stem}_研究助理工作進度報告.docx"
        md_to_docx(md, out)
        print(f"00 進度　{out.name}")

    print("01 研究報告")
    md_to_docx(CONTENT / "report.md", DEST / "01_一貫道國家檔案研究報告.docx")
    print("  01_一貫道國家檔案研究報告.docx")

    print("02 年表")
    write_docx("02_一貫道歷史與政教關係史年表", timeline_md())

    print("03 檔案清單")
    write_docx("03_一貫道國家檔案清單", inventory_md())

    print("04 引用書目")
    write_docx("04_鍾雲鶯論文引用書目", biblio_md())

    print("05 檔案全文（勿外傳）")
    transcript_docx(
        TRANSCRIPTS / "勿外傳 國史館 捕鼠案.txt",
        "〔勿外傳〕國防部「捕鼠案」逐字轉錄",
        ["國家發展委員會檔案管理局　檔號 A305000000C/0054/0400/9502-2",
         "原件標 0054/0400/9502-2（政治）　民國 36 年 9 月起至 54 年 10 月止",
         "國防部政治作戰局 106 年 7 月 12 日國政保防第 1060006435 號註銷機密等級",
         "頁緣戳記 02483–02568　供研究使用，不得公開流傳",
         "※ 合併儲存格造成的重複段落已壓縮；未經壓縮的逐字原文見 Drive 上的 .txt"])
    transcript_docx(
        TRANSCRIPTS / "勿外傳 國史館 敵偽.txt",
        "〔勿外傳〕行政院「敵偽組織及活動案（五）」逐字轉錄",
        ["國史館　典藏號 014-060300-0073　民國 33 年至 36 年",
         "行政院秘書長 104 年 1 月 7 日院臺檔字第 1040120288 號註銷機密等級",
         "供研究使用，不得公開流傳",
         "※ 合併儲存格造成的重複段落已壓縮；未經壓縮的逐字原文見 Drive 上的 .txt"])


if __name__ == "__main__":
    main()
