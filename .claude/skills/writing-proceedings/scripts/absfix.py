# -*- coding: utf-8 -*-
"""摘要正文不留粗體（摘要標題與關鍵詞那一行不動）。"""
import os,re,sys,zipfile
from lxml import etree
import ttbf
from ttbf import Q, para_text
sys.stdout.reconfigure(encoding="utf-8")
ABSH=re.compile(r"^(摘\s*要|Abstract)[：:]?$", re.I)
KW=re.compile(r"^(關鍵詞|關鍵字|Key\s*words?)", re.I)
def is_h(p):
    rPr=p.find(Q("pPr")+"/"+Q("rPr"))
    if rPr is None: return False
    rf,sz=rPr.find(Q("rFonts")),rPr.find(Q("sz"))
    return rf is not None and sz is not None and rf.get(Q("eastAsia"))==ttbf.F_HEAD and sz.get(Q("val")) in ("28","24")
for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f): continue
    dst="build/"+f
    z=zipfile.ZipFile(dst); parts={k:z.read(k) for k in z.namelist()}; z.close()
    root=etree.fromstring(parts["word/document.xml"])
    ps=root.find(Q("body")).findall(Q("p"))
    n=0; inabs=False
    for p in ps:
        t=para_text(p).strip()
        if ABSH.match(t): inabs=True; continue
        if not inabs: continue
        if KW.match(t) or is_h(p): inabs=False; continue
        for r in p.iter(Q("r")):                 # 走所有後代，run 可能被包了一層
            rp=r.find(Q("rPr"))
            if rp is None: continue
            for tag in ("b","bCs"):
                el=rp.find(Q(tag))
                if el is not None: rp.remove(el); n+=1
    if not n: continue
    parts["word/document.xml"]=etree.tostring(root,xml_declaration=True,encoding="UTF-8",standalone=True)
    zo=zipfile.ZipFile(dst,"w",zipfile.ZIP_DEFLATED)
    for k,d in parts.items(): zo.writestr(k,d)
    zo.close()
    print("  %-14s 摘要清掉 %d 個粗體標記" % (f,n))
print("done")
