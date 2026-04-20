export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");

  const [{ data: book, error: bookErr }, { data: excerpts, error: excErr }] =
    await Promise.all([
      supabase
        .from("books")
        .select("id, title, author, translator, publish_place, publisher, publish_year, edition, category_id, created_at")
        .eq("id", id!)
        .single(),
      supabase
        .from("excerpts")
        .select(`
          id, title, content, chapter, page_number, created_at,
          excerpt_book_projects(
            book_projects(id, name, type)
          )
        `)
        .eq("book_id", id!)
        .order("chapter")
        .order("created_at"),
    ]);

  if (bookErr) throw createError({ statusCode: 404, message: "Book not found" });
  if (excErr) throw createError({ statusCode: 500, message: excErr.message });

  // Flatten project info onto each excerpt
  const enriched = (excerpts ?? []).map((e: any) => ({
    id: e.id,
    title: e.title,
    content: e.content,
    chapter: e.chapter,
    page_number: e.page_number,
    created_at: e.created_at,
    projects: (e.excerpt_book_projects ?? [])
      .map((ebp: any) => ebp.book_projects)
      .filter(Boolean),
  }));

  return { ...book, excerpts: enriched };
});
