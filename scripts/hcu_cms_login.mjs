// 登入玄奘校網後台（www.hcu.edu.tw/backend）。登入頁有圖形驗證碼，所以分兩段：
//   1. 本腳本把驗證碼存成 c:/tmp/hcu-cms/captcha.png 然後等 captcha.txt
//   2. 人（或 Claude 讀圖）把答案寫進 c:/tmp/hcu-cms/captcha.txt，腳本續跑
// 登入成功後把 cookie 存進 c:/tmp/hcu-cms/state.json 供後續腳本沿用（ASP.NET session 有閒置逾時）。
//
// 🚨 這是校方正式官網：本腳本只登入與瀏覽，不送出任何內容表單。
//
// 用法：node scripts/hcu_cms_login.mjs [--headless] [--goto <url>]
import { readFileSync, writeFileSync, existsSync, unlinkSync, mkdirSync } from 'fs'
import { chromium } from 'playwright'

const ROOT = new URL('..', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')
const OUT = 'c:/tmp/hcu-cms'
const ANSWER = `${OUT}/captcha.txt`

function env(name) {
  for (const line of readFileSync(`${ROOT}/.env`, 'utf8').split(/\r?\n/)) {
    if (line.startsWith(`${name}=`)) return line.slice(name.length + 1).trim()
  }
  throw new Error(`.env 缺 ${name}`)
}

const headless = process.argv.includes('--headless')
const gotoIdx = process.argv.indexOf('--goto')
const gotoUrl = gotoIdx > 0 ? process.argv[gotoIdx + 1] : null

mkdirSync(OUT, { recursive: true })
if (existsSync(ANSWER)) unlinkSync(ANSWER)

const browser = await chromium.launch({ headless, channel: headless ? undefined : 'chrome' })
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } })
const page = await ctx.newPage()

await page.goto(env('HCU_WEB_CMS_URL'), { waitUntil: 'domcontentloaded' })
await page.fill('#txAccount', env('HCU_WEB_CMS_USER'))
await page.fill('#txPWD', env('HCU_WEB_CMS_PASS'))

// 驗證碼圖：放大三倍存檔，讀起來清楚些
const img = page.locator('img.Vaild').first()
await img.screenshot({ path: `${OUT}/captcha.png`, scale: 'css' })
await page.evaluate(() => {
  const i = document.querySelector('img.Vaild')
  if (i) { i.style.transform = 'scale(3)'; i.style.transformOrigin = 'left top' }
})
await page.waitForTimeout(200)
await img.screenshot({ path: `${OUT}/captcha-3x.png`, scale: 'css' }).catch(() => {})
await page.evaluate(() => {
  const i = document.querySelector('img.Vaild')
  if (i) i.style.transform = ''
})
console.log(`[captcha] 已存 ${OUT}/captcha.png（與 captcha-3x.png）。把答案寫進 ${ANSWER} …`)

let code = null
for (let i = 0; i < 300 && !code; i++) {
  if (existsSync(ANSWER)) {
    const t = readFileSync(ANSWER, 'utf8').trim()
    if (t) code = t
  }
  if (!code) await page.waitForTimeout(2000)
}
if (!code) { console.log('[captcha] 等不到答案，放棄'); await browser.close(); process.exit(2) }
console.log(`[captcha] 收到 ${code.length} 碼，送出登入`)

await page.fill('#txVerification', code)
await Promise.all([
  page.waitForLoadState('domcontentloaded').catch(() => {}),
  page.click('#btLogin'),
])
await page.waitForTimeout(3000)

const url = page.url()
const stillLogin = /login\.aspx/i.test(url)
console.log(`[login] url=${url}  ${stillLogin ? '❌ 仍在登入頁' : '✅ 已進入後台'}`)
await page.screenshot({ path: `${OUT}/10-after-login.png` })
writeFileSync(`${OUT}/10-after-login.html`, await page.content(), 'utf8')

if (stillLogin) {
  const msg = await page.$$eval('span, div.error, .alert, td', els => els
    .map(e => (e.innerText || '').replace(/\s+/g, ' ').trim())
    .filter(t => t && t.length < 60 && /(錯誤|驗證|失敗|帳號|密碼)/.test(t)).slice(0, 6))
  console.log('[login] 頁面訊息：', JSON.stringify(msg))
  await browser.close()
  process.exit(1)
}

await ctx.storageState({ path: `${OUT}/state.json` })
console.log(`[state] cookie 已存 ${OUT}/state.json`)

if (gotoUrl) {
  await page.goto(gotoUrl, { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(1500)
  await page.screenshot({ path: `${OUT}/11-goto.png`, fullPage: true })
  writeFileSync(`${OUT}/11-goto.html`, await page.content(), 'utf8')
  console.log(`[goto] ${page.url()}`)
}

// 把後台的導覽結構撈出來
for (const [i, f] of page.frames().entries()) {
  console.log(`\n[frame#${i}] name=${f.name()} url=${f.url()}`)
  try {
    const links = await f.$$eval('a', as => as.map(a => ({
      text: (a.innerText || a.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 44),
      href: a.getAttribute('href'),
    })).filter(x => x.text))
    for (const l of links) console.log(`   ${l.text}  ->  ${l.href}`)
  } catch (e) { console.log(`   (dump failed: ${e.message})`) }
}

await browser.close()
