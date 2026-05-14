/**
 * SVG diagnostic: dump card bboxes + line segments near 亞當/夏娃 + 拿鶴 area
 * to verify drop X is at marriage midpoint (instead of husband center).
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
  type: 'magiclink', email: USER_EMAIL,
  options: { redirectTo: APP_BASE + '/genealogy/biblical' },
})
const actionLink = linkData.properties.action_link

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 2000, height: 1400 } })
const page = await ctx.newPage()
await page.goto(actionLink, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const fragment = new URL(page.url()).hash.replace(/^#/, '')
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
  access_token: accessToken, refresh_token: refreshToken, expires_at: jwt.exp,
  expires_in: expiresIn, token_type: 'bearer',
  user: {
    id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: jwt.phone || '',
    app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {},
    role: jwt.role, aal: jwt.aal, amr: jwt.amr || [],
    session_id: jwt.session_id, is_anonymous: jwt.is_anonymous || false,
  },
}
function base64url(str) {
  return Buffer.from(str, 'utf-8').toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
const cookieValue = 'base64-' + base64url(JSON.stringify(session))
await ctx.addCookies([{
  name: `sb-${projectRef}-auth-token`, value: cookieValue,
  domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])

await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForSelector('.node-card', { timeout: 30000 })
await page.waitForTimeout(2500)

const expand = process.argv[2]
const peopleArg = process.argv.slice(3)
const yMin = process.env.Y_MIN ? parseInt(process.env.Y_MIN, 10) : null
const yMax = process.env.Y_MAX ? parseInt(process.env.Y_MAX, 10) : null
if (expand) {
  await page.evaluate((target) => {
    const cards = Array.from(document.querySelectorAll('.node-card'))
    for (const c of cards) {
      if (c.textContent?.includes(target)) {
        const btn = c.querySelector('button[title*="展開"]')
        if (btn) { btn.click(); return true }
      }
    }
    return false
  }, expand)
  await page.waitForTimeout(1500)
}

const data = await page.evaluate(([people, yMin, yMax]) => {
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const find = (name) => {
    const matches = cards.filter(c => c.textContent?.includes(name))
    return matches.map(c => ({
      text: c.textContent?.replace(/\s+/g,' ').slice(0, 50),
      cx: parseFloat(c.style.left || '0') + parseFloat(c.style.width || '0') / 2,
      cy: parseFloat(c.style.top || '0') + parseFloat(c.style.height || '52') / 2,
      x: parseFloat(c.style.left || '0'),
      y: parseFloat(c.style.top || '0'),
    }))
  }
  const out = {}
  for (const p of people) out[p] = find(p)
  // get all SVG line elements in canvas coords (SVG inside the transformed canvas)
  const allLines = []
  for (const l of document.querySelectorAll('line')) {
    allLines.push({
      x1: parseFloat(l.getAttribute('x1') || '0'),
      y1: parseFloat(l.getAttribute('y1') || '0'),
      x2: parseFloat(l.getAttribute('x2') || '0'),
      y2: parseFloat(l.getAttribute('y2') || '0'),
      stroke: l.getAttribute('stroke') || '',
      dash: l.getAttribute('stroke-dasharray') || '',
    })
  }
  out._allLineCount = allLines.length
  // Filter lines: keep those whose midpoint Y lies within [yMin, yMax]
  if (yMin != null && yMax != null) {
    out._linesInY = allLines.filter(l =>
      Math.min(l.y1, l.y2) >= yMin && Math.max(l.y1, l.y2) <= yMax
    ).sort((a, b) => a.x1 - b.x1)
  }
  return out
}, [peopleArg.length ? peopleArg : ['拉麥'], yMin, yMax])
console.log(JSON.stringify(data, null, 2))

await browser.close()
