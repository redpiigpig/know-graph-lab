# -*- coding: utf-8 -*-
"""2.1 關婉玲那篇：
   ① 英文摘要前的三行（英文題名／英文姓名／英文職稱）是作者自己的標題區，
      套上與中文題名同級的版式（題名 20pt 置中、署名 16pt 置中、職稱 10pt 置中）
   ② 英文摘要之後重複的中文題名與署名整組拿掉——篇首已經有了，職稱在與會學者名錄"""
import sys, zipfile
from lxml import etree
from ttbf import Q, para_text, restyle_para
sys.stdout.reconfigure(encoding="utf-8")

DST = "build/04_2-1.docx"
EN_TITLE = "Compassion Shift in Taiwan"
EN_AUTHOR = "Wan-Ling Kuan"
EN_AFFIL = "SEE Learning® Facilitator"
ZH_TITLE = "慈悲翻轉在台灣"
ZH_AUTHOR = "關婉玲 利仁教育基金會"

z = zipfile.ZipFile(DST)
parts = {k: z.read(k) for k in z.namelist()}
z.close()
root = etree.fromstring(parts["word/document.xml"])
body = root.find(Q("body"))
ps = body.findall(Q("p"))

done = []
for i, p in enumerate(ps):
    t = para_text(p).strip()
    if t == EN_TITLE:
        restyle_para(p, "title", keep_bold=False)
        done.append("英文題名 → 題名版式（20pt 置中）")
    elif t == EN_AUTHOR:
        restyle_para(p, "author", keep_bold=False)
        done.append("英文署名 → 署名版式（16pt 置中）")
    elif t.startswith(EN_AFFIL):
        restyle_para(p, "figure", keep_bold=False)   # 置中 10pt
        done.append("英文職稱 → 置中 10pt")
    elif i > 15 and t == ZH_TITLE:
        nxt = ps[i + 1] if i + 1 < len(ps) else None
        after = ps[i + 2] if i + 2 < len(ps) else None
        body.remove(p)
        done.append("拿掉重複的中文題名")
        if nxt is not None and para_text(nxt).strip().startswith(ZH_AUTHOR):
            body.remove(nxt)
            done.append("拿掉重複的中文署名與職稱")
        if after is not None and not para_text(after).strip():
            body.remove(after)
            done.append("拿掉隨附的空行")

parts["word/document.xml"] = etree.tostring(
    root, xml_declaration=True, encoding="UTF-8", standalone=True)
zo = zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED)
for k, d in parts.items():
    zo.writestr(k, d)
zo.close()
for d in done:
    print("  ", d)

# 重讀驗證
z = zipfile.ZipFile(DST)
root = etree.fromstring(z.read("word/document.xml"))
z.close()
print("--- 重讀後第 9–18 段 ---")
for i, p in enumerate(root.find(Q("body")).findall(Q("p"))[9:19], 9):
    rPr = p.find(Q("pPr") + "/" + Q("rPr"))
    sz = rPr.find(Q("sz")).get(Q("val")) if rPr is not None and rPr.find(Q("sz")) is not None else "?"
    jc = p.find(Q("pPr") + "/" + Q("jc"))
    print("  %2d [%spt %s] %s" % (i, int(sz) / 2, jc.get(Q("val")) if jc is not None else "-",
                                  para_text(p).strip()[:44]))
