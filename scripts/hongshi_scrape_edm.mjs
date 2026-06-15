// Scrape ALL 弘誓電子報 (issues 1–542). Issues are spread across 5 archive index
// pages and several epaper/hongshi pic{,2,3,5}/ + EDM/ folders. Harvest every
// issue URL from the indexes, then scrape each. Headful CF pass, paced, resumable.
// Output: C:/tmp/hongshi_dl/edm/edm-<n>.json   + _index.json (n→url map)
import { chromium } from 'playwright'
import fs from 'fs'
const DIR = 'C:/tmp/hongshi_dl/edm'
const sleep = ms => new Promise(r => setTimeout(r, ms))
const jitter = () => 6000 + Math.floor(Math.random() * 3000)
const CH = /just a moment|請稍候|稍候|loading|安全驗證|惡意機器人/i
const INDEX_PAGES = [
  'https://www.hongshi.org.tw/userfiles/epaper/hongshi%20pic/hongshi.htm',     // 401-542
  'https://www.hongshi.org.tw/userfiles/epaper/hongshi%20pic/301-400.htm',
  'https://www.hongshi.org.tw/userfiles/epaper/hongshi%20pic3/201-300.htm',
  'https://www.hongshi.org.tw/userfiles/epaper/hongshi%20pic2/101-200.htm',
  'https://www.hongshi.org.tw/userfiles/epaper/hongshi%20pic2/1-100.htm',
]
const b = await chromium.launch({ headless: false, channel: 'chrome', args: ['--disable-blink-features=AutomationControlled'] })
const ctx = await b.newContext({ locale: 'zh-TW' })
await ctx.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) })
const pg = await ctx.newPage()
async function load(url) {
  await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
  let t = await pg.title()
  for (let i = 0; i < 40 && (CH.test(t) || CH.test((await pg.locator('body').innerText().catch(() => '')).slice(0, 120))); i++) { await sleep(1000); t = await pg.title() }
  await sleep(1200); return t
}
// 1) harvest all issue URLs from the index pages
const map = {}
for (const idx of INDEX_PAGES) {
  await load(idx)
  // use a.href (browser-resolved absolute URL) so relative hrefs like "267.html"
  // on the older index pages resolve against their own folder.
  const links = await pg.$$eval('a[href]', as => as.map(a => a.href).filter(Boolean))
  let n0 = 0
  for (const url of links) {
    const m = url.match(/\/(\d+)\.html?(?:[?#]|$)/i)       // …/<n>.htm OR .html (old issues use .htm)
    if (!m || !/EDM\/|epaper\//i.test(url)) continue
    const n = +m[1]
    if (!map[n]) { map[n] = url; n0++ }
  }
  console.log(`index ${decodeURIComponent(idx.split('/').pop())}: +${n0} (total ${Object.keys(map).length})`)
  await sleep(jitter())
}
const nums = Object.keys(map).map(Number).sort((a, b) => b - a)
console.log(`harvested ${nums.length} EDM issues, range ${nums[nums.length - 1]}-${nums[0]}`)
fs.writeFileSync(`${DIR}/_index.json`, JSON.stringify(map, null, 2))
// 2) scrape each (resumable)
let ok = 0, skip = 0, fail = 0
for (const n of nums) {
  const fn = `${DIR}/edm-${n}.json`
  if (fs.existsSync(fn)) { skip++; continue }
  try {
    const t = await load(map[n])
    if (/404|not found/i.test(t)) { console.log(`  ✗ ${n} 404`); fail++; await sleep(jitter()); continue }
    const data = await pg.evaluate(() => {
      const NAV = /最新消息|弘誓學團|護持捐款|友善連結/
      let best = '', len = 0
      for (const el of document.querySelectorAll('body,div,article,section,td,table,main')) { const tx = (el.innerText || '').trim(); if (tx.length > len && tx.length < 100000 && !NAV.test(tx.slice(0, 40))) { len = tx.length; best = tx } }
      return best || (document.body.innerText || '').trim()
    })
    if (!data || data.length < 120 || /安全驗證|惡意機器人/.test(data)) { console.log(`  ∅ ${n} empty/challenge — backoff 40s`); fail++; await sleep(40000); continue }
    fs.writeFileSync(fn, JSON.stringify({ n, text: data }, null, 2))
    ok++; if (ok % 20 === 0 || ok < 3) console.log(`  ✓ EDM ${n} ${data.length} chars (${ok} done)`)
  } catch (e) { console.log(`  ✗ ${n} ${e.message.slice(0, 50)}`); fail++ }
  await sleep(jitter())
}
console.log(`\nDONE ok=${ok} skip=${skip} fail=${fail} | total files ${fs.readdirSync(DIR).filter(f => f.startsWith('edm-')).length}`)
await b.close()
