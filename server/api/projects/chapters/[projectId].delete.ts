// DELETE /api/projects/chapters/:projectId?chapter_code=XXX
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const projectId = getRouterParam(event, "projectId")!;
  const { chapter_code } = getQuery(event) as { chapter_code?: string };
  const chapterCode = decodeURIComponent((chapter_code ?? "").trim());

  if (!chapterCode || chapterCode === "（未分章）") {
    throw createError({ statusCode: 400, message: "無效的章節代碼" });
  }

  const { data: rows, error: selErr } = await supabase
    .from("excerpts")
    .select("id, excerpt_book_projects!inner(book_project_id)")
    .eq("chapter", chapterCode)
    .eq("excerpt_book_projects.book_project_id", projectId);

  if (selErr) throw createError({ statusCode: 500, message: selErr.message });

  const ids = (rows ?? []).map((r: any) => r.id).filter(Boolean);
  if (ids.length) {
    const { error: upErr } = await supabase.from("excerpts").update({ chapter: null }).in("id", ids);
    if (upErr) throw createError({ statusCode: 500, message: upErr.message });
  }

  const { error: delErr } = await supabase
    .from("project_chapters")
    .delete()
    .eq("project_id", projectId)
    .eq("chapter_code", chapterCode);

  if (delErr) throw createError({ statusCode: 500, message: delErr.message });
  return { success: true, detached_excerpts: ids.length };
});
