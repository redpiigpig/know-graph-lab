export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { category, subcategory } = getQuery(event) as { category?: string; subcategory?: string };

  let q = supabase
    .from("ebooks")
    .select("id, title, author, file_type, total_pages, created_at, category, subcategory, books(id, title, author)")
    .order("created_at", { ascending: false });

  if (category) q = q.eq("category", category);
  if (subcategory) q = q.ilike("subcategory", `${subcategory}%`);

  const { data, error } = await q;
  if (error) throw createError({ statusCode: 500, message: error.message });
  return data ?? [];
});
