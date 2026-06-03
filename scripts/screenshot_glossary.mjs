/** Visual check of /translation-glossary (翻譯定名) — principles page + a seeded
 * domain tab. Reuses the magic-link + screenshot-bot auth from screenshot_book.mjs.
 * Viewport-only shots stay under the 2000px session limit. */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'
import path from 'node:path'

const env = {}
for (const l of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!l.includes('=') || l.trim().startsWith('#')) continue
  const [k, ...r] = l.split('='); env[k.trim()] = r.join('=').trim().replace(/^["']|["']$/g, '')
}
const APP_BASE = 'http://localhost:3000'
const OUT_DIR = 'c:/tmp/glossary_shots'
fs.mkdirSync(OUT_DIR, { recursive: true })

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, { auth: { autoRefreshToken: false, persistSession: false } })
const { data: linkData, error } = await admin.auth.admin.generateLink({ type: 'magiclink', email: 'redpiigpig@gmail.com', options: { redirectTo: `${APP_BASE}/translation-glossary` } })
if (error) { console.error(error); process.exit(1) }

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 1280, height: 1500 } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const at = new URLSearchParams(new URL(page.url()).hash.replace(/^#/, '')).get('access_token')
const rt = new URLSearchParams(new URL(page.url()).hash.replace(/^#/, '')).get('refresh_token') || ''
if (!at) { console.error('no token', page.url()); process.exit(1) }
const dj = (t) => { const p = t.split('.')[1]; const pad = p + '='.repeat((4 - p.length % 4) % 4); return JSON.parse(Buffer.from(pad.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8')) }
const j = dj(at)
const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = { access_token: at, refresh_token: rt, expires_at: j.exp, expires_in: 3600, token_type: 'bearer', user: { id: j.sub, aud: j.aud, email: j.email, phone: '', app_metadata: j.app_metadata || {}, user_metadata: j.user_metadata || {}, role: j.role, aal: j.aal, amr: j.amr || [], session_id: j.session_id, is_anonymous: false } }
const b64u = (s) => Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
await ctx.addCookies([{ name: `sb-${ref}-auth-token`, value: 'base64-' + b64u(JSON.stringify(sess)), domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax' }])
await page.addInitScript(() => localStorage.setItem('kgl_device_id', 'screenshot-bot'))

await page.goto(`${APP_BASE}/translation-glossary`, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForTimeout(1200)
await page.screenshot({ path: path.join(OUT_DIR, 'principles.jpg'), type: 'jpeg', quality: 82 })
console.log('✓ principles')

// click 歷代帝王 tab button (has seeded name_root examples)
await page.getByRole('button', { name: /歷代帝王/ }).click().catch(() => {})
await page.waitForTimeout(700)
await page.screenshot({ path: path.join(OUT_DIR, 'rulers.jpg'), type: 'jpeg', quality: 82 })
console.log('✓ rulers')

await browser.close()
console.log('done')
