/**
 * Apply database/add-journal-articles.sql via Supabase Management API.
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
const sqlPath = path.join(process.cwd(), "database", "add-journal-articles.sql");
const query = fs.readFileSync(sqlPath, "utf8");

const endpoint = `https://api.supabase.com/v1/projects/${ref}/database/query`;
const res = await fetch(endpoint, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
  body: JSON.stringify({ query }),
});

const txt = await res.text();
if (!res.ok) {
  console.error("Failed:", txt);
  process.exit(1);
}
console.log("OK:", txt.slice(0, 200));
