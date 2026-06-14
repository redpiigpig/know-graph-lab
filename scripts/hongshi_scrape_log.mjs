// Scrape 學團日誌 (log-page.php?n=N). Needs Referer=log.php. Headful CF pass,
// paced 4-7s, resumable (skip saved). Output per entry: C:/tmp/hongshi_dl/log/log-NNN.json
import { chromium } from 'playwright'
import fs from 'fs'
const DIR = 'C:/tmp/hongshi_dl/log'
const sleep = ms => new Promise(r => setTimeout(r, ms))
const jitter = () => 8000 + Math.floor(Math.random() * 4000)   // 8-12s, gentler after rate-limit
const b = await chromium.launch({ headless: false, channel: 'chrome', args: ['--disable-blink-features=AutomationControlled'] })
const ctx = await b.newContext({ locale: 'zh-TW' })
await ctx.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) })
const pg = await ctx.newPage()
const CHALLENGE = /just a moment|請稍候|稍候|loading|正在執行安全驗證|安全驗證|惡意機器人/i
async function pass(){
  let t=await pg.title()
  for(let i=0;i<40 && (CHALLENGE.test(t) || CHALLENGE.test((await pg.locator('body').innerText().catch(()=>'')).slice(0,120)));i++){ await sleep(1000); t=await pg.title() }
  await sleep(1500); return t
}
// Robust index load: retry if 0 entries (rate-limit / unsolved challenge symptom).
async function loadIndex() {
  for (let attempt = 1; attempt <= 4; attempt++) {
    await pg.goto('https://www.hongshi.org.tw/log.php', { waitUntil: 'domcontentloaded', timeout: 60000 })
    const t = await pass()
    let es = await pg.$$eval('a[href*="log-page.php?n="]', as => [...new Map(as.map(a => {
      const h = a.getAttribute('href'); const n = parseInt((h.match(/n=(\d+)/) || [])[1]); return [n, { n, range: (a.textContent || '').trim().slice(0, 40) }]
    })).values()])
    es = es.filter(e => e.n).sort((a, b) => b.n - a.n)
    if (es.length) return es
    console.log(`  index attempt ${attempt}: 0 entries (title="${t}") — backing off 45s`)
    await sleep(45000)
  }
  return []
}
let entries = await loadIndex()
if (!entries.length) { console.log('STILL BLOCKED — aborting; cool down longer and retry'); await b.close(); process.exit(2) }
console.log('log entries found:', entries.length, 'n range', Math.min(...entries.map(e=>e.n)),'-',Math.max(...entries.map(e=>e.n)))
fs.writeFileSync(`${DIR}/_index.json`, JSON.stringify(entries,null,2))
await pg.setExtraHTTPHeaders({ Referer: 'https://www.hongshi.org.tw/log.php' })
let ok=0,skip=0,fail=0
for (const e of entries) {
  const fn=`${DIR}/log-${String(e.n).padStart(3,'0')}.json`
  if (fs.existsSync(fn)) { skip++; continue }
  try {
    await pg.goto(`https://www.hongshi.org.tw/log-page.php?n=${e.n}`,{waitUntil:'domcontentloaded',timeout:60000})
    const t=await pass()
    if (/錯誤|error/i.test(t)) { console.log(`  ✗ n=${e.n} error page`); fail++; await sleep(jitter()); continue }
    const text = await pg.evaluate(() => {
      const NAV=/最新消息|弘誓學團|護持捐款|友善連結/
      let best='',len=0
      for (const el of document.querySelectorAll('div,article,section,td,main')) {
        const tx=(el.innerText||'').trim()
        if (tx.length>len && tx.length<60000 && !NAV.test(tx.slice(0,60))) { len=tx.length; best=tx }
      }
      return best
    })
    if (!text || text.length<120 || /安全驗證|惡意機器人/.test(text)) { console.log(`  ∅ n=${e.n} empty/challenge (len=${(text||'').length}) — backing off 40s`); fail++; await sleep(40000); continue }
    fs.writeFileSync(fn, JSON.stringify({n:e.n,range:e.range,text},null,2))
    ok++; if (ok%10===0||ok<3) console.log(`  ✓ n=${e.n} ${text.length} chars (${ok} done)`)
  } catch(err){ console.log(`  ✗ n=${e.n} ${err.message.slice(0,50)}`); fail++ }
  await sleep(jitter())
}
console.log(`\nDONE ok=${ok} skip=${skip} fail=${fail}`)
await b.close()
