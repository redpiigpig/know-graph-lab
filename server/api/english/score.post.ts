/**
 * POST /api/english/score
 * Body: { lesson_no, quiz_type, score, total }  記錄一次測驗分數（可重複測驗，全保留）。
 */
// 單元測驗 5 型（lesson_no 1..20）；複習測驗用 lesson_no=0 + quiz_type:
//   review_all（總複習）/ review_1_5 / review_6_10 / review_11_15 / review_16_20（每 5 單元段考）
const TYPES = ["vocab", "listening", "speaking", "sentence", "comprehensive"];
const isReviewType = (t: string) => /^review_(all|\d{1,2}_\d{1,2})$/.test(t);

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { lesson_no, quiz_type, score, total } = (await readBody(event)) as {
    lesson_no: number;
    quiz_type: string;
    score: number;
    total: number;
  };

  if (!Number.isInteger(lesson_no) || lesson_no < 0 || lesson_no > 20)
    throw createError({ statusCode: 400, message: "lesson_no 不正確" });
  if (!TYPES.includes(quiz_type) && !isReviewType(quiz_type))
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
