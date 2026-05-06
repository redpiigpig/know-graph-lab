/**
 * GET /api/books/:id/tags
 * Returns the tags currently attached to this book, ordered by name.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const id = getRouterParam(event, "id");
  if (!id) throw createError({ statusCode: 400, message: "id required" });
  const supabase = getAdminClient();
  const { data, error } = await supabase
    .from("book_tags")
    .select("tag:tags(id, name, color)")
    .eq("book_id", id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return (data ?? [])
    .map((r: any) => r.tag)
    .filter(Boolean)
    .sort((a: any, b: any) => a.name.localeCompare(b.name));
});
