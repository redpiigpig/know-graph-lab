/**
 * Screenshot the new historical-borders map at several years.
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
  options: { redirectTo: APP_BASE + '/maps/historical-borders' },
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

await page.goto(APP_BASE + '/maps/historical-borders', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('svg path', { timeout: 30000 })
await page.waitForTimeout(2500)

async function shot(name) {
  const out = path.join(OUT_DIR, `borders_${name}.png`)
  await page.screenshot({ path: out, fullPage: false })
  console.log(`→ borders_${name}.png`)
}

async function setYear(y) {
  await page.evaluate((year) => {
    const range = document.querySelector('input[type="range"]')
    if (!range) throw new Error('no slider found')
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set
    setter.call(range, String(year))
    range.dispatchEvent(new Event('input', { bubbles: true }))
  }, y)
  await page.waitForTimeout(1000)
}

const years = [-4000, -2000, -1500, -500, 0, 500, 800, 1279, 1500, 1815, 2000]
for (const y of years) {
  await setYear(y)
  await shot(String(y))
}

// Switch to list view
await page.evaluate(() => {
  for (const b of document.querySelectorAll('button')) {
    if (b.textContent?.includes('國家列表')) { b.click(); return }
  }
})
await page.waitForTimeout(2000)
await shot('list_view')

await browser.close()
console.log('Done.')
