// POST /api/books
// Create a new source book
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as {
    title?: string;
    author?: string;
    translator?: string;
    publish_year?: number | null;
    publisher?: string;
  };

  const title = body.title?.trim();
  if (!title) throw createError({ statusCode: 400, message: "title is required" });

  const { data, error } = await supabase
    .from("books")
    .insert({
      title,
      author: body.author?.trim() || "佚名",
      translator: body.translator?.trim() || null,
      publish_year: body.publish_year ?? null,
      publisher: body.publisher?.trim() || null,
    })
    .select("id, title, author, translator, publish_year, publisher")
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
