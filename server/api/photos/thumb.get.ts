import { stat } from "node:fs/promises";
import { resolveFilePath, verifyFileSig } from "~/server/utils/photos";
import {
  getOrGenerateThumb,
  thumbCacheKey,
  ALLOWED_THUMB_WIDTHS,
} from "~/server/utils/photo-thumbs";

const SUPPORTED_EXTS = new Set([".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".avif", ".bmp"]);

export default defineEventHandler(async (event) => {
  const q = getQuery(event);
  const y = String(q.y || "");
  const m = String(q.m || "");
  const n = String(q.n || "");
  const exp = String(q.exp || "");
  const sig = String(q.sig || "");
  const width = Number(q.w || 480);
  if (!y || !m || !n || !exp || !sig) {
    throw createError({ statusCode: 400, message: "Missing params" });
  }
  if (!ALLOWED_THUMB_WIDTHS.has(width)) {
    throw createError({ statusCode: 400, message: `Invalid w: ${width}` });
  }
  if (!verifyFileSig(y, m, n, exp, sig)) {
    throw createError({ statusCode: 403, message: "Invalid or expired signature" });
  }
  // 只縮 image；video 不該到這
  const ext = n.slice(n.lastIndexOf(".")).toLowerCase();
  if (!SUPPORTED_EXTS.has(ext)) {
    throw createError({ statusCode: 415, message: "Unsupported" });
  }
  const filePath = resolveFilePath(y, m, n);
  const st = await stat(filePath).catch(() => null);
  if (!st || !st.isFile()) {
    throw createError({ statusCode: 404, message: "Not found" });
  }
  const key = thumbCacheKey(["chenwei", y, m, n]);
  const { buffer, cached } = await getOrGenerateThumb(filePath, width, key);
  setResponseHeaders(event, {
    "Content-Type": "image/webp",
    "Content-Length": String(buffer.length),
    "Cache-Control": "private, max-age=86400",
    "X-Thumb-Cache": cached ? "hit" : "miss",
  });
  return buffer;
});
