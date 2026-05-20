// POST /api/concepts/unlink-excerpt
// Body: { excerpt_id, concept_id }
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as { excerpt_id?: string; concept_id?: string };
  if (!body.excerpt_id || !body.concept_id) {
    throw createError({ statusCode: 400, message: "excerpt_id and concept_id required" });
  }
  const { error } = await supabase
    .from("excerpt_concepts")
    .delete()
    .eq("excerpt_id", body.excerpt_id)
    .eq("concept_id", body.concept_id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { success: true };
});
