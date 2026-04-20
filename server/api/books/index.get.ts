export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { categoryId } = getQuery(event) as { categoryId?: string };

  // When filtering by a parent category, also include child categories
  let categoryIds: string[] | null = null;
  if (categoryId) {
    const { data: children } = await supabase
      .from("book_categories")
      .select("id")
      .eq("parent_id", categoryId);
    const childIds = (children ?? []).map((c) => c.id);
    categoryIds = [categoryId, ...childIds];
  }

  let query = supabase
    .from("books")
    .select("id, title, author, translator, publish_place, publisher, publish_year, edition, category_id")
    .order("author");

  if (categoryIds) {
    query = query.in("category_id", categoryIds);
  }

  const [{ data: books, error }, { data: excerpts }] = await Promise.all([
    query,
    supabase.from("excerpts").select("book_id").not("book_id", "is", null),
  ]);

  if (error) throw createError({ statusCode: 500, message: error.message });

  const countMap: Record<string, number> = {};
  excerpts?.forEach((e) => {
    if (e.book_id) countMap[e.book_id] = (countMap[e.book_id] ?? 0) + 1;
  });

  return (books ?? []).map((b) => ({ ...b, excerpt_count: countMap[b.id] ?? 0 }));
});
