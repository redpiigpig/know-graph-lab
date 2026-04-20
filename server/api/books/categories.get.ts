export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const [{ data: cats, error: catErr }, { data: books, error: bookErr }] = await Promise.all([
    supabase
      .from("book_categories")
      .select("id, name, parent_id, display_order")
      .order("display_order"),
    supabase
      .from("books")
      .select("id, category_id")
      .not("category_id", "is", null),
  ]);

  if (catErr) throw createError({ statusCode: 500, message: catErr.message });

  // Count books per category
  const countMap: Record<string, number> = {};
  books?.forEach((b) => {
    if (b.category_id) countMap[b.category_id] = (countMap[b.category_id] ?? 0) + 1;
  });

  // Build tree: top-level categories with their children
  const allCats = (cats ?? []).map((c) => ({ ...c, book_count: countMap[c.id] ?? 0 }));
  const topLevel = allCats.filter((c) => !c.parent_id);
  const tree = topLevel.map((top) => ({
    ...top,
    children: allCats
      .filter((c) => c.parent_id === top.id)
      .map((child) => ({ ...child, children: [] })),
  }));

  return tree;
});
