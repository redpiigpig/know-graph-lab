/**
 * Anna's Archive 書目查詢（只查，不下載）。
 *
 * 站前有 DDOS-GUARD，curl 拿到 403；真 Chrome 也會停在「Complete the manual check」，
 * 自動過不了——要人在跳出的視窗裡點一次驗證。所以用持久 profile（c:/tmp/annas_profile），
 * 點過一次 cookie 就留著；第一筆會等最多 10 分鐘讓人點。🚨 卡在驗證頁時結果是 0 筆，
 * 那不是「查無此書」，所以偵測到驗證頁一律重等，不記成 0。
 * .li 網域已被停放出售，現用 annas-archive.gl。
 *
 *   node scripts/annas_search.mjs --file queries.txt --out hits.json
 */
import { chromium } from 'playwright'
import { readFileSync, writeFileSync } from 'node:fs'

const HOST = 'https://annas-archive.gl'
const args = process.argv.slice(2)
const val = (k) => (args.includes(k) ? args[args.indexOf(k) + 1] : null)
const queries = readFileSync(val('--file'), 'utf8').split('\n').map((s) => s.trim()).filter(Boolean)
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const ctx = await chromium.launchPersistentContext('c:/tmp/annas_profile', { headless: false, channel: 'chrome', viewport: { width: 1280, height: 900 } })
const page = ctx.pages()[0] || (await ctx.newPage())
const blocked = () => page.evaluate(() => /DDOS-GUARD|manual check|Checking your browser/i.test(document.title + (document.body?.innerText || '').slice(0, 500)))
const out = []
for (const q of queries) {
  let hits = []
  for (let attempt = 0; attempt < 3 && !hits.length; attempt++) {
    try {
      await page.goto(`${HOST}/search?q=${encodeURIComponent(q)}`, { waitUntil: 'domcontentloaded', timeout: 90000 })
      // 防護頁會自己轉回來；等到結果列或「沒有結果」字樣出現
      for (let w = 0; w < 300 && (await blocked()); w++) {
        if (w % 15 === 0) console.log('等待人工驗證…請在 Chrome 視窗點完驗證')
        await sleep(2000)
      }
      if (await blocked()) throw new Error('still blocked')
      for (let i = 0; i < 30; i++) {
        const ready = await page.evaluate(() =>
          document.querySelector('a.js-vim-focus') || /No files found|0 results|找不到/i.test(document.body.innerText))
        if (ready) break
        await sleep(2000)
      }
      hits = await page.evaluate(() => {
        // 結果列的書名連結帶 js-vim-focus；頁面上另有一排「最近下載」也是 /md5/ 連結，別抓到那個
        const seen = new Set(), rows = []
        for (const a of document.querySelectorAll('a.js-vim-focus[href^="/md5/"]')) {
          const md5 = a.getAttribute('href').slice(5)
          if (seen.has(md5)) continue
          seen.add(md5)
          let box = a.parentElement
          for (let i = 0; i < 3 && box && box.innerText.length < 120; i++) box = box.parentElement
          rows.push({ md5, title: a.innerText.trim(), text: (box?.innerText || '').replace(/\s+/g, ' ').slice(0, 400) })
        }
        return rows.slice(0, 12)
      })
      if (!hits.length) break
    } catch (e) { console.error('retry', q, e.message); await sleep(5000) }
  }
  console.log(`${hits.length}\t${q}`)
  out.push({ q, hits })
  writeFileSync(val('--out'), JSON.stringify(out, null, 1))  // 逐筆存，中斷不丟
  await sleep(2500)
}
writeFileSync(val('--out'), JSON.stringify(out, null, 1))
await ctx.close()
