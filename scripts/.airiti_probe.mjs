import { chromium } from 'playwright'
const b = await chromium.launch()
const p = await b.newPage()
await p.goto('https://www.airitilibrary.com/', { waitUntil: 'domcontentloaded', timeout: 90000 })
await p.waitForTimeout(2000)
const box = await p.$('input[type="text"], input[type="search"]')
await box.fill('敵偽、附匪與邪教'); await box.press('Enter')
await p.waitForTimeout(9000)
// 收集結果頁上所有連結，找單篇詳目
const hrefs = await p.$$eval('a[href]', as => [...new Set(as.map(a => a.href))])
const cand = hrefs.filter(h => /Article\/Detail|ArticleDetail|Publication\/alDetailedMesh|doi\.airiti/i.test(h))
console.log('詳目候選:', cand.slice(0, 5))
let target = cand[0]
if (!target) {
  // 有些版面把詳目掛在標題的 onclick
  const oc = await p.$$eval('a,span,div', els => els.filter(e => /從檔案觀察三十年代/.test(e.textContent || ''))
    .map(e => ({ tag: e.tagName, href: e.getAttribute('href') || '', oc: (e.getAttribute('onclick') || '').slice(0, 120) })).slice(0, 4))
  console.log('標題元素:', JSON.stringify(oc))
}
if (target) {
  await p.goto(target, { waitUntil: 'domcontentloaded', timeout: 90000 })
  await p.waitForTimeout(7000)
  console.log('到達:', p.url().slice(0, 120))
  const t = await p.locator('body').innerText()
  console.log('頁長', t.length)
  for (const k of ['全文下載', '免費', 'Open Access', '開放取用', '購買', '登入', '權限', '訂閱', '元']) {
    const n = (t.match(new RegExp(k, 'g')) || []).length
    if (n) console.log(`  「${k}」×${n}`)
  }
  const i = t.indexOf('全文下載')
  if (i >= 0) console.log('  全文附近:', t.slice(i - 80, i + 160).replace(/\s+/g, ' '))
}
await b.close()
