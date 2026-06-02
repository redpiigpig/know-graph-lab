/** GET /api/lang/courses/:id — 取得一門課程完整課表 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  const { data } = await supabase
    .from("lang_courses")
    .select("id, title, theme, level, syllabus, created_at")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();
  if (!data) throw createError({ statusCode: 404, message: "找不到課程" });
  return { course: data };
});
