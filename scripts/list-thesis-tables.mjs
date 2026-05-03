// 一次性掃描：列出所有 public schema 的 table，並針對 thesis/論文/口述 相關表打印筆數
import 'dotenv/config';
import { createClient } from '@supabase/supabase-js';

const url = process.env.SUPABASE_URL;
const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_KEY;
if (!url || !key) {
  console.error('SUPABASE_URL / SERVICE_ROLE_KEY missing');
  process.exit(1);
}

// Supabase REST 暴露 information_schema 受限，改用 PostgREST 的 OpenAPI spec 取得 table 清單
const res = await fetch(`${url}/rest/v1/`, {
  headers: { apikey: key, Authorization: `Bearer ${key}` },
});
const spec = await res.json();
const tables = Object.keys(spec.definitions || {}).sort();

console.log(`# Tables in public schema (${tables.length})`);
for (const t of tables) console.log(' -', t);

const keywords = ['thesis', 'paper', 'dissertation', 'interview', 'oral', '論文', '訪談', '口述', 'conference', 'master', 'bachelor'];
const hits = tables.filter(t => keywords.some(k => t.toLowerCase().includes(k.toLowerCase())));
console.log(`\n# Possible thesis-related tables (${hits.length})`);
for (const t of hits) console.log(' -', t);

console.log('\n# Row counts for hits');
const sb = createClient(url, key);
for (const t of hits) {
  const { count, error } = await sb.from(t).select('*', { count: 'exact', head: true });
  console.log(` - ${t}: ${error ? `ERR ${error.message}` : count}`);
}
