/**
 * Inspect specific people across all views to debug the Mary/Joseph/Salome area.
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

const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink', email: env.ALLOWED_EMAIL || 'redpiigpig@gmail.com',
  options: { redirectTo: APP_BASE + '/genealogy/biblical' },
})
const browser = await chromium.launch({ headless: true })
const context = await browser.newContext()
const page = await context.newPage()
await page.goto(linkData.properties.action_link, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
const fragment = new URL(page.url()).hash.replace(/^#/, '')
const params = new URLSearchParams(fragment)
const accessToken = params.get('access_token')
function decodeJwt(t) { const p = t.split('.')[1]; return JSON.parse(Buffer.from(p + '==='.slice(p.length % 4), 'base64').toString()) }
const jwt = decodeJwt(accessToken)
const projectRef = new URL(env.SUPABASE_URL).hostname.split('.')[0]
const session = {
  access_token: accessToken, refresh_token: params.get('refresh_token') || '',
  expires_at: jwt.exp, expires_in: parseInt(params.get('expires_in') || '3600'),
  token_type: 'bearer',
  user: { id: jwt.sub, aud: jwt.aud, email: jwt.email, phone: '', app_metadata: jwt.app_metadata||{}, user_metadata: jwt.user_metadata||{}, role: jwt.role, aal: jwt.aal, amr: jwt.amr||[], session_id: jwt.session_id, is_anonymous: false },
}
function b64url(s) { return Buffer.from(s).toString('base64').replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'') }
await context.addCookies([{
  name: `sb-${projectRef}-auth-token`, value: 'base64-' + b64url(JSON.stringify(session)),
  domain: new URL(APP_BASE).hostname, path: '/', httpOnly: false, secure: false, sameSite: 'Lax',
}])

const TARGETS = [
  '撒羅米（約瑟之前妻）',
  '約瑟（馬利亞之夫）',
  '馬利亞（耶穌之母）',
  '蘇比',
  '以利沙白',
  '撒迦利亞',
  '施洗約翰',
  '亞拿（聖母之母）',
  '雅各',  // ambiguous — may have multiple
  '約西',
  '西門',
  '猶大',
  '亞西亞',
  '呂底亞',
]
const VIEWS = ['protestant', 'early_consensus', 'orthodox', 'catholic']

for (const view of VIEWS) {
  let graph = null
  page.on('response', async r => {
    if (r.url().includes('/api/genealogy/biblical-graph') && !graph) {
      try { graph = await r.json() } catch {}
    }
  })
  await page.goto(`${APP_BASE}/genealogy/biblical-tree?view=${view}`, { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle').catch(() => {})
  await page.waitForTimeout(1500)
  if (!graph) { console.log(`[${view}] no graph captured`); continue }
  console.log(`\n========= view: ${view} (n=${graph.nodes.length}) =========`)
  const byName = new Map(graph.nodes.map(n => [n.data.name, n]))
  for (const t of TARGETS) {
    // exact + suffix matches
    const matches = graph.nodes.filter(n => n.data.name === t || n.data.name.startsWith(t + '（') || (n.data.name.includes(t) && t.length > 1 && !n.data.name.includes('之')))
    const exact = byName.get(t)
    const list = exact ? [exact] : matches
    for (const node of list) {
      const parentEdges = graph.edges.filter(e => e.target === node.id && e.data?.relationshipType === 'parentChild').map(e => byName.has(graph.nodes.find(n=>n.id===e.source)?.data.name) ? graph.nodes.find(n=>n.id===e.source).data.name : e.source)
      const childEdges = graph.edges.filter(e => e.source === node.id && e.data?.relationshipType === 'parentChild').map(e => graph.nodes.find(n=>n.id===e.target)?.data.name || e.target)
      const spouseEdges = graph.edges.filter(e => (e.source === node.id || e.target === node.id) && e.data?.relationshipType === 'spouse').map(e => {
        const other = e.source === node.id ? e.target : e.source
        return graph.nodes.find(n=>n.id===other)?.data.name || other
      })
      console.log(`  ${node.data.name} [gen ${node.data.generation}, trad=${node.data.tradition}]`)
      console.log(`     parents: ${parentEdges.join('、') || '(none)'}`)
      console.log(`     children: ${childEdges.join('、') || '(none)'}`)
      console.log(`     spouse: ${spouseEdges.join('、') || '(none)'}`)
    }
    if (list.length === 0) console.log(`  ❌ ${t}: NOT IN VIEW`)
  }
  graph = null
}

await browser.close()
