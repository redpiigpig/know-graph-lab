/**
 * Screenshot world-religions map at 4 states to verify behavior mirrors modern:
 *   1) Modern, non-drill (overview)
 *   2) Modern, drilled into Central Realm
 *   3) Historical (-1500), non-drill
 *   4) Historical (-1500), drilled into Central Realm
 *
 * Run: node scripts/screenshot_world_religions.mjs
 */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'
import path from 'node:path'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}

const SUPABASE_URL = env.SUPABASE_URL
const SUPABASE_SERVICE_ROLE_KEY = env.SUPABASE_SERVICE_ROLE_KEY
const USER_EMAIL = env.ALLOWED_EMAIL || 'redpiigpig@gmail.com'
const APP_BASE = process.env.APP_BASE || 'http://localhost:3000'
const OUT_DIR = 'C:/tmp/wr-shots'
fs.mkdirSync(OUT_DIR, { recursive: true })

const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink', email: USER_EMAIL,
  options: { redirectTo: APP_BASE + '/maps/world-religions' },
})
const actionLink = linkData.properties.action_link

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1600, height: 1000 } })
const page = await context.newPage()

await page.goto(actionLink, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const expiresIn = parseInt(params.get('expires_in') || '3600', 10)
function decodeJwt(t) {
  const p = t.split('.')[1]; const padded = p + '='.repeat((4 - p.length % 4) % 4)
  return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8'))
}
const jwt = decodeJwt(accessToken)
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken, refresh_token: refreshToken, expires_at: jwt.exp,
  expires_in: expiresIn, token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: jwt.phone || '',
    app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {},
    role: jwt.role, aal: jwt.aal, amr: jwt.amr || [], session_id: jwt.session_id,
    is_anonymous: jwt.is_anonymous || false },
}
const b64u = s => Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
await context.addCookies([{
  name: `sb-${projectRef}-auth-token`, value: 'base64-' + b64u(JSON.stringify(session)),
  domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])

// Go to map page
await page.goto(APP_BASE + '/maps/world-religions', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
// Wait for map to load (admin_0 features have loaded paths)
await page.waitForSelector('svg path', { timeout: 20000 })
await page.waitForTimeout(2000)  // extra settle for paths

async function shot(name) {
  const out = path.join(OUT_DIR, `${name}.png`)
  await page.screenshot({ path: out, fullPage: false })
  const sz = fs.statSync(out).size
  console.log(`→ ${name}.png (${(sz/1024).toFixed(0)} KB)`)
}

async function setYear(y) {
  // The TimeAxis has an <input type="range"> for the year. Set via JS.
  await page.evaluate((year) => {
    const range = document.querySelector('input[type="range"]')
    if (!range) throw new Error('no slider found')
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
    setter.call(range, String(year))
    range.dispatchEvent(new Event('input', { bubbles: true }))
  }, y)
  await page.waitForTimeout(800)
}

async function clickRealm(name) {
  // Realm buttons in default legend
  await page.evaluate((nm) => {
    for (const b of document.querySelectorAll('button')) {
      if (b.textContent?.replace(/\s+/g, '').includes(nm)) { b.click(); return }
    }
  }, name)
  await page.waitForTimeout(800)
}

async function exitDrill() {
  await page.evaluate(() => {
    for (const b of document.querySelectorAll('button')) {
      if (b.textContent?.includes('返回八大界域') || b.textContent?.includes('← 返回')) { b.click(); return }
    }
  })
  await page.waitForTimeout(500)
}

// === 1) Modern, non-drill ===
console.log('[1] Modern non-drill (2026)')
await shot('1_modern_overview')

// === 2) Modern, drilled into 中央界域 ===
console.log('[2] Modern drilled into 中央界域')
await clickRealm('中央界域')
await shot('2_modern_drilled_central')

// Exit drill
await exitDrill()
await page.waitForTimeout(500)

// === 3) Historical -1500 non-drill ===
console.log('[3] Historical -1500 non-drill')
await setYear(-1500)
await shot('3_historical_overview_bc1500')

// === 4) Historical -1500 drilled into 中央 ===
console.log('[4] Historical -1500 drilled into 中央')
await clickRealm('中央界域')
await shot('4_historical_drilled_bc1500')

// Bonus: -500 (axial age) drilled
await setYear(-500)
await page.waitForTimeout(500)
await shot('5_historical_drilled_bc500')

// Bonus: 500 CE (classical) drilled
await setYear(500)
await page.waitForTimeout(500)
await shot('6_historical_drilled_500ce')

// Bonus: -4000 BCE drilled (Sumer only)
await setYear(-4000)
await page.waitForTimeout(500)
await shot('7_historical_drilled_bc4000')

// Bonus: 800 CE (Abbasid) drilled
await setYear(800)
await page.waitForTimeout(500)
await shot('8_historical_drilled_800ce_abbasid')

// Bonus: 800 CE non-drill (Abbasid borders crossing spheres)
await exitDrill()
await page.waitForTimeout(500)
await shot('9_historical_overview_800ce')

await browser.close()
console.log('Done. Screenshots at ' + OUT_DIR)
