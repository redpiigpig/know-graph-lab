# -*- coding: utf-8 -*-
"""臺灣博碩士論文加值系統（NDLTD）**會員登入後**下載已授權電子全文。

與 thesis_fulltext.py 的分工：那支走「NDLTD 詳目 → 各校機構典藏」，不需登入；
這支走 NDLTD 自己的「電子全文」按鈕——**國圖其實有放全文**（站上自報「論文已授權
全文 85 萬筆」），只是要會員登入、每篇還要再過一次驗證碼。2026-09-25 太虛研究一輪
實測：69 筆有編號的候選，NDLTD 登入下載拿到 41 篇，學校典藏只多補到 1 篇。

流程（每一步都實測過）：
  1. 登入頁 /registry 有圖形驗證碼（6 位數字）。帳密讀 .env 的 NDLTD_USER／NDLTD_PASS。
  2. 詳目用 `ccd=<session>/search?s=id="<論文編號>".&searchmode=basic` 開；
     登入狀態下「電子全文」會是 window.open('…/fulltextdeclare?dbid=…')，
     **沒登入時同一顆按鈕只會跳「請先登入」**，所以抓 declare 連結前先確認頁上有「登出」。
     沒有 declare 連結＝作者沒授權公開（NDLTD 標「電子全文」但沒按鈕的也是這種），記原因跳過。
  3. 宣告頁再一次驗證碼 → 按「我同意」→ 出現「下載清單」頁，上面一個「下載」連結
     （brwfull?...&attachfile=1）才是檔案。**多數是 zip（內含一個 PDF），少數直接是 PDF**
     ——副檔名一律當 .zip 存，事後看開頭是 PK 還是 %PDF。
  4. 驗 `%PDF` 開頭與頁數（pypdf），寫 .part 再改名。

🚨 驗證碼只能人工判讀：腳本把圖放大三倍存到 <work>/captcha.png，寫 <work>/need.txt，
   等 <work>/answer.txt。判讀的人（或 agent 用 Read 看圖）寫入數字即可。
   原圖只有 100×25，直接看約一半會認錯；放大後大多對，但看得很清楚的也偶爾被判錯
   （太虛一輪約一成），所以答錯腳本會自己換一張重來，最多 3 次。
🚨 同一個 session 裡**不要回首頁**：goto('https://ndltd.ncl.edu.tw/') 會發一個新的 ccd，
   等於登出。一律沿用登入後網址裡的 ccd。
🚨 檢索（不是下載）撞到的是另一種驗證碼頁「驗證碼檢查機制」，同樣要人工過；
   本腳本只下載已知編號，不做檢索。編號從 thesis_ndltd.py 的檢索結果或詳目頁
   （頁面原始碼 `dbid=098FGU05105008` 那一段）取得。
🚨 「無授權」「有償授權」「校內限閱」一律記原因跳過，不繞過。

  # ids.json：[{"id": "098FGU05105008", "name": "98_佛光大學_郭育誠_太虛與僧伽制度之研究.pdf"}, …]
  python -X utf8 scripts/ndltd_member_fulltext.py --ids ids.json --out "G:/…/碩博論文" --work C:/tmp/ndltd_dl
  # 另開一個視窗看 <work>/need.txt，讀 <work>/captcha.png，把數字寫進 <work>/answer.txt
"""
import argparse
import io
import json
import os
import subprocess
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# 必須放 repo 內執行，否則 node 找不到 playwright
NODE_SCRIPT = REPO / "scripts/.ndltd_member_dl.mjs"

JS = r"""
import { chromium } from 'playwright'
import fs from 'fs'
const [ids, WORK] = [JSON.parse(fs.readFileSync(process.argv[2], 'utf8')), process.argv[3]]
const env = Object.fromEntries(fs.readFileSync('.env', 'utf8').split(/\r?\n/).filter(l => /^NDLTD_/.test(l))
  .map(l => { const i = l.indexOf('='); return [l.slice(0, i), l.slice(i + 1).replace(/^["']|["']$/g, '')] }))
const ledgerPath = WORK + '/ledger.json'
const ledger = fs.existsSync(ledgerPath) ? JSON.parse(fs.readFileSync(ledgerPath, 'utf8')) : {}
const save = () => fs.writeFileSync(ledgerPath, JSON.stringify(ledger, null, 1))
const sleep = ms => new Promise(r => setTimeout(r, ms))
async function ask(page, sel, tag) {
  await page.evaluate(s => { const i = document.querySelector(s); if (i) { i.style.width = i.naturalWidth * 3 + 'px'; i.style.height = i.naturalHeight * 3 + 'px' } }, sel)
  await page.waitForTimeout(300)
  await page.locator(sel).first().screenshot({ path: WORK + '/captcha.png' })
  const ans = WORK + '/answer.txt'
  if (fs.existsSync(ans)) fs.unlinkSync(ans)
  fs.writeFileSync(WORK + '/need.txt', tag)
  console.error('NEED_CAPTCHA ' + tag)
  while (!fs.existsSync(ans)) await sleep(1500)
  await sleep(300)
  const a = fs.readFileSync(ans, 'utf8').trim()
  fs.unlinkSync(ans); fs.writeFileSync(WORK + '/need.txt', '')
  return a
}
const b = await chromium.launch()
const ctx = await b.newContext({ acceptDownloads: true })
const p = await ctx.newPage()
const CAP = 'img[src*="validationimgs"]'
// 登入（驗證碼錯就重來）
// 🚨 流量閘「驗證碼檢查機制」過了之後**不可再 goto 首頁**：會再發一次閘，永遠繞不出去
//    （實測連撞 4 次）。過閘後直接從當下網址的 ccd 轉 /registry。
await p.goto('https://ndltd.ncl.edu.tw/', { waitUntil: 'domcontentloaded', timeout: 90000 })
await p.waitForTimeout(4000)
for (let t = 0; t < 6; t++) {
  if ((await p.locator('body').innerText()).includes('驗證碼檢查機制')) {
    await p.fill('#validinput', await ask(p, CAP, 'gate'))
    await Promise.all([p.waitForNavigation({ timeout: 90000 }).catch(() => {}), p.click('input[name="check"]')])
    await p.waitForTimeout(3000)
    continue
  }
  if (!/\/ccd=[\w-]+\//.test(p.url())) { await p.waitForTimeout(3000); continue }
  await p.goto(p.url().replace(/\/(login|registry|search).*/, '/registry'), { waitUntil: 'domcontentloaded', timeout: 90000 })
  await p.waitForTimeout(3000)
  const a = await ask(p, CAP, 'login')
  await p.fill('#id', env.NDLTD_USER); await p.fill('#ps', env.NDLTD_PASS); await p.fill('#validinput', a)
  await Promise.all([p.waitForNavigation({ timeout: 90000 }).catch(() => {}), p.click('#button')])
  await p.waitForTimeout(4000)
  if ((await p.locator('body').innerText()).includes('登出')) break
}
if (!(await p.locator('body').innerText()).includes('登出')) { console.error('LOGIN_FAILED'); await b.close(); process.exit(3) }
const base = p.url().match(/^(.*\/ccd=[\w-]+)\//)[1]   // 🚨 之後一律沿用這個 ccd，不回首頁
console.error('LOGGED_IN')
for (const { id } of ids) {
  if (ledger[id] && /^(downloaded|skip)/.test(ledger[id].status)) continue
  await p.goto(base + '/search?s=id=%22' + id + '%22.&searchmode=basic', { waitUntil: 'domcontentloaded', timeout: 90000 })
  await p.waitForTimeout(2500)
  const h = await p.content()
  if (!(await p.locator('body').innerText()).includes('登出')) { console.error('SESSION_LOST'); break }
  const decl = (h.match(/(\/cgi-bin\/gs32\/gsweb\.cgi\/ccd=[\w-]+\/fulltextdeclare\?dbid=[^'"]+)/) || [])[1]
  if (!decl) { ledger[id] = { status: 'skip: NDLTD 無授權電子全文' }; save(); console.error(id + ' skip'); await sleep(4000); continue }
  let ok = false
  for (let t = 0; t < 3 && !ok; t++) {
    const fd = await ctx.newPage()
    await fd.goto('https://ndltd.ncl.edu.tw' + decl.replace(/&amp;/g, '&'), { waitUntil: 'domcontentloaded', timeout: 90000 })
    await fd.waitForTimeout(2500)
    await fd.locator('input[type="text"]').first().fill(await ask(fd, CAP, id))
    await Promise.all([fd.waitForNavigation({ timeout: 60000 }).catch(() => {}), fd.locator('input[value="我同意"]').click()])
    await fd.waitForTimeout(3000)
    if ((await fd.locator('body').innerText()).includes('下載清單')) {
      const [dl] = await Promise.all([fd.waitForEvent('download', { timeout: 180000 }).catch(() => null),
        fd.locator('a[href*="brwfull"]').first().click().catch(() => {})])
      if (dl) { await dl.saveAs(WORK + '/' + id + '.zip'); ledger[id] = { status: 'fetched' }; save(); ok = true }
    }
    await fd.close()
  }
  if (!ok) { ledger[id] = { status: 'fail: 下載流程未完成' }; save() }
  console.error(id + (ok ? ' fetched' : ' fail'))
  await sleep(5000)
}
await b.close()
"""


def finish(ids, work, out, ledger):
    """zip 或 PDF → 驗 %PDF 與頁數 → 寫 .part 再改名到 out。"""
    from pypdf import PdfReader
    for it in ids:
        tid, name = it["id"], it["name"]
        rec = ledger.get(tid, {})
        raw = work / f"{tid}.zip"
        if rec.get("status") != "fetched" or not raw.exists():
            continue
        data = raw.read_bytes()
        if data[:2] == b"PK":
            z = zipfile.ZipFile(io.BytesIO(data))
            pdfs = [z.read(n) for n in z.namelist() if n.lower().endswith(".pdf")]
        else:
            pdfs = [data]
        pdfs = [x for x in pdfs if x[:4] == b"%PDF" and len(x) > 50_000]
        if not pdfs:
            rec["status"] = "fail: 下載內容不是 PDF"
            continue
        files, pages = [], 0
        for i, blob in enumerate(pdfs):
            n = name if len(pdfs) == 1 else name.replace(".pdf", f"_{i + 1}.pdf")
            pages += len(PdfReader(io.BytesIO(blob)).pages)
            part = out / (n + ".part")
            part.write_bytes(blob)
            os.replace(part, out / n)
            files.append(n)
        ledger[tid] = {"status": "downloaded", "files": files, "pages": pages}
        print(f"  ✔ {tid} {files[0]}（{pages} 頁）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", required=True, help='JSON：[{"id": 論文編號, "name": 目標檔名}, …]')
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", default="C:/tmp/ndltd_dl")
    a = ap.parse_args()
    work, out = Path(a.work), Path(a.out)
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    ids = json.loads(Path(a.ids).read_text(encoding="utf-8"))
    NODE_SCRIPT.write_text(JS, encoding="utf-8")
    subprocess.run(["node", str(NODE_SCRIPT), str(Path(a.ids).resolve()), str(work.resolve())], cwd=REPO)
    lp = work / "ledger.json"
    ledger = json.loads(lp.read_text(encoding="utf-8")) if lp.exists() else {}
    finish(ids, work, out, ledger)
    lp.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(Counter(v["status"].split(":")[0] for v in ledger.values()))


if __name__ == "__main__":
    main()
