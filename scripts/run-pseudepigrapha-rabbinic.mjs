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

const sql = fs.readFileSync(path.join(__dirname, '../database/pseudepigrapha-rabbinic.sql'), 'utf8')
console.log('=== Step 1: Insert pseudepigrapha + rabbinic people ===')
await runSql('pseudo-rabbinic-seed', sql)

const autolinkSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
console.log('\n=== Step 2: Autolink + generation recompute ===')
await runSql('autolink+generation', autolinkSql)

const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
console.log('\n=== Step 3: Manual generation assignments ===')
await runSql('manual-generations', manualSql)

console.log('\n=== Step 4: Verification ===')
await runSql('total',    `SELECT COUNT(*) AS total FROM biblical_people`)
await runSql('null-gen', `SELECT COUNT(*) AS null_gen FROM biblical_people WHERE generation IS NULL`)
await runSql('jubilees-check', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '亞哇（亞當之女）','亞士拉（亞當之女）','挪亞姆（塞特之女）',
    '慕阿利拉（以挪士之女）','拉忽雅（以諾之女）','以墨拉（挪亞之妻）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('enoch-check', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN ('示米哈匝（守望者之首）','亞薩谷（守望者）','拿非利人')
  ORDER BY generation NULLS LAST
`)
await runSql('hillel-chain', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '希勒（長者）','拉班·西緬（希勒之子）','拉班·迦瑪利一世（拉班·西緬之子）',
    '拉班·西緬三世（拉班·迦瑪利一世之子）','拉班·迦瑪利二世（拉班·西緬三世之子）',
    '拉比·西緬四世（拉班·迦瑪利二世之子）','拉比·猶大·哈納西（拉比·西緬四世之子）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('null-list', `
  SELECT name_zh, sort_order FROM biblical_people
  WHERE generation IS NULL ORDER BY sort_order LIMIT 20
`)
