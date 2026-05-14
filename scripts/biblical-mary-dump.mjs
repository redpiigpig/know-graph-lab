/**
 * Dump every card with "馬利亞" in its text for early_consensus view,
 * with position + parent dataset attributes to identify the duplicate.
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
const APP_BASE = process.env.APP_BASE || 'http://localhost:3002'
const VIEW = process.env.VIEW || 'early_consensus'

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, { auth: { autoRefreshToken: false, persistSession: false } })
const { data } = await admin.auth.admin.generateLink({ type: 'magiclink', email: env.ALLOWED_EMAIL || 'redpiigpig@gmail.com', options: { redirectTo: APP_BASE + '/genealogy/biblical' } })
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 2800, height: 1800 } })
const page = await context.newPage()
await page.goto(data.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
function decodeJwt(t) { const p = t.split('.')[1]; return JSON.parse(Buffer.from(p + '==='.slice(p.length % 4), 'base64').toString()) }
const jwt = decodeJwt(accessToken)
const projectRef = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const session = { access_token: accessToken, refresh_token: params.get('refresh_token') || '', expires_at: jwt.exp, expires_in: parseInt(params.get('expires_in') || '3600'), token_type: 'bearer', user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: '', app_metadata: jwt.app_metadata||{}, user_metadata: jwt.user_metadata||{}, role: jwt.role, aal: jwt.aal, amr: jwt.amr||[], session_id: jwt.session_id, is_anonymous: false } }
function b64url(s) { return Buffer.from(s).toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'') }
await context.addCookies([{ name: `sb-${projectRef}-auth-token`, value: 'base64-' + b64url(JSON.stringify(session)), domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax' }])

await page.goto(`${APP_BASE}/genealogy/biblical-tree?view=${VIEW}`, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000)

const dump = await page.evaluate(() => {
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const TARGETS = ['拿鶴', '烏斯', '瑪迦', '彼土利', '布斯', '戶斯', '基母利', '基薛', '哈瑣', '必達', '益拉', '他拉', '亞伯拉罕', '哈蘭']
  const matched = cards.filter(c => {
    const t = c.querySelector('[title]')?.getAttribute('title') || c.textContent || ''
    return TARGETS.some(n => t.includes(n))
  })
  return matched.map(c => ({
    title: c.querySelector('[title]')?.getAttribute('title') || '',
    text: c.textContent?.replace(/\s+/g, ' ').trim().slice(0, 80),
    top: parseFloat(c.style.top),
    left: parseFloat(c.style.left),
    width: parseFloat(c.style.width),
    classes: c.className,
    dataAttrs: Object.fromEntries(Array.from(c.attributes).filter(a => a.name.startsWith('data-')).map(a => [a.name, a.value])),
    innerHTML: c.innerHTML.replace(/<!--.+?-->/g, '').replace(/\s+/g, ' ').slice(0, 600),
    id: c.id || c.getAttribute('id'),
  }))
})

console.log(`View: ${VIEW} — found ${dump.length} cards near Joseph/Mary area:\n`)
// sort by top, then left, to read row-by-row
dump.sort((a, b) => (a.top - b.top) || (a.left - b.left))
let prevTop = null
for (const c of dump) {
  if (prevTop !== null && Math.abs(c.top - prevTop) > 10) console.log('')
  prevTop = c.top
  const spineMark = c.classes.includes('bg-amber-50') ? '[A]' : c.classes.includes('bg-rose-50/90') ? '[F]' : c.classes.includes('bg-white') ? '[S]' : '[?]'
  console.log(`  top=${c.top}  left=${c.left}  ${spineMark}  title="${c.title}"  text="${c.text}"`)
}

await browser.close()
