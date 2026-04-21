// PATCH /api/excerpts/:id  — inline editing: title / content / chapter (主題)
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id")!;
  const body = await readBody(event) as { title?: string; content?: string; chapter?: string | null };

  const updates: Record<string, string | null> = { updated_at: new Date().toISOString() };
  if (body.title !== undefined) updates.title = body.title;
  if (body.content !== undefined) updates.content = body.content;
  if (body.chapter !== undefined) updates.chapter = body.chapter;

  const { error } = await supabase.from("excerpts").update(updates).eq("id", id);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { success: true };
});
