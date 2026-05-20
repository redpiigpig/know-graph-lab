// POST /api/concepts
// Body: { name, slug?, aliases?, summary?, body?, color? }
import { rebuildConceptLinks, slugify } from "../../utils/concept-links";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as {
    name?: string; slug?: string; aliases?: string[];
    summary?: string; body?: string; color?: string;
  };

  if (!body.name?.trim()) throw createError({ statusCode: 400, message: "name required" });

  let slug = (body.slug || slugify(body.name)).trim();
  // ensure uniqueness — append -2, -3, …
  for (let suffix = 1; suffix < 99; suffix++) {
    const tryCandidate = suffix === 1 ? slug : `${slug}-${suffix}`;
    const { data: clash } = await supabase
      .from("concepts").select("id").eq("slug", tryCandidate).maybeSingle();
    if (!clash) { slug = tryCandidate; break; }
  }

  const { data, error } = await supabase
    .from("concepts")
    .insert({
      name: body.name.trim(),
      slug,
      aliases: body.aliases ?? [],
      summary: body.summary ?? null,
      body: body.body ?? "",
      color: body.color ?? null,
    })
    .select("id, name, slug")
    .single();

  if (error) throw createError({ statusCode: 500, message: error.message });

  if (body.body?.trim()) {
    await rebuildConceptLinks(supabase, (data as any).id, body.body);
  }

  return data;
});
