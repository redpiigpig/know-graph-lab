# -*- coding: utf-8 -*-
"""跨篇體例比對：空行、行距、摘要、註腳、圖表標號、標點、參考文獻格式。"""
import os, re, sys, zipfile, collections
from lxml import etree
import ttbf
from ttbf import Q, para_text, is_ref_heading
sys.stdout.reconfigure(encoding="utf-8")
INNER = (Q("drawing"), Q("pict"), Q("object"))
NAMES = {"01_0": "0 格桑堅參", "02_1-1": "1.1 謝伯讓", "03_1-2": "1.2 張耀堂",
         "04_2-1": "2.1 關婉玲", "05_2-2": "2.2 盧惠娟", "06_3-1": "3.1 秋浪法師",
         "07_3-2": "3.2 昂望聽列", "08_3-3": "3.3 堪布澤仁扎西",
         "09_4-1-1": "4.1.1 陳明茹", "10_4-1-2": "4.1.2 劉國威",
         "11_4-2-1": "4.2.1 堪布其美多吉", "12_4-2-2": "4.2.2 堪布昂旺克周",
         "13_4-2-3": "4.2.3 哈欣仁波切", "14_4-3-1": "4.3.1 劉宇光",
         "15_4-3-2": "4.3.2 盧佳慧", "16_A1": "附1 英文版"}

print("%-20s %5s %6s %5s %4s %4s %6s %6s %s" %
      ("篇", "段數", "段間空行", "註腳", "摘要", "關鍵詞", "參考文獻", "圖表", "圖表標號寫法"))
for f in sorted(os.listdir("build")):
    m = re.match(r"^((0[1-9]|1[0-6])_\S+)\.docx$", f)
    if not m:
        continue
    key = f[:-5]
    z = zipfile.ZipFile(os.path.join("build", f))
    parts = {k: z.read(k) for k in z.namelist()}
    z.close()
    root = etree.fromstring(parts["word/document.xml"])
    body = root.find(Q("body"))
    ps = body.findall(Q("p"))
    texts = [para_text(p) for p in ps]
    n_para = sum(1 for t in texts if t.strip())
    n_blank = sum(1 for t in texts if not t.strip())
    fn = parts.get("word/footnotes.xml")
    n_fn = 0
    if fn is not None:
        fr = etree.fromstring(fn)
        n_fn = sum(1 for x in fr.findall(Q("footnote"))
                   if x.get(Q("id")) not in ("0", "1", "-1"))
    has_abs = any(re.match(r"^摘\s*要", t.strip()) for t in texts)
    has_en_abs = any(re.match(r"^Abstract", t.strip(), re.I) for t in texts)
    has_kw = any(re.match(r"^(關鍵詞|關鍵字|Key\s*words?)", t.strip(), re.I) for t in texts)
    has_ref = any(is_ref_heading(t.strip()) for t in texts)
    n_img = sum(1 for p in ps if any(next(p.iter(x), None) is not None for x in INNER))
    caps = collections.Counter()
    for t in texts:
        mm = re.match(r"^\s*(表|圖|Table|Figure)\s*([一二三四五六七八九十]+|\d+)\s*([、，．.:：]?)", t)
        if mm:
            caps["%s%s%s" % (mm.group(1),
                             "N" if mm.group(2).isdigit() else "漢",
                             mm.group(3) or "無")] += 1
    print("%-20s %5d %8s %5d %4s %4s %6s %6s %s" %
          (NAMES.get(key, key), n_para,
           "%d (%.0f%%)" % (n_blank, 100 * n_blank / max(n_para, 1)),
           n_fn, "有" if has_abs else ("英" if has_en_abs else "－"),
           "有" if has_kw else "－", "有" if has_ref else "－",
           n_img or "－",
           " ".join("%s×%d" % kv for kv in caps.most_common(3)) or "－"))
