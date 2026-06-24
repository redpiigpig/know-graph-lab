/**
 * GET /api/english/progress
 * 回傳：今日學習分鐘、累計分鐘、連續天數。
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const today = tzToday();

  const [{ data: prog }, { data: acts }] = await Promise.all([
    supabase
      .from("english_progress")
      .select("total_minutes, streak_days, last_active")
      .eq("user_id", user.id)
      .single(),
    supabase
      .from("english_activity")
      .select("minutes")
      .eq("user_id", user.id)
      .eq("activity_date", today),
  ]);

  const todayMinutes =
    (acts ?? []).reduce((s: number, a: any) => s + (Number(a.minutes) || 0), 0);

  // streak 過期判定：最後活躍既非今天也非昨天 → 連續中斷，顯示 0
  let streak = prog?.streak_days || 0;
  if (prog?.last_active && prog.last_active !== today && prog.last_active !== tzDaysAgo(1)) {
    streak = 0;
  }

  return {
    today_minutes: Math.round(todayMinutes * 10) / 10,
    total_minutes: Math.round((prog?.total_minutes || 0) * 10) / 10,
    streak_days: streak,
  };
});
