// GET /api/works/projects — public list
export default defineEventHandler(async () => {
  const supabase = getAdminClient();
  const { data, error } = await supabase
    .from("writing_projects")
    .select("id, slug, title, subtitle, description, emoji, color, status, sort_order")
    .order("sort_order", { ascending: true })
    .order("created_at", { ascending: true });
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { projects: data ?? [] };
});
