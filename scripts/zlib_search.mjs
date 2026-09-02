/**
 * z-library 書目查詢（只查，不下載）。
 *
 * 用途：REFERENCE-first 的第一步——動手自譯之前先查有沒有現成中譯本，有就列進獵表
 * 交使用者下載（[[feedback_collected_works_reference_first]]）。
 *
 * 為什麼要開瀏覽器：站方前面擋著 DiamWall，curl 只會拿到 513「Verifying your
 * browser」的 JS challenge 頁。playwright 帶著真的瀏覽器過牆，challenge 過完把
 * cookie 留在 c:/tmp/zlib_state.json，之後幾次查詢就不必重過。
 *
 * 只輸出書目欄位（書名／作者／年／語言／格式／大小／連結），不碰下載——下載是使用者
 * 自己的事，這支不做。
 *
 *   node scripts/zlib_search.mjs "韋伯 宗教社會學"
 *   node scripts/zlib_search.mjs --file c:/tmp/queries.txt --out c:/tmp/zlib_hits.json
 */
import { chromium } from 'playwright'
import { readFileSync, writeFileSync, existsSync } from 'node:fs'

const HOST = 'https://z-library.sk'
const STATE = 'c:/tmp/zlib_state.json'
const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'

const args = process.argv.slice(2)
const fileArg = args.indexOf('--file')
const outArg = args.indexOf('--out')
const queries =
  fileArg >= 0
    ? readFileSync(args[fileArg + 1], 'utf8').split('\n').map((s) => s.trim()).filter(Boolean)
    : [args.filter((a) => !a.startsWith('--')).join(' ')]
const outPath = outArg >= 0 ? args[outArg + 1] : null

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

/** 一頁搜尋結果 → 書目列表（純解析，跑在瀏覽器裡）。 */
async function scrape(page) {
  return page.evaluate(() => {
    const rows = [...document.querySelectorAll('z-bookcard, .book-item, .resItemBox')]
    return rows.slice(0, 25).map((el) => {
      const attr = (n) => el.getAttribute?.(n) || ''
      const text = (sel) => el.querySelector(sel)?.textContent?.trim() || ''
      // 書名與作者在 slot 裡（<div slot="title">），不是 attribute——年份、語言、
      // 格式才是 attribute。兩邊都讀。
      const slot = (n) => text(`[slot="${n}"]`)
      return {
        title: slot('title') || attr('title') || text('h3'),
        author: slot('author') || attr('author') || text('.authors'),
        year: attr('year') || text('.property_year .property_value'),
        language: attr('language') || text('.property_language .property_value'),
        extension: attr('extension') || text('.property__file'),
        filesize: attr('filesize') || text('.property__file'),
        href: attr('href') || el.querySelector('a')?.getAttribute('href') || '',
      }
    })
  })
}

// 用系統裝好的 Chrome（playwright 自己那份 chromium 這台機器沒下載）；
// headless 會被 DiamWall 直接判掉，所以開真視窗。
/** DiamWall 的 challenge 頁會自己驗完再轉走；等它，別把那一頁當結果解析。 */
async function gotoPastWall(page, url, tries = 3) {
  const blocked = (t) => /DiamWall|验证|驗證|Verifying/i.test(t)
  for (let i = 0; i < tries; i++) {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
    if (!blocked(await page.title())) return true
    await page.waitForTimeout(12000)
    if (!blocked(await page.title())) return true
  }
  return false
}

const browser = await chromium.launch({ headless: false, channel: 'chrome' })
const context = await browser.newContext({
  // 不要覆寫 userAgent：DiamWall 會比對 UA 與瀏覽器指紋，自訂 UA 反而過不了牆
  // （實測覆寫後連三次都被擋在 challenge 頁，拿掉就過）。
  locale: 'zh-TW',
  ...(existsSync(STATE) ? { storageState: STATE } : {}),
})
const page = await context.newPage()

const results = {}
try {
  if (!(await gotoPastWall(page, HOST))) throw new Error('DiamWall 沒過，先手動開一次瀏覽器')
  await page.waitForTimeout(3000)
  await context.storageState({ path: STATE })

  for (const q of queries) {
    // 不在 URL 上掛 extensions/languages 過濾——實測那樣多半直接 0 筆
    // （站方的過濾對中文書標記很不完整）。全抓回來自己看語言與格式。
    const url = `${HOST}/s/${encodeURIComponent(q)}`
    await gotoPastWall(page, url)
    // 結果是 web component，晚一點才掛上來；等它出現再抓，別靠固定秒數猜
    await page.waitForSelector('z-bookcard', { timeout: 20000 }).catch(() => {})
    const hits = await scrape(page)
    if (!hits.length) {
      const dump = `c:/tmp/zlib_dump_${encodeURIComponent(q).slice(0, 30)}.html`
      writeFileSync(dump, await page.content(), 'utf8')
      console.log(`   （0 筆，頁面已存 ${dump} 供診斷）`)
    }
    results[q] = hits
    console.log(`\n=== ${q} —— ${hits.length} 筆`)
    for (const h of hits.slice(0, 8)) {
      console.log(
        `   ${(h.title || '').slice(0, 40).padEnd(42)} ${(h.author || '').slice(0, 18).padEnd(20)}` +
          ` ${h.year || ''} ${h.language || ''} ${h.extension || ''} ${h.filesize || ''}`
      )
    }
    await sleep(3000) // 站方本來就在擋機器人，慢一點
  }
} finally {
  if (outPath) writeFileSync(outPath, JSON.stringify(results, null, 2), 'utf8')
  await browser.close()
}
