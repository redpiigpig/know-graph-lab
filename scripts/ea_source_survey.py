# -*- coding: utf-8 -*-
"""東亞本土神學：公有領域著作的取源可得性盤點（只回報，不下載）。

26 位裡有 43 筆在版權內（依榮格前例 hub＋書目先行，**不該收全文**），
真正「可以收但還沒收」的是 24 筆、集中在七位公有領域作者。
這支逐筆去問來源站有沒有，產出一張表給使用者決定投不投。

🚨 **只看命中數會被騙，一定要把命中的題名印出來。**
第一版就是這樣廢掉的：
  * NDL 的 `hit` 在**回應頂層**不在 `data` 底下，路徑寫錯 → 全部回 0，
    但《死線を越えて》其實有 6 個公開版本。
  * archive.org 預設是全文模糊檢索，逐字都算命中 →「中華歸主」回 22,070 筆、
    「教會的正統」27,704 筆，全是雜訊。要用 `title:("…")` 限定題名欄位。

    python scripts/ea_source_survey.py --who 賀川豐彥
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (knowledge-graph-lab research survey)"}

# (作者, 卒年, 著作, 查詢用題名們)
# 題名要給多個寫法（繁／簡／英／日）—— 各站收錄的寫法不一。
WORKS = [
    ("吳雷川", 1944, "基督教與中國文化", ["基督教與中國文化", "基督教与中国文化"]),
    ("吳雷川", 1944, "基督徒的希望", ["基督徒的希望"]),
    ("吳雷川", 1944, "墨翟與耶穌", ["墨翟與耶穌", "墨翟与耶稣"]),
    ("吳雷川", 1944, "真理週刊", ["真理週刊", "真理周刊"]),
    ("誠靜怡", 1939, "中華基督教會年鑑", ["中華基督教會年鑑", "中华基督教会年鉴"]),
    ("誠靜怡", 1939, "中華歸主", ["The Christian Occupation of China", "中華歸主"]),
    ("誠靜怡", 1939, "愛丁堡大會發言", ["World Missionary Conference 1910"]),
    ("賈玉銘", 1964, "神道學", ["神道學", "神道学"]),
    ("賈玉銘", 1964, "聖經要義", ["聖經要義", "圣经要义"]),
    ("賈玉銘", 1964, "新舊約全書註釋", ["新舊約全書註釋", "新旧约全书注释"]),
    ("賈玉銘", 1964, "靈交詩歌", ["靈交詩歌", "灵交诗歌"]),
    ("賈玉銘", 1964, "得勝詩歌", ["得勝詩歌", "得胜诗歌"]),
    ("賈玉銘", 1964, "聖徒心聲", ["聖徒心聲", "圣徒心声"]),
    ("劉廷芳", 1947, "普天頌讚", ["普天頌讚", "Hymns of Universal Praise"]),
    ("劉廷芳", 1947, "生命月刊", ["生命月刊"]),
    ("劉廷芳", 1947, "紫晶", ["紫晶"]),
    ("倪柝聲", 1972, "屬靈人", ["屬靈人", "The Spiritual Man"]),
    ("倪柝聲", 1972, "正常的基督徒生活", ["The Normal Christian Life"]),
    ("倪柝聲", 1972, "教會的正統", ["教會的正統", "The Orthodoxy of the Church"]),
    ("李龍道", 1933, "李龍道日記", ["이용도 일기", "李龍道日記"]),
    ("李龍道", 1933, "李龍道書簡集", ["이용도 서간집", "李龍道書簡集"]),
    ("賀川豐彥", 1960, "死線を越えて", ["死線を越えて"]),
    ("賀川豐彥", 1960, "一粒の麦", ["一粒の麦"]),
    ("賀川豐彥", 1960, "愛の科学", ["愛の科学"]),
]


def ndl_search(title: str, author: str = "") -> list:
    """NDL 檢索 → [(pid, 題名, 年, 責任者)]。

    🚨 這是**全文檢索**，關鍵詞出現在別人書的內文也會回來，所以要自己再比對題名。
    """
    try:
        r = requests.get("https://lab.ndl.go.jp/dl/api/book/search",
                         params={"keyword": title, "size": 30}, headers=UA, timeout=40)
        d = r.json()
    except Exception:
        return []
    out = []
    key = title.replace(" ", "")
    for w in (d.get("list") or []):
        t = (w.get("title") or "").replace(" ", "")
        if key not in t:                       # 題名對不上＝內文命中，不算
            continue
        out.append((w.get("id"), w.get("title"), w.get("published"),
                    w.get("responsibility") or ""))
    return out


def archive_search(title: str) -> list:
    """archive.org **題名欄位**精確檢索 → [(identifier, 題名, 年)]。"""
    try:
        q = urllib.parse.quote('title:("%s")' % title)
        r = requests.get(
            "https://archive.org/advancedsearch.php"
            f"?q={q}&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=year"
            "&rows=8&page=1&output=json", headers=UA, timeout=40)
        docs = r.json()["response"]["docs"]
    except Exception:
        return []
    return [(d.get("identifier"), d.get("title"), d.get("year")) for d in docs]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--who", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = []
    for who, died, work, titles in WORKS:
        if args.who and args.who != who:
            continue
        ndl, ia = [], []
        for t in titles:
            ndl += ndl_search(t, who)
            ia += archive_search(t)
            time.sleep(0.7)                    # 公共資源，節流
        seen = set()
        ndl = [x for x in ndl if not (x[0] in seen or seen.add(x[0]))]
        seen = set()
        ia = [x for x in ia if not (x[0] in seen or seen.add(x[0]))]
        rows.append({"author": who, "died": died, "work": work,
                     "ndl": ndl, "archive": ia})
        mark = "✅" if (ndl or ia) else "❌"
        print("\n%s %s《%s》 NDL %d ／ archive.org %d" % (mark, who, work, len(ndl), len(ia)))
        for pid, t, y, resp in ndl[:4]:
            print("     NDL %-9s %-4s %-26s %s" % (pid, y, (t or "")[:24], resp[:18]))
        for ident, t, y in ia[:4]:
            tt = t if isinstance(t, str) else str(t)
            print("     IA  %-26s %-6s %s" % ((ident or "")[:26], y or "", tt[:34]))

    if args.out:
        json.dump(rows, open(args.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print("\n→", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
