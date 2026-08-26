# -*- coding: utf-8 -*-
"""把 w:pPr 的子元素排回 OOXML 規定的順序（rPr 一定在最後）。
   先前 fix_figure 把 w:jc 直接 append 到 pPr 尾端，排到了 rPr 之後，
   Word 開檔會跳修復對話框、整個合本卡死。"""
import os, re, sys, zipfile
from lxml import etree
from ttbf import Q
sys.stdout.reconfigure(encoding="utf-8")

ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
         "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
         "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct",
         "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
         "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
         "suppressOverlap", "jc", "textDirection", "textAlignment",
         "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr",
         "sectPr", "pPrChange"]
RANK = {name: i for i, name in enumerate(ORDER)}


def fix_pPr(pPr):
    kids = list(pPr)
    want = sorted(kids, key=lambda e: RANK.get(etree.QName(e).localname, 500))
    if kids == want:
        return False
    for e in kids:
        pPr.remove(e)
    for e in want:
        pPr.append(e)
    return True


for f in sorted(os.listdir("build")):
    if not f.endswith(".docx"):
        continue
    dst = os.path.join("build", f)
    z = zipfile.ZipFile(dst)
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    n = sum(1 for pPr in root.iter(Q("pPr")) if fix_pPr(pPr))
    if not n:
        continue
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for k, d in parts.items():
        zo.writestr(k, d)
    zo.close()
    print("  %-18s 修正 %d 個 pPr 的子元素順序" % (f, n))

# 重讀驗證：全書不該再有順序不對的 pPr
bad = 0
for f in sorted(os.listdir("build")):
    if not f.endswith(".docx"):
        continue
    z = zipfile.ZipFile(os.path.join("build", f))
    root = etree.fromstring(z.read("word/document.xml"))
    z.close()
    for pPr in root.iter(Q("pPr")):
        kids = [etree.QName(e).localname for e in pPr]
        ranks = [RANK.get(k, 500) for k in kids]
        if ranks != sorted(ranks):
            bad += 1
print("重讀驗證：順序仍有問題的 pPr =", bad)
