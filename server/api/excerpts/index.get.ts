export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const { search, searchField, type, chapter, bookId } = getQuery(event) as {
    search?: string;
    searchField?: string;
    type?: string;
    chapter?: string;
    bookId?: string;
  };

  let query = supabase
    .from("excerpts")
    .select(
      `id, title, content, chapter, page_number, created_at,
       books(id, title, author),
       journal_articles(id, title, venue, author),
       excerpt_book_projects(book_project_id, book_projects(id, name, type))`
    )
    .order("chapter")
    .order("created_at", { ascending: true });

  if (bookId) query = query.eq("book_id", bookId);
  if (chapter) query = query.eq("chapter", chapter);

  const { data, error } = await query;

  if (error) {
    throw createError({ statusCode: 500, message: error.message });
  }

  let result = data ?? [];

  if (search?.trim()) {
    const q = search.trim().toLowerCase();
    result = result.filter(
      (e) => {
        const inTitle = e.title?.toLowerCase().includes(q);
        const inContent = e.content?.toLowerCase().includes(q);
        const inBook = (e.books as any)?.title?.toLowerCase().includes(q);
        const inAuthor = (e.books as any)?.author?.toLowerCase().includes(q);
        const ja = e.journal_articles as any;
        const inJournal = ja?.title?.toLowerCase().includes(q) || ja?.venue?.toLowerCase().includes(q);
        const inJaAuthor = ja?.author?.toLowerCase().includes(q);
        if (searchField === "title") return inTitle;
        if (searchField === "content") return inContent;
        if (searchField === "book") return inBook || inJournal;
        if (searchField === "author") return inAuthor || inJaAuthor;
        return inTitle || inContent || inBook || inAuthor || inJournal || inJaAuthor || e.chapter?.toLowerCase().includes(q);
      }
    );
  }

  if (type && type !== "全部") {
    result = result.filter((e) =>
      (e.excerpt_book_projects as any[])?.some(
        (ep) => (ep.book_projects as any)?.type === type
      )
    );
  }

  return result;
});
