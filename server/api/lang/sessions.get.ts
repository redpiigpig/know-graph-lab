/** GET /api/lang/sessions?language=en — 該語言的對話 session 清單 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = getQuery(event).language as string;
  if (!language) throw createError({ statusCode: 400, message: "缺少 language" });

  const { data } = await supabase
    .from("lang_sessions")
    .select("id, title, summary, message_count, created_at, updated_at")
    .eq("user_id", user.id)
    .eq("language", language)
    .order("updated_at", { ascending: false });

  return { sessions: data ?? [] };
});
