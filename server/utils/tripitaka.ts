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
  /** 段的唯一鍵。純行號不唯一（全藏 6.5% 的段與別的段同行起頭），
   *  所以同行第二段起加 `.2` 後綴。對照／詞條／DOM anchor 一律用這個。 */
  uid: string;
  /** 引用式 ＝ 大正藏行號，允許重複，只作顯示與引用之用 */
  seg: string;
  juan?: number;
  /** 德格版甘珠爾用的定址：函（vol）＋葉碼（folio）＋行（line）。
   *  葉碼原樣保留不轉數字——全帙有重出葉（33xa／33xb），轉數字就對不回原書。 */
  vol?: number;
  folio?: string;
  line?: number;
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
  /** 該節點起始段的唯一鍵 */
  uid: string;
  juan: number;
}

export interface TripTerm {
  zh: string;
  forms: Record<string, string>;
  uid: string | null;
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

/**
 * 正文的 LRU。
 *
 * 🚨 上限必須按**位元組**算，不能按筆數算。原本寫成「最多留 12 筆」，
 *    在漢文藏經是安全的（一部最多幾 MB），但德格版甘珠爾一部可以到
 *    47 MB JSONL、65,897 段——解析成 JS 物件後單部就上看 150 MB，
 *    12 筆能吃掉 1–2 GB，dev server 實測就是這樣 8 GB 堆用滿當掉。
 *    而且症狀是整個 server 掛掉，不是某一頁壞掉，從頁面上完全看不出根因。
 */
const CACHE_MAX_BYTES = 256 * 1024 * 1024;
const CACHE_MAX_ENTRIES = 24;
const cache = new Map<string, { value: unknown; bytes: number }>();
let cacheBytes = 0;

/** 粗估佔多少記憶體。只要量級對就夠了，不必精確。 */
function roughBytes(v: unknown): number {
  if (typeof v === "string") return v.length * 2 + 16;
  if (Array.isArray(v)) {
    // 逐筆量會把 6.5 萬段掃一遍，抽樣估即可
    const n = v.length;
    if (!n) return 32;
    const step = Math.max(1, Math.floor(n / 50));
    let sample = 0;
    let taken = 0;
    for (let i = 0; i < n; i += step) { sample += roughBytes(v[i]); taken++; }
    return (sample / taken) * n + 32;
  }
  if (v && typeof v === "object") {
    let t = 40;
    for (const [k, val] of Object.entries(v as Record<string, unknown>)) {
      t += k.length * 2 + 24 + roughBytes(val);
    }
    return t;
  }
  return 16;
}

function cacheGet<T>(key: string): T | undefined {
  const e = cache.get(key);
  if (!e) return undefined;
  cache.delete(key);
  cache.set(key, e); // 移到最新
  return e.value as T;
}

function cachePut(key: string, value: unknown) {
  const old = cache.get(key);
  if (old) cacheBytes -= old.bytes;
  const bytes = roughBytes(value);
  cache.set(key, { value, bytes });
  cacheBytes += bytes;
  while (cache.size > 1 && (cacheBytes > CACHE_MAX_BYTES || cache.size > CACHE_MAX_ENTRIES)) {
    const oldest = cache.keys().next().value as string;
    cacheBytes -= cache.get(oldest)!.bytes;
    cache.delete(oldest);
  }
}

/** 作品 id 只允許 CBETA 的形狀，擋掉路徑穿越。 */
/**
 * 作品代號的白名單。這個函式同時是**路徑注入的唯一防線**（代號會直接拼成
 * 檔名去讀 Drive 與 R2），所以只放行已知的四種藏經代號，不要放寬成通配。
 *
 *   T0262 / T0220a / T1005A   大正藏（分卷用小寫 a–p 或大寫 A–F）
 *   X0001                     卍新纂續藏
 *   N01n0001                  漢譯南傳（冊號 ＋ 經號）
 *   DKtoh0113 / DKtoh0539a    德格版甘珠爾（Toh 編號，後綴本小寫）
 *   DKkarchag                 德格版甘珠爾的目錄冊，沒有 Toh 號
 *
 * 🚨 2026-09-16 修：原本只寫 `T…|N…`，**卍續藏那 1,230 部全部打不開**
 *    （`/api/tripitaka/work?id=X0001` 一律回 400 invalid work id）。
 *    症狀在首頁完全看不出來——目錄照樣列出 1,230 部、字數統計照樣有，
 *    只有點進去才會壞。加代號時務必連這裡一起改，並補測試。
 */
export function isValidWorkId(id: string): boolean {
  return /^(?:[TX]\d{4}[A-Za-z]?|N\d{2}n\d{4}[A-Za-z]?|DK(?:toh\d{4}[a-z]?|karchag))$/
    .test(id);
}

/** 甘珠爾一頁最多幾行。單函最多 5,737 行、110 萬字（Toh 8 第 24 函），
 *  整函一次送瀏覽器會卡住，所以函底下再按葉碼切段。 */
export const DK_PAGE_LINES = 1200;

export interface DkPage {
  key: string;
  label: string;
  vol: number;
  from: string;
  to: string;
  n: number;
  /** 這一頁在整部段落陣列裡的起點與長度。存下來，切片時不要再回頭推算
   *  ——葉碼會重出（33xa／33xb），照葉碼找起點會找錯。 */
  start: number;
  count: number;
}

/**
 * 甘珠爾的分頁 —— 藏文佛典沒有「卷」，定址單位是**函＋葉碼**。
 *
 * 先按函分，函內再按 DK_PAGE_LINES 切段，每段以起訖葉碼命名
 * （`51:1` → 「第 51 函 1b–42a」）。葉碼原樣保留不轉數字：全帙有重出葉
 * （33xa／33xb 之類），轉成數字就對不回原書。
 */
export function dkPages(segs: TripSegment[]): DkPage[] {
  const out: DkPage[] = [];
  let start = 0;
  let vol: number | null = null;
  const flush = (end: number) => {
    if (end <= start || vol == null) return;
    const n = out.filter((p) => p.vol === vol).length + 1;
    out.push({
      key: `${vol}:${n}`,
      label: `${segs[start].folio ?? ""}–${segs[end - 1].folio ?? ""}`,
      vol,
      from: segs[start].folio ?? "",
      to: segs[end - 1].folio ?? "",
      n,
      start,
      count: end - start,
    });
    start = end;
  };
  for (let i = 0; i < segs.length; i++) {
    if (segs[i].vol !== vol) {
      flush(i);
      vol = segs[i].vol ?? null;
      start = i;
    } else if (i - start >= DK_PAGE_LINES) {
      flush(i);
    }
  }
  flush(segs.length);
  return out;
}

/** 某一頁包含哪些段。頁鍵不認得時回空陣列而不是整部 —— 整部會拖垮瀏覽器。 */
export function dkSlice(segs: TripSegment[], pages: DkPage[], key: string): TripSegment[] {
  const p = pages.find((x) => x.key === key);
  return p ? segs.slice(p.start, p.start + p.count) : [];
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

/** 現代繁中白話（本站自譯）。段 uid → 白話。
 *  另存一檔而不寫進正文 JSONL：正文是 CBETA 的原始資料、白話是本站產物，
 *  兩者分開才好各自重建。讀取時再併進該段的 sources.zh-mod。 */
export async function loadVernacular(workId: string): Promise<Record<string, string>> {
  if (!isValidWorkId(workId)) return {};
  const key = `zhmod:${workId}`;
  const hit = cacheGet<Record<string, string>>(key);
  if (hit) return hit;
  const raw = await readFile(`${workId}.zhmod.json`);
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
