# -*- coding: utf-8 -*-
"""碩士論文與學士論文的原參考文獻 → 結構化 JSON，供兩本改寫本比對與補文獻。

兩份來源的形狀完全不同，各走各的：
  碩論《當代的大愛道革命》底稿：PDF 的「徵引資料」一節（Drive 唯讀原檔）
  學士論文〈福音派運動在台灣基督教中的起源與發展〉：站上已有 ref.txt

🚨 PDF 抽出來的行是**排版行不是條目行**——一筆書目常被拆成三四行，
   而且每頁夾一個孤行頁碼。所以要先併行再切條目，不能一行當一筆。
   判斷條目起點用「行首是作者或書名號或年代」，不要用縮排（PDF 沒有縮排資訊）。

  python -X utf8 scripts/degree_biblio.py
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "public/content/works/degree-bibliographies.json"
MA_PDF = Path("G:/我的雲端硬碟/資料/知識圖工作室/研究資料/大愛道革命/論文資料/"
              "碩士文稿/張辰瑋碩士論文.pdf")
MA_FROM, MA_TO = 154, 177          # PDF 頁次（1 起）：徵引資料到附錄前
BA_REF = REPO / "public/content/bachelor/ref.txt"

# 「一、佛典」「（一）政府檔案」這類分類標題
SECTION = re.compile(r"^\s*([一二三四五六七八九十]+)\s*[、.]\s*(.*)$")
SUBSEC = re.compile(r"^\s*[（(]([一二三四五六七八九十]+)[）)]\s*(.*)$")
FOOTNOTE = re.compile(r"^\s*(\d{1,3})\s+\S")
# 🚨 外文書目不以「。」收尾，只靠句號切會把整個外文區黏成一筆（實測 610 字一筆）。
#    外文條目一律是「姓, 名」開頭，用這個當條目起點來補刀。
EN_START = re.compile(r"^[A-Z][A-Za-z\-'’]+,\s+[A-Z]")
# 「台南：台灣教會公報社，2016。」這種是折行的後半截，不是新的一筆
CONT = re.compile(r"^(?:[一-鿿]{2,5}：|\d{4}[。，]|頁\d)")


def parse(raw, source):
    """把排版行併成條目。

    🚨 空行不是條目邊界——兩份來源都把一筆書目折成好幾行，行與行之間一樣有空行。
       可靠的邊界是**條目以「。」收尾**（兩份的體例都如此），所以一路併到句號為止。
       用空行切會把一筆切成三四筆，看起來筆數很多其實全是碎片。
    🚨 分類標題要在併行**之前**認掉，否則會被黏進下一筆的開頭。
    """
    items, sec, sub, buf = [], "", "", ""
    for ln in raw:
        s = ln.strip()
        if not s or re.fullmatch(r"\d{1,4}", s):        # 空行、孤行頁碼
            continue
        if not buf:                                      # 只有在沒有半截條目時才可能是標題
            m = SECTION.match(s)
            if m and len(s) <= 20:
                sec, sub = (m.group(2) or "").strip(), ""
                continue
            m = SUBSEC.match(s)
            if m and len(s) <= 20:
                sub = (m.group(2) or "").strip()
                continue
            # 沒有編號的次標題（「史料彙編、文集、回憶錄」「報紙、雜誌」）：
            # 短、不以句號收尾、不含書名號與數字
            if len(s) <= 16 and not s.endswith("。") and not re.search(r"[《〈\d]", s):
                sub = s
                continue
        if buf and EN_START.match(s):        # 外文：遇到下一筆的開頭就先收掉上一筆
            items.append({"section": sec, "sub": sub, "text": buf, "source": source})
            buf = ""
        buf += s
        if buf.endswith("。"):
            items.append({"section": sec, "sub": sub, "text": buf, "source": source})
            buf = ""
    if buf:
        items.append({"section": sec, "sub": sub, "text": buf, "source": source})
    # 🚨 條目內部也可能出現句號（「〈洛桑信約〉（The Lausanne Covenant）。／1974。」），
    #    那會把一筆切成兩筆，而後半截短得離譜。太短的一律併回前一筆。
    out = []
    for it in items:
        if out and (len(it["text"]) < 14 or CONT.match(it["text"])):
            out[-1]["text"] += it["text"]
        else:
            out.append(it)
    return out


def master():
    import fitz
    d = fitz.open(MA_PDF)
    raw = []
    for i in range(MA_FROM - 1, MA_TO):
        raw += d[i].get_text().splitlines()
    d.close()
    # 砍掉標題行本身
    raw = [x for x in raw if x.strip() != "徵引資料"]
    return parse(raw, "碩士論文")


def bachelor():
    """ref.txt 前段是參考文獻、後段是全文註腳（以「1 」開頭那行起）。
    註腳裡有大量書目沒收進參考文獻，一樣要留，但要標明來源不同。"""
    raw = [x for x in BA_REF.read_text(encoding="utf-8-sig").splitlines()
           if x.strip() != "參考文獻"]
    # 🚨 ref.txt 尾巴還接了一張「附錄‧台灣福音派運動歷史年表」的表格，
    #    不切掉會被當成一筆四千多字的書目。
    cut = next((i for i, x in enumerate(raw)
                if FOOTNOTE.match(x) or x.strip().startswith("附錄")), len(raw))
    bib = parse(raw[:cut], "學士論文")
    notes = []
    for x in raw[cut:]:
        m = FOOTNOTE.match(x)
        if m:
            notes.append({"section": "註腳", "sub": "", "n": int(m.group(1)),
                          "text": x.strip(), "source": "學士論文"})
        elif notes:
            notes[-1]["text"] += x.strip()
    return bib, notes


def main():
    ma = master()
    ba, ba_notes = bachelor()
    data = {
        "note": "兩本改寫計畫的原始徵引資料。碩論取自 Drive 原檔「徵引資料」一節，"
                "學士論文取自站上 ref.txt。分類沿用原論文的層級。",
        "groups": [
            {"key": "mahaprajapati-revolution", "degree": "碩士論文",
             "title": "當代的大愛道革命（原題：昭慧法師與性廣法師的人間佛教思想與實踐）",
             "school": "國立臺北教育大學台灣文化研究所", "year": "2025",
             "count": len(ma), "items": ma},
            {"key": "bachelor-evangelical", "degree": "學士論文",
             "title": "福音派運動在台灣基督教中的起源與發展",
             "school": "國立臺灣大學歷史學系", "year": "2018",
             "count": len(ba), "items": ba,
             "footnotes": ba_notes, "footnoteCount": len(ba_notes)},
        ],
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    for g in data["groups"]:
        secs = sorted({i["section"] for i in g["items"] if i["section"]})
        extra = f"＋註腳 {g['footnoteCount']} 條" if g.get("footnoteCount") else ""
        print(f"  {g['degree']}：{g['count']} 筆{extra}／{len(secs)} 類　{'、'.join(secs)[:60]}")
    print(f"→ {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
