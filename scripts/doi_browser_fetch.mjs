/**
 * 用真的 Chrome 開 DOI，看校內網路對這篇有沒有訂閱，有就把 PDF 存下來。
 *
 * 為什麼要開瀏覽器：curl／requests 開 doi.org 會被 SAGE、OUP、JSTOR 的防機器人擋成 403，
 * 看起來像「學校沒訂」其實只是「腳本被擋」。用 playwright 開實體 Chrome（比照 zlib_fetch.mjs）
 * 出版社看到的是真人瀏覽器，有訂就會給 PDF 連結。
 *
 * 判定：頁面上有 PDF 連結（href 含 /pdf/ 或 .pdf 或 download）且抓回來是 %PDF → 存檔；
 *      頁面有 "Get access"／"Purchase"／"Buy"／"Sign in to access" 且沒有 PDF → 校方沒訂；
 *      其他 → 記 unknown 給人看。
 *
 *   node scripts/doi_browser_fetch.mjs output/top-papers/biblical-studies-doi.json "G:/…/聖經研究五百篇" [--limit 6] [--offset 0]
 *
 * 🚨 12 秒一篇、跑完就關，別開多分頁：機構 IP 被擋是整校一起擋。
 */
import { chromium } from 'playwright'
import fs from 'node:fs'
import path from 'node:path'

const [listPath, outDir, ...rest] = process.argv.slice(2)
const arg = (k, d) => { const i = rest.indexOf(k); return i >= 0 ? Number(rest[i + 1]) : d }
const limit = arg('--limit', 9999), offset = arg('--offset', 0)
const items = JSON.parse(fs.readFileSync(listPath, 'utf8')).slice(offset, offset + limit)
const ledgerPath = listPath.replace(/\.json$/, '-browser-ledger.json')
const ledger = fs.existsSync(ledgerPath) ? JSON.parse(fs.readFileSync(ledgerPath, 'utf8')) : {}
fs.mkdirSync(outDir, { recursive: true })
const sleep = ms => new Promise(r => setTimeout(r, ms))
const safe = s => s.replace(/[\\/:*?"<>|]+/g, '／').slice(0, 90)

const browser = await chromium.launch({ headless: false, channel: 'chrome' })
const ctx = await browser.newContext({ acceptDownloads: true, locale: 'en-US' })
const page = await ctx.newPage()

let ok = 0, noAccess = 0, unknown = 0
for (const it of items) {
  if (ledger[it.doi]?.status === 'ok') continue
  const url = 'https://doi.org/' + it.doi
  process.stdout.write(`\n── ${it.year} ${it.title.slice(0, 60)}\n   ${url}\n`)
  let status = 'unknown', note = ''
  try {
    const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
    await sleep(4000)
    const finalUrl = page.url()
    const html = await page.content()
    const text = (await page.evaluate(() => document.body?.innerText || '')).slice(0, 20000)
    const ct = resp?.headers()['content-type'] || ''
    let pdfHref = null
    if (ct.includes('application/pdf')) pdfHref = finalUrl
    if (!pdfHref) {
      const hrefs = await page.evaluate(() => Array.from(document.querySelectorAll('a[href]')).map(a => ({ h: a.href, t: (a.innerText || a.getAttribute('aria-label') || '').trim() })))
      const cand = hrefs.filter(x => /\/pdf\/|\.pdf(\?|$)|\/doi\/pdf|download.*pdf|pdf.*download|epdf|\/reader\//i.test(x.h + ' ' + x.t) && !/supplement|toc|front|back-matter|cover/i.test(x.h))
      const first = cand.find(x => /pdf/i.test(x.t)) || cand[0]
      pdfHref = first?.h || null
    }
    const denied = /get access|purchase|buy this|sign in to access|institutional login|rent this|add to cart|access options|purchase pdf|subscribe/i.test(text)
    if (pdfHref) {
      const r = await ctx.request.get(pdfHref, { timeout: 90000, headers: { Referer: finalUrl } })
      const buf = await r.body()
      if (buf.slice(0, 5).toString() === '%PDF-') {
        const dest = path.join(outDir, `${it.year}_${safe(it.author.split(/[,&]/)[0].trim().split(' ').pop())}_${safe(it.title)}.pdf`)
        fs.writeFileSync(dest, buf)
        status = 'ok'; note = `${(buf.length / 1024) | 0} KB ← ${pdfHref}`; ok++
      } else {
        status = denied ? 'no-access' : 'pdf-link-not-pdf'; note = `${pdfHref} → ${r.status()} ${r.headers()['content-type'] || ''}`
        if (status === 'no-access') noAccess++; else unknown++
      }
    } else if (denied) {
      status = 'no-access'; note = new URL(finalUrl).hostname; noAccess++
    } else if (/403|access denied|just a moment|verify you are human|captcha/i.test(text + html.slice(0, 3000))) {
      status = 'blocked'; note = new URL(finalUrl).hostname; unknown++
    } else {
      status = 'unknown'; note = new URL(finalUrl).hostname; unknown++
    }
  } catch (e) {
    status = 'error'; note = String(e).slice(0, 120); unknown++
  }
  ledger[it.doi] = { status, note, title: it.title, year: it.year, when: new Date().toISOString() }
  fs.writeFileSync(ledgerPath, JSON.stringify(ledger, null, 1))
  process.stdout.write(`   ${status}  ${note}\n`)
  await sleep(12000)
}
await browser.close()
console.log(`\n存檔 ${ok}／校方沒訂 ${noAccess}／不確定 ${unknown}；帳本 ${ledgerPath}`)
