import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";

const YEAR_RE = /^(\d{4})相片$/;
const MONTH_RE = /^(\d{4})\.(0[1-9]|1[0-2])$/;
const IMAGE_EXTS = new Set([
  ".jpg", ".jpeg", ".png", ".webp", ".gif", ".heic", ".heif", ".avif", ".bmp",
]);
const VIDEO_EXTS = new Set([".mp4", ".mov", ".m4v", ".webm", ".mkv"]);

export type PhotoKind = "image" | "video";
export type PhotoSource = "photo" | "screenshot" | "download" | "event";
export type Segment = string; // "01"-"12" | "screenshots" | "downloads" | <event-folder-name>

export interface PhotoFile {
  name: string;
  kind: PhotoKind;
  source: PhotoSource;
  ext: string;
  size: number;
  mtime: number;
  url: string;
}

// 多相簿支援：辰瑋（年-月-事件）/ 訓練（平鋪事件）/ 弘誓（民國年-事件）
export type LibrarySlug = "chenwei" | "training" | "hongshi";
export type LibraryLayout = "year-month" | "folders";

export interface LibraryMeta {
  slug: LibrarySlug;
  name: string;
  folder: string;
  layout: LibraryLayout;
}

export const LIBRARIES: Record<LibrarySlug, LibraryMeta> = {
  chenwei: { slug: "chenwei", name: "辰瑋相片", folder: "辰瑋相片", layout: "year-month" },
  training: { slug: "training", name: "訓練相片", folder: "訓練相片", layout: "folders" },
  hongshi: { slug: "hongshi", name: "弘誓相片", folder: "弘誓相片", layout: "folders" },
};

export function isLibrarySlug(s: string): s is LibrarySlug {
  return s === "chenwei" || s === "training" || s === "hongshi";
}

export function getPhotosRoot(): string {
  const root = useRuntimeConfig().photosRoot as string;
  if (!root) {
    throw createError({ statusCode: 500, message: "PHOTOS_ROOT not configured" });
  }
  return root;
}

/** Library root = photosRoot 的兄弟資料夾（皆位於儲存資料夾／下）。 */
export function getLibraryRoot(slug: LibrarySlug): string {
  const parent = path.dirname(getPhotosRoot());
  return path.join(parent, LIBRARIES[slug].folder);
}

function signingSecret(): string {
  const cfg = useRuntimeConfig();
  return (cfg.encryptionKey as string) || (cfg.supabaseServiceRoleKey as string) || "dev-secret";
}

function sign(payload: string): string {
  return crypto.createHmac("sha256", signingSecret()).update(payload).digest("base64url");
}

export function signFileUrl(year: string, segment: Segment, name: string, ttlSec = 3600): string {
  const exp = Math.floor(Date.now() / 1000) + ttlSec;
  const sig = sign(`${year}|${segment}|${name}|${exp}`);
  const q = new URLSearchParams({ y: year, m: segment, n: name, exp: String(exp), sig });
  return `/api/photos/file?${q.toString()}`;
}

export function verifyFileSig(year: string, segment: Segment, name: string, exp: string, sig: string): boolean {
  const expNum = Number(exp);
  if (!expNum || expNum < Math.floor(Date.now() / 1000)) return false;
  const expected = sign(`${year}|${segment}|${name}|${expNum}`);
  if (expected.length !== sig.length) return false;
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(sig));
}

export function classify(name: string): { kind: PhotoKind; ext: string } | null {
  const ext = path.extname(name).toLowerCase();
  if (IMAGE_EXTS.has(ext)) return { kind: "image", ext };
  if (VIDEO_EXTS.has(ext)) return { kind: "video", ext };
  return null;
}

export async function listYears(): Promise<string[]> {
  const root = getPhotosRoot();
  const entries = await fs.readdir(root, { withFileTypes: true });
  const years: string[] = [];
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const m = e.name.match(YEAR_RE);
    if (m) years.push(m[1]);
  }
  years.sort((a, b) => Number(b) - Number(a));
  return years;
}

export async function listMonths(year: string): Promise<string[]> {
  if (!/^\d{4}$/.test(year)) {
    throw createError({ statusCode: 400, message: "Invalid year" });
  }
  const dir = path.join(getPhotosRoot(), `${year}相片`);
  const entries = await fs.readdir(dir, { withFileTypes: true }).catch(() => []);
  const months: string[] = [];
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    const m = e.name.match(MONTH_RE);
    if (m && m[1] === year) months.push(m[2]);
  }
  months.sort();
  return months;
}

/** Resolve the absolute folder for a (year, segment) tuple. */
export function bucketDir(year: string, segment: Segment): string {
  if (!/^\d{4}$/.test(year)) {
    throw createError({ statusCode: 400, message: "Invalid year" });
  }
  const yearRoot = path.join(getPhotosRoot(), `${year}相片`);
  if (/^(0[1-9]|1[0-2])$/.test(segment)) {
    return path.join(yearRoot, `${year}.${segment}`);
  }
  if (segment === "screenshots") return path.join(yearRoot, `${year}截圖`);
  if (segment === "downloads") return path.join(yearRoot, `${year}下載`);
  // 事件資料夾：任意名稱，但必須是 yearRoot 的直接子資料夾且不能是 path traversal
  if (!segment || segment.includes("/") || segment.includes("\\") || segment.startsWith(".")) {
    throw createError({ statusCode: 400, message: `Invalid segment: ${segment}` });
  }
  return path.join(yearRoot, segment);
}

export function sourceForSegment(segment: Segment): PhotoSource {
  if (segment === "screenshots") return "screenshot";
  if (segment === "downloads") return "download";
  if (/^(0[1-9]|1[0-2])$/.test(segment)) return "photo";
  return "event";
}

/** List event subfolders under {year}相片 (non YYYY.MM, non 截圖/下載). */
export async function listEvents(year: string): Promise<{ name: string; count: number }[]> {
  if (!/^\d{4}$/.test(year)) {
    throw createError({ statusCode: 400, message: "Invalid year" });
  }
  const yearRoot = path.join(getPhotosRoot(), `${year}相片`);
  const entries = await fs.readdir(yearRoot, { withFileTypes: true }).catch(() => []);
  const monthRe = new RegExp(`^${year}\\.(0[1-9]|1[0-2])$`);
  const out: { name: string; count: number }[] = [];
  for (const e of entries) {
    if (!e.isDirectory()) continue;
    if (monthRe.test(e.name)) continue;
    if (e.name === `${year}截圖` || e.name === `${year}下載`) continue;
    if (e.name.startsWith(".")) continue;
    const sub = path.join(yearRoot, e.name);
    const subEntries = await fs.readdir(sub, { withFileTypes: true }).catch(() => []);
    let count = 0;
    for (const f of subEntries) if (f.isFile() && classify(f.name)) count++;
    out.push({ name: e.name, count });
  }
  out.sort((a, b) => a.name.localeCompare(b.name));
  return out;
}

export async function countBucket(year: string, segment: Segment): Promise<number> {
  const dir = bucketDir(year, segment);
  const entries = await fs.readdir(dir, { withFileTypes: true }).catch(() => []);
  let n = 0;
  for (const e of entries) {
    if (e.isFile() && classify(e.name)) n++;
  }
  return n;
}

/** @deprecated use bucketDir */
export const monthDir = bucketDir;
/** @deprecated use countBucket */
export const countMonth = countBucket;

export async function listFiles(year: string, segment: Segment): Promise<PhotoFile[]> {
  const dir = bucketDir(year, segment);
  const source = sourceForSegment(segment);
  const entries = await fs.readdir(dir, { withFileTypes: true }).catch(() => []);
  const out: PhotoFile[] = [];
  for (const e of entries) {
    if (!e.isFile()) continue;
    const meta = classify(e.name);
    if (!meta) continue;
    const stat = await fs.stat(path.join(dir, e.name));
    out.push({
      name: e.name,
      kind: meta.kind,
      source,
      ext: meta.ext,
      size: stat.size,
      mtime: stat.mtimeMs,
      url: signFileUrl(year, segment, e.name),
    });
  }
  out.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
  return out;
}

export function resolveFilePath(year: string, segment: Segment, name: string): string {
  const base = bucketDir(year, segment);
  const resolved = path.resolve(base, name);
  if (!resolved.startsWith(path.resolve(base) + path.sep) && resolved !== path.resolve(base)) {
    throw createError({ statusCode: 400, message: "Path traversal" });
  }
  return resolved;
}

// ===== 通用 folder browser（給 訓練 / 弘誓 用，辰瑋 仍走原本 year-month 路徑）=====

export interface FolderNode {
  name: string;
  fileCount: number;       // 直接子層的照片數
  subfolderCount: number;  // 直接子層的資料夾數
}

function validateSubpath(subpath: string): string[] {
  if (!subpath) return [];
  const segs = subpath.split("/").filter(Boolean);
  for (const s of segs) {
    if (s === "." || s === ".." || s.includes("\\")) {
      throw createError({ statusCode: 400, message: `Invalid path segment: ${s}` });
    }
  }
  return segs;
}

export function resolveLibFolder(slug: LibrarySlug, subpath: string): string {
  const root = getLibraryRoot(slug);
  const segs = validateSubpath(subpath);
  const resolved = path.resolve(root, ...segs);
  const rootResolved = path.resolve(root);
  if (resolved !== rootResolved && !resolved.startsWith(rootResolved + path.sep)) {
    throw createError({ statusCode: 400, message: "Path traversal" });
  }
  return resolved;
}

export async function listLibraryFolder(slug: LibrarySlug, subpath: string):
  Promise<{ folders: FolderNode[]; files: PhotoFile[] }>
{
  const dir = resolveLibFolder(slug, subpath);
  const entries = await fs.readdir(dir, { withFileTypes: true }).catch(() => []);
  const folders: FolderNode[] = [];
  const files: PhotoFile[] = [];
  for (const e of entries) {
    if (e.name.startsWith(".")) continue;
    if (e.isDirectory()) {
      const sub = path.join(dir, e.name);
      const subEntries = await fs.readdir(sub, { withFileTypes: true }).catch(() => []);
      let fileCount = 0, subfolderCount = 0;
      for (const f of subEntries) {
        if (f.isFile() && classify(f.name)) fileCount++;
        else if (f.isDirectory() && !f.name.startsWith(".")) subfolderCount++;
      }
      folders.push({ name: e.name, fileCount, subfolderCount });
    } else if (e.isFile()) {
      const meta = classify(e.name);
      if (!meta) continue;
      const stat = await fs.stat(path.join(dir, e.name));
      files.push({
        name: e.name,
        kind: meta.kind,
        source: "event",
        ext: meta.ext,
        size: stat.size,
        mtime: stat.mtimeMs,
        url: signLibFileUrl(slug, subpath, e.name),
      });
    }
  }
  folders.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
  files.sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));
  return { folders, files };
}

/** 計算 library 根目錄下的總照片數（遞迴）+ 第一層資料夾數。給 /photos 卡片用。 */
export async function summarizeLibrary(slug: LibrarySlug):
  Promise<{ totalFiles: number; topFolders: number }>
{
  const root = getLibraryRoot(slug);
  let totalFiles = 0;
  let topFolders = 0;

  async function walk(dir: string, depth: number) {
    const entries = await fs.readdir(dir, { withFileTypes: true }).catch(() => []);
    for (const e of entries) {
      if (e.name.startsWith(".")) continue;
      if (e.isDirectory()) {
        if (depth === 0) topFolders++;
        await walk(path.join(dir, e.name), depth + 1);
      } else if (e.isFile() && classify(e.name)) {
        totalFiles++;
      }
    }
  }
  await walk(root, 0);
  return { totalFiles, topFolders };
}

// ===== 多 library 的 signed URL（path-based，給訓練/弘誓用）=====

export function signLibFileUrl(slug: LibrarySlug, subpath: string, name: string, ttlSec = 3600): string {
  const exp = Math.floor(Date.now() / 1000) + ttlSec;
  const sig = sign(`lib|${slug}|${subpath}|${name}|${exp}`);
  const q = new URLSearchParams({ lib: slug, p: subpath, n: name, exp: String(exp), sig });
  return `/api/photos/lib/${slug}/file?${q.toString()}`;
}

export function verifyLibFileSig(slug: string, subpath: string, name: string, exp: string, sig: string): boolean {
  const expNum = Number(exp);
  if (!expNum || expNum < Math.floor(Date.now() / 1000)) return false;
  const expected = sign(`lib|${slug}|${subpath}|${name}|${expNum}`);
  if (expected.length !== sig.length) return false;
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(sig));
}

export function resolveLibFilePath(slug: LibrarySlug, subpath: string, name: string): string {
  const dir = resolveLibFolder(slug, subpath);
  const resolved = path.resolve(dir, name);
  if (!resolved.startsWith(path.resolve(dir) + path.sep) && resolved !== path.resolve(dir)) {
    throw createError({ statusCode: 400, message: "Path traversal" });
  }
  return resolved;
}

export function contentTypeFor(ext: string): string {
  switch (ext) {
    case ".jpg":
    case ".jpeg": return "image/jpeg";
    case ".png": return "image/png";
    case ".webp": return "image/webp";
    case ".gif": return "image/gif";
    case ".heic":
    case ".heif": return "image/heic";
    case ".avif": return "image/avif";
    case ".bmp": return "image/bmp";
    case ".mp4": return "video/mp4";
    case ".mov": return "video/quicktime";
    case ".m4v": return "video/x-m4v";
    case ".webm": return "video/webm";
    case ".mkv": return "video/x-matroska";
    default: return "application/octet-stream";
  }
}
