/**
 * POST /api/excerpts
 * Create a new excerpt
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event);

  const { content, title, book_id, chapter, page_number } = body;
  if (!content?.trim()) throw createError({ statusCode: 400, message: "content is required" });

  const { data, error } = await supabase
    .from("excerpts")
    .insert({ content, title: title || null, book_id: book_id || null, chapter: chapter || null, page_number: page_number || null })
    .select()
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
