/**
 * z-library 依清單逐本下載 → repo 的 z-lib/ drop 夾。
 *
 * 銜接既有流程：檔案落進 z-lib/ 之後，每日 16:00 的 ingest_new_books.py 會自己
 * 判作者書名、分類、搬進 Drive 電子圖書館。這支只負責「把書弄下來」。
 *
 * 站方前面擋著 DiamWall（curl 只會拿到 513 challenge 頁），所以走 playwright 開
 * 真的 Chrome；**不要覆寫 userAgent**，DiamWall 會比對 UA 與指紋，自訂 UA 反而過
 * 不了牆。登入狀態存 c:/tmp/zlib_state.json，之後免登入。
 *
 * 免費帳號每日有下載上限（十本上下），所以這支的設計前提就是「每天跑一輪、跑到額
 * 度用完就停」，配 Windows 排程長期消化清單。帳本記在
 * scripts/state/zlib_ledger.jsonl，重跑不會重抓。
 *
 *   node scripts/zlib_fetch.mjs --list c:/tmp/wanted.jsonl --limit 8
 *   node scripts/zlib_fetch.mjs --list ... --dry-run     # 只查不下載
 */
import { chromium } from 'playwright'
import { readFileSync, writeFileSync, appendFileSync, existsSync, mkdirSync, readdirSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const HOST = 'https://z-library.sk'
const STATE = 'c:/tmp/zlib_state.json'
const DROP = resolve(ROOT, 'z-lib')
const LEDGER = resolve(ROOT, 'scripts/state/zlib_ledger.jsonl')

const args = process.argv.slice(2)
const arg = (n, d = null) => {
  const i = args.indexOf(n)
  return i >= 0 ? args[i + 1] : d
}
const DRY = args.includes('--dry-run')
const LIMIT = Number(arg('--limit', '8'))

function env() {
  const out = {}
  for (const line of readFileSync(resolve(ROOT, '.env'), 'utf8').split('\n')) {
    const t = line.trim()
    if (!t || t.startsWith('#') || !t.includes('=')) continue
    const i = t.indexOf('=')
    out[t.slice(0, i).trim()] = t.slice(i + 1).trim().replace(/^["']|["']$/g, '')
  }
  return out
}

/** 已經處理過的（抓到、或查無）不再重試。 */
function doneKeys() {
  if (!existsSync(LEDGER)) return new Set()
  return new Set(
    readFileSync(LEDGER, 'utf8')
      .split('\n')
      .filter(Boolean)
      .map((l) => {
        try { return JSON.parse(l).key } catch { return null }
      })
      .filter(Boolean)
  )
}

const note = (rec) => appendFileSync(LEDGER, JSON.stringify({ ...rec, at: new Date().toISOString() }) + '\n', 'utf8')

/** DiamWall 的 challenge 會自己驗完再轉走；等它，別把那一頁當內容解析。 */
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

/** 挑版本：繁體優先、其次簡體，格式 EPUB 優先（PDF 常是掃描本，還要 OCR）。 */
/**
 * 挑版本。`expect` 是書名核心詞、`who` 是作者／譯者核心詞——沒有這道閘，搜「韋伯
 * 中國的宗教」會抓到孫中興《久等了，韋伯先生！》這種研究專書而不是原著中譯。
 */
const BLACKLIST = (() => {
  // 跟 scripts/author_blacklist.py 同一份名單，避免兩邊各記一套。
  try {
    const f = new URL('../data/author-blacklist.json', import.meta.url)
    const raw = JSON.parse(readFileSync(f, 'utf-8'))
    return (raw.authors || []).flatMap((a) => [a.name, ...(a.aka || [])])
      .map((n) => n.toLowerCase().replace(/\s+/g, ''))
      .filter(Boolean)
  } catch {
    return []
  }
})()

export function isBlacklisted(...fields) {
  const hay = fields.filter(Boolean).join(' | ').toLowerCase().replace(/\s+/g, '')
  return BLACKLIST.some((n) => hay.includes(n))
}

export function rank(hit, query = '', expect = '', who = '') {
  const lang = (hit.language || '').toLowerCase()
  const ext = (hit.extension || '').toLowerCase()
  // 站上有一批「書名就是別人的搜尋字串」的垃圾上傳（多半是 txt/english），
  // 命中它們比沒命中更糟——會把一本假書送進 drop 夾。
  const title = (hit.title || '').trim()
  // 使用者判定不值得讀的作者（data/author-blacklist.json）——寧可沒命中也別抓回來
  if (isBlacklisted(hit.author, title)) return -100
  if (['txt', 'rar', 'zip', 'doc'].includes(ext)) return -100
  if (query && title && title.replace(/\s+/g, '') === query.replace(/\s+/g, '')) return -100
  const flat = (x) => (x || '').toLowerCase().replace(/[\s《》〈〉「」（）()：:·‧、,，.。!！?？—\-]/g, '')
  if (expect && !flat(title).includes(flat(expect))) return -100
  if (who && !flat(`${hit.author} ${title}`).includes(flat(who))) return -100
  let s = 0
  if (lang.includes('traditional')) s += 40
  else if (lang.includes('chinese')) s += 25
  else if (lang.includes('english')) s += 5
  if (ext === 'epub') s += 20
  else if (ext === 'azw3' || ext === 'mobi') s += 12
  else if (ext === 'pdf') s += 8
  const mb = parseFloat(hit.filesize) || 0
  if (mb > 0 && mb < 60) s += 4          // 動輒上百 MB 的多半是掃描
  return s
}

async function search(page, q) {
  await gotoPastWall(page, `${HOST}/s/${encodeURIComponent(q)}`)
  await page.waitForSelector('z-bookcard', { timeout: 20000 }).catch(() => {})
  return page.evaluate(() => {
    const cards = [...document.querySelectorAll('z-bookcard')]
    return cards.slice(0, 25).map((el) => {
      const a = (n) => el.getAttribute(n) || ''
      const t = (sel) => el.querySelector(sel)?.textContent?.trim() || ''
      return {
        title: t('[slot="title"]') || a('title'),
        author: t('[slot="author"]') || a('author'),
        year: a('year'), language: a('language'),
        extension: a('extension'), filesize: a('filesize'),
        href: a('href') || el.querySelector('a')?.getAttribute('href') || '',
      }
    })
  })
}

async function login(page, e) {
  if (!e.ZLIB_EMAIL || !e.ZLIB_PASSWORD) throw new Error('.env 沒有 ZLIB_EMAIL / ZLIB_PASSWORD')
  await gotoPastWall(page, `${HOST}/`)
  const loggedIn = await page.locator('a[href*="/logout"], .user-info, [href*="/profile"]').count()
  if (loggedIn) return true
  await gotoPastWall(page, `${HOST}/login`)
  await page.fill('input[name="email"]', e.ZLIB_EMAIL).catch(() => {})
  await page.fill('input[name="password"]', e.ZLIB_PASSWORD).catch(() => {})
  await Promise.all([
    page.waitForLoadState('domcontentloaded').catch(() => {}),
    page.click('button[type="submit"], input[type="submit"]').catch(() => {}),
  ])
  await page.waitForTimeout(5000)
  return (await page.locator('a[href*="/logout"], [href*="/profile"]').count()) > 0
}

async function main() {
  const e = env()
  const listPath = arg('--list')
  if (!listPath) throw new Error('需要 --list <jsonl>')
  const wanted = readFileSync(listPath, 'utf8').split('\n').filter(Boolean).map((l) => JSON.parse(l))
  const done = doneKeys()
  const todo = wanted.filter((w) => !done.has(w.key)).slice(0, LIMIT)
  console.log(`清單 ${wanted.length} 筆，已處理 ${done.size}，本輪 ${todo.length} 筆${DRY ? '（只查）' : ''}`)
  if (!todo.length) return

  mkdirSync(DROP, { recursive: true })
  mkdirSync(dirname(LEDGER), { recursive: true })
  const browser = await chromium.launch({ headless: false, channel: 'chrome' })
  const context = await browser.newContext({
    locale: 'zh-TW',
    acceptDownloads: true,
    ...(existsSync(STATE) ? { storageState: STATE } : {}),
  })
  const page = await context.newPage()
  let downloadFails = 0
  try {
    const ok = await login(page, e)
    console.log(ok ? '✓ 已登入' : '⚠ 登入狀態不明，先試著抓看看')
    await context.storageState({ path: STATE })

    for (const w of todo) {
      const hits = await search(page, w.query)
      if (!hits.length) {
        console.log(`  ✗ 查無：${w.query}`)
        note({ key: w.key, query: w.query, status: 'not-found' })
        await page.waitForTimeout(3000)
        continue
      }
      const scored = hits.map((h) => [rank(h, w.query, w.expect, w.who), h])
      if (DRY) {
        // 只查的時候把被閘擋掉的也列出來，才看得出「是閘太嚴，還是站上真的沒有」
        for (const [r, h] of scored.slice(0, 6)) {
          console.log(`     ${r > 0 ? '✓' : '·'} ${String(r).padStart(4)} ${(h.title || '').slice(0, 36).padEnd(38)}` +
            ` ${(h.author || '').slice(0, 14).padEnd(16)} ${h.language || ''} ${h.extension || ''}`)
        }
      }
      const ranked = scored.filter(([r]) => r > 0).sort((a, b) => b[0] - a[0])
      if (!ranked.length) {
        console.log(`  ✗ 沒有對得上的版本：${w.query}`)
        note({ key: w.key, query: w.query, status: 'no-usable-hit' })
        await page.waitForTimeout(3000)
        continue
      }
      const best = ranked[0][1]
      console.log(`  → ${w.query}\n     ${best.title?.slice(0, 46)} | ${best.language} ${best.extension} ${best.filesize}`)
      if (DRY) {
        note({ key: w.key, query: w.query, status: 'dry', pick: best })
        await page.waitForTimeout(2500)
        continue
      }
      try {
        await gotoPastWall(page, best.href.startsWith('http') ? best.href : HOST + best.href)
        const [dl] = await Promise.all([
          page.waitForEvent('download', { timeout: 60000 }),
          // 真正的下載是 a.addDownloadedBook（href=/dl/…）；a.dlButton 在 DOM 裡
          // 先出現的那個是 "Read Online"，點了不會有 download 事件。
          page.click('a.addDownloadedBook, a[href^="/dl/"]', { timeout: 20000 }),
        ])
        const name = dl.suggestedFilename()
        await dl.saveAs(resolve(DROP, name))
        console.log(`     ✓ ${name}`)
        downloadFails = 0
        note({ key: w.key, query: w.query, status: 'downloaded', file: name, pick: best })
      } catch (err) {
        const msg = String(err).slice(0, 120)
        console.log(`     ✗ 下載失敗：${msg}`)
        note({ key: w.key, query: w.query, status: 'download-failed', error: msg })
        // 額度用完的樣子就是「點了下載鈕但永遠等不到 download 事件」，站方不會
        // 明說。連兩本都這樣就是今天到頂了，收工，明天排程再來。
        downloadFails += 1
        if (/limit|quota|上限/i.test(msg) || downloadFails >= 2) {
          console.log('  今日額度應該用完了，本輪結束')
          note({ key: '_quota', status: 'quota-exhausted' })
          break
        }
      }
      await page.waitForTimeout(4000)
    }
  } finally {
    await browser.close()
    console.log(`drop 夾現有 ${readdirSync(DROP).length} 個檔`)
  }
}

await main()
