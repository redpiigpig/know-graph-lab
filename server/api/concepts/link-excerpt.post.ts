// POST /api/concepts/link-excerpt
// Body: { excerpt_id, concept_id }   OR  { excerpt_id, concept_name }
// Idempotent — UNIQUE(excerpt_id, concept_id) handles dupes.
import { slugify } from "../../utils/concept-links";

export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const body = await readBody(event) as { excerpt_id?: string; concept_id?: string; concept_name?: string };

  if (!body.excerpt_id) throw createError({ statusCode: 400, message: "excerpt_id required" });

  let conceptId = body.concept_id;
  if (!conceptId && body.concept_name?.trim()) {
    const name = body.concept_name.trim();
    const { data: existing } = await supabase
      .from("concepts").select("id").ilike("name", name).maybeSingle();
    if (existing) conceptId = (existing as any).id;
    else {
      let slug = slugify(name);
      for (let suffix = 1; suffix < 99; suffix++) {
        const tryCandidate = suffix === 1 ? slug : `${slug}-${suffix}`;
        const { data: clash } = await supabase
          .from("concepts").select("id").eq("slug", tryCandidate).maybeSingle();
        if (!clash) { slug = tryCandidate; break; }
      }
      const { data: created, error } = await supabase
        .from("concepts").insert({ name, slug }).select("id").single();
      if (error) throw createError({ statusCode: 500, message: error.message });
      conceptId = (created as any).id;
    }
  }
  if (!conceptId) throw createError({ statusCode: 400, message: "concept_id or concept_name required" });

  const { error } = await supabase
    .from("excerpt_concepts")
    .insert({ excerpt_id: body.excerpt_id, concept_id: conceptId });
  // unique-violation = already linked, treat as success
  if (error && !`${error.message}`.includes("duplicate")) {
    throw createError({ statusCode: 500, message: error.message });
  }
  return { success: true, concept_id: conceptId };
});
