// 把 HTML 灌進「單頁型節點」的節點內容（NodeContent.aspx），並可一併掛一個附件（Word）。
//
// 用在 Template=SingleData 的節點：那種節點沒有「文章」，內容在節點自己身上
// （ArticleEditor 找不到 Title 欄位就是這個原因）。
//
// 🚨 只動參數點名的那一個節點；不建立、不刪除節點。
//
// 用法：
//   node scripts/hcu_cms_node_publish.mjs --node <rid> --html <檔> [--attach <docx>] [--dry]
import { readFileSync, existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
const STATE = `${OUT}/state.json`
if (!existsSync(STATE)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }
function arg(n, d = null) { const i = process.argv.indexOf(`--${n}`); return i > 0 ? process.argv[i + 1] : d }
const RID = arg('node'), HTML = arg('html'), ATTACH = arg('attach')
const DRY = process.argv.includes('--dry')
if (!RID || !HTML) { console.error('要 --node <rid> 與 --html <檔>'); process.exit(2) }
const body = readFileSync(HTML, 'utf8')

const CT07 = "[id='ucNodeContent$ctl07']"
const CT05 = "[id='ucNodeContent$ctl05']"

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: STATE, viewport: { width: 1440, height: 1100 } })
const page = await ctx.newPage()
const dialogs = []
page.on('dialog', async d => { dialogs.push(d.message()); await d.accept() })
await page.goto(`https://www.hcu.edu.tw/backend/MngCms/NodeContent.aspx?rid=${RID}`, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3500)
if (/login\.aspx/i.test(page.url())) { console.log('❌ session 過期'); await browser.close(); process.exit(1) }

// 內容：已有段落就改它，沒有就按「增加內容」長一個
let field = 'ucNodeContent$ctl07$Modify$Content$1'
if (!(await page.locator(`textarea[name="${field}"]`).count())) {
  await page.locator(`${CT07} a.bottom-add, ${CT07} a.add`).first().click()
  await page.waitForTimeout(2500)
  field = 'ucNodeContent$ctl07$Add$Content$1'
}
if (!(await page.locator(`textarea[name="${field}"]`).count())) {
  console.log('❌ 找不到內容欄位'); await page.screenshot({ path: `${OUT}/nodepub-fail.png`, fullPage: true })
  await browser.close(); process.exit(1)
}
// 🚨 CKEditor 的 instance key 是欄位 name（textarea 沒有 id）；用 id 找不到就會退回塞裸
//    textarea，送出時被 CKEditor 的空內容覆蓋。
const via = await page.evaluate(({ name, html }) => {
  const ta = document.querySelector(`textarea[name="${name}"]`)
  const ck = window.CKEDITOR && window.CKEDITOR.instances[name]
  if (ck) { ck.setData(html); return 'ckeditor' }
  if (ta) { ta.value = html; return 'textarea' }
  return 'none'
}, { name: field, html: body })
await page.waitForTimeout(1500)
const len = await page.evaluate(name => {
  const ck = window.CKEDITOR && window.CKEDITOR.instances[name]
  return ck ? ck.getData().length : null
}, field)
console.log(`[內容] ${field}  方式=${via}  來源 ${body.length} → CKEditor ${len}`)
if (via === 'ckeditor' && !len) { console.log('❌ CKEditor 讀回 0 字'); await browser.close(); process.exit(1) }

// 附件：按「增加附件」後在該區塊的 file input 放檔
if (ATTACH) {
  await page.locator(`${CT05} a.bottom-add, ${CT05} a.add`).first().click()
  await page.waitForTimeout(2000)
  const fi = page.locator(`${CT05} input[type=file]`).first()
  if (!(await fi.count())) { console.log('❌ 附件區沒有 file input') }
  else {
    await fi.setInputFiles(ATTACH)
    await page.waitForTimeout(3000)
    const desc = page.locator(`${CT05} input[type=text]`).first()
    if (await desc.count()) {
      const name = ATTACH.split(/[\/]/).pop().replace(/\.docx?$/i, '')
      await desc.fill(name)
      console.log(`[附件] ${name}`)
    } else console.log('[附件] 已選檔（無說明欄）')
  }
}

await page.screenshot({ path: `${OUT}/nodepub-before-save.png`, fullPage: true })
if (DRY) { console.log('[dry] 不存檔'); await browser.close(); process.exit(0) }

let btn = page.locator('#btnSubmit2')
if (!(await btn.isVisible().catch(() => false))) btn = page.locator('#btnSubmit')
await Promise.all([page.waitForLoadState('domcontentloaded').catch(() => {}), btn.click()])
await page.waitForTimeout(4500)
console.log(`[送出後] url=${page.url()}`)
if (dialogs.length) console.log('[對話框]', dialogs)
await page.screenshot({ path: `${OUT}/nodepub-after-save.png`, fullPage: true })
await browser.close()
