/**
 * 在 writing_projects 新增兩本教科書寫作計畫（kind='lecture' 講義寫作分區）：
 *  1.《世界宗教文化導論》（world-religions-intro）— 八大界域架構的宗教系教科書
 *  2.《漢字文學史》（sinographic-literature）— 宗教系國文講義
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

// 卡片描述需精簡（/works 卡片 line-clamp 3 行）；詳述放書頁與章節草稿。
const books = [
  {
    slug: 'world-religions-intro',
    title: '世界宗教文化導論',
    subtitle: '全球八大人文宗教界域',
    description: '宗教系大學教科書：以六百年時代律 × 八大界域為時空雙座標的世界宗教文化史。',
    emoji: '🌍',
    color: 'emerald',
  },
  {
    slug: 'sinographic-literature',
    title: '宗教系國文講義',
    subtitle: '漢字文學史——宗教與東亞漢字書寫圈的文學世界',
    description: '宗教系國文講義：以宗教為軸線、涵蓋中日韓越台漢文書寫圈的漢字文學史。',
    emoji: '🖋️',
    color: 'amber',
  },
]

for (const b of books) {
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
  status = EXCLUDED.status,
  kind = EXCLUDED.kind
RETURNING slug, title, kind, sort_order;`
  console.log(await runSql(sql))
}
