import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const TOKEN  = '>[REDACTED_PAT_2]'
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
