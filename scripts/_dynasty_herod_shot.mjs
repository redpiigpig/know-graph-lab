import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'
const env = {}; for (const l of fs.readFileSync('.env','utf-8').split('\n')) { if (!l.includes('=')||l.trim().startsWith('#')) continue; const [k,...r]=l.split('='); env[k.trim()]=r.join('=').trim().replace(/^["']|["']$/g,'') }
const APP_BASE = 'http://localhost:3001'
const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, { auth: { autoRefreshToken: false, persistSession: false } })
const { data: linkData } = await admin.auth.admin.generateLink({ type: 'magiclink', email: 'redpiigpig@gmail.com', options: { redirectTo: APP_BASE + '/genealogy/biblical' } })
const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 3200, height: 2200 } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const at = params.get('access_token'); const rt = params.get('refresh_token') || ''
function dj(t){const p=t.split('.')[1];const pad=p+'='.repeat((4-p.length%4)%4);return JSON.parse(Buffer.from(pad.replace(/-/g,'+').replace(/_/g,'/'),'base64').toString('utf-8'))}
const j = dj(at); const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = { access_token:at, refresh_token:rt, expires_at:j.exp, expires_in:3600, token_type:'bearer', user:{id:j.sub,aud:j.aud,email:j.email,phone:'',app_metadata:j.app_metadata||{},user_metadata:j.user_metadata||{},role:j.role,aal:j.aal,amr:j.amr||[],session_id:j.session_id,is_anonymous:false}}
const b64u = (s) => Buffer.from(s,'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await ctx.addCookies([{ name:`sb-${ref}-auth-token`, value:'base64-'+b64u(JSON.stringify(sess)), domain:new URL(APP_BASE).hostname, path:'/', httpOnly:false, secure:false, sameSite:'Lax' }])
await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(1500)
await page.evaluate(() => { const btn = Array.from(document.querySelectorAll('button')).find(b => (b.textContent||'').includes('展開朝代')); btn?.click() })
await page.waitForTimeout(2500)
// Pan to 大希律
const HEROD = 'eebb3fe4-048d-436d-9bfd-c8846d246e0a'
const ok = await page.evaluate((id) => {
  const vp = document.querySelector('.bg-stone-50'); if (!vp) return false
  const card = Array.from(document.querySelectorAll('.node-card')).find(c => c.dataset.personId === id)
  if (!card) return false
  const canvas = vp.querySelector('div[style*="transform"]'); if (!canvas) return false
  const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/); if (!m) return false
  const scale = parseFloat(m[3]); const vpRect = vp.getBoundingClientRect()
  const cl = parseFloat(card.style.left); const ct = parseFloat(card.style.top); const cw = parseFloat(card.style.width)
  canvas.style.transform = `translate(${vpRect.width/2 - (cl+cw/2)*scale}px, ${vpRect.height/2 - (ct+26)*scale}px) scale(${scale})`
  return true
}, HEROD)
console.log('pan to Herod:', ok)
await page.waitForTimeout(500)
await page.screenshot({ path: 'c:/tmp/dynasty-esau-herod.png' })
console.log('→ c:/tmp/dynasty-esau-herod.png')
await browser.close()
