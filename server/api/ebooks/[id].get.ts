import { loadChunk, loadToc } from "~/server/utils/ebook-chunks";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  const { page, includeToc } = getQuery(event) as { page?: string; includeToc?: string };

  const { data: ebook, error } = await supabase
    .from("ebooks")
    .select("id, title, author, file_type, chunk_count, total_pages, created_at, book_id")
    .eq("id", id!)
    .single();

  if (error || !ebook) throw createError({ statusCode: 404, message: "找不到電子書" });

  const totalChunks = ebook.chunk_count ?? ebook.total_pages ?? 0;
  const chunkIndex = Math.max(0, (page ? parseInt(page) : 1) - 1);
  const [chunk, toc] = await Promise.all([
    totalChunks > 0 ? loadChunk(id!, chunkIndex) : Promise.resolve(null),
    includeToc === "1" && totalChunks > 0 ? loadToc(id!) : Promise.resolve(undefined),
  ]);

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
        }
      : null,
  };
});
