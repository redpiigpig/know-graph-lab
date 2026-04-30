import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const env   = Object.fromEntries(
  fs.readFileSync(path.join(__dirname, '../.env'), 'utf8')
    .split(/?
/).filter(l => l && !l.startsWith('#'))
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
  return ok
}

// Step 1: insert Exodus–Deuteronomy genealogies
const seedSql = fs.readFileSync(path.join(__dirname, '../database/biblical-exodus-deuteronomy.sql'), 'utf8')
console.log('=== Step 1: Inserting Exodus–Deuteronomy people ===')
await runSql('exodus-deuteronomy-seed', seedSql)

// Step 2: re-run autolink (pattern-based parent detection) + generation recompute
const autolinkSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
console.log('\n=== Step 2: Autolink + generation recompute ===')
await runSql('autolink+generation', autolinkSql)

// Step 3: manual generations for people not reachable from Adam/Eve tree
const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
console.log('\n=== Step 3: Manual generation assignments ===')
await runSql('manual-generations', manualSql)

// Step 4: check how many still have no generation
console.log('\n=== Step 4: Checking null generations ===')
await runSql('count-null-gen', `SELECT COUNT(*) AS still_null FROM biblical_people WHERE generation IS NULL`)
await runSql('list-null-gen', `SELECT name_zh FROM biblical_people WHERE generation IS NULL ORDER BY sort_order LIMIT 30`)
