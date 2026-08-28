# -*- coding: utf-8 -*-
"""替博士論文蒐集**參考書目**：華藝線上圖書館的檢索結果彙整成清單。

只收書目（題名／作者／出處／年／頁碼／是否 OpenAccess／連結），不下載全文——
華藝多數內容需訂閱，全文取用另循合法管道（學校圖書館）。

華藝的檢索是把一整包 JSON 塞進網址的 queryString，本檔負責構造那包 JSON；
結果頁是 JS 渲染，所以用 playwright 取。

臺灣博碩士論文加值系統（ndltd.ncl.edu.tw）**不做程式化抓取**：全站掛驗證碼
（連檢索頁都有 validinput），要人工過驗證，故本流程不含它——改由使用者以
本檔產出的關鍵詞人工查詢，或到館用館內資料庫。

index：public/content/research-data/pct/biblio-airiti.json

  python -X utf8 scripts/biblio_search.py --search          # 跑內建詞表
  python -X utf8 scripts/biblio_search.py --search --query "王憲治 鄉土神學"
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "public/content/research-data/pct/biblio-airiti.json"
# 必須放 repo 內執行，否則 node 找不到 playwright
NODE_SCRIPT = Path(__file__).resolve().parents[1] / ".airiti_fetch.mjs"

# 依論文七章的需要編的檢索詞；每條對應一個章節任務
QUERIES = [
    ("黃彰輝 實況化", "第四章第二節"),
    ("宋泉盛 故事神學", "第四章第三節"),
    ("王憲治 鄉土神學", "第四章第四節"),
    ("黃伯和 出頭天", "第四章第五節"),
    ("長老教會 公共神學", "第四章"),
    ("長老教會 人權宣言", "第四章第一節"),
    ("傳道法師 妙心寺", "第三章第三節"),
    ("昭慧 佛教倫理", "第三章第四節"),
    ("印順 人間佛教 公共", "第三章第二節"),
    ("太虛 人生佛教", "第三章第一節"),
    ("佛教 基督教 對話 台灣", "第六章"),
    ("無教會主義 台灣", "第二章日本線"),
]

JS_TEMPLATE = r"""
import { chromium } from 'playwright'
const queries = JSON.parse(process.argv[2])
const b = await chromium.launch()
const p = await b.newPage()
const out = []
for (const [q, note] of queries) {
  try {
    await p.goto('https://www.airitilibrary.com/', { waitUntil: 'domcontentloaded', timeout: 90000 })
    await p.waitForTimeout(1800)
    const box = await p.$('input[type="text"], input[type="search"]')
    await box.fill(q)
    await box.press('Enter')
    await p.waitForTimeout(7000)
    const url = p.url()
    const text = await p.locator('body').innerText()
    out.push({ query: q, note, url, text })
    console.error(`  ${q}: 取得結果頁`)
  } catch (e) {
    out.push({ query: q, note, error: String(e).slice(0, 120), text: '' })
    console.error(`  ${q}: FAIL`)
  }
}
console.log(JSON.stringify(out))
await b.close()
"""


# 結果頁的一筆長這樣（純文字）：
#   期刊 / 學位論文        ← 類型行
#   拯救與創造：…〈人權宣言〉…  ← 題名
#   蔡銘偉(Ming-Wei Tsai)   ← 作者
#   《神學與教會》 46卷2期&47卷1期 (2022 / 01) Pp. 79-101   ← 出處
#   （其後為摘要片段，到下一個「全文下載」為止）
KIND_RE = re.compile(r"^\s*(期刊|學位論文|會議論文|專書|電子書|報紙)\s*$")
SRC_RE = re.compile(r"《.+?》|學位論文\s*\(\d{4}\)|\(\d{4}\s*/\s*\d{1,2}\)")


def parse_results(text: str):
    lines = [l.strip() for l in (text or "").split("\n")]
    rows, i = [], 0
    while i < len(lines):
        if not KIND_RE.match(lines[i]):
            i += 1
            continue
        kind = lines[i].strip()
        # 類型行之後，跳過空行與 OpenAccess 標記，取題名／作者／出處
        j, got = i + 1, []
        while j < len(lines) and len(got) < 3 and j - i < 8:
            l = lines[j]
            if l and l != "OpenAccess":
                got.append(l)
            j += 1
        if len(got) >= 3:
            title, author, source = got[0], got[1], got[2]
            if SRC_RE.search(source):
                rows.append({"kind": kind, "title": title, "author": author, "source": source})
        i = j
    # 同一頁可能重複列出，去重
    seen, uniq = set(), []
    for r in rows:
        k = (r["title"], r["source"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq



def run(queries):
    NODE_SCRIPT.write_text(JS_TEMPLATE, encoding="utf-8")
    repo = Path(__file__).resolve().parents[1]
    r = subprocess.run(["node", str(NODE_SCRIPT), json.dumps(queries, ensure_ascii=False)],
                       cwd=repo, capture_output=True, text=True, encoding="utf-8", timeout=1800)
    sys.stderr.write(r.stderr or "")
    if not r.stdout.strip():
        raise SystemExit("華藝檢索沒有回傳結果")
    return json.loads(r.stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--query")
    args = ap.parse_args()
    if not args.search:
        ap.print_help()
        return
    qs = [[args.query, "自訂"]] if args.query else [[q, n] for q, n in QUERIES]
    raw = run(qs)
    data = []
    for g in raw:
        items = parse_results(g.get("text", ""))
        data.append({"query": g["query"], "note": g["note"], "url": g.get("url", ""),
                     "count": len(items), "items": items})
        print(f"  {g['query']}：{len(items)} 筆")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(d["items"]) for d in data)
    print(f"{len(data)} 組檢索 / {total} 筆書目 → {OUT}")


if __name__ == "__main__":
    main()
