#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓法鼓文理學院「佛學術語字辭典」（DILA Glossaries）的辭書資料。

**為什麼是這個來源**：使用者問佛光大辭典與相關漢文辭典該不該全文轉錄。查下來的實情是
三段不同的答案：

  一、**漢傳古代辭書早就在站上了**，它們本來就在大正藏事彙部，已隨 CBETA 全量收錄：
      《一切經音義》T2128（100 卷 38,384 段）、《續一切經音義》T2129、《翻梵語》T2130、
      《翻譯名義集》T2131、《釋氏要覽》T2127、《法界次第初門》T1925，合計約 4.9 萬段。
  二、**近現代辭典館內一本都沒有**，而其中最重要的丁福保《佛學大辭典》（1922，三萬餘條、
      360 餘萬字）**原文是公有領域**，法鼓的 TEI P5 版採 CC BY-SA 2.5 台灣，可直接下載。
  三、佛光大辭典（1988）與中華佛教百科全書（1994）**仍在版權期內**，另外決定。

這支處理第二段。DILA 這裡共 15 部，除丁福保外還有蘇慧廉—何樂益《中國佛教術語辭典》、
《翻譯名義大集》、《五譯合璧集要》、《南山律學辭典》，以及竺法護／鳩摩羅什／支婁迦讖
三種譯經的逐詞詞典——最後那幾部對比較譯語特別有用。

⚠️ **各部的授權不一樣**，不要一體看待：丁福保原文公有領域＋TEI 版 CC BY-SA；
其餘幾部要逐一看頁面上的 licence 欄位，本腳本會把它抓下來存進索引，別跳過。

⚠️ `/download` 這個路徑回 500（站方的頁壞了），真正的檔案在 `/data/<檔名>`，
連結寫在各部自己的頁面裡。

存放：Drive `知識圖工作室/_corpus/dila-glossaries/`（原始壓縮檔）
索引：`data/research-data/dila-glossaries.json`（進版控）

用法：
  python scripts/dila_glossaries_fetch.py --list   # 只列出有哪些、授權為何
  python scripts/dila_glossaries_fetch.py          # 抓（可重跑，跳過已有的）
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = Path("G:/我的雲端硬碟/資料/知識圖工作室/_corpus/dila-glossaries")
INDEX = ROOT / "data" / "research-data" / "dila-glossaries.json"

BASE = "https://glossaries.dila.edu.tw"
UA = {"User-Agent": "kglab-research/1.0 (academic corpus building)"}
DELAY = 1.5
TAG = re.compile(r"<[^>]+>")
# 偏好順序：TEI 是結構化的，其餘是給查詢軟體用的封裝格式
PREFER = ["tei", "xml", "htm", "gls", "bgl"]


def get(url: str, timeout: int = 90) -> bytes:
    return urllib.request.urlopen(
        urllib.request.Request(url, headers=UA), timeout=timeout).read()


def text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", s))).strip()


def listing() -> list[tuple[str, str]]:
    page = get(f"{BASE}/glossaries?locale=zh-TW").decode("utf-8", "replace")
    out = []
    for m in re.finditer(r'href="/glossaries/([A-Za-z0-9_-]+)\?locale=zh-TW"[^>]*>(.*?)</a>',
                         page, re.S):
        out.append((m.group(1), text(m.group(2))[:90]))
    return out


def detail(code: str) -> dict:
    page = get(f"{BASE}/glossaries/{code}?locale=zh-TW").decode("utf-8", "replace")
    title = text((re.search(r"<h1>(.*?)</h1>", page, re.S) or [None, code])[1]) \
        if re.search(r"<h1>(.*?)</h1>", page, re.S) else code
    # 說明與授權都在 h1 後面那一段 <p> 裡
    body = page.split("<b>下載</b>")[0].split("</h1>", 1)[-1]
    blurb = text(body)
    # ⚠️ 各部的授權措辭差很多，抓不到不等於沒有限制——抓不到要標成 unstated 讓人去看，
    # 不可以預設「沒寫就是自由」。辛嶋靜志那五部寫的是「經作者同意數位化」，
    # 那是授權給法鼓做資料庫，不等於授權我們再散布。
    lic, rights = "", "unstated"
    pats = [
        ("public-domain", r"(public domain[^<]{0,140})"),
        ("cc", r"(licen[sc]ed[^<]{0,200}|Creative Commons[^<)]{0,140})"),
        ("by-permission", r"((?:with|by)\s+(?:the\s+)?(?:kind\s+)?permission[^<]{0,120})"),
    ]
    for tag, pat in pats:
        m = re.search(pat, blurb, re.I)
        if m:
            lic = m.group(1).strip()
            rights = tag
            break
    files = []
    for fm in re.finditer(r"href='(/data/([^']+))'[^>]*>[^<]*</a>\s*</td>\s*<td>\[([^\]]*)\]",
                          page, re.S):
        files.append({"url": BASE + fm.group(1), "name": fm.group(2), "size": fm.group(3)})
    if not files:   # 版面若沒帶大小欄
        for fm in re.finditer(r"href='(/data/([^']+))'", page):
            files.append({"url": BASE + fm.group(1), "name": fm.group(2), "size": ""})
    return {"code": code, "title": title, "blurb": blurb[:700],
            "license": lic, "rights": rights, "files": files}


def pick(files: list[dict]) -> dict | None:
    """挑一個要下載的格式。TEI 優先——它有結構，其餘是查詢軟體的封裝格式。"""
    for key in PREFER:
        for f in files:
            if key in f["name"].lower():
                return f
    return files[0] if files else None


ENTRY = re.compile(r"<entry(?:\s[^>]*)?>(.*?)</entry>", re.S)
FORM = re.compile(r"<form(?:\s[^>]*)?>(.*?)</form>", re.S)
DEF = re.compile(r"<(?:def|quote|cit)(?:\s[^>]*)?>(.*?)</(?:def|quote|cit)>", re.S)
USG = re.compile(r"<usg(?:\s[^>]*)?>(.*?)</usg>", re.S)
SENSE_LANG = re.compile(r'<sense[^>]*xml:lang="([^"]+)"[^>]*>(.*?)</sense>', re.S)
SENSE_ANY = re.compile(r"<sense(?:\s[^>]*)?>(.*?)</sense>", re.S)


def definition_of(body: str, forms: list[str]) -> str:
    """取一條的釋義，分三層回退。

    ⚠️ 各部放釋義的方式不一樣，只認 `<def>` 會讓三部大辭典全部抽成空字串——
    而**條數照樣正確**，所以表面上看起來完全成功：Soothill-Hodous 16,792 條、
    巴漢辭典 10,599 條、長阿含研究 590 條，合計近兩萬八千條只有詞目沒有內容。
    抽查要看「有釋義的比例」，不能只看條數。

      一、`<def>`／`<quote>`／`<cit>`  —— 丁福保、翻譯名義大集、南山律這一型
      二、`<sense>` 的內文（混合內容）—— Soothill-Hodous、巴漢辭典這一型
      三、整條扣掉 `<form>` 之後的內文 —— 長阿含研究那種用 `<p>` 的
    """
    got = " ".join(text(x) for x in DEF.findall(body)).strip()
    if got:
        return got
    got = " ".join(text(x) for x in SENSE_ANY.findall(body)).strip()
    if got:
        return got
    rest = FORM.sub(" ", body)
    return text(rest).strip()


def parse_tei(zip_path: Path) -> list[dict]:
    """把 TEI 詞典拆成一條一筆。

    ⚠️ 壓縮檔裡通常有兩個 .xml：真本與 macOS 的 `__MACOSX/._…` 資源叉。
    後者不是 XML，照著讀會拿到亂碼而且不會報錯——要濾掉。
    """
    with zipfile.ZipFile(zip_path) as z:
        xmls = [n for n in z.namelist()
                if n.lower().endswith(".xml") and "__MACOSX" not in n]
        if not xmls:
            return []
        raw = z.read(max(xmls, key=lambda n: z.getinfo(n).file_size)).decode("utf-8", "replace")
    rows = []
    for m in ENTRY.finditer(raw):
        body = m.group(1)
        forms = [text(x) for x in FORM.findall(body) if text(x)]
        senses = [(lg, text(t)) for lg, t in SENSE_LANG.findall(body) if text(t)]
        if not forms and not senses:
            continue
        if forms:
            rows.append({
                "term": forms[0],
                "variants": forms[1:],
                "domain": [text(x) for x in USG.findall(body) if text(x)],
                "definition": definition_of(body, forms),
            })
        else:
            # ⚠️ 多語對照型的詞典沒有 <form>，詞目分散在各語的 <sense xml:lang>。
            # 《五譯合璧集要》1,071 條（梵藏滿蒙漢）就是這一型——只認 <form> 會
            # 整部判成零條，而零條看起來很像「這個檔不是 TEI」，會查錯方向。
            zh = next((t for lg, t in senses if lg.startswith(("zho", "cmn", "han"))), "")
            rows.append({
                "term": zh or senses[0][1],
                "variants": [t for _, t in senses if t != (zh or senses[0][1])],
                "langs": {lg: t for lg, t in senses},
                "domain": [text(x) for x in USG.findall(body) if text(x)],
                "definition": "",
            })
    return rows


def do_parse() -> int:
    if not INDEX.exists():
        print("先跑一次不帶 --parse 的抓取")
        return 1
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    nl = chr(10)
    total = 0
    for d in idx["rows"]:
        name = d.get("downloaded")
        if not name or not name.lower().endswith(".zip"):
            d["entries"] = 0
            continue
        zp = OUT / name
        if not zp.exists():
            d["entries"] = 0
            continue
        try:
            rows = parse_tei(zp)
        except Exception as e:
            print(f"  {d['code']} 解析失敗 {type(e).__name__}")
            d["entries"] = 0
            continue
        d["entries"] = len(rows)
        total += len(rows)
        if rows:
            out = OUT / f"{d['code']}.jsonl"
            out.write_text(nl.join(json.dumps(r, ensure_ascii=False) for r in rows) + nl,
                           encoding="utf-8")
        flag = "" if rows else "　⚠️ 零條——先確認它是不是 TEI（gls/bgl 是查詢軟體的封裝），再懷疑解析"
        print(f"  {d['code']:6s} {len(rows):>7,} 條  {d['title'][:32]}{flag}")
    INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nl}合計 {total:,} 條 → {OUT}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--parse", action="store_true", help="把已下載的 TEI 拆成 JSONL")
    args = ap.parse_args()

    if args.parse:
        return do_parse()

    rows = []
    for i, (code, name) in enumerate(listing(), 1):
        try:
            d = detail(code)
        except Exception as e:
            print(f"  {code} 取不到：{type(e).__name__}", file=sys.stderr)
            continue
        d["listed_name"] = name
        rows.append(d)
        chosen = pick(d["files"])
        print(f"  {code:6s} {d['title'][:34]:36s} 檔 {len(d['files'])} 種"
              f"　{(chosen or {}).get('name', '—')[:38]}")
        mark = {"public-domain": "公有領域", "cc": "CC 授權",
                "by-permission": "⚠️ 作者授權法鼓數位化（再散布權未明）",
                "unstated": "⚠️ 頁面未載授權，要人工看過"}[d["rights"]]
        print(f"         {mark}　{d['license'][:70]}")
        time.sleep(DELAY)

    if args.list:
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    got = skipped = 0
    for d in rows:
        f = pick(d["files"])
        if not f:
            d["downloaded"] = None
            continue
        target = OUT / f"{d['code']}__{f['name']}"
        if target.exists() and target.stat().st_size > 1024:
            skipped += 1
            d["downloaded"] = target.name
            continue
        try:
            target.write_bytes(get(f["url"], timeout=180))
        except Exception as e:
            print(f"  {d['code']} 下載失敗 {type(e).__name__}")
            d["downloaded"] = None
            continue
        d["downloaded"] = target.name
        d["bytes"] = target.stat().st_size
        got += 1
        print(f"  ↓ {d['code']:6s} {target.name[:46]:48s} {target.stat().st_size/1048576:.2f} MB")
        time.sleep(DELAY)

    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps({
        "source": f"{BASE}/glossaries",
        "note": "法鼓文理學院佛學術語字辭典；各部授權不同，見每一筆的 license 欄",
        "corpus_dir": str(OUT),
        "count": len(rows), "rows": rows,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n下載 {got}／略過 {skipped}（已有）　→ {INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
