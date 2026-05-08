// PATCH /api/works/projects/reorder — batch reorder (admin only)
// Body: { order: [{ slug: string, sort_order: number }, ...] }
// Static path; takes precedence over [slug].patch.ts in nitro routing
export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const body = (await readBody(event)) as {
    order?: { slug: string; sort_order: number }[];
  };
  const items = body.order;
  if (!Array.isArray(items) || items.length === 0) {
    throw createError({ statusCode: 400, message: "order array required" });
  }

  const supabase = getAdminClient();
  const now = new Date().toISOString();
  for (const item of items) {
    if (typeof item.slug !== "string" || typeof item.sort_order !== "number") continue;
    const { error } = await supabase
      .from("writing_projects")
      .update({ sort_order: item.sort_order, updated_at: now })
      .eq("slug", item.slug);
    if (error) throw createError({ statusCode: 500, message: error.message });
  }

  return { ok: true };
});
