export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");

  const [{ data: book, error: bookErr }, { data: excerpts, error: excErr }] =
    await Promise.all([
      supabase
        .from("books")
        .select("id, title, author, translator, publish_place, publisher, publish_year, edition, created_at")
        .eq("id", id!)
        .single(),
      supabase
        .from("excerpts")
        .select("id, title, content, chapter, page_number, created_at")
        .eq("book_id", id!)
        .order("chapter")
        .order("created_at"),
    ]);

  if (bookErr) throw createError({ statusCode: 404, message: "Book not found" });
  if (excErr) throw createError({ statusCode: 500, message: excErr.message });

  return { ...book, excerpts: excerpts ?? [] };
});
