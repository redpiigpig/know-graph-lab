// One-off: snapshot the 3 genealogy graph endpoints into test fixtures.
// Signs in with env creds to satisfy requireAuth. Token is never printed.
import { createClient } from '@supabase/supabase-js'
import { readFileSync, writeFileSync } from 'node:fs'

const env = Object.fromEntries(
  readFileSync('.env', 'utf8').split(/\r?\n/)
    .filter(l => l && !l.startsWith('#') && l.includes('='))
    .map(l => { const i = l.indexOf('='); return [l.slice(0, i), l.slice(i + 1)] })
)

const EMAIL = env.ALLOWED_EMAIL || 'redpiigpig@gmail.com'
// Mint a real user session token via the admin API (no password needed).
const admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
})
const { data: link, error: linkErr } = await admin.auth.admin.generateLink({ type: 'magiclink', email: EMAIL })
if (linkErr) { console.error('generateLink failed:', linkErr.message); process.exit(1) }
const otp = link.properties?.email_otp
const anon = createClient(env.SUPABASE_URL, env.SUPABASE_KEY, { auth: { persistSession: false } })
const { data: sess, error: otpErr } = await anon.auth.verifyOtp({ email: EMAIL, token: otp, type: 'magiclink' })
if (otpErr) { console.error('verifyOtp failed:', otpErr.message); process.exit(1) }
const token = sess.session.access_token

const base = 'http://localhost:3037/api/genealogy'
const targets = [['biblical', 'biblical-graph'], ['islamic', 'islamic-graph'], ['episcopal', 'episcopal-graph']]
for (const [name, path] of targets) {
  const r = await fetch(`${base}/${path}`, { headers: { Authorization: `Bearer ${token}` } })
  const j = await r.json()
  writeFileSync(`test/genealogy/fixtures/snapshots/${name}.json`, JSON.stringify(j))
  const summary = j.nodes
    ? `nodes=${j.nodes.length} edges=${j.edges?.length ?? '-'}`
    : `spines=${j.spines?.length ?? '-'} branches=${j.branches?.length ?? '-'} apostles=${j.apostles?.length ?? '-'}`
  console.error(`${name}: HTTP ${r.status} ${summary}`)
}
process.exit(0)
