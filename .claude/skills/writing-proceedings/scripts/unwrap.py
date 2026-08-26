# -*- coding: utf-8 -*-
"""把浮動錨定（文繞圖）的圖改成隨文（inline）。
   2.1 那三張圖是 wp:anchor + wrapSquare，正文會繞著圖排，
   於是「註：資料來源…」被切成左右兩半夾住圖。改 inline 就回到正常的
   「圖說在上、圖、資料來源在下」。"""
import copy, os, re, sys, zipfile
from lxml import etree
from ttbf import Q, para_text
sys.stdout.reconfigure(encoding="utf-8")
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
W = lambda t: "{%s}%s" % (WP, t)
ORDER = ["extent", "effectExtent", "docPr", "cNvGraphicFramePr"]


def to_inline(drawing):
    anc = drawing.find(W("anchor"))
    if anc is None:
        return False
    inl = etree.Element(W("inline"))
    for a in ("distT", "distB", "distL", "distR"):
        inl.set(a, anc.get(a) or "0")
    for name in ORDER:
        el = anc.find(W(name))
        if el is not None:
            inl.append(copy.deepcopy(el))
    g = anc.find("{http://schemas.openxmlformats.org/drawingml/2006/main}graphic")
    if g is None:
        return False
    inl.append(copy.deepcopy(g))
    drawing.remove(anc)
    drawing.append(inl)
    return True


for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f):
        continue
    dst = os.path.join("build", f)
    z = zipfile.ZipFile(dst)
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    n = sum(1 for d in root.iter(Q("drawing")) if to_inline(d))
    if not n:
        continue
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for k, d in parts.items():
        zo.writestr(k, d)
    zo.close()
    print("  %-14s 改成隨文的圖 %d 張" % (f, n))

# 重讀驗證：全書不該再有 anchor
left = 0
for f in sorted(os.listdir("build")):
    if not f.endswith(".docx"):
        continue
    z = zipfile.ZipFile(os.path.join("build", f))
    root = etree.fromstring(z.read("word/document.xml"))
    z.close()
    left += sum(1 for d in root.iter(Q("drawing")) if d.find(W("anchor")) is not None)
print("重讀驗證：仍是浮動錨定的圖 =", left)
