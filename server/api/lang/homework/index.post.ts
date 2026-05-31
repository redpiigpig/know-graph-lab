/** POST /api/lang/homework — 手動新增一份作業（教練聊天中也會自動建立） */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();
  const body = (await readBody(event)) as {
    language: string;
    topic: string;
    prompt: string;
    hw_type?: string;
    due_date?: string;
  };
  if (!body.language || !body.prompt) throw createError({ statusCode: 400, message: "缺少必要欄位" });

  const { data, error } = await supabase
    .from("lang_homework")
    .insert({
      user_id: user.id,
      language: body.language,
      topic: body.topic ?? "練習",
      prompt: body.prompt,
      hw_type: body.hw_type ?? "writing",
      due_date: body.due_date ?? null,
      status: "assigned",
    })
    .select("*")
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { homework: data };
});
