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

# 🚨 低精確率的詞。**不要把這些詞從 TERMS 刪掉**——刪掉會犧牲召回率，
# 而且從結果上完全看不出來（清單變乾淨了，但你不知道漏了什麼）。
# 正解是留在詞表裡照收，只把「命中的全是弱詞」那些篇目標 weak，頁面上分開呈現。
# 依據是 2026-09-12 的抽樣（見 PRECISION），每一條後面是它為什麼弱。
WEAK = {
    "practical": {
        "禮儀",      # 幾乎全部命中「中國禮儀之爭」，那是宣教史不是實踐神學
        "崇拜",      # 命中「祖靈崇拜」「偶像崇拜」
        "宗教教育",  # 命中政教關係與宗教教育法制的文章
    },
    "biblical": {
        "聖經神學",  # 🚨 最典型的一個：命中長老教會「大專聖經神學研究班」的活動報導，
                     # 20 筆抽樣裡有 7 筆是這個。不是「聖經神學」這門學科。
    },
    "narrative": {
        "敘事",      # 聖經敘事批判、敘事治療、文學敘事研究、身分敘事全會命中，
                     # 與敘事神學是四回事
    },
    "contextual": {
        "原住民",    # 🚨 大量命中原住民社會議題的評論與報導，不是處境神學
        "族群",      # 命中「熟齡族群」「族群融合」
    },
    "global": {
        "全球化",    # 命中「全球化與台灣」「全球化傳染病」這類社會評論
    },
    "systematics": {
        "神論",      # 會命中景教文獻《一神論》
    },
    "liberal": {
        "現代主義",  # 會命中「後現代主義」
    },
}

# 2026-09-12 的抽樣結果：每區隨機抽 20 筆（母體不足 20 的全抽）逐筆判讀。
# precision = 真的屬於該區的比例。這組數字要出現在頁面上——本項工作的成果
# 不是「清單變乾淨」，而是「讀者知道這份清單有多不乾淨」。
PRECISION = {
    "history": (20, 1.00), "gender": (20, 1.00), "liberation": (7, 1.00),
    "secular": (6, 1.00), "systematics": (20, 0.95), "method": (20, 0.90),
    "liberal": (5, 0.80), "global": (20, 0.75), "practical": (20, 0.70),
    "biblical": (20, 0.65), "contextual": (20, 0.35), "narrative": (20, 0.35),
}
SAMPLED_ON = "2026-09-12"

AUTHOR_EN = re.compile(r"\s*\([^)]*\)\s*$")


def clean_author(a: str) -> str:
    """華藝的作者欄是「楊順從(Shun Chung Yang)」，頁面只要中文那一段。"""
    return AUTHOR_EN.sub("", a or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    hits: dict[str, list[dict]] = {k: [] for k in TERMS}
    total = scanned = weak_n = 0
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
                matched = [w for w in words if w in title]
                if not matched:
                    continue
                # 命中的詞全部都在 weak 清單裡，才標 weak：只要有一個強詞命中，
                # 這一筆就照常收（見檔頭「不要把詞表改成只留高精確率的詞」那一段）。
                weak = bool(matched) and all(w in WEAK.get(area, ()) for w in matched)
                hits[area].append({
                    "journal": jname, "slug": slug,
                    "title": title,
                    "authors": [clean_author(x) for x in (a.get("authors") or [])],
                    "issue": a.get("volIssue") or a.get("issueLabel"),
                    "date": a.get("date"), "pages": a.get("pages"),
                    "fulltext": bool(a.get("fulltext")),
                    "docId": a.get("docId"),
                    "hit": matched,
                    "weak": weak,
                })
                total += 1
                weak_n += weak
    if missing:
        print(f"⚠️ 這幾刊還沒抓篇目：{'、'.join(missing)}（跑 press_airiti.py --toc <slug>）")

    print(f"掃過 {scanned:,} 篇，命中 {total:,} 筆（同一篇可落多區），其中只靠弱詞命中 {weak_n:,} 筆")
    for area, rows in hits.items():
        rows.sort(key=lambda r: (r.get("date") or ""), reverse=True)
        ft = sum(1 for r in rows if r["fulltext"])
        wk = sum(1 for r in rows if r["weak"])
        pr = PRECISION.get(area, (0, None))[1]
        prs = f"　抽樣精確率 {pr:.0%}" if pr is not None else ""
        print(f"  {NAMES[area]:12s} {len(rows):>4} 篇（弱詞 {wk:>3}）"
              f"，其中華藝有全文 {ft}{prs}")
        if args.check and rows:
            for r in rows[:3]:
                print(f"        {r['date']}　{r['journal']}　{r['title'][:40]}")

    if args.check:
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "note": "從既有華藝篇目按關鍵詞粗篩出的候選清單，一篇可落多區，未經逐筆複核；"
                "各區的 precision 是抽樣量測值，weak 標記的是只靠低精確率的詞命中的篇目",
        "scanned": scanned,
        "sampled_on": SAMPLED_ON,
        "journals": JOURNALS,
        "areas": {a: {
            "name": NAMES[a], "terms": TERMS[a],
            "weak_terms": sorted(WEAK.get(a, ())),
            "count": len(r),
            "weak_count": sum(1 for x in r if x["weak"]),
            "sample": PRECISION.get(a, (0, None))[0],
            "precision": PRECISION.get(a, (0, None))[1],
            "items": r,
        } for a, r in hits.items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
