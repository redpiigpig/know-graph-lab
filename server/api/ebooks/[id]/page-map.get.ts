/**
 * GET /api/ebooks/{id}/page-map
 * Returns [{ chunk_index, page_number }] for every chunk, ordered by chunk_index.
 *
 * The original-PDF reader (/ebook/pdf/[id]) renders physical PDF pages via
 * pdf.js, but OCR chunk_index ≠ physical page when OCR skipped blank/cover
 * pages (e.g. 979 chunks for a 983-page scan). The chunk's page_number IS the
 * true physical page, so this map lets the client fetch the right OCR text for
 * whatever page pdf.js is showing.
 *
 * 2026-09-16 起改讀 JSONL，不再查 `ebook_chunks`。那張表在 Supabase 免費層
 * （500 MB）佔了 503 MB 要退場，而這裡要的 (chunk_index, page_number)
 * JSONL 本來就有 —— reader 的其他部分也早就只讀 JSONL。
 */
import { loadPageMap } from "~/server/utils/ebook-chunks";

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const id = getRouterParam(event, "id");
  if (!id) throw createError({ statusCode: 400, message: "缺少 ebook id" });
  return await loadPageMap(id);
});
