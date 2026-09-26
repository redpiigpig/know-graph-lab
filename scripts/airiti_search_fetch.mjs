
import { chromium } from 'playwright'
const queries = JSON.parse(process.argv[2])
const MAX_PAGES = 8
const b = await chromium.launch()
const p = await b.newPage()
const out = []
for (const [q, note] of queries) {
  try {
    await p.goto('https://www.airitilibrary.com/', { waitUntil: 'domcontentloaded', timeout: 90000 })
    await p.waitForTimeout(1800)
    const box = await p.$('input[type="text"], input[type="search"]')
    await box.fill(q)
    await box.press('Enter')
    await p.waitForTimeout(7000)
    const url = p.url()
    // 每頁改 50 筆，減少翻頁次數
    try {
      await p.selectOption('#Result_每頁顯示', { label: '50 筆' })
      await p.waitForTimeout(6000)
    } catch (e) { /* 版面偶爾沒有這個選單，照 10 筆翻 */ }
    let text = '', cur = 1
    while (cur <= MAX_PAGES) {
      text += "\n" + await p.locator('body').innerText()
      const next = p.locator(`.page a`, { hasText: new RegExp(`^${cur + 1}$`) }).first()
      if (!(await next.count())) break
      await next.click(); await p.waitForTimeout(5000); cur++
    }
    out.push({ query: q, note, url, text, pages: cur })
    console.error(`  ${q}: ${cur} 頁`)
  } catch (e) {
    out.push({ query: q, note, error: String(e).slice(0, 120), text: '' })
    console.error(`  ${q}: FAIL`)
  }
}
console.log(JSON.stringify(out))
await b.close()
