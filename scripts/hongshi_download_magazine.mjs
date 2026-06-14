// Download all harvested 弘誓雙月刊 issue PDFs via the Cloudflare-passing browser
// session (PDFs sit behind CF too). Resumable (skip existing), paced 4-7s.
import { chromium } from 'playwright'
import fs from 'fs'
const IDX = 'C:/tmp/hongshi_magazine_index.json'
const DIR = 'C:/tmp/hongshi_dl/magazine'
const sleep = ms => new Promise(r => setTimeout(r, ms))
const jitter = () => 4000 + Math.floor(Math.random() * 3000)
const issues = JSON.parse(fs.readFileSync(IDX, 'utf-8'))
const b = await chromium.launch({ headless: false, channel: 'chrome', args: ['--disable-blink-features=AutomationControlled'] })
const ctx = await b.newContext({ locale: 'zh-TW' })
await ctx.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) })
const pg = await ctx.newPage()
// pass CF once on the magazine page; cookies then shared with ctx.request
await pg.goto('https://www.hongshi.org.tw/hongshi-magazine.php', { waitUntil: 'domcontentloaded', timeout: 60000 })
let t = await pg.title()
for (let i = 0; i < 30 && /just a moment|請稍候|稍候|loading/i.test(t); i++) { await sleep(1000); t = await pg.title() }
console.log('CF passed, title=', t)
let ok = 0, skip = 0, fail = 0
for (const it of issues) {
  for (let pi = 0; pi < it.pdfs.length; pi++) {
    const url = it.pdfs[pi]
    const part = it.pdfs.length > 1 ? `-p${pi + 1}` : ''
    const fn = `${DIR}/弘誓雙月刊-${String(it.issue).padStart(3, '0')}${part}.pdf`
    if (fs.existsSync(fn) && fs.statSync(fn).size > 10000) { skip++; continue }
    try {
      const resp = await ctx.request.get(url, { timeout: 60000 })
      if (!resp.ok()) { console.log(`  ✗ ${it.issue}${part} HTTP ${resp.status()}`); fail++; await sleep(jitter()); continue }
      const buf = await resp.body()
      fs.writeFileSync(fn, buf)
      ok++
      console.log(`  ✓ 期${it.issue}${part} ${(buf.length/1024/1024).toFixed(1)}MB`)
    } catch (e) { console.log(`  ✗ ${it.issue}${part} ${e.message.slice(0,60)}`); fail++ }
    await sleep(jitter())
  }
}
console.log(`\nDONE ok=${ok} skip=${skip} fail=${fail}`)
await b.close()
