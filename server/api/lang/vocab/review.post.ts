/**
 * POST /api/lang/vocab/review
 * Body: { id, quality }  quality: 2(again)/3(hard)/4(good)/5(easy)
 * 套用 FSRS（v4.5）更新單字的複習排程（2026-06-05 由 SM-2 改 FSRS）。
 */
import { fsrs } from "~/server/utils/srs";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { id, quality } = (await readBody(event)) as { id: string; quality: number };
  if (!id) throw createError({ statusCode: 400, message: "缺少 id" });
  const q = Math.max(0, Math.min(5, Number(quality) || 0));

  const { data: v } = await supabase
    .from("lang_vocab")
    .select("difficulty, stability, last_reviewed, repetitions")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();
  if (!v) throw createError({ statusCode: 404, message: "找不到單字" });

  // 距上次複習過了幾天（給 FSRS 算 retrievability）；新卡或無紀錄 → 0
  const today = tzToday();
  let elapsed = 0;
  if (v.last_reviewed) {
    elapsed = Math.max(0, Math.round((new Date(today).getTime() - new Date(v.last_reviewed).getTime()) / 86400000));
  }

  const r = fsrs({ difficulty: v.difficulty ?? null, stability: v.stability ?? null }, q, elapsed);

  const { data: updated } = await supabase
    .from("lang_vocab")
    .update({
      difficulty: r.difficulty,
      stability: r.stability,
      interval_days: r.interval_days,
      repetitions: (v.repetitions ?? 0) + 1,
      mastery_level: r.mastery_level,
      next_review: r.next_review,
      last_reviewed: today,
      updated_at: new Date().toISOString(),
    })
    .eq("id", id)
    .eq("user_id", user.id)
    .select("id, next_review, mastery_level")
    .single();

  return { ok: true, vocab: updated };
});
