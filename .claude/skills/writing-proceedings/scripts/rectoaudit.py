# -*- coding: utf-8 -*-
"""檢查奇數頁起排是否「只在必要時」補空白頁：
   每篇都要從奇數頁起；空白頁只能出現在「前一篇收在奇數頁」的情況。"""
import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open("out/第三屆臺灣藏傳佛教論壇會議論文集.pdf")


def has_body(i):
    p = doc[i]
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if p.rect.height * 0.09 < s["bbox"][1] and \
                   s["bbox"][3] < p.rect.height * 0.92 and s["text"].strip():
                    return True
    if p.get_image_info():
        return True
    return False


TITLES = ["從宗教交流到民主夥伴", "從預測編碼理論理解", "佛法緣起因果律在數理",
          "慈悲翻轉在台灣", "一位國中教師實踐", "當 AI 敲響雪域", "可信度與共鳴度",
          "覺察與演算", "藏傳佛教於印度格魯派", "噶舉派在台的發展",
          "藏傳佛教寧瑪派教育體制", "吉祥薩迦派的教育體制", "藏傳佛教南印度格魯派",
          "南印藏區三大寺田野", "教育與照護之間", "Reliable and Relatable"]
starts = []
for t in TITLES:
    for i in range(doc.page_count):
        big = [s for b in doc[i].get_text("dict")["blocks"] for l in b.get("lines", [])
               for s in l["spans"] if s["size"] > 17 and t[:8] in s["text"]]
        if big:
            starts.append((i, t))
            break

blanks = [i for i in range(doc.page_count) if not has_body(i)]
print("空白頁（實體）：", [i + 1 for i in blanks])
print()
bad = 0
for k, (i, t) in enumerate(starts):
    parity = "奇/正面" if (i + 1) % 2 else "偶/背面 ！"
    if (i + 1) % 2 == 0:
        bad += 1
    prev_blank = (i - 1) in blanks
    note = ""
    if prev_blank:
        # 前一頁是空白：只有在「再前一頁是奇數頁」時才必要
        note = "　前有空白背頁（%s）" % ("必要" if (i - 1) % 2 else "！不必要")
    print("%-24s 實體%3d %s%s" % (t[:20], i + 1, parity, note))
print()
print("落在偶數頁的篇：%d" % bad)
