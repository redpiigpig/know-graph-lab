/**
 * GET /api/ebooks/:id/reading-status
 * Returns { status: 'reading' | 'read' | null, updated_at?: string }.
 * Used by the reader page to render the bookshelf toggle button.
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const ebookId = getRouterParam(event, "id");
  if (!ebookId) throw createError({ statusCode: 400, message: "ebook id required" });

  const supabase = getAdminClient();
  const { data, error } = await supabase
    .from("user_reading_status")
    .select("status, updated_at")
    .eq("user_id", user.id)
    .eq("ebook_id", ebookId)
    .maybeSingle();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return data ?? { status: null };
});
