/**
 * 書內插圖（scripts/epub_figures.py 在正文放回的 `![圖說](/api/ebooks/{id}/image/{檔名})`）。
 *
 *   GET /api/ebooks/{ebook_id}/image/image00147.jpeg
 *
 * 2026-10-01 使用者定：插圖只存在 Drive，不上 R2（全館五千多本書，R2 放不下）。
 * 所以這裡直接從 Drive 上的原 EPUB（ebooks.file_path）讀出那張圖——
 * 只有在本機跑網站時讀得到；正式站（Zeabur）讀不到 G:，回 404，閱讀器就只留圖說文字。
 *
 * ⚠️ id 與檔名都限定字元集；檔名只拿來比對 EPUB 內的 manifest，不拼路徑。
 */
import fs from "node:fs";
import path from "node:path";
import { serverSupabaseUser } from "#supabase/server";

const SAFE_NAME = /^[A-Za-z0-9][A-Za-z0-9._~-]{0,120}\.(jpe?g|png|gif|webp)$/i;
const SAFE_ID = /^[0-9a-f-]{36}$/i;

// 同一本書連續讀好幾張圖：開過的 EPUB 留著（最多 3 本，大書一本就上百 MB）
const cache = new Map<string, any>();

async function openEpub(file: string) {
  if (cache.has(file)) return cache.get(file);
  const { EPub } = await import("epub2");
  const epub = await EPub.createAsync(file);
  if (cache.size >= 3) cache.delete(cache.keys().next().value!);
  cache.set(file, epub);
  return epub;
}

export default defineEventHandler(async (event) => {
  const user = await serverSupabaseUser(event).catch(() => null);
  if (!user) throw createError({ statusCode: 401, message: "Unauthorized" });

  const id = getRouterParam(event, "id") || "";
  const name = path.basename(decodeURIComponent(getRouterParam(event, "name") || ""));
  if (!SAFE_ID.test(id) || !SAFE_NAME.test(name)) {
    throw createError({ statusCode: 400, message: "圖檔名格式錯誤" });
  }

  const { data } = await getAdminClient().from("ebooks").select("file_path").eq("id", id).single();
  const file = (data?.file_path as string | null) ?? "";
  if (!file || !/\.epub$/i.test(file) || !fs.existsSync(file)) {
    // 正式站讀不到 Drive：照使用者的決定，圖不顯示、只留圖說
    throw createError({ statusCode: 404, message: "插圖只存在 Drive，本機才看得到" });
  }

  const epub = await openEpub(file);
  const item = Object.values(epub.manifest as Record<string, any>)
    .find((m: any) => typeof m.href === "string" && path.posix.basename(m.href) === name);
  if (!item) throw createError({ statusCode: 404, message: "找不到這張圖" });
  const [buf, mime] = await epub.getImageAsync(item.id);
  setHeader(event, "Content-Type", mime || "image/jpeg");
  setHeader(event, "Cache-Control", "private, max-age=86400");
  return buf;
});
