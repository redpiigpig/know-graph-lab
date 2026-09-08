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
4. 🚨 **字形送錯會靜默回 0 筆**，跟「真的沒有」長得一模一樣。查「矢內原忠雄」
   得 0、查「矢内原忠雄」得 41 —— 差別只在舊字體 內／新字體 内。NDL 的作者欄
   一律新字體，但我們的書目是舊字體。現在會自動兩種字形都查再合併，
   `--strict` 可關掉。日後新增作者若回 0，**先確認字形再下結論**。

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


# 人名裡會出現的舊字體→新字體。NDL 作者欄一律新字體，我們的書目是舊字體，
# 送錯的下場是靜默 0 筆（見模組 docstring 第 4 點）。
SHINJITAI = str.maketrans(
    "內澤齋濱邊學國廣榮惠淸曾眞德瀨齊龍兒圓應假藝辨嶋槇彌樂圀顯壽禮"
    "萬與亞區單嚴據櫻澁溫獨當體歸戀鐵斷寫壯藏爲鄕縣關驛"
    "豐彥淺賴郞條稻拜續團醫覺觀讀變辭舊燈發惡賣譯麥黑步每增拂卽敎靑戶莊拔",
    "内沢斎浜辺学国広栄恵清曽真徳瀬斉竜児円応仮芸弁島槙弥楽国顕寿礼"
    "万与亜区単厳拠桜渋温独当体帰恋鉄断写壮蔵為郷県関駅"
    "豊彦浅頼郎条稲拝続団医覚観読変辞旧灯発悪売訳麦黒歩毎増払即教青戸荘抜")


def name_variants(name: str) -> list:
    """[原樣, 新字體]（同形就只有一個）。"""
    shin = name.translate(SHINJITAI)
    return [name] if shin == name else [name, shin]


def search_author(name: str, cap: int = 600, strict: bool = False) -> list:
    """翻完搜尋結果，回傳 responsibility 真的是這位作者的條目（依 id 去重）。

    預設把舊／新字體兩種寫法都查過再合併，因為兩邊都可能只命中一半。
    """
    import requests
    names = [name] if strict else name_variants(name)
    targets = [norm_name(n) for n in names]
    seen, out = set(), []
    for q in names:
        frm = 0
        while frm < cap:
            r = requests.get(SEARCH_API, params={"keyword": q, "size": 100, "from": frm},
                             timeout=60, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            d = r.json()
            lst = d.get("list") or []
            if not lst:
                break
            for e in lst:
                resp = norm_name(e.get("responsibility"))
                if not any(t in resp for t in targets):
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
    ap.add_argument("--strict", action="store_true",
                    help="只查你給的字形，不自動加查新字體")
    args = ap.parse_args()

    names = [args.author] if args.strict else name_variants(args.author)
    if len(names) > 1:
        print("字形變體：%s（NDL 作者欄用新字體）" % "／".join(names))
    items = search_author(args.author, strict=args.strict)
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
