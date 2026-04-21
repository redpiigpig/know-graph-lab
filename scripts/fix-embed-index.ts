import * as dotenv from "dotenv";
dotenv.config();

const TOKEN = process.env.SUPABASE_ACCESS_TOKEN!;
const REF   = "vloqgautkahgmqcwgfuo";

async function sql(q: string) {
  const r = await fetch(`https://api.supabase.com/v1/projects/${REF}/database/query`, {
    method: "POST",
    headers: { Authorization: `Bearer ${TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query: q }),
  });
  const d = await r.json();
  if (!r.ok) throw new Error(JSON.stringify(d));
  return d;
}

(async () => {
  await sql("CREATE UNIQUE INDEX IF NOT EXISTS excerpt_embeddings_excerpt_id_idx ON excerpt_embeddings(excerpt_id)");
  console.log("✓ Unique index on excerpt_embeddings(excerpt_id) ready");
})().catch(console.error);
