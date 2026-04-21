/**
 * Vectorize all existing excerpts using nomic-embed-text via Ollama
 * Run: npx ts-node scripts/vectorize-excerpts.ts
 *
 * - Skips excerpts already vectorized
 * - Paginates to get all excerpts (Supabase REST limit is 1000/req)
 * - Stores via Management API SQL to avoid auth issues
 * - Shows progress bar + ETA
 */
import * as dotenv from "dotenv";
dotenv.config();

const SUPABASE_URL  = process.env.SUPABASE_URL!;
const SERVICE_KEY   = process.env.SUPABASE_SERVICE_ROLE_KEY!;
const ACCESS_TOKEN  = process.env.SUPABASE_ACCESS_TOKEN!;
const PROJECT_REF   = "vloqgautkahgmqcwgfuo";
const OLLAMA_BASE   = "http://localhost:11434";
const EMBED_MODEL   = "nomic-embed-text";
const MAX_CHARS     = 1500;  // safe limit for nomic-embed-text
const BATCH_SIZE    = 5;
const DELAY_MS      = 300;

// ── REST helper (read only – service key) ────────────────────────────────────
async function sbGet(path: string): Promise<any[]> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1${path}`, {
    headers: {
      apikey: SERVICE_KEY,
      Authorization: `Bearer ${SERVICE_KEY}`,
      "Content-Type": "application/json",
    },
  });
  if (!res.ok) throw new Error(`GET error ${res.status}: ${await res.text()}`);
  return res.json();
}

// ── Management API (write) ────────────────────────────────────────────────────
async function sqlRun(query: string): Promise<any> {
  const res = await fetch(
    `https://api.supabase.com/v1/projects/${PROJECT_REF}/database/query`,
    {
      method: "POST",
      headers: { Authorization: `Bearer ${ACCESS_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    }
  );
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`SQL error: ${err}`);
  }
  return res.json();
}

// ── Embed ─────────────────────────────────────────────────────────────────────
async function embed(text: string): Promise<number[]> {
  const truncated = text.slice(0, MAX_CHARS);
  const res = await fetch(`${OLLAMA_BASE}/api/embeddings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: EMBED_MODEL, prompt: truncated }),
  });
  if (!res.ok) throw new Error(`Embed error: ${await res.text()}`);
  const data = await res.json() as any;
  return data.embedding ?? [];
}

function sleep(ms: number) { return new Promise(r => setTimeout(r, ms)); }

function etaStr(done: number, total: number, startMs: number): string {
  if (done === 0) return "?";
  const elapsed = Date.now() - startMs;
  const ms = (elapsed / done) * (total - done);
  const mins = Math.ceil(ms / 60000);
  return mins < 1 ? "< 1 min" : `~${mins} min`;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  console.log("\n=== 書摘向量化 (nomic-embed-text) ===\n");

  // Check Ollama
  const tagRes = await fetch(`${OLLAMA_BASE}/api/tags`).catch(() => null);
  if (!tagRes?.ok) { console.error("❌ Ollama 未啟動"); process.exit(1); }
  const { models } = await tagRes.json() as any;
  if (!models.some((m: any) => m.name.includes("nomic-embed"))) {
    console.error("❌ 找不到 nomic-embed-text，請執行: ollama pull nomic-embed-text");
    process.exit(1);
  }
  console.log("✓ Ollama 就緒");

  // Fetch ALL excerpts (paginate)
  console.log("  拉取所有書摘…");
  const excerpts: any[] = [];
  let offset = 0;
  while (true) {
    const page: any[] = await sbGet(
      `/excerpts?select=id,title,content,chapter&order=created_at.asc&limit=1000&offset=${offset}`
    );
    excerpts.push(...page);
    if (page.length < 1000) break;
    offset += 1000;
  }
  console.log(`  共 ${excerpts.length} 筆書摘`);

  // Find already vectorized
  const existing: any[] = await sbGet("/excerpt_embeddings?select=excerpt_id&limit=10000");
  const done = new Set(existing.map(e => e.excerpt_id));
  const todo = excerpts.filter(e => !done.has(e.id));
  console.log(`  已完成：${done.size}，待向量化：${todo.length}\n`);

  if (todo.length === 0) {
    console.log("✓ 全部已向量化！RAG 已可使用。");
    return;
  }

  const startMs = Date.now();
  let success = 0;
  let skipped = 0;

  for (let i = 0; i < todo.length; i += BATCH_SIZE) {
    const batch = todo.slice(i, i + BATCH_SIZE);
    const inserts: string[] = [];

    for (const ex of batch) {
      const text = [ex.title, ex.chapter, ex.content].filter(Boolean).join("\n");
      try {
        const vec = await embed(text);
        if (!vec.length) { skipped++; continue; }
        // Escape: no Chinese in the SQL string itself, only floats + uuid
        inserts.push(`('${ex.id}', '[${vec.join(",")}]'::vector, '${EMBED_MODEL}')`);
        success++;
      } catch {
        skipped++;
      }
    }

    if (inserts.length > 0) {
      const sql = `
        INSERT INTO excerpt_embeddings (excerpt_id, embedding, model)
        VALUES ${inserts.join(",\n")}
        ON CONFLICT DO NOTHING
      `;
      await sqlRun(sql).catch(e => {
        console.warn(`\n  ⚠ Insert batch failed: ${e.message.slice(0, 80)}`);
      });
    }

    // Progress bar
    const total = done.size + success;
    const pct = Math.round((total / excerpts.length) * 100);
    const bar = "█".repeat(Math.floor(pct / 5)).padEnd(20, "░");
    process.stdout.write(
      `\r  [${bar}] ${pct}%  ${total}/${excerpts.length}  ETA: ${etaStr(success, todo.length, startMs)}   `
    );

    await sleep(DELAY_MS);
  }

  const elapsed = Math.round((Date.now() - startMs) / 1000);
  console.log(`\n\n✓ 完成！成功 ${success} 筆，跳過 ${skipped} 筆，耗時 ${elapsed} 秒`);
  console.log(`  現在可到 /ai 頁面使用書摘問答功能了！\n`);
}

main().catch(e => { console.error("\n❌", e.message); process.exit(1); });
