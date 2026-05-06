/**
 * POST /api/ebooks/:id/bookmarks
 * Body: { chunk_index: number }
 * Creates a "📅 read-to-here" marker at the given chunk for the current user.
 * Returns the new row.
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const ebookId = getRouterParam(event, "id");
  if (!ebookId) throw createError({ statusCode: 400, message: "ebook id required" });

  const body = (await readBody(event)) as { chunk_index?: number };
  if (body.chunk_index === undefined || body.chunk_index === null || body.chunk_index < 0)
    throw createError({ statusCode: 400, message: "chunk_index required (>= 0)" });

  const supabase = getAdminClient();
  const { data, error } = await supabase
    .from("reading_bookmarks")
    .insert({ user_id: user.id, ebook_id: ebookId, chunk_index: body.chunk_index })
    .select()
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
