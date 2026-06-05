/**
 * GET /api/lang/content/watch-stats?language=en
 * YouTube 觀看時長統計：今日、本月累積、總計、影片數。
 * 資料來源＝lang_activity（source=youtube，分析過與只記錄觀看都算）。
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";

  const today = tzToday();
  const monthStart = tzMonth() + "-01";

  const [actR, countR] = await Promise.all([
    // 本月以來的 youtube 活動（今日／本月都從這批算，省一次查詢）
    supabase
      .from("lang_activity")
      .select("activity_date, minutes")
      .eq("user_id", user.id)
      .eq("language", language)
      .eq("source", "youtube")
      .gte("activity_date", monthStart),
    // 影片總數（lang_content 的 youtube 筆數）
    supabase
      .from("lang_content")
      .select("id", { count: "exact", head: true })
      .eq("user_id", user.id)
      .eq("language", language)
      .eq("source_type", "youtube"),
  ]);

  let todayMin = 0;
  let monthMin = 0;
  for (const a of actR.data ?? []) {
    const m = Number(a.minutes) || 0;
    monthMin += m;
    if (a.activity_date === today) todayMin += m;
  }

  return {
    today: Math.round(todayMin),
    month: Math.round(monthMin),
    videoCount: countR.count ?? 0,
  };
});
