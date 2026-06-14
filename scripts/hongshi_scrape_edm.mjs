// Scrape available 弘誓電子報 (EDM/<n>.html — only recent ~15 preserved on site).
// Headful CF pass, paced, resumable. Output: C:/tmp/hongshi_dl/edm/edm-<n>.json
import { chromium } from 'playwright'
import fs from 'fs'
const DIR = 'C:/tmp/hongshi_dl/edm'
const sleep = ms => new Promise(r => setTimeout(r, ms))
const jitter = () => 7000 + Math.floor(Math.random() * 3000)
const CH=/just a moment|請稍候|稍候|loading|安全驗證|惡意機器人/i
const arch = JSON.parse(fs.readFileSync('C:/tmp/hongshi_edm_archive.json','utf-8'))
const nums = [...new Set(arch.nums)].sort((a,b)=>b-a)
const b = await chromium.launch({ headless: false, channel: 'chrome', args: ['--disable-blink-features=AutomationControlled'] })
const ctx = await b.newContext({ locale: 'zh-TW' })
await ctx.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) })
const pg = await ctx.newPage()
async function load(url){ await pg.goto(url,{waitUntil:'domcontentloaded',timeout:60000}); let t=await pg.title(); for(let i=0;i<40&&(CH.test(t)||CH.test((await pg.locator('body').innerText().catch(()=>'')).slice(0,120)));i++){await sleep(1000);t=await pg.title()} await sleep(1200); return t }
await load('https://www.hongshi.org.tw/edm-page.php')   // warm CF
let ok=0,fail=0,skip=0
for (const n of nums) {
  const fn=`${DIR}/edm-${n}.json`
  if (fs.existsSync(fn)) { skip++; continue }
  try {
    const t = await load(`https://hongshi.org.tw/EDM/${n}.html`)
    if (/404|not found/i.test(t)) { console.log(`  ✗ ${n} 404`); fail++; await sleep(jitter()); continue }
    const data = await pg.evaluate(() => {
      const NAV=/最新消息|弘誓學團|護持捐款|友善連結/
      let best='',len=0
      for (const el of document.querySelectorAll('body,div,article,section,td,table,main')) { const tx=(el.innerText||'').trim(); if(tx.length>len&&tx.length<80000&&!NAV.test(tx.slice(0,40))){len=tx.length;best=tx} }
      return best || (document.body.innerText||'').trim()
    })
    if (!data || data.length<120 || /安全驗證|惡意機器人/.test(data)) { console.log(`  ∅ ${n} empty/challenge — backoff 30s`); fail++; await sleep(30000); continue }
    fs.writeFileSync(fn, JSON.stringify({n, text:data}, null, 2))
    ok++; console.log(`  ✓ EDM ${n} ${data.length} chars`)
  } catch(e){ console.log(`  ✗ ${n} ${e.message.slice(0,50)}`); fail++ }
  await sleep(jitter())
}
console.log(`\nDONE ok=${ok} skip=${skip} fail=${fail}`)
await b.close()
