import zipfile, sys, os, glob, re
from lxml import etree
sys.stdout.reconfigure(encoding='utf-8')
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
def ptext(p):
    o=[]
    for el in p.iter():
        if el.tag==W+"t": o.append(el.text or "")
        elif el.tag==W+"tab": o.append(" ")
        elif el.tag==W+"br": o.append(" ")
    return "".join(o).strip()
def paras(path):
    z=zipfile.ZipFile(path)
    root=etree.fromstring(z.read("word/document.xml"))
    out=[]
    for p in root.iter(W+"p"):
        t=ptext(p)
        if t: out.append(t)
    imgs=len([n for n in z.namelist() if n.startswith("word/media/")])
    fn=""
    if "word/footnotes.xml" in z.namelist():
        fr=etree.fromstring(z.read("word/footnotes.xml"))
        fns=[ptext(p) for p in fr.iter(W+"p")]
        fn=" | ".join(x for x in fns if x)[:300]
    return out, imgs, fn
for f in sorted(glob.glob("src/*.docx")):
    if "議程" in f: continue
    try:
        ps, imgs, fn = paras(f)
    except Exception as e:
        print(f"\n########## {os.path.basename(f)} -> ERROR {e}"); continue
    txt="\n".join(ps)
    print(f"\n########## {os.path.basename(f)}")
    print(f"  段落數={len(ps)}  字數≈{len(txt)}  圖片={imgs}")
    for kw in ["摘要","摘 要","Abstract","關鍵詞","關鍵字","Keywords","參考文獻","參考書目","引言","前言","結論","註釋"]:
        if kw in txt: print(f"  ✓有「{kw}」", end="")
    print()
    print("  --- 前 14 段 ---")
    for t in ps[:14]: print("   |", t[:110])
    print("  --- 末 5 段 ---")
    for t in ps[-5:]: print("   |", t[:110])
    if fn: print("  --- 註腳 ---\n   |", fn[:250])
