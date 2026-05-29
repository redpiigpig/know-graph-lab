/**
 * Screenshot helper for /ebook/[id] reader. Pages we want to verify for
 * ANF Vol 1 after the polish+extras+consolidate pipeline:
 *
 *   page=1  → 封面（cover hero with author imprint）
 *   page=5  → 革利免一書 第1-10章（multi-chap consolidated letter page）
 *   page=11 → 致丟格那妥書 第1-10章（typical small letter）
 *   page=24 → 依納爵致羅馬人書 (single-page letter, ≤10 chap)
 *
 * Viewport capped at 1900×1100 — memory says >2000px detonates the session.
 *
 * Usage:
 *   node scripts/_ebook_shot.mjs --page 11 --out c:/tmp/ebook-p11.png
 */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

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

const PORT = flag('port', '3000')
const APP_BASE = `http://localhost:${PORT}`
const EBOOK_ID = flag('ebook', 'c98d358d-7066-4691-a896-b7232707b0db')
const PAGE = flag('page', '5')
const OUT = flag('out', `c:/tmp/ebook-${EBOOK_ID.slice(0,8)}-p${PAGE}.png`)
const VIEW = flag('view', 'bi')  // zh | bi | en

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false }
})

const target = `${APP_BASE}/ebook/${EBOOK_ID}?page=${PAGE}`
const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: 'redpiigpig@gmail.com',
  options: { redirectTo: target },
})
if (linkErr) { console.error('magic link failed:', linkErr); process.exit(1) }

const browser = await chromium.launch({ headless: true })
const VW = parseInt(flag('vw', '1900')) || 1900
const VH = parseInt(flag('vh', '1100')) || 1100
const ctx = await browser.newContext({ viewport: { width: VW, height: VH } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})

// Decode access_token from URL fragment and inject session cookie
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const at = params.get('access_token')
const rt = params.get('refresh_token') || ''
if (!at) { console.error('no access_token in redirect; URL =', page.url()); await browser.close(); process.exit(1) }
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

// Set view mode preference BEFORE the reader checks localStorage
await page.addInitScript((v) => { localStorage.setItem('ebook-viewMode', v) }, VIEW)

await page.goto(target, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})
await page.waitForSelector('article', { timeout: 15000 }).catch(()=>{})
await page.waitForTimeout(1500)
// Scroll to top
await page.evaluate(() => { document.querySelector('[ref="scrollEl"], .flex-1.overflow-y-auto')?.scrollTo?.(0,0) })

await page.screenshot({ path: OUT, fullPage: false })
console.log(`→ ${OUT}`)
await browser.close()
