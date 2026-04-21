// POST /api/journal-articles — create a journal / magazine article record
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as {
    title?: string;
    venue?: string;
    author?: string;
    publish_year?: number | null;
    issue_label?: string;
  };

  const title = body.title?.trim();
  if (!title) throw createError({ statusCode: 400, message: "title is required" });

  const { data, error } = await supabase
    .from("journal_articles")
    .insert({
      title,
      venue: body.venue?.trim() || null,
      author: body.author?.trim() || null,
      publish_year: body.publish_year ?? null,
      issue_label: body.issue_label?.trim() || null,
    })
    .select("id, title, venue, author, publish_year, issue_label")
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
