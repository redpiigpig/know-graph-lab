import zipfile, sys
from lxml import etree
sys.stdout.reconfigure(encoding='utf-8')
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
def g(el,*names):
    for n in names:
        el = el.find(W+n) if el is not None else None
    return el
def val(el,attr="val"):
    return el.get(W+attr) if el is not None else None
def fmt_run(r):
    rPr = r.find(W+"rPr")
    if rPr is None: return ""
    f = rPr.find(W+"rFonts")
    parts=[]
    if f is not None:
        parts.append("A=%s/E=%s/C=%s"%(f.get(W+"ascii"),f.get(W+"eastAsia"),f.get(W+"cs")))
    for tag,label in [("sz","sz"),("szCs","szCs"),("b","B"),("i","I"),("color","col")]:
        e=rPr.find(W+tag)
        if e is not None:
            v=e.get(W+"val")
            parts.append(f"{label}={v if v is not None else 'on'}")
    return " ".join(parts)
def fmt_par(p):
    pPr=p.find(W+"pPr")
    if pPr is None: return ""
    parts=[]
    st=val(pPr.find(W+"pStyle"))
    if st: parts.append("style="+st)
    jc=val(pPr.find(W+"jc"))
    if jc: parts.append("jc="+jc)
    sp=pPr.find(W+"spacing")
    if sp is not None:
        parts.append("spacing["+",".join(f"{k.split('}')[1]}={v}" for k,v in sp.attrib.items())+"]")
    ind=pPr.find(W+"ind")
    if ind is not None:
        parts.append("ind["+",".join(f"{k.split('}')[1]}={v}" for k,v in ind.attrib.items())+"]")
    rPr=pPr.find(W+"rPr")
    if rPr is not None:
        f=rPr.find(W+"rFonts"); sz=rPr.find(W+"sz")
        parts.append("pmark["+ (f"A={f.get(W+'ascii')}/E={f.get(W+'eastAsia')} " if f is not None else "") + (f"sz={sz.get(W+'val')}" if sz is not None else "")+"]")
    return " ".join(parts)
def ptext(p):
    o=[]
    for el in p.iter():
        if el.tag==W+"t": o.append(el.text or "")
        elif el.tag==W+"tab": o.append("\t")
        elif el.tag==W+"br": o.append("\n")
        elif el.tag==W+"footnoteReference": o.append("[FN#%s]"%el.get(W+"id"))
    return "".join(o)

path=sys.argv[1]; part=sys.argv[2] if len(sys.argv)>2 else "word/document.xml"
z=zipfile.ZipFile(path)
root=etree.fromstring(z.read(part))
body=root.find(W+"body") if root.find(W+"body") is not None else root
n=0
for p in body.iter(W+"p"):
    n+=1
    t=ptext(p)
    print(f"[{n}] {fmt_par(p)}")
    print(f"    TEXT: {t[:200]!r}")
    for r in p.findall(W+"r")[:3]:
        rt="".join(x.text or "" for x in r.iter(W+"t"))
        print(f"      RUN {fmt_run(r)} :: {rt[:60]!r}")
    if n>200: break
