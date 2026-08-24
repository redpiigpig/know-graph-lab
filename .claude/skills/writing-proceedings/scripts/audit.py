import sys, os, zipfile
from lxml import etree
import ttbf
from ttbf import Q, para_text
sys.stdout.reconfigure(encoding="utf-8")
SZ2ROLE = {}
def role_of(p):
    pPr = p.find(Q("pPr"))
    if pPr is None: return "?"
    rp = pPr.find(Q("rPr"))
    sz = rp.find(Q("sz")).get(Q("val")) if rp is not None and rp.find(Q("sz")) is not None else "?"
    ea = rp.find(Q("rFonts")).get(Q("eastAsia")) if rp is not None and rp.find(Q("rFonts")) is not None else "?"
    ind = pPr.find(Q("ind"))
    jc = pPr.find(Q("jc"))
    jcv = jc.get(Q("val")) if jc is not None else "-"
    key = (ea, sz, jcv,
           ind.get(Q("leftChars")) if ind is not None else None,
           ind.get(Q("firstLineChars")) if ind is not None else None,
           ind.get(Q("hangingChars")) if ind is not None else None)
    return {
        (ttbf.F_HEAD,"28","both",None,None,None):"h1",
        (ttbf.F_HEAD,"24","both",None,None,None):"h2",
        (ttbf.F_BODY,"22","both",None,"200",None):"body",
        (ttbf.F_BODY,"22","both","300",None,None):"quote",
        (ttbf.F_BODY,"22","both",None,None,None):"keyword",
        (ttbf.F_BODY,"22","-",None,None,"200"):"ref",
        (ttbf.F_BODY,"20","both",None,None,None):"cell/note",
        (ttbf.F_BODY,"20","center",None,None,None):"figure",
        (ttbf.F_TITLE,"40","center",None,None,None):"title",
        (ttbf.F_KAI,"32","center",None,None,None):"author",
        (ttbf.F_HEI,"18","right",None,None,None):"conf",
    }.get(key, "%s/%s/%s" % (ea, sz, jcv))
f = sys.argv[1]
only = sys.argv[2] if len(sys.argv) > 2 else None
z = zipfile.ZipFile(os.path.join("build", f))
root = etree.fromstring(z.read("word/document.xml"))
for i, p in enumerate(root.find(Q("body")).iter(Q("p"))):
    r = role_of(p); t = para_text(p).strip()
    if only and r != only: continue
    print("%4d %-10s %s" % (i, r, t[:96]))
