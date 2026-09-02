/**
 * 在 writing_projects 新增《基督宗教概論》（christianity-intro，kind='lecture'）。
 * 對應玄奘大學宗教與文化學系 PPA005 基督宗教概論（二年制在職專班，雙週班）。
 * 走 Supabase Management API（見 reference_supabase_management_api）。
 */
import fs from 'node:fs'
import path from 'node:path'

const env = Object.fromEntries(
  fs.readFileSync(path.join(process.cwd(), '.env'), 'utf8')
    .split(/\r?\n/).filter((l) => l && !l.startsWith('#'))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i), l.slice(i + 1).trim().replace(/^["']|["']$/g, '')] })
)
const ref = env.SUPABASE_URL.replace('https://', '').split('.')[0]
const endpoint = `https://api.supabase.com/v1/projects/${ref}/database/query`
const token = env.SUPABASE_ACCESS_TOKEN

async function runSql(sql) {
  const res = await fetch(endpoint, {
    method: 'POST',
    headers: { 'content-type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify({ query: sql }),
  })
  const text = await res.text()
  if (!res.ok) { console.error(res.status, text); process.exit(1) }
  return JSON.parse(text)
}

const q = (s) => `'${s.replace(/'/g, "''")}'`

const b = {
  slug: 'christianity-intro',
  title: '基督宗教概論',
  subtitle: '一個宗教學的讀法——四項核心傳統、兩千年教史與臺灣現場',
  description: '基督宗教概論授課講義：從拿撒勒人耶穌到當代臺灣教會，依教主、聖典、教義、聖行、體制、宗派、當今概況逐項介紹（十六章）。',
  emoji: '✝️',
  color: 'sky',
}

const sql = `
INSERT INTO writing_projects (slug, title, subtitle, description, emoji, color, status, kind, sort_order)
VALUES (
  ${q(b.slug)}, ${q(b.title)}, ${q(b.subtitle)}, ${q(b.description)},
  ${q(b.emoji)}, ${q(b.color)}, '構思中', 'lecture',
  COALESCE((SELECT MAX(sort_order) FROM writing_projects), 0) + 1
)
ON CONFLICT (slug) DO UPDATE SET
  title = EXCLUDED.title,
  subtitle = EXCLUDED.subtitle,
  description = EXCLUDED.description,
  emoji = EXCLUDED.emoji,
  color = EXCLUDED.color,
  kind = EXCLUDED.kind
RETURNING slug, title, kind, sort_order;`

console.log(await runSql(sql))
