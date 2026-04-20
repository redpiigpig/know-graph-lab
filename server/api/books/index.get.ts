export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const [{ data: books, error }, { data: excerpts }] = await Promise.all([
    supabase
      .from("books")
      .select("id, title, author, translator, publish_place, publisher, publish_year, edition")
      .order("author"),
    supabase.from("excerpts").select("book_id").not("book_id", "is", null),
  ]);

  if (error) throw createError({ statusCode: 500, message: error.message });

  const countMap: Record<string, number> = {};
  excerpts?.forEach((e) => {
    if (e.book_id) countMap[e.book_id] = (countMap[e.book_id] || 0) + 1;
  });

  return (books ?? []).map((b) => ({ ...b, excerpt_count: countMap[b.id] ?? 0 }));
});
