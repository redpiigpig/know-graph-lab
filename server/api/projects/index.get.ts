// GET /api/projects?type=待寫著作
// Lists all book_projects, optionally filtered by type, with excerpt count
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { type } = getQuery(event) as { type?: string };

  let q = supabase
    .from("book_projects")
    .select("id, name, type, description, created_at")
    .order("created_at");

  if (type) q = q.eq("type", type);

  const { data, error } = await q;
  if (error) throw createError({ statusCode: 500, message: error.message });

  // Attach excerpt counts
  const result = await Promise.all(
    (data ?? []).map(async (proj) => {
      const { count } = await supabase
        .from("excerpt_book_projects")
        .select("excerpt_id", { count: "exact", head: true })
        .eq("book_project_id", proj.id);

      // Also get distinct source books used
      const { data: junc } = await supabase
        .from("excerpt_book_projects")
        .select("excerpts(book_id)")
        .eq("book_project_id", proj.id);

      const bookIds = new Set(
        (junc ?? []).map((j: any) => j.excerpts?.book_id).filter(Boolean)
      );

      return { ...proj, excerpt_count: count ?? 0, book_count: bookIds.size };
    })
  );

  return result;
});
