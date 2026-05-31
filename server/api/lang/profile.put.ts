/** PUT /api/lang/profile — 更新學習者檔案（onboarding / 設定頁） */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const body = (await readBody(event)) as Record<string, any>;

  const allowed: Record<string, any> = { user_id: user.id, updated_at: new Date().toISOString() };
  for (const k of [
    "display_name",
    "native_lang",
    "primary_language",
    "goal_level",
    "target_exam",
    "exam_date",
    "interests",
    "daily_goal_minutes",
    "onboarded",
  ]) {
    if (k in body) allowed[k] = body[k];
  }

  const { data, error } = await supabase
    .from("lang_profile")
    .upsert(allowed, { onConflict: "user_id" })
    .select("*")
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { profile: data };
});
