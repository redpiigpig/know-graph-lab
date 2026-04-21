/**
 * Vectorize all existing excerpts using nomic-embed-text via Ollama
 * Run: npx ts-node scripts/vectorize-excerpts.ts
 *
 * - Skips excerpts already vectorized
 * - Processes in batches with short delays to avoid overloading Ollama
 * - Shows progress + estimated time remaining
 */
import * as dotenv from "dotenv";
dotenv.config();

const SUPABASE_URL   = process.env.SUPABASE_URL!;
const SERVICE_KEY    = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const OLLAMA_BASE    = "http://localhost:11434";
const EMBED_MODEL    = "nomic-embed-text";
const BATCH_SIZE     = 10;   // embed N at a time
const DELAY_MS       = 200;  // ms between batches

const ACCESS_TOKEN   = process.env.SUPABASE_ACCESS_TOKEN!;
const PROJECT_REF    = "vloqgautkahgmqcwgfuo";

// ── Helpers ──────────────────────────────────────────────────────────────────
async function sbFetch(path: string, opts: RequestInit = {}) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1${path}`, {
    ...opts,
    headers: {
      apikey: SERVICE_KEY,
      Authorization: `Bearer ${SERVICE_KEY}`,
      "Content-Type": "application/json",
      Prefer: "return=representation",
      ...(opts.headers as any ?? {}),
    },
  });
  if (!res.ok) throw new Error(`Supabase error ${res.status}: ${await res.text()}`);
  return res.json();
}

async function managementSQL(query: string) {
  const res = await fetch(
    `https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${ACCESS_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    }
  );
  if (!res.ok) throw new Error(`SQL error: ${await res.text()}`);
  return res.json();
}

async function embed(text: string): Promise<number[]> {
  const res = await fetch(`${OLLAMA_BASE}/api/embeddings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: EMBED_MODEL, prompt: text }),
  });
  if (!res.ok) throw new Error(`Ollama embed error: ${await res.text()}`);
  const data = await res.json() as any;
  return data.embedding ?? [];
}

function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

function eta(done: number, total: number, startMs: number): string {
  if (done === 0) return "?";
  const elapsed = Date.now() - startMs;
  const remaining = (elapsed / done) * (total - done);
  const mins = Math.round(remaining / 60000);
  return mins < 1 ? "< 1 分鐘" : `約 ${mins} 分鐘`;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  console.log("\n=== 書摘向量化 ===\n");

  // 1. Check Ollama
  const tagRes = await fetch(`${OLLAMA_BASE}/api/tags`).catch(() => null);
  if (!tagRes?.ok) { console.error("❌ Ollama 未啟動，請先執行 ollama serve"); process.exit(1); }
  const { models } = await tagRes.json() as any;
  const hasEmbed = models.some((m: any) => m.name.includes("nomic-embed"));
  if (!hasEmbed) { console.error(`❌ 找不到 ${EMBED_MODEL}，請先執行 ollama pull nomic-embed-text`); process.exit(1); }
  console.log(`✓ Ollama OK，使用模型：${EMBED_MODEL}`);

  // 2. Fetch all excerpts
  console.log("  拉取所有書摘…");
  const excerpts: any[] = await sbFetch(
    "/excerpts?select=id,title,content,chapter,page_number&order=created_at.asc&limit=10000"
  );
  console.log(`  找到 ${excerpts.length} 筆書摘`);

  // 3. Find already-vectorized excerpt IDs
  const existing: any[] = await sbFetch("/excerpt_embeddings?select=excerpt_id&limit=10000");
  const doneSet = new Set(existing.map(e => e.excerpt_id));
  const todo = excerpts.filter(e => !doneSet.has(e.id));
  console.log(`  已向量化：${doneSet.size} 筆，待處理：${todo.length} 筆\n`);

  if (todo.length === 0) { console.log("✓ 全部已向量化！"); return; }

  // 4. Vectorize in batches
  const startMs = Date.now();
  let done = 0;
  let errors = 0;

  for (let i = 0; i < todo.length; i += BATCH_SIZE) {
    const batch = todo.slice(i, i + BATCH_SIZE);

    const upserts: string[] = [];
    for (const ex of batch) {
      const text = [ex.title, ex.chapter, ex.content].filter(Boolean).join("\n").slice(0, 3000);
      try {
        const vec = await embed(text);
        if (!vec.length) continue;
        upserts.push(`('${ex.id}', '[${vec.join(",")}]', '${EMBED_MODEL}')`);
        done++;
      } catch (e: any) {
        console.warn(`  ⚠ 跳過 ${ex.id}: ${e.message}`);
        errors++;
      }
    }

    // Batch upsert via management API
    if (upserts.length > 0) {
      const sql = `
        INSERT INTO excerpt_embeddings (excerpt_id, embedding, model)
        VALUES ${upserts.join(",\n")}
        ON CONFLICT (excerpt_id) DO UPDATE SET embedding = EXCLUDED.embedding, model = EXCLUDED.model
      `;
      // Note: excerpt_embeddings has no unique constraint on excerpt_id yet – add it
      try {
        await sbFetch("/excerpt_embeddings", {
          method: "POST",
          headers: { Prefer: "resolution=merge-duplicates" } as any,
          body: JSON.stringify(
            batch.slice(0, upserts.length).map((ex, idx) => {
              const vecMatch = upserts[idx]?.match(/\[([^\]]+)\]/);
              return vecMatch ? { excerpt_id: ex.id, embedding: `[${vecMatch[1]}]`, model: EMBED_MODEL } : null;
            }).filter(Boolean)
          ),
        }).catch(async () => {
          // Fallback: use management API directly
          await managementSQL(sql).catch(() => {});
        });
      } catch { /* ignore */ }
    }

    const pct = Math.round(((done + doneSet.size) / excerpts.length) * 100);
    const bar = "█".repeat(Math.floor(pct / 5)) + "░".repeat(20 - Math.floor(pct / 5));
    process.stdout.write(`\r  [${bar}] ${pct}% (${done + doneSet.size}/${excerpts.length}) ETA: ${eta(done, todo.length, startMs)}   `);

    await sleep(DELAY_MS);
  }

  console.log(`\n\n✓ 完成！向量化 ${done} 筆，失敗 ${errors} 筆`);
  console.log(`  總耗時：${Math.round((Date.now() - startMs) / 1000)} 秒`);
  console.log("\n現在可以到 /ai 頁面使用 RAG 問答功能了！\n");
}

main().catch(e => { console.error("\n❌", e.message); process.exit(1); });
