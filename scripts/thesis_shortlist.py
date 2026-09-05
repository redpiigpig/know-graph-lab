# -*- coding: utf-8 -*-
"""把 NDLTD 抓回來的學位論文書目，篩成博士論文各章可用的優先清單。

上游是 `thesis_ndltd.py`（檢索與書目），本檔只做離線的篩選與排序，不連網。
分開的理由：檢索受站方驗證碼節制、常常只能一次跑幾組，而篩選規則會隨著
計畫書改章節而反覆調整——兩件事綁在一起的話，每改一次評分規則就得重抓一次。

🚨「有電子全文」只代表檔案存在，不代表拿得到。實際分三種：公開取用、
   校內限閱、有償授權未公開。逐本不同，必須一本一本確認。
   （實例：台大〈台灣基督長老教會政治論述之分析〉標有電子全文，
   實際是「有償授權、未授權公開取用」。）

index：public/content/research-data/pct/thesis-shortlist.json

  python -X utf8 scripts/thesis_shortlist.py
  python -X utf8 scripts/thesis_shortlist.py --axis 第二章    # 只看某一軸
"""
import argparse
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "public/content/research-data/pct/biblio-ndltd.json"
OUT = REPO / "public/content/research-data/pct/thesis-shortlist.json"

# 依計畫書現行七章（2026-09 版：《從彼岸向此岸的轉向》1920–2020）。
# 每一軸給一組題名關鍵詞；命中越多分數越高。
# 🚨 關鍵詞是拿來**排序**的，不是拿來判定「這本無關」。落在門檻外的不會被刪，
#    只是不進清單——所以門檻調鬆一點沒關係，調緊才會漏掉東西。
AXES = {
    "第二章　東亞近代宗教變革": [
        "清沢", "日蓮", "無教會", "內村鑑三", "矢內原", "賀川", "妹尾",
        "廟產興學", "吳耀宗", "青年會", "社會福音",
        "三一運動", "天道教", "東學", "韓龍雲", "民眾神學",
        "林秋梧", "文化協會", "南瀛佛教", "日治", "日據", "殖民",
        "近代", "明治", "大正",
    ],
    "第三章　人間佛教在台灣": [
        "太虛", "印順", "傳道", "妙心", "昭慧", "性廣",
        "人間佛教", "人生佛教", "佛教革命", "契理契機", "初期大乘",
        "佛教倫理", "規範倫理", "護生", "弘誓",
    ],
    "第四章　台灣本土神學": [
        "黃彰輝", "宋泉盛", "王憲治", "黃伯和",
        "實況化", "本色化", "鄉土神學", "出頭天", "故事神學",
        "本土神學", "長老教會", "台南神學院", "台灣神學院",
        "人權宣言", "國是聲明", "自決", "認同",
    ],
    "第五章　佛耶對話與議題結盟": [
        "佛耶", "佛教與基督教", "宗教對話", "跨宗教", "宗教交談",
        "煮雲", "龔天民", "吳恩溥", "護教", "論戰", "闢邪",
        "結盟", "社會運動", "反賭", "廢除死刑", "廢死",
        "動物保護", "動保", "同性婚姻", "性別平權", "婚姻平權",
    ],
    "第六章　理論：世俗化與宗教多元": [
        "世俗化", "宗教多元", "希克", "尼特", "潘尼卡",
        "比較神學", "宗教神學", "公共神學", "公共宗教", "公民社會",
        "政教關係", "宗教與政治",
    ],
}

# 這些詞出現在題名裡，代表這本是「以本論文的對象為題」而不只是順帶提到。
# 命中就加權——系譜八人與兩個核心概念。
CORE = ["太虛", "印順", "傳道法師", "昭慧", "黃彰輝", "宋泉盛", "王憲治", "黃伯和",
        "人間佛教", "本土神學", "實況化", "鄉土神學", "出頭天"]


def load():
    if not SRC.exists():
        raise SystemExit(f"找不到 {SRC}；先跑 thesis_ndltd.py --search")
    return json.loads(SRC.read_text(encoding="utf-8"))


def dedupe(groups):
    """同一本會在多組檢索裡重複出現；以（題名, 校院）為鍵合併，並記下它被哪幾組打到。

    🚨 用題名當唯一鍵是不夠的：不同學校會有同名論文。加上校院才不會把兩本併成一本。
    """
    by_key = {}
    for g in groups:
        for it in g.get("items", []):
            k = (it["title"].strip(), it.get("school", "").strip())
            row = by_key.setdefault(k, {**it, "hits": []})
            row["hits"].append(g.get("note") or g.get("query"))
    return list(by_key.values())


def score(row):
    """回傳 (最相關的軸, 分數, 命中的詞)。分數只用來排序，不代表相關程度的絕對值。"""
    title = row.get("title", "")
    best, best_n, best_words = "", 0, []
    for axis, words in AXES.items():
        hit = [w for w in words if w in title]
        if len(hit) > best_n:
            best, best_n, best_words = axis, len(hit), hit
    if not best_n:
        return "", 0, []
    n = best_n
    n += sum(2 for w in CORE if w in title)          # 以系譜人物為題的加重
    if row.get("degree") == "博士":
        n += 2                                        # 博士論文的文獻回顧本身就是地圖
    if row.get("fulltext"):
        n += 1
    return best, n, best_words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", help="只輸出某一軸（用章名的一部分比對）")
    ap.add_argument("--min-score", type=int, default=3)
    args = ap.parse_args()

    groups = load()
    rows = dedupe(groups)
    scored = []
    for r in rows:
        axis, n, words = score(r)
        if not axis or n < args.min_score:
            continue
        scored.append({
            "kind": "學位論文",
            "title": r["title"], "author": r.get("author", ""),
            "advisor": r.get("advisor", ""), "school": r.get("school", ""),
            "dept": r.get("dept", ""), "year": r.get("year", ""),
            "degree": r.get("degree", ""), "fulltext": bool(r.get("fulltext")),
            "axis": axis, "score": n, "matched": words,
            "priority": "★" if (r.get("degree") == "博士" and r.get("fulltext")
                                and any(w in r["title"] for w in CORE)) else "",
            "hits": sorted(set(r["hits"]))[:4],
        })
    scored.sort(key=lambda x: (x["axis"], -x["score"], x["school"]))
    if args.axis:
        scored = [x for x in scored if args.axis in x["axis"]]

    # 被截斷的組要明著寫進輸出。站上 840 筆只取回 160 筆的那種，
    # 清單看起來一樣漂亮，但少掉的 680 筆完全不留痕跡。
    # total 為 0 ＝那一組是舊版抓的、沒帶回站方自報總數，屬於「不確定有沒有截斷」，
    # 不要印成「站上 0 筆」——那會讀成「站上一本都沒有」，剛好相反。
    truncated = [{"query": g["query"], "note": g.get("note", ""),
                  "取回": g.get("count", 0),
                  "站上": g.get("total") or "（舊版未記錄）"}
                 for g in groups if g.get("truncated")]
    by_axis = Counter(x["axis"] for x in scored)

    data = {
        "name": "與博士論文相關的碩博士論文清單",
        "note": "計畫書《從彼岸向此岸的轉向：台灣佛教與基督教公共性之宗教史比較研究"
                "（1920–2020）》七章架構。分數只用來排序，不是相關度的絕對值；"
                "★＝博士學位＋有電子全文＋題名命中系譜人物或核心概念。"
                "🚨「有電子全文」只代表檔案存在，不代表拿得到——分公開取用、校內限閱、"
                "有償授權未公開三種，逐本不同，必須一本一本確認。",
        "counts": {
            "檢索組數": len(groups),
            "書目總筆數": sum(g.get("count", 0) for g in groups),
            "去重": len(rows),
            "入選": len(scored),
            "其中博士": sum(1 for x in scored if x["degree"] == "博士"),
            "其中有電子全文": sum(1 for x in scored if x["fulltext"]),
            "★優先追": sum(1 for x in scored if x["priority"]),
        },
        "byAxis": dict(by_axis),
        "truncated": truncated,
        "items": scored,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(groups)} 組檢索 / 去重 {len(rows)} 本 / 入選 {len(scored)} 本")
    for a, n in by_axis.most_common():
        print(f"  {a:<24} {n:>4} 本")
    if truncated:
        print(f"\n⚠ {len(truncated)} 組被截斷（站上比取回多）：")
        for t in truncated:
            print(f"  {t['query']:<22} 取回 {t['取回']:>3} / 站上 {t['站上']}")
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    main()
