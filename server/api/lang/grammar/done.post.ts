/** POST /api/lang/grammar/done  Body: { language, lessonId, done } — 標記某課完成/未完成 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { language, level, lessonId, done } = (await readBody(event)) as { language: string; level: string; lessonId: string; done: boolean };

  const { data: row } = await supabase
    .from("lang_grammar")
    .select("syllabus")
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("level", level)
    .single();
  if (!row?.syllabus?.length) throw createError({ statusCode: 404, message: "尚未建立大綱" });

  const syllabus = row.syllabus.map((s: any) => (s.id === lessonId ? { ...s, done: !!done } : s));
  await supabase
    .from("lang_grammar")
    .update({ syllabus, updated_at: new Date().toISOString() })
    .eq("user_id", user.id)
    .eq("language", language)
    .eq("level", level);

  return { ok: true };
});
