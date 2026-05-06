/**
 * GET /api/ebooks/:id/bookmarks
 * Returns the user's reading bookmarks for this book, ordered newest-first.
 * Reader uses these to draw date badges in the TOC sidebar and to decide
 * whether to auto-jump on first load (handled client-side).
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const ebookId = getRouterParam(event, "id");
  if (!ebookId) throw createError({ statusCode: 400, message: "ebook id required" });

  const supabase = getAdminClient();
  const { data, error } = await supabase
    .from("reading_bookmarks")
    .select("id, chunk_index, created_at")
    .eq("user_id", user.id)
    .eq("ebook_id", ebookId)
    .order("created_at", { ascending: false });
  if (error) throw createError({ statusCode: 500, message: error.message });
  return data ?? [];
});
