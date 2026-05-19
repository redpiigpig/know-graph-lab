#!/usr/bin/env node
/**
 * Pre-warm photo thumbnails: walk photo_index.json and generate 480w + 1600w
 * webp for every renderable image into .cache/thumbs/. After this script,
 * 整個 /photos 任何月份首次點開都是 cache hit，毫秒級顯示。
 *
 * 用法：
 *   node scripts/prewarm_thumbs.mjs                 # 全 chenwei + training + hongshi
 *   node scripts/prewarm_thumbs.mjs chenwei         # 只跑 chenwei
 *   node scripts/prewarm_thumbs.mjs --widths=480    # 只跑 grid 寬度
 *
 * 進度寫到 stdout，cache 失敗（如 HEIC 沒 libheif）逐檔印 warning 但不中止。
 */
import crypto from "node:crypto";
import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import sharp from "sharp";

const REPO = path.resolve(import.meta.dirname, "..");
const INDEX_PATH = path.join(REPO, "scripts", "photo_index.json");
const CACHE_DIR = path.join(REPO, ".cache", "thumbs");
const PHOTOS_PARENT = "G:/我的雲端硬碟/資料/儲存資料夾";
const LIB_FOLDERS = { chenwei: "辰瑋相片", training: "訓練相片", hongshi: "弘誓相片" };

const SUPPORTED_EXTS = new Set([".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".avif", ".bmp"]);
const ALLOWED_WIDTHS = new Set([240, 480, 800, 1600]);

const argv = process.argv.slice(2);
const onlyLibs = argv.filter((a) => !a.startsWith("--"));
const widthArg = argv.find((a) => a.startsWith("--widths="));
const widths = widthArg
  ? widthArg.slice(9).split(",").map(Number).filter((w) => ALLOWED_WIDTHS.has(w))
  : [480, 1600];

function thumbCacheKey(parts) {
  return crypto.createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 32);
}
function cachePath(key, width) {
  return path.join(CACHE_DIR, key.slice(0, 2), `${key}_${width}.webp`);
}

const ensuredDirs = new Set();
async function ensureDir(p) {
  const dir = path.dirname(p);
  if (ensuredDirs.has(dir)) return;
  await fs.mkdir(dir, { recursive: true });
  ensuredDirs.add(dir);
}

async function genOne(origPath, key, width) {
  const cp = cachePath(key, width);
  if (fsSync.existsSync(cp)) return { skipped: true };
  try {
    const buffer = await sharp(origPath, { failOn: "none" })
      .rotate()
      .resize(width, null, { fit: "inside", withoutEnlargement: true })
      .webp({ quality: 80 })
      .toBuffer();
    await ensureDir(cp);
    await fs.writeFile(cp, buffer);
    return { generated: true };
  } catch (e) {
    return { error: e.message };
  }
}

async function processFile(origPath, keyParts, stats) {
  const ext = path.extname(origPath).toLowerCase();
  if (!SUPPORTED_EXTS.has(ext)) return;
  const key = thumbCacheKey(keyParts);
  for (const w of widths) {
    const r = await genOne(origPath, key, w);
    if (r.skipped) stats.skipped++;
    else if (r.generated) stats.generated++;
    else stats.errors.push(`${origPath} @${w}w: ${r.error}`);
  }
  stats.total++;
  if (stats.total % 100 === 0) {
    process.stdout.write(
      `  ${stats.total} files | gen=${stats.generated} skip=${stats.skipped} err=${stats.errors.length}\n`
    );
  }
}

async function processChenwei(idx, stats) {
  const lib = idx.libraries.chenwei;
  if (!lib) return;
  const root = path.join(PHOTOS_PARENT, LIB_FOLDERS.chenwei);
  for (const [year, yd] of Object.entries(lib.years)) {
    for (const [bucket, files] of Object.entries(yd.buckets)) {
      let folderName;
      if (/^(0[1-9]|1[0-2])$/.test(bucket)) folderName = `${year}.${bucket}`;
      else if (bucket === "screenshots") folderName = `${year}截圖`;
      else if (bucket === "downloads") folderName = `${year}下載`;
      else folderName = bucket; // 事件夾
      const folder = path.join(root, `${year}相片`, folderName);
      for (const f of files) {
        const orig = path.join(folder, f.name);
        await processFile(orig, ["chenwei", year, bucket, f.name], stats);
      }
    }
  }
}

async function processFolderLib(idx, slug, stats) {
  const lib = idx.libraries[slug];
  if (!lib) return;
  const root = path.join(PHOTOS_PARENT, LIB_FOLDERS[slug]);
  for (const [subpath, node] of Object.entries(lib.folders)) {
    const folder = subpath === "" ? root : path.join(root, ...subpath.split("/"));
    for (const f of node.files) {
      const orig = path.join(folder, f.name);
      await processFile(orig, ["lib", slug, subpath, f.name], stats);
    }
  }
}

async function main() {
  const idx = JSON.parse(await fs.readFile(INDEX_PATH, "utf-8"));
  const targets = onlyLibs.length ? onlyLibs : ["chenwei", "training", "hongshi"];
  console.log(`Pre-warming thumbs to ${CACHE_DIR}`);
  console.log(`Widths: ${widths.join(", ")}`);
  console.log(`Libraries: ${targets.join(", ")}\n`);

  const stats = { total: 0, generated: 0, skipped: 0, errors: [] };
  const t0 = Date.now();
  for (const slug of targets) {
    console.log(`=== ${slug} ===`);
    if (slug === "chenwei") await processChenwei(idx, stats);
    else await processFolderLib(idx, slug, stats);
  }
  const elapsed = (Date.now() - t0) / 1000;
  console.log(`\n=== Done in ${elapsed.toFixed(1)}s ===`);
  console.log(`Total files: ${stats.total}`);
  console.log(`Generated:   ${stats.generated}`);
  console.log(`Already in cache: ${stats.skipped}`);
  console.log(`Errors:      ${stats.errors.length}`);
  if (stats.errors.length) {
    console.log("\nFirst 10 errors:");
    for (const e of stats.errors.slice(0, 10)) console.log(`  ${e}`);
  }
}

main().catch((e) => {
  console.error("FATAL:", e);
  process.exit(1);
});
