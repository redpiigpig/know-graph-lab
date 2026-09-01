# -*- coding: utf-8 -*-
"""docx／pptx → PDF（走 Windows COM，需要本機已安裝 Word／PowerPoint）。

用途：講義紙本版要同時出 Word 與 PDF；簡報要出 PDF 備份與版面檢查。
成品與來源同目錄同檔名，副檔名換成 .pdf。

用法：
  python scripts/office_to_pdf.py "<檔案或資料夾>" [...]
  python scripts/office_to_pdf.py "G:\\...\\講義"        # 整個資料夾
"""
import sys
from pathlib import Path

import pythoncom
import win32com.client as win32

WD_PDF = 17
PP_PDF = 32


def convert_word(paths):
    app = win32.DispatchEx('Word.Application')
    app.Visible = False
    app.DisplayAlerts = 0
    try:
        for p in paths:
            out = p.with_suffix('.pdf')
            doc = app.Documents.Open(str(p), ReadOnly=False)
            try:
                # 目錄欄位（TOC）要更新兩趟才有正確頁碼
                for _ in range(2):
                    doc.Fields.Update()
                    for toc in doc.TablesOfContents:
                        toc.Update()
                doc.SaveAs(str(out), FileFormat=WD_PDF)
                print('✔', out)
            finally:
                doc.Close(SaveChanges=0)
    finally:
        app.Quit()


def convert_ppt(paths):
    app = win32.DispatchEx('PowerPoint.Application')
    try:
        for p in paths:
            out = p.with_suffix('.pdf')
            pres = app.Presentations.Open(str(p), WithWindow=False)
            try:
                pres.SaveAs(str(out), PP_PDF)
                print('✔', out)
            finally:
                pres.Close()
    finally:
        app.Quit()


def collect(args):
    words, ppts = [], []
    for a in args:
        p = Path(a)
        items = sorted(p.iterdir()) if p.is_dir() else [p]
        for f in items:
            if f.name.startswith('~$'):
                continue
            if f.suffix.lower() == '.docx':
                words.append(f.resolve())
            elif f.suffix.lower() == '.pptx':
                ppts.append(f.resolve())
    return words, ppts


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    words, ppts = collect(sys.argv[1:])
    if not words and not ppts:
        sys.exit('沒有找到 .docx 或 .pptx')
    pythoncom.CoInitialize()
    try:
        if words:
            convert_word(words)
        if ppts:
            convert_ppt(ppts)
    finally:
        pythoncom.CoUninitialize()
