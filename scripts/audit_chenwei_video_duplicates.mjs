#!/usr/bin/env node
/**
 * Read-only duplicate audit for Chenwei MOV/MP4 files.
 *
 * Every run streams every selected current original through SHA-256.  ffprobe
 * metadata and three ffmpeg frame fingerprints may resume from a checkpoint,
 * but only when keyed by that freshly computed original SHA.  Videos are
 * compared only with videos; image thumbnails are never mixed into this audit.
 */

import crypto from "node:crypto";
import { execFile as execFileCallback } from "node:child_process";
import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const execFile = promisify(execFileCallback);
const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO = path.resolve(SCRIPT_DIR, "..");
const DEFAULT_INDEX = path.join(REPO, "scripts", "photo_index.json");
const DEFAULT_PHOTOS_ROOT = "G:/我的雲端硬碟/資料/知識圖工作室/照片/辰瑋相片";
const DEFAULT_DIR = path.join(REPO, ".cache", "photo-duplicate-audit");
const DEFAULT_CHECKPOINT = path.join(DEFAULT_DIR, "chenwei-video-frames.v1.jsonl");
const DEFAULT_OUT_PREFIX = path.join(REPO, "output", "photo-audit", "chenwei-video-current");
const VERSION = "video-sha256-3frame-phash16-dhash9-v1";
const PHASH_N = 16;
const PHASH_LOW = 8;
const FRAME_WIDTH = 160;
const FRAME_POSITIONS = [0.1, 0.5, 0.9];
const COS_TABLE = Array.from({ length: PHASH_LOW }, (_, u) =>
  Float64Array.from({ length: PHASH_N }, (_, x) =>
    Math.cos(((2 * x + 1) * u * Math.PI) / (2 * PHASH_N))),
);

function usage() {
  console.log(`Read-only Chenwei video duplicate audit

Usage:
  node scripts/audit_chenwei_video_duplicates.mjs [options]

Options:
  --index=PATH                  photo_index.json path
  --photos-root=PATH            current Chenwei original root
  --out-prefix=PATH             output prefix
  --checkpoint=PATH             resumable frame-fingerprint JSONL
  --years=YYYY,YYYY             restrict years
  --limit=N                     first N selected videos (0 = all)
  --concurrency=N               current-original workers (default 2, max 4)
  --file-timeout-ms=N           SHA stream timeout (default 180000)
  --ffmpeg-timeout-ms=N         each probe/frame timeout (default 60000)
  --duration-tolerance-sec=N    absolute duration tolerance (default 1)
  --duration-tolerance-ratio=N  relative duration tolerance (default 0.01)
  --progress-every=N            progress interval (default 25)
  --no-checkpoint               do not reuse/append frame checkpoint
  --help                        show help

Safety:
  Originals are opened read-only. Exact byte identity and three-frame visual
  similarity are reported separately; every row still requires human review.`);
}

function integer(value, name, min, max) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed < min || parsed > max) {
    throw new Error(`${name} must be an integer in ${min}..${max}`);
  }
  return parsed;
}

function number(value, name, min, max) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < min || parsed > max) {
    throw new Error(`${name} must be a number in ${min}..${max}`);
  }
  return parsed;
}

function parseArgs(argv) {
  const opts = {
    index: DEFAULT_INDEX,
    photosRoot: DEFAULT_PHOTOS_ROOT,
    outPrefix: DEFAULT_OUT_PREFIX,
    checkpoint: DEFAULT_CHECKPOINT,
    years: null,
    limit: 0,
    concurrency: 2,
    fileTimeoutMs: 180_000,
    ffmpegTimeoutMs: 60_000,
    durationToleranceSec: 1,
    durationToleranceRatio: 0.01,
    progressEvery: 25,
    useCheckpoint: true,
  };
  for (const arg of argv) {
    if (arg === "--help" || arg === "-h") return { ...opts, help: true };
    if (arg === "--no-checkpoint") { opts.useCheckpoint = false; continue; }
    const [name, ...rest] = arg.split("=");
    const value = rest.join("=");
    if (!name.startsWith("--") || !value) throw new Error(`Unknown or incomplete option: ${arg}`);
    if (name === "--index") opts.index = path.resolve(REPO, value);
    else if (name === "--photos-root") opts.photosRoot = path.resolve(REPO, value);
    else if (name === "--out-prefix") opts.outPrefix = path.resolve(REPO, value);
    else if (name === "--checkpoint") opts.checkpoint = path.resolve(REPO, value);
    else if (name === "--years") opts.years = new Set(value.split(",").map((part) => part.trim()).filter(Boolean));
    else if (name === "--limit") opts.limit = integer(value, name, 0, Number.MAX_SAFE_INTEGER);
    else if (name === "--concurrency") opts.concurrency = integer(value, name, 1, 4);
    else if (name === "--file-timeout-ms") opts.fileTimeoutMs = integer(value, name, 1000, 900_000);
    else if (name === "--ffmpeg-timeout-ms") opts.ffmpegTimeoutMs = integer(value, name, 1000, 300_000);
    else if (name === "--duration-tolerance-sec") opts.durationToleranceSec = number(value, name, 0, 60);
    else if (name === "--duration-tolerance-ratio") opts.durationToleranceRatio = number(value, name, 0, 0.25);
    else if (name === "--progress-every") opts.progressEvery = integer(value, name, 1, Number.MAX_SAFE_INTEGER);
    else throw new Error(`Unknown option: ${name}`);
  }
  return opts;
}

function sha256(data) {
  return crypto.createHash("sha256").update(data).digest("hex");
}

function sourceForBucket(bucket) {
  if (bucket === "screenshots") return "screenshot";
  if (bucket === "downloads") return "download";
  if (/^(0[1-9]|1[0-2])$/.test(bucket)) return "photo";
  return "event";
}

function flattenVideos(index, opts) {
  const years = index?.libraries?.chenwei?.years;
  if (!years) throw new Error("Index has no libraries.chenwei.years");
  const videos = [];
  let imagesSkipped = 0;
  for (const year of Object.keys(years).sort()) {
    if (opts.years && !opts.years.has(year)) continue;
    for (const bucket of Object.keys(years[year].buckets ?? {}).sort()) {
      for (const file of years[year].buckets[bucket] ?? []) {
        if (file.kind !== "video") { imagesSkipped++; continue; }
        const mtime = Number(file.mtime) || 0;
        videos.push({
          ref: `${year}/${bucket}/${file.name}`,
          year,
          bucket,
          source: sourceForBucket(bucket),
          name: file.name,
          ext: String(file.ext || path.extname(file.name)).toLowerCase(),
          indexSize: Number(file.size) || 0,
          indexMtime: mtime,
          indexMtimeIso: mtime ? new Date(mtime).toISOString() : null,
        });
      }
    }
  }
  videos.sort((a, b) => a.ref.localeCompare(b.ref, undefined, { numeric: true }));
  return {
    videos: opts.limit ? videos.slice(0, opts.limit) : videos,
    selectedBeforeLimit: videos.length,
    imagesSkipped,
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
    if (eventParts.length !== 1 || !eventParts[0] || eventParts[0].includes("\\")) {
      throw new Error("invalid indexed month event");
    }
    folder = path.join(`${item.year}.${month}`, eventParts[0]);
  } else {
    if (!item.bucket || item.bucket.includes("/") || item.bucket.includes("\\")) {
      throw new Error("invalid indexed event bucket");
    }
    folder = item.bucket;
  }
  const root = path.resolve(photosRoot);
  const resolved = path.resolve(root, `${item.year}相片`, folder, item.name);
  if (!resolved.startsWith(root + path.sep)) throw new Error("indexed path escaped photo root");
  return resolved;
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
  await Promise.all(Array.from({ length: Math.min(items.length, concurrency) }, () => worker()));
  return results;
}

async function hashCurrentFile(file, timeoutMs) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const hash = crypto.createHash("sha256");
    const stream = fsSync.createReadStream(file, { signal: controller.signal });
    for await (const chunk of stream) hash.update(chunk);
    return hash.digest("hex");
  } finally {
    clearTimeout(timeout);
  }
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function bitsToHex(bits) {
  let out = "";
  for (let i = 0; i < bits.length; i += 4) {
    let value = 0;
    for (let j = 0; j < 4; j++) value = (value << 1) | (bits[i + j] ? 1 : 0);
    out += value.toString(16);
  }
  return out;
}

function perceptualHash16(pixels) {
  const rows = Array.from({ length: PHASH_N }, () => new Float64Array(PHASH_LOW));
  for (let y = 0; y < PHASH_N; y++) {
    for (let u = 0; u < PHASH_LOW; u++) {
      let sum = 0;
      for (let x = 0; x < PHASH_N; x++) sum += pixels[y * PHASH_N + x] * COS_TABLE[u][x];
      rows[y][u] = sum;
    }
  }
  const coefficients = [];
  for (let v = 0; v < PHASH_LOW; v++) {
    for (let u = 0; u < PHASH_LOW; u++) {
      let sum = 0;
      for (let y = 0; y < PHASH_N; y++) sum += rows[y][u] * COS_TABLE[v][y];
      coefficients.push(sum);
    }
  }
  const threshold = median(coefficients.slice(1));
  return bitsToHex(coefficients.map((coefficient) => coefficient > threshold));
}

function differenceHash(pixels) {
  const bits = [];
  for (let y = 0; y < 8; y++) {
    for (let x = 0; x < 8; x++) bits.push(pixels[y * 9 + x] > pixels[y * 9 + x + 1]);
  }
  return bitsToHex(bits);
}

function averageRgb(buffer) {
  const sums = [0, 0, 0];
  let count = 0;
  for (let index = 0; index + 2 < buffer.length; index += 3) {
    sums[0] += buffer[index]; sums[1] += buffer[index + 1]; sums[2] += buffer[index + 2]; count++;
  }
  return sums.map((sum) => Math.round((sum / Math.max(1, count)) * 100) / 100);
}

async function fingerprintFrame(buffer) {
  const image = sharp(buffer, { failOn: "none", limitInputPixels: 25_000_000 });
  const [metadata, pPixels, dPixels, colorPixels] = await Promise.all([
    image.clone().metadata(),
    image.clone().resize(PHASH_N, PHASH_N, { fit: "fill" }).greyscale().raw().toBuffer(),
    image.clone().resize(9, 8, { fit: "fill" }).greyscale().raw().toBuffer(),
    image.clone().resize(8, 8, { fit: "fill" }).removeAlpha().toColourspace("srgb").raw().toBuffer(),
  ]);
  if (!metadata.width || !metadata.height) throw new Error("frame_has_no_dimensions");
  return {
    pHash: perceptualHash16(pPixels),
    dHash: differenceHash(dPixels),
    averageRgb: averageRgb(colorPixels),
    width: metadata.width,
    height: metadata.height,
  };
}

async function probeVideo(file, timeoutMs) {
  const { stdout } = await execFile("ffprobe", [
    "-v", "error", "-select_streams", "v:0",
    "-show_entries", "stream=width,height:format=duration",
    "-of", "json", file,
  ], { timeout: timeoutMs, windowsHide: true, maxBuffer: 2 * 1024 * 1024, encoding: "utf8" });
  const parsed = JSON.parse(stdout);
  const stream = parsed.streams?.[0];
  const duration = Number(parsed.format?.duration);
  if (!stream?.width || !stream?.height || !Number.isFinite(duration) || duration < 0) {
    throw new Error("ffprobe_missing_video_metadata");
  }
  return { duration, width: Number(stream.width), height: Number(stream.height) };
}

async function extractFrame(file, second, timeoutMs) {
  const { stdout } = await execFile("ffmpeg", [
    "-v", "error", "-ss", second.toFixed(3), "-i", file,
    "-map", "0:v:0", "-frames:v", "1",
    "-vf", `scale=${FRAME_WIDTH}:-2:force_original_aspect_ratio=decrease`,
    "-f", "image2pipe", "-vcodec", "png", "pipe:1",
  ], { timeout: timeoutMs, windowsHide: true, maxBuffer: 8 * 1024 * 1024, encoding: "buffer" });
  if (!Buffer.isBuffer(stdout) || stdout.length < 32) throw new Error("ffmpeg_empty_frame");
  return stdout;
}

async function fingerprintVideo(file, opts) {
  const metadata = await probeVideo(file, opts.ffmpegTimeoutMs);
  const frames = [];
  for (const position of FRAME_POSITIONS) {
    const upper = Math.max(0, metadata.duration - 0.1);
    const requestedSecond = Math.min(upper, Math.max(0, metadata.duration * position));
    let frame;
    try {
      frame = await extractFrame(file, requestedSecond, opts.ffmpegTimeoutMs);
    } catch (error) {
      if (position !== 0.9) throw error;
      frame = await extractFrame(file, Math.max(0, metadata.duration * 0.8), opts.ffmpegTimeoutMs);
    }
    frames.push({ position, second: requestedSecond, ...(await fingerprintFrame(frame)) });
  }
  return { ...metadata, aspectRatio: metadata.width / metadata.height, frames };
}

async function loadCheckpoint(file) {
  const found = new Map();
  if (!fsSync.existsSync(file)) return found;
  const lines = readline.createInterface({ input: fsSync.createReadStream(file, { encoding: "utf8" }), crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line);
      if (row.v === VERSION && row.key && row.fingerprint) found.set(row.key, row.fingerprint);
    } catch { /* interrupted final line is ignored */ }
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
    this.pending.push(JSON.stringify({ v: VERSION, key, fingerprint }));
    if (this.pending.length >= 10) this.flush();
  }
  flush() {
    if (!this.pending.length || !this.enabled) return;
    const text = this.pending.splice(0).join("\n") + "\n";
    this.chain = this.chain.then(async () => {
      await fs.mkdir(path.dirname(this.file), { recursive: true });
      await fs.appendFile(this.file, text, "utf8");
    });
  }
  async close() { this.flush(); await this.chain; }
}

function errorCode(error) {
  return String(error?.code || error?.name || "Error").replace(/[^A-Za-z0-9_-]/g, "").slice(0, 60);
}

async function collectVideos(items, opts, checkpoint, writer) {
  const stats = { selected: items.length, currentOriginalsHashed: 0, checkpointHits: 0, framesExtracted: 0, errors: 0 };
  let completed = 0;
  const results = await mapLimit(items, opts.concurrency, async (item) => {
    try {
      const originalPath = resolveOriginalPath(item, opts.photosRoot);
      const stat = await fs.stat(originalPath);
      if (!stat.isFile()) throw new Error("current_original_not_file");
      const originalSha256 = await hashCurrentFile(originalPath, opts.fileTimeoutMs);
      stats.currentOriginalsHashed++;
      const checkpointKey = `${VERSION}|${item.ref}|${originalSha256}`;
      let fingerprint = opts.useCheckpoint ? checkpoint.get(checkpointKey) : null;
      if (fingerprint) stats.checkpointHits++;
      else {
        fingerprint = await fingerprintVideo(originalPath, opts);
        stats.framesExtracted += fingerprint.frames.length;
        writer.append(checkpointKey, fingerprint);
      }
      return {
        ok: true,
        item,
        actualSize: stat.size,
        actualMtime: stat.mtimeMs,
        actualMtimeIso: stat.mtime.toISOString(),
        originalSha256,
        fingerprint,
      };
    } catch (error) {
      stats.errors++;
      return { ok: false, item, reason: `current_video_read_probe_or_frame_error:${errorCode(error)}` };
    } finally {
      completed++;
      if (completed % opts.progressEvery === 0 || completed === items.length) {
        console.log(`[video ${completed}/${items.length}] hashed=${stats.currentOriginalsHashed} checkpoint=${stats.checkpointHits} errors=${stats.errors}`);
      }
    }
  });
  return { results, stats };
}

function popcount32(value) {
  let x = value >>> 0;
  x -= (x >>> 1) & 0x55555555;
  x = (x & 0x33333333) + ((x >>> 2) & 0x33333333);
  return ((((x + (x >>> 4)) & 0x0f0f0f0f) * 0x01010101) >>> 24);
}

function hashDistance(left, right) {
  const a = left.padStart(16, "0"), b = right.padStart(16, "0");
  return popcount32((Number.parseInt(a.slice(0, 8), 16) ^ Number.parseInt(b.slice(0, 8), 16)) >>> 0) +
    popcount32((Number.parseInt(a.slice(8), 16) ^ Number.parseInt(b.slice(8), 16)) >>> 0);
}

function rgbDistance(left, right) {
  return Math.sqrt((left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2 + (left[2] - right[2]) ** 2);
}

function compareVideoFrames(left, right) {
  const frameMetrics = left.frames.map((frame, index) => ({
    position: frame.position,
    pHashDistance: hashDistance(frame.pHash, right.frames[index].pHash),
    dHashDistance: hashDistance(frame.dHash, right.frames[index].dHash),
    colorDistance: Math.round(rgbDistance(frame.averageRgb, right.frames[index].averageRgb) * 100) / 100,
  }));
  return {
    frameMetrics,
    sumPHashDistance: frameMetrics.reduce((sum, metric) => sum + metric.pHashDistance, 0),
    sumDHashDistance: frameMetrics.reduce((sum, metric) => sum + metric.dHashDistance, 0),
    maxPHashDistance: Math.max(...frameMetrics.map((metric) => metric.pHashDistance)),
    maxDHashDistance: Math.max(...frameMetrics.map((metric) => metric.dHashDistance)),
    averageColorDistance: Math.round(frameMetrics.reduce((sum, metric) => sum + metric.colorDistance, 0) / frameMetrics.length * 100) / 100,
  };
}

function publicItem(record) {
  return {
    ref: record.item.ref,
    year: record.item.year,
    bucket: record.item.bucket,
    source: record.item.source,
    name: record.item.name,
    ext: record.item.ext,
    indexSize: record.item.indexSize,
    indexMtimeIso: record.item.indexMtimeIso,
    actualSize: record.actualSize,
    actualMtimeIso: record.actualMtimeIso,
    durationSeconds: Math.round(record.fingerprint.duration * 1000) / 1000,
    width: record.fingerprint.width,
    height: record.fingerprint.height,
    originalSha256: record.originalSha256,
  };
}

function sortOldest(left, right) {
  return (left.actualMtime || Number.MAX_SAFE_INTEGER) - (right.actualMtime || Number.MAX_SAFE_INTEGER) ||
    left.item.ref.localeCompare(right.item.ref, undefined, { numeric: true });
}

function groupBy(records, keyFn) {
  const groups = new Map();
  for (const record of records) {
    const key = keyFn(record);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(record);
  }
  return groups;
}

function makeCandidate(type, leftRecord, rightRecord, extra) {
  const oldest = [leftRecord, rightRecord].sort(sortOldest)[0];
  const byteIdentical = type === "original_byte_identical";
  return {
    type,
    validationStatus: byteIdentical ? "validated_current_video_bytes" : "validated_current_video_multiframe_similarity",
    originalByteIdentical: byteIdentical,
    left: publicItem(leftRecord),
    right: publicItem(rightRecord),
    earliestCurrentMtimeRef: oldest.item.ref,
    earliestCurrentMtimeCaveat: "current_mtime_is_not_proof_of_download_or_import_time",
    deletionRecommendation: byteIdentical
      ? "byte_identical_current_videos_human_review_required"
      : "none_human_review_required",
    humanVisualReviewRequired: true,
    ...extra,
  };
}

function buildCandidates(records, opts) {
  const candidates = [];
  const exactGroups = [...groupBy(records, (record) => record.originalSha256).entries()]
    .filter(([, members]) => members.length > 1)
    .map(([sha, members], index) => ({ id: `video-exact-${String(index + 1).padStart(5, "0")}`, sha, members: members.sort(sortOldest) }));
  const exactEdgeKeys = new Set();
  for (const group of exactGroups) {
    for (const member of group.members.slice(1)) {
      const candidate = makeCandidate("original_byte_identical", group.members[0], member, { exactGroupId: group.id });
      candidates.push(candidate);
      exactEdgeKeys.add([candidate.left.ref, candidate.right.ref].sort().join("\u0000"));
    }
  }

  const sorted = [...records].sort((a, b) => a.fingerprint.duration - b.fingerprint.duration || sortOldest(a, b));
  for (let leftIndex = 0; leftIndex < sorted.length; leftIndex++) {
    const left = sorted[leftIndex];
    for (let rightIndex = leftIndex + 1; rightIndex < sorted.length; rightIndex++) {
      const right = sorted[rightIndex];
      const durationDelta = right.fingerprint.duration - left.fingerprint.duration;
      const durationLimit = Math.max(opts.durationToleranceSec,
        Math.max(left.fingerprint.duration, right.fingerprint.duration) * opts.durationToleranceRatio);
      if (durationDelta > durationLimit) break;
      const edgeKey = [left.item.ref, right.item.ref].sort().join("\u0000");
      if (exactEdgeKeys.has(edgeKey) || left.originalSha256 === right.originalSha256) continue;
      const aspectDelta = Math.abs(left.fingerprint.aspectRatio - right.fingerprint.aspectRatio) /
        Math.max(left.fingerprint.aspectRatio, right.fingerprint.aspectRatio);
      if (aspectDelta > 0.03) continue;
      const metrics = compareVideoFrames(left.fingerprint, right.fingerprint);
      if (metrics.maxPHashDistance > 8 || metrics.maxDHashDistance > 10) continue;
      if (metrics.sumPHashDistance > 12 || metrics.sumDHashDistance > 18) continue;
      if (metrics.averageColorDistance > 35) continue;
      candidates.push(makeCandidate("current_video_multiframe_perceptual", left, right, {
        durationDeltaSeconds: Math.round(durationDelta * 1000) / 1000,
        aspectDelta: Math.round(aspectDelta * 100000) / 100000,
        ...metrics,
      }));
    }
  }
  candidates.sort((a, b) => Number(b.originalByteIdentical) - Number(a.originalByteIdentical) ||
    a.left.ref.localeCompare(b.left.ref, undefined, { numeric: true }));
  return { exactGroups, candidates };
}

function buildClusters(candidates) {
  const adjacency = new Map();
  const itemByRef = new Map();
  for (const candidate of candidates) {
    itemByRef.set(candidate.left.ref, candidate.left);
    itemByRef.set(candidate.right.ref, candidate.right);
    if (!adjacency.has(candidate.left.ref)) adjacency.set(candidate.left.ref, new Set());
    if (!adjacency.has(candidate.right.ref)) adjacency.set(candidate.right.ref, new Set());
    adjacency.get(candidate.left.ref).add(candidate.right.ref);
    adjacency.get(candidate.right.ref).add(candidate.left.ref);
  }
  const visited = new Set();
  const clusters = [];
  for (const start of [...adjacency.keys()].sort()) {
    if (visited.has(start)) continue;
    const refs = [];
    const queue = [start];
    visited.add(start);
    for (let cursor = 0; cursor < queue.length; cursor++) {
      const ref = queue[cursor]; refs.push(ref);
      for (const other of adjacency.get(ref) ?? []) {
        if (!visited.has(other)) { visited.add(other); queue.push(other); }
      }
    }
    const refSet = new Set(refs);
    const edges = candidates.filter((candidate) => refSet.has(candidate.left.ref) && refSet.has(candidate.right.ref));
    const members = refs.map((ref) => itemByRef.get(ref)).sort((a, b) =>
      Date.parse(a.actualMtimeIso) - Date.parse(b.actualMtimeIso) || a.ref.localeCompare(b.ref));
    clusters.push({
      id: "",
      size: members.length,
      edgeCount: edges.length,
      allEdgesByteIdentical: edges.every((edge) => edge.originalByteIdentical),
      humanVisualReviewRequired: true,
      deletionRecommendation: edges.every((edge) => edge.originalByteIdentical)
        ? "byte_identical_current_videos_human_review_required"
        : "none_human_review_required",
      members,
      edges: edges.map((edge) => ({ leftRef: edge.left.ref, rightRef: edge.right.ref, type: edge.type })),
    });
  }
  clusters.sort((a, b) => b.size - a.size || a.members[0].ref.localeCompare(b.members[0].ref));
  const clusterByPair = new Map();
  clusters.forEach((cluster, index) => {
    cluster.id = `video-review-${String(index + 1).padStart(5, "0")}`;
    for (const edge of cluster.edges) clusterByPair.set([edge.leftRef, edge.rightRef].sort().join("\u0000"), cluster.id);
  });
  return {
    clusters,
    candidates: candidates.map((candidate) => ({
      ...candidate,
      reviewClusterId: clusterByPair.get([candidate.left.ref, candidate.right.ref].sort().join("\u0000")),
    })),
  };
}

function csvCell(value) {
  if (value === null || value === undefined) return "";
  const text = typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(rows, columns) {
  return [columns.join(","), ...rows.map((row) => columns.map((column) => csvCell(row[column])).join(","))].join("\r\n") + "\r\n";
}

async function writeReports(opts, indexRaw, index, selection, collection, built, clustered, elapsedMs) {
  const missing = collection.results.filter((result) => !result.ok).map((result) => ({ ...result.item, reason: result.reason }));
  const jsonPath = `${opts.outPrefix}.json`;
  const csvPath = `${opts.outPrefix}.csv`;
  const missingPath = `${opts.outPrefix}.missing.csv`;
  const sourceIndexPath = `${opts.outPrefix}.source-index.json`;
  const report = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    readonly: true,
    mediaKind: "video",
    originalMediaMutated: false,
    sourceIndex: {
      path: path.relative(REPO, opts.index).replaceAll("\\", "/"),
      snapshotPath: path.relative(REPO, sourceIndexPath).replaceAll("\\", "/"),
      generatedAt: index.generatedAt ?? null,
      sha256: sha256(indexRaw),
    },
    config: {
      fingerprintVersion: VERSION,
      framePositions: FRAME_POSITIONS,
      frameWidth: FRAME_WIDTH,
      years: opts.years ? [...opts.years] : null,
      limit: opts.limit,
      concurrency: opts.concurrency,
      fileTimeoutMs: opts.fileTimeoutMs,
      ffmpegTimeoutMs: opts.ffmpegTimeoutMs,
      durationToleranceSec: opts.durationToleranceSec,
      durationToleranceRatio: opts.durationToleranceRatio,
      checkpointEnabled: opts.useCheckpoint,
    },
    limitations: [
      "Scope is limited to videos represented in the saved source-index snapshot; unindexed nested files and top-level staging are excluded.",
      "Only video-to-video comparisons are made; still images are never compared with videos.",
      "Every selected current video is freshly streamed through SHA-256 on every run.",
      "Non-byte-identical matches are based on three representative frames and duration; they are similarity candidates, not duplicate proof.",
      "Live Photo still/video pairing is not inferred as duplication.",
      "No row is an automatic deletion recommendation; human playback review is required.",
    ],
    stats: {
      selectedBeforeLimit: selection.selectedBeforeLimit,
      selectedVideos: selection.videos.length,
      imagesSkipped: selection.imagesSkipped,
      ...collection.stats,
      successfulVideos: collection.results.filter((result) => result.ok).length,
      missingVideos: missing.length,
      exactByteGroups: built.exactGroups.length,
      candidatePairs: clustered.candidates.length,
      byteIdenticalPairs: clustered.candidates.filter((candidate) => candidate.originalByteIdentical).length,
      perceptualPairs: clustered.candidates.filter((candidate) => !candidate.originalByteIdentical).length,
      reviewClusters: clustered.clusters.length,
      elapsedSeconds: Math.round(elapsedMs / 10) / 100,
    },
    exactByteGroups: built.exactGroups.map((group) => ({
      id: group.id,
      sha256: group.sha,
      size: group.members.length,
      deletionRecommendation: "byte_identical_current_videos_human_review_required",
      members: group.members.map(publicItem),
    })),
    candidates: clustered.candidates,
    reviewClusters: clustered.clusters,
    missingVideos: missing,
  };
  await fs.mkdir(path.dirname(opts.outPrefix), { recursive: true });
  await fs.writeFile(sourceIndexPath, indexRaw);
  await fs.writeFile(jsonPath, JSON.stringify(report, null, 2) + "\n", "utf8");
  const candidateColumns = [
    "reviewClusterId", "type", "validationStatus", "originalByteIdentical", "durationDeltaSeconds",
    "sumPHashDistance", "sumDHashDistance", "maxPHashDistance", "maxDHashDistance", "averageColorDistance",
    "deletionRecommendation", "leftRef", "leftName", "leftSource", "leftDuration", "leftSize",
    "rightRef", "rightName", "rightSource", "rightDuration", "rightSize",
  ];
  const candidateRows = clustered.candidates.map((candidate) => ({
    ...candidate,
    leftRef: candidate.left.ref,
    leftName: candidate.left.name,
    leftSource: candidate.left.source,
    leftDuration: candidate.left.durationSeconds,
    leftSize: candidate.left.actualSize,
    rightRef: candidate.right.ref,
    rightName: candidate.right.name,
    rightSource: candidate.right.source,
    rightDuration: candidate.right.durationSeconds,
    rightSize: candidate.right.actualSize,
  }));
  await fs.writeFile(csvPath, toCsv(candidateRows, candidateColumns), "utf8");
  await fs.writeFile(missingPath, toCsv(missing, ["ref", "year", "bucket", "source", "name", "ext", "indexSize", "indexMtimeIso", "reason"]), "utf8");
  return { report, jsonPath, csvPath, missingPath, sourceIndexPath };
}

async function main() {
  let opts;
  try { opts = parseArgs(process.argv.slice(2)); }
  catch (error) { console.error(`Argument error: ${error.message}`); usage(); process.exitCode = 2; return; }
  if (opts.help) { usage(); return; }
  const started = Date.now();
  const indexRaw = await fs.readFile(opts.index);
  const index = JSON.parse(indexRaw.toString("utf8"));
  const selection = flattenVideos(index, opts);
  console.log("READ-ONLY video audit: current originals will not be changed.");
  console.log(`Index generated: ${index.generatedAt ?? "unknown"}`);
  console.log(`Selected videos: ${selection.videos.length} (before limit ${selection.selectedBeforeLimit})`);
  const checkpoint = opts.useCheckpoint ? await loadCheckpoint(opts.checkpoint) : new Map();
  console.log(`Checkpoint frame fingerprints available: ${checkpoint.size}`);
  const writer = new CheckpointWriter(opts.checkpoint, opts.useCheckpoint);
  const collection = await collectVideos(selection.videos, opts, checkpoint, writer);
  await writer.close();
  const successful = collection.results.filter((result) => result.ok);
  const built = buildCandidates(successful, opts);
  const clustered = buildClusters(built.candidates);
  const outputs = await writeReports(opts, indexRaw, index, selection, collection, built, clustered, Date.now() - started);
  console.log("\n=== Video audit complete (no originals changed) ===");
  console.log(`Successful videos: ${outputs.report.stats.successfulVideos}`);
  console.log(`Missing/errors: ${outputs.report.stats.missingVideos}`);
  console.log(`Candidate pairs: ${outputs.report.stats.candidatePairs} (${outputs.report.stats.byteIdenticalPairs} byte-identical)`);
  console.log(`Review clusters: ${outputs.report.stats.reviewClusters}`);
  console.log(`JSON: ${outputs.jsonPath}`);
  console.log(`CSV: ${outputs.csvPath}`);
  console.log(`Missing CSV: ${outputs.missingPath}`);
  console.log(`Source index snapshot: ${outputs.sourceIndexPath}`);
}

main().catch((error) => {
  console.error(`FATAL ${errorCode(error)}: ${String(error?.message || "video audit failed").slice(0, 300)}`);
  process.exitCode = 1;
});
