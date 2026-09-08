# -*- coding: utf-8 -*-
"""盤點某位作者在 NDL 有哪些**インターネット公開**的數位化本。

    python scripts/ndl_author_survey.py 畔上賢造

🚨 三個坑：

1. `/dl/api/book/search?keyword=` 是**全文檢索**，關鍵詞出現在別人書的內文
   也會回來（查「畔上賢造」445 筆，實際著作只有一小部分）。一定要再用
   `responsibility` 欄過濾。
2. NDL 的作者欄格式不一（`畔上賢造 [著]`／`畔上賢造 訳註`／`藤井, 武, 1888-1930`），
   比對前要把空白、逗號都去掉，否則必然 0 筆。
3. **公開範圍只能靠 IIIF manifest 判**（200＝公開／404＝館內限定），
   書誌 metadata 不帶這個欄位。「圖書館‧個人送信」境外不能用，不算公開。

見 .claude/skills/ebook-collected-works/ndl_open_scans.md。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import ndl_build as nb  # noqa: E402

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SEARCH_API = "https://lab.ndl.go.jp/dl/api/book/search"


def norm_name(s: str) -> str:
    """作者欄比對用：空白與逗號全去掉（NDL 的格式很不一致）。"""
    return re.sub(r"[\s　,，]", "", s or "")


def search_author(name: str, cap: int = 600) -> list:
    """翻完搜尋結果，回傳 responsibility 真的是這位作者的條目（依 id 去重）。"""
    import requests
    seen, out, frm = set(), [], 0
    target = norm_name(name)
    while frm < cap:
        r = requests.get(SEARCH_API, params={"keyword": name, "size": 100, "from": frm},
                         timeout=60, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        d = r.json()
        lst = d.get("list") or []
        if not lst:
            break
        for e in lst:
            if target not in norm_name(e.get("responsibility")):
                continue
            if e["id"] in seen:
                continue
            seen.add(e["id"])
            out.append(e)
        if frm + 100 >= int(d.get("hit") or 0):
            break
        frm += 100
        time.sleep(0.5)          # NDL 是公共資源，節流
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("author")
    ap.add_argument("--out", default=None, help="把公開清單寫成 JSON")
    args = ap.parse_args()

    items = search_author(args.author)
    print("%s：responsibility 相符 %d 筆，逐筆驗公開範圍…\n" % (args.author, len(items)))

    public = []
    for e in sorted(items, key=lambda x: str(x.get("published") or "")):
        ok = nb.is_open(e["id"])
        time.sleep(0.3)
        mark = "✅公開" if ok else "⛔限定"
        print("  %s %-9s %-30s %-6s %-16s %s頁"
              % (mark, e["id"], (e.get("title") or "")[:28],
                 e.get("published") or "—", (e.get("publisher") or "")[:14],
                 e.get("page") or "?"))
        if ok:
            public.append({"pid": e["id"], "title": e.get("title"),
                           "published": e.get("published"),
                           "publisher": e.get("publisher"), "pages": e.get("page"),
                           "responsibility": e.get("responsibility")})

    print("\n公開 %d／共 %d 筆" % (len(public), len(items)))
    if args.out:
        Path(args.out).write_text(
            json.dumps(public, ensure_ascii=False, indent=1), encoding="utf-8")
        print("→ %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
