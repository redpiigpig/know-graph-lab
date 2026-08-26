# -*- coding: utf-8 -*-
"""① 有圖的段落不能用固定行高（會把行內圖裁成一條）→ 改自動行高、置中、不縮排
   ② 摘要（含英文摘要）與正文之間換頁"""
import io, os, re, sys, zipfile
from lxml import etree
import ttbf
from ttbf import Q, para_text
sys.stdout.reconfigure(encoding="utf-8")
INNER = (Q("drawing"), Q("pict"), Q("object"))
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
             "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd",
             "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN",
             "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "jc"]


def has_img(p):
    return any(next(p.iter(t), None) is not None for t in INNER)


def ensure_flag(p, name):
    pPr = p.find(Q("pPr"))
    if pPr is None:
        pPr = etree.Element(Q("pPr"))
        p.insert(0, pPr)
    if pPr.find(Q(name)) is not None:
        return False
    rank = PPR_ORDER.index(name)
    at = len(pPr)
    for i, el in enumerate(pPr):
        tag = etree.QName(el).localname
        if tag not in PPR_ORDER or PPR_ORDER.index(tag) > rank:
            at = i
            break
    pPr.insert(at, etree.Element(Q(name)))
    return True


def fix_figure(p):
    """自動行高、置中、取消首行縮排。"""
    pPr = p.find(Q("pPr"))
    if pPr is None:
        return False
    sp = pPr.find(Q("spacing"))
    if sp is None:
        sp = etree.SubElement(pPr, Q("spacing"))
    sp.set(Q("line"), "240")
    sp.set(Q("lineRule"), "auto")
    ind = pPr.find(Q("ind"))
    if ind is not None:
        pPr.remove(ind)
    jc = pPr.find(Q("jc"))
    if jc is None:
        jc = etree.SubElement(pPr, Q("jc"))
    jc.set(Q("val"), "center")
    return True


ABS = re.compile(r"^(摘\s*要|Abstract|關鍵詞|關鍵字|Key\s*words?)", re.I)


def is_head(p, sizes=("28", "24")):
    rPr = p.find(Q("pPr") + "/" + Q("rPr"))
    if rPr is None:
        return False
    rf, sz = rPr.find(Q("rFonts")), rPr.find(Q("sz"))
    return (rf is not None and sz is not None
            and rf.get(Q("eastAsia")) == ttbf.F_HEAD
            and sz.get(Q("val")) in sizes)


def break_after_abstract(body):
    """摘要區（中英摘要與關鍵詞）之後的第一個節標題另起一頁。沒有摘要的篇不動。"""
    ps = body.findall(Q("p"))
    last_abs = -1
    for i, p in enumerate(ps):
        t = para_text(p).strip()
        if ABS.match(t) and is_head(p, ("28",)) or (ABS.match(t) and i < 12):
            last_abs = i
    if last_abs < 0:
        return None
    for p in ps[last_abs + 1:]:
        if is_head(p, ("28",)):
            t = para_text(p).strip()
            if ABS.match(t):
                continue
            return p if ensure_flag(p, "pageBreakBefore") else None
    return None


for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f):
        continue
    dst = os.path.join("build", f)
    z = zipfile.ZipFile(dst)
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(Q("body"))
    n_fig = sum(1 for p in body.findall(Q("p")) if has_img(p) and fix_figure(p))
    brk = break_after_abstract(body)
    if not (n_fig or brk is not None):
        print("  %-14s 無異動" % f)
        continue
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for k, d in parts.items():
        zo.writestr(k, d)
    zo.close()
    print("  %-14s 圖 %d 張改自動行高；摘要後換頁：%s"
          % (f, n_fig, para_text(brk).strip()[:24] if brk is not None else "－"))
print("done")
