/**
 * Read full chunk text for ebooks.
 *
 * DB stores only a 200-char preview (Supabase free-tier 500 MB cap). Full text
 * lives in JSONL — locally for dev, on Cloudflare R2 for production.
 *
 * Loader strategy (with simple LRU cache):
 *   1. In-memory cache hit → return immediately
 *   2. Local JSONL at `${ebookChunksDir}/{ebook_id}.jsonl` exists → use it (dev)
 *   3. R2 `ebook-chunks/{ebook_id}.jsonl.gz` → fetch + gunzip (prod)
 *   4. None of the above → null
 */
import { promises as fs } from "node:fs";
import path from "node:path";
import { gunzipSync } from "node:zlib";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

export interface ChunkData {
  chunk_index: number;
  chunk_type: "page" | "chapter" | "section";
  page_number: number | null;
  chapter_path: string | null;
  volume?: string | null;
  format?: "markdown" | "text";
  content: string;
}

// ── R2 client (lazy) ───────────────────────────────────────────
let _r2: S3Client | null = null;
function getR2(): S3Client | null {
  const cfg = useRuntimeConfig();
  if (!cfg.r2Endpoint || !cfg.r2AccessKey || !cfg.r2SecretKey || !cfg.r2Bucket) {
    return null;
  }
  if (_r2) return _r2;
  _r2 = new S3Client({
    region: "auto",
    endpoint: cfg.r2Endpoint as string,
    credentials: {
      accessKeyId: cfg.r2AccessKey as string,
      secretAccessKey: cfg.r2SecretKey as string,
    },
  });
  return _r2;
}

// ── In-memory LRU cache: keyed by ebookId, holds parsed lines ──
// One book averages ~1 MB of JSONL; cap at 20 books (~20 MB peak).
const CACHE_MAX = 20;
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 min
interface CacheEntry { lines: string[]; expires: number }
const cache = new Map<string, CacheEntry>();

function cacheGet(id: string): string[] | null {
  const e = cache.get(id);
  if (!e) return null;
  if (e.expires < Date.now()) {
    cache.delete(id);
    return null;
  }
  // touch (LRU): re-insert to move to end
  cache.delete(id);
  cache.set(id, e);
  return e.lines;
}
function cacheSet(id: string, lines: string[]) {
  if (cache.size >= CACHE_MAX) {
    const oldest = cache.keys().next().value;
    if (oldest) cache.delete(oldest);
  }
  cache.set(id, { lines, expires: Date.now() + CACHE_TTL_MS });
}

// ── Loaders ────────────────────────────────────────────────────
function localPath(ebookId: string): string {
  const dir = useRuntimeConfig().ebookChunksDir as string;
  return path.join(dir, `${ebookId}.jsonl`);
}

async function loadLocal(ebookId: string): Promise<string[] | null> {
  try {
    const raw = await fs.readFile(localPath(ebookId), "utf8");
    return raw.split(/\r?\n/).filter(Boolean);
  } catch (err: any) {
    // Network drives may timeout or have permission issues; fallback to R2 instead of throwing.
    if (err.code !== "ENOENT") {
      console.warn(`[ebook-chunks] local read failed for ${ebookId}:`, err.message ?? err);
    }
    return null;
  }
}

async function loadR2(ebookId: string): Promise<string[] | null> {
  const client = getR2();
  if (!client) return null;
  const cfg = useRuntimeConfig();
  try {
    const res = await client.send(
      new GetObjectCommand({
        Bucket: cfg.r2Bucket as string,
        Key: `ebook-chunks/${ebookId}.jsonl.gz`,
      })
    );
    const body = res.Body;
    if (!body) return null;
    const buffers: Buffer[] = [];
    // Body is a Node.js Readable stream in the Nitro runtime
    for await (const chunk of body as AsyncIterable<Uint8Array>) {
      buffers.push(Buffer.from(chunk));
    }
    const gz = Buffer.concat(buffers);
    const raw = gunzipSync(gz).toString("utf8");
    return raw.split(/\r?\n/).filter(Boolean);
  } catch (err: any) {
    if (err.name === "NoSuchKey" || err.$metadata?.httpStatusCode === 404) return null;
    // Checksum validation errors still contain valid data; log but continue
    if (err.message?.includes("checksum")) {
      console.warn(`[ebook-chunks] R2 checksum warning for ${ebookId}, retrying...`);
      return null; // Let it retry from local
    }
    console.error(`[ebook-chunks] R2 fetch failed for ${ebookId}:`, err.message ?? err);
    return null;
  }
}

async function loadLines(ebookId: string): Promise<string[] | null> {
  const cached = cacheGet(ebookId);
  if (cached) return cached;

  // Try local first (dev), then R2 (production)
  let lines = await loadLocal(ebookId);
  if (!lines) lines = await loadR2(ebookId);
  if (lines) cacheSet(ebookId, lines);
  return lines;
}

// ── Public API ─────────────────────────────────────────────────
export async function loadChunk(
  ebookId: string,
  chunkIndex: number
): Promise<ChunkData | null> {
  const lines = await loadLines(ebookId);
  if (!lines) return null;
  const line = lines[chunkIndex];
  if (!line) return null;
  try {
    return JSON.parse(line) as ChunkData;
  } catch {
    return null;
  }
}

export async function loadChunksByIndices(
  ebookId: string,
  indices: number[]
): Promise<Map<number, ChunkData>> {
  const out = new Map<number, ChunkData>();
  if (!indices.length) return out;
  const lines = await loadLines(ebookId);
  if (!lines) return out;
  for (const i of new Set(indices)) {
    const line = lines[i];
    if (!line) continue;
    try {
      out.set(i, JSON.parse(line) as ChunkData);
    } catch {
      /* skip */
    }
  }
  return out;
}

export async function chunksExist(ebookId: string): Promise<boolean> {
  const lines = await loadLines(ebookId);
  return !!lines && lines.length > 0;
}

/**
 * TOC entry for sidebar nav. Level is derived from the first heading in
 * the chunk's markdown content (## → 2, ### → 3, #### → 4). Falls back
 * to chapter_path metadata when content has no heading (e.g. cover page).
 */
export interface TocEntry {
  chunk_index: number;
  title: string;
  level: number;
  volume?: string | null;
}

export async function loadToc(ebookId: string): Promise<TocEntry[]> {
  const lines = await loadLines(ebookId);
  if (!lines) return [];
  const out: TocEntry[] = [];
  for (let i = 0; i < lines.length; i++) {
    try {
      const c = JSON.parse(lines[i]) as ChunkData;
      const head = (c.content || "").match(/^(#{1,4})\s+(.+)$/m);
      out.push({
        chunk_index: i,
        title: head ? head[2].trim() : (c.chapter_path || `第 ${i + 1} 段`),
        level: head ? head[1].length : 2,
        volume: c.volume ?? null,
      });
    } catch {
      out.push({ chunk_index: i, title: `第 ${i + 1} 段`, level: 2, volume: null });
    }
  }
  return out;
}
