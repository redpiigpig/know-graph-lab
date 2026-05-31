/** DELETE /api/lang/vocab/[id] */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  const { error } = await supabase
    .from("lang_vocab")
    .delete()
    .eq("id", id)
    .eq("user_id", user.id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { ok: true };
});
