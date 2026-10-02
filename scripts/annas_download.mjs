/**
 * Anna's Archive 慢速下載（給 LibGen 沒有、只有 Anna's 收的檔）。常駐＋多分頁並行。
 *
 *   node scripts/annas_download.mjs --queue c:/tmp/annas_queue.jsonl --out <資料夾> [--tabs 10]
 *   佇列檔一行一筆 {"md5": "...", "name": "書名 (作者)"}；常駐不結束，每 15 秒重讀佇列，
 *   要下載新書就往佇列檔加行。結果逐行寫進 <佇列檔>.log（OK／FAIL）。
 *
 * 🚨 不要為了改程式或加書去停這支：停了視窗就關，又得請人重點驗證（2026-10-01 一晚關了
 *    四次，使用者很火）。改程式的話，等佇列清空、使用者同意再重開。
 * 🚨 DDOS-GUARD 驗證要人點，cookie 存在持久 profile（c:/tmp/annas_profile），所有分頁共用，
 *    點一次就夠（使用者 10-01 的提議：一次驗證、十個分頁輪流下載）。
 * 🚨 每次進 slow_download 頁都會先跑一次自動檢查再跳轉；跳轉當下 evaluate 會丟
 *    "Execution context was destroyed"——那不是失敗，當成「還在檢查」繼續等。
 * 🚨 拿到檔案連結後要用**分頁本身去開**（比照真人點擊），不要用 ctx.request 另抓：
 *    後者沒有 Referer，夥伴伺服器回 504（Karmiris 那本 server 0／2 都這樣）。
 */
import { chromium } from 'playwright'
import { readFileSync, existsSync, writeFileSync, appendFileSync } from 'node:fs'
import { join } from 'node:path'

const HOST = 'https://annas-archive.gl'
const args = process.argv.slice(2)
const val = (k) => (args.includes(k) ? args[args.indexOf(k) + 1] : null)
const QUEUE = val('--queue')
const OUT = val('--out')
const TABS = Number(val('--tabs') || 10)
const LOG = QUEUE + '.log'
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))
const log = (...a) => { const s = a.join(' '); console.log(s); try { appendFileSync(LOG, s + '\n') } catch {} }

const ctx = await chromium.launchPersistentContext('c:/tmp/annas_profile', { headless: false, channel: 'chrome', acceptDownloads: true, viewport: { width: 1280, height: 900 } })

const safeEval = async (page, fn, arg) => { try { return await page.evaluate(fn, arg) } catch { return undefined } }
const isBlocked = async (page) =>
  (await safeEval(page, () => /DDOS-GUARD|manual check|Checking your browser|Please wait a few seconds/i.test(document.title + (document.body?.innerText || '').slice(0, 500)))) !== false
let warned = 0
async function waitHuman(page) {
  for (let w = 0; w < 300 && (await isBlocked(page)); w++) {
    if (Date.now() - warned > 30000) { warned = Date.now(); console.log('等待人工驗證…請在 Chrome 視窗點完驗證') }
    await sleep(2000)
  }
}
const extOf = (buf, url) => {
  const head = buf.subarray(0, 8).toString('latin1')
  if (head.startsWith('%PDF')) return 'pdf'
  if (head.startsWith('AT&TFORM')) return 'djvu'
  if (head.startsWith('PK')) return (url.match(/\.(epub|zip)/i) || ['', 'epub'])[1].toLowerCase()
  return null
}
// 頁面說明：跳過頁首語言清單，取含 wait／download／slow／limit 的那幾句
const pageNote = async (page) =>
  String(await safeEval(page, () => {
    const t = document.body.innerText.split('\n').map((s) => s.trim()).filter(Boolean)
    return t.filter((s) => /wait|download|slow|limit|server|error|full|try/i.test(s) && s.length < 300).slice(0, 8).join(' ｜ ')
  }))

async function fetchOne(page, it) {
  for (let server = 0; server < 8; server++) {
    try {
      await page.goto(`${HOST}/slow_download/${it.md5}/0/${server}`, { waitUntil: 'domcontentloaded', timeout: 120000 })
      await waitHuman(page)
      let href = null
      for (let i = 0; i < 120 && !href; i++) {   // 倒數最多等 4 分鐘
        if (await isBlocked(page)) { await sleep(2000); continue }
        href = (await safeEval(page, () => {
          const a = [...document.querySelectorAll('a')].find((x) => /download now|📚|點此下載|下載/i.test(x.innerText) && /^https?:/.test(x.href) && !x.href.includes('annas-archive'))
          return a ? a.href : null
        })) || null
        if (!href) await sleep(2000)
      }
      if (!href) { log('no-link', `server${server}`, it.name, '｜', await pageNote(page)); continue }
      // 🚨 另開一個分頁去開檔案連結：用工作分頁本身開的話，Chrome 判定是下載就把那個分頁收掉，
      //    之後每一次 goto 都是 "Target page closed"（10-02 Karmiris 那本就是下載到一半這樣斷的）。
      //    可能觸發下載事件，也可能內嵌開 PDF（那就拿 response body）。
      const dp = await ctx.newPage()
      const dlP = dp.waitForEvent('download', { timeout: 900000 }).catch(() => null)
      let buf = null
      try {
        const resp = await dp.goto(href, { waitUntil: 'commit', timeout: 900000, referer: page.url() })
        if (resp) { await resp.finished().catch(() => {}); buf = await resp.body().catch(() => null) }
      } catch (e) { if (!/Download is starting|net::ERR_ABORTED/i.test(e.message)) throw e }
      if (!buf || !extOf(buf, href)) {
        const dl = await dlP
        if (dl) { const p = await dl.path().catch(() => null); if (p) buf = readFileSync(p) }
      }
      await dp.close().catch(() => {})
      const ext = buf && extOf(buf, href)
      if (!ext || buf.length < 50000) { log('not-file', `server${server}`, it.name, buf ? `${buf.length}B` : 'no body'); continue }
      writeFileSync(join(OUT, `${it.name}.${ext}`), buf)
      log('OK', it.name, ext, Math.round(buf.length / 1024), 'KB')
      return true
    } catch (e) { log('retry', `server${server}`, it.name, e.message.slice(0, 140)); await sleep(5000) }
  }
  log('FAIL', it.name)
  return false
}

// 佇列：常駐，每 15 秒重讀；TABS 個分頁各自從共用游標取工作
const taken = new Set()
function nextItem() {
  const items = existsSync(QUEUE)
    ? readFileSync(QUEUE, 'utf8').split(/\r?\n/).filter(Boolean).map((l) => { try { return JSON.parse(l) } catch { return null } }).filter(Boolean)
    : []
  for (const it of items) {
    if (taken.has(it.md5)) continue
    taken.add(it.md5)
    if (['pdf', 'epub', 'djvu', 'zip'].some((e) => existsSync(join(OUT, `${it.name}.${e}`)))) { log('SKIP', it.name); continue }
    return it
  }
  return null
}
async function worker(n) {
  const page = n === 0 ? (ctx.pages()[0] || (await ctx.newPage())) : await ctx.newPage()
  if (n > 0) await sleep(n * 4000)   // 錯開起步，別十個同時打同一台
  while (true) {
    const it = nextItem()
    if (!it) { await sleep(15000); continue }
    await fetchOne(page, it)
  }
}
await Promise.all(Array.from({ length: TABS }, (_, i) => worker(i)))
