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

  // Page through both tables — Supabase PostgREST hard-caps responses at
  // 1000 rows. Without this, library views silently truncated as the
  // catalog grew past 1000 books / excerpts.
  const PAGE = 1000;
  async function pageAll<T = any>(builder: () => any): Promise<T[]> {
    const out: T[] = [];
    for (let from = 0; ; from += PAGE) {
      const { data, error } = await builder().range(from, from + PAGE - 1);
      if (error) throw createError({ statusCode: 500, message: error.message });
      if (!data?.length) break;
      out.push(...data);
      if (data.length < PAGE) break;
    }
    return out;
  }

  const [books, excerpts] = await Promise.all([
    pageAll<any>(() => {
      let q = supabase
        .from("books")
        .select("id, title, author, translator, publish_place, publisher, publish_year, edition, category_id")
        .order("author");
      if (categoryIds) q = q.in("category_id", categoryIds);
      return q;
    }),
    pageAll<{ book_id: string }>(() =>
      supabase.from("excerpts").select("book_id").not("book_id", "is", null)
    ),
  ]);

  const countMap: Record<string, number> = {};
  excerpts.forEach((e) => {
    if (e.book_id) countMap[e.book_id] = (countMap[e.book_id] ?? 0) + 1;
  });

  return books.map((b) => ({ ...b, excerpt_count: countMap[b.id] ?? 0 }));
});
