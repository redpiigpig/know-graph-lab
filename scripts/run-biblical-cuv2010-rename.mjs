import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const TOKEN = '>[REDACTED_PAT_2]'
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
  console.log(`${label}: ${r.status}${ok ? '' : ' — ' + text.slice(0, 500)}`)
  return ok
}

const renameSql = fs.readFileSync(path.join(__dirname, '../database/biblical-cuv2010-rename.sql'), 'utf8')
console.log('=== Step 1: CUV2010 renames + children field updates ===')
await runSql('cuv2010-rename', renameSql)

const autolinkSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
console.log('\n=== Step 2: Autolink + generation recompute ===')
await runSql('autolink+generation', autolinkSql)

const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
console.log('\n=== Step 3: Manual generation fixes ===')
await runSql('manual-generations', manualSql)

console.log('\n=== Step 4: Verification ===')
await runSql('total', `SELECT COUNT(*) AS total FROM biblical_people`)
await runSql('null-gen', `SELECT COUNT(*) AS null_gen FROM biblical_people WHERE generation IS NULL`)
await runSql('sample-呂便', `SELECT name_zh, children, generation FROM biblical_people WHERE name_zh IN ('呂便','哈諾（呂便之子）','希斯倫（呂便之子）')`)
await runSql('sample-spies', `SELECT name_zh FROM biblical_people WHERE sort_order BETWEEN 327 AND 339 ORDER BY sort_order`)
