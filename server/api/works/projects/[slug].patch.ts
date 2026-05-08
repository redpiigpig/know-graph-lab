// PATCH /api/works/projects/[slug] — update project (admin only)
const RESERVED_SLUGS = new Set(["reorder", "new", "edit", ""]);

function slugify(input: string): string {
  return input
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9一-龥]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 60);
}

export default defineEventHandler(async (event) => {
  await requireAdmin(event);
  const slug = getRouterParam(event, "slug");
  if (!slug) throw createError({ statusCode: 400, message: "slug required" });

  const body = (await readBody(event)) as {
    slug?: string;
    title?: string;
    subtitle?: string | null;
    description?: string | null;
    emoji?: string;
    color?: string;
    status?: string | null;
    content_json?: unknown;
  };

  const updates: Record<string, unknown> = { updated_at: new Date().toISOString() };

  if (body.slug !== undefined) {
    const newSlug = slugify(body.slug);
    if (!newSlug) throw createError({ statusCode: 400, message: "slug invalid" });
    if (RESERVED_SLUGS.has(newSlug)) {
      throw createError({ statusCode: 400, message: `slug "${newSlug}" is reserved` });
    }
    updates.slug = newSlug;
  }
  if (body.title !== undefined) updates.title = body.title.trim();
  if (body.subtitle !== undefined) updates.subtitle = body.subtitle?.trim() || null;
  if (body.description !== undefined) updates.description = body.description?.trim() || null;
  if (body.emoji !== undefined) updates.emoji = body.emoji.trim() || "📝";
  if (body.color !== undefined) updates.color = body.color.trim() || "amber";
  if (body.status !== undefined) updates.status = body.status?.trim() || null;
  if (body.content_json !== undefined) updates.content_json = body.content_json;

  const supabase = getAdminClient();
  const { data, error } = await supabase
    .from("writing_projects")
    .update(updates)
    .eq("slug", slug)
    .select("id, slug, title, subtitle, description, emoji, color, status, sort_order, content_json")
    .maybeSingle();

  if (error) throw createError({ statusCode: 500, message: error.message });
  if (!data) throw createError({ statusCode: 404, message: "project not found" });
  return { project: data };
});
