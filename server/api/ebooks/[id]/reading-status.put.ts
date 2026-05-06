/**
 * PUT /api/ebooks/:id/reading-status
 * Body: { status: 'reading' | 'read' | null }
 *   null  → remove the row (un-shelve)
 *   else  → upsert with new status
 */
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event);
  const ebookId = getRouterParam(event, "id");
  if (!ebookId) throw createError({ statusCode: 400, message: "ebook id required" });

  const body = (await readBody(event)) as { status: "reading" | "read" | null };
  const supabase = getAdminClient();

  if (body.status === null) {
    const { error } = await supabase
      .from("user_reading_status")
      .delete()
      .eq("user_id", user.id)
      .eq("ebook_id", ebookId);
    if (error) throw createError({ statusCode: 500, message: error.message });
    return { status: null };
  }

  if (body.status !== "reading" && body.status !== "read") {
    throw createError({ statusCode: 400, message: "status must be 'reading' | 'read' | null" });
  }

  const { data, error } = await supabase
    .from("user_reading_status")
    .upsert(
      { user_id: user.id, ebook_id: ebookId, status: body.status, updated_at: new Date().toISOString() },
      { onConflict: "user_id,ebook_id" }
    )
    .select()
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
