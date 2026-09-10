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
const DROP = resolve(ROOT, 'z-lib')
const LEDGER = resolve(ROOT, 'scripts/state/zlib_ledger.jsonl')

const args = process.argv.slice(2)
const arg = (n, d = null) => {
  const i = args.indexOf(n)
  return i >= 0 ? args[i + 1] : d
}
const DRY = args.includes('--dry-run')
const LIMIT = Number(arg('--limit', '8'))
// 落空不花下載額度，但會花時間與搜尋次數，所以仍要有上限 —— 否則一輪會把
// 五千多筆清單整個走完。預設給下載目標的六倍。
const MAX_TRIES = Number(arg('--max-tries', String(Math.max(1, LIMIT) * 6)))

// 每個帳號要有各自的 session state 檔。共用一個的話，換帳號登入會把前一個的
// cookie 蓋掉，下次跑回原帳號又得重登，而且 DiamWall 對「同一個瀏覽器 profile
// 反覆換身分」特別敏感。
//
// 主帳號在 .env 裡沒有後綴（ZLIB_EMAIL），對應的 --account 值是空字串；但空字串
// 沒辦法乾淨地穿過 PowerShell → cmd → node 這條命令列，所以排程用 '1' 指主帳號。
const ACCOUNT = (arg('--account', '') === '1' ? '' : arg('--account', ''))
const STATE = ACCOUNT ? `c:/tmp/zlib_state_${ACCOUNT}.json` : 'c:/tmp/zlib_state.json'

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

// 下載失敗要重試幾次才放棄。搜到了、也挑到版本了，卡在下載那一步——最常見的
// 原因是當天額度用完（站方不明說，就是點了下載鈕永遠等不到 download 事件），
// 那是「今天不行」不是「這本不存在」。
const RETRY_FAILS = 3

/**
 * 已經處理過的（抓到、或查無）不再重試。
 *
 * 🚨 download-failed 不算「處理過」——每天額度用完時最後那兩本都會記成
 * download-failed，若當成已處理，等於每天靜靜燒掉兩本書再也不會回頭抓
 * （帳本裡已經這樣丟掉 8 本）。連續失敗 RETRY_FAILS 次才真的放棄。
 */
function doneKeys() {
  if (!existsSync(LEDGER)) return new Set()
  const fails = new Map()
  const done = new Set()
  for (const l of readFileSync(LEDGER, 'utf8').split('\n')) {
    if (!l) continue
    let r
    try { r = JSON.parse(l) } catch { continue }
    if (!r || !r.key) continue
    // 🚨 --dry-run 什麼都沒下載，不能算「已處理」。之前 dry 也寫進帳本，
    //    試跑一次就把那些 key 永久封死，正式跑時整份清單靜靜地變成 0 筆。
    if (r.status === 'dry') continue
    if (r.status === 'download-failed') {
      const n = (fails.get(r.key) || 0) + 1
      fails.set(r.key, n)
      if (n >= RETRY_FAILS) done.add(r.key)
      continue
    }
    done.add(r.key)
  }
  return done
}

const note = (rec) => appendFileSync(LEDGER, JSON.stringify({ ...rec, at: new Date().toISOString() }) + '\n', 'utf8')

// 挑版本的規則版本。探勘（--dry-run）判定「站上沒有」時會把這個字串一起記進
// 帳本——規則以後一定還會再放寬（2026-09-10 就因為少了繁簡正規化，把「心靈的
// 黑夜」判成不存在，而站上其實有「心灵的黑夜」），到時候要能精準地只撤掉舊規則
// 判過的那一批，而不是整份帳本重來。
const RULE = 'v2-t2s'

// 探勘的落空與正式跑的落空要分開記。兩者都算「已處理」而退出佇列，但探勘那批
// 是規則判的、可回溯；正式跑那批是真的搜過也試過了。
const missStatus = (base) => (DRY ? 'probe-miss' : base)

/**
 * DiamWall 的 challenge 會自己驗完再轉走；等它，別把那一頁當內容解析。
 *
 * 🚨 page.goto 自己會丟例外（net::ERR_ABORTED、frame detached、逾時），而這支
 * 是整條流程的最底層——2026-09-10 那一輪就是在這裡丟出未捕捉的例外，把 node
 * 整個帶走，帳號 3、4 的二十本額度一次都沒動用。導覽失敗屬於「這一筆跳過」，
 * 不是「整輪結束」，所以在這裡就把它吞掉、重試，真的過不去才回 false。
 */
async function gotoPastWall(page, url, tries = 3) {
  const blocked = (t) => /DiamWall|验证|驗證|Verifying/i.test(t)
  for (let i = 0; i < tries; i++) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 })
      if (!blocked(await page.title())) return true
      await page.waitForTimeout(12000)
      if (!blocked(await page.title())) return true
    } catch (err) {
      console.log(`     ↻ 導覽失敗（${String(err).split('\n')[0].slice(0, 70)}），重試 ${i + 1}/${tries}`)
      await page.waitForTimeout(5000)
    }
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

export function rank(hit, query = '', expect = '', who = '', wantLang = '', wantExt = '',
                     expectS = '', whoS = '') {
  const lang = (hit.language || '').toLowerCase()
  const ext = (hit.extension || '').toLowerCase()
  // 站上有一批「書名就是別人的搜尋字串」的垃圾上傳（多半是 txt/english），
  // 命中它們比沒命中更糟——會把一本假書送進 drop 夾。
  const title = (hit.title || '').trim()
  // 使用者判定不值得讀的作者（data/author-blacklist.json）——寧可沒命中也別抓回來
  if (isBlacklisted(hit.author, title)) return -100
  // 語言閘。一本書同時掛「中譯本」與「原文本」兩個目標時，若中譯本根本不存在，
  // 沒有這道閘就會退而抓回同一本原文 —— 重複下載，還吃掉一天十本裡的一格。
  // 找不到就讓它空手而回，明天再說。
  if (wantLang === 'zh' && !lang.includes('chinese')) return -100
  if (wantLang === 'orig' && lang.includes('chinese')) return -100
  if (['txt', 'rar', 'zip', 'doc'].includes(ext)) return -100
  // 格式閘。按頁碼指定的讀物（課程大綱寫「Blackwell Companion 91-122」那種）
  // 只有 PDF 對得上——epub／azw3 沒有固定分頁，抓回來就是翻不到指定的頁。
  // 下面的加分項偏好 epub，所以非得有這道閘才壓得住。
  if (wantExt && ext !== wantExt.toLowerCase()) return -100
  if (query && title && title.replace(/\s+/g, '') === query.replace(/\s+/g, '')) return -100
  const flat = (x) => (x || '').toLowerCase().replace(/[\s《》〈〉「」（）()：:·‧、,，.。!！?？—\-]/g, '')
  // 🚨 我們的清單一律繁體（repo 規矩），z-library 的中文藏書幾乎全是簡體。
  // 沒有這一道折衷，「心靈的黑夜」永遠對不上站上的「心灵的黑夜」——2026-09-10
  // 抽樣四十筆，命中率 2.5%，而漏掉的裡面至少三本站上明明就有，差的只是字體。
  // expectS／whoS 是 zlib_wanted.py 用 opencc 先轉好的簡體版，這裡兩邊都比。
  const matches = (hay, a, b) => flat(hay).includes(flat(a)) || (b && flat(hay).includes(flat(b)))
  if (expect && !matches(title, expect, expectS)) return -100
  if (who) {
    const w = flat(who)
    // 🚨 太短的姓氏不能當子字串比對。實測 who='Tu'（杜維明）配上空的 expect，
    //    唯一的閘門就只剩「含 tu 的中文書」，結果抓回一本雅思寫作書
    //    （音譯書名 "Shi tian tu po…" 裡剛好有 tu）。三個字以下的西文姓氏
    //    改成整詞比對，中日韓姓名本身夠獨特不受此限。
    const hay = `${hit.author} ${title}`
    const isShortLatin = /^[a-z]{1,3}$/.test(w)
    if (isShortLatin) {
      const words = hay.toLowerCase().split(/[^a-z]+/)
      if (!words.includes(w)) return -100
    } else if (!matches(hay, who, whoS)) {
      return -100
    }
  }
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

function creds(e) {
  const suffix = ACCOUNT ? `_${ACCOUNT}` : ''
  return { email: e[`ZLIB_EMAIL${suffix}`], password: e[`ZLIB_PASSWORD${suffix}`], suffix }
}

async function login(page, e) {
  const { email, password, suffix } = creds(e)
  if (!email || !password) throw new Error(`.env 沒有 ZLIB_EMAIL${suffix} / ZLIB_PASSWORD${suffix}`)
  await gotoPastWall(page, `${HOST}/`)
  const loggedIn = await page.locator('a[href*="/logout"], .user-info, [href*="/profile"]').count()
  if (loggedIn) return true
  await gotoPastWall(page, `${HOST}/login`)
  await page.fill('input[name="email"]', email).catch(() => {})
  await page.fill('input[name="password"]', password).catch(() => {})
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
  // 🚨 LIMIT 是「要抓幾本」不是「要試幾筆」。清單裡每本書都有 -zh 與 -orig 兩格，
  // 而西方近人著作多半沒有中譯，-zh 那格必然落空（語言閘會擋掉英文版，這是對的）。
  // 若拿 LIMIT 去切待辦清單，一輪十二筆可能全是落空的中譯目標，一本都沒抓到。
  // 所以這裡不預先切，改在迴圈裡數「成功下載」，抓滿了才收工。
  const todo = wanted.filter((w) => !done.has(w.key))
  console.log(`清單 ${wanted.length} 筆，已處理 ${done.size}，本輪目標 ${LIMIT} 本／最多試 ${MAX_TRIES} 筆${DRY ? '（只查）' : ''}`)
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
  let downloaded = 0
  try {
    const ok = await login(page, e)
    // 只印帳號代號，不印 email 與密碼
    console.log(`${ok ? '✓ 已登入' : '⚠ 登入狀態不明，先試著抓看看'}（帳號 ${ACCOUNT || '主'}）`)
    await context.storageState({ path: STATE })

    let tried = 0
    // 一筆搜壞了就跳下一筆；但整站掛掉的時候不該傻傻把清單走完，所以連續壞
    // 五筆就收工。
    let searchErrors = 0
    for (const w of todo) {
      if (tried >= MAX_TRIES) {
        console.log(`  已試 ${tried} 筆（上限 ${MAX_TRIES}），本輪結束`)
        break
      }
      if (searchErrors >= 5) {
        console.log('  連續五筆搜尋都失敗，站況不對，本輪結束')
        break
      }
      tried += 1
      let hits
      try {
        hits = await search(page, w.query)
        searchErrors = 0
      } catch (err) {
        // 搜尋這一步壞掉不代表這本書不存在，所以**不寫帳本**——下一輪還會再試。
        searchErrors += 1
        console.log(`  ⚠ 搜尋失敗，跳過本筆：${w.query}\n     ${String(err).split('\n')[0].slice(0, 90)}`)
        await page.waitForTimeout(4000)
        continue
      }
      if (!hits.length) {
        console.log(`  ✗ 查無：${w.query}`)
        note({ key: w.key, query: w.query, status: missStatus('not-found'), why: 'no-results', rule: RULE })
        await page.waitForTimeout(3000)
        continue
      }
      const scored = hits.map((h) => [
        rank(h, w.query, w.expect, w.who, w.lang || '', w.ext || '', w.expect_s || '', w.who_s || ''),
        h,
      ])
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
        note({ key: w.key, query: w.query, status: missStatus('no-usable-hit'), why: 'all-gated', rule: RULE })
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
        downloaded += 1
        note({ key: w.key, query: w.query, status: 'downloaded', file: name, pick: best })
        if (downloaded >= LIMIT) {
          console.log(`  已達本輪目標 ${LIMIT} 本，收工`)
          break
        }
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
    // 這一行是給 zlib_daily.ps1 讀的：它要知道這個帳號還有沒有額度，決定要不要
    // 換下一個帳號、或今天是不是已經湊滿目標。
    console.log(`本輪下載 ${downloaded} 本（帳號 ${ACCOUNT || '主'}）`)
    console.log(`drop 夾現有 ${readdirSync(DROP).length} 個檔`)
  }
}

// 🚨 頂層一定要接住。這支是排程從 PowerShell 叫起來的，未捕捉的例外會讓 node
// 直接爆掉、把整輪（含還沒輪到的帳號）帶走。印出來、以非零離開就好。
try {
  await main()
} catch (err) {
  console.log(`✗ 本輪中止：${String(err).split('\n')[0].slice(0, 160)}`)
  process.exitCode = 1
}
