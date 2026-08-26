# -*- coding: utf-8 -*-
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
def abs_paras(ps):
    out=[]; inabs=False
    for p in ps:
        t=para_text(p).strip()
        if ABSH.match(t): inabs=True; continue
        if not inabs: continue
        if KW.match(t) or is_h(p): inabs=False; continue
        if t: out.append(p)
    return out
for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f): continue
    z=zipfile.ZipFile("build/"+f); root=etree.fromstring(z.read("word/document.xml")); z.close()
    ps=root.find(Q("body")).findall(Q("p"))
    ap=abs_paras(ps)
    if not ap: continue
    tot=bold=0
    for p in ap:
        for r in p.findall(Q("r")):
            if not "".join(x.text or "" for x in r.iter(Q("t"))).strip(): continue
            tot+=1
            rp=r.find(Q("rPr"))
            if rp is not None and rp.find(Q("b")) is not None: bold+=1
    print("%-14s 摘要 %2d 段 %3d run，粗體 %3d（%3.0f%%）" % (f,len(ap),tot,bold,100*bold/max(tot,1)))
