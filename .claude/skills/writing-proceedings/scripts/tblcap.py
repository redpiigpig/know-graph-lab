# -*- coding: utf-8 -*-
"""① 表格整塊不跨頁（原本只套在重排過的那一篇，其餘 15 篇沒保護到）
   ② 圖與它的標題不要分家：標題在上就 keepNext 標題，標題在下就 keepNext 圖"""
import os, re, sys, zipfile
from lxml import etree
import build
from build import keep_tables_whole, set_keep_next
from ttbf import Q, para_text
sys.stdout.reconfigure(encoding="utf-8")
INNER = (Q("drawing"), Q("pict"), Q("object"))
CAP = re.compile(r"^\s*(表|圖|Table|Figure)\s*([一二三四五六七八九十]+|\d+)")


def has_img(p):
    return any(next(p.iter(x), None) is not None for x in INNER)


def bind_captions(body):
    n = 0
    for p in body.findall(Q("p")):
        if not has_img(p):
            continue
        prev, nxt = p.getprevious(), p.getnext()
        if prev is not None and prev.tag == Q("p"):
            t = para_text(prev).strip()
            # 圖上方的標題：可能寫「表五，…」，也可能只是短短一行圖名，
            # 或是「…如下圖顯示：」這種引出句
            if t and (CAP.match(t) or t.endswith(("：", ":"))
                      or (len(t) <= 48 and not t.endswith("。"))):
                set_keep_next(prev)
                n += 1
        if nxt is not None and nxt.tag == Q("p"):
            t = para_text(nxt).strip()
            if CAP.match(t) or re.match(r"^註\s*[：:]", t):   # 圖下方的圖說或資料來源
                set_keep_next(p)
                n += 1
    return n


for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f):
        continue
    dst = os.path.join("build", f)
    z = zipfile.ZipFile(dst)
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(Q("body"))
    n_tbl = len(list(body.iter(Q("tbl"))))
    keep_tables_whole(body)
    n_cap = bind_captions(body)
    if not (n_tbl or n_cap):
        continue
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for k, d in parts.items():
        zo.writestr(k, d)
    zo.close()
    print("  %-14s 表格 %-2d 個設為不跨頁；圖與標題綁住 %d 處" % (f, n_tbl, n_cap))
print("done")
