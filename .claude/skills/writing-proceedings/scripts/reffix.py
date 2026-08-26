# -*- coding: utf-8 -*-
"""參考文獻區統一：一律套 ref 版式（行距 380、懸掛縮排 2 字、11pt），不留粗體。
   3.2 與 4.2.1 當初書目標題沒被認出來（判斷式那時還是完全相符），
   整段書目被當成內文排；1.1 的書目則整區粗體。"""
import os, re, sys, zipfile
from lxml import etree
import ttbf
from ttbf import Q, para_text, is_ref_heading, restyle_para
sys.stdout.reconfigure(encoding="utf-8")

for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f):
        continue
    dst = os.path.join("build", f)
    z = zipfile.ZipFile(dst)
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    ps = root.find(Q("body")).findall(Q("p"))
    start = next((i for i, p in enumerate(ps)
                  if is_ref_heading(para_text(p).strip())), None)
    if start is None:
        continue
    n = 0
    for p in ps[start + 1:]:
        if not para_text(p).strip():
            continue
        if any(a.tag == Q("tc") for a in p.iterancestors()):
            continue
        restyle_para(p, "ref", keep_bold=False)
        n += 1
    parts["word/document.xml"] = etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True)
    zo = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    for k, d in parts.items():
        zo.writestr(k, d)
    zo.close()
    print("  %-14s 參考文獻 %d 段套上 ref 版式" % (f, n))
print("done")
