/**
 * Apply Bible schema + seed data to Supabase.
 * Requires SUPABASE_URL and SUPABASE_ACCESS_TOKEN in .env
 */
import fs from "node:fs";
import path from "node:path";

const envPath = path.join(process.cwd(), ".env");
const env = Object.fromEntries(
  fs
    .readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .filter((l) => l && !l.startsWith("#"))
    .map((l) => {
      const i = l.indexOf("=");
      return [l.slice(0, i), l.slice(i + 1).trim().replace(/^["']|["']$/g, "")];
    })
);

const url = env.SUPABASE_URL;
const token = env.SUPABASE_ACCESS_TOKEN;
if (!url || !token) {
  console.error("Missing SUPABASE_URL or SUPABASE_ACCESS_TOKEN");
  process.exit(1);
}

const ref = url.replace("https://", "").split(".")[0];
const endpoint = `https://api.supabase.com/v1/projects/${ref}/database/query`;

const files = [
  "database/bible-schema.sql",
  "database/bible-versions-seed.sql",
  "database/bible-books-seed.sql",
];

async function runSql(name, sql) {
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ query: sql }),
  });
  const text = await res.text();
  if (!res.ok) {
    console.error(`✗ ${name} → ${res.status} ${res.statusText}`);
    console.error(text);
    process.exit(1);
  }
  console.log(`✓ ${name}`);
}

for (const file of files) {
  const sql = fs.readFileSync(path.join(process.cwd(), file), "utf8");
  await runSql(file, sql);
}

// Verification
const verify = await fetch(endpoint, {
  method: "POST",
  headers: { "content-type": "application/json", Authorization: `Bearer ${token}` },
  body: JSON.stringify({
    query: `
      SELECT
        (SELECT COUNT(*) FROM bible_books) AS books,
        (SELECT COUNT(*) FROM bible_versions) AS versions,
        (SELECT COUNT(*) FROM bible_books WHERE canon_protestant) AS canon_prot,
        (SELECT COUNT(*) FROM bible_books WHERE canon_catholic) AS canon_cath,
        (SELECT COUNT(*) FROM bible_books WHERE canon_orthodox) AS canon_orth,
        (SELECT COUNT(*) FROM bible_books WHERE canon_ethiopian) AS canon_eth,
        (SELECT COUNT(*) FROM bible_books WHERE canon_syriac) AS canon_syr;
    `,
  }),
});
const verifyJson = await verify.json();
console.log("\nCounts:", verifyJson);
