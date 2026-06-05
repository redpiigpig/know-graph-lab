/** GET /api/lang/content?language=en — 過往沉浸內容清單 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";
  const { data } = await supabase
    .from("lang_content")
    .select("id, source_type, url, title, summary, analysis, session_id, created_at")
    .eq("user_id", user.id)
    .eq("language", language)
    .order("created_at", { ascending: false })
    .limit(30);
  return { content: data ?? [] };
});
