"""把校務系統匯出的「課堂管理名冊」.xls 轉成點名表 .docx。

模板＝教學/115-1_世界宗教文化導論/二年制世界宗教文化導論-點名表.docx
（該檔本身是校務系統匯出後人工整理的成果，此腳本把整理步驟自動化）

用法：
    python scripts/build_roster_docx.py <匯出的.xls> [...] --outdir <資料夾>

點名欄數由 xls 的「上課時間」推得：標(單)/(雙)＝隔週上課→9 次，否則→18 次。
"""
from __future__ import annotations

import argparse
import copy
import re
import shutil
import zipfile
from pathlib import Path

import xlrd
from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def w(tag: str) -> str:
    return f"{{{W}}}{tag}"


TEMPLATE = Path(
    r"G:\我的雲端硬碟\資料\知識圖工作室\教學\115-1_世界宗教文化導論"
    r"\二年制世界宗教文化導論-點名表.docx"
)
TOTAL_W = 13942  # 模板表格總寬（dxa）


def read_roster(xls_path: Path) -> dict:
    """讀課堂管理名冊 xls，回傳課名與學生清單。"""
    book = xlrd.open_workbook(str(xls_path), encoding_override="cp950")
    sheet = book.sheet_by_index(0)
    rows = [[str(c.value).strip() for c in sheet.row(r)] for r in range(sheet.nrows)]

    meta = {}
    for row in rows[:3]:
        for cell in row:
            if ":" in cell:
                k, _, v = cell.partition(":")
                meta[k.strip()] = v.strip()

    header = next(i for i, row in enumerate(rows) if row[0] == "序號")
    students = []
    for row in rows[header + 1 :]:
        if not row[0]:
            continue
        students.append({"seq": row[0], "id": row[1], "name": row[2], "class": row[3]})

    periods = meta.get("上課時間", "")
    sessions = 9 if ("(單)" in periods or "(雙)" in periods) else 18

    return {
        "title": meta.get("科目名稱", xls_path.stem),
        "code": meta.get("科目代號", ""),
        "unit": meta.get("開課單位", ""),
        "periods": periods,
        "sessions": sessions,
        "students": students,
    }


def grid_widths(sessions: int) -> list[int]:
    """欄寬：9 欄時完全照模板；欄數變多就壓縮固定欄讓點名格還寫得下。"""
    if sessions == 9:
        return [727, 1510, 1684, 2073] + [362] * 9 + [1471, 1073, 1073, 1073]
    head = [560, 1200, 1400, 1500]
    tail = [1000, 900, 900, 900]
    each = (TOTAL_W - sum(head) - sum(tail)) // sessions
    head[3] += TOTAL_W - sum(head) - sum(tail) - each * sessions  # 餘數補給「級別」
    return head + [each] * sessions + tail


def set_text(tc, text: str) -> None:
    """把儲存格裡第一個 w:t 換成 text（模板保證每個有字的格都有一個 run）。"""
    node = tc.find(f".//{w('t')}")
    node.text = text
    node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def cells(tr) -> list:
    return tr.findall(w("tc"))


def set_span(tc, span: int, width: int) -> None:
    tc_pr = tc.find(w("tcPr"))
    tc_pr.find(w("tcW")).set(w("w"), str(width))
    grid_span = tc_pr.find(w("gridSpan"))
    grid_span.set(w("val"), str(span))


def repeat_header(tr) -> None:
    """跨頁時重複表頭；tblHeader 依 schema 必須排在 trHeight 之後。"""
    tr_pr = tr.find(w("trPr"))
    el = etree.SubElement(tr_pr, w("tblHeader"))
    tr_pr.remove(el)
    height = tr_pr.find(w("trHeight"))
    tr_pr.insert(list(tr_pr).index(height) + 1 if height is not None else 0, el)


def build(roster: dict, out_path: Path) -> None:
    shutil.copy(TEMPLATE, out_path)
    with zipfile.ZipFile(out_path) as zf:
        parts = {n: zf.read(n) for n in zf.namelist()}

    doc = etree.fromstring(parts["word/document.xml"])
    tbl = doc.find(f".//{w('tbl')}")
    rows = tbl.findall(w("tr"))
    title_row, group_row, head_row = rows[0], rows[1], rows[2]
    data_tpl = copy.deepcopy(rows[3])
    note_row = rows[-1]

    n = roster["sessions"]
    widths = grid_widths(n)

    # 表格骨架：欄寬
    grid = tbl.find(w("tblGrid"))
    for col in grid.findall(w("gridCol")):
        grid.remove(col)
    for width in widths:
        etree.SubElement(grid, w("gridCol")).set(w("w"), str(width))

    # 浮動定位拿掉，改一般流排；表頭跨頁重複（49 人的班會超過一頁）
    tbl_pr = tbl.find(w("tblPr"))
    for pos in tbl_pr.findall(w("tblpPr")):
        tbl_pr.remove(pos)

    # 標題列、群組列、註記列的跨欄數
    set_span(cells(title_row)[0], n + 8, TOTAL_W)
    set_text(cells(title_row)[0], roster["title"])
    gc = cells(group_row)
    set_span(gc[1], n + 2, sum(widths[3 : 4 + n + 1]))
    set_span(gc[2], 3, sum(widths[-3:]))
    set_span(cells(note_row)[0], n + 8, TOTAL_W)

    # 點名欄編號 1..n
    hc = cells(head_row)
    session_tpl = copy.deepcopy(hc[4])
    for tc in hc[4 : 4 + 9]:
        head_row.remove(tc)
    anchor = cells(head_row)[3]
    for i in range(n):
        tc = copy.deepcopy(session_tpl)
        set_text(tc, str(i + 1))
        anchor.addnext(tc)
        anchor = tc

    # 學生列
    blank_tpl = copy.deepcopy(cells(data_tpl)[4])
    dc = cells(data_tpl)
    for tc in dc[4 : 4 + 9]:
        data_tpl.remove(tc)
    anchor = cells(data_tpl)[3]
    for _ in range(n):
        tc = copy.deepcopy(blank_tpl)
        anchor.addnext(tc)
        anchor = tc

    for tr in rows[3:-1]:
        tbl.remove(tr)
    anchor = head_row
    for stu in roster["students"]:
        tr = copy.deepcopy(data_tpl)
        tc = cells(tr)
        for target, value in zip(tc[:4], (stu["seq"], stu["id"], stu["name"], stu["class"])):
            set_text(target, value)
        anchor.addnext(tr)
        anchor = tr

    for tr in (title_row, group_row, head_row):
        repeat_header(tr)

    parts["word/document.xml"] = etree.tostring(
        doc, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in parts.items():
            zf.writestr(name, data)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("xls", nargs="+", type=Path)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--name", help="輸出檔名（單一檔案時用），預設為「科目名稱-點名表.docx」")
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    for path in args.xls:
        roster = read_roster(path)
        stem = args.name if args.name and len(args.xls) == 1 else f"{roster['title']}-點名表"
        out = args.outdir / f"{stem}.docx"
        build(roster, out)
        print(
            f"{out}  ←  {path.name}  "
            f"[{roster['code']} {roster['unit']} {roster['periods']}] "
            f"{len(roster['students'])} 人 / {roster['sessions']} 次"
        )


if __name__ == "__main__":
    main()
