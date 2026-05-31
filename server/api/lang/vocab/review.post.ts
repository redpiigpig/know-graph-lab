/**
 * POST /api/lang/vocab/review
 * Body: { id, quality }  quality: 2(again)/3(hard)/4(good)/5(easy)
 * 套用 SM-2 更新單字的複習排程。
 */
import { sm2 } from "~/server/utils/srs";

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { id, quality } = (await readBody(event)) as { id: string; quality: number };
  if (!id) throw createError({ statusCode: 400, message: "缺少 id" });
  const q = Math.max(0, Math.min(5, Number(quality) || 0));

  const { data: v } = await supabase
    .from("lang_vocab")
    .select("ease_factor, interval_days, repetitions")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();
  if (!v) throw createError({ statusCode: 404, message: "找不到單字" });

  const r = sm2(
    { ease_factor: v.ease_factor ?? 2.5, interval_days: v.interval_days ?? 0, repetitions: v.repetitions ?? 0 },
    q
  );

  const { data: updated } = await supabase
    .from("lang_vocab")
    .update({
      ease_factor: r.ease_factor,
      interval_days: r.interval_days,
      repetitions: r.repetitions,
      mastery_level: r.mastery_level,
      next_review: r.next_review,
      last_reviewed: new Date().toISOString().slice(0, 10),
      updated_at: new Date().toISOString(),
    })
    .eq("id", id)
    .eq("user_id", user.id)
    .select("id, next_review, mastery_level")
    .single();

  return { ok: true, vocab: updated };
});
