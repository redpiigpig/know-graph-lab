/**
 * DELETE /api/tags/:id
 * Deletes a tag. CASCADE drops all book_tags / excerpt_tags links automatically.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const id = getRouterParam(event, "id");
  if (!id) throw createError({ statusCode: 400, message: "id required" });
  const supabase = getAdminClient();
  const { error } = await supabase.from("tags").delete().eq("id", id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { ok: true };
});
