// PATCH /api/books/:id — update book metadata (incl. citation fields)
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id")!;
  const body = await readBody(event) as Record<string, unknown>;

  const allowed = [
    "title", "author", "translator", "editor",
    "publish_place", "publisher", "publish_year",
    "edition", "edition_number",
    "original_author", "original_title", "original_publisher", "original_publish_year",
    "isbn", "doi",
    "series_title", "series_number",
    "container_title", "container_editor",
    "pages", "url", "accessed_date", "language", "citation_key",
    "category_id",
  ] as const;

  const updates: Record<string, unknown> = {};
  for (const key of allowed) {
    if (body[key] !== undefined) updates[key] = body[key];
  }

  if (Object.keys(updates).length === 0)
    throw createError({ statusCode: 400, message: "No fields to update" });

  const { error } = await supabase.from("books").update(updates).eq("id", id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { success: true };
});
