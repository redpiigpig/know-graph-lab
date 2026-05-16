/** Find where 哈娃 (Eve) is rendered in the DOM. */
import { chromium } from 'playwright'
import { createClient } from '@supabase/supabase-js'
import fs from 'node:fs'

const env = {}
for (const line of fs.readFileSync('.env', 'utf-8').split('\n')) {
  if (!line.includes('=') || line.trim().startsWith('#')) continue
  const [k, ...rest] = line.split('=')
  env[k.trim()] = rest.join('=').trim().replace(/^["']|["']$/g, '')
}

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: 'redpiigpig@gmail.com',
  options: { redirectTo: 'http://localhost:3006/genealogy/islamic-tree' },
})

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1800, height: 1200 } })
const page = await context.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})

function decodeJwt(token) {
  const payload = token.split('.')[1]
  const padded = payload + '='.repeat((4 - payload.length % 4) % 4)
  return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8'))
}
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const jwt = decodeJwt(accessToken)
const projectRef = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken, refresh_token: refreshToken,
  expires_at: jwt.exp, expires_in: 3600, token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, role: jwt.role, aal: jwt.aal,
    app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {} },
}
function base64url(s) { return Buffer.from(s, 'utf-8').toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'') }
await context.addCookies([{
  name: `sb-${projectRef}-auth-token`,
  value: 'base64-' + base64url(JSON.stringify(session)),
  domain: 'localhost', path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])
await page.goto('http://localhost:3006/genealogy/islamic-tree?view=sunni', { waitUntil: 'domcontentloaded', timeout: 90000 })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2500)

const result = await page.evaluate(() => {
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const summary = cards.map((c, i) => ({
    idx: i,
    text: (c.textContent || '').slice(0, 40),
    left: parseFloat(c.style.left || '0'),
    top: parseFloat(c.style.top || '0'),
    rectX: Math.round(c.getBoundingClientRect().x),
    rectY: Math.round(c.getBoundingClientRect().y),
    parent: c.parentElement?.className?.slice(0, 30),
  }))
  // Marriage lines (red horizontal) at gen 1 area (top<150)
  const lines = Array.from(document.querySelectorAll('svg line'))
    .map(l => ({
      x1: parseFloat(l.getAttribute('x1')),
      y1: parseFloat(l.getAttribute('y1')),
      x2: parseFloat(l.getAttribute('x2')),
      y2: parseFloat(l.getAttribute('y2')),
      stroke: l.getAttribute('stroke'),
    }))
    .filter(l => l.y1 < 200 && l.y2 < 200 && l.stroke && (l.stroke.includes('dc2626') || l.stroke.includes('f43f5e')))
  return {
    total: cards.length,
    eve: summary.filter(s => s.text.includes('哈娃')),
    adam: summary.filter(s => s.text.includes('阿丹')),
    muhammad: summary.filter(s => s.text.includes('穆罕默德') && !s.text.includes('巴基爾') && !s.text.includes('伊本')).slice(0, 3),
    wives: summary.filter(s =>
      s.text.includes('赫蒂徹') || s.text.includes('阿伊莎') || s.text.includes('蘇黛') ||
      s.text.includes('哈芙莎') || s.text.includes('烏姆·薩拉瑪') || s.text.includes('賈赫什') ||
      s.text.includes('朱韋里葉') || s.text.includes('烏姆·哈比巴') || s.text.includes('莎菲婭') ||
      s.text.includes('邁穆娜') || s.text.includes('瑪利亞·科普特') || s.text.includes('胡扎伊瑪')
    ),
  }
})
console.log('Total cards:', result.total)
console.log('Eve:', JSON.stringify(result.eve))
console.log('Adam:', JSON.stringify(result.adam))
console.log('Muhammad:', JSON.stringify(result.muhammad))
console.log('Wives:')
for (const w of result.wives) console.log(' ', JSON.stringify(w))

await browser.close()
