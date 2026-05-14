/**
 * Debug version of biblical-shot — takes screenshot without waiting for .node-card,
 * dumps DOM + console + network errors so we can see what's actually happening.
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
const APP_BASE = process.env.APP_BASE || 'http://localhost:3002'

const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: USER_EMAIL,
  options: { redirectTo: APP_BASE + '/genealogy/biblical' },
})
const actionLink = linkData.properties.action_link

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 2800, height: 1800 } })
const page = await context.newPage()

// ── capture console + page errors + failed requests ────
const consoleLogs = []
page.on('console', msg => consoleLogs.push(`[${msg.type()}] ${msg.text()}`))
page.on('pageerror', err => consoleLogs.push(`[pageerror] ${err.message}\n${err.stack}`))
page.on('requestfailed', req => consoleLogs.push(`[reqfail] ${req.url()} — ${req.failure()?.errorText}`))
page.on('response', resp => {
  if (resp.status() >= 400) consoleLogs.push(`[resp ${resp.status()}] ${resp.url()}`)
})

await page.goto(actionLink, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const prodUrl = page.url()
const fragment = new URL(prodUrl).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const expiresIn = parseInt(params.get('expires_in') || '3600', 10)

function decodeJwt(token) {
  const payload = token.split('.')[1]
  const padded = payload + '='.repeat((4 - payload.length % 4) % 4)
  return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8'))
}
const jwt = decodeJwt(accessToken)
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken,
  refresh_token: refreshToken,
  expires_at: jwt.exp,
  expires_in: expiresIn,
  token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: '', app_metadata: jwt.app_metadata||{}, user_metadata: jwt.user_metadata||{}, role: jwt.role, aal: jwt.aal, amr: jwt.amr||[], session_id: jwt.session_id, is_anonymous: false },
}
function base64url(str) {
  return Buffer.from(str, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
const cookieValue = 'base64-' + base64url(JSON.stringify(session))
await context.addCookies([{
  name: `sb-${projectRef}-auth-token`,
  value: cookieValue,
  domain: new URL(APP_BASE).hostname,
  path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])

await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForTimeout(3000)

const url = page.url()
console.log('LANDED:', url)

// dump DOM summary
const summary = await page.evaluate(() => {
  return {
    title: document.title,
    bodyTextSample: document.body.innerText.slice(0, 1500),
    cardCount: document.querySelectorAll('.node-card').length,
    spineTreeExists: !!document.querySelector('.bg-stone-50'),
    canvasExists: !!document.querySelector('div[style*="transform"]'),
    errorBlocks: Array.from(document.querySelectorAll('[class*="error"], pre')).map(e => e.textContent?.slice(0, 500)).filter(Boolean),
    h1: document.querySelector('h1')?.textContent,
    rootChildCount: document.querySelector('#__nuxt')?.children.length,
  }
})
console.log('DOM SUMMARY:', JSON.stringify(summary, null, 2))

console.log('\n--- CONSOLE LOGS ---')
consoleLogs.forEach(l => console.log(l))

await page.screenshot({ path: 'c:/tmp/biblical-debug.png', fullPage: false })
console.log('\nScreenshot: c:/tmp/biblical-debug.png')

await browser.close()
