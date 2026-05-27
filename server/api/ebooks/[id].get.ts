import { loadChunk, loadToc } from "~/server/utils/ebook-chunks";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  const { page, includeToc } = getQuery(event) as { page?: string; includeToc?: string };

  const { data: ebook, error } = await supabase
    .from("ebooks")
    .select("id, title, author, file_type, chunk_count, total_pages, created_at, book_id, cover_url, subtitle, original_title, author_en, translator, publisher, publication_year, original_author, original_publish_year, category, subcategory, display_mode")
    .eq("id", id!)
    .single();

  if (error || !ebook) throw createError({ statusCode: 404, message: "找不到電子書" });

  const dbChunkCount = ebook.chunk_count ?? ebook.total_pages ?? 0;
  const chunkIndex = Math.max(0, (page ? parseInt(page) : 1) - 1);
  const [chunk, toc] = await Promise.all([
    dbChunkCount > 0 ? loadChunk(id!, chunkIndex) : Promise.resolve(null),
    includeToc === "1" && dbChunkCount > 0 ? loadToc(id!) : Promise.resolve(undefined),
  ]);

  // Translation pipeline only PATCHes ebooks.chunk_count at end-of-run, so a
  // book mid-translation reports a stale DB count and the reader's page nav
  // caps too low. Prefer the live JSONL length (via TOC) when it's bigger.
  const tocLen = Array.isArray(toc) ? toc.length : 0;
  const totalChunks = Math.max(dbChunkCount, tocLen);

  return {
    ...ebook,
    total_pages: totalChunks,
    toc,
    currentPage: chunk
      ? {
          id: `${id}-${chunkIndex}`,
          page_number: chunk.page_number ?? chunkIndex + 1,
          chapter_path: chunk.chapter_path,
          chunk_type: chunk.chunk_type,
          content: chunk.content,
          source_text: chunk.source_text ?? null,
          source_lang: chunk.source_lang ?? null,
          section_type: chunk.section_type ?? null,
          dh_number: chunk.dh_number ?? null,
          page_numbers: chunk.page_numbers ?? null,
        }
      : null,
  };
});
