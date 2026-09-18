# -*- coding: utf-8 -*-
"""把抽出來的篇目整理成站上用的《聖書之研究》分號目次 JSON。

輸入：output/seisho-kenkyu-index.jsonl（seisho_kenkyu_index.py 產出）
輸出：public/content/collected-works/seisho-kenkyu.json

原則：**不靜默修資料**。號數與年月對不上的（OCR 把漢數字咬壞）標成 suspect 留在原地，
頁面上打問號讓人看得見，不要替它選一個看起來比較順的答案。

號↔年月：1900 年 9 月創刊、按月發行，1930 年 4 月終刊第 357 號；
356 個月出 357 號，所以「第 N 號 ≈ 1900-09 起算第 N 個月」只能當推估，
沒有實際年月時才拿來填，並標 date_estimated。
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "output" / "seisho-kenkyu-index.jsonl"
OUT = REPO / "public" / "content" / "collected-works" / "seisho-kenkyu.json"
LAST_ISSUE = 357

VOL_NAMES = {
    1: "初期的著作 上", 2: "初期的著作 下", 3: "舊約研究 上", 4: "舊約研究 下",
    5: "新約研究（福音書）", 6: "新約研究（羅馬書）", 7: "新約研究（使徒行傳～默示錄）",
    8: "教義研究 上", 9: "教義研究 下", 10: "", 11: "信仰講演・講話",
    12: "所感・詩與歌・愛吟", 13: "感想", 14: "時事・宗教與現世",
    15: "英文 上", 16: "英文 下", 17: "日記 上", 18: "日記 下",
    19: "隨筆・雜錄・雜報", 20: "書簡選集",
}


def ebook_id(vol: int) -> str:
    return f"d0000001-0000-4000-8000-{vol:012d}"


def est_date(issue: int) -> tuple[int, int]:
    m0 = (1900 * 12 + 9 - 1) + (issue - 1)
    return m0 // 12, m0 % 12 + 1


def clean_title(t: str) -> str:
    t = re.sub(r"[\s　]+", "", t or "")
    t = t.strip("・.,-—–_|｜")
    return t


def main() -> int:
    if not SRC.exists():
        print(f"✗ 找不到 {SRC}；先跑 seisho_kenkyu_index.py")
        return 1
    rows = [json.loads(l) for l in SRC.open(encoding="utf-8")]

    by = defaultdict(list)
    seen = set()
    dropped = 0
    for r in rows:
        title = clean_title(r.get("title", ""))
        if len(title) < 2:                       # OCR 只剩碎片的丟掉
            dropped += 1
            continue
        issue = r["issue"]
        key = (issue, title, r["vol"])
        if key in seen:
            continue
        seen.add(key)
        y, mo = r.get("year"), r.get("month")
        est = est_date(issue)
        item = {
            "title": title,
            "vol": r["vol"],
            "volName": VOL_NAMES.get(r["vol"], ""),
            "ebookId": ebook_id(r["vol"]),
            "year": y or est[0],
            "month": mo or est[1],
            "dateEstimated": not (y and mo),
            "suspect": r.get("consistent") is False,
            "src": r.get("src", ""),        # 這條篇目是哪一份 OCR 抽到的，備查用
        }
        by[issue].append(item)

    issues = []
    for n in range(1, LAST_ISSUE + 1):
        items = sorted(by.get(n, []), key=lambda x: (x["vol"], x["title"]))
        y, mo = est_date(n)
        if items:                                # 有實際年月就用多數決那個
            real = [(i["year"], i["month"]) for i in items if not i["dateEstimated"]]
            if real:
                y, mo = max(set(real), key=real.count)
        issues.append({"issue": n, "year": y, "month": mo,
                       "count": len(items), "items": items})

    data = {
        "journal": "聖書之研究",
        "journalOriginal": "聖書之研究",
        "slug": "uchimura",
        "founded": "1900-09", "ended": "1930-04",
        "totalIssues": LAST_ISSUE,
        "totalItems": sum(i["count"] for i in issues),
        "issuesWithItems": sum(1 for i in issues if i["count"]),
        "missingIssues": [i["issue"] for i in issues if not i["count"]],
        "source": "《內村鑑三全集》（岩波書店 1932–33）各卷末「內容年譜」",
        "caveat": "全集的年譜只記到篇名、號數與年月，**沒有原刊頁碼**；此處頁碼欄從缺。"
                  "篇名的文字層來自兩份獨立 OCR（archive.org djvu 與本機 MinerU），逐號取抽得較完整的一份，每條的 src 欄記著出處。"
                  "另外，這是「全集所收錄的該號篇目」，不等於該號印出來的完整目次。",
        "issues": issues,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"篇目 {data['totalItems']}（丟掉碎片 {dropped}）｜有篇目的號 "
          f"{data['issuesWithItems']}／{LAST_ISSUE}｜缺 {len(data['missingIssues'])}")
    print(f"→ {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
