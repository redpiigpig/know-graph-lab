// DELETE /api/works/projects/[slug] — delete project (admin only)
// Cascades to video_transcripts via FK
export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const slug = getRouterParam(event, "slug");
  if (!slug) throw createError({ statusCode: 400, message: "slug required" });

  const supabase = getAdminClient();
  const { error } = await supabase.from("writing_projects").delete().eq("slug", slug);
  if (error) throw createError({ statusCode: 500, message: error.message });
  return { ok: true };
});
