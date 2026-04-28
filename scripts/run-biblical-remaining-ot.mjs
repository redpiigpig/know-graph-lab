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

const remainingOtSql = fs.readFileSync(path.join(__dirname, '../database/biblical-remaining-ot.sql'), 'utf8')
console.log('=== Step 1: Insert remaining OT people ===')
await runSql('remaining-ot-seed', remainingOtSql)

const autolinkSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
console.log('\n=== Step 2: Autolink + generation recompute ===')
await runSql('autolink+generation', autolinkSql)

const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
console.log('\n=== Step 3: Manual generation assignments ===')
await runSql('manual-generations', manualSql)

console.log('\n=== Step 4: Verification ===')
await runSql('total',    `SELECT COUNT(*) AS total FROM biblical_people`)
await runSql('null-gen', `SELECT COUNT(*) AS null_gen FROM biblical_people WHERE generation IS NULL`)
await runSql('prophets-check', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '何西阿（比利之子）','約珥（毗土利之子）','阿摩司（提哥亞牧人）',
    '約拿（亞米太之子）','彌迦（摩利沙人）','那鴻（伊勒歌斯人）',
    '哈巴谷（先知）','西番雅（古實之子）','以西結（布西之子）',
    '但以理（先知）','哈該（先知）','撒迦利亞（比利家之子）','瑪拉基（先知）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('job-check', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN ('約伯（烏斯人）','以利法（帖曼人）','以利戶（巴拿基勒之子）')
  ORDER BY generation NULLS LAST
`)
await runSql('null-list', `
  SELECT name_zh, sort_order FROM biblical_people
  WHERE generation IS NULL ORDER BY sort_order LIMIT 20
`)
