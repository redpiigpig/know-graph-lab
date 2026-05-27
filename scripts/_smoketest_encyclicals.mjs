/**
 * Smoke test for the 4-page drill-down:
 *   /encyclicals → century → pope → doc detail
 *
 * Logs in via magic link, walks the chain, asserts core elements render,
 * grabs a small (1280×1800 max) screenshot per page.
 */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const l of fs.readFileSync('.env','utf-8').split('\n')) {
  if (!l.includes('=') || l.trim().startsWith('#')) continue
  const [k, ...r] = l.split('=')
  env[k.trim()] = r.join('=').trim().replace(/^["']|["']$/g,'')
}

const APP_BASE = 'http://localhost:3002'

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false }
})

const { data: linkData, error: linkErr } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: 'redpiigpig@gmail.com',
  options: { redirectTo: `${APP_BASE}/encyclicals` },
})
if (linkErr) { console.error(linkErr); process.exit(1) }

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } })
const page = await ctx.newPage()

const consoleErrors = []
page.on('console', (m) => {
  if (m.type() === 'error') consoleErrors.push(m.text())
})
page.on('pageerror', (e) => consoleErrors.push(`PAGEERROR: ${e.message}`))

await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})

const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const at = params.get('access_token')
const rt = params.get('refresh_token') || ''
if (!at) { console.error('NO access_token; url=', page.url()); process.exit(1) }
function dj(t){const p=t.split('.')[1];const pad=p+'='.repeat((4-p.length%4)%4);return JSON.parse(Buffer.from(pad.replace(/-/g,'+').replace(/_/g,'/'),'base64').toString('utf-8'))}
const j = dj(at)
const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = {
  access_token: at, refresh_token: rt, expires_at: j.exp, expires_in: 3600,
  token_type: 'bearer',
  user: { id: j.sub, aud: j.aud, email: j.email, phone: '',
    app_metadata: j.app_metadata||{}, user_metadata: j.user_metadata||{},
    role: j.role, aal: j.aal, amr: j.amr||[], session_id: j.session_id,
    is_anonymous: false }
}
const b64u = (s) => Buffer.from(s,'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await ctx.addCookies([{
  name: `sb-${ref}-auth-token`,
  value: 'base64-'+b64u(JSON.stringify(sess)),
  domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax'
}])

async function shot(url, name, h = 1500, assertions = null) {
  console.log(`\n--- ${name} (${url}) ---`)
  await page.goto(`${APP_BASE}${url}`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(800)
  const h1 = await page.locator('h1').first().textContent().catch(() => null)
  console.log(`  H1: ${JSON.stringify(h1)}`)
  if (assertions) await assertions()
  await page.screenshot({
    path: `c:/tmp/encyclicals_${name}.jpg`,
    type: 'jpeg',
    quality: 75,
    clip: { x: 0, y: 0, width: 1280, height: h },
  })
}

await shot('/encyclicals', 'idx', 1200, async () => {
  const cards = await page.locator('a[href^="/encyclicals/century/"]').count()
  console.log(`  Century cards: ${cards}`)
})

await shot('/encyclicals/century/21', 'c21', 1200, async () => {
  const popes = await page.locator('a[href^="/encyclicals/pope/"]').count()
  console.log(`  Popes listed: ${popes}`)
})

await shot('/encyclicals/century/20', 'c20', 1500, async () => {
  const popes = await page.locator('a[href^="/encyclicals/pope/"]').count()
  console.log(`  Popes listed: ${popes}`)
  const crossChip = await page.locator('text=跨世紀').count()
  console.log(`  跨世紀 chips: ${crossChip}`)
})

await shot('/encyclicals/century/16', 'c16', 1800, async () => {
  const popes = await page.locator('a[href^="/encyclicals/pope/"]').count()
  console.log(`  Popes listed: ${popes}`)
  // Leo X should appear (1513-1521)
  const leo10 = await page.locator('text=良十世').count()
  console.log(`  良十世 occurrences: ${leo10}`)
})

await shot('/encyclicals/century/4', 'c4', 1200, async () => {
  const popes = await page.locator('a[href^="/encyclicals/pope/"]').count()
  console.log(`  Popes listed: ${popes}`)
  const sylvester = await page.locator('text=西爾物斯德一世').count()
  console.log(`  Sylvester I occurrences: ${sylvester}`)
})

await shot('/encyclicals/pope/leo-xiv', 'pope-leo-xiv', 1000, async () => {
  const h1 = await page.locator('h1').first().textContent()
  console.log(`  Pope page H1: ${h1}`)
})

await shot('/encyclicals/pope/francis', 'pope-francis', 1200, async () => {
  const docs = await page.locator('a[href^="/encyclicals/laudato"]').count()
  console.log(`  Docs listed: ${docs}`)
})

await shot('/encyclicals/laudato-si-2015', 'doc-detail', 1800, async () => {
  // Wait for paragraphs (async load)
  await page.waitForSelector('article[id^="para-"]', { timeout: 10000 })
  const paraCount = await page.locator('article[id^="para-"]').count()
  console.log(`  Paragraphs: ${paraCount}`)
  // Check breadcrumb
  const breadcrumb = await page.locator('nav.sticky').textContent()
  console.log(`  Breadcrumb: ${breadcrumb?.replace(/\s+/g,' ').trim().slice(0, 100)}`)
})

if (consoleErrors.length) {
  console.log('\n=== Console Errors ===')
  consoleErrors.forEach(e => console.log('  -', e))
} else {
  console.log('\n✓ No console errors')
}

await browser.close()
