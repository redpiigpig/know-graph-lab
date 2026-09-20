// 把某節點底下**所有**內容的原稿撈下來（分頁會自動翻），存成
//   <out>/<id>.html（內文 HTML）與 <out>/index.json（id／標題／顯示日期）。
//
// 用途：要把既有各期頁重排版面時，資料就在這些原稿裡（中英篇名／作者／頁數／PDF 連結），
// 不必回去爬別的站。
//
// 🚨 只讀：不按儲存、不刪除。
//
// 用法：node scripts/hcu_cms_dump_node_articles.mjs --node <rid> [--out c:/tmp/hcu-cms/old]
import { writeFileSync, readFileSync, mkdirSync, existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT_ROOT = 'c:/tmp/hcu-cms'
if (!existsSync(`${OUT_ROOT}/state.json`)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }
function arg(n, d = null) { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : d }
const RID = arg('node')
const OUT = arg('out', `${OUT_ROOT}/old`)
if (!RID) { console.error('要 --node <rid>'); process.exit(2) }
mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: `${OUT_ROOT}/state.json`, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()

// 要撈哪些 id：--ids <json>（{期號: 公開頁URL} 或 [{id,title}]）優先，
// 否則從清單頁抓——🚨 清單是 JS 表格（paramquery），`?page=` 沒用、只會一直給第一頁 20 筆，
// 所以有 --ids 就別走清單。
const rows = new Map()
const idsFile = arg('ids')
if (idsFile) {
  const raw = JSON.parse(readFileSync(idsFile, 'utf8'))
  const entries = Array.isArray(raw)
    ? raw.map(r => [r.id, r.title || ''])
    : Object.entries(raw).map(([k, v]) => [String(v).match(/([0-9A-Fa-f]{32})\/?$/)?.[1], `第${k}期`])
  for (const [id, title] of entries) if (id) rows.set(id.toUpperCase(), { id: id.toUpperCase(), title, date: '' })
  console.log(`[來源] ${idsFile} → ${rows.size} 筆`)
} else {
  await page.goto(`https://www.hcu.edu.tw/backend/MngCms/ArticleList.aspx?rid=${RID}`, { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(2500)
  const got = await page.evaluate(() => {
    const out = []
    document.querySelectorAll('tr.pq-grid-row').forEach(tr => {
      const a = tr.querySelector('a[href*="ArticleEditor.aspx?id="]')
      if (!a) return
      const id = (a.getAttribute('href').match(/id=([0-9A-F]{32})/) || [])[1]
      const cells = Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim())
      out.push({ id, cells })
    })
    return out
  })
  for (const g of got) {
    const title = g.cells.find(c => /期玄奘佛學研究/.test(c)) || ''
    if (g.id && !rows.has(g.id)) rows.set(g.id, { id: g.id, title, date: '' })
  }
  console.log(`[清單] ${rows.size} 筆（只有第一頁，要全部請用 --ids）`)
}

// 逐篇開編輯頁，把內文 textarea 的原稿存下來
let n = 0
for (const r of rows.values()) {
  await page.goto(`https://www.hcu.edu.tw/backend/MngCms/ArticleEditor.aspx?id=${r.id}&rid=${RID}`,
    { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(2200)
  const html = await page.evaluate(() => {
    const ta = Array.from(document.querySelectorAll('textarea'))
      .find(t => /Content\$\d+$/.test(t.getAttribute('name') || ''))
    return ta ? ta.value : ''
  })
  if (!html) { console.log(`  ❓ ${r.title || r.id} 沒有內文`); continue }
  writeFileSync(`${OUT}/${r.id}.html`, html, 'utf8')
  n++
  if (n % 10 === 0) console.log(`  …已存 ${n} 篇`)
}
writeFileSync(`${OUT}/index.json`, JSON.stringify([...rows.values()], null, 1), 'utf8')
console.log(`\n共 ${rows.size} 筆、存下 ${n} 篇原稿 → ${OUT}`)
await browser.close()
