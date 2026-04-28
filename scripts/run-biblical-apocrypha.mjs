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
  console.log(`${label}: ${r.status}${ok ? '' : ' — ' + text.slice(0, 600)}`)
  return ok
}

const apocryphaSql = fs.readFileSync(path.join(__dirname, '../database/apocrypha.sql'), 'utf8')
console.log('=== Step 1: Insert apocrypha people ===')
await runSql('apocrypha-seed', apocryphaSql)

const autolinkSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
console.log('\n=== Step 2: Autolink + generation recompute ===')
await runSql('autolink+generation', autolinkSql)

const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
console.log('\n=== Step 3: Manual generation assignments ===')
await runSql('manual-generations', manualSql)

console.log('\n=== Step 4: Verification ===')
await runSql('total',    `SELECT COUNT(*) AS total FROM biblical_people`)
await runSql('null-gen', `SELECT COUNT(*) AS null_gen FROM biblical_people WHERE generation IS NULL`)
await runSql('tobit-check', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '托彼爾（多比之父）','多比（托彼爾之子）','多比亞（多比之子）',
    '辣古耳（撒拉之父）','撒拉（辣古耳之女）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('hasmonean-check', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '西默盎（哈斯蒙族長）','約翰（西默盎之子）','瑪他提亞（約翰之子）',
    '猶大瑪加比（瑪他提亞之子）','西門（瑪他提亞之子）',
    '若望依爾卡諾（西門之子）','亞歷山大雅內（依爾卡諾之子）',
    '許爾加諾二世（亞歷山大之子）','安提哥諾（許爾加諾二世之子）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('null-list', `
  SELECT name_zh, sort_order FROM biblical_people
  WHERE generation IS NULL ORDER BY sort_order LIMIT 20
`)
