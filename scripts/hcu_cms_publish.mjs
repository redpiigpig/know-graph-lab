// 在玄奘校網後台「臺灣佛教研究中心」站的某個節點下**新增一篇內容**（或改既有一篇），
// 內文 HTML 從檔案讀入，存檔後可一併按「發布」。
//
// 🚨 只動參數點名的那一篇。既有其他內容一律不碰（本腳本沒有刪除功能）。
// 🚨 ArchiveDate 要設成 9999 年，跟既有各期一致；預設值是「一年後」，放著會讓頁面一年後自動過期。
//
// 用法：
//   node scripts/hcu_cms_publish.mjs --node <rid> --title "第四十四期玄奘佛學研究" \
//        --html c:/tmp/hcu-cms/out/issue-44.html --date 2025-11-05 [--publish] [--dry]
//   node scripts/hcu_cms_publish.mjs --node <rid> --id <articleId> --html … [--publish]   # 改既有
import { readFileSync, existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
const STATE = `${OUT}/state.json`
if (!existsSync(STATE)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }

function arg(name, def = null) {
  const i = process.argv.indexOf(`--${name}`)
  return i > 0 ? process.argv[i + 1] : def
}
const NODE = arg('node')
const TITLE = arg('title')
const HTML_FILE = arg('html')
const DATE = arg('date')                       // 顯示日期 YYYY-MM-DD
const ID = arg('id')                           // 有給就是改既有那一篇
const DO_PUBLISH = process.argv.includes('--publish')
const DRY = process.argv.includes('--dry')
if (!NODE || !HTML_FILE || (!TITLE && !ID)) {
  console.error('缺參數：--node 與 --html 必填；新增要 --title，改既有要 --id')
  process.exit(2)
}
const body = readFileSync(HTML_FILE, 'utf8')

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: STATE, viewport: { width: 1440, height: 1100 } })
const page = await ctx.newPage()
const dialogs = []
page.on('dialog', async d => { dialogs.push(d.message()); await d.accept() })

const url = ID
  ? `https://www.hcu.edu.tw/backend/MngCms/ArticleEditor.aspx?id=${ID}&rid=${NODE}`
  : `https://www.hcu.edu.tw/backend/MngCms/ArticleEditor.aspx?rid=${NODE}`
await page.goto(url, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout
await page.waitForTimeout(3500)
if (/login\.aspx/i.test(page.url())) { console.log('❌ session 過期，重跑 hcu_cms_login.mjs'); await browser.close(); process.exit(1) }

if (TITLE) await page.fill('input[name="Title"]', TITLE)
if (DATE) {
  await page.fill('input[name="DisplayDate"]', DATE)
  // 🚨 生效時間要是「已經到了」的時刻。設當天 08:00 而現在才凌晨的話，
  //    後台狀態會是「等待」，公開端直接 404——而後台看起來一切正常、也不會報錯。
  await page.fill('input[name="PublishDate"]', `${DATE}T00:00`)
}
// 不過期：跟既有各期一樣設 9999 年
const ad = await page.locator('input[name="ArchiveDate"]').inputValue().catch(() => '')
if (!/^9999/.test(ad)) await page.fill('input[name="ArchiveDate"]', '9999-12-31T00:00')

// 內容段落：既有那篇是 Modify$Content$1；新增的要先按「增加內容」生出 Add$Content$1
let target = 'textarea[name="ucArticle$ctl07$Modify$Content$1"]'
if (!(await page.locator(target).count())) {
  const add = page.locator('#ucArticle\\$ctl07 a.bottom-add, #ucArticle\\$ctl07 a.add').first()
  await add.click()
  await page.waitForTimeout(2500)
  target = 'textarea[name="ucArticle$ctl07$Add$Content$1"]'
  if (!(await page.locator(target).count())) {
    const names = await page.$$eval('textarea', ts => ts.map(t => t.getAttribute('name')))
    console.log('❌ 按了「增加內容」還是找不到內文欄位，現有 textarea：', names)
    await page.screenshot({ path: `${OUT}/publish-fail.png`, fullPage: true })
    await browser.close(); process.exit(1)
  }
}
console.log(`[內文欄位] ${target}`)

// 🚨 CKEditor 掛在那個 textarea 上，而 **instance 的 key 是欄位 name，不是 id**
//    （這些 textarea 根本沒有 id）。用 id 去找會找不到 instance、退回塞裸 textarea，
//    然後送出時 CKEditor 會用它自己的（空）內容覆蓋回去——存出來就是一片空白。
const fieldName = target.match(/name="([^"]+)"/)[1]
const setVia = await page.evaluate(({ name, html }) => {
  const ta = document.querySelector(`textarea[name="${name}"]`)
  if (!ta) return 'no-textarea'
  const ck = window.CKEDITOR && (window.CKEDITOR.instances[name] || (ta.id && window.CKEDITOR.instances[ta.id]))
  if (ck) { ck.setData(html); return 'ckeditor' }
  ta.value = html
  ta.dispatchEvent(new Event('change', { bubbles: true }))
  return 'textarea'
}, { name: fieldName, html: body })
await page.waitForTimeout(1500)
// 讀回來確認真的進去了（別只信 setData 沒報錯）
const check = await page.evaluate(name => {
  const ck = window.CKEDITOR && window.CKEDITOR.instances[name]
  const ta = document.querySelector(`textarea[name="${name}"]`)
  return { ck: ck ? ck.getData().length : null, ta: ta ? ta.value.length : null }
}, fieldName)
console.log(`[灌內容] 方式=${setVia}  來源 ${body.length} chars  → CKEditor ${check.ck} / textarea ${check.ta}`)
if (setVia === 'ckeditor' && !check.ck) {
  console.log('❌ CKEditor 讀回 0 字，內容沒進去，停止')
  await browser.close(); process.exit(1)
}

await page.screenshot({ path: `${OUT}/publish-before-save.png`, fullPage: true })
if (DRY) { console.log('[dry] 不存檔，結束'); await browser.close(); process.exit(0) }

// 存檔（新增／儲存都是 btnSubmit）
// 🚨 頁面上有兩顆同名的鈕：#btnSubmit（type=submit，被 CSS 藏起來）與
//    #btnSubmit2（type=button，真正看得見、會先跑前端驗證再送出）。
//    點 #btnSubmit 會卡在「element is not visible」直到逾時。
let btn = page.locator('#btnSubmit2')
if (!(await btn.isVisible().catch(() => false))) btn = page.locator('#btnSubmit')
const label = await btn.inputValue().catch(() => '')
console.log(`[送出] 按「${label}」`)
await Promise.all([page.waitForLoadState('domcontentloaded').catch(() => {}), btn.click()])
await page.waitForTimeout(4000)
console.log(`[送出後] url=${page.url()}`)
if (dialogs.length) console.log('[對話框]', dialogs)
await page.screenshot({ path: `${OUT}/publish-after-save.png`, fullPage: true })

// 新增成功後會轉回清單，**新文章的 id 就在 url 的 ?id= 裡**——比回頭爬清單可靠。
const fromUrl = (page.url().match(/[?&]id=([0-9A-Fa-f]{32})/) || [])[1] || null
if (fromUrl) console.log(`[新增] id=${fromUrl}`)

// 回清單找這一篇，取 id 並（可選）發布
await page.goto(`https://www.hcu.edu.tw/backend/MngCms/ArticleList.aspx?rid=${NODE}`, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3500)
const found = await page.evaluate(t => {
  const rows = Array.from(document.querySelectorAll('#content, body'))
  const html = document.body.innerHTML
  const re = new RegExp(`ArticleEditor\\.aspx\\?id=([0-9A-F]{32})[^>]*>修改[\\s\\S]{0,400}?${t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`)
  const m = html.match(re)
  return m ? m[1] : null
}, TITLE || '')
console.log(`[清單] 找到 id=${found || '(清單比對失敗)'}`)
const articleId = ID || fromUrl || found

if (DO_PUBLISH && articleId) {
  const aid = articleId
  await page.evaluate(({ aid, rid }) => window.PublicEditor(aid, rid), { aid, rid: NODE })
  await page.waitForTimeout(4000)
  console.log('[發布] 已呼叫 PublicEditor')
  if (dialogs.length) console.log('[對話框]', dialogs)
  await page.screenshot({ path: `${OUT}/publish-after-public.png`, fullPage: true })
}

await browser.close()
