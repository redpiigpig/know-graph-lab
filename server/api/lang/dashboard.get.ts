/**
 * GET /api/lang/dashboard?language=en
 * 聚合儀表板資料：進度、四技能時間（近 30 天 + 今日 + 近 7 天）、單字統計、CEFR 曲線、目標倒數。
 */
const SKILLS = ["listening", "speaking", "reading", "writing"];

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";

  const today = tzToday();
  const from30 = tzDaysAgo(29);
  const from7 = tzDaysAgo(6);

  const [profileR, progressR, activityR, levelR, vocabAllR, vocabDueR] = await Promise.all([
    supabase.from("lang_profile").select("*").eq("user_id", user.id).single(),
    supabase.from("lang_progress").select("*").eq("user_id", user.id).eq("language", language).single(),
    supabase
      .from("lang_activity")
      .select("activity_date, skill, minutes")
      .eq("user_id", user.id)
      .eq("language", language)
      .gte("activity_date", from30),
    supabase
      .from("lang_level_history")
      .select("level, cefr_score, scores, assessed_at, method")
      .eq("user_id", user.id)
      .eq("language", language)
      .order("assessed_at", { ascending: true }),
    supabase
      .from("lang_vocab")
      .select("mastery_level", { count: "exact" })
      .eq("user_id", user.id)
      .eq("language", language),
    supabase
      .from("lang_vocab")
      .select("id", { count: "exact", head: true })
      .eq("user_id", user.id)
      .eq("language", language)
      .lte("next_review", today),
  ]);

  const activity = activityR.data ?? [];

  // 每日總分鐘（近 30 天，補滿空日）
  const byDate: Record<string, number> = {};
  const bySkill: Record<string, { today: number; week: number; total30: number }> = {};
  for (const s of SKILLS) bySkill[s] = { today: 0, week: 0, total30: 0 };

  for (const a of activity) {
    const m = Number(a.minutes) || 0;
    byDate[a.activity_date] = (byDate[a.activity_date] || 0) + m;
    if (bySkill[a.skill]) {
      bySkill[a.skill].total30 += m;
      if (a.activity_date >= from7) bySkill[a.skill].week += m;
      if (a.activity_date === today) bySkill[a.skill].today += m;
    }
  }

  const dailySeries: { date: string; minutes: number }[] = [];
  for (let i = 29; i >= 0; i--) {
    const d = tzDaysAgo(i);
    dailySeries.push({ date: d, minutes: Math.round((byDate[d] || 0) * 10) / 10 });
  }
  const todayMinutes = Math.round((byDate[today] || 0) * 10) / 10;

  // 單字熟練度分布
  const masteryDist = [0, 0, 0, 0, 0, 0];
  for (const v of vocabAllR.data ?? []) {
    const lvl = Math.min(5, Math.max(0, v.mastery_level || 0));
    masteryDist[lvl]++;
  }

  // 目標倒數
  const profile = profileR.data ?? null;
  let daysToExam: number | null = null;
  if (profile?.exam_date) {
    daysToExam = Math.ceil((new Date(profile.exam_date).getTime() - Date.now()) / 86400000);
  }

  return {
    profile,
    progress: progressR.data ?? { level: "B2", streak_days: 0, total_minutes: 0, last_active: null },
    todayMinutes,
    dailyGoal: profile?.daily_goal_minutes ?? 90,
    bySkill,
    dailySeries,
    vocab: {
      total: vocabAllR.count ?? 0,
      dueToday: vocabDueR.count ?? 0,
      masteryDist,
    },
    levelHistory: levelR.data ?? [],
    daysToExam,
  };
});
