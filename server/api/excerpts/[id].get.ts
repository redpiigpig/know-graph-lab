export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const id = getRouterParam(event, "id");
  if (!id) {
    throw createError({ statusCode: 400, message: "Missing id" });
  }

  const { data, error } = await supabase
    .from("excerpts")
    .select(
      `id, title, content, chapter, page_number, created_at, updated_at,
       books(id, title, author, translator, publish_place, publisher, publish_year, edition),
       excerpt_book_projects(book_project_id, book_projects(id, name, type))`
    )
    .eq("id", id)
    .single();

  if (error || !data) {
    throw createError({ statusCode: 404, message: "Excerpt not found" });
  }

  return data;
});
