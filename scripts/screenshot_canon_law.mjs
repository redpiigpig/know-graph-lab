/**
 * Visual check of /canon-law — list page + CIC 1983 reader (page 1 + a mid page
 * to see the 卷/題 sidebar tree + 中/英/拉 three columns). Adapted from
 * screenshot_gnostic.mjs (magic-link auth + screenshot-bot device). Viewport-only
 * shots keep every image under the 2000px session limit.
 *
 * Usage: node scripts/screenshot_canon_law.mjs --base http://localhost:3000
 */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'
import path from 'node:path'

const env = {}
for (const l of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!l.includes('=') || l.trim().startsWith('#')) continue
  const [k, ...r] = l.split('=')
  env[k.trim()] = r.join('=').trim().replace(/^["']|["']$/g, '')
}
const args = process.argv.slice(2)
const flag = (n, d) => { const i = args.indexOf(`--${n}`); return i >= 0 ? args[i + 1] : d }
const APP_BASE = flag('base', 'http://localhost:3000')
const OUT_DIR = flag('out', 'c:/tmp/canon_law_shots')
const DEVICE = 'screenshot-bot'
fs.mkdirSync(OUT_DIR, { recursive: true })

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink', email: 'redpiigpig@gmail.com',
  options: { redirectTo: `${APP_BASE}/canon-law` },
})
if (linkErr) { console.error(linkErr); process.exit(1) }

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 1280, height: 1600 } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})

const fragment = new URL(page.url()).hash.replace(/^#/, '')
const at = new URLSearchParams(fragment).get('access_token')
const rt = new URLSearchParams(fragment).get('refresh_token') || ''
if (!at) { console.error('no access_token; url=', page.url()); process.exit(1) }
const dj = (t) => { const p = t.split('.')[1]; const pad = p + '='.repeat((4 - p.length % 4) % 4); return JSON.parse(Buffer.from(pad.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8')) }
const j = dj(at)
const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = { access_token: at, refresh_token: rt, expires_at: j.exp, expires_in: 3600, token_type: 'bearer',
  user: { id: j.sub, aud: j.aud, email: j.email, phone: '', app_metadata: j.app_metadata || {}, user_metadata: j.user_metadata || {}, role: j.role, aal: j.aal, amr: j.amr || [], session_id: j.session_id, is_anonymous: false } }
const b64u = (s) => Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
await ctx.addCookies([{ name: `sb-${ref}-auth-token`, value: 'base64-' + b64u(JSON.stringify(sess)),
  domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax' }])
await page.addInitScript((d) => { localStorage.setItem('kgl_device_id', d) }, DEVICE)

for (const [name, url, sel] of [
  ['portal', `${APP_BASE}/scripture-canon`, '.grid'],
  ['list', `${APP_BASE}/canon-law`, '.grid'],
  ['reader-p1', `${APP_BASE}/canon-law/cic-1983`, 'article'],
  ['reader-p3', `${APP_BASE}/canon-law/cic-1983?page=3`, 'article'],
]) {
  await page.goto(url, { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle').catch(() => {})
  await page.waitForSelector(sel, { timeout: 15000 }).catch(() => {})
  await page.waitForTimeout(900)
  const out = path.join(OUT_DIR, `${name}.jpg`)
  await page.screenshot({ path: out, type: 'jpeg', quality: 82 })
  console.log(`✓ ${name} → ${out}`)
}
await browser.close()
console.log('done')
