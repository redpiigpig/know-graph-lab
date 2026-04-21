export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");

  const [{ data: book, error: bookErr }, { data: excerpts, error: excErr }, { data: projChapters }] =
    await Promise.all([
      supabase
        .from("books")
        .select("id, title, author, translator, publish_place, publisher, publish_year, edition, original_author, original_title, original_publisher, original_publish_year, category_id, created_at")
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
      supabase.from("project_chapters").select("chapter_code"),
    ]);

  if (bookErr) throw createError({ statusCode: 404, message: "Book not found" });
  if (excErr) throw createError({ statusCode: 500, message: excErr.message });

  const projectChapterCodes = (projChapters ?? []).map((c: any) => c.chapter_code).filter(Boolean);

  // Flatten project info onto each excerpt
  const enriched = (excerpts ?? []).map((e: any) => ({
    // Hide project-derived chapter labels in library view.
    // Keep chapter only when it is likely original-book chapter.
    // (If it matches a known project chapter code and excerpt belongs to writing/article project, suppress it.)
    ...(() => {
      const projects = (e.excerpt_book_projects ?? []).map((ebp: any) => ebp.book_projects).filter(Boolean);
      const chapterRaw = e.chapter as string | null;
      const isProjectChapter = !!chapterRaw && projectChapterCodes.some((code: string) =>
        chapterRaw === code || chapterRaw.startsWith(`${code}：`) || chapterRaw.startsWith(`${code}:`)
      );
      const chapter = isProjectChapter ? null : chapterRaw;
      return { chapter, projects };
    })(),
    id: e.id,
    title: e.title,
    content: e.content,
    // In library view, chapter info must come from original excerpt only.
    // Do not map project chapter names (e.g. 千面上帝章節) onto source books.
    chapterName: "",
    page_number: e.page_number,
    created_at: e.created_at,
  }));

  return { ...book, excerpts: enriched, chapterNameMap: {} };
});
