export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const { data, error } = await supabase
    .from("book_projects")
    .select("id, name, type, description, created_at")
    .order("type");

  if (error) {
    throw createError({ statusCode: 500, message: error.message });
  }

  return data ?? [];
});
