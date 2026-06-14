// Harvest the complete 弘誓雙月刊 issue list across all ?p pages.
// Headful real-Chrome to pass Cloudflare; paced 5-8s between loads.
// Output: C:/tmp/hongshi_magazine_index.json  [{issue, date, title, pdfs:[url...]}]
import { chromium } from 'playwright'
import fs from 'fs'
const OUT = 'C:/tmp/hongshi_magazine_index.json'
const sleep = ms => new Promise(r => setTimeout(r, ms))
const jitter = () => 5000 + Math.floor(Math.random() * 3000)
const b = await chromium.launch({ headless: false, channel: 'chrome', args: ['--disable-blink-features=AutomationControlled'] })
const ctx = await b.newContext({ locale: 'zh-TW' })
await ctx.addInitScript(() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) })
const pg = await ctx.newPage()
async function load(url) {
  await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
  let t = await pg.title()
  for (let i = 0; i < 30 && /just a moment|請稍候|稍候|loading/i.test(t); i++) { await sleep(1000); t = await pg.title() }
  await sleep(1200); return t
}
const byIssue = {}
let emptyStreak = 0
for (let p = 1; p <= 80 && emptyStreak < 3; p++) {
  await load(`https://www.hongshi.org.tw/hongshi-magazine.php?p=${p}`)
  // each issue block: a PDF link admin/upload/file/...magazine-NNN-*.pdf + nearby heading text
  const rows = await pg.$$eval('a[href*="admin/upload/file"][href*=".pdf"]', as => as.map(a => {
    const href = a.getAttribute('href')
    // climb to a container to grab issue label/date text
    let box = a.closest('li,div,td,article,section') || a.parentElement
    let txt = ''
    for (let i = 0; i < 4 && box; i++) { txt = box.innerText || box.textContent || ''; if (txt.trim().length > 8) break; box = box.parentElement }
    return { href, txt: txt.replace(/\s+/g, ' ').trim().slice(0, 120) }
  }))
  let newCount = 0
  for (const r of rows) {
    const m = r.href.match(/magazine-(\d+)(?:-(\d))?-(\d{8})\.pdf/i)
    if (!m) continue
    const issue = parseInt(m[1])
    const url = r.href.startsWith('http') ? r.href : `https://www.hongshi.org.tw/${r.href.replace(/^\//, '')}`
    if (!byIssue[issue]) { byIssue[issue] = { issue, date: m[3], title: r.txt, pdfs: [] }; newCount++ }
    if (!byIssue[issue].pdfs.includes(url)) byIssue[issue].pdfs.push(url)
  }
  const total = Object.keys(byIssue).length
  console.log(`p=${p}: rows=${rows.length} new=${newCount} totalIssues=${total}`)
  emptyStreak = newCount === 0 ? emptyStreak + 1 : 0
  fs.writeFileSync(OUT, JSON.stringify(Object.values(byIssue).sort((a,b)=>b.issue-a.issue), null, 2))
  await sleep(jitter())
}
const all = Object.values(byIssue).sort((a,b)=>b.issue-a.issue)
const nums = all.map(x=>x.issue)
console.log(`\nDONE issues=${all.length} range ${Math.min(...nums)}-${Math.max(...nums)}`)
const gaps=[]; for(let i=Math.min(...nums);i<=Math.max(...nums);i++) if(!nums.includes(i)) gaps.push(i)
console.log('gaps:', gaps.join(','))
console.log('multi-part issues:', all.filter(x=>x.pdfs.length>1).map(x=>x.issue).join(','))
await b.close()
