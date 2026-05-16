/**
 * Debug: find the ghost card between 撒羅米 and 約瑟 in orthodox view.
 * Dumps every node card with its label, position, classes and personId.
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
const SERVICE = env.SUPABASE_SERVICE_ROLE_KEY
const APP_BASE = process.env.APP_BASE || 'http://localhost:3004'

const admin = createClient(SUPABASE_URL, SERVICE, { auth: { persistSession: false } })
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink', email: env.ALLOWED_EMAIL || 'redpiigpig@gmail.com',
  options: { redirectTo: APP_BASE + '/genealogy/biblical-tree?view=orthodox' },
})

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 1800, height: 1200 } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})

const url = page.url()
const hash = new URL(url).hash.replace(/^#/, '')
const params = new URLSearchParams(hash)
const at = params.get('access_token'); const rt = params.get('refresh_token') || ''
const jwt = JSON.parse(Buffer.from((at.split('.')[1] + '==').replace(/-/g,'+').replace(/_/g,'/'), 'base64').toString())
const ref = new URL(SUPABASE_URL).hostname.split('.')[0]
const session = { access_token: at, refresh_token: rt, expires_at: jwt.exp, expires_in: 3600, token_type: 'bearer',
  user: { id: jwt.sub, email: jwt.email, aud: jwt.aud, role: jwt.role, app_metadata: {}, user_metadata: {} } }
const b64 = (s) => Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await ctx.addCookies([{
  name: `sb-${ref}-auth-token`, value: 'base64-' + b64(JSON.stringify(session)),
  domain: new URL(APP_BASE).hostname, path: '/', sameSite: 'Lax', secure: false, httpOnly: false,
}])

await page.goto(APP_BASE + '/genealogy/biblical-tree?view=orthodox', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000)

// Pan to 馬利亞 area so we get them in rendered scope
await page.evaluate(() => {
  const vp = document.querySelector('.bg-stone-50')
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const target = cards.find(c => c.textContent?.includes('馬利亞'))
  if (!target || !vp) return
  const canvas = vp.querySelector('div[style*="transform"]')
  const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/)
  const scale = parseFloat(m[3])
  const cl = parseFloat(target.style.left), ct = parseFloat(target.style.top), cw = parseFloat(target.style.width)
  const rect = vp.getBoundingClientRect()
  canvas.style.transform = `translate(${rect.width/2 - (cl + cw/2)*scale}px, ${rect.height/2 - (ct + 26)*scale}px) scale(${scale})`
})
await page.waitForTimeout(500)

// Dump every visible card near the gen 63 row
const nodes = await page.evaluate(() => {
  const out = []
  const cards = Array.from(document.querySelectorAll('.node-card'))
  for (const c of cards) {
    const top = parseFloat(c.style.top || '0')
    const left = parseFloat(c.style.left || '0')
    const width = parseFloat(c.style.width || '0')
    const height = parseFloat(c.style.height || '0')
    // Try to find the text content (innerText) and the id-like attrs
    const text = (c.textContent || '').trim().replace(/\s+/g, ' ')
    const dataPid = c.getAttribute('data-pid') || c.getAttribute('data-person-id') || ''
    const cls = c.className
    out.push({ top, left, width, height, text, dataPid, cls })
  }
  // Sort by top then left
  out.sort((a, b) => a.top - b.top || a.left - b.left)
  return out
})

// Print just gen 63ish rows (top within a window) — pick range from 馬利亞's top
const maryRow = nodes.filter(n => n.text.includes('馬利亞') || n.text.includes('撒羅米') || n.text.includes('約瑟') || n.text.includes('革羅罷'))
console.log('=== marriage row candidates ===')
for (const n of maryRow) console.log(JSON.stringify(n))

// Anything at the same top as the spine wife row that is "empty"
const tops = new Set(maryRow.map(n => Math.round(n.top / 20)))
console.log('\n=== ALL cards within ±100px of 馬利亞 row ===')
const maryTop = (maryRow.find(n => n.text.includes('馬利亞')) || {}).top || 0
for (const n of nodes) {
  if (Math.abs(n.top - maryTop) < 120) {
    console.log(`top=${n.top} left=${n.left} w=${n.width} h=${n.height} | ${n.text.slice(0, 80) || '(empty)'} | cls=${n.cls.slice(0, 80)}`)
  }
}

await browser.close()
