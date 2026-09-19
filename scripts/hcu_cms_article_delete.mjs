// 刪除某節點底下指定 id 的內容——只刪參數點名的那幾個 id。
//
// 🚨 沒有「批次刪除」「依標題刪除」這種模式：一定要明確給 id，
//    因為這是校方正式官網，刪錯就是對外可見的資料消失。
//
// 用法：node scripts/hcu_cms_article_delete.mjs --node <rid> <articleId> [<articleId>…]
import { existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
if (!existsSync(`${OUT}/state.json`)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }
const i = process.argv.indexOf('--node')
const RID = i > 0 ? process.argv[i + 1] : null
// 🚨 節點 rid 也是 32 位十六進位，要排除，否則會拿 rid 去當文章 id 刪
const IDS = process.argv.slice(2).filter(a => /^[0-9A-Fa-f]{32}$/.test(a) && a.toUpperCase() !== String(RID).toUpperCase())
if (!RID || !IDS.length) { console.error('要 --node <rid> 與至少一個 32 位 id'); process.exit(2) }

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: `${OUT}/state.json`, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()
const dialogs = []
page.on('dialog', async d => { dialogs.push(d.message()); await d.accept() })

for (const id of IDS) {
  // 🚨 直接打 ArticleDelete.aspx 會被踢回 login.aspx（它認 iframe／Referer），
  //    要走清單頁上那個 class="dialog" 的「刪除」連結，再在彈出的 iframe 裡按確認。
  await page.goto(`https://www.hcu.edu.tw/backend/MngCms/ArticleList.aspx?rid=${RID}`, { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(3000)
  if (/login\.aspx/i.test(page.url())) { console.log('❌ session 過期，重跑 hcu_cms_login.mjs'); break }
  const link = page.locator(`a.dialog[href*="${id}"]`).first()
  if (!(await link.count())) { console.log(`❓ ${id} 清單上找不到刪除連結（可能已刪）`); continue }
  await link.click()
  await page.waitForTimeout(3000)
  const frame = page.frames().find(f => /ArticleDelete\.aspx/.test(f.url()))
  if (!frame) { console.log(`❓ ${id} 沒等到刪除彈窗`); continue }
  const btn = frame.locator('input[type=submit], button[type=submit]').first()
  const label = await btn.inputValue().catch(() => '(button)')
  await btn.click()
  await page.waitForTimeout(3000)
  console.log(`🗑 ${id}  按「${label}」`)
}
if (dialogs.length) console.log('[對話框]', dialogs)

// 刪完回清單點名剩下什麼
await page.goto(`https://www.hcu.edu.tw/backend/MngCms/ArticleList.aspx?rid=${RID}`, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3000)
const left = await page.$$eval('#content, body', () => {
  const html = document.body.innerHTML
  return [...html.matchAll(/ArticleEditor\.aspx\?id=([0-9A-F]{32})/g)].map(m => m[1])
})
console.log(`[清單] 現有內容 ${new Set(left).size} 筆`)
for (const id of IDS) if (left.includes(id)) console.log(`   ❌ ${id} 還在清單裡`)
await browser.close()
