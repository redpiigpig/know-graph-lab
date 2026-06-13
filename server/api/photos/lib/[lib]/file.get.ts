import fs from "node:fs";
import { stat } from "node:fs/promises";
import path from "node:path";
import {
  contentTypeFor, isLibrarySlug, resolveLibFilePath, verifyLibFileSig, photoBackend, classify,
} from "~/server/utils/photos";
import { getThumbFromR2, thumbCacheKey } from "~/server/utils/photo-thumbs";

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
  if (!n || !exp || !sig) {
    throw createError({ statusCode: 400, message: "Missing params" });
  }
  if (!verifyLibFileSig(lib, subpath, n, exp, sig)) {
    throw createError({ statusCode: 403, message: "Invalid or expired signature" });
  }

  // r2 後端（雲端）：原檔不在本機。圖片降級供 1600w 縮圖；影片無原檔 → 404（前端占位）。
  if (photoBackend() === "r2") {
    const cls = classify(n);
    if (cls?.kind !== "image") {
      throw createError({ statusCode: 404, message: "Original not available on cloud" });
    }
    const buffer = await getThumbFromR2(thumbCacheKey(["lib", lib, subpath, n]), 1600);
    if (!buffer) throw createError({ statusCode: 404, message: "Not found" });
    setResponseHeaders(event, {
      "Content-Type": "image/webp",
      "Content-Length": String(buffer.length),
      "Cache-Control": "public, max-age=86400",
    });
    return buffer;
  }

  const filePath = resolveLibFilePath(lib, subpath, n);
  const st = await stat(filePath).catch(() => null);
  if (!st || !st.isFile()) {
    throw createError({ statusCode: 404, message: "Not found" });
  }
  setResponseHeaders(event, {
    "Content-Type": contentTypeFor(path.extname(n).toLowerCase()),
    "Content-Length": String(st.size),
    "Cache-Control": "private, max-age=3600",
  });
  return sendStream(event, fs.createReadStream(filePath));
});
