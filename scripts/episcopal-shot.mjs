/**
 * Headless screenshot helper for /genealogy/episcopal-tree.
 * Usage:
 *   node scripts/episcopal-shot.mjs
 *   node scripts/episcopal-shot.mjs --width 1800 --height 1200 --out c:/tmp/episcopal.png
 *   node scripts/episcopal-shot.mjs --expand <branchId>
 */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}

const SUPABASE_URL = env.SUPABASE_URL
const SUPABASE_SERVICE_ROLE_KEY = env.SUPABASE_SERVICE_ROLE_KEY
const USER_EMAIL = env.ALLOWED_EMAIL || 'redpiigpig@gmail.com'
const APP_BASE = process.env.APP_BASE || 'http://localhost:3004'

const args = process.argv.slice(2)
function arg(name) { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : null }
const outPath = arg('out') || 'c:/tmp/episcopal-tree.png'
const viewportW = parseInt(arg('width') || '1800', 10)
const viewportH = parseInt(arg('height') || '1200', 10)

console.log('→ Mint magic link…')
const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, { auth: { autoRefreshToken: false, persistSession: false } })
const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink', email: USER_EMAIL,
  options: { redirectTo: APP_BASE + '/genealogy/episcopal-tree' },
})
if (linkErr) { console.error(linkErr); process.exit(1) }
const actionLink = linkData?.properties?.action_link
if (!actionLink) { console.error('No action_link'); process.exit(1) }

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: viewportW, height: viewportH } })
const page = await context.newPage()
page.on('console', msg => {
  if (msg.type() === 'error') console.log('  PAGE-ERR', msg.text().slice(0, 500))
})
page.on('pageerror', err => console.log('  PAGEERROR', err.message.slice(0, 500)))
await page.goto(actionLink, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})

const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const expiresIn = parseInt(params.get('expires_in') || '3600', 10)
if (!accessToken) { console.error('no access_token'); process.exit(1) }

function decodeJwt(t) { const p = t.split('.')[1]; const padded = p + '='.repeat((4 - p.length % 4) % 4); return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8')) }
const jwt = decodeJwt(accessToken)
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken, refresh_token: refreshToken, expires_at: jwt.exp, expires_in: expiresIn, token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: jwt.phone || '', app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {}, role: jwt.role, aal: jwt.aal, amr: jwt.amr || [], session_id: jwt.session_id, is_anonymous: jwt.is_anonymous || false },
}
function base64url(s) { return Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') }
const cookieValue = 'base64-' + base64url(JSON.stringify(session))
await context.addCookies([{ name: `sb-${projectRef}-auth-token`, value: cookieValue, domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax' }])

console.log(`→ Loading /genealogy/episcopal-tree`)
await page.goto(APP_BASE + '/genealogy/episcopal-tree', { waitUntil: 'domcontentloaded', timeout: 90000 })
await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {})

if (page.url().includes('/login')) {
  console.error('Auth cookie not accepted, redirected to /login')
  process.exit(1)
}

await page.waitForTimeout(3000)

// Optional zoom to viewport scale 1 (no fit-all)
const noFit = args.includes('--no-fit')
if (noFit) {
  await page.evaluate(() => {
    // Reset transform via clicking nothing — workaround: force no fit by reload then no-op
    // Instead, find the canvas wrapper and reset transform
    const wrapper = document.querySelector('.absolute.top-0.left-0.origin-top-left')
    if (wrapper) wrapper.style.transform = 'translate(20px, 20px) scale(0.6)'
  })
  await page.waitForTimeout(500)
}

// Optional: click a branch to expand it
const expandLabel = arg('expand')
if (expandLabel) {
  const btn = page.locator(`button:has-text("${expandLabel}")`).first()
  const exists = await btn.count()
  console.log(`  trying to click expand "${expandLabel}" — found ${exists} matches`)
  if (exists > 0) {
    await btn.click({ force: true })
    await page.waitForTimeout(1500)
  }
}

await page.screenshot({ path: outPath, fullPage: false })
console.log(`✔ saved to ${outPath}`)
await browser.close()
