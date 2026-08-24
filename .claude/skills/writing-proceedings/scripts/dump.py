import sys, zipfile, re
from lxml import etree
sys.stdout.reconfigure(encoding='utf-8')
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def para_text(p):
    out = []
    for el in p.iter():
        t = el.tag
        if t == W+"t": out.append(el.text or "")
        elif t == W+"tab": out.append("\t")
        elif t == W+"br": out.append("\n")
    return "".join(out)

def walk(node, depth=0):
    for ch in node:
        tag = ch.tag
        if tag == W+"p":
            txt = para_text(ch).strip()
            if txt: print(("  "*depth) + txt)
        elif tag == W+"tbl":
            print(("  "*depth) + "<<TABLE>>")
            for tr in ch.findall(W+"tr"):
                cells = []
                for tc in tr.findall(W+"tc"):
                    cells.append(" / ".join(x for x in (para_text(p).strip() for p in tc.iter(W+"p")) if x))
                print(("  "*depth) + " || ".join(cells))
            print(("  "*depth) + "<<END TABLE>>")
        elif tag in (W+"sdt", W+"sdtContent"):
            walk(ch, depth)

path = sys.argv[1]
z = zipfile.ZipFile(path)
root = etree.fromstring(z.read("word/document.xml"))
walk(root.find(W+"body"))
