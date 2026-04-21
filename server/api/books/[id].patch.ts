// PATCH /api/books/:id — update original book info
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id")!;
  const body = await readBody(event) as {
    original_title?: string;
    original_publisher?: string;
    original_publish_year?: number;
    title?: string;
    author?: string;
  };

  const allowed = ["original_author", "original_title", "original_publisher", "original_publish_year", "title", "author"] as const;
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
