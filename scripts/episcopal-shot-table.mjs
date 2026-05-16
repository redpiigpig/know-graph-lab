/** Quick screenshot of /genealogy/episcopal (the existing table view) to verify the toggle. */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}

const APP_BASE = process.env.APP_BASE || 'http://localhost:3004'
const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, { auth: { autoRefreshToken: false, persistSession: false } })
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink', email: env.ALLOWED_EMAIL || 'redpiigpig@gmail.com',
  options: { redirectTo: APP_BASE + '/genealogy/episcopal' },
})
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1600, height: 1000 } })
const page = await context.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})

const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
function decodeJwt(t) { const p = t.split('.')[1]; const padded = p + '='.repeat((4 - p.length % 4) % 4); return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8')) }
const jwt = decodeJwt(accessToken)
const session = { access_token: accessToken, refresh_token: refreshToken, expires_at: jwt.exp, expires_in: 3600, token_type: 'bearer', user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: jwt.phone || '', app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {}, role: jwt.role, aal: jwt.aal, amr: jwt.amr || [], session_id: jwt.session_id, is_anonymous: jwt.is_anonymous || false } }
function base64url(s) { return Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') }
const projectRef = new URL(env.SUPABASE_URL).hostname.split('.')[0]
await context.addCookies([{ name: `sb-${projectRef}-auth-token`, value: 'base64-' + base64url(JSON.stringify(session)), domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax' }])

await page.goto(APP_BASE + '/genealogy/episcopal', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForTimeout(1500)
await page.screenshot({ path: 'c:/tmp/episcopal-table.png', fullPage: false })
console.log('saved c:/tmp/episcopal-table.png')
await browser.close()
