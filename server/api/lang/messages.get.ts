/** GET /api/lang/messages?sessionId=... — 載入某 session 的對話歷史 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const sessionId = getQuery(event).sessionId as string;
  if (!sessionId) throw createError({ statusCode: 400, message: "缺少 sessionId" });

  // 驗證歸屬
  const { data: s } = await supabase
    .from("lang_sessions")
    .select("user_id")
    .eq("id", sessionId)
    .single();
  if (!s || s.user_id !== user.id) throw createError({ statusCode: 404, message: "找不到對話" });

  const { data } = await supabase
    .from("lang_messages")
    .select("id, role, content, translation, corrections, created_at")
    .eq("session_id", sessionId)
    .order("created_at", { ascending: true });

  return { messages: data ?? [] };
});
