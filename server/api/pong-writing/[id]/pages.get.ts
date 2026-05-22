/**
 * Return structured pages JSONL for a thesis writing.
 *
 * Loads from R2 (pong-writings-pages/{slug}.jsonl.gz), gunzips, parses each
 * line as a {page, blocks} entry, returns as a JSON array. Mirrors the
 * ebook-chunks loader pattern but with its own cache + R2 prefix.
 */
import { gunzipSync } from "node:zlib";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { createClient } from "@supabase/supabase-js";

let _r2: S3Client | null = null;
function getR2() {
  if (_r2) return _r2;
  const cfg = useRuntimeConfig();
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

// In-memory cache: { writing_id: { pages, expires } }
const CACHE_TTL_MS = 10 * 60 * 1000;
const CACHE_MAX = 10;
type CacheEntry = { pages: any[]; expires: number };
const cache = new Map<string, CacheEntry>();

function cacheGet(id: string) {
  const e = cache.get(id);
  if (!e) return null;
  if (e.expires < Date.now()) {
    cache.delete(id);
    return null;
  }
  cache.delete(id);
  cache.set(id, e);
  return e.pages;
}
function cacheSet(id: string, pages: any[]) {
  if (cache.size >= CACHE_MAX) {
    const oldest = cache.keys().next().value;
    if (oldest) cache.delete(oldest);
  }
  cache.set(id, { pages, expires: Date.now() + CACHE_TTL_MS });
}

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id") as string;

  const cached = cacheGet(id);
  if (cached) return cached;

  const cfg = useRuntimeConfig();
  const supabase = createClient(
    cfg.public.supabaseUrl as string,
    cfg.supabaseServiceRoleKey as string
  );

  const { data, error } = await supabase
    .from("pong_writings")
    .select("pages_r2_key, is_published")
    .eq("id", id)
    .single();

  if (error || !data) {
    throw createError({ statusCode: 404, message: "找不到此篇文章" });
  }
  if (!data.is_published) {
    throw createError({ statusCode: 404, message: "此篇文章未公開" });
  }
  if (!data.pages_r2_key) {
    throw createError({ statusCode: 404, message: "本篇文章沒有結構化 pages" });
  }

  const r2 = getR2();
  let res;
  try {
    res = await r2.send(
      new GetObjectCommand({
        Bucket: cfg.r2Bucket as string,
        Key: data.pages_r2_key,
      })
    );
  } catch (err: any) {
    if (err.name === "NoSuchKey" || err.$metadata?.httpStatusCode === 404) {
      throw createError({ statusCode: 404, message: "pages 不存在於儲存區" });
    }
    throw createError({ statusCode: 502, message: "R2 fetch failed: " + (err.message || err) });
  }

  const body = res.Body;
  if (!body) {
    throw createError({ statusCode: 502, message: "R2 returned empty body" });
  }
  const buffers: Buffer[] = [];
  for await (const chunk of body as AsyncIterable<Uint8Array>) {
    buffers.push(Buffer.from(chunk));
  }
  const raw = gunzipSync(Buffer.concat(buffers)).toString("utf8");

  const pages: any[] = [];
  for (const line of raw.split(/\r?\n/)) {
    const s = line.trim();
    if (!s) continue;
    try {
      pages.push(JSON.parse(s));
    } catch {
      /* skip malformed line */
    }
  }
  pages.sort((a, b) => (a.page ?? 0) - (b.page ?? 0));
  cacheSet(id, pages);
  return pages;
});
