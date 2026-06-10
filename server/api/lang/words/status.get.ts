/**
 * GET /api/lang/words/status?language=en
 * 回傳該語言所有已標記詞的狀態 map（word → known|learning），給閱讀器著色用。
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const language = (getQuery(event).language as string) || "en";
  const { data } = await supabase
    .from("lang_word_status")
    .select("word, status")
    .eq("user_id", user.id)
    .eq("language", language);
  const statuses: Record<string, string> = {};
  for (const r of data ?? []) statuses[r.word.toLowerCase()] = r.status;
  return { statuses };
});
