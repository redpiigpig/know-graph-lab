import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'
const env={};for(const l of fs.readFileSync('.env','utf-8').split('\n')){if(!l.includes('=')||l.trim().startsWith('#'))continue;const[k,...r]=l.split('=');env[k.trim()]=r.join('=').trim().replace(/^["']|["']$/g,'')}
const admin=createClient(env.SUPABASE_URL,env.SUPABASE_SERVICE_ROLE_KEY,{auth:{autoRefreshToken:false,persistSession:false}})
const{data:linkData}=await admin.auth.admin.generateLink({type:'magiclink',email:env.ALLOWED_EMAIL||'redpiigpig@gmail.com',options:{redirectTo:'http://localhost:3003/genealogy/biblical'}})
const browser=await chromium.launch({headless:true})
const context=await browser.newContext({viewport:{width:1800,height:1200}})
const page=await context.newPage()
await page.goto(linkData.properties.action_link,{waitUntil:'domcontentloaded'})
await page.waitForLoadState('networkidle').catch(()=>{})
const f=new URL(page.url()).hash.replace(/^#/,'')
const p=new URLSearchParams(f)
const tok=p.get('access_token'),rtok=p.get('refresh_token')||''
const jwt=JSON.parse(Buffer.from((tok.split('.')[1]+'='.repeat((4-tok.split('.')[1].length%4)%4)).replace(/-/g,'+').replace(/_/g,'/'),'base64').toString())
const ref=new URL(env.SUPABASE_URL).hostname.split('.')[0]
const sess={access_token:tok,refresh_token:rtok,expires_at:jwt.exp,expires_in:3600,token_type:'bearer',user:{id:jwt.sub,aud:jwt.aud,email:jwt.email,phone:jwt.phone||'',app_metadata:jwt.app_metadata||{},user_metadata:jwt.user_metadata||{},role:jwt.role,aal:jwt.aal,amr:jwt.amr||[],session_id:jwt.session_id,is_anonymous:false}}
const b64u=s=>Buffer.from(s,'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')
await context.addCookies([{name:`sb-${ref}-auth-token`,value:'base64-'+b64u(JSON.stringify(sess)),domain:'localhost',path:'/',httpOnly:false,secure:false,sameSite:'Lax'}])
await page.goto('http://localhost:3003/genealogy/biblical-tree',{waitUntil:'domcontentloaded'})
await page.waitForLoadState('networkidle').catch(()=>{})
await page.waitForSelector('.node-card',{timeout:15000})
await page.waitForTimeout(2000)
// Find 底拿 + 她瑪 positions
const res=await page.evaluate(()=>{
  const cards=Array.from(document.querySelectorAll('.node-card'))
  const dina=cards.filter(c=>c.textContent?.includes('底拿')).map(c=>({text:c.textContent.trim().replace(/\s+/g,' ').slice(0,30),top:parseFloat(c.style.top||'0'),left:parseFloat(c.style.left||'0'),display:getComputedStyle(c).display}))
  const tamar=cards.filter(c=>c.textContent?.includes('她瑪')).map(c=>({text:c.textContent.trim().replace(/\s+/g,' ').slice(0,30),top:parseFloat(c.style.top||'0'),left:parseFloat(c.style.left||'0'),display:getComputedStyle(c).display}))
  const shua=cards.filter(c=>c.textContent?.includes('書亞之女')).map(c=>({text:c.textContent.trim().replace(/\s+/g,' ').slice(0,30),top:parseFloat(c.style.top||'0'),left:parseFloat(c.style.left||'0')}))
  // Find all red SVG lines at y matching gen 23 marriage area
  // SVG marriage lines might be in <line> or <path>, but ours use line.
  // Check parent g for v-for key (id)
  const lineEls=Array.from(document.querySelectorAll('svg line')).filter(l=>{
    const s=l.getAttribute('stroke')
    const y1=parseFloat(l.getAttribute('y1')||'0')
    const x1=parseFloat(l.getAttribute('x1')||'0')
    const x2=parseFloat(l.getAttribute('x2')||'0')
    return s==='#dc2626' && y1>=3190 && y1<=3210 && Math.abs(x2-x1) > 100  // wide ones
  })
  const lines = lineEls.map(l => {
    // Try to find the v-for key on parent g element
    let g = l.parentElement
    while (g && g.tagName.toLowerCase() !== 'g') g = g.parentElement
    return {
      x1:parseFloat(l.getAttribute('x1')||'0'),
      y:parseFloat(l.getAttribute('y1')||'0'),
      x2:parseFloat(l.getAttribute('x2')||'0'),
      display:getComputedStyle(l).display,
      outerHTML: l.outerHTML.slice(0, 250),
      parentHTML: g ? g.outerHTML.slice(0, 200) : '',
    }
  }).sort((a,b)=>a.x1-b.x1)
  return{dina,tamar,shua,lines}
})
console.log('底拿:',JSON.stringify(res.dina))
console.log('她瑪:',JSON.stringify(res.tamar))
console.log('書亞之女:',JSON.stringify(res.shua))
console.log('紅婚姻線 at y=3198±10 (width >100):')
for(const l of res.lines){
  console.log(`  x=${l.x1}-${l.x2} ${l.display}`)
  console.log(`    line: ${l.outerHTML}`)
  console.log(`    parent: ${l.parentHTML}`)
}
await browser.close()
