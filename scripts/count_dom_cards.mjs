/**
 * Click 展開朝代 → dump ALL .node-card text content to see what renders.
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
const APP_BASE = process.env.APP_BASE || 'http://localhost:3003'

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
const context = await browser.newContext({ viewport: { width: 1800, height: 1200 } })
const page = await context.newPage()

await page.goto(actionLink, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const prodUrl = page.url()
const fragment = new URL(prodUrl).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const expiresIn = parseInt(params.get('expires_in') || '3600', 10)
if (!accessToken) { console.error('No access_token'); process.exit(1) }

function decodeJwt(token) {
  const payload = token.split('.')[1]
  const padded = payload + '='.repeat((4 - payload.length % 4) % 4)
  return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8'))
}
const jwt = decodeJwt(accessToken)
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken, refresh_token: refreshToken,
  expires_at: jwt.exp, expires_in: expiresIn, token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: jwt.phone || '',
    app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {},
    role: jwt.role, aal: jwt.aal, amr: jwt.amr || [], session_id: jwt.session_id,
    is_anonymous: jwt.is_anonymous || false },
}
function base64url(str) {
  return Buffer.from(str, 'utf-8').toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
await context.addCookies([{
  name: `sb-${projectRef}-auth-token`, value: 'base64-' + base64url(JSON.stringify(session)),
  domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])

await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000)

await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  for (const b of btns) {
    if (b.textContent?.replace(/\s+/g, '').includes('展開朝代')) { b.click(); return }
  }
})
await page.waitForTimeout(2500)

// Diagnose what name resolution sees
const diag = await page.evaluate(() => {
  // Probe page-local variable. Better: search node text for the target name.
  const cards = Array.from(document.querySelectorAll('.node-card'))
  return {
    leviPatriarch: cards.filter(c => (c.textContent || '').match(/L23\s*利未/)).length,
    hananiahZerubbabel: cards.filter(c => (c.textContent || '').includes('哈拿尼雅')).length,
    shealtielKid: cards.filter(c => (c.textContent || '').match(/J53\s*所羅巴伯/)).length,
  }
})
console.log('Diag:', diag)

// Dump all .node-card text (after expansion)
const dump = await page.evaluate(() => {
  const cards = Array.from(document.querySelectorAll('.node-card'))
  return cards.map(c => {
    const txt = (c.textContent || '').trim().replace(/\s+/g, ' ')
    const top = parseFloat(c.style.top || '0')
    const left = parseFloat(c.style.left || '0')
    return { txt, top, left }
  }).sort((a, b) => a.top - b.top || a.left - b.left)
})
console.log(`TOTAL CARDS: ${dump.length}\n`)
for (const d of dump) console.log(`  y=${String(Math.round(d.top)).padStart(5)} x=${String(Math.round(d.left)).padStart(5)} | ${d.txt}`)
await browser.close()
