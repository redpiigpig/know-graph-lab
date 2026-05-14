/**
 * Headless screenshot helper for the biblical genealogy page.
 *
 * Auth: uses Supabase service-role to mint a magic-link for the configured
 * user, then Playwright navigates through it so the @nuxtjs/supabase session
 * cookies are set, then drives the page.
 *
 * Usage:
 *   node scripts/biblical-shot.mjs                  # default screenshot
 *   node scripts/biblical-shot.mjs --expand 拿鶴    # click ▼ on 拿鶴 then shot
 *   node scripts/biblical-shot.mjs --focus 他拉     # pan to focus on a person
 *   node scripts/biblical-shot.mjs --out path.png   # custom output path
 */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'
import path from 'node:path'

// ── Load .env ──────────────────────────────────────────────────────
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

// ── Parse args ─────────────────────────────────────────────────────
const args = process.argv.slice(2)
function arg(name) {
  const i = args.indexOf(`--${name}`)
  return i >= 0 ? args[i + 1] : null
}
const expandName = arg('expand')
const focusName  = arg('focus')
const view       = arg('view') || arg('tradition')  // protestant (default) | catholic | orthodox
const outPath    = arg('out') || `c:/tmp/biblical-${expandName ? 'expand-' + expandName : 'default'}.png`
const fullPage   = args.includes('--full')

// ── 1. Get magic link via Supabase admin ───────────────────────────
console.log('→ Minting magic link for', USER_EMAIL)
const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: USER_EMAIL,
  options: { redirectTo: APP_BASE + '/genealogy/biblical' },
})
if (linkErr) { console.error('generateLink failed:', linkErr); process.exit(1) }
const actionLink = linkData?.properties?.action_link
if (!actionLink) { console.error('No action_link in response'); process.exit(1) }

// Rewrite the link from supabase-hosted to our app's confirm endpoint so cookies
// get set on localhost (otherwise they'd land on the supabase domain only).
// Supabase magic-link redirects to <project>.supabase.co/auth/v1/verify?...&redirect_to=APP_BASE/...
// Playwright follows redirects, ending on APP_BASE — which DOES set the auth cookie.
console.log('  action_link:', actionLink.slice(0, 80) + '…')

// ── 2. Launch Playwright ────────────────────────────────────────────
const viewportW = parseInt(arg('width') || '2800', 10)
const viewportH = parseInt(arg('height') || '1800', 10)
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: viewportW, height: viewportH } })
const page = await context.newPage()

console.log('→ Following magic link (redirects to prod with tokens in URL hash)…')
await page.goto(actionLink, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const prodUrl = page.url()
const fragment = new URL(prodUrl).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const expiresIn = parseInt(params.get('expires_in') || '3600', 10)
if (!accessToken) { console.error('No access_token in URL fragment, got:', prodUrl); process.exit(1) }
console.log(`  got tokens (access_token ${accessToken.length} chars)`)

// Decode JWT payload for user info (no signature check — just parsing)
function decodeJwt(token) {
  const payload = token.split('.')[1]
  const padded = payload + '='.repeat((4 - payload.length % 4) % 4)
  return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8'))
}
const jwt = decodeJwt(accessToken)
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
console.log('  project ref:', projectRef, ' user:', jwt.email)

// ── 3. Inject supabase auth cookie on localhost ─────────────────────
// @nuxtjs/supabase reads `sb-<projectRef>-auth-token` cookie for SSR auth.
// Format: JSON-stringified session object, URL-encoded by browser.
const session = {
  access_token: accessToken,
  refresh_token: refreshToken,
  expires_at: jwt.exp,
  expires_in: expiresIn,
  token_type: 'bearer',
  user: {
    id: jwt.sub,
    aud: jwt.aud,
    email: jwt.email,
    phone: jwt.phone || '',
    app_metadata: jwt.app_metadata || {},
    user_metadata: jwt.user_metadata || {},
    role: jwt.role,
    aal: jwt.aal,
    amr: jwt.amr || [],
    session_id: jwt.session_id,
    is_anonymous: jwt.is_anonymous || false,
  },
}
const cookieName = `sb-${projectRef}-auth-token`
const localhostHost = new URL(APP_BASE).hostname

// @supabase/ssr cookieEncoding defaults to "base64url" → "base64-" + base64url(JSON)
function base64url(str) {
  return Buffer.from(str, 'utf-8').toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
const cookieValue = 'base64-' + base64url(JSON.stringify(session))

await context.addCookies([{
  name: cookieName,
  value: cookieValue,
  domain: localhostHost,
  path: '/',
  httpOnly: false,
  secure: false,
  sameSite: 'Lax',
}])
console.log(`→ Cookie set: ${cookieName} (${cookieValue.length} chars)`)

const viewQS = view ? `?view=${encodeURIComponent(view)}` : ''
console.log(`→ Loading /genealogy/biblical${viewQS}`)
await page.goto(APP_BASE + '/genealogy/biblical' + viewQS, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
console.log('  landed at:', page.url())
if (page.url().includes('/login')) {
  console.error('  ⚠️ Auth cookie not accepted, still redirected to /login')
  console.error('     (cookie format may not match @nuxtjs/supabase expectations)')
}

// Switch to 族譜圖 view if not already
console.log('→ Switching to tree view')
try {
  await page.click('button:has-text("族譜圖")', { timeout: 3000 })
} catch (e) {
  console.log('  (tree view button not found — already there?)')
}
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000) // let layout settle

// ── 4. Optional: expand a clan ──────────────────────────────────────
if (expandName) {
  console.log(`→ Looking for ▼ toggle near "${expandName}"`)
  // Find the card whose displayName contains expandName, then click its ▼ button
  const clicked = await page.evaluate((target) => {
    const cards = Array.from(document.querySelectorAll('.node-card'))
    for (const card of cards) {
      if (card.textContent?.includes(target)) {
        const btn = card.querySelector('button[title*="展開"]')
        if (btn) { (btn).click(); return true }
      }
    }
    return false
  }, expandName)
  console.log(clicked ? '  ▼ clicked' : `  ⚠️ no ▼ for "${expandName}"`)
  await page.waitForTimeout(1500)
}

// ── 5. Optional: pan the canvas to bring a card into view ───────────
// The chart uses CSS transform (not native scroll), so we mutate the
// transform's translate values directly via DOM.
async function panTo(target) {
  await page.evaluate((target) => {
    const vp = document.querySelector('.bg-stone-50') // viewport
    if (!vp) return
    const cards = Array.from(document.querySelectorAll('.node-card'))
    const card = cards.find(c => c.textContent?.includes(target))
    if (!card) return
    // Find the inner canvas div whose style has transform
    const canvas = vp.querySelector('div[style*="transform"]')
    if (!canvas) return
    const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/)
    if (!m) return
    const [, pxStr, pyStr, scaleStr] = m
    const scale = parseFloat(scaleStr)
    // Card position in canvas (pre-transform)
    const cardLeft = parseFloat(card.style.left)
    const cardTop = parseFloat(card.style.top)
    const cardW = parseFloat(card.style.width)
    const vpRect = vp.getBoundingClientRect()
    // Desired: card center == viewport center
    const newPanX = vpRect.width / 2 - (cardLeft + cardW / 2) * scale
    const newPanY = vpRect.height / 2 - (cardTop + 26) * scale
    canvas.style.transform = `translate(${newPanX}px, ${newPanY}px) scale(${scale})`
  }, target)
  await page.waitForTimeout(400)
}
if (focusName) {
  console.log(`→ Panning to "${focusName}"`)
  await panTo(focusName)
}
if (expandName) {
  // After expanding, also pan to it (the card is the anchor of its subtree)
  await panTo(expandName)
}

// ── 6. Screenshot ──────────────────────────────────────────────────
console.log(`→ Saving screenshot to ${outPath}`)
await page.screenshot({ path: outPath, fullPage })
console.log('✅ done')

await browser.close()
