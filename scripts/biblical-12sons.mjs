/**
 * Batch-screenshot Jacob's 12 sons' expansions.
 * Each shot pans to the son's card then expands his ▼ (if available).
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

const SONS = ['呂便', '西緬', '利未', '猶大', '但', '拿弗他利', '迦得', '亞設', '以薩迦', '西布倫', '約瑟', '便雅憫']
// Note: 利未 spine path conflicts since Levi → ... → Mary is spine B. We'll still
// open his ▼ even though his Lineage may already be partially on spine.

console.log('→ Minting magic link…')
const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: USER_EMAIL,
})
if (linkErr) { console.error(linkErr); process.exit(1) }

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 3000, height: 2000 } })
const page = await context.newPage()

await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
function decodeJwt(t) {
  const p = t.split('.')[1]
  return JSON.parse(Buffer.from(p.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - p.length % 4) % 4), 'base64').toString('utf-8'))
}
const jwt = decodeJwt(accessToken)
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken, refresh_token: refreshToken,
  expires_at: jwt.exp, expires_in: 3600, token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: '', app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {}, role: jwt.role, aal: jwt.aal, amr: jwt.amr || [], session_id: jwt.session_id, is_anonymous: false },
}
function b64url(s) { return Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '') }
const cookieValue = 'base64-' + b64url(JSON.stringify(session))
await context.addCookies([{ name: `sb-${projectRef}-auth-token`, value: cookieValue, domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax' }])

console.log('→ Loading biblical page once…')
await page.goto(APP_BASE + '/genealogy/biblical', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.click('button:has-text("族譜圖")', { timeout: 3000 }).catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(1500)

async function panTo(target) {
  await page.evaluate((target) => {
    const vp = document.querySelector('.bg-stone-50')
    if (!vp) return
    const cards = Array.from(document.querySelectorAll('.node-card'))
    const card = cards.find(c => {
      const n = c.querySelector('.text-\\[12px\\]')
      return n && (n.textContent || '').trim() === target
    })
    if (!card) return
    const canvas = vp.querySelector('div[style*="transform"]')
    if (!canvas) return
    const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/)
    if (!m) return
    const scale = parseFloat(m[3])
    const cardLeft = parseFloat(card.style.left)
    const cardTop = parseFloat(card.style.top)
    const cardW = parseFloat(card.style.width)
    const vpRect = vp.getBoundingClientRect()
    canvas.style.transform = `translate(${vpRect.width / 2 - (cardLeft + cardW / 2) * scale}px, ${vpRect.height / 2 - (cardTop + 26) * scale}px) scale(${scale})`
  }, target)
  await page.waitForTimeout(300)
}

async function expandAndShot(son, idx) {
  console.log(`[${idx+1}/12] ${son}`)
  // Reload page to ensure clean state (no leftover expansions from previous son)
  await page.goto(APP_BASE + '/genealogy/biblical', { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle').catch(() => {})
  try { await page.click('button:has-text("族譜圖")', { timeout: 2000 }) } catch {}
  await page.waitForSelector('.node-card', { timeout: 15000 })
  await page.waitForTimeout(1000)
  // First click ▼ on this son's card
  const clicked = await page.evaluate((target) => {
    // Match cards by the displayed name (1-7 char inside .text-[12px]) EXACTLY, not substring.
    const cards = Array.from(document.querySelectorAll('.node-card'))
    // Filter cards whose primary name === target
    const matches = cards.filter(c => {
      const nameEl = c.querySelector('.text-\\[12px\\]')
      if (!nameEl) return false
      const txt = (nameEl.textContent || '').trim()
      return txt === target
    })
    if (matches.length === 0) return 'no-card'
    // Prefer the one with ▼ button (i.e. has a subtree to expand)
    const expandable = matches.find(c => c.querySelector('button[title*="展開"]'))
    if (!expandable) return `no-button (${matches.length} matches but none have ▼)`
    expandable.querySelector('button[title*="展開"]').click()
    return 'ok'
  }, son)
  console.log(`   click: ${clicked}`)
  await page.waitForTimeout(800)
  await panTo(son)
  await page.waitForTimeout(400)
  const out = `c:/tmp/12sons-${idx+1}-${son}.png`
  await page.screenshot({ path: out })
  console.log(`   → ${out}`)
  // Collapse before next iteration (click ▲)
  await page.evaluate((target) => {
    const cards = Array.from(document.querySelectorAll('.node-card'))
    const card = cards.find(c => {
      const n = c.querySelector('.text-\\[12px\\]')
      return n && (n.textContent || '').trim() === target
    })
    if (!card) return
    const btn = card.querySelector('button[title*="收起"]')
    if (btn) btn.click()
  }, son)
  await page.waitForTimeout(400)
}

for (let i = 0; i < SONS.length; i++) {
  await expandAndShot(SONS[i], i)
}

await browser.close()
console.log('✅ all 12 done')
