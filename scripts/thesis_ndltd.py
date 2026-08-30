# -*- coding: utf-8 -*-
"""臺灣博碩士論文加值系統（ndltd.ncl.edu.tw）→ 博士論文用的**學位論文書目**。

只收書目欄位（論文名稱／研究生／指導教授／校院／系所／畢業學年度／學位／有無電子全文），
不下載全文——全文授權狀況逐篇不同，另循國圖或各校館藏取用。

🚨 兩個坑（2026-08 實測，先前誤判為「全站驗證碼、不可抓取」，其實沒有）：

1. **預設欄位是「論文名稱」且模式「精準」**，多數複合詞查回 0 筆。
   必須先勾 `#ALLFIELD_不限欄位`，才是真正的全欄位檢索。
2. **查詢模式不可選「模糊」**（`extrasearch=es1`）。它會把詞拆成單字比對，
   「長老教會 公共神學」會撈回一整頁植物生理學論文。一律用預設的「精準」，
   詞與詞之間的空白＝AND。

記錄連結帶 session 代碼（`ccd=XXXX`）**會過期**，故只存書目欄位不存連結；
要調閱時以論文名稱重查即可。

index：public/content/research-data/pct/biblio-ndltd.json

  python -X utf8 scripts/thesis_ndltd.py --search        # 一組一組跑、每組存檔，可續跑
  python -X utf8 scripts/thesis_ndltd.py --search --query "王憲治 鄉土神學"
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "public/content/research-data/pct/biblio-ndltd.json"
# 必須放 repo 內執行，否則 node 找不到 playwright
NODE_SCRIPT = REPO / "scripts/.ndltd_fetch.mjs"

# 與 biblio_search.py 同一組詞表，每條對應論文的一個章節任務
QUERIES = [
    ("黃彰輝 實況化", "第四章第二節"),
    ("宋泉盛 故事神學", "第四章第三節"),
    ("王憲治 鄉土神學", "第四章第四節"),
    ("黃伯和 出頭天", "第四章第五節"),
    ("長老教會 公共神學", "第四章"),
    ("長老教會 人權宣言", "第四章第一節"),
    ("傳道法師 妙心寺", "第三章第三節"),
    ("釋昭慧 佛教倫理", "第三章第四節"),
    ("印順 人間佛教", "第三章第二節"),
    ("太虛 人生佛教", "第三章第一節"),
    ("佛教 基督教 對話", "第六章"),
    ("無教會主義", "第二章日本線"),
    ("台灣 佛教 社會運動", "第三章"),
    ("台灣 基督教 本土神學", "第四章"),
]

JS = r"""
import { chromium } from 'playwright'
const queries = JSON.parse(process.argv[2])
const MAX_PAGES = 8          // 一頁 20 筆，上限 160 筆／組，足夠本論文的用途
const b = await chromium.launch()
const p = await b.newPage()
const out = []
for (const [q, note] of queries) {
  try {
    // 站方偶爾很慢，networkidle 會逾時；用 domcontentloaded＋固定等待，並重試一次
    for (let a = 0; a < 2; a++) {
      try {
        await p.goto('https://ndltd.ncl.edu.tw/', { waitUntil: 'domcontentloaded', timeout: 90000 })
        await p.waitForSelector('#ALLFIELD_不限欄位', { state: 'attached', timeout: 30000 })
        break
      } catch (e) { if (a) throw e; await p.waitForTimeout(8000) }
    }
    await p.waitForTimeout(3000)
    await p.check('#ALLFIELD_不限欄位', { force: true })          // 坑 1：不勾就只查論文名稱
    await p.fill('input[name="qs0"]', q)          // 坑 2：模式維持預設「精準」
    await Promise.all([
      p.waitForNavigation({ timeout: 90000 }).catch(() => {}),
      p.press('input[name="qs0"]', 'Enter'),
    ])
    await p.waitForTimeout(6000)
    // 「下一頁」是 <input type=image name=gonext alt="下一頁">——用 alt 抓，
    // 它沒有 value，用 input[value="下一頁"] 會永遠抓不到而只取回第一頁
    let text = '', page = 1
    while (page <= MAX_PAGES) {
      text += '\n' + await p.locator('body').innerText()
      // 結果頁渲染完才會掛上 gonext；不等就會誤判成「只有一頁」
      await p.waitForSelector('input[name="gonext"]', { state: 'attached', timeout: 15000 }).catch(() => {})
      const next = p.locator('input[name="gonext"]').first()
      if (!(await next.count())) break
      await Promise.all([
        p.waitForNavigation({ timeout: 60000 }).catch(() => {}),
        next.click({ force: true }).catch(() => {}),
      ])
      await p.waitForTimeout(4000)
      page++
    }
    out.push({ query: q, note, text, pages: page })
    const m = text.match(/檢索結果共\s*([\d,]+)\s*筆/)
    console.error(`  ${q}: 站上共 ${m ? m[1] : '?'} 筆，翻 ${page} 頁`)
  } catch (e) {
    out.push({ query: q, note, error: String(e).slice(0, 120), text: '' })
    console.error(`  ${q}: FAIL ${String(e).slice(0, 160)}`)
  }
}
console.log(JSON.stringify(out))
await b.close()
"""

# 結果頁一筆的樣態（純文字）：
#   \t12.\t
#   台灣基督長老教會的公共性…        ← 論文名稱
#   國立政治大學／宗教研究所／110／碩士／人文學門／宗教學類
#   研究生:王小明
#   指導教授:李大華
#   論文種類 : 學術論文
#   電子全文 / 國圖紙本論文
ITEM_RE = re.compile(r"^\t?\d+\.\t?\s*$")
INST_RE = re.compile(r"^.+／.+／\d+／(碩士|博士)")


def parse(text: str):
    lines = [l.rstrip() for l in (text or "").split("\n")]
    rows, i = [], 0
    while i < len(lines):
        if not ITEM_RE.match(lines[i]):
            i += 1
            continue
        j, buf = i + 1, []
        while j < len(lines) and len(buf) < 12 and not ITEM_RE.match(lines[j]):
            if lines[j].strip():
                buf.append(lines[j].strip())
            j += 1
        title = buf[0] if buf else ""
        inst = next((b for b in buf if INST_RE.match(b)), "")
        if title and inst:
            parts = inst.split("／")
            rows.append({
                "kind": "學位論文",
                "title": title,
                "author": next((b.split(":", 1)[1].strip() for b in buf if b.startswith("研究生:")), ""),
                "advisor": next((b.split(":", 1)[1].strip() for b in buf if b.startswith("指導教授:")), ""),
                "school": parts[0],
                "dept": parts[1] if len(parts) > 1 else "",
                "year": parts[2] if len(parts) > 2 else "",
                "degree": parts[3] if len(parts) > 3 else "",
                "fulltext": any("電子全文" in b for b in buf),
            })
        i = j
    seen, uniq = set(), []
    for r in rows:
        k = (r["title"], r["school"])
        if k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--query")
    ap.add_argument("--force", action="store_true", help="已完成的組也重跑")
    args = ap.parse_args()
    if not args.search:
        ap.print_help()
        return
    qs = [[args.query, "自訂"]] if args.query else [[q, n] for q, n in QUERIES]
    NODE_SCRIPT.write_text(JS, encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # 🚨 一次把 14 組丟給 node 會撞逾時，而且**跑完才回傳＝中斷就全部白跑**（踩過一次，
    # 一小時的結果全丟）。改成一組一組跑、每組存檔；已在檔裡的組跳過，可續跑。
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    done = {d["query"] for d in data if d.get("count")}
    todo = [q for q in qs if q[0] not in done or args.force]
    print(f"待查 {len(todo)} 組（已完成 {len(done)} 組）", flush=True)
    for one in todo:
        r = subprocess.run(["node", str(NODE_SCRIPT), json.dumps([one], ensure_ascii=False)],
                           cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=900)
        sys.stderr.write(r.stderr or "")
        if not r.stdout.strip():
            print(f"  {one[0]}：沒有回傳，跳過", flush=True)
            continue
        for g in json.loads(r.stdout):
            items = parse(g.get("text", ""))
            data = [d for d in data if d["query"] != g["query"]]
            data.append({"query": g["query"], "note": g["note"], "count": len(items),
                         "truncated": g.get("pages", 0) > 8, "items": items})
            print(f"  {g['query']}：取得 {len(items)} 筆", flush=True)
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(data)} 組檢索 / {sum(d['count'] for d in data)} 筆學位論文 → {OUT}")


if __name__ == "__main__":
    main()
