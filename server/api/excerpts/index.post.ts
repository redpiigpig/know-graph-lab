/**
 * POST /api/excerpts
 * Create a new excerpt
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event);

  const { content, title, book_id, journal_article_id, chapter, page_number } = body as {
    content?: string;
    title?: string;
    book_id?: string | null;
    journal_article_id?: string | null;
    chapter?: string | null;
    page_number?: string | null;
  };
  if (!content?.trim()) throw createError({ statusCode: 400, message: "content is required" });
  if (book_id && journal_article_id) {
    throw createError({ statusCode: 400, message: "Cannot set both book_id and journal_article_id" });
  }

  const { data, error } = await supabase
    .from("excerpts")
    .insert({
      content,
      title: title || null,
      book_id: book_id || null,
      journal_article_id: journal_article_id || null,
      chapter: chapter || null,
      page_number: page_number || null,
    })
    .select()
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
