// GET /api/works/dialogue-days?slug=<project_slug>
// 某條對話串的「每天一頁」清單（metadata 不含 html）。
// 私人內容：未登入回 { days: [], authed: false }。
export default defineEventHandler(async (event) => {
  const slug = String(getQuery(event).slug || "");
  if (!slug) throw createError({ statusCode: 400, message: "slug required" });

  const supabase = getAdminClient();
  const isAdmin = await getIsAdmin(event);

  // Unauthed: reveal only whether the thread has days (for the login prompt),
  // never the day list itself — content is private.
  if (!isAdmin) {
    const { count } = await supabase
      .from("dialogue_days")
      .select("day_date", { count: "exact", head: true })
      .eq("project_slug", slug);
    return { days: [], authed: false, hasDays: (count ?? 0) > 0 };
  }

  const { data, error } = await supabase
    .from("dialogue_days")
    .select("day_date, weekday, day_title, n_turns")
    .eq("project_slug", slug)
    .order("day_date", { ascending: true });
  if (error) throw createError({ statusCode: 500, message: error.message });

  return { days: data ?? [], authed: true, hasDays: (data ?? []).length > 0 };
});
