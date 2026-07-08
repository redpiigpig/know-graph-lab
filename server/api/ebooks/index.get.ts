export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { category, subcategory, tagId, collection } = getQuery(event) as {
    category?: string;
    subcategory?: string;
    tagId?: string;
    collection?: string; // 未帶=圖書館(排除全集)；'collected-works'=只看全集；'all'=不過濾
  };

  // tagId filter: fetch the book_ids for this tag once, then narrow ebooks
  // via books.id IN (...). ebooks isn't tagged directly — its `books` row is.
  let bookIdFilter: string[] | null = null;
  if (tagId) {
    const { data, error } = await supabase
      .from("book_tags")
      .select("book_id")
      .eq("tag_id", tagId);
    if (error) throw createError({ statusCode: 500, message: error.message });
    bookIdFilter = (data ?? []).map((r) => r.book_id);
    if (!bookIdFilter.length) return []; // tag has no books → no ebooks
  }

  // Supabase PostgREST hard-caps responses at 1000 rows server-side
  // regardless of the client's Range header. Page through with .range()
  // until a short page comes back, then return everything.
  const PAGE = 1000;
  const out: any[] = [];
  for (let from = 0; ; from += PAGE) {
    let q = supabase
      .from("ebooks")
      .select("id, title, author, file_type, total_pages, chunk_count, created_at, category, subcategory, collection, quality_score, quality_flags, books(id, title, author)")
      .order("created_at", { ascending: false })
      .range(from, from + PAGE - 1);

    if (collection === "all") {
      // 不過濾
    } else if (collection) {
      q = q.eq("collection", collection);
    } else {
      q = q.is("collection", null);
    }
    if (category) q = q.eq("category", category);
    if (subcategory) q = q.ilike("subcategory", `${subcategory}%`);
    if (bookIdFilter) q = q.in("book_id", bookIdFilter);

    const { data, error } = await q;
    if (error) throw createError({ statusCode: 500, message: error.message });
    if (!data?.length) break;
    out.push(...data);
    if (data.length < PAGE) break;
  }
  return out;
});
