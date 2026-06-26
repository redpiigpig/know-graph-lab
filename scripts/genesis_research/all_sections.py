# -*- coding: utf-8 -*-
import re,json
from pathlib import Path
CON=Path("public/content/works/genesis")
def split_recap(html):
    m=re.search(r'<section\s+class="chapter-recap"',html)
    return html[:m.start()] if m else html
vols=["M1","M2","M3","E1","E2","E3","O1","O2","O3","V1","V2","V3","B1","B2","B3"]
master={}
for v in vols:
    html=(CON/f"{v}.html").read_text(encoding="utf-8")
    # chapters by h2
    chaps=[(m.start(),re.sub(r'<[^>]+>','',m.group(1))) for m in re.finditer(r'<h2[^>]*>(.*?)</h2>',html,re.S)]
    bounds=[c[0] for c in chaps]+[len(html)]
    vol_secs=[]
    for i,(pos,ctitle) in enumerate(chaps):
        seg=html[pos:bounds[i+1]]
        content=split_recap(seg)
        secs=[re.sub(r'<[^>]+>','',m.group(1)).strip() for m in re.finditer(r'<h3[^>]*>(.*?)</h3>',content,re.S)]
        vol_secs.append({"ch":i+1,"title":ctitle.strip(),"sections":secs})
    master[v]=vol_secs
    nsec=sum(len(c["sections"]) for c in vol_secs)
    print(f"{v}: {len(vol_secs)} chapters, {nsec} content sections")
Path("c:/tmp/genesis_allsections.json").write_text(json.dumps(master,ensure_ascii=False,indent=1),encoding="utf-8")
print("\nTOTAL sections:",sum(sum(len(c['sections']) for c in cs) for cs in master.values()))
