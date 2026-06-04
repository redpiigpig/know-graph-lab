// GET /api/works/dialogue-days/<date>?slug=<project_slug>
// 單日對話全文 html + 前一天/後一天日期（給 reader 翻頁）。私人，需登入。
export default defineEventHandler(async (event) => {
  const date = getRouterParam(event, "date");
  const slug = String(getQuery(event).slug || "");
  if (!date || !slug) throw createError({ statusCode: 400, message: "date & slug required" });

  const isAdmin = await getIsAdmin(event);
  if (!isAdmin) throw createError({ statusCode: 401, message: "Unauthorized" });

  const supabase = getAdminClient();

  const { data: day, error } = await supabase
    .from("dialogue_days")
    .select("day_date, weekday, day_title, html, n_turns")
    .eq("project_slug", slug)
    .eq("day_date", date)
    .maybeSingle();
  if (error) throw createError({ statusCode: 500, message: error.message });
  if (!day) throw createError({ statusCode: 404, message: "day not found" });

  // 鄰日（給上一頁/下一頁）
  const [{ data: prev }, { data: next }] = await Promise.all([
    supabase
      .from("dialogue_days")
      .select("day_date")
      .eq("project_slug", slug)
      .lt("day_date", date)
      .order("day_date", { ascending: false })
      .limit(1)
      .maybeSingle(),
    supabase
      .from("dialogue_days")
      .select("day_date")
      .eq("project_slug", slug)
      .gt("day_date", date)
      .order("day_date", { ascending: true })
      .limit(1)
      .maybeSingle(),
  ]);

  return {
    day,
    prev: prev?.day_date ?? null,
    next: next?.day_date ?? null,
  };
});
