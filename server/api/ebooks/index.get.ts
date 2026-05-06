export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { category, subcategory } = getQuery(event) as { category?: string; subcategory?: string };

  // Supabase PostgREST hard-caps responses at 1000 rows server-side
  // regardless of the client's Range header. Page through with .range()
  // until a short page comes back, then return everything.
  const PAGE = 1000;
  const out: any[] = [];
  for (let from = 0; ; from += PAGE) {
    let q = supabase
      .from("ebooks")
      .select("id, title, author, file_type, total_pages, chunk_count, created_at, category, subcategory, books(id, title, author)")
      .order("created_at", { ascending: false })
      .range(from, from + PAGE - 1);

    if (category) q = q.eq("category", category);
    if (subcategory) q = q.ilike("subcategory", `${subcategory}%`);

    const { data, error } = await q;
    if (error) throw createError({ statusCode: 500, message: error.message });
    if (!data?.length) break;
    out.push(...data);
    if (data.length < PAGE) break;
  }
  return out;
});
