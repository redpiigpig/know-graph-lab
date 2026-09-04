// 華藝線上圖書館：依書目清單逐篇查詢、下載有權限的全文 PDF。
//
// 🚨 不讀使用者原本的 Chrome 設定檔。那等於去撈瀏覽器的 cookie 資料庫，
//    形狀就是憑證外洩，權限守門也會擋。改成專用設定檔：
//      node scripts/airiti_fetch.mjs --login    ← 開瀏覽器，你自己登入一次，關掉即可
//      node scripts/airiti_fetch.mjs --fetch    ← 重用那個設定檔，逐篇下載
//    登入狀態存在 C:/tmp/airiti-profile，只有這支腳本會用到。
//
// 🚨 華藝多數文章要訂閱才給全文。腳本只下載「這個帳號真的按得到下載」的那些，
//    按不到就記進帳本標明原因，不會硬闖也不會把付費牆頁面存成假 PDF。
//    每篇存檔前驗 %PDF 魔術位元組——站方常在沒權限時回一個 200 的 HTML。
import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

const PROFILE = 'C:/tmp/airiti-profile'
const LEDGER = 'C:/tmp/airiti_fetch.json'
const LIST = 'public/content/research-data/pct/airiti-shortlist.json'
const OUT = 'G:/我的雲端硬碟/資料/知識圖工作室/研究資料/博論參考文獻/華藝全文'
const DELAY = 6000

const args = process.argv.slice(2)
const has = (f) => args.includes(f)
const limit = Number((args.find((a) => a.startsWith('--limit=')) || '').split('=')[1] || 0)

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const load = (p, d) => (fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : d)

async function open (headless) {
  fs.mkdirSync(PROFILE, { recursive: true })
  return chromium.launchPersistentContext(PROFILE, {
    headless,
    acceptDownloads: true,
    viewport: { width: 1400, height: 950 },
    args: ['--disable-blink-features=AutomationControlled'],
  })
}

if (has('--login')) {
  const ctx = await open(false)
  const p = ctx.pages()[0] || (await ctx.newPage())
  await p.goto('https://www.airitilibrary.com/', { waitUntil: 'domcontentloaded', timeout: 90000 })
  console.log('瀏覽器已開。請在這個視窗登入華藝（機構或個人帳號都可以），')
  console.log('登入完成後直接關掉視窗，登入狀態會留在 ' + PROFILE)
  await p.waitForEvent('close', { timeout: 0 }).catch(() => {})
  await ctx.close()
  process.exit(0)
}

if (!has('--fetch')) {
  console.log('用法：--login 先登入一次；--fetch 開始下載（可加 --limit=N）')
  process.exit(0)
}

const items = load(LIST, { items: [] }).items
const led = load(LEDGER, {})
fs.mkdirSync(OUT, { recursive: true })

const ctx = await open(true)
const page = ctx.pages()[0] || (await ctx.newPage())

// 先確認登入狀態還在——沒確認就跑，會整輪都拿到付費牆而不自知
await page.goto('https://www.airitilibrary.com/', { waitUntil: 'domcontentloaded', timeout: 90000 })
await sleep(3000)
const body = await page.locator('body').innerText()
const loggedOut = /登入\s*\/\s*註冊|請先登入/.test(body) && !/登出|會員中心/.test(body)
console.log(loggedOut ? '⚠ 看起來沒有登入狀態，先跑一次 --login' : '登入狀態看起來還在')
if (loggedOut) { await ctx.close(); process.exit(1) }

let done = 0
for (const it of items) {
  if (limit && done >= limit) break
  const key = it.title
  if (led[key]) continue

  try {
    await page.goto('https://www.airitilibrary.com/Search/alDetailedSearch?Field=DocTitle&Keyword=' +
      encodeURIComponent(key.slice(0, 40)), { waitUntil: 'domcontentloaded', timeout: 90000 })
    await sleep(4000)
    const links = await page.$$eval('a[href]', (as) => [...new Set(as.map((a) => a.href))])
    const detail = links.find((h) => /Article\/Detail|alDetailedMesh|Publication\/Index/i.test(h))
    if (!detail) { led[key] = { status: '搜尋無結果' }; continue }

    await page.goto(detail, { waitUntil: 'domcontentloaded', timeout: 90000 })
    await sleep(4000)
    const txt = await page.locator('body').innerText()
    // 站方對沒權限的文章一樣顯示「下載」按鈕，但按下去是購買流程
    if (/購買|加入購物車|付費/.test(txt) && !/已訂購|機構已訂購|開放取用|Open Access/.test(txt)) {
      led[key] = { status: '需付費', url: detail }
      continue
    }
    const btn = await page.$('a:has-text("全文下載"), button:has-text("全文下載"), a:has-text("下載PDF")')
    if (!btn) { led[key] = { status: '無下載按鈕', url: detail }; continue }

    const [dl] = await Promise.all([
      page.waitForEvent('download', { timeout: 60000 }),
      btn.click(),
    ])
    const safe = key.replace(/[\\/:*?"<>|]/g, '_').slice(0, 70)
    const dest = path.join(OUT, safe + '.pdf')
    await dl.saveAs(dest)
    const head = fs.readFileSync(dest).subarray(0, 4).toString('latin1')
    if (head !== '%PDF') {                    // 200 的 HTML 也會存成檔案
      fs.unlinkSync(dest)
      led[key] = { status: '下載到的不是 PDF', url: detail }
      continue
    }
    led[key] = { status: 'OK', bytes: fs.statSync(dest).size, path: dest, url: detail }
    console.log(`  ✔ ${key.slice(0, 34)}　${(led[key].bytes / 1024) | 0} KB`)
  } catch (e) {
    led[key] = { status: '錯誤：' + String(e).slice(0, 80) }
  } finally {
    fs.writeFileSync(LEDGER, JSON.stringify(led, null, 1))
    done++
    await sleep(DELAY)
  }
}

const tally = {}
for (const v of Object.values(led)) tally[v.status?.split('：')[0] ?? '?'] = (tally[v.status?.split('：')[0] ?? '?'] || 0) + 1
console.log('本輪處理 ' + done + ' 篇；累計：' + JSON.stringify(tally, null, 0))
await ctx.close()
