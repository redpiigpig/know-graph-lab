/**
 * PATCH /api/annotations/:id
 * Update note or color of an annotation.
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id");
  if (!id) throw createError({ statusCode: 400, message: "Missing id" });

  const body = await readBody(event) as { note?: string; color?: string };
  const patch: Record<string, any> = {};
  if (body.note !== undefined) patch.note = body.note;
  if (body.color !== undefined) patch.color = body.color;
  if (Object.keys(patch).length === 0) {
    throw createError({ statusCode: 400, message: "Nothing to update" });
  }

  const { data, error } = await supabase
    .from("annotations")
    .update(patch)
    .eq("id", id)
    .select()
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
