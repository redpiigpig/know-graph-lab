#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""盤點玄奘大學圖書館訂了哪些電子資料庫與電子期刊平台。

目的是替未來的排程下載列一份**可下載清單**：哪些庫真的訂了、要不要綁校內 IP、
有沒有全文、涵蓋哪些學科。使用者是玄奘的博士生，機構身分只有在校內網段才驗得過
（[[research-data-airiti]] 那條排程踩過「人在學校時筆電用電池，排程預設不啟動」的坑）。

⚠️ 玄奘圖書館的資料庫清單在 webopac 的「特色館藏」底下，分「外文資料庫」「中文資料庫」
「電子書」三類，而那三個連結是 **ASP.NET postback**（`javascript:__doPostBack(...)`），
不是普通網址——直接 curl 那頁只會拿到分類名稱，拿不到清單。要帶著
`__VIEWSTATE`／`__VIEWSTATEGENERATOR`／`__EVENTVALIDATION` 回 POST。

輸出 `data/research-data/hcu-eresources.json`（進版控，是策展清單不是大檔）。

用法：
  python scripts/hcu_eresources.py            # 盤點並寫檔
  python scripts/hcu_eresources.py --list     # 只印出來看
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "research-data" / "hcu-eresources.json"

BASE = "https://hculibrary.hcu.edu.tw/webopac/Tsgc.aspx?dc=5&fc=1&n=5"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
      "Accept-Language": "zh-TW,zh;q=0.9"}
TAG = re.compile(r"<[^>]+>")


def text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", s))).strip()


def hidden(page: str) -> dict:
    """抓 ASP.NET 的三個隱藏欄位。少一個就會被伺服器判成無效回傳。"""
    out = {}
    for name in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION",
                 "__VIEWSTATEENCRYPTED", "__PREVIOUSPAGE"):
        m = re.search(r'id="' + name + r'"[^>]*value="([^"]*)"', page)
        if m:
            out[name] = html.unescape(m.group(1))
    return out


def categories(page: str) -> dict[str, str]:
    """分類名 → postback 的 target（ctl00$...$LinkButton1）。"""
    out = {}
    for m in re.finditer(
            r"""<a[^>]+href="javascript:__doPostBack\('([^']+)','[^']*'\)"[^>]*>(.*?)</a>""",
            page, re.S):
        name = text(m.group(2))
        if name:
            out[name] = m.group(1)
    return out


def postback(s: requests.Session, page: str, target: str, arg: str = "") -> str:
    """送一次 postback。

    ⚠️ 翻頁跟點分類不一樣：分類是換 `__EVENTTARGET`，翻頁是 target 固定為
    `…$AspNetPager1` 而把**頁碼放進 `__EVENTARGUMENT`**。把頁碼當 target 找，
    會一直找不到「下一頁」而默默只收第一頁。
    """
    data = hidden(page)
    data["__EVENTTARGET"] = target
    data["__EVENTARGUMENT"] = arg
    r = s.post(BASE, data=data, headers={**UA, "Referer": BASE}, timeout=60)
    r.encoding = "utf-8"   # ⚠️ 別用 apparent_encoding，它把這頁猜成西里爾字集
    return r.text


# ⚠️ 別拿 `<td class="hidden">MARC…</td>` 當列的錨點：那一格只出現在 50 列裡的 16 列，
# 於是清單默默只剩三分之一，而畫面與程式都不會抱怨。每一列一定有的是題名那個
# postback 連結（id 以 lbtgcd2 結尾），拿它當錨點才完整。
TITLE_A = re.compile(r'<a[^>]*id="[^"]*lbtgcd2"[^>]*>(.*?)</a>', re.S)
YEAR = re.compile(r">(\d{4})<")
PAGER = re.compile(r"__doPostBack\('([^']*AspNetPager\d*)','(\d+)'\)")
SORT = re.compile(r"__doPostBack\('([^']*\$dg)','(Sort\$[A-Za-z0-9]+)'\)")


def parse_list(page: str) -> list[dict]:
    """一頁的清單。

    ⚠️ 條目的連結是 postback 不是外部網址——這個 OPAC 在清單頁不給資料庫的真正入口，
    要再點進書目才有。所以這裡只收「館方有哪些紀錄、哪一年建檔」。
    """
    rows, marks = [], [m for m in TITLE_A.finditer(page)]
    for i, m in enumerate(marks):
        name = text(m.group(1))
        for junk in ("[電子資源]", "[ 電子資源 ]", "[電子書]", "[ 電子書 ]"):
            name = name.replace(junk, "")
        name = name.strip(" /.:")
        tail = page[m.end(): marks[i + 1].start() if i + 1 < len(marks) else m.end() + 900]
        y = YEAR.search(tail)
        if name:
            rows.append({"name": name, "year": y.group(1) if y else None})
    return rows


def collect(s: requests.Session, first: str) -> list[dict]:
    """把一類收完。

    ⚠️ **這個 OPAC 的分頁翻不過去**：pager 的 postback（target 是 …$AspNetPager1、
    頁碼放 `__EVENTARGUMENT`）送出去之後，回來的頁面掉了查詢狀態，一列都沒有。
    而一頁只出 50 筆，外文資料庫有 69 筆——照單全收就會**默默少 19 筆**。

    繞法是換排序：表頭每一欄都能 postback 重排（`Sort$cata12` 之類），排序一換，
    第一頁那 50 筆就換一批。把每一種排序的第一頁聯集起來，只要總數不超過
    50×排序數就收得全。收完會比對「查詢條列數」那個數字，不足就明講。
    """
    rows = parse_list(first)
    m = re.search(r"查詢條列數[:：]\s*(\d+)", text(first))
    expect = int(m.group(1)) if m else None

    tried = set()
    for sm in SORT.finditer(first):
        key = sm.group(2)
        if key in tried:
            continue
        tried.add(key)
        for _ in range(2):          # 同一欄送兩次＝升冪與降冪
            page = postback(s, first, sm.group(1), key)
            rows += parse_list(page)
        if expect and len({r["name"] for r in rows}) >= expect:
            break

    seen, out = set(), []
    for r in rows:
        if r["name"] in seen:
            continue
        seen.add(r["name"]); out.append(r)
    if expect and len(out) < expect:
        print(f"  ⚠️ 館方說有 {expect} 筆，只湊到 {len(out)} 筆（分頁翻不過去，換排序也沒補齊）",
              file=sys.stderr)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    s = requests.Session()
    r = s.get(BASE, headers=UA, timeout=60)
    # ⚠️ 這站沒在標頭宣告編碼，requests 的 apparent_encoding 會把中文猜成西里爾字集，
    # 於是「外文資料庫」變成「еӨ–ж–ҮиіҮж–ҷеә«」，分類一個都對不上而程式不報錯。
    r.encoding = "utf-8"
    page = r.text

    cats = categories(page)
    want = [c for c in cats if "資料庫" in c or "電子書" in c]
    print(f"特色館藏分類 {len(cats)} 個，其中電子資源相關 {len(want)} 個：{'、'.join(want)}")

    result = {}
    for name in want:
        sub = postback(s, page, cats[name])
        rows = collect(s, sub)
        result[name] = rows
        print(f"\n── {name}：{len(rows)} 筆")
        for x in rows:
            print(f"    {x['year']}  {x['name'][:64]}")

    if args.list:
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": BASE,
        "note": "玄奘大學圖書館 webopac 特色館藏底下的電子資源清單；多數需校內 IP 或帳號",
        "caveat": "⚠️ 這個 OPAC 一頁只給 50 筆，而分頁與換排序的 postback 回來都掉查詢狀態，"
                  "所以每一類都只收得到前 50 筆。館方自報的總數見各類的 expect 欄，"
                  "差額要用有頭瀏覽器（Playwright）才補得齊。",
        "categories": {k: {"listed": len(v), "items": v} for k, v in result.items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
