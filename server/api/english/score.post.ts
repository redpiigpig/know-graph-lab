/**
 * POST /api/english/score
 * Body: { lesson_no, quiz_type, score, total }  記錄一次測驗分數（可重複測驗，全保留）。
 */
const TYPES = ["vocab", "listening", "speaking", "sentence", "comprehensive"];

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { lesson_no, quiz_type, score, total } = (await readBody(event)) as {
    lesson_no: number;
    quiz_type: string;
    score: number;
    total: number;
  };

  if (!Number.isInteger(lesson_no) || lesson_no < 1 || lesson_no > 20)
    throw createError({ statusCode: 400, message: "lesson_no 不正確" });
  if (!TYPES.includes(quiz_type))
    throw createError({ statusCode: 400, message: "quiz_type 不正確" });

  const s = Math.max(0, Math.round(Number(score) || 0));
  const t = Math.max(1, Math.round(Number(total) || 1));

  await supabase.from("english_scores").insert({
    user_id: user.id,
    lesson_no,
    quiz_type,
    score: Math.min(s, t),
    total: t,
  });

  return { ok: true };
});
