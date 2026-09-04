# -*- coding: utf-8 -*-
"""產生整個補助期間的「研究生論文指導紀錄表」——每次討論一張，事先填好固定欄位。

《玄奘大學研究生助學金實施辦法》第六條第二款：每月與指導教授討論二次以上，
次月五日前彙整送研發處。表上註 2 又寫「每次討論前請列印本表，討論後師生簽名」，
所以這是**一次一張**的表，不是一學期一張。雙週三 = 每月兩次，剛好對得上。

只填不會變的欄位（姓名學號、指導教授、院系、論文題目、日期時間、第幾次），
討論內容與簽名留白給當天填。

🚨 表格有合併儲存格：python-docx 讀合併列時同一個 tc 會在 row.cells 重複出現，
   照索引寫會把同一格寫好幾次、或把值寫到隔壁去。一律用 id(tc) 去重。
🚨 產出檔留 Drive，不進 repo（含學號等個資，repo 是公開的）。

  python -X utf8 scripts/fill_advising_log.py
"""
import copy
from datetime import date, timedelta
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

BASE = Path("G:/我的雲端硬碟/玄奘/博一/獎學金/玄奘助學金")
SRC = BASE / "04-研究生論文指導記錄表(docx) (1).docx"
OUT = BASE / "04-研究生論文指導記錄表（已填‧全學年）.docx"

FIRST = date(2026, 9, 16)     # 115 學年度第一學期開學後第一個週三
LAST = date(2027, 6, 30)      # 助學金補助期間到 2027 年 6 月
EVERY = 14                    # 雙週

NAME = "張辰瑋（DB1153002）"
ADVISOR = "釋昭慧"
COLLEGE = "社會科學院／宗教與文化學系"
TITLE = "從彼岸向此岸的轉向：台灣佛教與基督教公共性之宗教史比較研究（1920年代–2020年代）"
PLACE = "玄奘大學宗教與文化學系研究室"
TIME = "14 時 00 分至　15 時 00 分"
CJK, EN = "標楷體", "Times New Roman"


def dates():
    out, d = [], FIRST
    while d <= LAST:
        out.append(d)
        d += timedelta(days=EVERY)
    return out


def write(cell, text, *, size=12):
    cell.text = ""
    run = cell.paragraphs[0].add_run(text)
    run.font.size = Pt(size)
    run.font.name = EN
    run._element.rPr.rFonts.set(qn("w:eastAsia"), CJK)


def uniq(row):
    """合併格在 row.cells 會重複出現，回傳 (欄索引, cell) 的去重序列。"""
    seen, out = [], []
    for i, c in enumerate(row.cells):
        if id(c._tc) in seen:
            continue
        seen.append(id(c._tc))
        out.append((i, c))
    return out


def fill(table, d, n):
    roc = d.year - 1911
    stamp = f"{roc} 年 {d.month} 月 {d.day} 日（星期三）"
    pairs = {
        "研究生姓名": NAME, "指導教授姓名": ADVISOR, "院      系": COLLEGE,
        "討論日期": stamp, "討論時間": TIME, "討論地點": PLACE, "論文題目": TITLE,
    }
    for row in table.rows:
        cells = uniq(row)
        for k, (idx, cell) in enumerate(cells):
            label = cell.text.strip().replace("\n", "")
            for key, val in pairs.items():
                if label.startswith(key.replace(" ", "")) or label.startswith(key):
                    if k + 1 < len(cells):
                        write(cells[k + 1][1], val, size=11 if key == "論文題目" else 12)
            if label.startswith("院"):
                # 「□博士班」那一格在同一列的最右邊
                write(cells[-1][1], "■博士班　□碩士班")
            if label.startswith("1.本次為本學期第"):
                write(cell, f"1.本次為本學期第 {n} 次討論，是否為定期討論？■是 □否")


def main():
    tpl = Document(SRC)
    out = Document(SRC)
    body = out.element.body
    sect = body.find(qn("w:sectPr"))
    for el in list(body):
        if el is not sect:
            body.remove(el)

    ds = dates()
    # 每學期各自從第 1 次起算。
    # 🚨 第一學期是 9 月到**隔年 1 月**，不是到 12 月為止；用「年份換了就換學期」
    #    會把 1 月那兩次算成第二學期的第 1、2 次。
    per_sem = {}
    for i, d in enumerate(ds):
        sem = 1 if (d.month >= 8 or d.month == 1) else 2
        per_sem[sem] = per_sem.get(sem, 0) + 1
        first_p = None
        for el in tpl.element.body:
            if el is tpl.element.body.find(qn("w:sectPr")):
                continue
            cp = copy.deepcopy(el)
            body.insert(len(body) - (1 if sect is not None else 0), cp)
            if first_p is None and cp.tag == qn("w:p"):
                first_p = cp
        # 🚨 不要插「只有分頁符的空段落」：那個段落自己也會佔一頁，21 張會變 41 頁。
        #    改成在這一份的第一段設 pageBreakBefore。
        if i and first_p is not None:
            pPr = first_p.get_or_add_pPr()
            pPr.append(pPr.makeelement(qn("w:pageBreakBefore"), {}))
        fill(out.tables[i], d, per_sem[sem])

    out.save(OUT)
    print(f"{len(ds)} 次討論（{ds[0]} … {ds[-1]}）→ {OUT.name}")


if __name__ == "__main__":
    main()
