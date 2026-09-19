// 讀出後台某一篇內容（ArticleEditor.aspx）的表單欄位與 HTML 原稿——**只讀，不按儲存**。
// 用來照既有格式做新內容；例：拿第四十三期當範本再上第四十四、四十五期。
//
// 用法：node scripts/hcu_cms_article_dump.mjs <articleId> <nodeRid> [tag]
import { readFileSync, writeFileSync, existsSync } from 'fs'
import { chromium } from 'playwright'

const OUT = 'c:/tmp/hcu-cms'
const STATE = `${OUT}/state.json`
if (!existsSync(STATE)) { console.error('先跑 hcu_cms_login.mjs'); process.exit(2) }

const [id, rid, tagArg] = process.argv.slice(2)
if (!id || !rid) { console.error('用法：node scripts/hcu_cms_article_dump.mjs <articleId|NEW> <nodeRid> [tag]'); process.exit(2) }
const tag = tagArg || `article-${id.slice(0, 8)}`
// id 給 NEW 就開「新增」那張空白表單（ArticleEditor.aspx?rid=… 不帶 id）
const editorUrl = id === 'NEW'
  ? `https://www.hcu.edu.tw/backend/MngCms/ArticleEditor.aspx?rid=${rid}`
  : `https://www.hcu.edu.tw/backend/MngCms/ArticleEditor.aspx?id=${id}&rid=${rid}`

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: STATE, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()
await page.goto(editorUrl, { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(3000)

if (/login\.aspx/i.test(page.url())) { console.log('❌ session 過期'); await browser.close(); process.exit(1) }
console.log(`[url] ${page.url()}`)

// 表單欄位
const inputs = await page.$$eval('input, select, textarea', els => els.map(e => ({
  tag: e.tagName, type: e.getAttribute('type'), name: e.getAttribute('name'), id: e.id,
  value: e.tagName === 'TEXTAREA' ? `<len ${(e.value || '').length}>` : (e.value || '').slice(0, 60),
})).filter(e => e.name && !/^__/.test(e.name)))
console.log('\n[fields]')
for (const f of inputs) console.log(`  ${f.tag}/${f.type || ''}  name=${f.name}  id=${f.id}  value=${f.value}`)

// 富文字編輯器：CKEditor/TinyMCE 多半塞在 iframe，或以 textarea 為載體
const texts = await page.$$eval('textarea', ts => ts.map(t => ({ id: t.id, name: t.getAttribute('name'), html: t.value })))
for (const t of texts) {
  if (!t.html) continue
  const fn = `${OUT}/${tag}-${(t.id || t.name || 'ta').replace(/[^\w.-]/g, '_')}.html`
  writeFileSync(fn, t.html, 'utf8')
  console.log(`\n[textarea] ${t.id || t.name}  ${t.html.length} chars -> ${fn}`)
}
for (const [i, f] of page.frames().entries()) {
  if (f === page.mainFrame()) continue
  try {
    const html = await f.evaluate(() => document.body ? document.body.innerHTML : '')
    if (html && html.length > 40) {
      const fn = `${OUT}/${tag}-frame${i}.html`
      writeFileSync(fn, html, 'utf8')
      console.log(`[frame#${i}] ${f.url().slice(0, 80)}  ${html.length} chars -> ${fn}`)
    }
  } catch {}
}

writeFileSync(`${OUT}/${tag}-page.html`, await page.content(), 'utf8')
await page.screenshot({ path: `${OUT}/${tag}.png`, fullPage: true })
console.log(`\n[snap] ${OUT}/${tag}.png`)
await browser.close()
