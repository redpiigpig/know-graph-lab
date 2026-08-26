# -*- coding: utf-8 -*-
"""合本前先逐檔試插一次：哪個檔會讓 Word 卡住，馬上就知道，
   不必等十分鐘的合本跑完才發現。"""
import os, sys, time
import win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")

app = win32.Dispatch("Word.Application")
app.Visible = False
app.DisplayAlerts = 0
ok = True
for f in sorted(os.listdir(BUILD)):
    if not f.endswith(".docx"):
        continue
    t0 = time.time()
    doc = app.Documents.Add()
    try:
        app.Selection.InsertFile(FileName=os.path.join(BUILD, f),
                                 ConfirmConversions=False, Link=False,
                                 Attachment=False)
        n = doc.Range().Sections.Count
        print("  %-18s ok  節=%d  %.1fs" % (f, n, time.time() - t0))
    except Exception as e:
        ok = False
        print("  %-18s ！%s" % (f, e))
    finally:
        doc.Close(0)
if app.Documents.Count == 0:
    app.Quit()
print("preflight", "通過" if ok else "有問題")
