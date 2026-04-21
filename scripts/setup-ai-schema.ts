/**
 * Set up pgvector extension + AI/ebook tables
 * Run: npx ts-node scripts/setup-ai-schema.ts
 */
import * as dotenv from "dotenv";
dotenv.config();

const ACCESS_TOKEN = process.env.SUPABASE_ACCESS_TOKEN!;
const PROJECT_REF = "vloqgautkahgmqcwgfuo";

async function sql(query: string, label = "") {
  console.log(`  ${label || query.slice(0, 60).replace(/\n/g, " ")}…`);
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
    // Ignore "already exists" errors
    if (err.includes("already exists")) { console.log("    (already exists, skipped)"); return; }
    throw new Error(`SQL Error: ${err}`);
  }
  return res.json();
}

async function main() {
  console.log("\n=== Setting up AI schema ===\n");

  // 1. Enable pgvector
  console.log("1. Enable pgvector extension");
  await sql(`CREATE EXTENSION IF NOT EXISTS vector`, "enable pgvector");

  // 2. Excerpt embeddings table (for RAG over excerpts)
  console.log("\n2. Create excerpt_embeddings table");
  await sql(`
    CREATE TABLE IF NOT EXISTS excerpt_embeddings (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      excerpt_id uuid REFERENCES excerpts(id) ON DELETE CASCADE,
      embedding vector(768),
      model text DEFAULT 'nomic-embed-text',
      created_at timestamptz DEFAULT now()
    )
  `, "create excerpt_embeddings");
  await sql(
    `CREATE INDEX IF NOT EXISTS excerpt_embeddings_idx ON excerpt_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)`,
    "create vector index"
  );

  // 3. Ebooks table
  console.log("\n3. Create ebooks table");
  await sql(`
    CREATE TABLE IF NOT EXISTS ebooks (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      title text NOT NULL,
      author text,
      file_type text CHECK (file_type IN ('pdf', 'epub')),
      file_path text,
      total_pages int,
      category_id uuid REFERENCES book_categories(id) ON DELETE SET NULL,
      book_id uuid REFERENCES books(id) ON DELETE SET NULL,
      created_at timestamptz DEFAULT now()
    )
  `, "create ebooks");

  // 4. Book pages (full text per page)
  console.log("\n4. Create book_pages table");
  await sql(`
    CREATE TABLE IF NOT EXISTS book_pages (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      ebook_id uuid REFERENCES ebooks(id) ON DELETE CASCADE,
      page_number int NOT NULL,
      content text NOT NULL,
      created_at timestamptz DEFAULT now(),
      UNIQUE (ebook_id, page_number)
    )
  `, "create book_pages");

  // 5. Page embeddings (for full-text semantic search)
  console.log("\n5. Create page_embeddings table");
  await sql(`
    CREATE TABLE IF NOT EXISTS page_embeddings (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      page_id uuid REFERENCES book_pages(id) ON DELETE CASCADE,
      embedding vector(768),
      model text DEFAULT 'nomic-embed-text',
      created_at timestamptz DEFAULT now()
    )
  `, "create page_embeddings");
  await sql(
    `CREATE INDEX IF NOT EXISTS page_embeddings_idx ON page_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)`,
    "create page vector index"
  );

  // 6. RPC for similarity search on excerpts
  console.log("\n6. Create similarity search function");
  await sql(`
    CREATE OR REPLACE FUNCTION match_excerpts(
      query_embedding vector(768),
      match_count int DEFAULT 10,
      threshold float DEFAULT 0.3
    )
    RETURNS TABLE (
      excerpt_id uuid,
      similarity float
    )
    LANGUAGE sql STABLE
    AS $$
      SELECT ee.excerpt_id, 1 - (ee.embedding <=> query_embedding) AS similarity
      FROM excerpt_embeddings ee
      WHERE 1 - (ee.embedding <=> query_embedding) > threshold
      ORDER BY similarity DESC
      LIMIT match_count;
    $$
  `, "create match_excerpts function");

  // 7. RPC for similarity search on pages
  await sql(`
    CREATE OR REPLACE FUNCTION match_pages(
      query_embedding vector(768),
      match_count int DEFAULT 10,
      threshold float DEFAULT 0.3
    )
    RETURNS TABLE (
      page_id uuid,
      ebook_id uuid,
      page_number int,
      similarity float
    )
    LANGUAGE sql STABLE
    AS $$
      SELECT bp.id, bp.ebook_id, bp.page_number,
             1 - (pe.embedding <=> query_embedding) AS similarity
      FROM page_embeddings pe
      JOIN book_pages bp ON bp.id = pe.page_id
      WHERE 1 - (pe.embedding <=> query_embedding) > threshold
      ORDER BY similarity DESC
      LIMIT match_count;
    $$
  `, "create match_pages function");

  console.log("\n✓ AI schema setup complete!\n");
}

main().catch(console.error);
