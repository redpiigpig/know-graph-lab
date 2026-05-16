/**
 * Headless screenshot helper for the Islamic genealogy tree page.
 *
 * Adapted from biblical-shot.mjs — same magic-link auth flow, different route.
 *
 * Usage:
 *   node scripts/islamic-shot.mjs                   # default (sunni view)
 *   node scripts/islamic-shot.mjs --view quranic    # ?view=quranic
 *   node scripts/islamic-shot.mjs --focus 穆罕默德   # pan to focus
 *   node scripts/islamic-shot.mjs --out path.png    # custom output
 *   node scripts/islamic-shot.mjs --width 1800 --height 1200
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
const APP_BASE = process.env.APP_BASE || 'http://localhost:3001'

const args = process.argv.slice(2)
function arg(name) {
  const i = args.indexOf(`--${name}`)
  return i >= 0 ? args[i + 1] : null
}
const focusName = arg('focus')
const view      = arg('view')  // sunni (default) | quranic | shia_twelver | shia_ismaili | shia_zaidi
const outPath   = arg('out') || `c:/tmp/islamic-${view || 'default'}${focusName ? '-' + focusName : ''}.png`
const fullPage  = args.includes('--full')

console.log('→ Minting magic link for', USER_EMAIL)
const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: USER_EMAIL,
  options: { redirectTo: APP_BASE + '/genealogy/islamic-tree' },
})
if (linkErr) { console.error('generateLink failed:', linkErr); process.exit(1) }
const actionLink = linkData?.properties?.action_link
if (!actionLink) { console.error('No action_link in response'); process.exit(1) }
console.log('  action_link:', actionLink.slice(0, 80) + '…')

const viewportW = parseInt(arg('width') || '1800', 10)
const viewportH = parseInt(arg('height') || '1200', 10)
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: viewportW, height: viewportH } })
const page = await context.newPage()

console.log('→ Following magic link…')
await page.goto(actionLink, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const prodUrl = page.url()
const fragment = new URL(prodUrl).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const expiresIn = parseInt(params.get('expires_in') || '3600', 10)
if (!accessToken) { console.error('No access_token in URL fragment, got:', prodUrl); process.exit(1) }
console.log(`  got tokens (${accessToken.length} chars)`)

function decodeJwt(token) {
  const payload = token.split('.')[1]
  const padded = payload + '='.repeat((4 - payload.length % 4) % 4)
  return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8'))
}
const jwt = decodeJwt(accessToken)
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
console.log('  project ref:', projectRef, ' user:', jwt.email)

const session = {
  access_token: accessToken, refresh_token: refreshToken,
  expires_at: jwt.exp, expires_in: expiresIn, token_type: 'bearer',
  user: {
    id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: jwt.phone || '',
    app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {},
    role: jwt.role, aal: jwt.aal, amr: jwt.amr || [],
    session_id: jwt.session_id, is_anonymous: jwt.is_anonymous || false,
  },
}
const cookieName = `sb-${projectRef}-auth-token`
const localhostHost = new URL(APP_BASE).hostname
function base64url(str) {
  return Buffer.from(str, 'utf-8').toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
const cookieValue = 'base64-' + base64url(JSON.stringify(session))
await context.addCookies([{
  name: cookieName, value: cookieValue,
  domain: localhostHost, path: '/',
  httpOnly: false, secure: false, sameSite: 'Lax',
}])
console.log(`→ Cookie set: ${cookieName}`)

const viewQS = view ? `?view=${encodeURIComponent(view)}` : ''
console.log(`→ Loading /genealogy/islamic-tree${viewQS}`)
await page.goto(APP_BASE + '/genealogy/islamic-tree' + viewQS, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
console.log('  landed at:', page.url())
if (page.url().includes('/login')) {
  console.error('  ⚠️ Auth cookie rejected, still on /login')
  process.exit(1)
}

await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2500) // let layout settle

async function panTo(target, forceScale = null) {
  await page.evaluate(({ target, forceScale }) => {
    const vp = document.querySelector('.bg-stone-50')
    if (!vp) return
    const cards = Array.from(document.querySelectorAll('.node-card'))
    const base = target.split('（')[0].trim()
    const matches = cards.filter(c => c.textContent?.includes(base))
    if (!matches.length) return
    matches.sort((a, b) => parseFloat(b.style.top || '0') - parseFloat(a.style.top || '0'))
    const card = matches[0]
    if (!card) return
    const canvas = vp.querySelector('div[style*="transform"]')
    if (!canvas) return
    const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/)
    if (!m) return
    const scale = forceScale != null ? forceScale : parseFloat(m[3])
    const cardLeft = parseFloat(card.style.left)
    const cardTop = parseFloat(card.style.top)
    const cardW = parseFloat(card.style.width)
    const vpRect = vp.getBoundingClientRect()
    const newPanX = vpRect.width / 2 - (cardLeft + cardW / 2) * scale
    const newPanY = vpRect.height / 2 - (cardTop + 26) * scale
    canvas.style.transform = `translate(${newPanX}px, ${newPanY}px) scale(${scale})`
  }, { target, forceScale })
  await page.waitForTimeout(400)
}
const zoomArg = arg('zoom')
const forceScale = zoomArg ? parseFloat(zoomArg) : null
if (focusName) {
  console.log(`→ Panning to "${focusName}"${forceScale ? ` @ zoom ${forceScale}` : ''}`)
  await panTo(focusName, forceScale)
}

// Card count for QA
const cardCount = await page.locator('.node-card').count()
console.log(`  rendered ${cardCount} cards`)

console.log(`→ Saving screenshot to ${outPath}`)
await page.screenshot({ path: outPath, fullPage })
console.log('✅ done')

await browser.close()
