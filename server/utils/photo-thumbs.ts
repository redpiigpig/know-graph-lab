import crypto from "node:crypto";
import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import sharp from "sharp";

// Disk cache for resized photo thumbnails.
// 第一次 cold-render 約 100-300 ms / 張（sharp + libvips 處理 iPhone JPG），結果存進
// .cache/thumbs/ 內。第二次起直接讀本機 webp（毫秒級），等同 Google Photos 體感。
//
// Cache key 純粹基於 (kind|year|segment|name|width) hash + 副檔名固定 webp，所以
// 同一原檔不同寬度有不同檔。原檔被刪不會自動清快取（accepted trade-off — Drive
// 30 天垃圾桶 + 手動清 .cache/thumbs/ 都行）。

const THUMB_CACHE_DIR = path.resolve(process.cwd(), ".cache", "thumbs");

// 允許的寬度白名單（限制 enumeration、保護 cache 不爆增）
export const ALLOWED_THUMB_WIDTHS = new Set([240, 480, 800, 1600]);

export function thumbCacheKey(parts: string[]): string {
  return crypto.createHash("sha256").update(parts.join("|")).digest("hex").slice(0, 32);
}

function cachePath(key: string, width: number): string {
  // 把 hash 前 2 char 當子資料夾分桶，避免單一資料夾百萬檔
  return path.join(THUMB_CACHE_DIR, key.slice(0, 2), `${key}_${width}.webp`);
}

let dirEnsuredFor = new Set<string>();
async function ensureDir(p: string) {
  const dir = path.dirname(p);
  if (dirEnsuredFor.has(dir)) return;
  await fs.mkdir(dir, { recursive: true });
  dirEnsuredFor.add(dir);
}

export async function getOrGenerateThumb(
  origPath: string,
  width: number,
  cacheKey: string,
): Promise<{ buffer: Buffer; cached: boolean }> {
  if (!ALLOWED_THUMB_WIDTHS.has(width)) {
    throw createError({ statusCode: 400, message: `Invalid width: ${width}` });
  }
  const cp = cachePath(cacheKey, width);

  // 1. cache hit
  try {
    const buffer = await fs.readFile(cp);
    return { buffer, cached: true };
  } catch { /* cache miss → generate */ }

  // 2. generate via sharp
  const buffer = await sharp(origPath, { failOn: "none" })
    .rotate() // honor EXIF orientation flag
    .resize(width, null, { fit: "inside", withoutEnlargement: true })
    .webp({ quality: 80 })
    .toBuffer();

  // 3. async-write to cache (fire-and-forget; the response doesn't wait)
  ensureDir(cp)
    .then(() => fs.writeFile(cp, buffer))
    .catch((e) => console.warn("[thumb] cache write failed:", cp, e));

  return { buffer, cached: false };
}

/** 同步寫版（給 prewarm script 用，要確認真的寫到 disk） */
export async function generateThumbToCache(
  origPath: string,
  width: number,
  cacheKey: string,
): Promise<{ generated: boolean; path: string }> {
  if (!ALLOWED_THUMB_WIDTHS.has(width)) {
    throw new Error(`Invalid width: ${width}`);
  }
  const cp = cachePath(cacheKey, width);
  if (fsSync.existsSync(cp)) {
    return { generated: false, path: cp };
  }
  const buffer = await sharp(origPath, { failOn: "none" })
    .rotate()
    .resize(width, null, { fit: "inside", withoutEnlargement: true })
    .webp({ quality: 80 })
    .toBuffer();
  await ensureDir(cp);
  await fs.writeFile(cp, buffer);
  return { generated: true, path: cp };
}
