/**
 * Debug: dump every card containing 斯多蘭/蘇比/以利沙白/撒迦利亞/施洗約翰
 * to see if they render at all (and where) in protestant + orthodox view.
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
  options: { redirectTo: APP_BASE + '/genealogy/biblical-tree' },
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

const NEEDLES = ['斯多蘭', '蘇比', '以利沙白', '撒迦利亞', '施洗約翰']

async function probe(view) {
  await page.goto(APP_BASE + `/genealogy/biblical-tree?view=${view}`, { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle').catch(() => {})
  await page.waitForSelector('.node-card', { timeout: 15000 })
  await page.waitForTimeout(2000)

  const all = await page.evaluate((needles) => {
    const out = []
    const cards = Array.from(document.querySelectorAll('.node-card'))
    for (const c of cards) {
      const txt = (c.textContent || '').trim().replace(/\s+/g, ' ')
      if (needles.some(n => txt.includes(n))) {
        out.push({
          text: txt.slice(0, 80),
          top: parseFloat(c.style.top || '0'),
          left: parseFloat(c.style.left || '0'),
          width: parseFloat(c.style.width || '0'),
          display: c.style.display || '(default)',
          visibility: c.style.visibility || '(default)',
          opacity: c.style.opacity || '(default)',
          classes: c.className.slice(0, 100),
        })
      }
    }
    return out
  }, NEEDLES)

  console.log(`\n=== ${view} (total cards matching: ${all.length}) ===`)
  for (const r of all) {
    console.log(`  top=${r.top.toFixed(0)} left=${r.left.toFixed(0)} disp=${r.display} vis=${r.visibility} op=${r.opacity}`)
    console.log(`    text: ${r.text}`)
  }
}

await probe('protestant')
await probe('early_consensus')
await probe('orthodox')
await probe('catholic')

await browser.close()
