/**
 * Apply episcopal succession SQL files to Supabase in dependency order.
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
  "database/episcopal-sees.sql",
  "database/episcopal-succession.sql",
  "database/episcopal-sees-seed.sql",
  "database/episcopal-succession-seed.sql",
  "database/episcopal-succession-schisms.sql",
  "database/episcopal-sees-autocephalous.sql",
  "database/episcopal-succession-primates.sql",
  "database/episcopal-succession-primates-oriental.sql",
  "database/episcopal-sees-latin.sql",
  "database/episcopal-succession-canterbury.sql",
  "database/episcopal-succession-york.sql",
  "database/episcopal-succession-latin-sees.sql",
  "database/episcopal-succession-anglican-provinces.sql",
  "database/episcopal-succession-protestant.sql",
  "database/episcopal-sees-catholic-europe.sql",
  "database/episcopal-sees-catholic-global.sql",
  "database/episcopal-succession-gniezno-esztergom.sql",
  "database/episcopal-succession-catholic-americas.sql",
  "database/episcopal-succession-catholic-asia-africa.sql",
];

for (const file of files) {
  const sqlPath = path.join(process.cwd(), file);
  const query = fs.readFileSync(sqlPath, "utf8");
  process.stdout.write(`Applying ${file} ... `);
  const res = await fetch(endpoint, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  const txt = await res.text();
  if (!res.ok) {
    console.error(`FAILED:\n${txt}`);
    process.exit(1);
  }
  console.log("OK");
}

console.log("All files applied successfully.");
