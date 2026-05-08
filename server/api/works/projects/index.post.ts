// POST /api/works/projects — create new project (admin only)
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
  const supabase = getAdminClient();
  const body = (await readBody(event)) as {
    slug?: string;
    title?: string;
    subtitle?: string;
    description?: string;
    emoji?: string;
    color?: string;
    status?: string;
  };

  const title = body.title?.trim();
  if (!title) throw createError({ statusCode: 400, message: "title required" });

  let slug = (body.slug ? slugify(body.slug) : slugify(title)) || "untitled";
  if (RESERVED_SLUGS.has(slug)) {
    throw createError({ statusCode: 400, message: `slug "${slug}" is reserved` });
  }

  // ensure uniqueness; append -2, -3, ... if collision
  let finalSlug = slug;
  for (let i = 2; i < 100; i++) {
    const { data } = await supabase
      .from("writing_projects")
      .select("id")
      .eq("slug", finalSlug)
      .maybeSingle();
    if (!data) break;
    finalSlug = `${slug}-${i}`;
  }

  // sort_order = max + 1
  const { data: maxRow } = await supabase
    .from("writing_projects")
    .select("sort_order")
    .order("sort_order", { ascending: false })
    .limit(1)
    .maybeSingle();
  const nextOrder = (maxRow?.sort_order ?? -1) + 1;

  const { data, error } = await supabase
    .from("writing_projects")
    .insert({
      slug: finalSlug,
      title,
      subtitle: body.subtitle?.trim() || null,
      description: body.description?.trim() || null,
      emoji: body.emoji?.trim() || "📝",
      color: body.color?.trim() || "amber",
      status: body.status?.trim() || null,
      sort_order: nextOrder,
    })
    .select("id, slug, title, subtitle, description, emoji, color, status, sort_order")
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });
  return { project: data };
});
