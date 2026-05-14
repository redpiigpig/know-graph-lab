/**
 * Spine diagnostic: fetch /api/genealogy/biblical-graph and walk the dual-spine
 * waypoints to find the broken segment.
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
const APP_BASE = process.env.APP_BASE || 'http://localhost:3002'
const VIEW = process.env.VIEW || 'protestant'

const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: linkData } = await admin.auth.admin.generateLink({
  type: 'magiclink', email: USER_EMAIL,
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
const projectRef = new URL(SUPABASE_URL).hostname.split('.')[0]
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

// Capture biblical-graph response when the page fetches it itself
let graph = null
page.on('response', async (resp) => {
  if (resp.url().includes('/api/genealogy/biblical-graph')) {
    try { graph = await resp.json() } catch {}
  }
})
await page.goto(APP_BASE + `/genealogy/biblical-tree?view=${VIEW}`, { waitUntil: 'domcontentloaded' })
await page.waitForLoadState('networkidle').catch(() => {})
await page.waitForTimeout(2000)
if (!graph) { console.error('No biblical-graph response captured'); await browser.close(); process.exit(1) }
console.log('Captured nodes:', graph.nodes?.length, 'edges:', graph.edges?.length)
console.log('nodes:', graph.nodes?.length, 'edges:', graph.edges?.length)

// build adjacency
const childrenOf = new Map()
const byName = new Map()
const byId = new Map()
for (const n of graph.nodes) {
  byName.set(n.data.name, n.id)
  byId.set(n.id, n.data.name)
}
for (const e of graph.edges) {
  if (e.data?.relationshipType === 'parentChild') {
    if (!childrenOf.has(e.source)) childrenOf.set(e.source, [])
    childrenOf.get(e.source).push(e.target)
  }
}

const SPINE_A = ['亞當','塞特','挪亞','閃','亞伯拉罕','以撒','雅各','猶大','大衛（耶西之子）','所羅門（大衛之子）','雅各（馬但之子）','約瑟（馬利亞之夫）','耶穌（拿撒勒人）']
const SPINE_B = ['亞當','塞特','挪亞','閃','亞伯拉罕','以撒','雅各','猶大','大衛（耶西之子）','拿單（大衛之子）','瑪塔（路加 3:24）','約亞敬（聖母之父）','馬利亞（耶穌之母）','耶穌（拿撒勒人）']

function bfs(src, dst) {
  if (src === dst) return [src]
  const q = [[src]]
  const vis = new Set()
  while (q.length) {
    const p = q.shift()
    const cur = p[p.length-1]
    if (cur === dst) return p
    if (vis.has(cur)) continue
    vis.add(cur)
    for (const c of childrenOf.get(cur) ?? []) if (!vis.has(c)) q.push([...p, c])
  }
  return []
}

function diagSpine(label, names) {
  console.log(`\n=== ${label} ===`)
  let prevId = null
  for (const name of names) {
    const id = byName.get(name)
    if (!id) { console.log(`❌ name not found in DB: "${name}"`); prevId = null; continue }
    if (prevId !== null) {
      const seg = bfs(prevId, id)
      if (!seg.length) {
        console.log(`❌ no path: "${byId.get(prevId)}" → "${name}"`)
        const kids = (childrenOf.get(prevId) ?? []).map(c => byId.get(c))
        console.log(`   "${byId.get(prevId)}".children = [${kids.join(', ')}]`)
      } else {
        console.log(`✅ "${byId.get(prevId)}" → "${name}" (${seg.length} hops)`)
      }
    } else {
      console.log(`✅ start: "${name}"`)
    }
    prevId = id
  }
}

diagSpine('SPINE A (馬太)', SPINE_A)
diagSpine('SPINE B (路加)', SPINE_B)

await browser.close()
