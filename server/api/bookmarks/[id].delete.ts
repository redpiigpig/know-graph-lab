/**
 * DELETE /api/bookmarks/:id
 * Removes one reading bookmark. Owner check enforced by user_id filter.
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const id = getRouterParam(event, "id");
  if (!id) throw createError({ statusCode: 400, message: "id required" });

  const supabase = getAdminClient();
  const { error } = await supabase
    .from("reading_bookmarks")
    .delete()
    .eq("id", id)
    .eq("user_id", user.id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { ok: true };
});
