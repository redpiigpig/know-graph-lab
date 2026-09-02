# -*- coding: utf-8 -*-
"""國史館檔案（加密 docx）→ 轉出可讀文字。

來源是使用者取得的兩份國史館案卷，標「勿外傳」、供研究使用：
  國防部「捕鼠案」          0054/0400/9502-2/0008（政治），民國 36-54 年
  行政院「敵偽組織及活動案」 014-060300-0073，民國 33-36 年
兩份都已由原機關註銷機密等級（106 年／104 年）。

🚨 **只放站內（已登入才看得到）與 Drive，不對外公開。** 站上 research-data 的
   API 已加 requireAdmin（2026-09-02 補；在那之前九支端點未登入就能取全文）。

排版有兩個坑，兩個都會讓內容看起來「有抓到」但其實讀不通：

🚨 一、**儲存格順序是反的**。傳統直排表格由右至左讀，而 python-docx 的
   `row.cells` 是由左至右。證據：目次那列出來是「31｜30｜29｜28｜27｜次目」
   ——數字遞減，而且「次目」正是「目次」反過來。所以每一列都要 reversed()。

🚨 二、**單一儲存格內是直排**，文字以換行逐字排列（`中\\n華\\n民\\n國`）。
   要把格內的空白與換行全部去掉才併得回「中華民國」。

還有一類修不掉的：`位單轉移`／`位單案原` 這種**格內橫排但由右至左**的欄位名
（應為「移轉單位」「原案單位」）。那需要語意判斷才知道該不該倒轉，硬套規則會
把正常的詞也弄反，所以**原樣保留**，讀的人看得出來。

  python -X utf8 scripts/archives_guoshiguan.py --extract
"""
import argparse
import io
import re
import sys
from pathlib import Path

import msoffcrypto
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

SRC = Path("G:/我的雲端硬碟/資料/知識圖工作室/研究資料/國家檔案調閱/國史館")
OUT_TXT = SRC / "_轉出文字"
OUT_JSON = Path(__file__).resolve().parents[1] / "public/content/research-data/yiguandao"


def blocks(doc):
    """按文件順序走段落與表格。

    只抓 doc.paragraphs 會漏掉表格——這兩份的內容九成在表格裡
    （捕鼠案 296 列、敵偽 488 列）。
    """
    for child in doc.element.body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            yield "p", Paragraph(child, doc)
        elif tag == "tbl":
            yield "t", Table(child, doc)


def cell_text(c):
    """格內直排 → 併回一串。空白與換行全清掉。"""
    return "".join(c.text.split())


def extract(path, password):
    buf = io.BytesIO()
    with path.open("rb") as fh:
        off = msoffcrypto.OfficeFile(fh)
        off.load_key(password=password)
        off.decrypt(buf)
    buf.seek(0)
    doc = Document(buf)
    lines, nrows = [], 0
    for kind, el in blocks(doc):
        if kind == "p":
            t = " ".join(el.text.split())
            if t:
                lines.append(t)
            continue
        for row in el.rows:
            cells = [cell_text(c) for c in reversed(row.cells)]   # 坑一：由右至左
            ded = [c for i, c in enumerate(cells) if c and (i == 0 or c != cells[i - 1])]
            if ded:
                lines.append(" ｜ ".join(ded))
                nrows += 1
    return lines, nrows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract", action="store_true")
    ap.add_argument("--password", default=None,
                    help="不給就從環境變數 GSG_DOCX_PW 讀；一律不寫進檔案或版控")
    a = ap.parse_args()
    if not a.extract:
        ap.print_help()
        return
    import os
    pw = a.password or os.environ.get("GSG_DOCX_PW")
    if not pw:
        print("需要密碼：--password 或環境變數 GSG_DOCX_PW", file=sys.stderr)
        sys.exit(2)
    OUT_TXT.mkdir(parents=True, exist_ok=True)
    for f in sorted(SRC.glob("*.docx")):
        lines, nrows = extract(f, pw)
        name = re.sub(r"[\[\]]", "", f.stem).strip()
        txt = "\n".join(lines)
        (OUT_TXT / f"{name}.txt").write_text(txt, encoding="utf-8")
        single = sum(1 for l in lines if len(l) == 1)
        print(f"● {name}：{len(lines)} 行（表格 {nrows}）／{len(txt):,} 字"
              f"｜單字元行 {single}（{single / max(1, len(lines)) * 100:.0f}%）")


if __name__ == "__main__":
    main()
