#!/usr/bin/env node
/**
 * Read-only perceptual duplicate audit for the Chenwei photo library.
 *
 * Inputs:
 *   - scripts/photo_index.json (metadata only)
 *   - existing 480 px WebP thumbnails in .cache/thumbs/
 *   - missing 480 px thumbnails fetched read-only from configured R2
 *
 * Outputs (default under .cache/photo-duplicate-audit/):
 *   - *.json          structured candidate report
 *   - *.csv           candidate pairs
 *   - *.missing.csv   files that could not be fingerprinted
 *   - *.stale-thumbnails.csv cached thumbnails that disagree with originals
 *   - *.source-index.json exact photo-index snapshot used by the audit
 *   - fingerprints.v1.jsonl checkpoint, so interrupted/rerun audits resume
 *
 * The script reads current originals only for candidate validation; it never
 * moves, renames, writes, or deletes them. R2 access uses GetObject only.
 * Fetched thumbnails are atomically cached locally.
 *
 * Candidate generation is sub-quadratic in normal use: pHash+dHash signatures
 * are searched with a BK-tree under Hamming distance, then filtered by separate
 * pHash/dHash, aspect, brightness, and average-colour limits. Output is always a
 * review list, never an automatic deletion decision.
 *
 * Examples:
 *   node scripts/audit_chenwei_photo_duplicates.mjs --limit=300 --no-r2
 *   node scripts/audit_chenwei_photo_duplicates.mjs --years=2025,2026
 *   node scripts/audit_chenwei_photo_duplicates.mjs
 */

import crypto from "node:crypto";
import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";
import sharp from "sharp";
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(SCRIPT_DIR, "..");
const DEFAULT_INDEX = path.join(REPO, "scripts", "photo_index.json");
const DEFAULT_CACHE_ROOT = path.join(REPO, ".cache", "thumbs");
const DEFAULT_AUDIT_DIR = path.join(REPO, ".cache", "photo-duplicate-audit");
const DEFAULT_OUT_PREFIX = path.join(DEFAULT_AUDIT_DIR, "chenwei-duplicates");
const DEFAULT_CHECKPOINT = path.join(DEFAULT_AUDIT_DIR, "fingerprints.v1.jsonl");
const DEFAULT_PHOTOS_ROOT = "G:/我的雲端硬碟/資料/知識圖工作室/照片/辰瑋相片";
const THUMB_WIDTH = 480;
const THUMB_PREFIX = "photos/thumb/";
const FINGERPRINT_VERSION = "phash16-dhash9-color8-v1";
const R2_THUMB_EXTS = new Set([".jpg", ".jpeg", ".png", ".webp", ".avif", ".bmp"]);

function usage() {
  console.log(`Read-only Chenwei perceptual duplicate audit

Usage:
  node scripts/audit_chenwei_photo_duplicates.mjs [options]

Options:
  --index=PATH                 photo_index.json path
  --cache-root=PATH            480px thumbnail cache root
  --photos-root=PATH           current Chenwei original-photo root
  --out-prefix=PATH            output prefix (writes .json/.csv/.missing.csv)
  --checkpoint=PATH            resumable fingerprint JSONL
  --years=YYYY,YYYY            restrict years
  --buckets=NAME,NAME          restrict exact bucket keys
  --limit=N                    process first N selected images (0 = all)
  --concurrency=N              bounded thumbnail workers (default 6)
  --r2-timeout-ms=N            per-thumbnail R2 read timeout (default 30000)
  --original-concurrency=N     bounded current-original validators (default 2)
  --original-timeout-ms=N      per-original Drive read timeout (default 60000)
  --progress-every=N           progress interval (default 250)
  --phash-distance=N           maximum pHash Hamming distance (default 8)
  --dhash-distance=N           maximum dHash Hamming distance (default 10)
  --total-distance=N           maximum pHash+dHash distance (default 14)
  --aspect-delta=RATIO         relative aspect-ratio difference (default 0.04)
  --brightness-delta=N         grayscale mean difference 0..255 (default 32)
  --color-distance=N           average RGB Euclidean distance (default 48)
  --max-neighbors=N            near matches retained per fingerprint group (default 10)
  --stale-phash-distance=N     cached-vs-current pHash limit (default 4)
  --stale-dhash-distance=N     cached-vs-current dHash limit (default 6)
  --stale-aspect-delta=RATIO   cached-vs-current aspect limit (default 0.02)
  --stale-brightness-delta=N   cached-vs-current brightness limit (default 20)
  --stale-color-distance=N     cached-vs-current RGB limit (default 28)
  --no-r2                      do not fetch missing thumbnails from R2
  --no-cache-fetched           do not save R2 thumbnails into local cache
  --no-checkpoint              do not load or append fingerprint checkpoint
  --candidate-plan-only        stop after candidate generation (no reports)
  --help                       show this help

Safety:
  Original photos and R2 objects are never changed. Cached thumbnails generate
  candidates only. Every reported pair is rechecked against current originals,
  and the script never recommends deletion automatically.`);
}

function parseInteger(value, name, { min = 0, max = Number.MAX_SAFE_INTEGER } = {}) {
  const n = Number(value);
  if (!Number.isInteger(n) || n < min || n > max) {
    throw new Error(`${name} must be an integer in ${min}..${max}`);
  }
  return n;
}

function parseNumber(value, name, { min = 0, max = Number.MAX_VALUE } = {}) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < min || n > max) {
    throw new Error(`${name} must be a number in ${min}..${max}`);
  }
  return n;
}

function parseArgs(argv) {
  const opts = {
    index: DEFAULT_INDEX,
    cacheRoot: DEFAULT_CACHE_ROOT,
    photosRoot: DEFAULT_PHOTOS_ROOT,
    outPrefix: DEFAULT_OUT_PREFIX,
    checkpoint: DEFAULT_CHECKPOINT,
    years: null,
    buckets: null,
    limit: 0,
    concurrency: 6,
    r2TimeoutMs: 30_000,
    originalConcurrency: 2,
    originalTimeoutMs: 60_000,
    progressEvery: 250,
    pHashDistance: 8,
    dHashDistance: 10,
    totalDistance: 14,
    aspectDelta: 0.04,
    brightnessDelta: 32,
    colorDistance: 48,
    maxNeighbors: 10,
    stalePHashDistance: 4,
    staleDHashDistance: 6,
    staleAspectDelta: 0.02,
    staleBrightnessDelta: 20,
    staleColorDistance: 28,
    useR2: true,
    cacheFetched: true,
    useCheckpoint: true,
    candidatePlanOnly: false,
  };

  for (const arg of argv) {
    if (arg === "--help" || arg === "-h") return { ...opts, help: true };
    if (arg === "--no-r2") { opts.useR2 = false; continue; }
    if (arg === "--no-cache-fetched") { opts.cacheFetched = false; continue; }
    if (arg === "--no-checkpoint") { opts.useCheckpoint = false; continue; }
    if (arg === "--candidate-plan-only") { opts.candidatePlanOnly = true; continue; }
    const [name, ...rest] = arg.split("=");
    const value = rest.join("=");
    if (!name.startsWith("--") || !value) throw new Error(`Unknown or incomplete option: ${arg}`);
    if (name === "--index") opts.index = path.resolve(REPO, value);
    else if (name === "--cache-root") opts.cacheRoot = path.resolve(REPO, value);
    else if (name === "--photos-root") opts.photosRoot = path.resolve(REPO, value);
    else if (name === "--out-prefix") opts.outPrefix = path.resolve(REPO, value);
    else if (name === "--checkpoint") opts.checkpoint = path.resolve(REPO, value);
    else if (name === "--years") opts.years = new Set(value.split(",").map((s) => s.trim()).filter(Boolean));
    else if (name === "--buckets") opts.buckets = new Set(value.split(",").map((s) => s.trim()).filter(Boolean));
    else if (name === "--limit") opts.limit = parseInteger(value, name);
    else if (name === "--concurrency") opts.concurrency = parseInteger(value, name, { min: 1, max: 32 });
    else if (name === "--r2-timeout-ms") opts.r2TimeoutMs = parseInteger(value, name, { min: 1000, max: 300_000 });
    else if (name === "--original-concurrency") opts.originalConcurrency = parseInteger(value, name, { min: 1, max: 8 });
    else if (name === "--original-timeout-ms") opts.originalTimeoutMs = parseInteger(value, name, { min: 1000, max: 300_000 });
    else if (name === "--progress-every") opts.progressEvery = parseInteger(value, name, { min: 1 });
    else if (name === "--phash-distance") opts.pHashDistance = parseInteger(value, name, { max: 64 });
    else if (name === "--dhash-distance") opts.dHashDistance = parseInteger(value, name, { max: 64 });
    else if (name === "--total-distance") opts.totalDistance = parseInteger(value, name, { max: 128 });
    else if (name === "--aspect-delta") opts.aspectDelta = parseNumber(value, name, { max: 2 });
    else if (name === "--brightness-delta") opts.brightnessDelta = parseNumber(value, name, { max: 255 });
    else if (name === "--color-distance") opts.colorDistance = parseNumber(value, name, { max: 442 });
    else if (name === "--max-neighbors") opts.maxNeighbors = parseInteger(value, name, { min: 1, max: 100 });
    else if (name === "--stale-phash-distance") opts.stalePHashDistance = parseInteger(value, name, { max: 64 });
    else if (name === "--stale-dhash-distance") opts.staleDHashDistance = parseInteger(value, name, { max: 64 });
    else if (name === "--stale-aspect-delta") opts.staleAspectDelta = parseNumber(value, name, { max: 2 });
    else if (name === "--stale-brightness-delta") opts.staleBrightnessDelta = parseNumber(value, name, { max: 255 });
    else if (name === "--stale-color-distance") opts.staleColorDistance = parseNumber(value, name, { max: 442 });
    else throw new Error(`Unknown option: ${name}`);
  }
  return opts;
}

function sha256(data) {
  return crypto.createHash("sha256").update(data).digest("hex");
}

function thumbCacheKey(parts) {
  return sha256(parts.join("|")).slice(0, 32);
}

function cachePath(cacheRoot, key) {
  return path.join(cacheRoot, key.slice(0, 2), `${key}_${THUMB_WIDTH}.webp`);
}

function r2ThumbKey(key) {
  return `${THUMB_PREFIX}${key}_${THUMB_WIDTH}.webp`;
}

function sourceForBucket(bucket) {
  if (bucket === "screenshots") return "screenshot";
  if (bucket === "downloads") return "download";
  if (/^(0[1-9]|1[0-2])$/.test(bucket)) return "photo";
  return "event";
}

function dateInFilename(name) {
  const m = name.match(/(?:^|[^0-9])(20[0-2]\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])(?:[^0-9]|$)/);
  return m ? `${m[1]}-${m[2]}-${m[3]}` : null;
}

function flattenChenwei(index, opts) {
  const lib = index?.libraries?.chenwei;
  if (!lib?.years) throw new Error("Index has no libraries.chenwei.years");
  const out = [];
  let videos = 0;
  for (const year of Object.keys(lib.years).sort()) {
    if (opts.years && !opts.years.has(year)) continue;
    const yd = lib.years[year];
    for (const bucket of Object.keys(yd.buckets ?? {}).sort()) {
      if (opts.buckets && !opts.buckets.has(bucket)) continue;
      for (const file of yd.buckets[bucket] ?? []) {
        if (file.kind !== "image") { videos++; continue; }
        const key = thumbCacheKey(["chenwei", year, bucket, file.name]);
        const mtime = Number(file.mtime) || 0;
        out.push({
          ref: `${year}/${bucket}/${file.name}`,
          year,
          bucket,
          source: sourceForBucket(bucket),
          name: file.name,
          ext: String(file.ext || path.extname(file.name)).toLowerCase(),
          size: Number(file.size) || 0,
          mtime,
          mtimeIso: mtime ? new Date(mtime).toISOString() : null,
          dateInFilename: dateInFilename(file.name),
          cacheKey: key,
          cachePath: cachePath(opts.cacheRoot, key),
          r2Key: r2ThumbKey(key),
        });
      }
    }
  }
  out.sort((a, b) => a.ref.localeCompare(b.ref, undefined, { numeric: true }));
  return { images: opts.limit ? out.slice(0, opts.limit) : out, selectedBeforeLimit: out.length, videos };
}

function loadDotEnv() {
  const values = {};
  try {
    for (const line of fsSync.readFileSync(path.join(REPO, ".env"), "utf8").split(/\r?\n/)) {
      const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
      if (m) values[m[1]] = m[2].trim().replace(/^["']|["']$/g, "");
    }
  } catch { /* .env is optional */ }
  return { ...values, ...process.env };
}

class R2ThumbReader {
  constructor(enabled, timeoutMs) {
    this.enabled = enabled;
    this.timeoutMs = timeoutMs;
    this.client = null;
    this.bucket = null;
    this.disabledReason = enabled ? null : "disabled_by_option";
    this.systemErrors = 0;
  }

  ensureClient() {
    if (!this.enabled || this.disabledReason) return false;
    if (this.client) return true;
    const env = loadDotEnv();
    const endpoint = env.R2_ENDPOINT;
    const accessKeyId = env.R2_ACCESS_KEY;
    const secretAccessKey = env.R2_SECRET_KEY;
    const bucket = env.R2_BUCKET;
    if (!endpoint || !accessKeyId || !secretAccessKey || !bucket) {
      this.disabledReason = "r2_not_configured";
      return false;
    }
    this.bucket = bucket;
    this.client = new S3Client({
      region: "auto",
      endpoint,
      credentials: { accessKeyId, secretAccessKey },
    });
    return true;
  }

  async get(key) {
    if (!this.ensureClient()) return { ok: false, reason: this.disabledReason };
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
    try {
      const res = await this.client.send(
        new GetObjectCommand({ Bucket: this.bucket, Key: key }),
        { abortSignal: controller.signal },
      );
      if (!res.Body) return { ok: false, reason: "r2_empty_body" };
      const bytes = await res.Body.transformToByteArray();
      return { ok: true, buffer: Buffer.from(bytes) };
    } catch (error) {
      const status = Number(error?.$metadata?.httpStatusCode) || 0;
      const name = String(error?.name || "R2Error").replace(/[^A-Za-z0-9_-]/g, "").slice(0, 50);
      if (status === 404 || name === "NoSuchKey" || name === "NotFound") {
        return { ok: false, reason: "r2_not_found" };
      }
      this.systemErrors++;
      // Avoid thousands of repeated credential/network failures. No endpoint,
      // request object, or credential value is ever included in output.
      const reason = `r2_read_error:${name}:http_${status || "unknown"}`;
      if (status === 401 || status === 403 || this.systemErrors >= 3) this.disabledReason = reason;
      return { ok: false, reason };
    } finally {
      clearTimeout(timeout);
    }
  }
}

async function atomicWrite(file, buffer) {
  await fs.mkdir(path.dirname(file), { recursive: true });
  const tmp = `${file}.${process.pid}.${crypto.randomBytes(4).toString("hex")}.tmp`;
  try {
    await fs.writeFile(tmp, buffer);
    await fs.rename(tmp, file);
  } finally {
    await fs.rm(tmp, { force: true }).catch(() => {});
  }
}

const PHASH_N = 16;
const PHASH_LOW = 8;
const COS_TABLE = Array.from({ length: PHASH_LOW }, (_, u) =>
  Float64Array.from({ length: PHASH_N }, (_, x) =>
    Math.cos(((2 * x + 1) * u * Math.PI) / (2 * PHASH_N))),
);

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function bitsToHex(bits) {
  let out = "";
  for (let i = 0; i < bits.length; i += 4) {
    let n = 0;
    for (let j = 0; j < 4; j++) n = (n << 1) | (bits[i + j] ? 1 : 0);
    out += n.toString(16);
  }
  return out;
}

function perceptualHash16(pixels) {
  // Separable 2-D DCT: 16x16 input, low 8x8 coefficients.
  const rowProjection = Array.from({ length: PHASH_N }, () => new Float64Array(PHASH_LOW));
  for (let y = 0; y < PHASH_N; y++) {
    const rowOffset = y * PHASH_N;
    for (let u = 0; u < PHASH_LOW; u++) {
      let sum = 0;
      const cos = COS_TABLE[u];
      for (let x = 0; x < PHASH_N; x++) sum += pixels[rowOffset + x] * cos[x];
      rowProjection[y][u] = sum;
    }
  }
  const coeffs = [];
  for (let v = 0; v < PHASH_LOW; v++) {
    const cosY = COS_TABLE[v];
    for (let u = 0; u < PHASH_LOW; u++) {
      let sum = 0;
      for (let y = 0; y < PHASH_N; y++) sum += rowProjection[y][u] * cosY[y];
      coeffs.push(sum);
    }
  }
  const threshold = median(coeffs.slice(1)); // exclude DC from threshold
  return bitsToHex(coeffs.map((value) => value > threshold));
}

function differenceHash9x8(pixels) {
  const bits = [];
  for (let y = 0; y < 8; y++) {
    const row = y * 9;
    for (let x = 0; x < 8; x++) bits.push(pixels[row + x] > pixels[row + x + 1]);
  }
  return bitsToHex(bits);
}

function meanByte(buffer) {
  let total = 0;
  for (const value of buffer) total += value;
  return total / Math.max(1, buffer.length);
}

function averageRgb(buffer) {
  const sums = [0, 0, 0];
  let count = 0;
  for (let i = 0; i + 2 < buffer.length; i += 3) {
    sums[0] += buffer[i]; sums[1] += buffer[i + 1]; sums[2] += buffer[i + 2]; count++;
  }
  return sums.map((sum) => Math.round((sum / Math.max(1, count)) * 100) / 100);
}

async function fingerprintThumbnail(buffer) {
  const image = sharp(buffer, { failOn: "none", limitInputPixels: 100_000_000 });
  const [meta, pPixels, dPixels, colorPixels] = await Promise.all([
    image.clone().metadata(),
    image.clone().resize(PHASH_N, PHASH_N, { fit: "fill" }).greyscale().raw().toBuffer(),
    image.clone().resize(9, 8, { fit: "fill" }).greyscale().raw().toBuffer(),
    image.clone().resize(8, 8, { fit: "fill" }).removeAlpha().toColourspace("srgb").raw().toBuffer(),
  ]);
  if (!meta.width || !meta.height) throw new Error("thumbnail has no dimensions");
  const aspectRatio = meta.width / meta.height;
  return {
    thumbSha256: sha256(buffer),
    normalizedSha256: sha256(pPixels),
    pHash: perceptualHash16(pPixels),
    dHash: differenceHash9x8(dPixels),
    width: meta.width,
    height: meta.height,
    aspectRatio,
    brightness: Math.round(meanByte(pPixels) * 100) / 100,
    averageRgb: averageRgb(colorPixels),
  };
}

function checkpointKey(item) {
  return `${FINGERPRINT_VERSION}|${item.cacheKey}|${item.size}|${item.mtime}`;
}

async function loadCheckpoint(file) {
  const found = new Map();
  if (!fsSync.existsSync(file)) return found;
  const stream = fsSync.createReadStream(file, { encoding: "utf8" });
  const lines = readline.createInterface({ input: stream, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line);
      if (row.v === FINGERPRINT_VERSION && row.key && row.fingerprint) found.set(row.key, row.fingerprint);
    } catch { /* tolerate an interrupted final line */ }
  }
  return found;
}

class CheckpointWriter {
  constructor(file, enabled) {
    this.file = file;
    this.enabled = enabled;
    this.pending = [];
    this.chain = Promise.resolve();
  }

  append(key, fingerprint) {
    if (!this.enabled) return;
    this.pending.push(JSON.stringify({ v: FINGERPRINT_VERSION, key, fingerprint }));
    if (this.pending.length >= 50) this.flush();
  }

  flush() {
    if (!this.enabled || !this.pending.length) return;
    const text = this.pending.splice(0).join("\n") + "\n";
    this.chain = this.chain.then(async () => {
      await fs.mkdir(path.dirname(this.file), { recursive: true });
      await fs.appendFile(this.file, text, "utf8");
    });
  }

  async close() {
    this.flush();
    await this.chain;
  }
}

async function mapLimit(items, concurrency, handler) {
  const results = new Array(items.length);
  let cursor = 0;
  async function worker() {
    while (true) {
      const index = cursor++;
      if (index >= items.length) return;
      results[index] = await handler(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, () => worker()));
  return results;
}

function safeErrorName(error) {
  return String(error?.name || "Error").replace(/[^A-Za-z0-9_-]/g, "").slice(0, 50);
}

async function collectFingerprints(items, opts, checkpoint, checkpointWriter, r2Reader) {
  const stats = {
    selected: items.length,
    fingerprinted: 0,
    checkpointHits: 0,
    localCacheHits: 0,
    r2Fetches: 0,
    r2CachedLocally: 0,
    missing: 0,
    decodeErrors: 0,
  };
  let completed = 0;

  const results = await mapLimit(items, opts.concurrency, async (item) => {
    const cpKey = checkpointKey(item);
    const previous = opts.useCheckpoint ? checkpoint.get(cpKey) : null;
    let buffer;
    let thumbnailSource;
    if (previous) {
      // A cache key does not include content/mtime. Never trust a checkpoint
      // solely because the logical key matches: re-read the cached WebP and
      // verify its bytes against the fingerprinted thumbnail SHA first.
      try {
        buffer = await fs.readFile(item.cachePath);
        thumbnailSource = "local-cache";
        stats.localCacheHits++;
        if (sha256(buffer) === previous.thumbSha256) {
          stats.checkpointHits++;
          stats.fingerprinted++;
          completed++;
          if (completed % opts.progressEvery === 0 || completed === items.length) printProgress(completed, items.length, stats);
          return { ok: true, item, fingerprint: previous, thumbnailSource: "checkpoint-verified-cache" };
        }
      } catch { /* no current local cache: fetch/recompute below */ }
    }

    if (!buffer) {
      try {
        buffer = await fs.readFile(item.cachePath);
        thumbnailSource = "local-cache";
        stats.localCacheHits++;
      } catch { /* fetch below */ }
    }
    if (!buffer) {
      if (!R2_THUMB_EXTS.has(item.ext)) {
        completed++; stats.missing++;
        if (completed % opts.progressEvery === 0 || completed === items.length) printProgress(completed, items.length, stats);
        return { ok: false, item, reason: "unsupported_extension_without_cached_thumbnail" };
      }
      const fetched = await r2Reader.get(item.r2Key);
      if (!fetched.ok) {
        completed++; stats.missing++;
        if (completed % opts.progressEvery === 0 || completed === items.length) printProgress(completed, items.length, stats);
        return { ok: false, item, reason: fetched.reason };
      }
      buffer = fetched.buffer;
      thumbnailSource = "r2";
      stats.r2Fetches++;
      if (opts.cacheFetched) {
        try {
          await atomicWrite(item.cachePath, buffer);
          stats.r2CachedLocally++;
        } catch {
          // Cache failure does not invalidate the read-only audit result.
        }
      }
    }

    try {
      const fingerprint = await fingerprintThumbnail(buffer);
      checkpointWriter.append(cpKey, fingerprint);
      stats.fingerprinted++;
      completed++;
      if (completed % opts.progressEvery === 0 || completed === items.length) printProgress(completed, items.length, stats);
      return { ok: true, item, fingerprint, thumbnailSource };
    } catch (error) {
      stats.decodeErrors++; stats.missing++; completed++;
      if (completed % opts.progressEvery === 0 || completed === items.length) printProgress(completed, items.length, stats);
      return { ok: false, item, reason: `thumbnail_decode_error:${safeErrorName(error)}` };
    }
  });

  return { results, stats };
}

function printProgress(done, total, stats) {
  console.log(
    `[${done}/${total}] fingerprinted=${stats.fingerprinted} checkpoint=${stats.checkpointHits} ` +
    `local=${stats.localCacheHits} r2=${stats.r2Fetches} missing=${stats.missing}`,
  );
}

function popcount32(value) {
  let x = value >>> 0;
  x -= (x >>> 1) & 0x55555555;
  x = (x & 0x33333333) + ((x >>> 2) & 0x33333333);
  return ((((x + (x >>> 4)) & 0x0f0f0f0f) * 0x01010101) >>> 24);
}

function hex64Words(hex) {
  const h = hex.padStart(16, "0");
  return [Number.parseInt(h.slice(0, 8), 16) >>> 0, Number.parseInt(h.slice(8, 16), 16) >>> 0];
}

function combinedWords(fingerprint) {
  return [...hex64Words(fingerprint.pHash), ...hex64Words(fingerprint.dHash)];
}

function hammingWords(a, b) {
  return popcount32(a[0] ^ b[0]) + popcount32(a[1] ^ b[1]) +
    popcount32(a[2] ^ b[2]) + popcount32(a[3] ^ b[3]);
}

function pHashDistance(a, b) {
  const aw = hex64Words(a), bw = hex64Words(b);
  return popcount32(aw[0] ^ bw[0]) + popcount32(aw[1] ^ bw[1]);
}

function dHashDistance(a, b) {
  return pHashDistance(a, b);
}

class BKTree {
  constructor(distance) {
    this.distance = distance;
    this.root = null;
  }

  insert(value) {
    if (!this.root) {
      this.root = { words: value.words, values: [value], children: new Map() };
      return;
    }
    let node = this.root;
    while (true) {
      const distance = this.distance(value.words, node.words);
      if (distance === 0) { node.values.push(value); return; }
      const child = node.children.get(distance);
      if (child) node = child;
      else {
        node.children.set(distance, { words: value.words, values: [value], children: new Map() });
        return;
      }
    }
  }

  search(words, maxDistance) {
    if (!this.root) return [];
    const out = [];
    const stack = [this.root];
    while (stack.length) {
      const node = stack.pop();
      const distance = this.distance(words, node.words);
      if (distance <= maxDistance) out.push(...node.values);
      const low = distance - maxDistance;
      const high = distance + maxDistance;
      for (const [edge, child] of node.children) {
        if (edge >= low && edge <= high) stack.push(child);
      }
    }
    return out;
  }
}

function relativeAspectDelta(a, b) {
  return Math.abs(a - b) / Math.max(a, b, Number.EPSILON);
}

function rgbDistance(a, b) {
  return Math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2);
}

function sortKeepFirst(a, b) {
  const am = a.item.mtime || Number.MAX_SAFE_INTEGER;
  const bm = b.item.mtime || Number.MAX_SAFE_INTEGER;
  return am - bm || a.item.ref.localeCompare(b.item.ref, undefined, { numeric: true });
}

function publicItem(record) {
  const { item } = record;
  return {
    ref: item.ref,
    year: item.year,
    bucket: item.bucket,
    source: item.source,
    name: item.name,
    ext: item.ext,
    size: item.size,
    mtime: item.mtime,
    mtimeIso: item.mtimeIso,
    dateInFilename: item.dateInFilename,
    cacheKey: item.cacheKey,
  };
}

function groupBy(records, keyFn) {
  const map = new Map();
  for (const record of records) {
    const key = keyFn(record);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(record);
  }
  return map;
}

function buildSignatureGroups(records) {
  const map = groupBy(records, (record) => {
    const fp = record.fingerprint;
    const aspectBucket = Math.round(Math.log(fp.aspectRatio) * 100);
    return `${fp.pHash}:${fp.dHash}:${aspectBucket}`;
  });
  return [...map.entries()].map(([key, members], index) => {
    members.sort(sortKeepFirst);
    const fp = members[0].fingerprint;
    return {
      id: `sig-${String(index + 1).padStart(6, "0")}`,
      key,
      members,
      representative: members[0],
      fingerprint: fp,
      words: combinedWords(fp),
    };
  });
}

function confidenceFor(type, pDistance, dDistance, aspectDelta, colorDistance) {
  if (type === "exact_thumbnail" || type === "normalized_pixels_identical") return "high";
  if (type === "fingerprint_identical" && aspectDelta <= 0.01 && colorDistance <= 18) return "high";
  if (pDistance <= 4 && dDistance <= 5 && aspectDelta <= 0.02 && colorDistance <= 28) return "high";
  if (pDistance <= 6 && dDistance <= 8 && aspectDelta <= 0.03) return "moderate";
  return "review";
}

function makeCandidate(type, leftRecord, rightRecord, metrics, extra = {}) {
  const earliest = [leftRecord, rightRecord].sort(sortKeepFirst)[0];
  return {
    type,
    generationConfidence: confidenceFor(type, metrics.pHashDistance, metrics.dHashDistance,
      metrics.aspectDelta, metrics.colorDistance),
    score: Math.round((metrics.pHashDistance * 2 + metrics.dHashDistance +
      metrics.aspectDelta * 100 + metrics.brightnessDelta / 10 + metrics.colorDistance / 20) * 100) / 100,
    ...metrics,
    left: publicItem(leftRecord),
    right: publicItem(rightRecord),
    earliestIndexMtimeRef: earliest.item.ref,
    earliestIndexMtimeCaveat: "index_mtime_is_not_proof_of_download_or_import_time",
    deletionRecommendation: "none_until_current_original_validation_and_human_review",
    reviewRequired: true,
    ...extra,
  };
}

function pairMetrics(left, right) {
  return fingerprintMetrics(left.fingerprint, right.fingerprint);
}

function fingerprintMetrics(a, b) {
  const pDistance = pHashDistance(a.pHash, b.pHash);
  const dDistance = dHashDistance(a.dHash, b.dHash);
  const aspectDelta = relativeAspectDelta(a.aspectRatio, b.aspectRatio);
  const brightnessDelta = Math.abs(a.brightness - b.brightness);
  const colorDistance = rgbDistance(a.averageRgb, b.averageRgb);
  return {
    pHashDistance: pDistance,
    dHashDistance: dDistance,
    totalHashDistance: pDistance + dDistance,
    aspectDelta: Math.round(aspectDelta * 100000) / 100000,
    brightnessDelta: Math.round(brightnessDelta * 100) / 100,
    colorDistance: Math.round(colorDistance * 100) / 100,
  };
}

function resolveOriginalPath(item, photosRoot) {
  if (path.basename(item.name) !== item.name || item.name === "." || item.name === "..") {
    throw new Error("invalid indexed filename");
  }
  let folder;
  if (/^(0[1-9]|1[0-2])$/.test(item.bucket)) folder = `${item.year}.${item.bucket}`;
  else if (item.bucket === "screenshots") folder = `${item.year}截圖`;
  else if (item.bucket === "downloads") folder = `${item.year}下載`;
  else if (/^(0[1-9]|1[0-2])\//.test(item.bucket)) {
    const [month, ...eventParts] = item.bucket.split("/");
    if (eventParts.length !== 1 || !eventParts[0] || eventParts[0] === "." || eventParts[0] === "..") {
      throw new Error("invalid indexed month event");
    }
    folder = path.join(`${item.year}.${month}`, eventParts[0]);
  } else {
    if (!item.bucket || item.bucket.includes("/") || item.bucket.includes("\\") || item.bucket === "." || item.bucket === "..") {
      throw new Error("invalid indexed event bucket");
    }
    folder = item.bucket;
  }
  const root = path.resolve(photosRoot);
  const resolved = path.resolve(root, `${item.year}相片`, folder, item.name);
  if (!resolved.startsWith(root + path.sep)) throw new Error("indexed path escaped photo root");
  return resolved;
}

async function readCurrentOriginal(record, opts) {
  try {
    if (!record?.item) return { ok: false, record, reason: "current_original_record_missing" };
    const originalPath = resolveOriginalPath(record.item, opts.photosRoot);
    const stat = await fs.stat(originalPath);
    if (!stat.isFile()) return { ok: false, record, reason: "current_original_not_file" };
    // Candidate-only current-original validation: bounded concurrency keeps
    // Drive File Stream and memory pressure under control.
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), opts.originalTimeoutMs);
    let bytes;
    try {
      bytes = await fs.readFile(originalPath, { signal: controller.signal });
    } finally {
      clearTimeout(timeout);
    }
    const originalSha256 = sha256(bytes);
    const freshThumb = await sharp(bytes, { failOn: "none", limitInputPixels: 100_000_000 })
      .rotate()
      .resize(THUMB_WIDTH, null, { fit: "inside", withoutEnlargement: true })
      .webp({ quality: 80 })
      .toBuffer();
    const freshFingerprint = await fingerprintThumbnail(freshThumb);
    const cachedVsCurrent = fingerprintMetrics(record.fingerprint, freshFingerprint);
    const materiallyStale = record.fingerprint.thumbSha256 !== freshFingerprint.thumbSha256 && (
      cachedVsCurrent.pHashDistance > opts.stalePHashDistance ||
      cachedVsCurrent.dHashDistance > opts.staleDHashDistance ||
      cachedVsCurrent.aspectDelta > opts.staleAspectDelta ||
      cachedVsCurrent.brightnessDelta > opts.staleBrightnessDelta ||
      cachedVsCurrent.colorDistance > opts.staleColorDistance
    );
    return {
      ok: true,
      record,
      actualSize: stat.size,
      actualMtime: stat.mtimeMs,
      actualMtimeIso: stat.mtime.toISOString(),
      indexSizeMatches: stat.size === record.item.size,
      indexMtimeMatches: Math.abs(stat.mtimeMs - record.item.mtime) <= 2,
      originalSha256,
      freshFingerprint,
      cachedVsCurrent,
      materiallyStale,
    };
  } catch (error) {
    const code = String(error?.code || safeErrorName(error)).replace(/[^A-Za-z0-9_-]/g, "").slice(0, 50);
    return { ok: false, record, reason: `current_original_read_or_decode_error:${code}` };
  }
}

function originalPairMatches(metrics, opts) {
  return metrics.pHashDistance <= opts.pHashDistance &&
    metrics.dHashDistance <= opts.dHashDistance &&
    metrics.totalHashDistance <= opts.totalDistance &&
    metrics.aspectDelta <= opts.aspectDelta &&
    metrics.brightnessDelta <= opts.brightnessDelta &&
    metrics.colorDistance <= opts.colorDistance;
}

function currentOriginalSummary(result) {
  if (!result?.ok) return { ok: false, reason: result?.reason ?? "not_validated" };
  return {
    ok: true,
    actualSize: result.actualSize,
    actualMtime: result.actualMtime,
    actualMtimeIso: result.actualMtimeIso,
    indexSizeMatches: result.indexSizeMatches,
    indexMtimeMatches: result.indexMtimeMatches,
    originalSha256: result.originalSha256,
    freshThumbnailSha256: result.freshFingerprint.thumbSha256,
    cachedThumbnailMateriallyStale: result.materiallyStale,
    cachedVsCurrent: result.cachedVsCurrent,
  };
}

async function validateCandidatesAgainstCurrentOriginals(candidates, records, opts) {
  const recordByRef = new Map(records.map((record) => [record.item.ref, record]));
  const refs = [...new Set(candidates.flatMap((candidate) => [candidate.left.ref, candidate.right.ref]))].sort();
  let completed = 0;
  console.log(`Validating ${refs.length} candidate-involved current originals (concurrency=${opts.originalConcurrency})...`);
  const results = await mapLimit(refs, opts.originalConcurrency, async (ref) => {
    const result = await readCurrentOriginal(recordByRef.get(ref), opts);
    completed++;
    if (completed % 25 === 0 || completed === refs.length) {
      console.log(`[original ${completed}/${refs.length}] current files decoded and hashed`);
    }
    return result;
  });
  const byRef = new Map(results.map((result) => [result.record.item.ref, result]));
  const staleThumbnails = results.filter((result) => result.ok && result.materiallyStale).map((result) => ({
    ...publicItem(result.record),
    cachedThumbnailSha256: result.record.fingerprint.thumbSha256,
    freshThumbnailSha256: result.freshFingerprint.thumbSha256,
    cachedVsCurrent: result.cachedVsCurrent,
    actualSize: result.actualSize,
    actualMtimeIso: result.actualMtimeIso,
    indexSizeMatches: result.indexSizeMatches,
    indexMtimeMatches: result.indexMtimeMatches,
    reason: "cached_thumbnail_materially_differs_from_current_original",
  }));

  const validatedCandidates = candidates.map((candidate) => {
    const left = byRef.get(candidate.left.ref);
    const right = byRef.get(candidate.right.ref);
    let validationStatus;
    let originalByteIdentical = false;
    let originalMetrics = null;
    if (!left?.ok || !right?.ok) {
      validationStatus = "unvalidated_current_original_error";
    } else {
      originalByteIdentical = left.originalSha256 === right.originalSha256;
      originalMetrics = fingerprintMetrics(left.freshFingerprint, right.freshFingerprint);
      if (originalByteIdentical) validationStatus = "validated_current_original_bytes";
      else if (originalPairMatches(originalMetrics, opts)) validationStatus = "validated_current_original_perceptual";
      else validationStatus = "rejected_current_originals_differ";
    }
    return {
      ...candidate,
      validationStatus,
      originalByteIdentical,
      originalMetrics,
      leftCurrentOriginal: currentOriginalSummary(left),
      rightCurrentOriginal: currentOriginalSummary(right),
      deletionRecommendation: originalByteIdentical
        ? "byte_identical_current_originals_human_review_required"
        : "none_human_review_required",
      humanVisualReviewRequired: true,
    };
  });

  const clustered = buildReviewClusters(validatedCandidates);
  const stats = {
    candidatePairs: validatedCandidates.length,
    uniqueCurrentOriginalsRequested: refs.length,
    currentOriginalsValidated: results.filter((result) => result.ok).length,
    currentOriginalErrors: results.filter((result) => !result.ok).length,
    materiallyStaleThumbnails: staleThumbnails.length,
    validatedByteIdenticalPairs: validatedCandidates.filter((c) => c.validationStatus === "validated_current_original_bytes").length,
    validatedPerceptualPairs: validatedCandidates.filter((c) => c.validationStatus === "validated_current_original_perceptual").length,
    rejectedDifferentOriginalPairs: validatedCandidates.filter((c) => c.validationStatus === "rejected_current_originals_differ").length,
    unvalidatedPairs: validatedCandidates.filter((c) => c.validationStatus === "unvalidated_current_original_error").length,
    reviewClusters: clustered.clusters.length,
    byteIdenticalOnlyClusters: clustered.clusters.filter((cluster) => cluster.allEdgesByteIdentical).length,
    largestReviewCluster: clustered.clusters.reduce((largest, cluster) => Math.max(largest, cluster.size), 0),
  };
  return {
    candidates: clustered.candidates,
    reviewClusters: clustered.clusters,
    staleThumbnails,
    originalResults: results,
    stats,
  };
}

function buildReviewClusters(candidates) {
  const included = candidates.filter((candidate) =>
    candidate.validationStatus === "validated_current_original_bytes" ||
    candidate.validationStatus === "validated_current_original_perceptual");
  const itemByRef = new Map();
  const adjacency = new Map();
  for (const candidate of included) {
    itemByRef.set(candidate.left.ref, candidate.left);
    itemByRef.set(candidate.right.ref, candidate.right);
    if (!adjacency.has(candidate.left.ref)) adjacency.set(candidate.left.ref, new Set());
    if (!adjacency.has(candidate.right.ref)) adjacency.set(candidate.right.ref, new Set());
    adjacency.get(candidate.left.ref).add(candidate.right.ref);
    adjacency.get(candidate.right.ref).add(candidate.left.ref);
  }

  const visited = new Set();
  const components = [];
  const componentByRef = new Map();
  for (const start of [...adjacency.keys()].sort()) {
    if (visited.has(start)) continue;
    const refs = [];
    const queue = [start];
    let cursor = 0;
    visited.add(start);
    while (cursor < queue.length) {
      const ref = queue[cursor++];
      refs.push(ref);
      for (const other of adjacency.get(ref) ?? []) {
        if (visited.has(other)) continue;
        visited.add(other);
        queue.push(other);
      }
    }
    refs.sort();
    const componentIndex = components.length;
    for (const ref of refs) componentByRef.set(ref, componentIndex);
    components.push({ refs, edges: [] });
  }
  for (const edge of included) {
    const componentIndex = componentByRef.get(edge.left.ref);
    if (componentIndex !== undefined) components[componentIndex].edges.push(edge);
  }

  const clusters = components.map(({ refs, edges }) => {
    const members = refs.map((ref) => itemByRef.get(ref)).sort((a, b) => {
      const am = a.mtime || Number.MAX_SAFE_INTEGER;
      const bm = b.mtime || Number.MAX_SAFE_INTEGER;
      return am - bm || a.ref.localeCompare(b.ref, undefined, { numeric: true });
    });
    const allEdgesByteIdentical = edges.every((edge) => edge.originalByteIdentical);
    const sourceCounts = {};
    for (const member of members) sourceCounts[member.source] = (sourceCounts[member.source] ?? 0) + 1;
    return {
      id: "",
      size: members.length,
      edgeCount: edges.length,
      allEdgesByteIdentical,
      sourceCounts,
      earliestIndexMtimeRef: members[0]?.ref ?? null,
      earliestIndexMtimeCaveat: "index_mtime_is_not_proof_of_download_or_import_time",
      deletionRecommendation: allEdgesByteIdentical
        ? "byte_identical_current_originals_human_review_required"
        : "none_human_review_required",
      humanVisualReviewRequired: true,
      members,
      edges: edges.map((edge) => ({
        leftRef: edge.left.ref,
        rightRef: edge.right.ref,
        type: edge.type,
        validationStatus: edge.validationStatus,
        originalByteIdentical: edge.originalByteIdentical,
      })),
    };
  });
  clusters.sort((a, b) => b.size - a.size || a.earliestIndexMtimeRef.localeCompare(b.earliestIndexMtimeRef));
  const clusterIdByPair = new Map();
  for (let i = 0; i < clusters.length; i++) {
    const cluster = clusters[i];
    cluster.id = `review-${String(i + 1).padStart(6, "0")}`;
    for (const edge of cluster.edges) {
      const key = [edge.leftRef, edge.rightRef].sort().join("\u0000");
      clusterIdByPair.set(key, cluster.id);
    }
  }
  const candidatesWithClusters = candidates.map((candidate) => ({
    ...candidate,
    reviewClusterId: clusterIdByPair.get([candidate.left.ref, candidate.right.ref].sort().join("\u0000")) ?? null,
  }));
  return { clusters, candidates: candidatesWithClusters };
}

function buildCandidates(records, opts) {
  const exactGroups = [...groupBy(records, (r) => r.fingerprint.thumbSha256).entries()]
    .filter(([, members]) => members.length > 1)
    .map(([hash, members], index) => ({
      id: `thumb-${String(index + 1).padStart(6, "0")}`,
      hash,
      members: members.sort(sortKeepFirst),
    }));
  const normalizedGroups = [...groupBy(records, (r) =>
    `${r.fingerprint.normalizedSha256}:${Math.round(Math.log(r.fingerprint.aspectRatio) * 100)}`).entries()]
    .filter(([, members]) => members.length > 1)
    .map(([hash, members], index) => ({
      id: `norm-${String(index + 1).padStart(6, "0")}`,
      hash,
      members: members.sort(sortKeepFirst),
    }));
  const signatureGroups = buildSignatureGroups(records);
  const candidates = [];
  const edgeKeys = new Set();

  function addCandidate(candidate) {
    const refs = [candidate.left.ref, candidate.right.ref].sort();
    const key = `${refs[0]}\u0000${refs[1]}`;
    if (edgeKeys.has(key)) return;
    edgeKeys.add(key);
    candidates.push(candidate);
  }

  // Exact cached-WebP groups: linear star edges, never all-pairs.
  for (const group of exactGroups) {
    const keep = group.members[0];
    for (const member of group.members.slice(1)) {
      addCandidate(makeCandidate("exact_thumbnail", keep, member, pairMetrics(keep, member), {
        exactGroupId: group.id,
        exactGroupSize: group.members.length,
      }));
    }
  }

  // Identical normalized 16x16 grayscale pixels, but possibly different WebP bytes.
  for (const group of normalizedGroups) {
    const byThumb = groupBy(group.members, (r) => r.fingerprint.thumbSha256);
    const representatives = [...byThumb.values()].map((members) => members.sort(sortKeepFirst)[0]).sort(sortKeepFirst);
    const keep = representatives[0];
    for (const member of representatives.slice(1)) {
      addCandidate(makeCandidate("normalized_pixels_identical", keep, member, pairMetrics(keep, member), {
        normalizedGroupId: group.id,
        normalizedGroupSize: group.members.length,
      }));
    }
  }

  // Same pHash+dHash+aspect bucket, but not already connected above.
  for (const group of signatureGroups.filter((g) => g.members.length > 1)) {
    const byNormalized = groupBy(group.members, (r) => r.fingerprint.normalizedSha256);
    const representatives = [...byNormalized.values()].map((members) => members.sort(sortKeepFirst)[0]).sort(sortKeepFirst);
    const keep = representatives[0];
    for (const member of representatives.slice(1)) {
      addCandidate(makeCandidate("fingerprint_identical", keep, member, pairMetrics(keep, member), {
        signatureGroupId: group.id,
        signatureGroupSize: group.members.length,
      }));
    }
  }

  // Near-neighbour groups via a BK-tree on the combined 128-bit pHash+dHash.
  const tree = new BKTree(hammingWords);
  for (const group of signatureGroups) {
    const near = [];
    for (const other of tree.search(group.words, opts.totalDistance)) {
      const metrics = pairMetrics(group.representative, other.representative);
      if (metrics.pHashDistance > opts.pHashDistance || metrics.dHashDistance > opts.dHashDistance) continue;
      if (metrics.totalHashDistance > opts.totalDistance) continue;
      if (metrics.aspectDelta > opts.aspectDelta) continue;
      if (metrics.brightnessDelta > opts.brightnessDelta) continue;
      if (metrics.colorDistance > opts.colorDistance) continue;
      near.push({ other, metrics });
    }
    near.sort((a, b) => {
      const sa = a.metrics.pHashDistance * 2 + a.metrics.dHashDistance + a.metrics.aspectDelta * 100;
      const sb = b.metrics.pHashDistance * 2 + b.metrics.dHashDistance + b.metrics.aspectDelta * 100;
      return sa - sb || a.other.id.localeCompare(b.other.id);
    });
    for (const { other, metrics } of near.slice(0, opts.maxNeighbors)) {
      addCandidate(makeCandidate("perceptual_near_match", group.representative, other.representative, metrics, {
        leftSignatureGroupId: group.id,
        leftSignatureGroupSize: group.members.length,
        rightSignatureGroupId: other.id,
        rightSignatureGroupSize: other.members.length,
      }));
    }
    tree.insert(group);
  }

  const priority = { exact_thumbnail: 0, normalized_pixels_identical: 1, fingerprint_identical: 2, perceptual_near_match: 3 };
  candidates.sort((a, b) => (priority[a.type] - priority[b.type]) || a.score - b.score ||
    a.left.ref.localeCompare(b.left.ref, undefined, { numeric: true }));

  return { exactGroups, normalizedGroups, signatureGroups, candidates };
}

function csvCell(value) {
  if (value === null || value === undefined) return "";
  const text = typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(rows, columns) {
  const lines = [columns.join(",")];
  for (const row of rows) lines.push(columns.map((column) => csvCell(row[column])).join(","));
  return lines.join("\r\n") + "\r\n";
}

function candidateCsvRows(candidates) {
  return candidates.map((c) => ({
    reviewClusterId: c.reviewClusterId,
    type: c.type,
    generationConfidence: c.generationConfidence,
    validationStatus: c.validationStatus,
    originalByteIdentical: c.originalByteIdentical,
    score: c.score,
    pHashDistance: c.pHashDistance,
    dHashDistance: c.dHashDistance,
    totalHashDistance: c.totalHashDistance,
    aspectDelta: c.aspectDelta,
    brightnessDelta: c.brightnessDelta,
    colorDistance: c.colorDistance,
    originalPHashDistance: c.originalMetrics?.pHashDistance,
    originalDHashDistance: c.originalMetrics?.dHashDistance,
    originalTotalHashDistance: c.originalMetrics?.totalHashDistance,
    originalAspectDelta: c.originalMetrics?.aspectDelta,
    originalBrightnessDelta: c.originalMetrics?.brightnessDelta,
    originalColorDistance: c.originalMetrics?.colorDistance,
    leftCachedThumbnailStale: c.leftCurrentOriginal?.cachedThumbnailMateriallyStale,
    rightCachedThumbnailStale: c.rightCurrentOriginal?.cachedThumbnailMateriallyStale,
    deletionRecommendation: c.deletionRecommendation,
    earliestIndexMtimeRef: c.earliestIndexMtimeRef,
    earliestIndexMtimeCaveat: c.earliestIndexMtimeCaveat,
    leftRef: c.left.ref,
    leftYear: c.left.year,
    leftBucket: c.left.bucket,
    leftSource: c.left.source,
    leftName: c.left.name,
    leftSize: c.left.size,
    leftMtimeIso: c.left.mtimeIso,
    rightRef: c.right.ref,
    rightYear: c.right.year,
    rightBucket: c.right.bucket,
    rightSource: c.right.source,
    rightName: c.right.name,
    rightSize: c.right.size,
    rightMtimeIso: c.right.mtimeIso,
    leftSignatureGroupSize: c.leftSignatureGroupSize ?? c.signatureGroupSize ?? c.exactGroupSize ?? c.normalizedGroupSize ?? 1,
    rightSignatureGroupSize: c.rightSignatureGroupSize ?? 1,
  }));
}

const CANDIDATE_COLUMNS = [
  "reviewClusterId", "type", "generationConfidence", "validationStatus", "originalByteIdentical", "score",
  "pHashDistance", "dHashDistance", "totalHashDistance", "aspectDelta", "brightnessDelta", "colorDistance",
  "originalPHashDistance", "originalDHashDistance", "originalTotalHashDistance", "originalAspectDelta",
  "originalBrightnessDelta", "originalColorDistance", "leftCachedThumbnailStale", "rightCachedThumbnailStale",
  "deletionRecommendation", "earliestIndexMtimeRef", "earliestIndexMtimeCaveat",
  "leftRef", "leftYear", "leftBucket", "leftSource", "leftName", "leftSize", "leftMtimeIso",
  "rightRef", "rightYear", "rightBucket", "rightSource", "rightName", "rightSize", "rightMtimeIso",
  "leftSignatureGroupSize", "rightSignatureGroupSize",
];

const MISSING_COLUMNS = ["ref", "year", "bucket", "source", "name", "ext", "size", "mtimeIso", "cacheKey", "r2Key", "reason"];
const STALE_COLUMNS = [
  "ref", "year", "bucket", "source", "name", "ext", "size", "mtimeIso", "cacheKey",
  "cachedThumbnailSha256", "freshThumbnailSha256", "actualSize", "actualMtimeIso",
  "indexSizeMatches", "indexMtimeMatches", "pHashDistance", "dHashDistance", "totalHashDistance",
  "aspectDelta", "brightnessDelta", "colorDistance", "reason",
];

function reportGroup(group) {
  return {
    id: group.id,
    size: group.members.length,
    earliestIndexMtimeRef: group.members[0].item.ref,
    earliestIndexMtimeCaveat: "index_mtime_is_not_proof_of_download_or_import_time",
    deletionRecommendation: "none_cached_thumbnail_group_only",
    members: group.members.map(publicItem),
  };
}

async function writeReports(opts, indexRaw, index, selection, collection, built, validation, elapsedMs, r2Reader) {
  const successful = collection.results.filter((r) => r.ok);
  const missingThumbnails = collection.results.filter((r) => !r.ok).map((r) => ({
    ...publicItem({ item: r.item }),
    r2Key: r.item.r2Key,
    reason: r.reason,
  }));
  const currentOriginalErrors = validation.originalResults.filter((result) => !result.ok).map((result) => ({
    ...publicItem(result.record),
    r2Key: "",
    reason: result.reason,
  }));
  const missing = [...missingThumbnails, ...currentOriginalErrors];
  const byType = {};
  for (const candidate of validation.candidates) byType[candidate.type] = (byType[candidate.type] ?? 0) + 1;

  const report = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    readonly: true,
    originalPhotosMutated: false,
    r2ObjectsMutated: false,
    sourceIndex: {
      path: path.relative(REPO, opts.index).replaceAll("\\", "/"),
      generatedAt: index.generatedAt ?? null,
      sha256: sha256(indexRaw),
    },
    config: {
      library: "chenwei",
      thumbnailWidth: THUMB_WIDTH,
      fingerprintVersion: FINGERPRINT_VERSION,
      years: opts.years ? [...opts.years] : null,
      buckets: opts.buckets ? [...opts.buckets] : null,
      limit: opts.limit,
      concurrency: opts.concurrency,
      r2TimeoutMs: opts.r2TimeoutMs,
      originalConcurrency: opts.originalConcurrency,
      originalTimeoutMs: opts.originalTimeoutMs,
      pHashDistance: opts.pHashDistance,
      dHashDistance: opts.dHashDistance,
      totalDistance: opts.totalDistance,
      aspectDelta: opts.aspectDelta,
      brightnessDelta: opts.brightnessDelta,
      colorDistance: opts.colorDistance,
      maxNeighbors: opts.maxNeighbors,
      stalePHashDistance: opts.stalePHashDistance,
      staleDHashDistance: opts.staleDHashDistance,
      staleAspectDelta: opts.staleAspectDelta,
      staleBrightnessDelta: opts.staleBrightnessDelta,
      staleColorDistance: opts.staleColorDistance,
      r2ReadsEnabled: opts.useR2,
      fetchedThumbnailsCachedLocally: opts.cacheFetched,
      checkpointEnabled: opts.useCheckpoint,
    },
    limitations: [
      "Scope is limited to media represented in the saved source-index snapshot; unindexed nested files and top-level staging are excluded.",
      "Cached/R2 480px thumbnails are candidate-generation only and may be stale because their key omits original content and mtime.",
      "Exact-thumbnail means identical cached WebP bytes, not identical current original-file bytes.",
      "Every candidate pair is re-decoded and re-hashed from current originals before it receives a validated status.",
      "A validated perceptual pair only confirms current-original visual similarity under configured thresholds; it is not proof of duplication.",
      "No row is an automatic deletion recommendation; even validated pairs require human visual review.",
      "The index mtime is not proof of original download/import time; earliest-mtime fields are review aids only.",
      "Files without a cached or R2 480px thumbnail are listed as missing and were not compared.",
      "Stale-thumbnail detection covers files involved in generated candidate pairs, not every singleton in the library.",
      "At most maxNeighbors near matches are retained per fingerprint group to keep reports bounded.",
    ],
    stats: {
      selectedBeforeLimit: selection.selectedBeforeLimit,
      selectedImages: selection.images.length,
      skippedVideosDuringSelection: selection.videos,
      ...collection.stats,
      successfulFingerprints: successful.length,
      missingThumbnailObjects: missingThumbnails.length,
      currentOriginalValidationErrors: currentOriginalErrors.length,
      missingObjects: missing.length,
      exactThumbnailGroups: built.exactGroups.length,
      normalizedPixelGroups: built.normalizedGroups.length,
      identicalFingerprintGroups: built.signatureGroups.filter((g) => g.members.length > 1).length,
      uniqueFingerprintGroups: built.signatureGroups.length,
      candidatePairs: validation.candidates.length,
      candidatePairsByType: byType,
      currentOriginalValidation: validation.stats,
      elapsedSeconds: Math.round(elapsedMs / 10) / 100,
      r2DisabledReason: r2Reader.disabledReason,
    },
    exactThumbnailGroups: built.exactGroups.map(reportGroup),
    normalizedPixelGroups: built.normalizedGroups.map(reportGroup),
    identicalFingerprintGroups: built.signatureGroups.filter((g) => g.members.length > 1).map((g) => ({
      id: g.id,
      size: g.members.length,
      pHash: g.fingerprint.pHash,
      dHash: g.fingerprint.dHash,
      earliestIndexMtimeRef: g.members[0].item.ref,
      earliestIndexMtimeCaveat: "index_mtime_is_not_proof_of_download_or_import_time",
      deletionRecommendation: "none_cached_thumbnail_group_only",
      members: g.members.map(publicItem),
    })),
    candidates: validation.candidates,
    reviewClusters: validation.reviewClusters,
    staleThumbnailScope: "candidate_members_only",
    staleThumbnailObjects: validation.staleThumbnails,
    missingThumbnailObjects: missingThumbnails,
    currentOriginalValidationErrors: currentOriginalErrors,
    missingObjects: missing,
  };

  const jsonPath = `${opts.outPrefix}.json`;
  const csvPath = `${opts.outPrefix}.csv`;
  const missingPath = `${opts.outPrefix}.missing.csv`;
  const stalePath = `${opts.outPrefix}.stale-thumbnails.csv`;
  const sourceIndexPath = `${opts.outPrefix}.source-index.json`;
  report.sourceIndex.snapshotPath = path.relative(REPO, sourceIndexPath).replaceAll("\\", "/");
  await fs.mkdir(path.dirname(opts.outPrefix), { recursive: true });
  await fs.writeFile(sourceIndexPath, indexRaw);
  await fs.writeFile(jsonPath, JSON.stringify(report, null, 2) + "\n", "utf8");
  await fs.writeFile(csvPath, toCsv(candidateCsvRows(validation.candidates), CANDIDATE_COLUMNS), "utf8");
  await fs.writeFile(missingPath, toCsv(missing, MISSING_COLUMNS), "utf8");
  const staleRows = validation.staleThumbnails.map((row) => ({
    ...row,
    pHashDistance: row.cachedVsCurrent.pHashDistance,
    dHashDistance: row.cachedVsCurrent.dHashDistance,
    totalHashDistance: row.cachedVsCurrent.totalHashDistance,
    aspectDelta: row.cachedVsCurrent.aspectDelta,
    brightnessDelta: row.cachedVsCurrent.brightnessDelta,
    colorDistance: row.cachedVsCurrent.colorDistance,
  }));
  await fs.writeFile(stalePath, toCsv(staleRows, STALE_COLUMNS), "utf8");
  return { jsonPath, csvPath, missingPath, stalePath, sourceIndexPath, report };
}

async function main() {
  let opts;
  try {
    opts = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`Argument error: ${error.message}`);
    usage();
    process.exitCode = 2;
    return;
  }
  if (opts.help) { usage(); return; }

  const started = Date.now();
  const indexRaw = await fs.readFile(opts.index);
  const index = JSON.parse(indexRaw.toString("utf8"));
  const selection = flattenChenwei(index, opts);
  console.log("READ-ONLY audit: original photos and R2 objects will not be changed.");
  console.log(`Index generated: ${index.generatedAt ?? "unknown"}`);
  console.log(`Selected images: ${selection.images.length} (before limit ${selection.selectedBeforeLimit})`);

  const checkpoint = opts.useCheckpoint ? await loadCheckpoint(opts.checkpoint) : new Map();
  console.log(`Checkpoint fingerprints available: ${checkpoint.size}`);
  const checkpointWriter = new CheckpointWriter(opts.checkpoint, opts.useCheckpoint);
  const r2Reader = new R2ThumbReader(opts.useR2, opts.r2TimeoutMs);
  const collection = await collectFingerprints(selection.images, opts, checkpoint, checkpointWriter, r2Reader);
  await checkpointWriter.close();

  const successful = collection.results.filter((r) => r.ok);
  console.log(`Building bounded candidate graph from ${successful.length} fingerprints...`);
  const built = buildCandidates(successful, opts);
  if (opts.candidatePlanOnly) {
    const candidateItems = new Map();
    for (const candidate of built.candidates) {
      candidateItems.set(candidate.left.ref, candidate.left);
      candidateItems.set(candidate.right.ref, candidate.right);
    }
    const candidateIndexBytes = [...candidateItems.values()].reduce((sum, item) => sum + item.size, 0);
    console.log(JSON.stringify({
      candidatePairs: built.candidates.length,
      uniqueCandidateOriginals: candidateItems.size,
      candidateIndexBytes,
      averageCandidateIndexBytes: candidateItems.size ? Math.round(candidateIndexBytes / candidateItems.size) : 0,
      exactThumbnailGroups: built.exactGroups.length,
      normalizedPixelGroups: built.normalizedGroups.length,
      identicalFingerprintGroups: built.signatureGroups.filter((group) => group.members.length > 1).length,
    }));
    return;
  }
  const validation = await validateCandidatesAgainstCurrentOriginals(built.candidates, successful, opts);
  const outputs = await writeReports(
    opts, indexRaw, index, selection, collection, built, validation, Date.now() - started, r2Reader,
  );

  console.log("\n=== Audit complete (no originals changed) ===");
  console.log(`Fingerprinted: ${outputs.report.stats.successfulFingerprints}`);
  console.log(`Candidate pairs: ${outputs.report.stats.candidatePairs}`);
  console.log(`Review clusters: ${validation.stats.reviewClusters} (largest ${validation.stats.largestReviewCluster})`);
  console.log(`Validated current-original pairs: ${validation.stats.validatedByteIdenticalPairs + validation.stats.validatedPerceptualPairs}`);
  console.log(`Rejected stale/different-original pairs: ${validation.stats.rejectedDifferentOriginalPairs}`);
  console.log(`Materially stale candidate thumbnails: ${validation.stats.materiallyStaleThumbnails}`);
  console.log(`Missing objects: ${outputs.report.stats.missingObjects}`);
  console.log(`JSON: ${outputs.jsonPath}`);
  console.log(`CSV: ${outputs.csvPath}`);
  console.log(`Missing CSV: ${outputs.missingPath}`);
  console.log(`Stale thumbnail CSV: ${outputs.stalePath}`);
  console.log(`Source index snapshot: ${outputs.sourceIndexPath}`);
}

main().catch((error) => {
  // Deliberately do not stringify SDK errors: request objects may contain
  // connection details. Only a short type + message is printed.
  console.error(`FATAL ${safeErrorName(error)}: ${String(error?.message || "audit failed").slice(0, 300)}`);
  process.exitCode = 1;
});
