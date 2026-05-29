import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const l of fs.readFileSync('c:/Users/user/Desktop/know-graph-lab/.env','utf-8').split('\n')) {
  if (!l.includes('=') || l.trim().startsWith('#')) continue
  const [k, ...r] = l.split('=')
  env[k.trim()] = r.join('=').trim().replace(/^["']|["']$/g,'')
}

const args = process.argv.slice(2)
function flag(name, fallback) {
  const i = args.indexOf(`--${name}`)
  return i >= 0 ? args[i+1] : fallback
}
const PORT = flag('port', '3000')
const PATH = flag('path', '/creeds')
const OUT = flag('out', 'c:/tmp/creeds-shot.png')

const APP_BASE = `http://localhost:${PORT}`
const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})

const target = `${APP_BASE}${PATH}`
const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: 'redpiigpig@gmail.com',
  options: { redirectTo: target },
})
if (linkErr) { console.error('magic link failed:', linkErr); process.exit(1) }

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1800 } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})

const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const at = params.get('access_token')
const rt = params.get('refresh_token') || ''
if (!at) { console.error('no access_token'); await browser.close(); process.exit(1) }
function dj(t){const p=t.split('.')[1];const pad=p+'='.repeat((4-p.length%4)%4);return JSON.parse(Buffer.from(pad.replace(/-/g,'+').replace(/_/g,'/'),'base64').toString('utf-8'))}
const j = dj(at)
const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = {
  access_token: at, refresh_token: rt, expires_at: j.exp, expires_in: 3600,
  token_type: 'bearer',
  user: { id: j.sub, aud: j.aud, email: j.email, phone: '',
    app_metadata: j.app_metadata||{}, user_metadata: j.user_metadata||{},
    role: j.role, aal: j.aal, amr: j.amr||[], session_id: j.session_id,
    is_anonymous: false },
}
const b64u = (s) => Buffer.from(s,'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await ctx.addCookies([{
  name: `sb-${ref}-auth-token`,
  value: 'base64-'+b64u(JSON.stringify(sess)),
  domain: 'localhost', path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])

await page.goto(target, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})
await page.waitForTimeout(1500)
await page.screenshot({ path: OUT, fullPage: true })
console.log(`→ ${OUT}`)
await browser.close()
