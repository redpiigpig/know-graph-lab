/** Apply database/english-learning.sql to Supabase via Management API. */
import fs from "node:fs";
import path from "node:path";

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
}

await runSql("english-learning.sql", fs.readFileSync(path.join(process.cwd(), "database/english-learning.sql"), "utf8"));

const verify = await fetch(endpoint, {
  method: "POST",
  headers: { "content-type": "application/json", Authorization: `Bearer ${env.SUPABASE_ACCESS_TOKEN}` },
  body: JSON.stringify({ query: `SELECT (SELECT COUNT(*) FROM english_activity) AS activity, (SELECT COUNT(*) FROM english_progress) AS progress, (SELECT COUNT(*) FROM english_scores) AS scores;` }),
});
console.log("Counts:", await verify.json());
