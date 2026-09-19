// 只讀：把節點樹 API（api/get-nodes.ashx）的回應印出來，取得每個節點在樹裡的真實 id，
// 以便拼出「建立」會開的 NodeEditor 網址。不建立、不修改任何節點。
import { chromium } from 'playwright'
const OUT = 'c:/tmp/hcu-cms'
const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ storageState: `${OUT}/state.json`, viewport: { width: 1440, height: 1000 } })
const page = await ctx.newPage()
await page.goto('https://www.hcu.edu.tw/backend/MngCms/NodeList.aspx', { waitUntil: 'domcontentloaded' })
await page.waitForTimeout(4000)

for (const id of ['', 'B975569CC2F04819892552ADE1A9090E', 'NODE-B975569CC2F04819892552ADE1A9090E']) {
  const res = await page.evaluate(async id => {
    const r = await fetch('api/get-nodes.ashx', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ id }).toString(),
    })
    return { status: r.status, text: (await r.text()).slice(0, 1500) }
  }, id)
  console.log(`\n[get-nodes id="${id}"] ${res.status}\n${res.text}`)
}
await browser.close()
