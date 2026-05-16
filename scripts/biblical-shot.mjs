/**
 * Headless screenshot helper for the biblical genealogy page.
 *
 * Auth: uses Supabase service-role to mint a magic-link for the configured
 * user, then Playwright navigates through it so the @nuxtjs/supabase session
 * cookies are set, then drives the page.
 *
 * Usage:
 *   node scripts/biblical-shot.mjs                                # default screenshot
 *   node scripts/biblical-shot.mjs --expand 拿鶴                  # click ▼ on first card matching 拿鶴
 *   node scripts/biblical-shot.mjs --focus 他拉                   # pan to focus on first card matching 他拉
 *   node scripts/biblical-shot.mjs --focus '雅各（以撒之子）'    # exact rawName match (full name w/ disambig)
 *   node scripts/biblical-shot.mjs --focus-id <uuid>              # exact personId match — best for same-name disambig
 *   node scripts/biblical-shot.mjs --expand-id <uuid>             # click ▼ on card with this personId
 *   node scripts/biblical-shot.mjs --out path.png                 # custom output path
 *
 * Same-name people in this tree (use --focus-id / --expand-id or full name with disambig):
 *   雅各: patriarch (gen 22) / 雅各（馬但之子）(gen 62) / 雅各（主的兄弟，L64）
 *   約瑟: patriarch (gen 23) / 約瑟（馬利亞之夫，gen 63） / 約瑟（巴拿巴）等
 *   利未: tribe (gen 23) / 利未（路加 3:24，gen 71） / 利未（馬利亞-革羅罷之子）
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
const expandId   = arg('expand-id')
const focusId    = arg('focus-id')
const view       = arg('view') || arg('tradition')  // protestant (default) | catholic | orthodox
const outPath    = arg('out') || `c:/tmp/biblical-${expandName ? 'expand-' + expandName : expandId ? 'expand-id' : 'default'}.png`
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
console.log(`→ Loading /genealogy/biblical-tree${viewQS}`)
await page.goto(APP_BASE + '/genealogy/biblical-tree' + viewQS, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
console.log('  landed at:', page.url())
if (page.url().includes('/login')) {
  console.error('  ⚠️ Auth cookie not accepted, still redirected to /login')
  console.error('     (cookie format may not match @nuxtjs/supabase expectations)')
}

// Wait for tree to render (we're already on /genealogy/biblical-tree)
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000) // let layout settle

// ── Selector strategies ────────────────────────────────────────────
// Three modes (most precise → least):
//   { mode: 'id',       value: uuid }     — match data-person-id exactly
//   { mode: 'rawName',  value: '雅各（馬但之子）' } — match data-raw-name exactly
//                                          (when target contains '（')
//   { mode: 'baseName', value: '雅各' }   — match displayed text loosely
//                                          (legacy substring; first match by deepest Y)
function selector(idArg, nameArg) {
  if (idArg) return { mode: 'id', value: idArg }
  if (!nameArg) return null
  if (nameArg.includes('（')) return { mode: 'rawName', value: nameArg }
  return { mode: 'baseName', value: nameArg }
}

async function findCard(sel) {
  return await page.evaluate((sel) => {
    const cards = Array.from(document.querySelectorAll('.node-card'))
    let matches = []
    if (sel.mode === 'id') {
      matches = cards.filter(c => c.dataset.personId === sel.value)
    } else if (sel.mode === 'rawName') {
      matches = cards.filter(c => c.dataset.rawName === sel.value)
    } else {
      const base = sel.value.split('（')[0].trim()
      matches = cards.filter(c => c.textContent?.includes(base))
    }
    if (!matches.length) return null
    // Prefer deepest-Y card (legacy behavior — biases towards bottom-most match)
    matches.sort((a, b) => parseFloat(b.style.top || '0') - parseFloat(a.style.top || '0'))
    const c = matches[0]
    return {
      personId: c.dataset.personId,
      rawName: c.dataset.rawName,
      left: c.style.left,
      top: c.style.top,
      width: c.style.width,
    }
  }, sel)
}

// ── 4. Optional: expand a clan ──────────────────────────────────────
const expandSel = selector(expandId, expandName)
if (expandSel) {
  const tag = expandSel.mode === 'id' ? `id=${expandSel.value}` : expandSel.value
  console.log(`→ Looking for ▼ toggle near "${tag}" (${expandSel.mode})`)
  const clicked = await page.evaluate((sel) => {
    const cards = Array.from(document.querySelectorAll('.node-card'))
    for (const card of cards) {
      let ok = false
      if (sel.mode === 'id') ok = card.dataset.personId === sel.value
      else if (sel.mode === 'rawName') ok = card.dataset.rawName === sel.value
      else ok = !!card.textContent?.includes(sel.value)
      if (!ok) continue
      const btn = card.querySelector('button[title*="展開"]')
      if (btn) { btn.click(); return card.dataset.rawName || true }
    }
    return false
  }, expandSel)
  console.log(clicked ? `  ▼ clicked on "${clicked}"` : `  ⚠️ no ▼ for "${tag}"`)
  await page.waitForTimeout(1500)
}

// ── 5. Optional: pan the canvas to bring a card into view ───────────
async function panTo(sel) {
  const card = await findCard(sel)
  if (!card) {
    console.log(`  ⚠️ no card matched ${sel.mode}=${sel.value}`)
    return
  }
  console.log(`  → matched ${card.rawName} (id ${(card.personId || '').slice(0,8)}…)`)
  await page.evaluate((c) => {
    const vp = document.querySelector('.bg-stone-50')
    if (!vp) return
    const canvas = vp.querySelector('div[style*="transform"]')
    if (!canvas) return
    const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/)
    if (!m) return
    const scale = parseFloat(m[3])
    const cardLeft = parseFloat(c.left)
    const cardTop = parseFloat(c.top)
    const cardW = parseFloat(c.width)
    const vpRect = vp.getBoundingClientRect()
    const newPanX = vpRect.width / 2 - (cardLeft + cardW / 2) * scale
    const newPanY = vpRect.height / 2 - (cardTop + 26) * scale
    canvas.style.transform = `translate(${newPanX}px, ${newPanY}px) scale(${scale})`
  }, card)
  await page.waitForTimeout(400)
}
const focusSel = selector(focusId, focusName)
if (focusSel) {
  const tag = focusSel.mode === 'id' ? `id=${focusSel.value}` : focusSel.value
  console.log(`→ Panning to "${tag}" (${focusSel.mode})`)
  await panTo(focusSel)
} else if (expandSel) {
  // Fallback: after expanding, pan to that same target
  await panTo(expandSel)
}

// ── 6. Screenshot ──────────────────────────────────────────────────
console.log(`→ Saving screenshot to ${outPath}`)
await page.screenshot({ path: outPath, fullPage })
console.log('✅ done')

await browser.close()
