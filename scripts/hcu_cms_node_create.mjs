// 在節點樹上「建立」子節點——走後台自己的 UI（右鍵選單 → 建立 → colorbox iframe 表單）。
//
// 🚨 NodeEditor.aspx 直接打網址會被踢回 NodeList（它認 iframe／Referer），一定要走 UI。
// 🚨 只在參數點名的父節點底下建立；不改名、不刪除、不搬動任何既有節點。
//
// 用法：
//   node scripts/hcu_cms_node_create.mjs --parent <父節點標題> --dump          # 只印表單欄位
//   node scripts/hcu_cms_node_create.mjs --parent <父節點標題> --name <節點名稱>  # 真的建立
import { chromium } from 'playwright'
const OUT = 'c:/tmp/hcu-cms'
function arg(n, d = null) { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : d }
const PARENT = arg('parent')
const NAME = arg('name')
const TEMPLATE = arg('template', '~/template/SingleData.aspx')   // 版型：單頁=SingleData、外連=URL.aspx
const URL_FIELD = arg('url')                                     // Template=URL.aspx 時要填的網址
const DUMP = process.argv.includes('--dump')
if (!PARENT) { console.error('要 --parent <父節點標題>'); process.exit(2) }

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: `${OUT}/state.json`, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()
page.on('dialog', async d => { console.log('[對話框]', d.message()); await d.accept() })
await page.goto('https://www.hcu.edu.tw/backend/MngCms/NodeList.aspx', { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(4000)

// 展開樹直到找到父節點（點 <ins> 展開箭頭，不點 <a>，因為 <a> 會導覽走）
async function expandTo(label) {
  for (let round = 0; round < 6; round++) {
    const a = page.locator(`#ctl00_cpContent_tree a:has-text("${label}")`).first()
    if (await a.count()) return a
    const closed = page.locator('#ctl00_cpContent_tree li.jstree-closed > ins')
    const n = await closed.count()
    if (!n) break
    for (let i = 0; i < n; i++) {
      await closed.nth(i).click({ timeout: 5000 }).catch(() => {})
      await page.waitForTimeout(700)
    }
    await page.waitForTimeout(1200)
  }
  return null
}
const node = await expandTo(PARENT)
if (!node) { console.log(`❌ 樹上找不到「${PARENT}」`); await page.screenshot({ path: `${OUT}/nodecreate-notfound.png`, fullPage: true }); await browser.close(); process.exit(1) }
console.log(`[父節點] ${PARENT}`)

await node.click({ button: 'right' })
await page.waitForTimeout(1200)
await page.locator('#vakata-contextmenu a:has-text("建立")').first().click()
await page.waitForTimeout(4000)

const frame = page.frames().find(f => /NodeEditor\.aspx/.test(f.url()))
if (!frame) { console.log('❌ 沒等到 NodeEditor 彈窗'); await page.screenshot({ path: `${OUT}/nodecreate-nodialog.png`, fullPage: true }); await browser.close(); process.exit(1) }
console.log(`[彈窗] ${frame.url()}`)

const fields = await frame.$$eval('input, select, textarea', els => els.map(e => ({
  tag: e.tagName, type: e.getAttribute('type'), name: e.getAttribute('name'), id: e.id,
  value: (e.value || '').slice(0, 40),
  options: e.tagName === 'SELECT' ? Array.from(e.options).map(o => `${o.value}=${o.text.trim()}`).slice(0, 20) : undefined,
})).filter(e => e.name && !/^__/.test(e.name)))
console.log('[表單欄位]')
for (const f of fields) console.log(`  ${f.tag}/${f.type || ''} name=${f.name} id=${f.id} value=${f.value}${f.options ? '\n      ' + f.options.join(' | ') : ''}`)
await page.screenshot({ path: `${OUT}/nodecreate-form.png`, fullPage: true })

if (DUMP || !NAME) { console.log('\n[dump] 不送出'); await browser.close(); process.exit(0) }

// 單頁型節點：Title＝選單上的名稱、IsList=false、版型選「文章內容」(SingleData)
await frame.fill('input[name="Title"]', NAME)
await frame.evaluate(() => {
  const r = document.querySelector('input[name="IsList"][value="false"]')
  if (r) { r.checked = true; r.dispatchEvent(new Event('click', { bubbles: true })) }
})
await frame.selectOption('select[name="Template"]', TEMPLATE).catch(e => console.log('[Template] 選不到:', e.message))
if (URL_FIELD) await frame.fill('input[name="Url"]', URL_FIELD).catch(e => console.log('[Url] 填不進去:', e.message))
await frame.selectOption('select[name="Enable"]', 'True').catch(() => {})
await frame.selectOption('select[name="Visible"]', 'True').catch(() => {})
await page.waitForTimeout(600)

const before = await frame.$$eval('select[name="Template"] option:checked, input[name="IsList"]:checked', els =>
  els.map(e => e.value || e.textContent))
console.log('[填好]', JSON.stringify({ name: NAME, state: before }))

const submit = frame.locator('#btNew, input[name="btNew"]').first()
await submit.click()
await page.waitForTimeout(4500)
await page.screenshot({ path: `${OUT}/nodecreate-after.png`, fullPage: true })
console.log('[完成] 已送出建立')
await browser.close()
