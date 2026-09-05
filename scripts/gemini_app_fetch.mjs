// 抓 gemini.google.com/app/<id> 這種「自己帳號底下」的對話全文。
//
// 跟 gemini_share_fetch.mjs 的差別：分享連結是公開的，這種不是，必須帶著使用者
// 已登入的 Chrome session 才看得到，否則只會拿到一片空白的「和 Gemini 的對話」。
//
// 兩種取用 session 的方式：
//   預設      把 Chrome profile 複製一份到 c:/tmp 再開（不動正在用的 profile，Chrome 可以開著）
//   --live    直接開真的 profile（Chrome 必須先關掉，否則 profile 被鎖）
// Chrome 127 以後 cookie 有 app-bound encryption，複製出去的 profile 有機會解不開；
// 真的解不開就會看到登入牆，這時改用 --live。
//
// 用法：node scripts/gemini_app_fetch.mjs <輸出資料夾> <url...> [--live]
import { chromium } from 'playwright'
import { cpSync, mkdirSync, writeFileSync, existsSync } from 'node:fs'
import { join } from 'node:path'

const args = process.argv.slice(2)
const live = args.includes('--live')
const [outDir, ...urls] = args.filter(a => a !== '--live')
if (!outDir || !urls.length) {
  console.error('用法：node scripts/gemini_app_fetch.mjs <輸出資料夾> <url...> [--live]')
  process.exit(1)
}

const REAL = join(process.env.LOCALAPPDATA, 'Google/Chrome/User Data')
if (!existsSync(REAL)) { console.error(`找不到 Chrome profile：${REAL}`); process.exit(1) }

let profile = REAL
if (!live) {
  profile = 'C:/tmp/gemini-profile'
  // 只複製登入狀態需要的東西，整個 User Data 幾 GB 不必搬
  mkdirSync(join(profile, 'Default/Network'), { recursive: true })
  for (const f of ['Local State']) cpSync(join(REAL, f), join(profile, f))
  for (const f of ['Network/Cookies', 'Preferences', 'Login Data']) {
    const src = join(REAL, 'Default', f)
    if (existsSync(src)) cpSync(src, join(profile, 'Default', f))
  }
}

mkdirSync(outDir, { recursive: true })
const ctx = await chromium.launchPersistentContext(profile, {
  channel: 'chrome', headless: false, locale: 'zh-TW', viewport: null,
})
const page = ctx.pages()[0] ?? await ctx.newPage()

for (const [i, url] of urls.entries()) {
  const id = url.match(/\/app\/([0-9a-f]+)/)?.[1] ?? String(i + 1)
  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
    await page.waitForTimeout(5000)          // 對話串在 networkidle 之後才掛上去
    const text = await page.evaluate(() => document.body.innerText)
    const walled = /^\s*$|登入$/m.test(text) && text.length < 500
    writeFileSync(join(outDir, `${id}.txt`), text, 'utf8')
    console.log(`${walled ? '⚠ 疑似登入牆' : '✓'} ${id}  ${text.length} 字`)
  } catch (e) {
    console.log(`✗ ${id}  ${e.message.split('\n')[0]}`)
  }
}
await ctx.close()
