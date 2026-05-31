/** GET /api/lang/memory?language=en — 取得統整記憶庫（教練對你的長期了解） */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";

  const { data } = await supabase
    .from("lang_memory")
    .select("memory, highlights, updated_at")
    .eq("user_id", user.id)
    .eq("language", language)
    .single();

  return { memory: data ?? { memory: "", highlights: {}, updated_at: null } };
});
