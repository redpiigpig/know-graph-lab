# -*- coding: utf-8 -*-
"""比版心寬的圖，等比例縮到版心寬（wp:extent 與 a:ext 兩處都要改）。"""
import os, re, sys, zipfile
from lxml import etree
from ttbf import Q
sys.stdout.reconfigure(encoding="utf-8")
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
MAX = 8050 * 635          # 版心寬 8050 twips → EMU


def fit(drawing):
    inl = drawing.find("{%s}inline" % WP)
    if inl is None:
        return 0
    ext = inl.find("{%s}extent" % WP)
    if ext is None:
        return 0
    cx, cy = int(ext.get("cx")), int(ext.get("cy"))
    if cx <= MAX:
        return 0
    f = MAX / cx
    ext.set("cx", str(MAX))
    ext.set("cy", str(int(round(cy * f))))
    eff = inl.find("{%s}effectExtent" % WP)
    if eff is not None:                       # 效果邊界跟著縮，否則仍會佔到版心外
        for a in ("l", "t", "r", "b"):
            v = eff.get(a)
            if v:
                eff.set(a, str(int(round(int(v) * f))))
    for e in inl.iter("{%s}ext" % A):
        try:
            e.set("cx", str(int(round(int(e.get("cx")) * f))))
            e.set("cy", str(int(round(int(e.get("cy")) * f))))
        except (TypeError, ValueError):
            pass
    return 1


for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f):
        continue
    dst = os.path.join("build", f)
    z = zipfile.ZipFile(dst)
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    n = sum(fit(d) for d in root.iter(Q("drawing")))
    if not n:
        continue
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for k, d in parts.items():
        zo.writestr(k, d)
    zo.close()
    print("  %-14s 縮了 %d 張圖" % (f, n))

# 重讀驗證
over = []
for f in sorted(os.listdir("build")):
    if not f.endswith(".docx"):
        continue
    z = zipfile.ZipFile(os.path.join("build", f))
    root = etree.fromstring(z.read("word/document.xml"))
    z.close()
    for d in root.iter(Q("drawing")):
        inl = d.find("{%s}inline" % WP)
        if inl is None:
            continue
        ext = inl.find("{%s}extent" % WP)
        if ext is not None and int(ext.get("cx")) > MAX:
            over.append((f, int(ext.get("cx")) / 360000))
print("重讀驗證：仍超出版心的圖 =", over or 0)
