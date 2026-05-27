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
  source_lang?: string | null;
  source_text?: string | null;
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
// Local-file backed entries record the file mtime so a JSONL re-write
// (e.g. after split_ebook_set or standardize_pdf) invalidates the cache
// without waiting for TTL expiry.
const CACHE_MAX = 20;
const CACHE_TTL_MS = 10 * 60 * 1000; // 10 min
interface CacheEntry { lines: string[]; expires: number; mtimeMs: number | null }
const cache = new Map<string, CacheEntry>();

async function localMtime(ebookId: string): Promise<number | null> {
  try {
    const st = await fs.stat(localPath(ebookId));
    return st.mtimeMs;
  } catch {
    return null;
  }
}

async function cacheGet(id: string): Promise<string[] | null> {
  const e = cache.get(id);
  if (!e) return null;
  if (e.expires < Date.now()) {
    cache.delete(id);
    return null;
  }
  // If local-backed, re-stat the file; invalidate if changed.
  if (e.mtimeMs !== null) {
    const cur = await localMtime(id);
    if (cur !== null && cur !== e.mtimeMs) {
      cache.delete(id);
      return null;
    }
  }
  // touch (LRU): re-insert to move to end
  cache.delete(id);
  cache.set(id, e);
  return e.lines;
}
function cacheSet(id: string, lines: string[], mtimeMs: number | null) {
  if (cache.size >= CACHE_MAX) {
    const oldest = cache.keys().next().value;
    if (oldest) cache.delete(oldest);
  }
  cache.set(id, { lines, expires: Date.now() + CACHE_TTL_MS, mtimeMs });
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
  const cached = await cacheGet(ebookId);
  if (cached) return cached;

  // Try local first (dev), then R2 (production)
  let lines = await loadLocal(ebookId);
  let mtime: number | null = null;
  if (lines) {
    mtime = await localMtime(ebookId);
  } else {
    lines = await loadR2(ebookId);
  }
  if (lines) cacheSet(ebookId, lines, mtime);
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
 *
 * `sections` lists section/subsection headings (### / ####) *inside* the
 * same chunk, with anchor ids matching what `renderMarkdown` emits in the
 * reader. Clicking a section navigates to the chunk and scrolls to the
 * anchor. Top-level entries are still grouped per chunk so "一章一頁"
 * remains the navigation unit.
 */
export interface TocSection {
  anchor_id: string;   // matches reader's `id="sec-{chunk}-{seq}"` on heading
  title: string;
  level: number;       // 3 or 4
}
export interface TocEntry {
  chunk_index: number;
  title: string;
  level: number;
  volume?: string | null;
  sections?: TocSection[];
}

// Front-matter chunks where sub-section anchors are noise rather than
// navigation aid. Their headings tend to be 1-char enumeration markers
// (一/二/三 …) inherited from publisher prefaces bundled into one chunk
// by `consolidate_frontmatter_into_publisher`.
const FRONTMATTER_NO_ANCHORS = new Set([
  "封面", "出版資訊", "出版說明", "目錄", "目　錄", "版權頁", "版權資訊", "扉頁",
  "前言", "引言", "序言", "序", "卷首語", "凡例", "編者按", "編序", "編輯前言",
  "導論", "導言", "緒論", "來自基督教經典電子圖書館",
]);
// Section-title patterns that are pure enumeration markers — never useful
// as TOC anchors. Single CJK digit / arabic-only / 1-3 char roman numeral.
const ENUM_ONLY_RE = /^([一二三四五六七八九十百千]+|[0-9]+|[IVXLC]+|[A-Z]|\d+\.?)$/;
// Generic single-word anchors that show up inside CCEL boilerplate chunks
// (book title page emits `### By` → 「著」, `#### Author Name`, copyright
// notice lines, etc.). These are body-level keywords, not real navigable
// sections — they pollute the TOC's nested-anchor list.
const NOISE_ANCHOR_RE = /^(著|編者|譯者|版權.*|版權所有.*|ANF\d+\.?.*|NPNF\d+.*|出版.*|印刷.*|致謝)/;
// Chunks whose chapter_path is just `第N卷` / `第N編` / `第N部` are volume
// dividers, not navigable chapters. We hide them from the TOC and use them
// to set the `volume` field on the chapters that follow.
const VOLUME_DIVIDER_RE = /^第[一二三四五六七八九十百千]+[卷編冊集篇部]$/;

export async function loadToc(ebookId: string): Promise<TocEntry[]> {
  const lines = await loadLines(ebookId);
  if (!lines) return [];

  // First pass — parse each line into a (chunk_index, raw entry). We still
  // process FRONT-MATTER chunks; the volume rollup + dedupe happens after.
  type Raw = { entry: TocEntry; rawChapterPath: string; skip: boolean };
  const raws: Raw[] = [];
  let inheritedVolume: string | null = null;
  // Track titles we've already emitted at the top level — duplicate
  // "目錄" / "目　錄" chunks appear once per volume in some EPUBs and
  // clutter the sidebar without adding navigation value.
  const seenTitles = new Set<string>();

  for (let i = 0; i < lines.length; i++) {
    try {
      const c = JSON.parse(lines[i]) as ChunkData;
      const content = c.content || "";
      const firstHead = content.match(/^(#{1,4})\s+(.+)$/m);
      const chapterTitle = (c.chapter_path || "").trim();

      // Volume divider — record as inherited volume for subsequent chunks
      // but DON'T emit a TOC entry for it.
      const collapsedChap = chapterTitle.replace(/\s+/g, "");
      if (VOLUME_DIVIDER_RE.test(collapsedChap)) {
        inheritedVolume = collapsedChap;  // e.g. "第一卷"
        raws.push({
          entry: { chunk_index: i, title: chapterTitle, level: 2, volume: inheritedVolume },
          rawChapterPath: chapterTitle,
          skip: true,
        });
        continue;
      }

      // Sub-section headings (### / ####) inside the chunk → anchors.
      // Filter out:
      //  - Enumeration-only titles ("一", "I", "23"); navigation-useless
      //  - The anchor that's the same as chunk's chapter_path itself —
      //    that's the chapter title shown above, NOT a sub-section
      //  - Duplicates within the same chunk (some EPUBs repeat the heading)
      //  - ALL anchors on volume-less chunks: those are front matter
      //    (title pages / book intros) where every H3/H4 is a credit line
      //    or section label that doesn't deserve a nested TOC entry.
      //    (`前尼西亞教父` chunk previously expanded to show 「亞歷山大‧羅
      //    伯茨」「詹姆斯‧唐納森」「修訂並按年代…」 — credit lines, not
      //    navigation.)
      const suppressAnchors = FRONTMATTER_NO_ANCHORS.has(chapterTitle)
        || c.volume == null;
      const sections: TocSection[] = [];
      const seenAnchorTitles = new Set<string>();
      const chapterTitleKey = chapterTitle.replace(/\[\^\d+\]/g, "").replace(/\s+/g, "").trim();
      let seq = 0;
      if (!suppressAnchors) {
        const headingRe = /^(#{2,4})\s+(.+)$/gm;
        let m: RegExpExecArray | null;
        while ((m = headingRe.exec(content)) !== null) {
          const depth = m[1].length;
          const title = m[2].trim();
          if (depth === 2) continue;
          if (depth >= 3) {
            const cleanTitle = title.replace(/\[\^\d+\]/g, "").trim();
            const collapsed = cleanTitle.replace(/\s+/g, "");
            // Drop: enum-only, matches chapter title, already seen, or
            // CCEL boilerplate noise (著/編者/版權.../ANF01.…) — these
            // are body keywords masquerading as h3/h4 headings.
            if (
              !ENUM_ONLY_RE.test(collapsed)
              && !NOISE_ANCHOR_RE.test(collapsed)
              && collapsed !== chapterTitleKey
              && !seenAnchorTitles.has(collapsed)
            ) {
              sections.push({ anchor_id: `sec-${i}-${seq}`, title: cleanTitle, level: depth });
              seenAnchorTitles.add(collapsed);
            }
            seq++;
          }
        }
      }

      // Use the inherited volume if the chunk doesn't already declare one
      // (so the sidebar's `volumes` computed groups chapters by volume).
      // Front-matter chunks (before the first divider) keep volume=null.
      const effectiveVolume = c.volume ?? inheritedVolume;

      // Inline footnote refs `[^N]` from the body sometimes leak into the
      // chapter_path (EPUB chapter heading had a footnote anchor right
      // after the title text). Strip them for clean TOC display — they're
      // still preserved in the body for in-reader navigation.
      const rawTitle = chapterTitle || (firstHead ? firstHead[2].trim() : `第 ${i + 1} 段`);
      const title = rawTitle.replace(/\[\^\d+\]/g, "").trim();

      // Dedupe across the whole book by collapsed title — "目錄"/"目　錄"/
      // "目　　錄" all map to "目錄" and only the first stays in TOC.
      const titleKey = title.replace(/\s+/g, "");
      if (seenTitles.has(titleKey)) {
        raws.push({
          entry: { chunk_index: i, title, level: 2, volume: effectiveVolume },
          rawChapterPath: chapterTitle,
          skip: true,
        });
        continue;
      }
      seenTitles.add(titleKey);

      // Uniform indent for entries inside a volume — without this, the
      // first page of each letter (which usually starts with `### Letter
      // Title`) gets level=3 while subsequent pages start with `#### Ch.X`
      // and get level=4, so 「第1-10章」 and 「第11-20章」 sit at different
      // indents in the sidebar (jarring). Volume entries should all be
      // level 3 (children of the volume bar).
      const inferredLevel = firstHead ? firstHead[1].length : 2;
      const entryLevel = effectiveVolume ? 3 : inferredLevel;
      raws.push({
        entry: {
          chunk_index: i,
          title,
          level: entryLevel,
          volume: effectiveVolume,
          sections: sections.length ? sections : undefined,
        },
        rawChapterPath: chapterTitle,
        skip: false,
      });
    } catch {
      raws.push({
        entry: { chunk_index: i, title: `第 ${i + 1} 段`, level: 2, volume: inheritedVolume },
        rawChapterPath: "",
        skip: false,
      });
    }
  }

  return raws.filter(r => !r.skip).map(r => r.entry);
}
