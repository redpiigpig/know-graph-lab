/**
 * 在 writing_projects 新增《當代的大愛道革命》書籍寫作計畫（kind='book'）。
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
// 卡片描述需精簡（/works 卡片 line-clamp 3 行）；詳述放書頁封面/分頁。
const desc = '碩士論文改寫的專書，全方位呈現昭慧法師與性廣法師兩位女性宗教師的思想與實踐——性別平權、社會運動、禪觀修持與宗教對話。'

// upsert by slug；sort_order 取書籍區（kind='book'）最大值 +1
const sql = `
INSERT INTO writing_projects (slug, title, subtitle, description, emoji, color, status, kind, sort_order)
VALUES (
  'mahaprajapati-revolution',
  '當代的大愛道革命',
  '昭慧法師與性廣法師的人間佛教思想與實踐',
  ${q(desc)},
  '🪷', 'rose', '構思中', 'book',
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
RETURNING slug, title, subtitle, kind, sort_order;`

console.log(await runSql(sql))
