/** GET /api/lang/vocab/review?language=en&limit=20 — 取得今日到期的複習單字佇列 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const q = getQuery(event);
  const language = (q.language as string) || "en";
  const limit = Math.min(50, parseInt((q.limit as string) || "20"));
  const today = new Date().toISOString().slice(0, 10);

  const cols = "id, word, reading, meaning, example, part_of_speech, mastery_level, next_review";
  const { data: dueRows } = await supabase
    .from("lang_vocab")
    .select(cols)
    .eq("user_id", user.id)
    .eq("language", language)
    .lte("next_review", today)
    .order("next_review", { ascending: true })
    .limit(limit);

  let queue = dueRows ?? [];
  // 到期不足時，從整個單字庫補進尚未精熟（mastery<5）的字，湊滿 limit
  if (queue.length < limit) {
    const have = new Set(queue.map((r: any) => r.id));
    const { data: fill } = await supabase
      .from("lang_vocab")
      .select(cols)
      .eq("user_id", user.id)
      .eq("language", language)
      .lt("mastery_level", 5)
      .order("mastery_level", { ascending: true })
      .limit(limit * 2);
    for (const r of fill ?? []) {
      if (queue.length >= limit) break;
      if (!have.has(r.id)) queue.push(r);
    }
  }

  // 給每張卡準備 4 選 1 的干擾選項（用其他字的釋義）
  const allMeanings = [...new Set(queue.map((r: any) => r.meaning).filter(Boolean))];
  const withOptions = queue.map((r: any) => {
    const distractors = allMeanings.filter((m) => m !== r.meaning).sort(() => 0.5 - Math.random()).slice(0, 3);
    const options = [r.meaning, ...distractors].sort(() => 0.5 - Math.random());
    return { ...r, options };
  });

  return { due: withOptions };
});
