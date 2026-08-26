import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc=fitz.open("out/第三屆臺灣藏傳佛教論壇會議論文集.pdf")
L,R=70.9,544.3-70.9
bad={}
for i in range(doc.page_count):
    p=doc[i]
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            for s in l["spans"]:
                if not s["text"].strip(): continue
                if s["bbox"][2] > R+2 or s["bbox"][0] < L-2:
                    bad.setdefault(i+1,[]).append((round(s["bbox"][2]-R,1), s["text"][:24]))
for pg,items in sorted(bad.items()):
    worst=max(items, key=lambda x:x[0])
    print("實體%3d（印刷%3d）超出右界 %.1f pt＝%.2f cm  例：%r" % (pg,pg-10,worst[0],worst[0]/28.35,worst[1]))
print("共 %d 頁有溢出" % len(bad))
