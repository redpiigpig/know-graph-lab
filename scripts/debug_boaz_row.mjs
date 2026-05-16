/** Dump every card near J30 / 波阿斯 row. */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}
const SBURL = env.SUPABASE_URL, SRK = env.SUPABASE_SERVICE_ROLE_KEY
const APP = process.env.APP_BASE || 'http://localhost:3004'

const admin = createClient(SBURL, SRK, { auth: { persistSession: false } })
const { data: ld } = await admin.auth.admin.generateLink({ type: 'magiclink', email: env.ALLOWED_EMAIL || 'redpiigpig@gmail.com', options: { redirectTo: APP + '/genealogy/biblical-tree' } })

const b = await chromium.launch({ headless: true })
const ctx = await b.newContext({ viewport: { width: 1800, height: 1200 } })
const p = await ctx.newPage()
await p.goto(ld.properties.action_link, { waitUntil: 'domcontentloaded' })
await p.waitForLoadState('networkidle').catch(() => {})
const u = p.url(); const hash = new URL(u).hash.replace(/^#/, '')
const at = new URLSearchParams(hash).get('access_token')
const rt = new URLSearchParams(hash).get('refresh_token') || ''
const jwt = JSON.parse(Buffer.from((at.split('.')[1] + '==').replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString())
const ref = new URL(SBURL).hostname.split('.')[0]
const session = { access_token: at, refresh_token: rt, expires_at: jwt.exp, expires_in: 3600, token_type: 'bearer', user: { id: jwt.sub, email: jwt.email, aud: jwt.aud, role: jwt.role, app_metadata: {}, user_metadata: {} } }
const b64 = s => Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
await ctx.addCookies([{ name: `sb-${ref}-auth-token`, value: 'base64-' + b64(JSON.stringify(session)), domain: new URL(APP).hostname, path: '/', sameSite: 'Lax', secure: false, httpOnly: false }])

await p.goto(APP + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await p.waitForLoadState('networkidle').catch(() => {})
await p.waitForSelector('.node-card', { timeout: 15000 })
await p.waitForTimeout(2000)

// Get 波阿斯 + 以利米勒 area
const data = await p.evaluate(() => {
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const boaz = cards.find(c => c.textContent?.includes('波阿斯'))
  const eli = cards.find(c => c.textContent?.includes('以利米勒'))
  if (!boaz || !eli) return { error: 'missing card' }
  const boazTop = parseFloat(boaz.style.top || '0')
  const eliTop = parseFloat(eli.style.top || '0')
  const range = cards.filter(c => {
    const t = parseFloat(c.style.top || '0')
    return t >= eliTop - 5 && t <= boazTop + 5
  })
  range.sort((a, b) => parseFloat(a.style.top) - parseFloat(b.style.top) || parseFloat(a.style.left) - parseFloat(b.style.left))
  return {
    rows: range.map(c => ({
      text: (c.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 40),
      top: parseFloat(c.style.top),
      left: parseFloat(c.style.left),
      width: parseFloat(c.style.width),
    }))
  }
})

console.log(JSON.stringify(data, null, 2))
await b.close()
