/** Click 🏛️ 展開朝代 button then screenshot Maccabees + Exilarch area. */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}
const SBURL = env.SUPABASE_URL
const SRK = env.SUPABASE_SERVICE_ROLE_KEY
const APP = process.env.APP_BASE || 'http://localhost:3004'
const target = process.argv[2] || '猶大·瑪加伯'
const outPath = process.argv[3] || `c:/tmp/biblical_verify/dynasties-${target}.png`

const admin = createClient(SBURL, SRK, { auth: { persistSession: false } })
const { data: ld } = await admin.auth.admin.generateLink({ type: 'magiclink', email: env.ALLOWED_EMAIL || 'redpiigpig@gmail.com', options: { redirectTo: APP + '/genealogy/biblical-tree' } })

const b = await chromium.launch({ headless: true })
const ctx = await b.newContext({ viewport: { width: 1800, height: 1200 } })
const p = await ctx.newPage()
await p.goto(ld.properties.action_link, { waitUntil: 'domcontentloaded' })
await p.waitForLoadState('networkidle').catch(() => {})
const u = p.url(); const hash = new globalThis.URL(u).hash.replace(/^#/, '')
const at = new URLSearchParams(hash).get('access_token')
const rt = new URLSearchParams(hash).get('refresh_token') || ''
const jwt = JSON.parse(Buffer.from((at.split('.')[1] + '==').replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString())
const ref = new globalThis.URL(SBURL).hostname.split('.')[0]
const session = { access_token: at, refresh_token: rt, expires_at: jwt.exp, expires_in: 3600, token_type: 'bearer', user: { id: jwt.sub, email: jwt.email, aud: jwt.aud, role: jwt.role, app_metadata: {}, user_metadata: {} } }
const b64 = s => Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
await ctx.addCookies([{ name: `sb-${ref}-auth-token`, value: 'base64-' + b64(JSON.stringify(session)), domain: new globalThis.URL(APP).hostname, path: '/', sameSite: 'Lax', secure: false, httpOnly: false }])

await p.goto(APP + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await p.waitForLoadState('networkidle').catch(() => {})
await p.waitForSelector('.node-card', { timeout: 15000 })
await p.waitForTimeout(2000)

console.log('→ Clicking 🏛️ 展開朝代')
await p.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  const dynBtn = btns.find(b => b.textContent?.includes('展開') && b.textContent?.includes('朝代'))
  if (dynBtn) (dynBtn).click()
})
await p.waitForTimeout(2000)

console.log(`→ Panning to "${target}"`)
await p.evaluate((tgt) => {
  const vp = document.querySelector('.bg-stone-50')
  if (!vp) return
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const base = tgt.split('（')[0].trim()
  const matches = cards.filter(c => c.textContent?.includes(base))
  if (!matches.length) return
  matches.sort((a, b) => parseFloat(b.style.top || '0') - parseFloat(a.style.top || '0'))
  const card = matches[0]
  const canvas = vp.querySelector('div[style*="transform"]')
  const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/)
  const scale = parseFloat(m[3])
  const cardLeft = parseFloat(card.style.left)
  const cardTop = parseFloat(card.style.top)
  const cardW = parseFloat(card.style.width)
  const vpRect = vp.getBoundingClientRect()
  const newPanX = vpRect.width / 2 - (cardLeft + cardW / 2) * scale
  const newPanY = vpRect.height / 2 - (cardTop + 26) * scale
  canvas.style.transform = `translate(${newPanX}px, ${newPanY}px) scale(${scale})`
}, target)
await p.waitForTimeout(500)

await p.screenshot({ path: outPath })
console.log('✅ saved', outPath)
await b.close()
