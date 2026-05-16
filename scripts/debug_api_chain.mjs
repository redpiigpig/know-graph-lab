/** Direct hit API → see if Anna chain people are in the nodes payload. */
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

const NEEDLES = ['斯多蘭', '蘇比', '以利沙白', '撒迦利亞', '施洗約翰', '利未（路加 3:24）', '瑪塔', '約亞敬', '亞拿（聖母']

// Make sure we're on the page (so the cookie attaches)
await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})

for (const view of ['protestant', 'early_consensus', 'orthodox', 'catholic']) {
  const resp = await page.request.get(`${APP_BASE}/api/genealogy/biblical-graph?view=${view}`, {
    headers: { Authorization: `Bearer ${at}` }
  })
  const data = { parsed: null }
  try { data.parsed = await resp.json() } catch (e) { data.raw = await resp.text() }
  if (!data.parsed) { console.log(`=== ${view} FAILED status=${resp.status()} ===`, (data.raw||'').slice(0, 400)); continue }
  const d = data.parsed
  console.log(`\n=== ${view} keys: ${Object.keys(d).join(',')} ===`)
  if (!d.nodes) { console.log('  no nodes! body:', JSON.stringify(d).slice(0, 400)); continue }
  const matched = d.nodes.filter(n => NEEDLES.some(needle => n.data.name.includes(needle)))
  console.log(`\n=== ${view} (${d.nodes.length} nodes, ${d.edges.length} edges) ===`)
  for (const n of matched) {
    console.log(`  [gen=${n.data.generationNum}] [${n.data.tradition}] ${n.data.name}`)
  }
}
await browser.close()
