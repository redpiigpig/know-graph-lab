/** Add per-volume scoping (book_id) to lit_review_entries via Supabase Management API.
 * Idempotent: re-runnable. book_id NOT NULL DEFAULT '' keeps existing paper/book
 * projects working; the unique key becomes (project_slug, book_id, ref_key) so two
 * 創生哲學 卷 can cite the same source without colliding. */
import fs from "node:fs";
import path from "node:path";

const env = Object.fromEntries(
  fs.readFileSync(path.join(process.cwd(), ".env"), "utf8")
    .split(/\r?\n/).filter((l) => l && !l.startsWith("#"))
    .map((l) => { const i = l.indexOf("="); return [l.slice(0, i), l.slice(i + 1).trim().replace(/^["']|["']$/g, "")]; })
);
const ref = env.SUPABASE_URL.replace("https://", "").split(".")[0];
const endpoint = `https://api.supabase.com/v1/projects/${ref}/database/query`;

const SQL = `
ALTER TABLE lit_review_entries ADD COLUMN IF NOT EXISTS book_id TEXT NOT NULL DEFAULT '';

-- drop whatever unique constraint sits exactly on (project_slug, ref_key), by name
DO $$
DECLARE c text;
BEGIN
  SELECT con.conname INTO c
  FROM pg_constraint con
  JOIN pg_class rel ON rel.oid = con.conrelid
  WHERE rel.relname = 'lit_review_entries' AND con.contype = 'u'
    AND (SELECT array_agg(att.attname::text ORDER BY att.attname::text)
         FROM unnest(con.conkey) k
         JOIN pg_attribute att ON att.attrelid = con.conrelid AND att.attnum = k)
        = ARRAY['project_slug','ref_key']::text[];
  IF c IS NOT NULL THEN EXECUTE format('ALTER TABLE lit_review_entries DROP CONSTRAINT %I', c); END IF;
END $$;

ALTER TABLE lit_review_entries DROP CONSTRAINT IF EXISTS lit_review_entries_project_book_ref_key;
ALTER TABLE lit_review_entries
  ADD CONSTRAINT lit_review_entries_project_book_ref_key UNIQUE (project_slug, book_id, ref_key);
`;

async function runSql(name, sql) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json", Authorization: `Bearer ${env.SUPABASE_ACCESS_TOKEN}` },
    body: JSON.stringify({ query: sql }),
  });
  const text = await res.text();
  if (!res.ok) { console.error(`✗ ${name} → ${res.status}`); console.error(text); process.exit(1); }
  console.log(`✓ ${name}`);
}

await runSql("lit_review book_id migration", SQL);

const verify = await fetch(endpoint, {
  method: "POST",
  headers: { "content-type": "application/json", Authorization: `Bearer ${env.SUPABASE_ACCESS_TOKEN}` },
  body: JSON.stringify({ query: `SELECT column_name FROM information_schema.columns WHERE table_name='lit_review_entries' AND column_name='book_id';` }),
});
console.log("book_id column:", await verify.json());
