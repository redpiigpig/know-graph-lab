// POST /api/projects/chapters/:projectId — 新增章節／主題（project_chapters）
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const projectId = getRouterParam(event, "projectId")!;
  const body = await readBody(event) as { chapter_code?: string; chapter_name?: string; sort_order?: number };

  const code = (body.chapter_code ?? body.chapter_name ?? "").trim();
  if (!code) throw createError({ statusCode: 400, message: "請提供章節代碼或主題名稱" });
  const chapter_name = (body.chapter_name ?? code).trim();

  const { data: dup } = await supabase
    .from("project_chapters")
    .select("chapter_code")
    .eq("project_id", projectId)
    .eq("chapter_code", code)
    .maybeSingle();

  if (dup) throw createError({ statusCode: 409, message: "此章節／主題已存在" });

  let sort_order = body.sort_order;
  if (typeof sort_order !== "number" || Number.isNaN(sort_order)) {
    const { data: last } = await supabase
      .from("project_chapters")
      .select("sort_order")
      .eq("project_id", projectId)
      .order("sort_order", { ascending: false })
      .limit(1);
    sort_order = ((last?.[0] as { sort_order?: number })?.sort_order ?? 0) + 1;
  }

  const { error } = await supabase.from("project_chapters").insert({
    project_id: projectId,
    chapter_code: code,
    chapter_name,
    sort_order,
  });

  if (error) throw createError({ statusCode: 500, message: error.message });
  return { success: true, chapter_code: code };
});
