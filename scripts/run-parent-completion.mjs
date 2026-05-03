import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const env = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, '../.env'), 'utf8')
    .split(/\r?\n/).filter(l => l && !l.startsWith('#'))
    .map(l => { const i = l.indexOf('='); return [l.slice(0, i), l.slice(i+1).trim().replace(/^["']|["']$/g, '')] })
)
const TOKEN = env.SUPABASE_ACCESS_TOKEN
const REF   = 'vloqgautkahgmqcwgfuo'
const URL   = `https://api.supabase.com/v1/projects/${REF}/database/query`

async function runSql(label, query) {
  const r = await fetch(URL, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${TOKEN}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  const text = await r.text()
  const ok = r.status === 201
  console.log(`${label}: ${r.status}${ok ? '' : ' — ' + text.slice(0, 600)}`)
  if (ok) {
    try {
      const rows = JSON.parse(text)
      if (Array.isArray(rows) && rows.length) console.log('  →', JSON.stringify(rows))
    } catch {}
  }
  return ok
}

// ── Step 1: 補全缺漏父母 ──────────────────────────────────────────────
console.log('=== Step 1: 掃描「X之子/女」模式，插入缺漏父母 ===')
const completionSql = fs.readFileSync(
  path.join(__dirname, '../database/biblical-parent-completion.sql'), 'utf8'
)
await runSql('parent-completion', completionSql)

// ── Step 2: 重跑 autolink（建立親子邊、重算代數）─────────────────────
console.log('\n=== Step 2: 重跑 autolink + generation ===')
const autolinkSql = fs.readFileSync(
  path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8'
)
await runSql('autolink + generation', autolinkSql)

// ── Step 3: 驗證 ─────────────────────────────────────────────────────
console.log('\n=== Step 3: 驗證結果 ===')
await runSql('total', `SELECT COUNT(*) AS total FROM biblical_people`)
await runSql('null-gen', `SELECT COUNT(*) AS null_gen FROM biblical_people WHERE generation IS NULL`)
await runSql('auto-completed', `
  SELECT name_zh, generation, notes
  FROM biblical_people
  WHERE notes LIKE '自動補全%'
  ORDER BY generation NULLS LAST, name_zh
  LIMIT 50
`)
await runSql('null-gen-list', `
  SELECT name_zh, notes
  FROM biblical_people
  WHERE generation IS NULL
  ORDER BY name_zh
  LIMIT 30
`)
