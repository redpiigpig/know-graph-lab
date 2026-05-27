// Zoom on a specific element / scroll position to verify footnote+page markers.
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const l of fs.readFileSync('.env','utf-8').split('\n')) {
  if (!l.includes('=') || l.trim().startsWith('#')) continue
  const [k, ...r] = l.split('='); env[k.trim()] = r.join('=').trim().replace(/^["']|["']$/g,'')
}
const args = process.argv.slice(2)
function flag(name, fb) { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i+1] : fb }
const APP_BASE = 'http://localhost:3000'
const EBOOK_ID = flag('ebook', 'c98d358d-7066-4691-a896-b7232707b0db')
const PAGE = flag('page', '9')
const OUT = flag('out', `c:/tmp/ebook-zoom-p${PAGE}.png`)
const VIEW = flag('view', 'bi')
const SCROLL = parseInt(flag('scroll', '0'), 10)
const SEL = flag('selector', null)

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, { auth: { autoRefreshToken: false, persistSession: false } })
const target = `${APP_BASE}/ebook/${EBOOK_ID}?page=${PAGE}`
const { data: linkData } = await admin.auth.admin.generateLink({ type: 'magiclink', email: 'redpiigpig@gmail.com', options: { redirectTo: target } })
const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1000 } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})
const at = new URLSearchParams(new URL(page.url()).hash.replace(/^#/, '')).get('access_token')
const rt = new URLSearchParams(new URL(page.url()).hash.replace(/^#/, '')).get('refresh_token') || ''
function dj(t){const p=t.split('.')[1];const pad=p+'='.repeat((4-p.length%4)%4);return JSON.parse(Buffer.from(pad.replace(/-/g,'+').replace(/_/g,'/'),'base64').toString('utf-8'))}
const j = dj(at)
const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = { access_token:at, refresh_token:rt, expires_at:j.exp, expires_in:3600, token_type:'bearer', user:{id:j.sub,aud:j.aud,email:j.email,phone:'',app_metadata:j.app_metadata||{},user_metadata:j.user_metadata||{},role:j.role,aal:j.aal,amr:j.amr||[],session_id:j.session_id,is_anonymous:false}}
const b64u = (s) => Buffer.from(s,'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await ctx.addCookies([{ name:`sb-${ref}-auth-token`, value:'base64-'+b64u(JSON.stringify(sess)), domain:new URL(APP_BASE).hostname, path:'/', httpOnly:false, secure:false, sameSite:'Lax' }])
await page.addInitScript((v) => { localStorage.setItem('ebook-viewMode', v) }, VIEW)
await page.goto(target, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})
await page.waitForSelector('article', { timeout: 15000 })
await page.waitForTimeout(1500)
if (SEL) {
  const el = await page.$(SEL)
  if (el) { await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(400); await el.screenshot({ path: OUT }); console.log(`→ ${OUT} (element ${SEL})`); await browser.close(); process.exit(0) }
}
if (SCROLL) await page.evaluate((y) => { const sc = document.querySelector('.flex-1.overflow-y-auto'); sc?.scrollTo({ top: y }); window.scrollTo(0, y) }, SCROLL)
await page.waitForTimeout(400)
await page.screenshot({ path: OUT, fullPage: false })
console.log(`→ ${OUT}`)
await browser.close()
