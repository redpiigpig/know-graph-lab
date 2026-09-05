// 抓 Gemini 分享連結的對話全文。
// 分享頁是純 JS 殼（curl / WebFetch 只拿得到空殼、正文 0 字），必須渲染。
// 用法：node scripts/gemini_share_fetch.mjs <share-url> [輸出檔] [--json]
//   短網址 share.gemini.google/XXXX 或 gemini.google.com/share/XXXX 都可以。
//
// --json 會分角色輸出。body.innerText 把提問和回覆黏成一片，長貼文根本切不開
// （「你說了」那行只是截斷到 ~100 字的標籤），要分辨哪句是我講的就得從 DOM 拿：
// 每輪是一個 share-turn-viewer，底下 user-query 是使用者、response-container 是 Gemini。
import { chromium } from 'playwright'
import { writeFileSync } from 'node:fs'

const argv = process.argv.slice(2)
const asJson = argv.includes('--json')
const [url, out] = argv.filter(a => a !== '--json')
if (!url) { console.error('用法：node scripts/gemini_share_fetch.mjs <share-url> [輸出檔] [--json]'); process.exit(1) }

const browser = await chromium.launch()
const page = await browser.newPage({ locale: 'zh-TW' })
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(4000)   // 對話串是 networkidle 之後才掛上去的

const payload = asJson
  ? await page.evaluate(() => ({
      title: document.title.replace(/\s*[-–—]\s*Gemini\s*$/, '').trim(),
      turns: [...document.querySelectorAll('share-turn-viewer')].flatMap((t, i) => {
        const grab = sel => t.querySelector(sel)?.innerText?.trim() ?? ''
        const user = grab('user-query-content') || grab('user-query')
        const model = grab('response-container')
        return [
          user && { i, role: 'user', text: user },
          model && { i, role: 'gemini', text: model },
        ].filter(Boolean)
      }),
    }))
  : await page.evaluate(() => document.body.innerText)
await browser.close()

const text = asJson ? JSON.stringify(payload, null, 1) : payload
const size = asJson ? `${payload.turns.length} 段／${text.length} 字` : `${text.length} 字`
if (out) { writeFileSync(out, text, 'utf8'); console.error(`已寫入 ${out}（${size}）`) }
else console.log(text)
