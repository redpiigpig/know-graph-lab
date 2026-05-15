/**
 * Clicks the "展開朝代" button + counts expected dynasty figures in DOM.
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

const SUPABASE_URL = env.SUPABASE_URL
const SUPABASE_SERVICE_ROLE_KEY = env.SUPABASE_SERVICE_ROLE_KEY
const USER_EMAIL = env.ALLOWED_EMAIL || 'redpiigpig@gmail.com'
const APP_BASE = process.env.APP_BASE || 'http://localhost:3003'

const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink',
  email: USER_EMAIL,
  options: { redirectTo: APP_BASE + '/genealogy/biblical' },
})
const actionLink = linkData.properties.action_link

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({ viewport: { width: 1800, height: 1200 } })
const page = await context.newPage()

await page.goto(actionLink, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const prodUrl = page.url()
const fragment = new URL(prodUrl).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
const refreshToken = params.get('refresh_token') || ''
const expiresIn = parseInt(params.get('expires_in') || '3600', 10)
if (!accessToken) { console.error('No access_token'); process.exit(1) }

function decodeJwt(token) {
  const payload = token.split('.')[1]
  const padded = payload + '='.repeat((4 - payload.length % 4) % 4)
  return JSON.parse(Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf-8'))
}
const jwt = decodeJwt(accessToken)
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken, refresh_token: refreshToken,
  expires_at: jwt.exp, expires_in: expiresIn, token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: jwt.phone || '',
    app_metadata: jwt.app_metadata || {}, user_metadata: jwt.user_metadata || {},
    role: jwt.role, aal: jwt.aal, amr: jwt.amr || [], session_id: jwt.session_id,
    is_anonymous: jwt.is_anonymous || false },
}
function base64url(str) {
  return Buffer.from(str, 'utf-8').toString('base64')
    .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}
await context.addCookies([{
  name: `sb-${projectRef}-auth-token`, value: 'base64-' + base64url(JSON.stringify(session)),
  domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])

await page.goto(APP_BASE + '/genealogy/biblical-tree', { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
console.log('landed:', page.url())
await page.waitForSelector('.node-card', { timeout: 15000 })
await page.waitForTimeout(2000)

const beforeCount = await page.evaluate(() => document.querySelectorAll('.node-card').length)
console.log('cards BEFORE dynasty button:', beforeCount)

const clicked = await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  for (const b of btns) {
    if (b.textContent?.replace(/\s+/g, '').includes('展開朝代')) {
      b.click(); return true
    }
  }
  return false
})
console.log('button clicked =', clicked)
await page.waitForTimeout(2500)

const afterCount = await page.evaluate(() => document.querySelectorAll('.node-card').length)
console.log('cards AFTER dynasty button :', afterCount)

const sampleNames = await page.evaluate(() => {
  const expected = [
    '利未', '哥轄', '暗蘭', '亞倫', '以利亞撒', '約雅黎', '哈斯摩尼',
    '瑪塔提亞', '猶大·瑪加伯', '約翰·許爾堪一世', '亞歷山大·詹尼亞斯',
    '馬利安美一世', '大希律', '亞基老', '希律安提帕',
    '亞乃', '布斯坦奈', '馬·烏卡瓦一世',
    '哈突', '希勒爾長者', '加瑪列一世', '猶大親王', '加瑪列六世',
  ]
  const cards = Array.from(document.querySelectorAll('.node-card'))
  return expected.map(n => ({
    name: n,
    visible: cards.some(c => (c.textContent || '').replace(/\s+/g, '').includes(n)),
  }))
})
console.log('Sample names visible:')
for (const s of sampleNames) console.log(`  ${s.visible ? '✓' : '✗'}  ${s.name}`)

await page.screenshot({ path: process.argv[2] || 'c:/tmp/dynasty-shot.png' })
console.log('saved', process.argv[2] || 'c:/tmp/dynasty-shot.png')
await browser.close()
