import { stat } from "node:fs/promises";
import {
  isLibrarySlug,
  resolveLibFilePath,
  verifyLibFileSig,
} from "~/server/utils/photos";
import {
  getOrGenerateThumb,
  thumbCacheKey,
  ALLOWED_THUMB_WIDTHS,
} from "~/server/utils/photo-thumbs";

const SUPPORTED_EXTS = new Set([".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".avif", ".bmp"]);

export default defineEventHandler(async (event) => {
  const lib = getRouterParam(event, "lib") || "";
  if (!isLibrarySlug(lib)) {
    throw createError({ statusCode: 404, message: `Unknown library: ${lib}` });
  }
  const q = getQuery(event);
  const subpath = String(q.p || "");
  const n = String(q.n || "");
  const exp = String(q.exp || "");
  const sig = String(q.sig || "");
  const width = Number(q.w || 480);
  if (!n || !exp || !sig) {
    throw createError({ statusCode: 400, message: "Missing params" });
  }
  if (!ALLOWED_THUMB_WIDTHS.has(width)) {
    throw createError({ statusCode: 400, message: `Invalid w: ${width}` });
  }
  if (!verifyLibFileSig(lib, subpath, n, exp, sig)) {
    throw createError({ statusCode: 403, message: "Invalid or expired signature" });
  }
  const ext = n.slice(n.lastIndexOf(".")).toLowerCase();
  if (!SUPPORTED_EXTS.has(ext)) {
    throw createError({ statusCode: 415, message: "Unsupported" });
  }
  const filePath = resolveLibFilePath(lib, subpath, n);
  const st = await stat(filePath).catch(() => null);
  if (!st || !st.isFile()) {
    throw createError({ statusCode: 404, message: "Not found" });
  }
  const key = thumbCacheKey(["lib", lib, subpath, n]);
  const { buffer, cached } = await getOrGenerateThumb(filePath, width, key);
  setResponseHeaders(event, {
    "Content-Type": "image/webp",
    "Content-Length": String(buffer.length),
    "Cache-Control": "private, max-age=86400",
    "X-Thumb-Cache": cached ? "hit" : "miss",
  });
  return buffer;
});
