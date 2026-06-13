#!/usr/bin/env node
/**
 * Drive + R2 hybrid 同步：把 /photos 三相簿的「網頁縮圖」(480w + 1600w webp) 推到 R2，
 * 讓 redpiigpig.com（Zeabur 雲端，無 G: 槽）也能瀏覽照片。原檔仍留 Drive（canonical）。
 *
 * 鍵與端點完全一致：
 *   index :  photos/index.json
 *   thumb :  photos/thumb/{cacheKey}_{w}.webp  ，cacheKey = sha256(parts).slice(0,32)
 *            chenwei parts = ["chenwei", year, bucket, name]
 *            lib     parts = ["lib", slug, subpath, name]
 * （與 server/utils/photo-thumbs.ts thumbCacheKey / photos.ts r2ThumbKey 對齊）
 *
 * 只能在本機跑（原檔只在 G:）。影片 / HEIC 跳過（雲端不播 / sharp 無 libheif）。
 *
 * 用法：
 *   node scripts/sync_photos_to_r2.mjs --dry-run            # 只統計數量 + 估容量，不上傳
 *   node scripts/sync_photos_to_r2.mjs                      # 全 chenwei + training + hongshi
 *   node scripts/sync_photos_to_r2.mjs chenwei              # 只跑 chenwei
 *   node scripts/sync_photos_to_r2.mjs --widths=480         # 只跑 grid 寬度
 *   node scripts/sync_photos_to_r2.mjs --index-only         # 只重傳 index（新增照片後快速更新清單）
 *
 * 可續跑：啟動時 ListObjectsV2 把已在 R2 的 thumb key 撈成 Set，已存在的跳過。
 * crash 復原：current-marker + skiplist（同 prewarm_thumbs.mjs）。
 */
import crypto from "node:crypto";
import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import sharp from "sharp";
import {
  S3Client,
  PutObjectCommand,
  ListObjectsV2Command,
} from "@aws-sdk/client-s3";

const REPO = path.resolve(import.meta.dirname, "..");
const INDEX_PATH = path.join(REPO, "scripts", "photo_index.json");
const CURRENT_FILE_MARKER = path.join(REPO, ".cache", "_r2sync_current.txt");
const SKIPLIST_PATH = path.join(REPO, ".cache", "_r2sync_skiplist.txt");
const PHOTOS_PARENT = "G:/我的雲端硬碟/資料/儲存資料夾";
const LIB_FOLDERS = { chenwei: "辰瑋相片", training: "訓練相片", hongshi: "弘誓相片" };

// 只同步可在 sharp 處理且雲端可顯示的圖片。HEIC/HEIF 排除（Windows sharp 無 libheif）。
const SYNC_EXTS = new Set([".jpg", ".jpeg", ".png", ".webp", ".avif", ".bmp"]);
const ALLOWED_WIDTHS = new Set([240, 480, 800, 1600]);
const THUMB_PREFIX = "photos/thumb/";
const INDEX_KEY = "photos/index.json";

// ── .env（R2 憑證）─────────────────────────────────────────────────────────
function loadEnv() {
  const env = {};
  try {
    for (const l of fsSync.readFileSync(path.join(REPO, ".env"), "utf-8").split(/\r?\n/)) {
      const m = l.match(/^([A-Z0-9_]+)=(.*)$/);
      if (m) env[m[1]] = m[2].replace(/^["']|["']$/g, "");
    }
  } catch {}
  return env;
}
const ENV = loadEnv();
const BUCKET = ENV.R2_BUCKET;
function makeClient() {
  if (!ENV.R2_ENDPOINT || !ENV.R2_ACCESS_KEY || !ENV.R2_SECRET_KEY || !BUCKET) {
    throw new Error("缺 R2_ENDPOINT / R2_ACCESS_KEY / R2_SECRET_KEY / R2_BUCKET（看 .env）");
  }
  return new S3Client({
    region: "auto",
    endpoint: ENV.R2_ENDPOINT,
    credentials: { accessKeyId: ENV.R2_ACCESS_KEY, secretAccessKey: ENV.R2_SECRET_KEY },
  });
}

// ── args ───────────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
const DRY = argv.includes("--dry-run");
const INDEX_ONLY = argv.includes("--index-only");
const onlyLibs = argv.filter((a) => !a.startsWith("--"));
const widthArg = argv.find((a) => a.startsWith("--widths="));
const widths = widthArg
  ? widthArg.slice(9).split(",").map(Number).filter((w) => ALLOWED_WIDTHS.has(w))
  : [480, 1600];

// ── keys（與後端 thumbCacheKey 一致）─────────────────────────────────────────
function thumbCacheKey(parts) {
  return crypto.createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 32);
}
function r2ThumbKey(key, width) {
  return `${THUMB_PREFIX}${key}_${width}.webp`;
}

// ── crash skiplist（同 prewarm）──────────────────────────────────────────────
const skipset = new Set();
if (!DRY) {
  try {
    const prev = fsSync.readFileSync(CURRENT_FILE_MARKER, "utf-8").trim();
    if (prev) {
      console.log(`!! 偵測到上次 crash 在 ${prev}，加進 skiplist`);
      fsSync.appendFileSync(SKIPLIST_PATH, prev + "\n");
      fsSync.unlinkSync(CURRENT_FILE_MARKER);
    }
  } catch {}
  try {
    for (const ln of fsSync.readFileSync(SKIPLIST_PATH, "utf-8").split(/\r?\n/)) {
      if (ln.trim()) skipset.add(ln.trim());
    }
    if (skipset.size) console.log(`Skiplist: ${skipset.size} 個檔曾 crash，本次跳過`);
  } catch {}
}

let client = null;

// 啟動時把 R2 已有的 thumb key 撈成 Set（避免每檔 HeadObject）
async function loadExistingKeys() {
  const set = new Set();
  let token;
  let pages = 0;
  do {
    const res = await client.send(new ListObjectsV2Command({
      Bucket: BUCKET, Prefix: THUMB_PREFIX, ContinuationToken: token,
    }));
    for (const o of res.Contents ?? []) set.add(o.Key);
    token = res.IsTruncated ? res.NextContinuationToken : undefined;
    pages++;
    if (pages % 10 === 0) process.stdout.write(`  …已列 ${set.size} 個既有 thumb\n`);
  } while (token);
  return set;
}

async function genWebp(origPath, width) {
  return sharp(origPath, { failOn: "none" })
    .rotate()
    .resize(width, null, { fit: "inside", withoutEnlargement: true })
    .webp({ quality: 80 })
    .toBuffer();
}

async function processFile(origPath, keyParts, stats, existing) {
  const ext = path.extname(origPath).toLowerCase();
  if (!SYNC_EXTS.has(ext)) { stats.skippedExt++; return; }
  const key = thumbCacheKey(keyParts);

  if (DRY) {
    for (const w of widths) stats.wouldUpload++;
    stats.total++;
    return;
  }
  if (skipset.has(origPath)) { stats.skippedByList++; stats.total++; return; }

  fsSync.writeFileSync(CURRENT_FILE_MARKER, origPath);
  for (const w of widths) {
    const rkey = r2ThumbKey(key, w);
    if (existing.has(rkey)) { stats.skipped++; continue; }
    try {
      const buf = await genWebp(origPath, w);
      await client.send(new PutObjectCommand({
        Bucket: BUCKET, Key: rkey, Body: buf, ContentType: "image/webp",
      }));
      existing.add(rkey);
      stats.uploaded++;
      stats.bytes += buf.length;
    } catch (e) {
      stats.errors.push(`${origPath} @${w}w: ${e.message}`);
    }
  }
  try { fsSync.unlinkSync(CURRENT_FILE_MARKER); } catch {}
  stats.total++;
  if (stats.total % 200 === 0) {
    process.stdout.write(
      `  ${stats.total} imgs | up=${stats.uploaded} skip=${stats.skipped} ext=${stats.skippedExt} err=${stats.errors.length} | ${(stats.bytes/1e6).toFixed(0)}MB\n`
    );
  }
}

async function processChenwei(idx, stats, existing) {
  const lib = idx.libraries.chenwei;
  if (!lib) return;
  const root = path.join(PHOTOS_PARENT, LIB_FOLDERS.chenwei);
  for (const [year, yd] of Object.entries(lib.years)) {
    for (const [bucket, files] of Object.entries(yd.buckets)) {
      let folderName;
      if (/^(0[1-9]|1[0-2])$/.test(bucket)) folderName = `${year}.${bucket}`;
      else if (bucket === "screenshots") folderName = `${year}截圖`;
      else if (bucket === "downloads") folderName = `${year}下載`;
      else folderName = bucket;
      const folder = path.join(root, `${year}相片`, folderName);
      for (const f of files) {
        await processFile(path.join(folder, f.name), ["chenwei", year, bucket, f.name], stats, existing);
      }
    }
  }
}

async function processFolderLib(idx, slug, stats, existing) {
  const lib = idx.libraries[slug];
  if (!lib) return;
  const root = path.join(PHOTOS_PARENT, LIB_FOLDERS[slug]);
  for (const [subpath, node] of Object.entries(lib.folders)) {
    const folder = subpath === "" ? root : path.join(root, ...subpath.split("/"));
    for (const f of node.files) {
      await processFile(path.join(folder, f.name), ["lib", slug, subpath, f.name], stats, existing);
    }
  }
}

async function uploadIndex() {
  const body = await fs.readFile(INDEX_PATH);
  await client.send(new PutObjectCommand({
    Bucket: BUCKET, Key: INDEX_KEY, Body: body, ContentType: "application/json",
  }));
  console.log(`✓ 上傳 ${INDEX_KEY}（${(body.length/1e6).toFixed(2)}MB）`);
}

async function main() {
  if (INDEX_ONLY) {
    client = makeClient();
    await uploadIndex();
    return;
  }

  const idx = JSON.parse(await fs.readFile(INDEX_PATH, "utf-8"));
  const targets = onlyLibs.length ? onlyLibs : ["chenwei", "training", "hongshi"];
  console.log(DRY ? "[DRY-RUN] 只統計，不上傳\n" : `同步縮圖到 R2 bucket=${BUCKET}\n`);
  console.log(`Widths: ${widths.join(", ")}`);
  console.log(`Libraries: ${targets.join(", ")}\n`);

  let existing = new Set();
  if (!DRY) {
    client = makeClient();
    console.log("列出 R2 既有 thumb …");
    existing = await loadExistingKeys();
    console.log(`R2 既有 thumb: ${existing.size} 個\n`);
  }

  const stats = { total: 0, uploaded: 0, skipped: 0, skippedExt: 0, skippedByList: 0, wouldUpload: 0, bytes: 0, errors: [] };
  const t0 = Date.now();
  for (const slug of targets) {
    console.log(`=== ${slug} ===`);
    if (slug === "chenwei") await processChenwei(idx, stats, existing);
    else await processFolderLib(idx, slug, stats, existing);
  }

  if (!DRY) await uploadIndex();

  const elapsed = (Date.now() - t0) / 1000;
  console.log(`\n=== Done in ${elapsed.toFixed(1)}s ===`);
  console.log(`Images:        ${stats.total}`);
  if (DRY) {
    const objs = stats.wouldUpload;
    // 粗估：480w ~25KB、1600w ~120KB；若兩寬都跑 → 平均 ~72KB/obj
    const avgKB = widths.length === 2 ? 72 : widths.includes(1600) ? 120 : 25;
    console.log(`要上傳物件:    ${objs}（${widths.length} 寬 × 圖片數）`);
    console.log(`估計容量:      ~${(objs * avgKB / 1e6).toFixed(2)} GB（粗估 avg ${avgKB}KB/obj）`);
    console.log(`跳過(非圖/HEIC): ${stats.skippedExt}`);
  } else {
    console.log(`Uploaded:      ${stats.uploaded}`);
    console.log(`Already in R2: ${stats.skipped}`);
    console.log(`跳過(非圖/HEIC): ${stats.skippedExt}`);
    console.log(`Skiplist 跳過: ${stats.skippedByList}`);
    console.log(`Uploaded 容量: ${(stats.bytes/1e6).toFixed(0)} MB`);
    console.log(`Errors:        ${stats.errors.length}`);
    if (stats.errors.length) {
      console.log("\nFirst 10 errors:");
      for (const e of stats.errors.slice(0, 10)) console.log(`  ${e}`);
    }
  }
}

main().catch((e) => {
  console.error("FATAL:", e);
  process.exit(1);
});
