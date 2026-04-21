export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  const { page } = getQuery(event) as { page?: string };

  const [{ data: ebook, error }, pageResult] = await Promise.all([
    supabase
      .from("ebooks")
      .select("id, title, author, file_type, total_pages, created_at")
      .eq("id", id!)
      .single(),
    page
      ? supabase
          .from("book_pages")
          .select("id, page_number, content")
          .eq("ebook_id", id!)
          .eq("page_number", parseInt(page))
          .single()
      : supabase
          .from("book_pages")
          .select("id, page_number, content")
          .eq("ebook_id", id!)
          .order("page_number")
          .limit(1)
          .single(),
  ]);

  if (error) throw createError({ statusCode: 404, message: "找不到電子書" });
  return { ...ebook, currentPage: pageResult.data };
});
