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

const churchSql = fs.readFileSync(path.join(__dirname, '../database/church-tradition-genealogy.sql'), 'utf8')
console.log('=== Step 1: Insert church tradition genealogy ===')
await runSql('church-tradition-seed', churchSql)

const autolinkSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
console.log('\n=== Step 2: Autolink + generation recompute ===')
await runSql('autolink+generation', autolinkSql)

const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
console.log('\n=== Step 3: Manual generation assignments ===')
await runSql('manual-generations', manualSql)

console.log('\n=== Step 4: Verification ===')
await runSql('total',    `SELECT COUNT(*) AS total FROM biblical_people`)
await runSql('null-gen', `SELECT COUNT(*) AS null_gen FROM biblical_people WHERE generation IS NULL`)
await runSql('joachim-mary-chain', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '約亞敬（聖母之父）', '亞拿（聖母之母）', '馬利亞（耶穌之母）',
    '耶穌（拿撒勒人）', '雅各（主的兄弟）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('clopas-simeon', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '克洛帕斯（約瑟之兄）', '西默盎（克洛帕斯之子）',
    '佐革爾（主血親）', '雅各（主血親後裔）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('philip-daughters', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '腓力（傳道者）',
    '腓力之長女（先知）', '腓力之次女（先知）',
    '腓力之三女（先知）', '腓力之末女（先知）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('cyrene-rufus', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '古利奈西門（背十字架者）',
    '亞力山大（古利奈西門之子）', '魯孚（古利奈西門之子）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('null-list', `
  SELECT name_zh, sort_order FROM biblical_people
  WHERE generation IS NULL ORDER BY sort_order LIMIT 20
`)
