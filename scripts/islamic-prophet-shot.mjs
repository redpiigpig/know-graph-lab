/** Screenshot Islamic tree after clicking "先知鏈" auto-expand button + pan to target. */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}
const APP_BASE = process.env.APP_BASE || 'http://localhost:3006'

const args = process.argv.slice(2)
function arg(n) { const i = args.indexOf('--' + n); return i >= 0 ? args[i+1] : null }
const focusName = arg('focus') || '達烏德'
const zoomArg = arg('zoom') ? parseFloat(arg('zoom')) : 0.7
const outPath = arg('out') || `c:/tmp/islamic-prophet-${focusName}.png`
const view = arg('view') || 'sunni'
const w = parseInt(arg('width') || '2400', 10)
const h = parseInt(arg('height') || '1400', 10)

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: 'redpiigpig@gmail.com',
  options: { redirectTo: APP_BASE + '/genealogy/islamic-tree' },
})

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: w, height: h } })
const page = await context.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded', timeout: 90000 })
await page.waitForLoadState('networkidle').catch(() => {})

function decodeJwt(t) {
  const p = t.split('.')[1]
  return JSON.parse(Buffer.from((p + '==='.slice((p.length + 3) % 4)).replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString())
}
const params = new URLSearchParams(new URL(page.url()).hash.replace(/^#/, ''))
const at = params.get('access_token'), rt = params.get('refresh_token') || ''
const jwt = decodeJwt(at)
const projectRef = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: at, refresh_token: rt, expires_at: jwt.exp, expires_in: 3600, token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, role: jwt.role, aal: jwt.aal,
    app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {} },
}
function b64url(s) { return Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'') }
await context.addCookies([{
  name: `sb-${projectRef}-auth-token`,
  value: 'base64-' + b64url(JSON.stringify(session)),
  domain: 'localhost', path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])

await page.goto(`${APP_BASE}/genealogy/islamic-tree?view=${view}`, { waitUntil: 'domcontentloaded', timeout: 90000 })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000)

// Click "先知鏈" button
const btn = page.locator('button[title*="先知鏈"]')
const cnt = await btn.count()
console.log(`  found 先知鏈 button: ${cnt}`)
if (cnt > 0) {
  await btn.first().click()
  console.log('  clicked 先知鏈')
  await page.waitForTimeout(1500)
}

const cardCount = await page.locator('.node-card').count()
console.log(`  rendered ${cardCount} cards after expand`)

// Pan to target
await page.evaluate(({ target, scale }) => {
  const vp = document.querySelector('.bg-stone-50')
  if (!vp) return
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const base = target.split('（')[0].trim()
  const matches = cards.filter(c => c.textContent?.includes(base))
  if (!matches.length) { console.log('no match for', target); return }
  matches.sort((a, b) => parseFloat(b.style.top || '0') - parseFloat(a.style.top || '0'))
  const card = matches[0]
  const canvas = vp.querySelector('div[style*="transform"]')
  if (!canvas) return
  const cardLeft = parseFloat(card.style.left)
  const cardTop = parseFloat(card.style.top)
  const cardW = parseFloat(card.style.width)
  const vpRect = vp.getBoundingClientRect()
  const newPanX = vpRect.width / 2 - (cardLeft + cardW / 2) * scale
  const newPanY = vpRect.height / 2 - (cardTop + 26) * scale
  canvas.style.transform = `translate(${newPanX}px, ${newPanY}px) scale(${scale})`
}, { target: focusName, scale: zoomArg })
await page.waitForTimeout(500)

await page.screenshot({ path: outPath })
console.log(`✅ saved ${outPath}`)
await browser.close()
