/**
 * PUT /api/ebooks/:id/cover
 * Body: { cover_url: string | null }
 *
 * Sets or clears the cover image URL on an ebooks row. Any authenticated
 * user can set the cover — these are book-level metadata, not per-user.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const ebookId = getRouterParam(event, "id");
  if (!ebookId) throw createError({ statusCode: 400, message: "ebook id required" });

  const body = (await readBody(event)) as { cover_url: string | null };
  const url = body.cover_url?.trim() || null;

  // Basic URL sanity — only accept http(s).
  if (url && !/^https?:\/\//i.test(url)) {
    throw createError({ statusCode: 400, message: "cover_url must be http(s) URL" });
  }

  const supabase = getAdminClient();
  const { data, error } = await supabase
    .from("ebooks")
    .update({ cover_url: url, cover_source: url ? "manual_paste" : null })
    .eq("id", ebookId)
    .select("id, cover_url")
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
