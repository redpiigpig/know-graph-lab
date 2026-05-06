/**
 * POST /api/tags
 * Body: { name, color? }
 * Creates a new tag. If a tag with the same name already exists, returns
 * the existing one (idempotent — used by the picker's "create from typeahead").
 */
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = (await readBody(event)) as { name?: string; color?: string };

  const name = (body.name || "").trim();
  if (!name) throw createError({ statusCode: 400, message: "name required" });
  if (name.length > 50) throw createError({ statusCode: 400, message: "name too long (max 50)" });

  // Idempotent — case-insensitive lookup first.
  const existing = await supabase
    .from("tags")
    .select("id, name, color, created_at")
    .ilike("name", name)
    .maybeSingle();
  if (existing.data) return existing.data;

  const { data, error } = await supabase
    .from("tags")
    .insert({ name, color: body.color || null })
    .select("id, name, color, created_at")
    .single();
  if (error) throw createError({ statusCode: 500, message: error.message });
  return data;
});
