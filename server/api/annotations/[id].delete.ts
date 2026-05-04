/**
 * DELETE /api/annotations/:id
 * Delete an annotation. Linked excerpt (if any) is left in place.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  if (!id) throw createError({ statusCode: 400, message: "Missing id" });

  const { error } = await supabase.from("annotations").delete().eq("id", id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { ok: true };
});
