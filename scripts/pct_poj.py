# -*- coding: utf-8 -*-
"""《台灣府城教會報》→《台灣教會公報》白話字全文（1885–1969）收錄 pipeline。

補的是 tcnn（2010-12 起）之前那一大截：長老教會自己的機關報，從 1885 年巴克禮創刊
到 1969 年改出華文為止，八十四年全以白話字書寫。這一段正好是論文第二章與第四章前段
最缺的史料——黃彰輝那一代之前，長老教會在公共領域說了什麼，只能從這裡看。

來源是師大台文所「台灣白話字文獻館」（2007–2010 數位典藏國家型計畫）的 GitHub 鏡像
`Taiwanese-Corpus/Khin-hoan_2010_pojbh` 的 `pojbh.json`。

🚨 這是**選輯不是全份**。中研院語言學研究所另有 1885–1969 逐頁掃描並輸入的完整閩語
   資料庫（數位典藏編號 LAMINTX0008），但那批要去信 ilsecretariat@sinica.edu.tw
   談授權，站上沒有下載。不要把本批說成「教會公報全收了」。
🚨 **只收文字不收圖片**。README 載明文字採 CC 授權，圖片則是另向台灣教會公報社、
   長老教會教會歷史委員會、真理大學牛津學堂、淡江中學校史館授權的——不是我們的。
   （同臺灣記憶那批的規矩。）

每篇有兩種寫法：漢羅（漢字＋白話字混寫）與台羅（全羅馬字）。兩種都存，reader 兩欄對照。

R2：pct-fulltext/poj/<年代>.jsonl（按十年打包；逐篇一個小檔會讓語料層掃描慢一個
    數量級——論壇報那兩萬多個小檔的教訓）
index：public/content/research-data/pct/poj-index.json（各年代篇數字數）
       public/content/research-data/pct/poj-articles.json（篇目，不含全文）

  python -X utf8 scripts/pct_poj.py --fetch      # 抓 pojbh.json
  python -X utf8 scripts/pct_poj.py --build      # 打包上 R2 並產 index
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dadaodao_fulltext as df  # noqa: E402

SRC_URL = ("https://raw.githubusercontent.com/Taiwanese-Corpus/"
           "Khin-hoan_2010_pojbh/master/pojbh.json")
SRC = Path(r"C:/tmp/pojbh.json")
R2_PREFIX = "pct-fulltext/poj"
OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/pct"

# 篇名一律是「漢字 [ Pe̍h-oē-jī ]」，作者多半是「漢字 Pe̍h-oē-jī」
TITLE_RE = re.compile(r"^(.*?)\s*\[\s*(.*?)\s*\]\s*$")
YEAR_RE = re.compile(r"^(\d{4})")


def split_title(raw: str):
    """→ (漢字題名, 白話字題名)。抓不到括號就整串當漢字題名。"""
    m = TITLE_RE.match((raw or "").strip())
    return (m.group(1).strip(), m.group(2).strip()) if m else ((raw or "").strip(), "")


def decade_of(date: str) -> str:
    """→ '1880'…'1960'，或 '未詳'。

    🚨 日期只到「年/月」，且有 17 筆寫「不詳」。不詳一律歸到自己那一桶，
    不做任何內插——這批刊期本來就不規則（週刊、月刊、合刊都有）。
    """
    m = YEAR_RE.match((date or "").strip())
    return f"{int(m.group(1)) // 10 * 10}" if m else "未詳"


def fetch():
    SRC.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(SRC_URL, timeout=300)
    r.raise_for_status()
    SRC.write_bytes(r.content)
    print(f"{SRC}：{len(r.content):,} bytes")


def build():
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    by_dec, arts = defaultdict(list), []
    for r in rows:
        han = "\n".join(r.get("hanlo") or []).strip()
        tai = "\n".join(r.get("tailo") or []).strip()
        if not han and not tai:
            continue                     # 只有書目沒有全文的那幾十筆不收
        title, title_poj = split_title(r.get("篇名"))
        dec = decade_of(r.get("日期"))
        rec = {
            "id": r["pianho"],
            "mag": (r.get("刊名") or "").strip(),
            "date": (r.get("日期") or "").strip(),
            "issue": (r.get("卷期") or "").strip(),
            "page": (r.get("頁數") or "").strip(),
            "author": (r.get("作者") or "").strip(),
            "title": title,
            "titlePoj": title_poj,
        }
        by_dec[dec].append({**rec, "hanlo": han, "tailo": tai})
        arts.append({**rec, "decade": dec, "chars": len(han)})

    index = []
    for dec in sorted(by_dec, key=lambda d: (d == "未詳", d)):
        items = by_dec[dec]
        body = "\n".join(json.dumps(x, ensure_ascii=False) for x in items)
        df.r2_put_text(f"{R2_PREFIX}/{dec}.jsonl", body)
        chars = sum(len(x["hanlo"]) for x in items)
        index.append({"decade": dec, "count": len(items), "chars": chars})
        print(f"  {dec}：{len(items)} 篇 / {chars:,} 字", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "poj-index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    arts.sort(key=lambda x: (x["date"] or "9999", x["id"]))
    (OUT / "poj-articles.json").write_text(
        json.dumps(arts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(arts)} 篇 / {sum(x['chars'] for x in index):,} 字（漢羅）"
          f" → {OUT / 'poj-index.json'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--build", action="store_true")
    args = ap.parse_args()
    if args.fetch:
        fetch()
    if args.build:
        build()
    if not (args.fetch or args.build):
        ap.print_help()


if __name__ == "__main__":
    main()
