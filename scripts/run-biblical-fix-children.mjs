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
  console.log(`${label}: status ${r.status}`, r.status !== 201 ? text.slice(0, 300) : '')
  return r.status === 201
}

// Step 1: fix children fields
const fixSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-fix-children.sql'), 'utf8')
console.log('=== Step 1: Fixing children fields ===')
await runSql('fix-children', fixSql)

// Step 2: re-run generation calculation
const genSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-generation.sql'), 'utf8')
console.log('\n=== Step 2: Recomputing generations ===')
await runSql('generation', genSql)

// Step 3: manually assign generations for Seir clan (not reachable from Adam tree)
// Seir was the Horite patriarch, contemporary with Isaac; his family intersected with Esau's.
// We use Isaac's generation (21) as Seir's level so his grandchildren align with Esau (gen 22).
console.log('\n=== Step 3: Seir family manual generations ===')
await runSql('seir-root', `UPDATE biblical_people SET generation = 21 WHERE name_zh = '西珥' AND generation IS NULL`)

// Re-run generation one more time so Seir's family cascades down
await runSql('generation-pass2', genSql)

console.log('\n完成。所有有親子關係的人物都應已獲得代數。')
