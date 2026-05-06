/**
 * PUT /api/books/:id/tags
 * Body: { tag_ids: string[] }   — replaces the entire tag set for this book.
 * Empty array clears all tags. Idempotent.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const id = getRouterParam(event, "id");
  if (!id) throw createError({ statusCode: 400, message: "id required" });
  const body = (await readBody(event)) as { tag_ids?: string[] };
  const tagIds = Array.from(new Set(body.tag_ids ?? []));

  const supabase = getAdminClient();

  // Replace strategy — wipe then insert. Cheap on a junction table that
  // typically has < 20 rows per book.
  const { error: delErr } = await supabase.from("book_tags").delete().eq("book_id", id);
  if (delErr) throw createError({ statusCode: 500, message: delErr.message });

  if (tagIds.length) {
    const rows = tagIds.map((tag_id) => ({ book_id: id, tag_id }));
    const { error: insErr } = await supabase.from("book_tags").insert(rows);
    if (insErr) throw createError({ statusCode: 500, message: insErr.message });
  }

  return { ok: true, count: tagIds.length };
});
