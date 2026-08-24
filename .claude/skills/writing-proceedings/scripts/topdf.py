import os, sys, win32com.client as win32
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
d = os.path.join(HERE, "out", "第三屆臺灣藏傳佛教論壇會議論文集.docx")
p = d[:-5] + ".pdf"
app = win32.Dispatch("Word.Application"); app.Visible = False; app.DisplayAlerts = 0
doc = app.Documents.Open(d, False, True)
doc.ExportAsFixedFormat(OutputFileName=p, ExportFormat=17, OpenAfterExport=False,
                        OptimizeFor=0, CreateBookmarks=0, DocStructureTags=True)
doc.Close(0)
if app.Documents.Count == 0: app.Quit()
print(p, os.path.getsize(p))
