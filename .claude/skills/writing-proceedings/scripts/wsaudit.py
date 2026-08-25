# -*- coding: utf-8 -*-
"""全書空白與換行體檢（唯讀）：段首空白、中文間空格、硬換行、連續空格、
   句子被切成兩段、段尾空白、tab、全形空格。"""
import os, re, sys, zipfile, collections
from lxml import etree
from ttbf import Q, para_text
sys.stdout.reconfigure(encoding="utf-8")

CJK = r"[㐀-鿿぀-ヿ]"
MID_SPACE = re.compile(CJK + r" +" + CJK)          # 中文字之間的空格
MULTI = re.compile(r"\S {3,}\S")                    # 連續三個以上空格
FULLW = re.compile(r"　")
TAB = re.compile(r"\t")
# 上一段結尾沒有標點、下一段開頭不是標題／編號 → 可能是被硬切成兩段的句子
ENDPUNC = re.compile(r"[。！？：；」』）\)\.!?;:，、,…—－\-]$")
STARTNEW = re.compile(r"^([第壹貳參肆伍陸柒捌玖拾一二三四五六七八九十（(\d]|[A-Z])")

rows = []
for f in sorted(os.listdir("build")):
    if not re.match(r"^(0[1-9]|1[0-6])_", f):
        continue
    z = zipfile.ZipFile(os.path.join("build", f))
    root = etree.fromstring(z.read("word/document.xml"))
    z.close()
    body = root.find(Q("body"))
    ps = body.findall(Q("p"))
    texts = [para_text(p) for p in ps]
    st = collections.Counter()
    samples = collections.defaultdict(list)

    for p, t in zip(ps, texts):
        if t and not t.strip() == "" and t[:1] in (" ", "　", "\t"):
            st["段首空白"] += 1
            samples["段首空白"].append(t[:34])
        for m in MID_SPACE.finditer(t):
            st["中文間空格"] += 1
            samples["中文間空格"].append(t[max(0, m.start()-8):m.end()+8])
        if MULTI.search(t):
            st["連續空格"] += 1
            samples["連續空格"].append(t[:40])
        if FULLW.search(t.strip()):
            st["全形空格"] += 1
            samples["全形空格"].append(t.strip()[:34])
        if TAB.search(t):
            st["tab"] += 1
            samples["tab"].append(t.strip()[:34])
        if t.rstrip() != t and t.strip():
            st["段尾空白"] += 1
        if len(p.findall(Q("br"))) or len(p.findall(".//" + Q("br"))):
            st["硬換行 w:br"] += 1
            samples["硬換行 w:br"].append(t[:40])

    prev = ""
    for t in texts:
        cur = t.strip()
        if prev and cur and len(prev) > 12 and not ENDPUNC.search(prev) \
           and not STARTNEW.match(cur) and len(cur) > 6:
            st["疑似被切斷的句子"] += 1
            samples["疑似被切斷的句子"].append(prev[-16:] + " ⏎ " + cur[:16])
        if cur:
            prev = cur

    if st:
        rows.append((f, st, samples))

for f, st, samples in rows:
    print("=== %s ===" % f)
    for k, v in st.items():
        print("   %-12s %d" % (k, v))
        for s in samples[k][:2]:
            print("        %r" % s)
