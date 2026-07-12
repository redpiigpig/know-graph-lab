/**
 * 通用頁面截圖工具（playwright chromium）。
 * 用法：node scripts/shot.mjs <url> <out.png> [--w 1440] [--h 1100] [--wait 3000] [--full] [--selector CSS] [--js "..."]
 *   --selector：只截該元素的 bounding box
 *   --js：截圖前在頁面執行的 JS（如點擊圖例切換界域）
 */
import { chromium } from 'playwright'

const [url, out, ...rest] = process.argv.slice(2)
if (!url || !out) { console.error('usage: node scripts/shot.mjs <url> <out.png> [--w N] [--h N] [--wait ms] [--full] [--selector css] [--js code]'); process.exit(1) }
const opt = (name, dflt) => { const i = rest.indexOf(`--${name}`); return i >= 0 ? rest[i + 1] : dflt }
const has = (name) => rest.includes(`--${name}`)

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: Number(opt('w', 1440)), height: Number(opt('h', 1100)) } })
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 })
await page.waitForTimeout(Number(opt('wait', 3000)))
const js = opt('js', null)
if (js) { await page.evaluate(js); await page.waitForTimeout(1500) }
const sel = opt('selector', null)
if (sel) {
  const el = page.locator(sel).first()
  await el.screenshot({ path: out })
} else {
  await page.screenshot({ path: out, fullPage: has('full') })
}
console.log('url:', page.url())
console.log('saved:', out)
await browser.close()
