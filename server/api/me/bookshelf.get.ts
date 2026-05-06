/**
 * GET /api/me/bookshelf
 * Returns the current user's bookshelf — books they marked as 'reading' or
 * 'read', joined with ebook metadata + the latest bookmark per book.
 *
 * Shape:
 *   [{ status, updated_at, ebook: { id, title, author, category, ... },
 *      latest_bookmark_at?: string }]
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const supabase = getAdminClient();

  const { data: rows, error } = await supabase
    .from("user_reading_status")
    .select(`
      status,
      updated_at,
      ebook:ebooks ( id, title, author, category, subcategory, total_pages, chunk_count, file_type )
    `)
    .eq("user_id", user.id)
    .order("updated_at", { ascending: false });
  if (error) throw createError({ statusCode: 500, message: error.message });

  const ebookIds = (rows ?? []).map((r: any) => r.ebook?.id).filter(Boolean);
  if (!ebookIds.length) return [];

  // One MAX(created_at) per ebook for this user — used to render last-read date.
  const { data: bms, error: bmErr } = await supabase
    .from("reading_bookmarks")
    .select("ebook_id, created_at")
    .eq("user_id", user.id)
    .in("ebook_id", ebookIds);
  if (bmErr) throw createError({ statusCode: 500, message: bmErr.message });

  const latestByBook: Record<string, string> = {};
  for (const b of bms ?? []) {
    const cur = latestByBook[b.ebook_id];
    if (!cur || b.created_at > cur) latestByBook[b.ebook_id] = b.created_at;
  }

  return (rows ?? []).map((r: any) => ({
    ...r,
    latest_bookmark_at: r.ebook?.id ? latestByBook[r.ebook.id] ?? null : null,
  }));
});
