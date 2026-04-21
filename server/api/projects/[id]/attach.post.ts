// POST /api/projects/:id/attach
// Attach excerpts to a book project
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const projectId = getRouterParam(event, "id")!;
  const body = await readBody(event) as { excerptIds?: string[] };
  const ids = body.excerptIds ?? [];

  if (!ids.length) return { inserted: 0 };

  const rows = ids.map((excerpt_id) => ({
    excerpt_id,
    book_project_id: projectId,
  }));

  const { error } = await supabase
    .from("excerpt_book_projects")
    .upsert(rows, { onConflict: "excerpt_id,book_project_id" });

  if (error) throw createError({ statusCode: 500, message: error.message });
  return { inserted: ids.length };
});
