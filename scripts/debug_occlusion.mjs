/**
 * Debug: find which expansion shape is hiding the Levi↔米加 marriage line.
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

// Click 展開朝代
await page.evaluate(() => {
  for (const b of document.querySelectorAll('button')) {
    if (b.textContent?.replace(/\s+/g, '').includes('展開朝代')) { b.click(); return }
  }
})
await page.waitForTimeout(3000)

// Find any SVG line/path that intersects y=3198 in x range 3500-3700 (米加→Levi marriage)
const res = await page.evaluate(() => {
  const all = Array.from(document.querySelectorAll('svg line, svg rect, svg path'))
  const hits = []
  for (const el of all) {
    const tag = el.tagName.toLowerCase()
    if (tag === 'line') {
      const x1 = parseFloat(el.getAttribute('x1') || '0')
      const y1 = parseFloat(el.getAttribute('y1') || '0')
      const x2 = parseFloat(el.getAttribute('x2') || '0')
      const y2 = parseFloat(el.getAttribute('y2') || '0')
      // Cross y=3198 within x 3500-3700?
      const minY = Math.min(y1, y2), maxY = Math.max(y1, y2)
      const minX = Math.min(x1, x2), maxX = Math.max(x1, x2)
      if (minY <= 3220 && maxY >= 3170 && minX <= 3700 && maxX >= 3500) {
        hits.push({ tag, x1, y1, x2, y2, stroke: el.getAttribute('stroke'),
          display: getComputedStyle(el).display, dataAttrs: el.outerHTML.slice(0, 200) })
      }
    }
  }
  // Also find ALL 米加 cards
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const allMika = cards.filter(c => (c.textContent || '').includes('米加')).map(c => ({
    text: (c.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40),
    top: parseFloat(c.style.top || '0'),
    left: parseFloat(c.style.left || '0'),
    w: c.offsetWidth, h: c.offsetHeight,
    display: getComputedStyle(c).display,
    classList: c.className,
  }))
  return { hits, allMika }
})
console.log('Lines crossing 米加→Levi area:')
for (const h of res.hits) console.log(' ', JSON.stringify(h, null, 2))
console.log('\nAll 米加 cards:')
for (const c of res.allMika) console.log(' ', JSON.stringify(c))
await browser.close()
