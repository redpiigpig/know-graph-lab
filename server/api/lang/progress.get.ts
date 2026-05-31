/** GET /api/lang/progress — 所有語言的學習進度（給語言選擇頁顯示等級/連續天數） */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { data } = await supabase
    .from("lang_progress")
    .select("language, level, streak_days, last_active, total_minutes")
    .eq("user_id", user.id);
  return { progress: data ?? [] };
});
