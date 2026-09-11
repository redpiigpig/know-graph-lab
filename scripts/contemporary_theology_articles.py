#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""替「當代神學研究」卡片補上**文章**那一層。

書目那一層（`bibliography.jsonl`）收的是專書，多半是外文。這一層收的是**華語神學
期刊的論文**，來源是既有的華藝篇目索引——那批早就抓好了（見 [[research-data-airiti]]），
而且帶著做註腳非有不可的三個欄位：**卷期、起訖頁、正式作者署名**。

作法是把十二個分區各給一組關鍵詞，拿去掃篇名。⚠️ 這是**粗篩不是分類**：

  * 一篇可以同時落進多區（〈女性主義的解放神學〉進 gender 也進 liberation），
    這是刻意的，不要硬分單一類。
  * 關鍵詞比對必然有假命中（「解放」可能是講出埃及）。所以頁面上標明這是
    候選清單，要人工再挑；也因此**寧可嚴一點**——寧可漏，不要讓每一區都塞滿雜訊。
  * 沒被任何一區收走的篇目不代表不相關，只代表篇名裡沒有這些詞。

輸出 `public/content/research-data/contemporary-theology/articles.json`（進版控）。

用法：
  python scripts/contemporary_theology_articles.py          # 建文章層
  python scripts/contemporary_theology_articles.py --check  # 只看各區命中數與抽樣
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
OUT = ROOT / "public" / "content" / "research-data" / "contemporary-theology" / "articles.json"

# 只掃基督教／神學這一側的刊；佛教與宗教學那些留給各自的卡片
JOURNALS = ["theology-church", "taiwan-theology", "logos-pneuma", "sino-christian",
            "jiandao", "collectanea", "ces-journal", "baptist-annual",
            "campus", "new-messenger", "wilderness", "dao-magazine"]

# 分區 → 篩選詞。用長詞、少用單字詞，寧可漏不要髒。
TERMS = {
    "method": ["神學方法", "方法論", "神學建構", "漢語神學", "處境化", "本色化",
               "後自由", "神學詮釋學", "神學與哲學", "神學的任務", "典範轉移"],
    "history": ["神學史", "巴特", "田立克", "潘霍華", "士萊馬赫", "哈納克", "布特曼",
                "拉內", "莫特曼", "潘能伯格", "特爾慈", "尼布爾", "新正統", "祈克果",
                "齊克果", "梵二", "第二次梵蒂岡"],
    "biblical": ["舊約神學", "新約神學", "聖經神學", "正典", "釋經", "經文詮釋",
                 "保羅神學", "福音書", "符類福音", "約翰福音", "希伯來聖經", "七十士"],
    "systematics": ["系統神學", "教義學", "基督論", "三一", "救恩論", "教會論",
                    "末世論", "聖靈論", "創造論", "稱義", "神論", "恩典論", "位格"],
    "practical": ["實踐神學", "牧養", "牧會", "教牧", "講道", "宣講", "禮儀", "崇拜",
                  "靈修神學", "宗教教育", "基督教教育", "關顧", "輔導", "小組",
                  "門徒訓練", "青年事工"],
    "liberal": ["自由神學", "自由主義神學", "社會福音", "現代主義", "去神話"],
    "secular": ["世俗化", "世俗神學", "上帝之死", "無宗教", "後基督教", "公共領域"],
    "narrative": ["敘事神學", "故事神學", "敘事", "生命故事"],
    "liberation": ["解放神學", "受壓迫", "民眾神學", "第三世界神學", "拉丁美洲"],
    "gender": ["女性主義", "婦女神學", "性別", "女性神學", "同志", "酷兒", "父權",
               "女性主義神學", "婦女"],
    "contextual": ["處境神學", "鄉土神學", "本土神學", "出頭天", "原住民", "後殖民",
                   "亞洲神學", "非洲神學", "黑人神學", "本色化神學", "族群"],
    "global": ["普世運動", "普世教會", "全球化", "世界基督教", "宗教交談", "宗教對話",
               "跨宗教", "宗教多元", "合一運動"],
}

NAMES = {"method": "神學方法論", "history": "二十世紀神學史", "biblical": "聖經神學",
         "systematics": "系統神學經典", "practical": "實踐神學", "liberal": "自由神學",
         "secular": "世俗神學", "narrative": "敘事神學", "liberation": "解放神學",
         "gender": "性別神學", "contextual": "各地的神學", "global": "全球神學的嘗試"}

AUTHOR_EN = re.compile(r"\s*\([^)]*\)\s*$")


def clean_author(a: str) -> str:
    """華藝的作者欄是「楊順從(Shun Chung Yang)」，頁面只要中文那一段。"""
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
