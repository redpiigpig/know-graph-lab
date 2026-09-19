// 補上節點附件的「描述」欄位並存檔。
//
// 🚨 為什麼需要這支：附件上傳成功、後台看得到檔案，但公開頁的「相關附件」區是空的——
//    因為描述（Description）是必填卻空著，樣板就不把那一筆畫出來。
//    「後台有檔」不等於「前台看得到」。
// 🚨 不用 hcu_cms_node_publish.mjs 重跑：那會再掛一份附件上去。
//
// 用法：node scripts/hcu_cms_node_attach_desc.mjs --node <rid> [--desc "顯示文字"]
import { existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
if (!existsSync(`${OUT}/state.json`)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }
function arg(n, d = null) { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : d }
const RID = arg('node'), DESC = arg('desc')
if (!RID) { console.error('要 --node <rid>'); process.exit(2) }

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: `${OUT}/state.json`, viewport: { width: 1440, height: 1100 } })
const page = await ctx.newPage()
const dialogs = []
page.on('dialog', async d => { dialogs.push(d.message()); await d.accept() })
await page.goto(`https://www.hcu.edu.tw/backend/MngCms/NodeContent.aspx?rid=${RID}`, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3500)
if (/login\.aspx/i.test(page.url())) { console.log('❌ session 過期'); await browser.close(); process.exit(1) }

const rows = await page.$$eval("[id='ucNodeContent$ctl05'] li.item", lis => lis.map(li => ({
  orig: (li.querySelector('.original-filename') || {}).value || '',
  descName: (li.querySelector('.Description') || {}).name || '',
  descValue: (li.querySelector('.Description') || {}).value || '',
})))
if (!rows.length) { console.log('（這個節點沒有附件）'); await browser.close(); process.exit(0) }

for (const r of rows) {
  const text = DESC || r.orig.replace(/\.docx?$/i, '')
  if (!r.descName) { console.log(`❓ 找不到描述欄位：${r.orig}`); continue }
  await page.fill(`input[name="${r.descName}"]`, text)
  console.log(`[描述] ${r.orig} → 「${text}」${r.descValue ? `（原本是「${r.descValue}」）` : '（原本是空的）'}`)
}

let btn = page.locator('#btnSubmit2')
if (!(await btn.isVisible().catch(() => false))) btn = page.locator('#btnSubmit')
await Promise.all([page.waitForLoadState('domcontentloaded').catch(() => {}), btn.click()])
await page.waitForTimeout(4000)
if (dialogs.length) console.log('[對話框]', dialogs)
await browser.close()
