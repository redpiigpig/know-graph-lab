/**
 * Debug: enumerate marriage + drop lines in rendered tree.
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
  type: 'magiclink', email: USER_EMAIL,
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

await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000)

// Sample marriage lines near gen 23 row (利未 + 米加 area)
const result = await page.evaluate(() => {
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const levi = cards.find(c => (c.textContent || '').match(/L23\s*利未/))
  const mika = cards.find(c => (c.textContent || '').includes('米加'))
  const judah = cards.find(c => (c.textContent || '').match(/J23\s*猶大/))
  if (!levi) return { error: 'no levi' }
  const leviTop = parseFloat(levi.style.top || '0')
  const leviLeft = parseFloat(levi.style.left || '0')
  const out = {
    levi: { top: leviTop, left: leviLeft, w: levi.offsetWidth, h: levi.offsetHeight },
    mika: mika ? { top: parseFloat(mika.style.top), left: parseFloat(mika.style.left), w: mika.offsetWidth } : null,
    judah: judah ? { top: parseFloat(judah.style.top), left: parseFloat(judah.style.left), w: judah.offsetWidth } : null,
  }
  // Find all SVG lines/marriages at y near levi
  const svgLines = Array.from(document.querySelectorAll('line, path'))
  const nearY = svgLines.filter(l => {
    const y1 = parseFloat(l.getAttribute('y1') || '0')
    const y2 = parseFloat(l.getAttribute('y2') || '0')
    return Math.abs((y1+y2)/2 - (leviTop + 30)) < 60 // within 60px of Levi center
  }).slice(0, 50)
  out.linesNearLevi = nearY.map(l => ({
    x1: parseFloat(l.getAttribute('x1') || '0'),
    y1: parseFloat(l.getAttribute('y1') || '0'),
    x2: parseFloat(l.getAttribute('x2') || '0'),
    y2: parseFloat(l.getAttribute('y2') || '0'),
    stroke: l.getAttribute('stroke') || (l.style && l.style.stroke) || '',
  }))
  return out
})
console.log(JSON.stringify(result, null, 2))
await browser.close()
