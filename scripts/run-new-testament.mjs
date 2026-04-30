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

const ntSql = fs.readFileSync(path.join(__dirname, '../database/new-testament.sql'), 'utf8')
console.log('=== Step 1: Insert New Testament people ===')
await runSql('nt-seed', ntSql)

const autolinkSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
console.log('\n=== Step 2: Autolink + generation recompute ===')
await runSql('autolink+generation', autolinkSql)

const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
console.log('\n=== Step 3: Manual generation assignments ===')
await runSql('manual-generations', manualSql)

console.log('\n=== Step 4: Verification ===')
await runSql('total',    `SELECT COUNT(*) AS total FROM biblical_people`)
await runSql('null-gen', `SELECT COUNT(*) AS null_gen FROM biblical_people WHERE generation IS NULL`)
await runSql('matthew-chain', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '亞比烏（所羅巴伯之子）','馬但（以利亞撒之子）','雅各（馬但之子）',
    '約瑟（馬利亞之夫）','耶穌（拿撒勒人）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('jesus-family', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '馬利亞（耶穌之母）','撒迦利亞（施洗約翰之父）','施洗約翰（撒迦利亞之子）',
    '雅各（主的兄弟）','拿但（大衛之子）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('herod-chain', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '安提帕特（大希律之父）','大希律（安提帕特之子）','希律安提帕（大希律之子）',
    '亞里斯托布魯（大希律之子）','亞基帕一世（亞里斯托布魯之子）','亞基帕二世（亞基帕一世之子）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('apostles', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '西門彼得（約拿之子）','安得烈（約拿之子）','雅各（西庇太之子）',
    '約翰（西庇太之子）','保羅（使徒）','提摩太（友尼基之子）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('null-list', `
  SELECT name_zh, sort_order FROM biblical_people
  WHERE generation IS NULL ORDER BY sort_order LIMIT 20
`)
