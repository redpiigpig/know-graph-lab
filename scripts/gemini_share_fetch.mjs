// 抓 Gemini 分享連結的對話全文。
// 分享頁是純 JS 殼（curl / WebFetch 只拿得到空殼、正文 0 字），必須渲染。
// 用法：node scripts/gemini_share_fetch.mjs <share-url> [輸出檔]
//   短網址 share.gemini.google/XXXX 或 gemini.google.com/share/XXXX 都可以。
import { chromium } from 'playwright'
import { writeFileSync } from 'node:fs'

const [url, out] = process.argv.slice(2)
if (!url) { console.error('用法：node scripts/gemini_share_fetch.mjs <share-url> [輸出檔]'); process.exit(1) }

const browser = await chromium.launch()
const page = await browser.newPage({ locale: 'zh-TW' })
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(4000)   // 對話串是 networkidle 之後才掛上去的
const text = await page.evaluate(() => document.body.innerText)
await browser.close()

if (out) { writeFileSync(out, text, 'utf8'); console.error(`已寫入 ${out}（${text.length} 字）`) }
else console.log(text)
