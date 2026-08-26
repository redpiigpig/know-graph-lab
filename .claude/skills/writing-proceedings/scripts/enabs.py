# -*- coding: utf-8 -*-
"""英文摘要另起一頁：有中英雙摘要的篇，英文那份要自己一頁。
   2.1 的英文摘要前面還有英文題名／署名／職稱三行，換頁要下在那三行之前；
   附1 全篇英文、Abstract 就是篇首那份，不能加（會多出空白頁）。"""
import os, re, sys, zipfile
from lxml import etree
import ttbf
from ttbf import Q, para_text
sys.stdout.reconfigure(encoding="utf-8")
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
             "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd",
             "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
             "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "jc"]


def ensure_break(p):
    pPr = p.find(Q("pPr"))
    if pPr is None:
        pPr = etree.Element(Q("pPr"))
        p.insert(0, pPr)
    if pPr.find(Q("pageBreakBefore")) is not None:
        return False
    rank = PPR_ORDER.index("pageBreakBefore")
    at = len(pPr)
    for i, el in enumerate(pPr):
        t = etree.QName(el).localname
        if t not in PPR_ORDER or PPR_ORDER.index(t) > rank:
            at = i
            break
    pPr.insert(at, etree.Element(Q("pageBreakBefore")))
    return True


def size_of(p):
    rPr = p.find(Q("pPr") + "/" + Q("rPr"))
    if rPr is None:
        return None
    sz = rPr.find(Q("sz"))
    return sz.get(Q("val")) if sz is not None else None


for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f):
        continue
    dst = os.path.join("build", f)
    z = zipfile.ZipFile(dst)
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    ps = root.find(Q("body")).findall(Q("p"))
    idx = next((i for i, p in enumerate(ps)
                if re.fullmatch(r"Abstract[：:]?", para_text(p).strip(), re.I)), None)
    if idx is None or idx < 4:          # 附1 那種全英文的篇，Abstract 就在篇首
        continue
    # 往前收英文題名區（40pt 題名／32pt 署名／20pt 職稱），換頁下在最前面那一行
    target = idx
    j = idx - 1
    while j > 0 and size_of(ps[j]) in ("40", "32", "20"):
        target = j
        j -= 1
    if not ensure_break(ps[target]):
        print("  %-14s 已經有換頁" % f)
        continue
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for k, d in parts.items():
        zo.writestr(k, d)
    zo.close()
    print("  %-14s 英文摘要另起一頁，換頁下在：%r"
          % (f, para_text(ps[target]).strip()[:36]))
print("done")
