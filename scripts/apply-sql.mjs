/**
 * 跑一份 .sql 到 Supabase（Management API）。
 *
 * 為什麼要有這一支：scripts/ 底下已經有九支 apply-*-schema.mjs，內容除了檔名以外
 * 一模一樣——每次加一個欄位就複製一份，是純粹的重複。這一支收斂成一個泛用入口。
 * psycopg2 直連是 IPv6-only 跑不通的，一律走 Management API
 * （見 [[reference_supabase_management_api]]）。
 *
 *   node scripts/apply-sql.mjs database/lit-review-add-citation-locus.sql
 *   node scripts/apply-sql.mjs <file.sql> --verify "SELECT count(*) FROM foo;"
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
  console.error("Missing SUPABASE_URL or SUPABASE_ACCESS_TOKEN in .env");
  process.exit(1);
}

const args = process.argv.slice(2);
const file = args.find((a) => !a.startsWith("--"));
if (!file) {
  console.error("用法: node scripts/apply-sql.mjs <file.sql> [--verify \"SELECT …\"]");
  process.exit(1);
}
const vi = args.indexOf("--verify");
const verifySql = vi >= 0 ? args[vi + 1] : null;

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
  return text;
}

await runSql(file, fs.readFileSync(path.join(process.cwd(), file), "utf8"));
if (verifySql) console.log("verify:", await runSql("--verify", verifySql));
