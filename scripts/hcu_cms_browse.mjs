// 沿用 hcu_cms_login.mjs 存下的 cookie，瀏覽後台任一頁並把表格／連結／下拉選單撈出來。
// 只讀：不點儲存、不送內容表單。
//
// 用法：node scripts/hcu_cms_browse.mjs <後台相對或完整 URL> [tag]
//   node scripts/hcu_cms_browse.mjs MngCms/NodeList.aspx nodes
import { readFileSync, writeFileSync, existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
const STATE = `${OUT}/state.json`
if (!existsSync(STATE)) { console.error('先跑 hcu_cms_login.mjs 取得 cookie'); process.exit(2) }

const arg = process.argv[2]
if (!arg) { console.error('用法：node scripts/hcu_cms_browse.mjs <url> [tag]'); process.exit(2) }
const tag = process.argv[3] || 'browse'
const url = arg.startsWith('http') ? arg : `https://www.hcu.edu.tw/backend/${arg.replace(/^\//, '')}`

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: STATE, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()
await page.goto(url, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(2000)

console.log(`[url] ${page.url()}`)
if (/login\.aspx/i.test(page.url())) {
  console.log('❌ session 過期，要重跑 hcu_cms_login.mjs')
  await browser.close(); process.exit(1)
}

writeFileSync(`${OUT}/${tag}.html`, await page.content(), 'utf8')
await page.screenshot({ path: `${OUT}/${tag}.png`, fullPage: true })

// 表格逐列
const tables = await page.$$eval('table', ts => ts.map(t => Array.from(t.querySelectorAll('tr')).map(tr =>
  Array.from(tr.querySelectorAll('th,td')).map(td => (td.innerText || '').replace(/\s+/g, ' ').trim()).join(' | ')
)))
tables.forEach((rows, i) => {
  if (rows.length < 2) return
  console.log(`\n[table#${i}] ${rows.length} rows`)
  rows.slice(0, 80).forEach(r => console.log('  ' + r))
})

// 連結（含 javascript 的編輯連結，帶 GUID）
const links = await page.$$eval('a', as => as.map(a => ({
  text: (a.innerText || a.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40),
  href: a.getAttribute('href'), onclick: (a.getAttribute('onclick') || '').slice(0, 120),
})).filter(x => x.text || x.onclick))
console.log(`\n[links] ${links.length}`)
links.slice(0, 120).forEach(l => console.log(`  ${l.text || '(no text)'}  ->  ${l.href}  ${l.onclick}`))

// 下拉選單（節點選擇器常在這裡）
const selects = await page.$$eval('select', ss => ss.map(s => ({
  name: s.getAttribute('name'), id: s.id,
  options: Array.from(s.options).map(o => `${o.value}=${o.text.replace(/\s+/g, ' ').trim()}`),
})))
selects.forEach(s => {
  console.log(`\n[select] ${s.id || s.name}  (${s.options.length})`)
  s.options.slice(0, 60).forEach(o => console.log('   ' + o))
})

await browser.close()
