/**
 * 查 z-library 帳號的實際每日下載額度與升級選項。
 *
 * 只讀不寫：沿用 zlib_fetch.mjs 已存的登入 state，開 profile 與 donate 頁把數字抓下來。
 * 「免費就是 10 本嗎、捐款能不能加」這種問題別靠記憶回答，站方條件常改，跑這支看當下的。
 *
 *   node scripts/zlib_account.mjs
 */
import { chromium } from 'playwright'
import { readFileSync, existsSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const HOST = 'https://z-library.sk'
const STATE = 'c:/tmp/zlib_state.json'

function env() {
  const out = {}
  for (const line of readFileSync(resolve(ROOT, '.env'), 'utf-8').split(/\r?\n/)) {
    const m = line.match(/^([A-Z0-9_]+)=(.*)$/)
    if (m) out[m[1]] = m[2].trim()
  }
  return out
}

async function gotoPastWall(page, url, tries = 3) {
  const blocked = (t) => /DiamWall|验证|驗證|Verifying/i.test(t)
  for (let i = 0; i < tries; i++) {
    // DiamWall 慢起來會吃掉整個 60s，逾時不該讓整支掛掉——換下一輪重試就好
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 })
    } catch (err) {
      console.log(`  goto 逾時（第 ${i + 1} 次）: ${String(err).split('\n')[0]}`)
      continue
    }
    if (!blocked(await page.title())) return true
    await page.waitForTimeout(15000)
    if (!blocked(await page.title())) return true
  }
  return false
}

const e = env()
const browser = await chromium.launch({ headless: false, channel: 'chrome' })
const context = await browser.newContext({
  locale: 'zh-TW',
  ...(existsSync(STATE) ? { storageState: STATE } : {}),
})
const page = await context.newPage()

try {
  await gotoPastWall(page, `${HOST}/`)
  console.log('首頁 title:', await page.title(), '| url:', page.url())
  const logged = await page.locator('a[href*="/logout"], [href*="/profile"]').count()
  console.log('登入中?', logged > 0)
  if (!logged) {
    await gotoPastWall(page, `${HOST}/login`)
    await page.fill('input[name="email"]', e.ZLIB_EMAIL).catch(() => {})
    await page.fill('input[name="password"]', e.ZLIB_PASSWORD).catch(() => {})
    await page.click('button[type="submit"], input[type="submit"]').catch(() => {})
    await page.waitForTimeout(8000)
    console.log('登入後 url:', page.url())
  }

  // 捐款頁的路徑會改（/plans.php 與 /donate 都已 404），別再寫死 —— 從 profile
  // 頁把 Donate 連結的實際 href 抓出來再走。
  await gotoPastWall(page, `${HOST}/profile`)
  const donateHref = await page.evaluate(() => {
    const a = [...document.querySelectorAll('a')]
      .find((x) => /donate|premium|plan|subscri/i.test(x.textContent + ' ' + x.getAttribute('href')))
    return a ? a.getAttribute('href') : null
  })
  console.log('profile 頁上的 Donate 連結:', donateHref)

  const targets = [['PROFILE', '/profile']]
  if (donateHref) targets.push(['DONATE', donateHref])

  for (const [label, path] of targets) {
    const ok = await gotoPastWall(page, path.startsWith('http') ? path : HOST + path)
    console.log(`\n===== ${label}  (${path})  wall-passed=${ok} =====`)
    console.log('title:', await page.title())
    const text = await page.evaluate(() => document.body?.innerText || '')
    // 只留有數字或關鍵字的行，整頁 innerText 太吵
    const keep = text
      .split('\n')
      .map((s) => s.trim())
      .filter((s) => s && /\d|download|限|額度|daily|每日|plan|premium|donat|捐/i.test(s))
    console.log(keep.slice(0, 60).join('\n'))
  }
} finally {
  await browser.close()
}
