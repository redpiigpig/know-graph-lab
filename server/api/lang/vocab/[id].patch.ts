/** PATCH /api/lang/vocab/[id] — 更新單字（熟練度 / 釋義 / SRS 複習日） */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  const body = (await readBody(event)) as Record<string, any>;

  const allowed: Record<string, any> = {};
  for (const k of ["word", "reading", "meaning", "example", "part_of_speech", "mastery_level", "next_review"]) {
    if (k in body) allowed[k] = body[k];
  }
  allowed.updated_at = new Date().toISOString();

  const { data, error } = await supabase
    .from("lang_vocab")
    .update(allowed)
    .eq("id", id)
    .eq("user_id", user.id)
    .select("*")
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { vocab: data };
});
