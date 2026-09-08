/**
 * 用真瀏覽器抓 Wiley 的單篇 PDF（校內 IP 才有授權）。
 *
 * curl 拿不到：Wiley 前面是 Cloudflare，會回 403 的 challenge 頁，而且那個頁面
 * 也是 200/403 的 HTML，副檔名叫 .pdf 也一樣——所以下載完一定要驗頭四個位元組
 * 是不是 %PDF，不驗就會存下一個「看起來成功」的假檔。
 *
 *   node scripts/fetch_wiley_article.mjs <doi> <輸出檔>
 */
import { chromium } from 'playwright'
import { writeFileSync, existsSync, readFileSync } from 'node:fs'

const doi = process.argv[2]
const out = process.argv[3]
if (!doi || !out) {
  console.error('用法: node scripts/fetch_wiley_article.mjs <doi> <輸出檔>')
  process.exit(1)
}

const STATE = 'c:/tmp/wiley_state.json'
const ART = `https://onlinelibrary.wiley.com/doi/${doi}`
const PDF = `https://onlinelibrary.wiley.com/doi/pdfdirect/${doi}?download=true`

const browser = await chromium.launch({ headless: false, channel: 'chrome' })
const ctx = await browser.newContext({
  acceptDownloads: true,
  storageState: existsSync(STATE) ? STATE : undefined,
  viewport: { width: 1280, height: 900 },
})
const page = await ctx.newPage()

console.log('→ 開文章頁，等 Cloudflare 放行…')
await page.goto(ART, { waitUntil: 'domcontentloaded', timeout: 90000 }).catch((e) =>
  console.log('  goto 警告:', e.message.slice(0, 80)),
)
// challenge 頁會自己跳轉，給它時間
for (let i = 0; i < 30; i++) {
  const t = await page.title().catch(() => '')
  if (t && !/just a moment|attention required|verify/i.test(t)) break
  await page.waitForTimeout(2000)
}
console.log('  標題:', await page.title().catch(() => '?'))

// 有沒有全文權限，看頁面上有沒有 PDF 連結
const hasPdf = await page.locator('a[href*="epdf"], a[href*="pdfdirect"]').count().catch(() => 0)
console.log('  頁面上的 PDF 連結數:', hasPdf)

const hrefs = await page.$$eval('a[href*="epdf"], a[href*="pdfdirect"]', (as) =>
  as.map((a) => a.href),
)
console.log('  PDF 連結:', hrefs)

console.log('→ 抓 PDF…')
// 🚨 四條路試過三條不通：
//   1. page.goto(PDF)：導走原頁面，之後的 evaluate 直接 Failed to fetch；
//   2. page.evaluate(fetch)：Wiley 的 CSP 擋跨路徑 fetch；
//   3. ctx.request.get(pdfdirect)：Cloudflare 認定機器人，回 403 的 HTML。
// 會通的是「照人的方式按頁面上的 Download PDF」，讓瀏覽器自己發請求。
let grabbed = null
page.on('response', async (res) => {
  if (grabbed) return
  if (!/pdf/i.test(res.headers()['content-type'] || '')) return
  const buf = await res.body().catch(() => null)
  if (buf && buf.subarray(0, 4).toString('latin1') === '%PDF') {
    grabbed = buf
    console.log(`  ✓ 攔到 ${buf.length}B  ${res.url().slice(0, 78)}`)
  }
})

const btn = page.locator('a:has-text("Download PDF"), a:has-text("PDF")').first()
try {
  const [dl] = await Promise.all([
    page.waitForEvent('download', { timeout: 45000 }).catch(() => null),
    btn.click({ timeout: 20000 }),
  ])
  if (dl) {
    await dl.saveAs(out)
    console.log('  ✓ 下載事件存檔')
    grabbed = grabbed || Buffer.from('%PDF')
  }
} catch (e) {
  console.log('  點 Download PDF:', e.message.slice(0, 70))
}
for (let i = 0; i < 30 && !grabbed; i++) await page.waitForTimeout(1500)
if (grabbed && grabbed.length > 8) writeFileSync(out, grabbed)

await ctx.storageState({ path: STATE })
await browser.close()

const head = existsSync(out) ? readFileSync(out).subarray(0, 4).toString('latin1') : ''
console.log(head === '%PDF' ? `✓ 真的是 PDF → ${out}` : `✗ 不是 PDF（開頭 "${head}"），沒拿到授權`)
process.exit(head === '%PDF' ? 0 : 2)
