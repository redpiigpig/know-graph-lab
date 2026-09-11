/**
 * 把日韓文無教會研究裡**開放全文**那批抓下來（74 筆）。
 *
 * 書目在 data/mukyokai/jp-kr-bibliography.jsonl（197 筆，2026-09-11 盤點）。
 * 只碰 access === 'open'；其餘是 abstract／paywall／print，沒有全文可抓。
 *
 * 為什麼要開瀏覽器而不是 curl：
 *   - **JAIRO Cloud（WEKO3）系機構典藏對 curl 一律回 HTTP 406**（關西學院、名古屋、
 *     立命館、金城、大阪國際…共 11 筆），換 UA 加 Accept 都沒用。
 *   - **KCI（韓國）的下載是 JS 觸發**（fncDown('KCI_FI…')），沒有靜態 PDF 連結。
 *     34 筆韓文全在這裡。
 *   - 只有 J-STAGE 那 13 筆是 `_pdf` 直連。
 *
 * 落地 Drive 研究資料／無教會主義／_jp-kr／（Drive 是 canonical storage）。
 * **不上 R2**——整本 PDF 是大檔，R2 只放小衍生物。
 *
 * 🚨 三道驗證，少一道就會收進一堆「看起來成功」的垃圾：
 *   1. 檔頭必須是 %PDF（機構典藏擋人時回 200 的 HTML 登入頁，存下來副檔名照樣是 .pdf）
 *   2. 大小不可過小（一頁的錯誤頁也可能是合法 PDF）
 *   3. 下載不到就**記下原因**，不可當成「這篇沒有全文」
 *
 *   node scripts/mukyokai_fetch_jpkr.mjs --dry
 *   node scripts/mukyokai_fetch_jpkr.mjs --run
 *   node scripts/mukyokai_fetch_jpkr.mjs --run --lang ko --limit 5
 */
import { chromium } from 'playwright'
import { createHash } from 'node:crypto'
import { readFileSync, appendFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'

const ROOT = process.cwd()
const BIB = join(ROOT, 'data/mukyokai/jp-kr-bibliography.jsonl')
const DRIVE = 'G:/我的雲端硬碟/資料/知識圖工作室/研究資料/無教會主義/_jp-kr'
const LEDGER = join(ROOT, 'scripts/state/mukyokai_jpkr_ledger.jsonl')
const MIN_BYTES = 20000
const PAUSE = 2500

const args = process.argv.slice(2)
const has = (f) => args.includes(f)
const val = (f) => (args.indexOf(f) >= 0 ? args[args.indexOf(f) + 1] : null)

const rows = readFileSync(BIB, 'utf8').split('\n').filter((l) => l.trim()).map((l) => JSON.parse(l))
let open = rows.filter((r) => r.access === 'open')
if (val('--lang')) open = open.filter((r) => r.lang === val('--lang'))

const done = new Set()
if (existsSync(LEDGER)) {
  for (const l of readFileSync(LEDGER, 'utf8').split('\n')) {
    if (!l.trim()) continue
    try { const d = JSON.parse(l); if (d.status === 'ok') done.add(d.slug) } catch {}
  }
}
const slugOf = (r) => {
  const h = createHash('sha1').update(`${r.author}|${r.title}|${r.year}`).digest('hex').slice(0, 8)
  const safe = `${r.author || ''}_${r.title || ''}`.replace(/[\\/:*?"<>|\s]+/g, '_').slice(0, 60)
  return `${r.lang}_${r.year || '____'}_${safe}_${h}`
}
let todo = open.filter((r) => !done.has(slugOf(r)))
if (val('--limit')) todo = todo.slice(0, Number(val('--limit')))

console.log(`書目 ${rows.length} 筆；open ${open.length} 筆；本輪要抓 ${todo.length}（已抓過 ${done.size}）`)
if (!has('--run')) {
  for (const r of todo.slice(0, 20)) {
    console.log(`  ${r.lang} ${String(r.year || '').padStart(5)} ${(r.title || '').slice(0, 38)}`)
  }
  console.log('\n加 --run 才會真的下載')
  process.exit(0)
}

mkdirSync(DRIVE, { recursive: true })
const note = (o) => appendFileSync(LEDGER, JSON.stringify(o) + '\n', 'utf8')

const browser = await chromium.launch({ headless: false, channel: 'chrome' })
const context = await browser.newContext({ locale: 'ja-JP', acceptDownloads: true })
const page = await context.newPage()

/** 直接拿 bytes；走 context.request 才會帶著瀏覽器的 UA 與 cookie（繞過 406）。
 *
 * 🚨 逾時與 ECONNRESET 要重試，不可當成「沒有全文」。2026-09-11 第一輪 74 筆裡
 *    13 筆敗在這裡（J-STAGE 大檔 90 秒拉不完、機構典藏偶發斷線），內容其實都在。 */
async function grab(url, tries = 3) {
  let last
  for (let i = 0; i < tries; i++) {
    try {
      const resp = await context.request.get(url, { timeout: 180000 })
      return await bodyOf(resp)
    } catch (e) {
      last = e
      await page.waitForTimeout(4000 * (i + 1))
    }
  }
  throw last
}

async function bodyOf(resp) {
  let buf = Buffer.from(await resp.body())
  // 🚨 CiNii 的「本文」連結回的是**內含 PDF 的 ZIP**（PK\x03\x04），而 Content-Type
  //    照樣寫 application/pdf。不解開就會整批判成「不是 PDF」而漏收。
  if (buf.subarray(0, 2).toString('latin1') === 'PK') {
    const inner = await unzipFirstPdf(buf)
    if (inner) buf = inner
  }
  return { status: resp.status(), ctype: (resp.headers()['content-type'] || '').toLowerCase(), buf }
}

/** ZIP → 裡面第一個 PDF。用 node 內建 zlib 解 deflate，不加相依。 */
async function unzipFirstPdf(zip) {
  const { inflateRawSync } = await import('node:zlib')
  let p = 0
  while (p + 30 <= zip.length && zip.readUInt32LE(p) === 0x04034b50) {
    const method = zip.readUInt16LE(p + 8)
    let csize = zip.readUInt32LE(p + 18)
    const nlen = zip.readUInt16LE(p + 26)
    const elen = zip.readUInt16LE(p + 28)
    const name = zip.subarray(p + 30, p + 30 + nlen).toString('utf8')
    const start = p + 30 + nlen + elen
    if (!csize) break                       // streaming（用 data descriptor）就放棄
    const body = zip.subarray(start, start + csize)
    if (/\.pdf$/i.test(name)) {
      try {
        return method === 0 ? Buffer.from(body) : inflateRawSync(body)
      } catch { return null }
    }
    p = start + csize
  }
  return null
}

/** DSpace 7（京大 KURENAI 等）沒有靜態 PDF 連結，檔案在 REST API 底下。 */
async function dspaceBitstream(pageUrl) {
  const m = page.url().match(/\/items\/([0-9a-f-]{36})/i)
  if (!m) return null
  const base = new URL(page.url()).origin
  try {
    const bundles = await (await context.request.get(
      `${base}/server/api/core/items/${m[1]}/bundles`, { timeout: 45000 })).json()
    for (const b of bundles?._embedded?.bundles || []) {
      const bs = await (await context.request.get(
        b._links.bitstreams.href, { timeout: 45000 })).json()
      for (const f of bs?._embedded?.bitstreams || []) {
        if (/\.pdf$/i.test(f.name || '')) return f._links?.content?.href || null
      }
    }
  } catch { return null }
  return null
}

/** 書目頁 → PDF 直連。回 null 代表頁面上沒有靜態連結（多半得改用點按鈕）。 */
async function findPdfLink() {
  return page.evaluate(() => {
    const abs = (h) => (h ? new URL(h, location.href).href : '')
    const as = [...document.querySelectorAll('a[href]')]
    const score = (a) => {
      const h = (a.getAttribute('href') || '').toLowerCase()
      const t = (a.textContent || '').toLowerCase()
      if (h.endsWith('.pdf') || h.includes('_pdf') || h.includes('/pdf/')) return 3
      if (h.includes('bitstream') && h.includes('download')) return 3
      if (h.includes('file') && (t.includes('pdf') || t.includes('本文') || t.includes('원문'))) return 2
      return 0
    }
    const best = as.map((a) => [score(a), abs(a.getAttribute('href'))]).filter(([s]) => s > 0)
    best.sort((x, y) => y[0] - x[0])
    return best.length ? best[0][1] : null
  })
}

// cookie 同意框會蓋住下載鈕，先按掉。各站用字不同，全列。
const CONSENT = ['許可', '拒否', '同意', 'Accept', 'OK', '확인', '동의']

/** 點下載鈕、接住 download 事件。回 Buffer 或 null。
 *
 * 🚨 京大 KURENAI 是 DSpace 7（Angular SPA）、KCI 是 fncDown() ——兩者都**沒有**
 *    靜態 PDF 連結，只有按鈕。單靠找 <a href> 會全部落空（實測 10 筆京大全滅）。 */
async function clickDownload() {
  for (const w of CONSENT) {
    const b = page.getByRole('button', { name: w, exact: false })
    if (await b.count().catch(() => 0)) { await b.first().click().catch(() => {}); await page.waitForTimeout(600) }
  }
  const words = ['PDF 다운로드', '원문보기', 'Download All', 'Download', 'ダウンロード', '本文', 'PDF']
  for (const w of words) {
    const el = page.getByText(w, { exact: false }).first()
    if (!(await el.count().catch(() => 0))) continue
    try {
      const [dl] = await Promise.all([
        page.waitForEvent('download', { timeout: 25000 }),
        el.click({ timeout: 8000 }),
      ])
      const path = await dl.path()
      if (path) return readFileSync(path)
    } catch {
      // 這個字沒觸發下載就換下一個；不要因此判定沒有全文
    }
  }
  return null
}

let ok = 0, fail = 0
for (const [i, r] of todo.entries()) {
  const url = r.fulltext_url || r.url || ''
  const slug = slugOf(r)
  const label = `${String(i + 1).padStart(3)}/${todo.length} ${r.lang} ${(r.title || '').slice(0, 28).padEnd(30)}`
  if (!url) { console.log(`${label} ✗ 沒有網址`); note({ slug, status: 'no-url', ...r }); fail++; continue }

  try {
    let target = url
    let buf = null, status = 0, ctype = ''
    const looksDirect = /\.pdf($|\?)/i.test(url) || url.includes('_pdf')
    if (looksDirect) {
      ({ status, ctype, buf } = await grab(target))
    } else {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
      await page.waitForTimeout(3000)
      const found = await findPdfLink()
      if (found) {
        target = found
        ;({ status, ctype, buf } = await grab(target))
      }
      // DSpace 7（京大 KURENAI…）：檔案只在 REST API 底下，頁面上沒有靜態連結
      if (!buf || buf.subarray(0, 4).toString('latin1') !== '%PDF') {
        const bs = await dspaceBitstream(url)
        if (bs) { target = bs; ({ status, ctype, buf } = await grab(target)) }
      }
      // 都不成 → 改點下載鈕
      if (!buf || buf.subarray(0, 4).toString('latin1') !== '%PDF') {
        const clicked = await clickDownload()
        if (clicked) { buf = clicked; target = url + ' (按鈕下載)'; status = 200; ctype = 'application/pdf' }
      }
      if (!buf) {
        console.log(`${label} ✗ 書目頁上既無 PDF 連結、按鈕也沒觸發下載`)
        note({ slug, status: 'no-pdf-link', url, ...r })
        fail++; await page.waitForTimeout(PAUSE); continue
      }
    }
    const isPdf = buf.subarray(0, 4).toString('latin1') === '%PDF'
    if (!isPdf) {
      const head = buf.subarray(0, 120).toString('utf8').replace(/\s+/g, ' ')
      console.log(`${label} ✗ 不是 PDF（HTTP ${status}, ${ctype.slice(0, 30)}）`)
      note({ slug, status: 'not-pdf', http: status, ctype, head, url: target, ...r })
      fail++; await page.waitForTimeout(PAUSE); continue
    }
    if (buf.length < MIN_BYTES) {
      console.log(`${label} ✗ 只有 ${buf.length} bytes，太小`)
      note({ slug, status: 'too-small', bytes: buf.length, url: target, ...r })
      fail++; await page.waitForTimeout(PAUSE); continue
    }
    const out = join(DRIVE, `${slug}.pdf`)
    writeFileSync(out, buf)
    console.log(`${label} ✓ ${(buf.length / 1024).toFixed(0)} KB`)
    note({ slug, status: 'ok', bytes: buf.length, url: target, file: out, ...r })
    ok++
  } catch (e) {
    console.log(`${label} ✗ ${e.constructor.name}: ${String(e.message).split('\n')[0].slice(0, 70)}`)
    note({ slug, status: 'error', error: String(e.message).slice(0, 200), url, ...r })
    fail++
  }
  await page.waitForTimeout(PAUSE)
}

console.log(`\n成功 ${ok}、失敗 ${fail}。落地 ${DRIVE}`)
console.log('🚨 失敗的不代表沒有全文——帳本記著網址與原因，可個別補。')
await browser.close()
