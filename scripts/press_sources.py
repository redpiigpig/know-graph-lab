# -*- coding: utf-8 -*-
"""三個來源的刊物對照表：同一份刊在華藝／國圖／臺大各有多少篇目。

做這張表的理由很實際：找《海潮音》的時候，華藝一筆都沒有、國圖 4,995 筆、
臺大 26,220 筆。不並排看，就會在只有一個來源的地方翻半天，
或者以為「查不到＝不存在」。

順帶標出年份離群值。來源端偶有筆誤（《人生》有一筆寫成 1858.03，該刊 1949 創刊），
**不改來源資料**，但要標出來——不標的話，日後做逐年詞頻會被一筆髒資料把橫軸拉長，
而圖表看起來完全正常。

輸出：public/content/research-data/press/sources-index.json

  python -X utf8 scripts/press_sources.py --build
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PRESS = REPO / "public/content/research-data/press"
OUT = PRESS / "sources-index.json"

_PUNCT = re.compile(r"[\s　《》〈〉「」『』（）()\[\]【】：:；;，,、。.？?！!"
                    r"‐-―─-┃﹘﹣－\-_~·‧．／/\\|'\"“”‘’=]+")


def norm(s):
    """刊名比對鍵。三邊寫法不一：華藝「道風：基督教文化評論」、
    臺大「菩提樹=Bodhedrum」、國圖「菩提樹」。取中文那半、去標點與全半形差異。
    🚨 也要去掉不斷行空白——臺大的 facet 值帶著 `\\xa0`。
    """
    s = unicodedata.normalize("NFKC", (s or "").replace("\xa0", " "))
    s = s.split("=")[0]
    parts = [p for p in s.split("/") if re.search(r"[一-鿿]", p)]
    if parts:
        s = parts[-1]
    return _PUNCT.sub("", s)


def load_airiti():
    f = PRESS / "airiti-index.json"
    if not f.exists():
        return {}
    return {norm(r["name"]): {"name": r["name"], "articles": r["articles"],
                              "fulltext": r.get("fulltext", 0),
                              "start": r.get("start"), "end": r.get("end"),
                              "to": f"/research-data/press/{r['slug']}"}
            for r in json.loads(f.read_text(encoding="utf-8"))}


def load_ncl():
    f = PRESS / "ncl-index.json"
    if not f.exists():
        return {}
    return {norm(r["name"]): {"name": r["name"], "articles": r["articles"],
                              "fulltext": r.get("pdf", 0),
                              "start": r.get("start"), "end": r.get("end"),
                              "slug": r["slug"]}
            for r in json.loads(f.read_text(encoding="utf-8"))}


def load_dlbs():
    f = PRESS / "dlbs-index.json"
    if not f.exists():
        return {}
    d = json.loads(f.read_text(encoding="utf-8"))
    return {norm(r["name"]): {"name": r["name"].strip(), "articles": r["articles"],
                              "fulltext": r.get("fulltext", 0),
                              "start": r.get("start"), "end": r.get("end"),
                              "slug": r["slug"], "key": r.get("key"),
                              "missingPage": r.get("missingPage", 0)}
            for r in d["journals"]}


# 孤立離群的判準：某一年只有 1–2 筆，而且與下一個有資料的年份相差 20 年以上。
#
# 🚨 **不能只用「年份是否落在合理區間」來判。** 那樣只抓得到 `year=1`、`year=4`
#    這種一眼假的，抓不到真正會害人的那種：《人生》索引起始寫 1858（該刊
#    1949 創刊），1858 落在任何「合理區間」內，卻是來源端把 1958 打成 1858。
#    實際分佈是 1858 只有 1 筆、下一個有資料的年份是 1935——差 77 年。
#    要看分佈才判得出來，而分佈在 R2 的逐筆篇目裡。
#
# 判出來也**不修改來源資料**，只記在索引裡。不記的話，逐年詞頻會被一筆髒資料
# 把橫軸拉長 90 年，而圖表看起來完全正常。
OUTLIER_MAX_COUNT = 2
OUTLIER_MIN_GAP = 20
# 由 `--scan-years` 產出，是逐份看過 R2 分佈的結果（見上）。
OUTLIER_CACHE = Path("C:/tmp/dlbs_year_outliers.json")


def load_outliers():
    if not OUTLIER_CACHE.exists():
        return {}
    return {x["name"]: x for x in json.loads(OUTLIER_CACHE.read_text(encoding="utf-8"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if not a.build:
        ap.print_help()
        return

    src = {"airiti": load_airiti(), "ncl": load_ncl(), "dlbs": load_dlbs()}
    outliers = load_outliers()
    keys = sorted(set().union(*(s.keys() for s in src.values())))
    rows, flagged = [], []
    for k in keys:
        row = {"key": k, "name": "", "sources": {}}
        best = 0
        for name, table in src.items():
            r = table.get(k)
            if not r:
                continue
            row["sources"][name] = r
            if r["articles"] > best:            # 顯示名取篇數最多那一邊的寫法
                best, row["name"] = r["articles"], r["name"]
            o = outliers.get(r["name"].strip())
            if o and name == "dlbs":
                flagged.append({"journal": r["name"].strip(), "source": name,
                                "indexStart": o["indexStart"],
                                "realStart": o["realStart"],
                                "outlierYears": o["outlierYears"]})
                r["realStart"] = o["realStart"]     # 讓頁面顯示實際起始
                r["yearOutliers"] = o["outlierYears"]
        row["total"] = sum(v["articles"] for v in row["sources"].values())
        row["inSources"] = len(row["sources"])
        rows.append(row)
    rows.sort(key=lambda r: -r["total"])

    OUT.write_text(json.dumps({
        "note": "同一份刊在華藝／國圖／臺大佛圖各收多少篇目。"
                "三邊互補而不是重複：華藝有全文但綁機構 IP、國圖卷期頁碼零缺漏、"
                "臺大量最大。yearOutliers 是來源端的年份筆誤，**沒有修改原始資料**，"
                "標出來是為了不讓逐年詞頻被一筆髒資料把橫軸拉長。",
        "counts": {
            "刊（去重後）": len(rows),
            "三邊都有": sum(1 for r in rows if r["inSources"] == 3),
            "只有一邊": sum(1 for r in rows if r["inSources"] == 1),
            "篇目合計（未跨來源去重）": sum(r["total"] for r in rows),
        },
        "yearOutliers": flagged,
        "journals": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{len(rows)} 刊（去重後）／篇目合計 {sum(r['total'] for r in rows):,}")
    print(f"  三邊都有 {sum(1 for r in rows if r['inSources']==3)}"
          f"｜兩邊 {sum(1 for r in rows if r['inSources']==2)}"
          f"｜只有一邊 {sum(1 for r in rows if r['inSources']==1)}")
    if flagged:
        print("\n年份離群（未修改來源資料，只標記）：")
        for x in flagged:
            print(f"  {x['journal'][:18]:<20}索引起始 {x['indexStart']} "
                  f"→ 實際 {x['realStart']}　離群 {x['outlierYears']}")
    print(f"\n→ {OUT}")


if __name__ == "__main__":
    main()
