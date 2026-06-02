/**
 * POST /api/lang/daily/done
 * Body: { language, kind: 'task'|'reading'|'listening'|'speaking', id, done }
 * 切換今日任務/項目的完成狀態。
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, kind, id, done } = (await readBody(event)) as {
    language: string; kind: string; id: string; done: boolean;
  };
  const today = new Date().toISOString().slice(0, 10);
  const key = kind === "task" ? "tasks" : kind;

  const { data: row } = await supabase
    .from("lang_daily")
    .select("plan")
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("plan_date", today)
    .single();
  if (!row?.plan?.[key]) throw createError({ statusCode: 404, message: "找不到項目" });

  const plan = row.plan;
  plan[key] = plan[key].map((x: any) => (x.id === id ? { ...x, done: !!done } : x));
  await supabase
    .from("lang_daily")
    .update({ plan })
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("plan_date", today);

  return { ok: true };
});
