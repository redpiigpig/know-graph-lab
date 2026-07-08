/**
 * 聖經經文讀取（bible_verses 已於 2026-07-08 搬出 Supabase — DB 超量救援）。
 *
 * 852K 節 × 33 版本改存每卷一檔的 gz JSON（同 ebook-chunks hybrid 架構）：
 *   - Drive canonical: G:/我的雲端硬碟/資料/聖經/_verses/{book}.json.gz（dev 本機讀）
 *   - R2: bible-verses/{book}.json.gz（production 讀）
 *
 * 檔案格式：{ book_code, chapters: { "1": [{ v: 1, t: { cuv2010: "…", … } }] } }
 * 匯出/上傳/覆核腳本：scripts/offload_bible_verses.py
 */
import { promises as fs } from "node:fs";
import path from "node:path";
import { gunzipSync } from "node:zlib";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

export interface BibleVerseEntry {
  v: number;
  t: Record<string, string>; // version_code → text
}
export interface BibleBookDoc {
  book_code: string;
  chapters: Record<string, BibleVerseEntry[]>;
}

let _r2: S3Client | null = null;
function getR2(): S3Client | null {
  const cfg = useRuntimeConfig();
  if (!cfg.r2Endpoint || !cfg.r2AccessKey || !cfg.r2SecretKey || !cfg.r2Bucket) return null;
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

// 每卷解析後 ~1-4MB；上限 12 卷（讀經通常停留在少數幾卷）
const CACHE_MAX = 12;
const CACHE_TTL_MS = 30 * 60 * 1000;
interface CacheEntry { doc: BibleBookDoc; expires: number }
const cache = new Map<string, CacheEntry>();

function localDir(): string {
  return (useRuntimeConfig().bibleVersesDir as string) ||
    "G:/我的雲端硬碟/資料/聖經/_verses";
}

async function loadLocal(book: string): Promise<BibleBookDoc | null> {
  try {
    const gz = await fs.readFile(path.join(localDir(), `${book}.json.gz`));
    return JSON.parse(gunzipSync(gz).toString("utf8"));
  } catch {
    return null;
  }
}

async function loadR2(book: string): Promise<BibleBookDoc | null> {
  const client = getR2();
  if (!client) return null;
  const cfg = useRuntimeConfig();
  try {
    const res = await client.send(new GetObjectCommand({
      Bucket: cfg.r2Bucket as string,
      Key: `bible-verses/${book}.json.gz`,
    }));
    if (!res.Body) return null;
    const buffers: Buffer[] = [];
    for await (const chunk of res.Body as AsyncIterable<Uint8Array>) {
      buffers.push(Buffer.from(chunk));
    }
    return JSON.parse(gunzipSync(Buffer.concat(buffers)).toString("utf8"));
  } catch (err: any) {
    if (err.name === "NoSuchKey" || err.$metadata?.httpStatusCode === 404) return null;
    console.error(`[bible-verses] R2 fetch failed for ${book}:`, err.message ?? err);
    return null;
  }
}

/** 讀一卷（LRU + local-first → R2）。查無此卷回 null。 */
export async function loadBibleBook(bookCode: string): Promise<BibleBookDoc | null> {
  const key = bookCode.toLowerCase();
  const hit = cache.get(key);
  if (hit && hit.expires > Date.now()) {
    cache.delete(key);
    cache.set(key, hit); // LRU touch
    return hit.doc;
  }
  const doc = (await loadLocal(key)) ?? (await loadR2(key));
  if (doc) {
    if (cache.size >= CACHE_MAX) {
      const oldest = cache.keys().next().value;
      if (oldest) cache.delete(oldest);
    }
    cache.set(key, { doc, expires: Date.now() + CACHE_TTL_MS });
  }
  return doc;
}

/** 搜尋用：逐卷載入但不佔 LRU（避免全庫掃描把閱讀快取洗掉）。 */
export async function loadBibleBookUncached(bookCode: string): Promise<BibleBookDoc | null> {
  const key = bookCode.toLowerCase();
  const hit = cache.get(key);
  if (hit && hit.expires > Date.now()) return hit.doc;
  return (await loadLocal(key)) ?? (await loadR2(key));
}
