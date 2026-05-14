/**
 * Dump rendered DOM positions of marriage lines, hbars, drops for David area.
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

await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000)

const dump = await page.evaluate(() => {
  // Find David card (J33 大衛)
  const cards = Array.from(document.querySelectorAll('.node-card'))
  const david = cards.find(c => c.textContent?.includes('大衛'))
  const haggith = cards.find(c => c.textContent?.includes('哈及'))
  const yfia = cards.find(c => c.textContent?.includes('雅非亞'))
  const cardInfo = (card, label) => card ? `${label}: top=${parseFloat(card.style.top).toFixed(0)} left=${parseFloat(card.style.left).toFixed(0)} text="${card.textContent.slice(0, 20)}"` : `${label}: NOT FOUND`

  // Find all SVG lines in the canvas (drops, hbars, marriages are SVG <line>)
  const lines = Array.from(document.querySelectorAll('svg line'))
  // Filter lines near David's row (Y range)
  const davidTop = david ? parseFloat(david.style.top) : 0
  const yfiaTop = yfia ? parseFloat(yfia.style.top) : 0
  const inRange = (y) => y >= davidTop - 10 && y <= yfiaTop + 40
  const relevantLines = lines.filter(l => {
    const y1 = parseFloat(l.getAttribute('y1'))
    const y2 = parseFloat(l.getAttribute('y2'))
    return inRange(y1) && inRange(y2)
  })
  // Group by Y for horizontals (y1==y2) and color
  const horizontals = relevantLines.filter(l => parseFloat(l.getAttribute('y1')) === parseFloat(l.getAttribute('y2')))
  const horizSummary = horizontals.map(l => {
    const y = parseFloat(l.getAttribute('y1'))
    const x1 = parseFloat(l.getAttribute('x1'))
    const x2 = parseFloat(l.getAttribute('x2'))
    const stroke = l.getAttribute('stroke') || l.style?.stroke || 'inherit'
    return { y: y.toFixed(1), x1: x1.toFixed(0), x2: x2.toFixed(0), w: (x2 - x1).toFixed(0), stroke }
  })
  horizSummary.sort((a, b) => parseFloat(a.y) - parseFloat(b.y))
  return {
    david: cardInfo(david, 'David'),
    haggith: cardInfo(haggith, 'Haggith'),
    yfia: cardInfo(yfia, 'YfiA(雅非亞)'),
    totalLines: lines.length,
    relevantHorizontals: horizSummary,
  }
})

console.log('David card:', dump.david)
console.log('Haggith card:', dump.haggith)
console.log('雅非亞 card:', dump.yfia)
console.log('Total SVG lines:', dump.totalLines)
console.log('\nHorizontals near David row, sorted by Y:')
for (const h of dump.relevantHorizontals) {
  console.log(`  y=${h.y}  x=[${h.x1}..${h.x2}]  w=${h.w}  stroke=${h.stroke}`)
}

await browser.close()
