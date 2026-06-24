/**
 * POST /api/english/activity
 * Body: { minutes, source? }  記錄一段學習時間，更新 streak / 累計分鐘 / 最後活躍日。
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { minutes, source } = (await readBody(event)) as { minutes: number; source?: string };

  const mins = Math.max(0, Math.round((Number(minutes) || 0) * 100) / 100);
  if (mins <= 0) return { ok: true, skipped: true };

  const today = tzToday();

  await supabase.from("english_activity").insert({
    user_id: user.id,
    activity_date: today,
    minutes: mins,
    source: source ?? "lesson",
  });

  const { data: prog } = await supabase
    .from("english_progress")
    .select("streak_days, last_active, total_minutes")
    .eq("user_id", user.id)
    .single();

  let streak = 1;
  if (prog?.last_active) {
    const last = prog.last_active as string;
    if (last === today) streak = prog.streak_days || 1;
    else if (last === tzDaysAgo(1)) streak = (prog.streak_days || 0) + 1;
    else streak = 1;
  }
  const totalMin = Math.round(((prog?.total_minutes || 0) + mins) * 100) / 100;

  await supabase.from("english_progress").upsert(
    {
      user_id: user.id,
      streak_days: streak,
      last_active: today,
      total_minutes: totalMin,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "user_id" }
  );

  return { ok: true, streak_days: streak, total_minutes: totalMin };
});
