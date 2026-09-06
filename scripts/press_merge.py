# -*- coding: utf-8 -*-
"""跨來源的篇目合併與去重：華藝 → 國圖 → 臺大佛圖，前面沒有的才收後面。

三個來源各有各的缺口，同一篇文章常常兩三邊都有：

  華藝      卷期頁碼齊、有全文，但綁玄奘機構 IP，且沒有戰後那批佛教老雜誌
  國圖      卷期頁碼零缺漏、部分 PDF 匿名可下，但基督教側幾乎不收
  臺大佛圖  量最大（《海潮音》26,220 vs 國圖 4,995），全文多但多半是掃描版

優先序就是上面的順序：**同一篇以先出現的那一份為準**，後面的只補新的。
理由是「已經收進站內的那一份」已經有下游（reader 頁、下載帳本、書目佇列）指著它，
換掉會讓那些指向落空；而三邊的卷期頁碼品質其實相當。

🚨 **去重鍵用（刊名, 卷, 期, 起始頁），不用篇名。**
   「編者的話」「打開天窗」這種標題每期都有一篇，拿篇名當鍵會把不同期的併成一篇——
   而合併後的清單看起來只是「少了幾筆重複」，完全看不出是把不同期的內容吃掉了。
   卷期或頁碼解析不出來的，一律**當成獨立一筆保留**，寧可重複也不要吃掉。

  python -X utf8 scripts/press_merge.py --report        # 只看重疊狀況，不寫檔
  python -X utf8 scripts/press_merge.py --build         # 產合併索引
"""
import argparse
import json
import re
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PRESS = REPO / "public/content/research-data/press"
OUT = PRESS / "merged-index.json"

# 優先序：先出現的贏
SOURCES = ["airiti", "ncl", "dlbs"]

_PUNCT = re.compile(r"[\s　《》〈〉「」『』（）()\[\]【】：:；;，,、。.？?！!"
                    r"‐-―─-┃﹘﹣－\-_~·‧．／/\\|'\"“”‘’=]+")


def norm_journal(s):
    """刊名比對鍵。三邊的寫法不一：
    華藝「道風：基督教文化評論」、臺大「菩提樹=Bodhedrum」、國圖「菩提樹」。
    取中文那半、去標點。
    """
    s = unicodedata.normalize("NFKC", s or "")
    s = s.split("=")[0]                     # 臺大的「中文=English」
    parts = [p for p in s.split("/") if re.search(r"[一-鿿]", p)]
    if parts:
        s = parts[-1]
    return _PUNCT.sub("", s)


VOL_PATTERNS = [
    re.compile(r"v\.\s*(\d+)\s*n\.\s*(\d+)"),      # 臺大 v.83 n.1
    re.compile(r"(\d+)\s*[:：]\s*(\d+)"),           # 國圖 80:6
    re.compile(r"(\d+)\s*卷\s*(\d+)\s*期"),         # 華藝 68卷2期
]
ISSUE_ONLY = [
    re.compile(r"^\s*n\.\s*(\d+)"),                 # 臺大 n.26
    re.compile(r"^\s*(\d+)\s*期"),                  # 華藝 26期
    re.compile(r"^\s*(\d+)\s"),                     # 國圖 「3 1999.02[民88.02]」
]


def vol_issue(s):
    """回 (卷, 期)；只有期號就回 (None, 期)；都解不出就回 (None, None)。"""
    s = unicodedata.normalize("NFKC", s or "")
    for p in VOL_PATTERNS:
        m = p.search(s)
        if m:
            return int(m.group(1)), int(m.group(2))
    for p in ISSUE_ONLY:
        m = p.search(s)
        if m:
            return None, int(m.group(1))
    return None, None


PAGE_RE = re.compile(r"(\d+)")


def page_start(s):
    m = PAGE_RE.search(unicodedata.normalize("NFKC", s or "").replace("頁", ""))
    return int(m.group(1)) if m else None


def key_of(journal, vol_text, page_text):
    """去重鍵。任何一段解不出來就回 None ＝ 這一筆不參與去重、一律保留。"""
    j = norm_journal(journal)
    v, n = vol_issue(vol_text)
    p = page_start(page_text)
    if not j or n is None or p is None:
        return None
    return (j, v, n, p)


# ---------------------------------------------------------------- 各來源讀取

def load_airiti():
    for f in sorted((PRESS / "airiti").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for a in d.get("articles", []):
            yield {"source": "airiti", "journal": d["name"], "title": a["title"],
                   "authors": a.get("authors", []), "vol": a.get("volIssue", ""),
                   "page": a.get("pages", ""), "date": a.get("date", ""),
                   "fulltext": bool(a.get("fulltext")), "id": a.get("docId", "")}


def load_ncl():
    for f in sorted((PRESS / "ncl").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for a in d.get("articles", []):
            yield {"source": "ncl", "journal": d["name"], "title": a["title"],
                   "authors": [a.get("author", "")], "vol": a.get("vol", ""),
                   "page": a.get("page", ""), "date": a.get("vol", ""),
                   "fulltext": bool(a.get("pdf")), "id": ""}


def load_dlbs():
    d_dir = PRESS / "dlbs"
    for f in sorted(d_dir.glob("*.json")) if d_dir.exists() else []:
        d = json.loads(f.read_text(encoding="utf-8"))
        for a in d.get("articles", []):
            yield {"source": "dlbs", "journal": d["name"], "title": a["title"],
                   "authors": [a.get("author", "")], "vol": a.get("archive", ""),
                   "page": a.get("page", ""), "date": a.get("presstime", ""),
                   "fulltext": bool(a.get("fulltext")), "id": a.get("seq", "")}


LOADERS = {"airiti": load_airiti, "ncl": load_ncl, "dlbs": load_dlbs}


def merge():
    seen, rows, stats = set(), [], {}
    for src in SOURCES:
        added = dup = nokey = 0
        for rec in LOADERS[src]():
            k = key_of(rec["journal"], rec["vol"], rec["page"])
            if k is None:
                nokey += 1                    # 解不出鍵就保留，不參與去重
            elif k in seen:
                dup += 1
                continue
            else:
                seen.add(k)
            rows.append(rec)
            added += 1
        stats[src] = {"新增": added, "與前面重複": dup, "無法產生去重鍵（保留）": nokey}
    return rows, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args()
    if not (a.report or a.build):
        ap.print_help()
        return
    rows, stats = merge()
    print(f"{'來源':<8}{'新增':>8}{'與前面重複':>10}{'無鍵保留':>10}")
    for s in SOURCES:
        st = stats[s]
        print(f"{s:<8}{st['新增']:>8}{st['與前面重複']:>10}{st['無法產生去重鍵（保留）']:>10}")
    print(f"{'合計':<8}{len(rows):>8}")
    if a.build:
        by_j = {}
        for r in rows:
            by_j.setdefault(norm_journal(r["journal"]), []).append(r)
        OUT.write_text(json.dumps(
            {"note": "跨來源合併：華藝→國圖→臺大佛圖，前面沒有的才收後面。"
                     "去重鍵是（刊名, 卷, 期, 起始頁），不是篇名——"
                     "「編者的話」這種每期都有，用篇名會把不同期併掉。",
             "priority": SOURCES, "stats": stats,
             "counts": {"合併後篇目": len(rows), "刊數": len(by_j)},
             "byJournal": {k: len(v) for k, v in sorted(by_j.items(), key=lambda x: -len(x[1]))}},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"→ {OUT}")


if __name__ == "__main__":
    main()
