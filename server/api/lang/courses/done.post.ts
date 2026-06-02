/** POST /api/lang/courses/done  Body: { courseId, lessonId, done } */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const { courseId, lessonId, done } = (await readBody(event)) as { courseId: string; lessonId: string; done: boolean };

  const { data: course } = await supabase
    .from("lang_courses")
    .select("syllabus")
    .eq("id", courseId)
    .eq("user_id", user.id)
    .single();
  if (!course?.syllabus?.length) throw createError({ statusCode: 404, message: "找不到課程" });

  const syllabus = course.syllabus.map((s: any) => (s.id === lessonId ? { ...s, done: !!done } : s));
  await supabase
    .from("lang_courses")
    .update({ syllabus, updated_at: new Date().toISOString() })
    .eq("id", courseId)
    .eq("user_id", user.id);
  return { ok: true };
});
