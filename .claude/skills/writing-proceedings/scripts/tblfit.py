# -*- coding: utf-8 -*-
"""超出版心的表格，欄寬按比例縮到剛好一個版心寬（8050 twips），
   縮排歸零、版面設為固定，避免 Word 自動調整又跑出去。"""
import os, re, sys, zipfile
from lxml import etree
from ttbf import Q
sys.stdout.reconfigure(encoding="utf-8")
TEXTW = 10886 - 1418 * 2

# w:tblPr 的子元素順序
TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual",
               "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc",
               "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout",
               "tblCellMar", "tblLook", "tblCaption", "tblDescription",
               "tblPrChange"]
RANK = {n: i for i, n in enumerate(TBLPR_ORDER)}


def set_in_tblPr(pr, name, attrs):
    el = pr.find(Q(name))
    if el is None:
        el = etree.Element(Q(name))
        rank = RANK[name]
        at = len(pr)
        for i, x in enumerate(pr):
            t = etree.QName(x).localname
            if t not in RANK or RANK[t] > rank:
                at = i
                break
        pr.insert(at, el)
    for k, v in attrs.items():
        el.set(Q(k), str(v))


def fit(tbl):
    pr = tbl.find(Q("tblPr"))
    if pr is None:
        return 0
    grid = tbl.find(Q("tblGrid"))
    if grid is None:
        return 0
    cols = grid.findall(Q("gridCol"))
    widths = [int(c.get(Q("w")) or 0) for c in cols]
    total = sum(widths)
    ind = pr.find(Q("tblInd"))
    indw = int(ind.get(Q("w")) or 0) if ind is not None else 0
    if total + indw <= TEXTW + 20 or total <= 0:
        return 0
    f = TEXTW / total
    new = [max(200, int(round(w * f))) for w in widths]
    new[-1] += TEXTW - sum(new)          # 湊足剛好一個版心寬
    for c, w in zip(cols, new):
        c.set(Q("w"), str(w))
    # 每個儲存格自己的寬度也要跟著縮，否則 Word 以 tcW 為準
    for tc in tbl.iter(Q("tc")):
        tcPr = tc.find(Q("tcPr"))
        if tcPr is None:
            continue
        tcW = tcPr.find(Q("tcW"))
        if tcW is None or tcW.get(Q("type")) not in (None, "dxa"):
            continue
        w = int(tcW.get(Q("w")) or 0)
        if w:
            tcW.set(Q("w"), str(max(200, int(round(w * f)))))
    set_in_tblPr(pr, "tblW", {"w": TEXTW, "type": "dxa"})
    set_in_tblPr(pr, "tblInd", {"w": 0, "type": "dxa"})
    set_in_tblPr(pr, "tblLayout", {"type": "fixed"})
    return 1


for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f):
        continue
    dst = os.path.join("build", f)
    z = zipfile.ZipFile(dst)
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    n = sum(fit(t) for t in root.iter(Q("tbl")))
    if not n:
        continue
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for k, d in parts.items():
        zo.writestr(k, d)
    zo.close()
    print("  %-14s 縮了 %d 個表格" % (f, n))
print("done")
