export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const { data, error } = await supabase
    .from("ebooks")
    .select("id, title, author, file_type, total_pages, created_at, books(id, title, author)")
    .order("created_at", { ascending: false });

  if (error) throw createError({ statusCode: 500, message: error.message });
  return data ?? [];
});
