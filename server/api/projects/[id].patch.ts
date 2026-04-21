// PATCH /api/projects/:id — update project name and/or description (e.g. excerpt layout JSON)
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const id = getRouterParam(event, "id")!;
  const body = await readBody(event) as {
    name?: string | null;
    description?: string | null;
  };

  const updates: Record<string, unknown> = {};
  if (body.name !== undefined) {
    const n = typeof body.name === "string" ? body.name.trim() : "";
    if (!n) throw createError({ statusCode: 400, message: "name cannot be empty" });
    updates.name = n;
  }
  if (body.description !== undefined) {
    const d = body.description;
    updates.description =
      d === null || d === "" ? null : typeof d === "string" ? d.trim() : String(d).trim();
  }

  if (!Object.keys(updates).length) {
    throw createError({ statusCode: 400, message: "Provide name and/or description" });
  }

  const { data, error } = await supabase
    .from("book_projects")
    .update(updates)
    .eq("id", id)
    .select("id, name, type, description, created_at")
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  if (!data) throw createError({ statusCode: 404, message: "找不到此項目" });
  return data;
});
