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
const REF    = 'vloqgautkahgmqcwgfuo'
const URL    = `https://api.supabase.com/v1/projects/${REF}/database/query`

const sql = fs.readFileSync(
  path.join(__dirname, '../database/biblical-genealogy-seed.sql'),
  'utf8'
)

const resp = await fetch(URL, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ query: sql }),
})

const text = await resp.text()
console.log('Status:', resp.status)
console.log('Body:', text.slice(0, 300))
