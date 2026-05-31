/** GET /api/lang/homework?language=en — 該語言的作業清單 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = getQuery(event).language as string;
  if (!language) throw createError({ statusCode: 400, message: "缺少 language" });

  const { data } = await supabase
    .from("lang_homework")
    .select("*")
    .eq("user_id", user.id)
    .eq("language", language)
    .order("created_at", { ascending: false });

  return { homework: data ?? [] };
});
