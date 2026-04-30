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
  console.log(`${label}: ${r.status}${ok ? '' : ' — ' + text.slice(0, 400)}`)
  return ok
}

const sql = fs.readFileSync(path.join(__dirname, '../database/biblical-genealogy-autolink.sql'), 'utf8')
await runSql('autolink + generation', sql)

const manualSql = fs.readFileSync(path.join(__dirname, '../database/biblical-manual-generations.sql'), 'utf8')
await runSql('manual-generations', manualSql)

// Check how many still have no generation
await runSql('count-null-gen', `
  SELECT COUNT(*) AS still_null FROM biblical_people WHERE generation IS NULL
`)
