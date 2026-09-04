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
    # 一貫道：戒嚴時期查禁、1987 合法化，是「國家取締宗教」最完整的一條案例。
    # 王博賢那本（政大宗教所 2006）直接把長老教會與一貫道並置比較，與本論文同一組對象。
    ("王博賢 政教關係", "一貫道：王博賢學位論文"),
    ("一貫道 政教關係", "一貫道：政教關係"),
    ("一貫道 合法化", "一貫道：1987 合法化"),
    ("一貫道 取締", "一貫道：查禁與取締"),
    # 一貫道研究本身要成一份清單（不只是政教關係那一角）：教義、儀式、組線、
    # 海外傳播、與民間宗教的關係，以及兩位主要研究者的學術系譜。
    ("鍾雲鶯 一貫道", "一貫道：鍾雲鶯"),
    ("楊弘任 一貫道", "一貫道：楊弘任"),
    ("一貫道 教義", "一貫道：教義與經典"),
    ("一貫道 儀式", "一貫道：儀式"),
    ("一貫道 祭祖", "一貫道：祭祖禮儀"),
    ("一貫道 發一崇德", "一貫道：發一崇德"),
    ("一貫道 寶光", "一貫道：寶光組線"),
    ("一貫道 基礎忠恕", "一貫道：基礎忠恕"),
    ("一貫道 組織", "一貫道：組線與組織"),
    ("一貫道 民間宗教", "一貫道：民間宗教脈絡"),
    ("一貫道 海外", "一貫道：海外傳播"),
    ("一貫道 素食", "一貫道：素食與生活實踐"),
    ("一貫道 女性", "一貫道：性別"),
    ("一貫道 教育", "一貫道：教育事業"),
    ("先天道 齋教", "一貫道：先天道與齋教前史"),
    ("鸞堂 扶乩", "一貫道：鸞堂扶乩比較"),
    # 碩士論文改寫《當代的大愛道革命》——昭慧、性廣、八敬法、佛教女性主義。
    ("八敬法", "碩論：八敬法"),
    ("性廣法師 禪觀", "碩論：性廣禪觀"),
    ("釋昭慧 性別", "碩論：昭慧與性別"),
    ("佛教 女性主義", "碩論：佛教女性主義"),
    ("比丘尼 戒律", "碩論：比丘尼戒律"),
    ("佛教 性別平等", "碩論：佛教性別平等"),
    ("台灣 比丘尼 教團", "碩論：台灣比丘尼教團"),
    ("佛教 社會運動 昭慧", "碩論：昭慧社會運動"),
    ("大愛道 摩訶波闍波提", "碩論：大愛道"),
    ("弘誓學院", "碩論：弘誓學院"),
    # 學士論文改寫〈福音派運動在台灣基督教中的起源與發展〉（台大歷史 2018）。
    ("台灣 福音派", "學士：台灣福音派"),
    ("福音派 運動", "學士：福音派運動"),
    ("校園團契 學生福音", "學士：校園團契"),
    ("台灣 基督教 宣教史", "學士：在台宣教史"),
    ("靈恩運動 台灣", "學士：靈恩運動"),
    ("台灣 教會增長", "學士：教會增長運動"),
    ("基要主義 基督教", "學士：基要主義"),
    ("中華福音神學院", "學士：華神與福音派建制"),
    ("台灣 基督教 本土化 教派", "學士：教派與本土化"),
    ("原住民 基督教 台灣", "學士：原住民教會"),
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
        // 首頁是一段 JS 轉址，等它跳完才讀得到真正的頁面
        await p.waitForTimeout(3000)
        // 驗證碼頁沒有 #ALLFIELD_不限欄位，所以要搶在 waitForSelector 之前認，
        // 否則只會拿到一句選擇器逾時，看不出真正的原因。
        if ((await p.locator('body').innerText()).includes('驗證碼')) {
          throw new Error('CAPTCHA：站方因流量對本 IP 掛出驗證碼，需等冷卻後再跑')
        }
        await p.waitForSelector('#ALLFIELD_不限欄位', { state: 'attached', timeout: 30000 })
        break
      } catch (e) {
        if (a || String(e).includes('CAPTCHA')) throw e   // 驗證碼不必重試
        await p.waitForTimeout(8000)
      }
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
    // 站方自報的總筆數要一起帶回來：光看翻了幾頁判斷不出有沒有截斷
    // （分頁鍵有時會在同一頁上打轉，翻滿 8 頁卻只拿到個位數筆）。
    const m = text.match(/檢索結果共\s*([\d,]+)\s*筆/)
    const total = m ? parseInt(m[1].replace(/,/g, ''), 10) : 0
    out.push({ query: q, note, text, pages: page, total })
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
    # 給排程用：印 ALL_DONE / PENDING <n>。keeper 是 ASCII-only 的 .ps1，
    # 不能在那邊比對中文字串（PS 5.1 讀無 BOM 的 .ps1 當 ANSI，中文會被切壞）。
    ap.add_argument("--check-done", action="store_true")
    args = ap.parse_args()
    if args.check_done:
        done = {r.get("query") for r in (json.loads(OUT.read_text(encoding="utf-8"))
                                         if OUT.exists() else [])}
        left = [q for q, _ in QUERIES if q not in done]
        print("ALL_DONE" if not left else f"PENDING {len(left)}")
        return
    if not args.search:
        ap.print_help()
        return
    qs = [[args.query, "自訂"]] if args.query else [[q, n] for q, n in QUERIES]
    NODE_SCRIPT.write_text(JS, encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # 🚨 一次把 14 組丟給 node 會撞逾時，而且**跑完才回傳＝中斷就全部白跑**（踩過一次，
    # 一小時的結果全丟）。改成一組一組跑、每組存檔；已在檔裡的組跳過，可續跑。
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    # 🚨 判準是「檔裡有沒有這一組」，不是「這一組有沒有命中」。抓失敗的組根本不寫檔
    #    （見下面 g["error"] 那一段），所以有紀錄就是抓成功了。用 count 當判準的話，
    #    真的 0 筆的組會被永遠重跑，keeper 也就永遠等不到完工、無限空轉。
    done = {d["query"] for d in data}
    todo = [q for q in qs if q[0] not in done or args.force]
    print(f"待查 {len(todo)} 組（已完成 {len(done)} 組）", flush=True)
    for one in todo:
        r = subprocess.run(["node", str(NODE_SCRIPT), json.dumps([one], ensure_ascii=False)],
                           cwd=REPO, capture_output=True, text=True, encoding="utf-8", timeout=900)
        sys.stderr.write(r.stderr or "")
        if not r.stdout.strip():
            print(f"  {one[0]}：沒有回傳，跳過", flush=True)
            continue
        stop = False
        for g in json.loads(r.stdout):
            if g.get("error"):
                print(f"  {g['query']}：抓取失敗，不寫入（{g['error'][:80]}）", flush=True)
                # 撞到驗證碼就整輪收手。站方是按 IP 計量的，剩下的組照跑只會一路撞、
                # 一路加重同一個 IP 的量，冷卻反而更久（踩過一次，13 組全撞完才停）。
                stop = stop or "CAPTCHA" in g["error"]
                continue
            items = parse(g.get("text", ""))
            data = [d for d in data if d["query"] != g["query"]]
            total = g.get("total") or 0
            # 截斷與否以「站方自報總數 vs 實際取回」為準，不看翻了幾頁。
            data.append({"query": g["query"], "note": g["note"], "count": len(items),
                         "total": total, "truncated": bool(total) and total > len(items),
                         "items": items})
            print(f"  {g['query']}：取得 {len(items)} 筆"
                  f"{f'（站上共 {total} 筆）' if total else ''}", flush=True)
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        if stop:
            print("")
            print("站方已對本 IP 掛出驗證碼，停止本輪；等冷卻後再下一次即可續跑。", flush=True)
            break
    print(f"{len(data)} 組檢索 / {sum(d['count'] for d in data)} 筆學位論文 → {OUT}")


if __name__ == "__main__":
    main()
