/**
 * Click 展開朝代, zoom out to scale 0.4, pan to Levi, screenshot.
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
const outPath = process.argv[2] || 'c:/tmp/levi-zoomed.png'
const targetScale = parseFloat(process.argv[3] || '0.3')

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

await page.evaluate(() => {
  for (const b of document.querySelectorAll('button')) {
    if (b.textContent?.replace(/\s+/g, '').includes('展開朝代')) { b.click(); return }
  }
})
await page.waitForTimeout(2500)

// Zoom out to see Levi + immediate subtree
await page.evaluate((scale) => {
  const vp = document.querySelector('.bg-stone-50')
  if (!vp) return
  const canvas = vp.querySelector('div[style*="transform"]')
  // Center the camera on Levi at roughly center of viewport
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const levi = cards.find(c => (c.textContent || '').match(/L23\s*利未/))
  if (!levi) return
  const cardRect = levi.getBoundingClientRect()
  const vpRect = vp.getBoundingClientRect()
  const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/)
  if (!m) return
  const [, tx, ty, sc] = m.map(Number)
  // World position of Levi
  const worldX = (cardRect.left - vpRect.left - tx) / sc
  const worldY = (cardRect.top - vpRect.top - ty) / sc
  // Center camera on Levi with new scale
  const newTx = vp.clientWidth / 2 - worldX * scale
  const newTy = 100 - worldY * scale  // top margin 100
  canvas.style.transform = `translate(${newTx}px, ${newTy}px) scale(${scale})`
}, targetScale)
await page.waitForTimeout(300)

await page.screenshot({ path: outPath })
console.log('saved', outPath)
await browser.close()
