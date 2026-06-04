/** Throwaway: screenshot the Müller trilingual reader in parallel view, clipped
 * to <2000px for chat viewing. Reuses screenshot_book.mjs auth. node scripts/_mueller_shot.mjs [page] */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const l of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!l.includes('=') || l.trim().startsWith('#')) continue
  const [k, ...r] = l.split('=')
  env[k.trim()] = r.join('=').trim().replace(/^["']|["']$/g, '')
}
const APP = 'http://localhost:3000'
const ID = '33333333-3333-4333-8333-333333333333'
const PAGE = process.argv[2] || '1'
const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, { auth: { autoRefreshToken: false, persistSession: false } })
const { data: ld, error } = await admin.auth.admin.generateLink({ type: 'magiclink', email: 'redpiigpig@gmail.com', options: { redirectTo: `${APP}/ebook/${ID}?page=${PAGE}` } })
if (error) { console.error(error); process.exit(1) }
const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 1280, height: 1400 } })
const page = await ctx.newPage()
await page.goto(ld.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const frag = new URLSearchParams(new URL(page.url()).hash.replace(/^#/, ''))
const at = frag.get('access_token'), rt = frag.get('refresh_token') || ''
if (!at) { console.error('no token', page.url()); process.exit(1) }
const dj = (t) => { const p = t.split('.')[1]; const pad = p + '='.repeat((4 - p.length % 4) % 4); return JSON.parse(Buffer.from(pad.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString()) }
const j = dj(at), ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = { access_token: at, refresh_token: rt, expires_at: j.exp, expires_in: 3600, token_type: 'bearer', user: { id: j.sub, aud: j.aud, email: j.email, phone: '', app_metadata: j.app_metadata || {}, user_metadata: j.user_metadata || {}, role: j.role, aal: j.aal, amr: j.amr || [], session_id: j.session_id, is_anonymous: false } }
const b64u = (s) => Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
await ctx.addCookies([{ name: `sb-${ref}-auth-token`, value: 'base64-' + b64u(JSON.stringify(sess)), domain: 'localhost', path: '/', httpOnly: false, secure: false, sameSite: 'Lax' }])
await page.addInitScript(() => { localStorage.setItem('ebook-viewMode', 'parallel'); localStorage.setItem('kgl_device_id', 'screenshot-bot') })
await page.goto(`${APP}/ebook/${ID}?page=${PAGE}`, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('article', { timeout: 15000 }).catch(() => {})
await page.waitForTimeout(800)
await page.screenshot({ path: 'c:/tmp/mueller_reader.jpg', type: 'jpeg', quality: 82, clip: { x: 0, y: 0, width: 1280, height: 1850 } })
console.log('shot -> c:/tmp/mueller_reader.jpg  url=', page.url())
await browser.close()
