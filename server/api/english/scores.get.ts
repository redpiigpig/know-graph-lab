/**
 * GET /api/english/scores
 * 回傳每位使用者各課各測驗的「最佳百分比」：{ "3:vocab": 90, "3:comprehensive": 75, ... }
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();

  const { data } = await supabase
    .from("english_scores")
    .select("lesson_no, quiz_type, score, total")
    .eq("user_id", user.id);

  const best: Record<string, number> = {};
  for (const r of data ?? []) {
    const pct = Math.round((r.score / Math.max(1, r.total)) * 100);
    const key = `${r.lesson_no}:${r.quiz_type}`;
    if (best[key] === undefined || pct > best[key]) best[key] = pct;
  }
  return { best };
});
