/**
 * 佛教大藏經 /tripitaka —— 逐段全文的讀取器。
 *
 * 全藏 9,788 萬字、101 萬段，這種量體絕不進 Supabase（2026-07 超量鎖站的教訓）。
 * DB 只存 2,554 列目錄，正文一律 file-backed：
 *
 *   1. 記憶體 LRU 命中 → 直接回
 *   2. 本機 `${tripitakaDir}/{id}.jsonl`（Drive 正本，開發機掛著 G: 就走這條）
 *   3. R2 `tripitaka/{id}.jsonl.gz` → 取回 + gunzip（線上）
 *   4. 都沒有 → null
 *
 * 與 server/utils/ebook-chunks.ts 同一套策略，但資料形狀不同：
 * 這裡一段一列、跨語言存在 `sources`，並帶大正藏行號 `seg` 供引用。
 */
import { promises as fs } from "node:fs";
import path from "node:path";
import { gunzipSync } from "node:zlib";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

/** 一段。`seg` 即大正藏行號（T09n0262_p0008a13），本身就是通行引用式。 */
export interface TripSegment {
  i: number;
  seg: string;
  juan?: number;
  /** 目錄樹索引（-1 = 不屬任何卷品）。整串路徑存在 toc，不逐段重複。 */
  d: number;
  kind: "prose" | "verse" | "head" | "byline" | "item";
  /** 語言碼 → 文本。lzh 恆存在；pi/sa/bo/zh-nan/zh-mod 視有無對照而定。 */
  sources: Record<string, string>;
  notes?: { n: string | null; type: string; text: string }[];
}

export interface TripTocNode {
  i: number;
  depth: number;
  type: string;
  head: string;
  n: string | null;
  parent: number;
  seg: string;
  juan: number;
}

export interface TripTerm {
  zh: string;
  forms: Record<string, string>;
  seg: string | null;
  anchor: string | null;
}

const R2_PREFIX = "tripitaka/";

// ── R2 client（延遲建立）────────────────────────────────
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

// ── LRU（一部大經可達數 MB，別無上限地留著）──────────────
const CACHE_MAX = 12;
const cache = new Map<string, unknown>();
function cacheGet<T>(key: string): T | undefined {
  if (!cache.has(key)) return undefined;
  const v = cache.get(key) as T;
  cache.delete(key);
  cache.set(key, v); // 移到最新
  return v;
}
function cachePut(key: string, value: unknown) {
  cache.set(key, value);
  while (cache.size > CACHE_MAX) cache.delete(cache.keys().next().value as string);
}

/** 作品 id 只允許 CBETA 的形狀，擋掉路徑穿越。 */
export function isValidWorkId(id: string): boolean {
  return /^(T\d{4}[A-Za-z]?|N\d{2}n\d{4}[A-Za-z]?)$/.test(id);
}

async function readLocal(name: string): Promise<string | null> {
  const dir = useRuntimeConfig().tripitakaDir as string | undefined;
  if (!dir) return null;
  try {
    return await fs.readFile(path.join(dir, name), "utf-8");
  } catch {
    return null;
  }
}

async function readR2(name: string): Promise<string | null> {
  const s3 = getR2();
  if (!s3) return null;
  const cfg = useRuntimeConfig();
  try {
    const r = await s3.send(
      new GetObjectCommand({ Bucket: cfg.r2Bucket as string, Key: `${R2_PREFIX}${name}.gz` }),
    );
    const buf = Buffer.from(await r.Body!.transformToByteArray());
    return gunzipSync(buf).toString("utf-8");
  } catch {
    return null;
  }
}

async function readFile(name: string): Promise<string | null> {
  return (await readLocal(name)) ?? (await readR2(name));
}

/** 一部經的全部段落。找不到回 null（呼叫端要回 404，不要當成空經）。 */
export async function loadSegments(workId: string): Promise<TripSegment[] | null> {
  if (!isValidWorkId(workId)) return null;
  const key = `seg:${workId}`;
  const hit = cacheGet<TripSegment[]>(key);
  if (hit) return hit;

  const raw = await readFile(`${workId}.jsonl`);
  if (raw === null) return null;
  const segs: TripSegment[] = [];
  for (const line of raw.split("\n")) {
    if (!line.trim()) continue;
    try {
      segs.push(JSON.parse(line));
    } catch {
      /* 壞行跳過：一行壞掉不該讓整部經打不開 */
    }
  }
  cachePut(key, segs);
  return segs;
}

/** 目錄樹（卷／品／經），reader 側欄用。 */
export async function loadToc(
  workId: string,
): Promise<{ meta: Record<string, unknown>; toc: TripTocNode[] } | null> {
  if (!isValidWorkId(workId)) return null;
  const key = `toc:${workId}`;
  const hit = cacheGet<{ meta: Record<string, unknown>; toc: TripTocNode[] }>(key);
  if (hit) return hit;
  const raw = await readFile(`${workId}.toc.json`);
  if (raw === null) return null;
  const parsed = JSON.parse(raw);
  cachePut(key, parsed);
  return parsed;
}

/** CBETA 的漢／梵／巴詞條對照（<cb:tt>）。沒有就回空陣列。 */
export async function loadTerms(workId: string): Promise<TripTerm[]> {
  if (!isValidWorkId(workId)) return [];
  const key = `term:${workId}`;
  const hit = cacheGet<TripTerm[]>(key);
  if (hit) return hit;
  const raw = await readFile(`${workId}.terms.json`);
  const parsed: TripTerm[] = raw === null ? [] : JSON.parse(raw);
  cachePut(key, parsed);
  return parsed;
}

/** 大正藏原註的巴利對應（<cb:div type="equiv-notes">）。 */
export async function loadEquivalents(
  workId: string,
): Promise<{ n: string; ref: string }[]> {
  if (!isValidWorkId(workId)) return [];
  const key = `eq:${workId}`;
  const hit = cacheGet<{ n: string; ref: string }[]>(key);
  if (hit) return hit;
  const raw = await readFile(`${workId}.equiv.json`);
  const parsed = raw === null ? [] : JSON.parse(raw);
  cachePut(key, parsed);
  return parsed;
}

/** 原典全文：段 → 對應的巴／梵／藏原文（一整部經，含各語自身的段 id）。 */
export interface TripOriginal {
  lang: string;
  uid: string;
  ref: string;
  src: string;
  partial: boolean;
  /** [[原文自身的段 id, 文字], …] —— 保留各語言自己的引用座標 */
  lines: [string, string][];
}

export async function loadOriginals(
  workId: string,
): Promise<Record<string, TripOriginal[]>> {
  if (!isValidWorkId(workId)) return {};
  const key = `orig:${workId}`;
  const hit = cacheGet<Record<string, TripOriginal[]>>(key);
  if (hit) return hit;
  const raw = await readFile(`${workId}.orig.json`);
  const parsed = raw === null ? {} : JSON.parse(raw);
  cachePut(key, parsed);
  return parsed;
}

/** 把目錄索引還原成麵包屑（「卷第一 › 觀因緣品第一」）。 */
export function breadcrumb(toc: TripTocNode[], d: number): string[] {
  const out: string[] = [];
  let i = d;
  let guard = 0;
  while (i >= 0 && i < toc.length && guard++ < 32) {
    out.push(toc[i].head);
    i = toc[i].parent;
  }
  return out.reverse();
}
