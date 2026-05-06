/**
 * GET /api/tags
 * List all tags with usage counts (books + excerpts that reference them).
 * Ordered by name. Used by tag picker autocomplete + /tags page.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const [{ data: tags, error }, { data: bookLinks }, { data: excerptLinks }] = await Promise.all([
    supabase.from("tags").select("id, name, color, created_at").order("name"),
    supabase.from("book_tags").select("tag_id"),
    supabase.from("excerpt_tags").select("tag_id"),
  ]);
  if (error) throw createError({ statusCode: 500, message: error.message });

  const bookCount: Record<string, number> = {};
  bookLinks?.forEach((r) => { bookCount[r.tag_id] = (bookCount[r.tag_id] ?? 0) + 1; });
  const excerptCount: Record<string, number> = {};
  excerptLinks?.forEach((r) => { excerptCount[r.tag_id] = (excerptCount[r.tag_id] ?? 0) + 1; });

  return (tags ?? []).map((t) => ({
    ...t,
    book_count:    bookCount[t.id]    ?? 0,
    excerpt_count: excerptCount[t.id] ?? 0,
  }));
});
