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


def postback(s: requests.Session, page: str, target: str) -> str:
    data = hidden(page)
    data["__EVENTTARGET"] = target
    data["__EVENTARGUMENT"] = ""
    r = s.post(BASE, data=data, headers={**UA, "Referer": BASE}, timeout=60)
    r.encoding = "utf-8"   # ⚠️ 別用 apparent_encoding，它把這頁猜成西里爾字集
    return r.text


def parse_list(page: str) -> list[dict]:
    """一類底下的資料庫清單。條目是連到外部網址的連結。"""
    rows, seen = [], set()
    for m in re.finditer(r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>', page, re.S):
        url, name = html.unescape(m.group(1)), text(m.group(2))
        if not name or len(name) < 3:
            continue
        if "hcu.edu.tw" in url and "webopac" in url:
            continue
        if (name, url) in seen:
            continue
        seen.add((name, url))
        rows.append({"name": name, "url": url})
    return rows


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
        rows = parse_list(sub)
        result[name] = rows
        print(f"\n── {name}：{len(rows)} 筆")
        for x in rows:
            print(f"    {x['name'][:52]:54s} {x['url'][:58]}")

    if args.list:
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": BASE,
        "note": "玄奘大學圖書館 webopac 特色館藏底下的電子資源清單；多數需校內 IP 或帳號",
        "categories": result,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n→ {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
