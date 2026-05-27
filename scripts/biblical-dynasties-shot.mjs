/**
 * Screenshot the 3 dynasty expansions triggered by 「🏛️ 展開朝代」 button:
 *   - 利未 → Moses chain + 亞倫 → 大祭司線 → 馬加比 → (via 馬利安美一世) 大希律家
 *   - 哈拿尼雅（所羅巴伯之子）→ 亞乃 → Exilarch + 哈突 → Hillel-Nasi
 *   - 以掃 → 安提帕特 Idumean → 大希律家 (Herod dynasty)
 *
 * Takes 4 shots: overview + 3 zoom-ins on each dynasty's bottom-most card.
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
const j = dj(at)
const ref = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess = { access_token:at, refresh_token:rt, expires_at:j.exp, expires_in:3600, token_type:'bearer', user:{id:j.sub,aud:j.aud,email:j.email,phone:'',app_metadata:j.app_metadata||{},user_metadata:j.user_metadata||{},role:j.role,aal:j.aal,amr:j.amr||[],session_id:j.session_id,is_anonymous:false}}
const b64u = (s) => Buffer.from(s,'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await ctx.addCookies([{ name:`sb-${ref}-auth-token`, value:'base64-'+b64u(JSON.stringify(sess)), domain:new URL(APP_BASE).hostname, path:'/', httpOnly:false, secure:false, sameSite:'Lax' }])

await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(()=>{})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(1500)

// Click the 展開朝代 button
console.log('→ Clicking 展開朝代 button')
const dynastyClicked = await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  const btn = btns.find(b => (b.textContent||'').includes('展開朝代'))
  if (!btn) return false
  btn.click()
  return true
})
console.log(`   ${dynastyClicked ? 'clicked' : 'NOT FOUND'}`)
await page.waitForTimeout(2000)

async function panToById(id) {
  return await page.evaluate((id) => {
    const vp = document.querySelector('.bg-stone-50'); if (!vp) return false
    const card = Array.from(document.querySelectorAll('.node-card')).find(c => c.dataset.personId === id)
    if (!card) return false
    const canvas = vp.querySelector('div[style*="transform"]'); if (!canvas) return false
    const m = canvas.style.transform.match(/translate\(([-\d.]+)px,\s*([-\d.]+)px\)\s*scale\(([\d.]+)\)/); if (!m) return false
    const scale = parseFloat(m[3])
    const cardLeft = parseFloat(card.style.left); const cardTop = parseFloat(card.style.top); const cardW = parseFloat(card.style.width)
    const vpRect = vp.getBoundingClientRect()
    canvas.style.transform = `translate(${vpRect.width/2 - (cardLeft+cardW/2)*scale}px, ${vpRect.height/2 - (cardTop+26)*scale}px) scale(${scale})`
    return true
  }, id)
}

// Helpful anchors deep inside each dynasty
const ANCHORS = [
  { tag: 'overview', id: null, note: 'after 展開朝代' },
  // Levi dynasty deep — 馬加比家 (gen ~40), or 馬利安美一世 (Herod's wife)
  { tag: 'levi-maccabee', id: 'levi-maccabee', note: 'pan to 利未→馬加比 deepest' },
  // Hananiah dynasty — gen ~30+
  { tag: 'hananiah', id: 'hananiah', note: 'pan to 哈拿尼雅 chain' },
  // Esau dynasty deep — 大希律 (Herod the Great, gen 60+)
  { tag: 'esau-herod', id: 'esau-herod', note: 'pan to 以掃→大希律' },
]

// We need actual UUIDs. Let me query DB now to find deepest anchors.
console.log('→ Looking up dynasty anchor IDs')
const anchorIds = await page.evaluate(() => {
  const cards = Array.from(document.querySelectorAll('.node-card'))
  function findByName(target) {
    const matches = cards.filter(c => c.dataset.rawName === target)
    return matches[0]?.dataset.personId
  }
  return {
    'levi-deep': findByName('猶大·瑪加伯（馬加比）') || findByName('馬加比') || findByName('馬利安美一世'),
    'hananiah-deep': findByName('亞乃（哈拿尼雅之子）') || findByName('亞乃') || findByName('哈拿尼雅（所羅巴伯之子）'),
    'esau-deep': findByName('大希律') || findByName('希律'),
  }
})
console.log('   anchors:', JSON.stringify(anchorIds))

await page.screenshot({ path: 'c:/tmp/dynasty-00-overview.png' })
console.log('   → c:/tmp/dynasty-00-overview.png')

for (const [tag, id] of Object.entries(anchorIds)) {
  if (!id) { console.log(`   skip ${tag} (no anchor)`); continue }
  const ok = await panToById(id)
  console.log(`→ pan to ${tag} (${id.slice(0,8)}…) — ${ok}`)
  await page.waitForTimeout(400)
  const out = `c:/tmp/dynasty-${tag}.png`
  await page.screenshot({ path: out })
  console.log(`   → ${out}`)
}

await browser.close()
console.log('✅ dynasties done')
