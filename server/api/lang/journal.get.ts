/**
 * GET /api/lang/journal?language=en&month=YYYY-MM
 * 回傳該月的：教練日誌條目 + 每日學習分鐘（給日曆著色與點閱）。
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const q = getQuery(event);
  const language = (q.language as string) || "en";
  const month = (q.month as string) || tzMonth(); // YYYY-MM
  const start = `${month}-01`;
  const endDate = new Date(new Date(start).getFullYear(), new Date(start).getMonth() + 1, 0);
  const end = endDate.toISOString().slice(0, 10);

  const [journalR, actR] = await Promise.all([
    supabase
      .from("lang_journal")
      .select("journal_date, summary, direction, minutes")
      .eq("user_id", user.id)
      .eq("language", language)
      .gte("journal_date", start)
      .lte("journal_date", end),
    supabase
      .from("lang_activity")
      .select("activity_date, skill, minutes")
      .eq("user_id", user.id)
      .eq("language", language)
      .gte("activity_date", start)
      .lte("activity_date", end),
  ]);

  // 每日分鐘聚合
  const byDate: Record<string, { total: number; skills: Record<string, number> }> = {};
  for (const a of actR.data ?? []) {
    const d = a.activity_date;
    if (!byDate[d]) byDate[d] = { total: 0, skills: {} };
    byDate[d].total += Number(a.minutes);
    byDate[d].skills[a.skill] = (byDate[d].skills[a.skill] || 0) + Number(a.minutes);
  }

  return {
    month,
    journals: journalR.data ?? [],
    days: Object.entries(byDate).map(([date, v]) => ({ date, minutes: Math.round(v.total * 10) / 10, skills: v.skills })),
  };
});
