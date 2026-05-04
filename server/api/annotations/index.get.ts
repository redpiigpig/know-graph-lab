/**
 * GET /api/annotations?ebookId=...&chunkIndex=...
 * List annotations for a specific chunk (or whole book if chunkIndex omitted).
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { ebookId, chunkIndex } = getQuery(event) as {
    ebookId?: string;
    chunkIndex?: string;
  };
  if (!ebookId) throw createError({ statusCode: 400, message: "ebookId is required" });

  let q = supabase
    .from("annotations")
    .select("id, ebook_id, chunk_index, selected_text, context_before, context_after, note, color, excerpt_id, created_at")
    .eq("ebook_id", ebookId)
    .order("chunk_index")
    .order("created_at");

  if (chunkIndex !== undefined) q = q.eq("chunk_index", parseInt(chunkIndex));

  const { data, error } = await q;
  if (error) throw createError({ statusCode: 500, message: error.message });
  return data ?? [];
});
