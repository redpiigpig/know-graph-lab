// POST /api/projects
// Create a new writing/article project
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as {
    name?: string;
    type?: string;
    description?: string;
  };

  const name = body.name?.trim();
  const type = body.type?.trim();
  if (!name) throw createError({ statusCode: 400, message: "name is required" });
  if (!type || !["待寫著作", "待寫文章"].includes(type)) {
    throw createError({ statusCode: 400, message: "type must be 待寫著作 or 待寫文章" });
  }

  const { data, error } = await supabase
    .from("book_projects")
    .insert({ name, type, description: body.description?.trim() || null })
    .select("id, name, type, description, created_at")
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
