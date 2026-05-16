import fs from "node:fs";
import { stat } from "node:fs/promises";
import path from "node:path";
import { contentTypeFor, resolveFilePath, verifyFileSig } from "~/server/utils/photos";

export default defineEventHandler(async (event) => {
  const q = getQuery(event);
  const y = String(q.y || "");
  const m = String(q.m || "");
  const n = String(q.n || "");
  const exp = String(q.exp || "");
  const sig = String(q.sig || "");
  if (!y || !m || !n || !exp || !sig) {
    throw createError({ statusCode: 400, message: "Missing params" });
  }
  if (!verifyFileSig(y, m, n, exp, sig)) {
    throw createError({ statusCode: 403, message: "Invalid or expired signature" });
  }
  const filePath = resolveFilePath(y, m, n);
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
