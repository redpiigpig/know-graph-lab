#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""替「當代佛學研究」卡片補上**文章**那一層。

書目那一層（`bibliography.jsonl`）收的是專書，多半是外文。這一層收的是**華語佛學
期刊的論文**，來源是既有的華藝篇目索引——那批早就抓好了（見 [[research-data-airiti]]），
而且帶著做註腳非有不可的三個欄位：**卷期、起訖頁、正式作者署名**。

作法與神學那張卡的 `contemporary_theology_articles.py` 一致：七個分區各給一組關鍵詞
去掃篇名。⚠️ 這是**粗篩不是分類**：

  * 一篇可以同時落進多區（〈比丘尼僧團的戒律問題〉進 gender 也進 institution），
    這是刻意的，不要硬分單一類。
  * 關鍵詞比對必然有假命中（「業」可能是「事業」）。所以詞表盡量用兩字以上的詞，
    頁面上也標明這是候選清單、要人工再挑。
  * 沒被任何一區收走的篇目不代表不相關，只代表篇名裡沒有這些詞。

⚠️ 弘誓雙月刊（2,226 篇）是刊物型而非學報型，短文與活動報導佔多數，命中率會偏低，
這是正常的——它的價值在 [[research-data-hongshi]] 那張卡，不在這裡。

輸出 `public/content/research-data/buddhist-studies/articles.json`（進版控）。

用法：
  python scripts/buddhist_studies_articles.py          # 建文章層
  python scripts/buddhist_studies_articles.py --check  # 只看各區命中數與抽樣
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
TOC = ROOT / "public" / "content" / "research-data" / "press" / "airiti"
OUT = ROOT / "public" / "content" / "research-data" / "buddhist-studies" / "articles.json"

# 只掃佛學這一側的刊；基督教與宗教學綜合那些留給各自的卡片
JOURNALS = ["chbs-journal", "chbs-journal-old", "chbs-studies", "ddbj",
            "ntu-buddhist", "ntu-buddhist-old", "fgu-journal", "hcu-buddhist",
            "dharma-seals", "huayen", "humanistic-buddhism", "hbj-arts", "hongshi"]

# 分區 → 篩選詞。用兩字以上的詞，寧可漏不要髒。
TERMS = {
    "method": ["佛學研究", "研究方法", "研究回顧", "方法論", "批判佛教", "京都學派",
               "文獻學", "學術史", "詮釋學", "研究述評", "研究趨勢", "學科"],
    "textual": ["寫本", "敦煌", "疑偽經", "偽經", "梵本", "梵文", "藏譯", "漢譯",
                "對勘", "異譯", "校勘", "版本", "巴利", "阿含", "文本", "譯經",
                "經典成立", "注疏", "音義", "抄本"],
    "history": ["佛教史", "教史", "中國佛教", "日本佛教", "韓國佛教", "印度佛教",
                "藏傳", "南傳", "近代佛教", "宗派", "僧傳", "傳播", "東傳",
                "明清佛教", "唐代", "宋代", "民國"],
    "gender": ["比丘尼", "八敬法", "性別", "女性", "尼眾", "女眾", "女性主義",
               "酷兒", "婦女", "菩薩戒與女"],
    "social": ["入世佛教", "人間佛教", "社會關懷", "環保", "生態", "慈善",
               "社會運動", "民族主義", "佛教與政治", "經濟倫理", "公民",
               "臨終關懷", "護生", "素食"],
    "institution": ["僧團", "戒律", "律制", "寺院", "僧伽", "僧教育", "教團",
                    "居士", "僧職", "度牒", "叢林", "清規", "教制", "道場"],
    "doctrine": ["阿毘達磨", "阿毗達磨", "中觀", "唯識", "如來藏", "佛性", "禪法",
                 "禪宗", "淨土", "密教", "天台", "華嚴", "空性", "緣起", "業報",
                 "涅槃", "菩薩", "般若", "止觀", "三性", "二諦", "法身"],
}

NAMES = {"method": "佛學研究方法論", "textual": "經典批判與詮釋", "history": "教史研究",
         "gender": "性別研究", "social": "社會研究", "institution": "制度研究",
         "doctrine": "教理研究"}

AUTHOR_EN = re.compile(r"\s*\([^)]*\)\s*$")


def clean_author(a: str) -> str:
    """華藝的作者欄是「釋昭慧(Shih Chao-Hwei)」，頁面只要中文那一段。"""
    return AUTHOR_EN.sub("", a or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    hits: dict[str, list[dict]] = {k: [] for k in TERMS}
    total = scanned = 0
    missing = []
    for slug in JOURNALS:
        f = TOC / f"{slug}.json"
        if not f.exists():
            missing.append(slug)
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        jname = d.get("name", slug)
        for a in d.get("articles") or []:
            scanned += 1
            title = a.get("title") or ""
            for area, words in TERMS.items():
                if any(w in title for w in words):
                    hits[area].append({
                        "journal": jname, "slug": slug,
                        "title": title,
                        "authors": [clean_author(x) for x in (a.get("authors") or [])],
                        "issue": a.get("volIssue") or a.get("issueLabel"),
                        "date": a.get("date"), "pages": a.get("pages"),
                        "fulltext": bool(a.get("fulltext")),
                        "docId": a.get("docId"),
                    })
                    total += 1
    if missing:
        print(f"⚠️ 這幾刊還沒抓篇目：{'、'.join(missing)}（跑 press_airiti.py --toc <slug>）")

    print(f"掃過 {scanned:,} 篇，命中 {total:,} 筆（同一篇可落多區）")
    for area, rows in hits.items():
        rows.sort(key=lambda r: (r.get("date") or ""), reverse=True)
        ft = sum(1 for r in rows if r["fulltext"])
        print(f"  {NAMES[area]:12s} {len(rows):>4} 篇，其中華藝有全文 {ft}")
        if args.check and rows:
            for r in rows[:3]:
                print(f"        {r['date']}　{r['journal']}　{r['title'][:40]}")

    if args.check:
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "note": "從既有華藝篇目按關鍵詞粗篩出的候選清單，一篇可落多區，未經人工複核",
        "scanned": scanned,
        "journals": JOURNALS,
        "areas": {a: {"name": NAMES[a], "terms": TERMS[a], "count": len(r), "items": r}
                  for a, r in hits.items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
