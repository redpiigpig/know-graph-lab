/** GET /api/lang/vocab/review?language=en&limit=20 — 取得今日到期的複習單字佇列 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const q = getQuery(event);
  const language = (q.language as string) || "en";
  const limit = Math.min(50, parseInt((q.limit as string) || "20"));
  const today = new Date().toISOString().slice(0, 10);

  const { data } = await supabase
    .from("lang_vocab")
    .select("id, word, reading, meaning, example, part_of_speech, mastery_level, next_review")
    .eq("user_id", user.id)
    .eq("language", language)
    .lte("next_review", today)
    .order("next_review", { ascending: true })
    .limit(limit);

  return { due: data ?? [] };
});
