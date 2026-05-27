/**
 * Batch-screenshot Jacob's 12 sons' expansions using personId — resilient to same-name ambiguity.
 * Replaces the legacy biblical-12sons.mjs whose substring matching hit NT 同名 cards (e.g. 西緬 J42 Luke 3:30).
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
const APP_BASE = process.env.APP_BASE || 'http://localhost:3001'

const SONS = [
  { name: '呂便',     id: '0c718aed-c683-4301-b868-6ab634355f49' },
  { name: '西緬',     id: '7d77894d-f939-45c7-9403-6e6dee7b471a' },
  { name: '利未',     id: '2f93d1cc-0bc9-4e69-81bd-be786d0d1469' },  // on spine — no ▼
  { name: '猶大',     id: '3f5dff0a-b537-48e7-a56a-af43a34db208' },  // on spine — no ▼
  { name: '但',       id: '5e577b3b-f999-48e5-a488-6cf45339a1ff' },
  { name: '拿弗他利', id: '0e93abe6-ec03-4816-a9e7-819a2e820233' },
  { name: '迦得',     id: 'f667b864-2cb3-44cf-9cd9-9073f3ebf7a5' },
  { name: '亞設',     id: '7d319f29-5744-46b0-b167-2e13bb0b1322' },
  { name: '以薩迦',   id: 'd1b87af9-bfb9-41cd-bb2e-8ae54f424b75' },
  { name: '西布倫',   id: '4c057b42-8d9a-4366-9bc5-15976231b2b8' },
  { name: '約瑟',     id: '84c7feaa-543d-4bbd-b9c5-1da86f0c7370' },
  { name: '便雅憫',   id: 'f58d55d0-7c1f-4d72-ada4-f2cbdb97d853' },
]

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, { auth: { autoRefreshToken: false, persistSession: false } })
const { data: linkData } = await admin.auth.admin.generateLink({ type: 'magiclink', email: 'redpiigpig@gmail.com', options: { redirectTo: APP_BASE + '/genealogy/biblical' } })
const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({ viewport: { width: 3000, height: 2000 } })
const page = await ctx.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const at = params.get('access_token'); const rt = params.get('refresh_token') || ''
function dj(t){const p=t.split('.')[1];const pad=p+'='.repeat((4-p.length%4)%4);return JSON.parse(Buffer.from(pad.replace(/-/g,'+').replace(/_/g,'/'),'base64').toString('utf-8'))}
const j = dj(at)
const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = { access_token:at, refresh_token:rt, expires_at:j.exp, expires_in:3600, token_type:'bearer', user:{id:j.sub,aud:j.aud,email:j.email,phone:'',app_metadata:j.app_metadata||{},user_metadata:j.user_metadata||{},role:j.role,aal:j.aal,amr:j.amr||[],session_id:j.session_id,is_anonymous:false}}
const b64u = (s) => Buffer.from(s,'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await ctx.addCookies([{ name:`sb-${ref}-auth-token`, value:'base64-'+b64u(JSON.stringify(sess)), domain:new URL(APP_BASE).hostname, path:'/', httpOnly:false, secure:false, sameSite:'Lax' }])

async function shotSon(son, idx) {
  console.log(`[${idx+1}/12] ${son.name} (id ${son.id.slice(0,8)}…)`)
  await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle').catch(()=>{})
  await page.waitForSelector('.node-card', { timeout: 15000 })
  await page.waitForTimeout(1000)
  const result = await page.evaluate((id) => {
    const cards = Array.from(document.querySelectorAll('.node-card'))
    const card = cards.find(c => c.dataset.personId === id)
    if (!card) return 'no-card'
    const btn = card.querySelector('button[title*="展開"]')
    if (!btn) return 'no-button'
    btn.click()
    return 'clicked'
  }, son.id)
  console.log(`   ${result}`)
  await page.waitForTimeout(800)
  // Pan to son
  await page.evaluate((id) => {
    const vp = document.querySelector('.bg-stone-50'); if (!vp) return
    const card = Array.from(document.querySelectorAll('.node-card')).find(c => c.dataset.personId === id)
    if (!card) return
    const canvas = vp.querySelector('div[style*="transform"]'); if (!canvas) return
    const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/); if (!m) return
    const scale = parseFloat(m[3])
    const cardLeft = parseFloat(card.style.left); const cardTop = parseFloat(card.style.top); const cardW = parseFloat(card.style.width)
    const vpRect = vp.getBoundingClientRect()
    canvas.style.transform = `translate(${vpRect.width/2 - (cardLeft+cardW/2)*scale}px, ${vpRect.height/2 - (cardTop+26)*scale}px) scale(${scale})`
  }, son.id)
  await page.waitForTimeout(400)
  const out = `c:/tmp/12sons-byid-${String(idx+1).padStart(2,'0')}-${son.name}.png`
  await page.screenshot({ path: out })
  console.log(`   → ${out}`)
}

for (let i = 0; i < SONS.length; i++) await shotSon(SONS[i], i)
await browser.close()
console.log('✅ all 12 done')
