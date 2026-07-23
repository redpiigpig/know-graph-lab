/**
 * ebooks 加 collection / quality 欄位，並把 stores/collectedWorks.ts 引用的
 * 全集卷 backfill 成 collection='collected-works'。
 * 用法：node scripts/apply-ebooks-quality-collection.mjs [--dry-run]
 */
import fs from "node:fs";
import path from "node:path";

const DRY = process.argv.includes("--dry-run");

const env = Object.fromEntries(
  fs.readFileSync(path.join(process.cwd(), ".env"), "utf8")
    .split(/\r?\n/).filter((l) => l && !l.startsWith("#"))
    .map((l) => { const i = l.indexOf("="); return [l.slice(0, i), l.slice(i + 1).trim().replace(/^["']|["']$/g, "")]; })
);
const ref = env.SUPABASE_URL.replace("https://", "").split(".")[0];
const endpoint = `https://api.supabase.com/v1/projects/${ref}/database/query`;

async function runSql(name, sql) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json", Authorization: `Bearer ${env.SUPABASE_ACCESS_TOKEN}` },
    body: JSON.stringify({ query: sql }),
  });
  const text = await res.text();
  if (!res.ok) { console.error(`✗ ${name} → ${res.status}`); console.error(text); process.exit(1); }
  console.log(`✓ ${name}`);
  try { return JSON.parse(text); } catch { return text; }
}

const DDL = `
ALTER TABLE ebooks
  ADD COLUMN IF NOT EXISTS collection text DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS quality_score int,
  ADD COLUMN IF NOT EXISTS quality_flags jsonb NOT NULL DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS quality_checked_at timestamptz;
CREATE INDEX IF NOT EXISTS idx_ebooks_collection ON ebooks(collection) WHERE collection IS NOT NULL;
`;

const store = fs.readFileSync(path.join(process.cwd(), "stores/collectedWorks.ts"), "utf8");
const ids = [...new Set([...store.matchAll(/ebookId:\s*['"]([0-9a-f-]{36})['"]/g)].map((m) => m[1]))];
console.log(`stores/collectedWorks.ts 抽出 ${ids.length} 個全集 ebookId`);

if (DRY) {
  console.log(ids.join("\n"));
  process.exit(0);
}

await runSql("DDL: collection + quality 欄位", DDL);

let updated = 0;
for (let i = 0; i < ids.length; i += 100) {
  const batch = ids.slice(i, i + 100);
  const list = batch.map((id) => `'${id}'`).join(",");
  const rows = await runSql(
    `backfill batch ${i / 100 + 1}`,
    `UPDATE ebooks SET collection='collected-works' WHERE id IN (${list}) RETURNING id;`
  );
  updated += Array.isArray(rows) ? rows.length : 0;
}
console.log(`backfill 完成：${updated}/${ids.length} 本在 DB 中被標記（其餘為尚未入庫的 placeholder id）`);

// 命名空間補標：全集確定命名空間但「尚未在 store 連 ebookId」的書。
// 主要救 SBE 東方聖書（有獨立 /sacred-books-east portal、不在 collectedWorks store，
// store-based backfill 永遠標不到）與潘尼卡等尚未連 hub 的卷。命名空間為確定性 id 根。
const NS_COND = `collection IS NULL AND (
  id::text LIKE '22222222%' OR id::text LIKE '33333333%' OR id::text LIKE '55555%'
  OR id::text LIKE 'a0000000%' OR id::text LIKE 'b0000000%' OR id::text LIKE 'c0000000%'
  OR id::text LIKE '70000000%')`;
const nsRows = await runSql(
  "命名空間補標（SBE／潘尼卡等未 store-link 的全集卷）",
  `UPDATE ebooks SET collection='collected-works' WHERE ${NS_COND} RETURNING id;`
);
console.log(`命名空間補標：${Array.isArray(nsRows) ? nsRows.length : 0} 本`);

const verify = await runSql(
  "verify",
  `SELECT count(*) FILTER (WHERE collection='collected-works') AS cw,
          count(*) FILTER (WHERE collection IS NULL) AS library,
          count(*) AS total FROM ebooks;`
);
console.log("Counts:", verify);
