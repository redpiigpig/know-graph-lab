// Scrape 弘誓/玄奘 歷屆學術活動 (meeting-B-page.php?n=N — needs Referer=meeting-B.php).
// 印順導師思想之理論與實踐 國際學術會議等歷屆研討會公告/徵稿/議程。
// Headful CF pass, paced, resumable, auto-relaunch on window close.
// Output: C:/tmp/hongshi_dl/meeting/meet-<n>.json + _index.json
import { chromium } from 'playwright'
import fs from 'fs'
const DIR = 'C:/tmp/hongshi_dl/meeting'
fs.mkdirSync(DIR, { recursive: true })
const sleep = ms => new Promise(r => setTimeout(r, ms))
const jitter = () => 7000 + Math.floor(Math.random() * 4000)
const CH = /just a moment|請稍候|稍候|loading|安全驗證|惡意機器人/i
let b, ctx, pg
async function fresh() {
  try { if (b) await b.close() } catch {}
  b = await chromium.launch({ headless: false, channel: 'chrome', args: ['--disable-blink-features=AutomationControlled'] })
  ctx = await b.newContext({ locale: 'zh-TW' })
  await ctx.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) })
  await ctx.setExtraHTTPHeaders({ Referer: 'https://www.hongshi.org.tw/meeting-B.php' })
  pg = await ctx.newPage()
}
const isClosed = e => /closed|Target closed|crash/i.test(e && e.message || '')
async function load(url) {
  await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
  let t = await pg.title()
  for (let i = 0; i < 40 && (CH.test(t) || CH.test((await pg.locator('body').innerText().catch(() => '')).slice(0, 120))); i++) { await sleep(1000); t = await pg.title() }
  await sleep(1200); return t
}
async function fetchPage(url) {
  for (let attempt = 0; attempt < 4; attempt++) {
    try {
      const t = await load(url)
      if (/錯誤|404|not found/i.test(t)) return { bad: true }
      const data = await pg.evaluate(() => {
        const NAV = /最新消息|弘誓學團|護持捐款|友善連結/
        let best = '', len = 0
        for (const el of document.querySelectorAll('div,article,section,td,main')) { const tx = (el.innerText || '').trim(); if (tx.length > len && tx.length < 80000 && !NAV.test(tx.slice(0, 40))) { len = tx.length; best = tx } }
        return best
      })
      return { data }
    } catch (e) { if (isClosed(e)) { console.log('   …relaunch'); await fresh(); await sleep(3000) } else throw e }
  }
  return { fail: true }
}

await fresh()
let items = []
for (let a = 0; a < 5; a++) {
  try {
    await load('https://www.hongshi.org.tw/meeting-B.php')
    items = await pg.$$eval('a[href*="meeting-B-page.php?n="]', as => [...new Map(as.map(x => { const n = parseInt((x.getAttribute('href').match(/n=(\d+)/) || [])[1]); return [n, { n, title: (x.textContent || '').trim().slice(0, 80) }] })).values()])
    items = items.filter(i => i.n)
    if (items.length) break
    console.log(`  index 0 items (attempt ${a + 1}) — backoff 60s`); await sleep(60000)
  } catch (e) { if (isClosed(e)) { await fresh(); await sleep(3000) } else throw e }
}
items.sort((a, b) => b.n - a.n)
if (!items.length) { console.log('STILL BLOCKED — cool down longer'); try { await b.close() } catch {}; process.exit(2) }
console.log('activities:', items.length)
fs.writeFileSync(`${DIR}/_index.json`, JSON.stringify(items, null, 2))
let ok = 0, skip = 0, fail = 0
for (const it of items) {
  const fn = `${DIR}/meet-${it.n}.json`
  if (fs.existsSync(fn)) { skip++; continue }
  const r = await fetchPage(`https://www.hongshi.org.tw/meeting-B-page.php?n=${it.n}`)
  if (r.bad || r.fail) { console.log(`  ✗ n=${it.n}`); fail++; await sleep(jitter()); continue }
  if (!r.data || r.data.length < 40 || /安全驗證|惡意機器人/.test(r.data)) { console.log(`  ∅ n=${it.n} — backoff 40s`); fail++; await sleep(40000); continue }
  fs.writeFileSync(fn, JSON.stringify({ n: it.n, title: it.title, text: r.data }, null, 2))
  ok++; if (ok % 10 === 0 || ok < 3) console.log(`  ✓ n=${it.n} ${r.data.length}c (${ok})`)
  await sleep(jitter())
}
console.log(`\nDONE ok=${ok} skip=${skip} fail=${fail}`)
try { await b.close() } catch {}
