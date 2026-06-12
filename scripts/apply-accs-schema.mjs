/**
 * Apply ACCS commentary schema to Supabase.
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

const file = "database/accs-commentary-schema.sql";
const sql = fs.readFileSync(path.join(process.cwd(), file), "utf8");
await runSql(file, sql);

const verify = await fetch(endpoint, {
  method: "POST",
  headers: { "content-type": "application/json", Authorization: `Bearer ${token}` },
  body: JSON.stringify({
    query: `SELECT COUNT(*) AS rows FROM accs_commentary;`,
  }),
});
console.log("\nVerify:", await verify.json());
