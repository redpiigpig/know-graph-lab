// 把 HTML 灌進「列表型節點」的節點內容（清單頁工具列的『節點內容』彈窗）。
//
// 🚨 列表型節點沒有 NodeContent.aspx：直接打會被轉回 ArticleList.aspx。
//    它的節點內容在 NodeContentDialog.aspx，而且要從清單頁的連結點開（認 iframe）。
//    這跟單頁型節點（用 hcu_cms_node_publish.mjs）是兩條不同的路。
//
// 用法：node scripts/hcu_cms_node_dialog.mjs --node <rid> --html <檔> [--dry]
import { readFileSync, existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
if (!existsSync(`${OUT}/state.json`)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }
function arg(n, d = null) { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : d }
const RID = arg('node'), HTML = arg('html')
const DRY = process.argv.includes('--dry')
if (!RID || !HTML) { console.error('要 --node 與 --html'); process.exit(2) }
const body = readFileSync(HTML, 'utf8')

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: `${OUT}/state.json`, viewport: { width: 1440, height: 1100 } })
const page = await ctx.newPage()
const dialogs = []
page.on('dialog', async d => { dialogs.push(d.message()); await d.accept() })
await page.goto(`https://www.hcu.edu.tw/backend/MngCms/ArticleList.aspx?rid=${RID}`, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3500)
if (/login\.aspx/i.test(page.url())) { console.log('❌ session 過期'); await browser.close(); process.exit(1) }

const link = page.locator(`a[href*="NodeContentDialog.aspx"]`).first()
if (!(await link.count())) { console.log('❌ 清單頁上沒有「節點內容」連結'); await browser.close(); process.exit(1) }
await link.click()
await page.waitForTimeout(4500)
const frame = page.frames().find(f => /NodeContentDialog/.test(f.url()))
if (!frame) { console.log('❌ 沒等到節點內容彈窗'); await page.screenshot({ path: `${OUT}/nodedlg-fail.png`, fullPage: true }); await browser.close(); process.exit(1) }
console.log(`[彈窗] ${frame.url()}`)

// 找內容區塊（欄位前綴可能是 ucNodeContent 或別的，一律用 name 裡含 Content$ 來抓）
let name = await frame.$$eval('textarea', ts => {
  const t = ts.find(x => /Content\$\d+$/.test(x.getAttribute('name') || ''))
  return t ? t.getAttribute('name') : null
})
if (!name) {
  const add = frame.locator('a.bottom-add, a.add').last()
  if (await add.count()) { await add.click(); await page.waitForTimeout(2500) }
  name = await frame.$$eval('textarea', ts => {
    const t = ts.find(x => /Content\$\d+$/.test(x.getAttribute('name') || ''))
    return t ? t.getAttribute('name') : null
  })
}
if (!name) {
  const names = await frame.$$eval('input,textarea,select', els => els.map(e => e.getAttribute('name')).filter(Boolean))
  console.log('❌ 找不到內容欄位。彈窗欄位：', JSON.stringify(names.slice(0, 40)))
  await browser.close(); process.exit(1)
}
const via = await frame.evaluate(({ n, html }) => {
  const ta = document.querySelector(`textarea[name="${n}"]`)
  const ck = window.CKEDITOR && window.CKEDITOR.instances[n]
  if (ck) { ck.setData(html); return 'ckeditor' }
  if (ta) { ta.value = html; return 'textarea' }
  return 'none'
}, { n: name, html: body })
await page.waitForTimeout(1500)
const len = await frame.evaluate(n => {
  const ck = window.CKEDITOR && window.CKEDITOR.instances[n]
  return ck ? ck.getData().length : null
}, name)
console.log(`[內容] ${name}  方式=${via}  來源 ${body.length} → CKEditor ${len}`)
await page.screenshot({ path: `${OUT}/nodedlg-before.png`, fullPage: true })
if (DRY) { console.log('[dry] 不存檔'); await browser.close(); process.exit(0) }

let btn = frame.locator('#btnSubmit2')
if (!(await btn.isVisible().catch(() => false))) btn = frame.locator('#btnSubmit, input[type=submit]').first()
await btn.click()
await page.waitForTimeout(4500)
if (dialogs.length) console.log('[對話框]', dialogs)
await page.screenshot({ path: `${OUT}/nodedlg-after.png`, fullPage: true })
await browser.close()
