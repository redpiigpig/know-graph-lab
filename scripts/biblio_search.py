# -*- coding: utf-8 -*-
"""替博士論文蒐集**參考書目**：華藝線上圖書館的檢索結果彙整成清單。

只收書目（題名／作者／出處／年／頁碼／是否 OpenAccess／連結），不下載全文——
華藝多數內容需訂閱，全文取用另循合法管道（學校圖書館）。

華藝的檢索是把一整包 JSON 塞進網址的 queryString，本檔負責構造那包 JSON；
結果頁是 JS 渲染，所以用 playwright 取。

學位論文另走 `scripts/thesis_ndltd.py`（臺灣博碩士論文加值系統）——先前判定它
「全站驗證碼、不可抓取」是**錯的**，2026-08 實測可抓，坑寫在那支的檔頭。

每組最多翻 8 頁 ×50 筆＝400 筆；撞到上限的組會標 `truncated: true` 並在
console 印警告，清單頁也會顯示，不讓截斷看起來像「這題目就這麼多」。

index：public/content/research-data/pct/biblio-airiti.json

  python -X utf8 scripts/biblio_search.py --search
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
    # 一貫道：戒嚴時期被查禁、1987 才合法化，是政教關係史最完整的一條「國家取締宗教」案例。
    # 鍾雲鶯（元智中語）與楊弘任（陽明交大人社）是這個題目的兩位主要研究者。
    ("一貫道 國民政府 取締", "一貫道：取締歷程"),
    ("一貫道 邪教 檔案", "一貫道：邪教指稱與檔案研究"),
    ("鍾雲鶯 一貫道", "一貫道：鍾雲鶯"),
    ("楊弘任 一貫道", "一貫道：楊弘任"),
    ("一貫道 台灣 合法化", "一貫道：1987 合法化"),
]

JS_TEMPLATE = r"""
import { chromium } from 'playwright'
const queries = JSON.parse(process.argv[2])
const MAX_PAGES = 8
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
    // 每頁改 50 筆，減少翻頁次數
    try {
      await p.selectOption('#Result_每頁顯示', { label: '50 筆' })
      await p.waitForTimeout(6000)
    } catch (e) { /* 版面偶爾沒有這個選單，照 10 筆翻 */ }
    let text = '', cur = 1
    while (cur <= MAX_PAGES) {
      text += "\n" + await p.locator('body').innerText()
      const next = p.locator(`.page a`, { hasText: new RegExp(`^${cur + 1}$`) }).first()
      if (!(await next.count())) break
      await next.click(); await p.waitForTimeout(5000); cur++
    }
    out.push({ query: q, note, url, text, pages: cur })
    console.error(`  ${q}: ${cur} 頁`)
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
        # 撞到 MAX_PAGES 就是被截斷的，必須標記——否則清單看起來像「這個題目就這麼多」
        truncated = g.get("pages", 0) > 8
        data.append({"query": g["query"], "note": g["note"], "url": g.get("url", ""),
                     "count": len(items), "truncated": truncated, "items": items})
        if truncated:
            print(f"    ⚠ {g['query']}：已達 8 頁上限，站上還有更多未取")
        print(f"  {g['query']}：{len(items)} 筆")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(d["items"]) for d in data)
    print(f"{len(data)} 組檢索 / {total} 筆書目 → {OUT}")


if __name__ == "__main__":
    main()
