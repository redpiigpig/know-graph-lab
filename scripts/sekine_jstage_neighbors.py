# -*- coding: utf-8 -*-
"""替 sekine_data/jstage_articles.json 每一篇補上「同頁的鄰篇」。

J-STAGE 的 PDF 是整頁切的：一篇書評若從第 77 頁中段開始，PDF 第一頁的上半
其實是前一篇的結尾；結束在第 94 頁中段，PDF 最後一頁的下半是下一篇的開頭。
不處理的話，那些別人的文字會以「這一篇的第一段／最後一段」的身分被翻譯、上架
（實測：Beer–Meyer《希伯來文法》書評的第一段是另一篇法文語意學書評的結尾）。

做法是查該期的**完整篇目**（J-STAGE API，cdjournal＋vol＋no），找出
  prev_title：結束頁＝本篇起始頁的那一篇
  next_title：起始頁＝本篇結束頁的那一篇
寫回 JSON。切的時候拿這兩個標題去本篇段落裡定位（sekine_build.trim_neighbors）。

  python -X utf8 scripts/sekine_jstage_neighbors.py
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
META = (Path(__file__).resolve().parent.parent / ".claude" / "skills" / "ebook-collected-works"
        / "sekine_data" / "jstage_articles.json")


def issue_articles(cd: str, vol: str, no: str) -> list[dict]:
    q = {"service": 3, "cdjournal": cd, "vol": vol, "count": 1000}
    if no:
        q["no"] = no
    url = "https://api.jstage.jst.go.jp/searchapi/do?" + urllib.parse.urlencode(q)
    t = urllib.request.urlopen(url, timeout=60).read().decode("utf-8")
    t = t.replace("<![CDATA[", "").replace("]]>", "")
    out = []
    for e in re.findall(r"(?s)<entry>(.*?)</entry>", t):
        def g(p):
            m = re.search(p, e, re.S)
            return html.unescape(re.sub(r"<[^>]+>|\s+", " ", m.group(1))).strip() if m else ""
        out.append({"title": g(r"<article_title>(.*?)</article_title>"),
                    "no": g(r"<prism:number>(.*?)</prism:number>"),
                    "sp": g(r"<prism:startingPage>(.*?)</prism:startingPage>"),
                    "ep": g(r"<prism:endingPage>(.*?)</prism:endingPage>"),
                    "doi": g(r"<prism:doi>(.*?)</prism:doi>")})
    return out


def main() -> None:
    d = json.loads(META.read_text(encoding="utf-8"))
    cache: dict[tuple, list] = {}
    for group in ("by", "about"):
        for r in d[group]:
            key = (r["cd"], r["vol"], r["no"])
            if key not in cache:
                cache[key] = issue_articles(*key)
                time.sleep(1)
            others = [a for a in cache[key] if a["doi"] != r["doi"] and a["no"] == r["no"]]
            r["prev_title"] = next((a["title"] for a in others if a["ep"] and a["ep"] == r["sp"]), "")
            r["next_title"] = next((a["title"] for a in others if a["sp"] and a["sp"] == r["ep"]), "")
            flag = ("←" if r["prev_title"] else " ") + ("→" if r["next_title"] else " ")
            print(f"{flag} {r['year']} {r['title'][:40]}")
    META.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("issues:", len(cache))


if __name__ == "__main__":
    main()
