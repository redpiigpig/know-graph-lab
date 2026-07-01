/**
 * Take a screenshot of EVERY page of an ebook in the reader, saved to
 * a directory. Pairs with `vision_proofread_book.py` which then sends
 * the PNGs to Haiku Vision for visual quality checks.
 *
 * Reuses the magic-link auth pattern from _ebook_shot.mjs.
 *
 * Usage:
 *   node scripts/screenshot_book.mjs --ebook <id>           # all pages
 *   node scripts/screenshot_book.mjs --ebook <id> --pages 1-20  # subset
 *   node scripts/screenshot_book.mjs --ebook <id> --view bi      # bilingual
 *
 * Output: c:/tmp/proofread_<ebook_prefix>/p<NNN>.png
 */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'
import path from 'node:path'

const env = {}
for (const l of fs.readFileSync('.env','utf-8').split('\n')) {
  if (!l.includes('=') || l.trim().startsWith('#')) continue
  const [k, ...r] = l.split('=')
  env[k.trim()] = r.join('=').trim().replace(/^["']|["']$/g,'')
}

const args = process.argv.slice(2)
function flag(name, fallback) {
  const i = args.indexOf(`--${name}`)
  return i >= 0 ? args[i+1] : fallback
}

const APP_BASE = flag('base', 'http://localhost:3000')
const EBOOK_ID = flag('ebook', 'c98d358d-7066-4691-a896-b7232707b0db')
const PAGES_ARG = flag('pages', null)  // "1-20" or "5,12,15"
const VIEW = flag('view', 'bi')
const OUT_DIR = flag('out', `c:/tmp/proofread_${EBOOK_ID.slice(0,8)}`)
const HEADLESS = flag('headless', '1') !== '0'
// Trusted-device id this headless browser presents. Pre-approve it once:
//   insert into trusted_devices(user_id, device_id, status) values (…, 'screenshot-bot', 'approved')
// Without this the device.global.ts gate bounces the shot to /device-pending.
const DEVICE = flag('device', 'screenshot-bot')

// Resolve which pages to shoot
const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false }
})
const { data: book, error: bErr } = await admin
  .from('ebooks')
  .select('id,title,chunk_count,total_pages')
  .eq('id', EBOOK_ID).single()
if (bErr) { console.error(bErr); process.exit(1) }
const totalPages = book.total_pages || book.chunk_count || 0
console.log(`Book: ${book.title}`)
console.log(`Total pages: ${totalPages}`)

let pages = []
if (PAGES_ARG) {
  for (const part of PAGES_ARG.split(',')) {
    const m = part.match(/^(\d+)-(\d+)$/)
    if (m) {
      for (let i = +m[1]; i <= +m[2]; i++) pages.push(i)
    } else if (/^\d+$/.test(part)) {
      pages.push(+part)
    }
  }
} else {
  for (let i = 1; i <= totalPages; i++) pages.push(i)
}
console.log(`Shooting ${pages.length} pages → ${OUT_DIR}`)

fs.mkdirSync(OUT_DIR, { recursive: true })

// Auth via magic link
const target0 = `${APP_BASE}/ebook/${EBOOK_ID}?page=${pages[0]}`
const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: 'redpiigpig@gmail.com',
  options: { redirectTo: target0 },
})
if (linkErr) { console.error(linkErr); process.exit(1) }

const browser = await chromium.launch({ headless: HEADLESS })
// Narrower viewport keeps the resulting image height manageable for
// Vision API (taller letters wrap into more lines). 1280 is a sweet
// spot for reading text + screenshot file size.
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})

const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const at = params.get('access_token')
const rt = params.get('refresh_token') || ''
if (!at) { console.error('no access_token; url=', page.url()); process.exit(1) }
function dj(t){const p=t.split('.')[1];const pad=p+'='.repeat((4-p.length%4)%4);return JSON.parse(Buffer.from(pad.replace(/-/g,'+').replace(/_/g,'/'),'base64').toString('utf-8'))}
const j = dj(at)
const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = {
  access_token: at, refresh_token: rt, expires_at: j.exp, expires_in: 3600,
  token_type: 'bearer',
  user: { id: j.sub, aud: j.aud, email: j.email, phone: '',
    app_metadata: j.app_metadata||{}, user_metadata: j.user_metadata||{},
    role: j.role, aal: j.aal, amr: j.amr||[], session_id: j.session_id,
    is_anonymous: false }
}
const b64u = (s) => Buffer.from(s,'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await ctx.addCookies([{
  name: `sb-${ref}-auth-token`,
  value: 'base64-'+b64u(JSON.stringify(sess)),
  domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax'
}])

await page.addInitScript(({ v, d }) => {
  localStorage.setItem('ebook-viewMode', v)
  localStorage.setItem('kgl_device_id', d)  // present a pre-approved device
}, { v: VIEW, d: DEVICE })

let done = 0
const t0 = Date.now()
// First authenticated navigation cold-compiles the reader route (can exceed the
// 30s default). Raise the navigation timeout so the first page doesn't time out.
page.setDefaultNavigationTimeout(Number(flag('nav', 150000)))
for (const p of pages) {
  const url = `${APP_BASE}/ebook/${EBOOK_ID}?page=${p}`
  await page.goto(url, { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle').catch(()=>{})
  await page.waitForSelector('article', { timeout: 15000 }).catch(()=>{})
  await page.waitForTimeout(500)
  const outPath = path.join(OUT_DIR, `p${String(p).padStart(3,'0')}.jpg`)
  // We want fullPage so the footnote section at the bottom is captured,
  // but Anthropic Vision caps any dimension at 8000px. Long 10-chapter
  // pages can be 9000-12000px tall. So: measure scrollHeight, cap to
  // 7800px via clip so the API accepts the upload. Pages taller than
  // that lose a tail; trade-off is acceptable for v1 (most pages fit).
  const scrollH = await page.evaluate(() => document.documentElement.scrollHeight)
  const viewportW = page.viewportSize().width
  if (scrollH <= 7800) {
    await page.screenshot({ path: outPath, fullPage: true,
                            type: 'jpeg', quality: 80 })
  } else {
    await page.screenshot({ path: outPath, type: 'jpeg', quality: 80,
                            clip: { x: 0, y: 0, width: viewportW, height: 7800 } })
  }
  done++
  if (done % 5 === 0 || done === pages.length) {
    const rate = done / ((Date.now() - t0) / 1000)
    const eta = (pages.length - done) / Math.max(rate, 0.01)
    console.log(`  p${p} → ${path.basename(outPath)} (${done}/${pages.length}, ${rate.toFixed(1)}/s, ETA ${(eta/60).toFixed(1)}m)`)
  }
}

await browser.close()
console.log(`✓ done — ${pages.length} screenshots in ${OUT_DIR}`)
