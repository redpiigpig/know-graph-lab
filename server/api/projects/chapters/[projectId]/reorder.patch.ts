// PATCH /api/projects/chapters/:projectId/reorder — 依陣列順序重設 sort_order（可 upsert 僅存在於摘文的章節）
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const projectId = getRouterParam(event, "projectId")!;
  const body = await readBody(event) as {
    chapter_codes?: string[];
    items?: { chapter_code: string; chapter_name?: string }[];
  };

  const items =
    body.items?.filter((x) => x.chapter_code?.trim()) ??
    (body.chapter_codes ?? []).filter((c) => c?.trim()).map((chapter_code) => ({ chapter_code, chapter_name: chapter_code }));

  if (!items.length) throw createError({ statusCode: 400, message: "items 或 chapter_codes 不可為空" });

  for (let i = 0; i < items.length; i++) {
    const chapter_code = items[i].chapter_code.trim();
    const chapter_name = (items[i].chapter_name ?? chapter_code).trim();
    const { error } = await supabase.from("project_chapters").upsert(
      {
        project_id: projectId,
        chapter_code,
        chapter_name,
        sort_order: i + 1,
      },
      { onConflict: "project_id,chapter_code" }
    );
    if (error) throw createError({ statusCode: 500, message: error.message });
  }

  return { success: true };
});
