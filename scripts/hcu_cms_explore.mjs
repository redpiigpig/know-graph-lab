// 探玄奘校網後台（www.hcu.edu.tw/backend）的結構——只讀，不送出任何表單。
//
// 🚨 這是校方正式官網：本腳本只做 GET／點選導覽，絕不按儲存或刪除。
// 帳密在 .env 的 HCU_WEB_CMS_URL / HCU_WEB_CMS_USER / HCU_WEB_CMS_PASS。
//
// 用法：node scripts/hcu_cms_explore.mjs [--headless]
import { readFileSync, writeFileSync, mkdirSync } from 'fs'
import { chromium } from 'playwright'

const ROOT = new URL('..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')
const OUT = 'c:/tmp/hcu-cms'

function env(name) {
  for (const line of readFileSync(`${ROOT}/.env`, 'utf8').split(/\r?\n/)) {
    if (line.startsWith(`${name}=`)) return line.slice(name.length + 1).trim()
  }
  throw new Error(`.env 缺 ${name}`)
}

const URL_LOGIN = env('HCU_WEB_CMS_URL')
const USER = env('HCU_WEB_CMS_USER')
const PASS = env('HCU_WEB_CMS_PASS')
const headless = process.argv.includes('--headless')

mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch({ headless, channel: headless ? undefined : 'chrome' })
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
const page = await ctx.newPage()

async function snap(tag) {
  await page.screenshot({ path: `${OUT}/${tag}.png`, fullPage: false })
  writeFileSync(`${OUT}/${tag}.html`, await page.content(), 'utf8')
  console.log(`[snap] ${tag}  url=${page.url()}`)
}

await page.goto(URL_LOGIN, { waitUntil: 'domcontentloaded' })
await snap('01-login')

// 登入表單欄位名未知：抓出所有 input 的 name/type/id 供判斷
const fields = await page.$$eval('input, select, button', els => els.map(e => ({
  tag: e.tagName, type: e.getAttribute('type'), name: e.getAttribute('name'),
  id: e.id, value: e.getAttribute('type') === 'password' ? '<pw>' : (e.value || '').slice(0, 30),
})))
console.log('[login fields]', JSON.stringify(fields, null, 1))

// 依欄位型別填：第一個 text → 帳號，第一個 password → 密碼
const userSel = 'input[type=text]:not([disabled])'
const passSel = 'input[type=password]'
if (await page.locator(userSel).count()) {
  await page.locator(userSel).first().fill(USER)
  await page.locator(passSel).first().fill(PASS)
  const submit = page.locator('input[type=submit], button[type=submit], input[type=image]').first()
  if (await submit.count()) {
    await Promise.all([
      page.waitForLoadState('domcontentloaded').catch(() => {}),
      submit.click(),
    ])
    await page.waitForTimeout(2500)
  }
}
await snap('02-after-login')

// 登入後把所有連結與 frame 撈出來，找「臺灣佛教研究中心」與「新增網頁」之類的入口
async function dumpLinks(frame, label) {
  const links = await frame.$$eval('a', as => as.map(a => ({
    text: (a.innerText || a.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 40),
    href: a.getAttribute('href'),
  })).filter(x => x.text))
  console.log(`\n[links:${label}] ${links.length}`)
  for (const l of links) console.log(`  ${l.text}  ->  ${l.href}`)
  return links
}

const frames = page.frames()
console.log(`\n[frames] ${frames.length}`)
for (const [i, f] of frames.entries()) {
  console.log(`  frame#${i} name=${f.name()} url=${f.url()}`)
  try { await dumpLinks(f, `frame${i}`) } catch (e) { console.log(`   (dump failed: ${e.message})`) }
}

writeFileSync(`${OUT}/frames.txt`, frames.map(f => `${f.name()}\t${f.url()}`).join('\n'), 'utf8')
console.log(`\n產物在 ${OUT}（png + html）。瀏覽器先留著不關，供人工確認。`)
if (headless) await browser.close()
else await page.waitForTimeout(600000)
