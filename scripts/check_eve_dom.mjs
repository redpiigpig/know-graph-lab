/** Find where 哈娃 (Eve) is rendered in the DOM. */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: 'redpiigpig@gmail.com',
  options: { redirectTo: 'http://localhost:3006/genealogy/islamic-tree' },
})

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1800, height: 1200 } })
const page = await context.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})

function decodeJwt(token) {
  const payload = token.split('.')[1]
  const padded = payload + '='.repeat((4 - payload.length % 4) % 4)
  return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8'))
}
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const jwt = decodeJwt(accessToken)
const projectRef = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken, refresh_token: refreshToken,
  expires_at: jwt.exp, expires_in: 3600, token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, role: jwt.role, aal: jwt.aal,
    app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {} },
}
function base64url(s) { return Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'') }
await context.addCookies([{
  name: `sb-${projectRef}-auth-token`,
  value: 'base64-' + base64url(JSON.stringify(session)),
  domain: 'localhost', path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])
await page.goto('http://localhost:3006/genealogy/islamic-tree?view=sunni', { waitUntil: 'domcontentloaded', timeout: 90000 })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2500)

// Click "先知鏈" auto-expand
const expBtn = page.locator('button[title*="先知鏈"]')
if (await expBtn.count() > 0) {
  await expBtn.first().click()
  await page.waitForTimeout(1200)
}


const result = await page.evaluate(() => {
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const summary = cards.map((c, i) => ({
    idx: i,
    text: (c.textContent || '').slice(0, 40),
    left: parseFloat(c.style.left || '0'),
    top: parseFloat(c.style.top || '0'),
    rectX: Math.round(c.getBoundingClientRect().x),
    rectY: Math.round(c.getBoundingClientRect().y),
    parent: c.parentElement?.className?.slice(0, 30),
  }))
  // Marriage lines (red horizontal) at gen 1 area (top<150)
  const lines = Array.from(document.querySelectorAll('svg line'))
    .map(l => ({
      x1: parseFloat(l.getAttribute('x1')),
      y1: parseFloat(l.getAttribute('y1')),
      x2: parseFloat(l.getAttribute('x2')),
      y2: parseFloat(l.getAttribute('y2')),
      stroke: l.getAttribute('stroke'),
    }))
    .filter(l => l.y1 < 200 && l.y2 < 200 && l.stroke && (l.stroke.includes('dc2626') || l.stroke.includes('f43f5e')))
  // Detect overlapping cards (any two cards with overlapping rect)
  const overlaps = []
  for (let i = 0; i < cards.length; i++) {
    for (let j = i+1; j < cards.length; j++) {
      const a = summary[i], b = summary[j]
      if (Math.abs(a.top - b.top) > 50) continue
      if (Math.abs(a.left - b.left) < 130) {
        overlaps.push([a, b])
      }
    }
  }
  // Find Ali (阿里) instances — match by Abu al-Hasan kunya (unique to Ali ibn Abi Talib)
  const aliCards = summary.filter(s => s.text.includes('Abu al-Hasan') || (s.text.startsWith('第 49 代阿里') && s.text.length < 50))
  return {
    total: cards.length,
    overlaps: overlaps.slice(0, 20).map(([a, b]) => ({ a: a.text.slice(0, 20), b: b.text.slice(0, 20), a_left: a.left, a_top: a.top, b_left: b.left, b_top: b.top })),
    aliInstances: aliCards.map(c => ({ top: c.top, left: c.left, text: c.text.slice(0, 30), hasSamePersonMarker: false })),
  }
})
console.log('Total cards:', result.total)
console.log(`\n--- Overlaps (${result.overlaps.length}) ---`)
for (const o of result.overlaps) console.log(' ', JSON.stringify(o))
console.log(`\n--- Ali instances (${result.aliInstances.length}) ---`)
for (const a of result.aliInstances) console.log(' ', JSON.stringify(a))

await browser.close()
