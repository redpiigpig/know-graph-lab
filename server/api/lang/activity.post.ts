/**
 * POST /api/lang/activity
 * Body: { language, skill: listening|speaking|reading|writing, minutes, source?, detail? }
 * 記錄一段練習時間，並更新 streak / 累計分鐘 / 最後活躍日。
 */
const SKILLS = ["listening", "speaking", "reading", "writing"];

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, skill, minutes, source, detail } = (await readBody(event)) as {
    language: string;
    skill: string;
    minutes: number;
    source?: string;
    detail?: string;
  };

  if (!language || !SKILLS.includes(skill)) throw createError({ statusCode: 400, message: "language/skill 不正確" });
  const mins = Math.max(0, Math.round((Number(minutes) || 0) * 100) / 100);
  if (mins <= 0) return { ok: true, skipped: true };

  const today = new Date().toISOString().slice(0, 10);

  await supabase.from("lang_activity").insert({
    user_id: user.id,
    language,
    activity_date: today,
    skill,
    minutes: mins,
    source: source ?? "chat",
    detail: detail ?? null,
  });

  // 更新進度（streak + 累計分鐘 + 最後活躍）
  const { data: prog } = await supabase
    .from("lang_progress")
    .select("streak_days, last_active, total_minutes")
    .eq("user_id", user.id)
    .eq("language", language)
    .single();

  let streak = 1;
  if (prog?.last_active) {
    const last = prog.last_active as string;
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
    if (last === today) streak = prog.streak_days || 1;
    else if (last === yesterday) streak = (prog.streak_days || 0) + 1;
    else streak = 1;
  }
  const totalMin = Math.round(((prog?.total_minutes || 0) + mins) * 100) / 100;

  await supabase.from("lang_progress").upsert(
    {
      user_id: user.id,
      language,
      streak_days: streak,
      last_active: today,
      total_minutes: totalMin,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "user_id,language" }
  );

  return { ok: true, streak_days: streak, total_minutes: totalMin };
});
