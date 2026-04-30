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

const chroniclesSql = fs.readFileSync(path.join(__dirname, '../database/biblical-chronicles.sql'), 'utf8')
console.log('=== Step 1: Insert Chronicles people ===')
await runSql('chronicles-seed', chroniclesSql)

const autolinkSql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
console.log('\n=== Step 2: Autolink + generation recompute ===')
await runSql('autolink+generation', autolinkSql)

const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
console.log('\n=== Step 3: Manual generation assignments ===')
await runSql('manual-generations', manualSql)

console.log('\n=== Step 4: Verification ===')
await runSql('total',    `SELECT COUNT(*) AS total FROM biblical_people`)
await runSql('null-gen', `SELECT COUNT(*) AS null_gen FROM biblical_people WHERE generation IS NULL`)
await runSql('priestly-chain', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '非尼哈','亞比書（非尼哈之子）','布基（亞比書之子）','烏西（布基之子）',
    '西拉希雅（烏西之子）','米拉約特（西拉希雅之子）','亞瑪利雅（第一）',
    '亞希突（第一）','撒督（第一）','亞希瑪斯（撒督之子）',
    '沙龍（撒督之子）','希勒家（沙龍之子）','西萊雅（亞撒利雅之子）',
    '約薩達（西萊雅之子）','耶書亞（約薩達之子）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('zerubbabel-chain', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN (
    '約雅斤（約雅敬之子）','撒拉鐵（約雅斤之子）','毗大雅（約雅斤之子）',
    '所羅巴伯（撒拉鐵之子）','哈拿尼雅（所羅巴伯之子）','示迦尼雅（哈拿尼雅之子）'
  )
  ORDER BY generation NULLS LAST
`)
await runSql('prophets', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN ('亞摩斯（以賽亞之父）','以賽亞（亞摩斯之子）','希勒家（耶利米之父）','耶利米（希勒家之子）')
  ORDER BY generation NULLS LAST
`)
await runSql('bezalel', `
  SELECT name_zh, generation FROM biblical_people
  WHERE name_zh IN ('迦勒（希斯崙之子）','戶珥（迦勒之子）','烏利（戶珥之子）','比撒列（烏利之子）')
  ORDER BY generation NULLS LAST
`)
await runSql('null-list', `
  SELECT name_zh, sort_order FROM biblical_people
  WHERE generation IS NULL ORDER BY sort_order LIMIT 20
`)
