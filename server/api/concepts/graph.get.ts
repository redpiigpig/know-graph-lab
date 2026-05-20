// GET /api/concepts/graph — nodes + edges payload for D3 force graph.
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();

  const [{ data: concepts, error: cErr }, { data: links, error: lErr }] = await Promise.all([
    supabase.from("concepts").select("id, name, slug, color, summary"),
    supabase.from("concept_links").select("from_concept_id, to_concept_id"),
  ]);
  if (cErr) throw createError({ statusCode: 500, message: cErr.message });
  if (lErr) throw createError({ statusCode: 500, message: lErr.message });

  const degree: Record<string, number> = {};
  (links ?? []).forEach((l: any) => {
    degree[l.from_concept_id] = (degree[l.from_concept_id] ?? 0) + 1;
    degree[l.to_concept_id]   = (degree[l.to_concept_id]   ?? 0) + 1;
  });

  return {
    nodes: (concepts ?? []).map((c: any) => ({
      id: c.id,
      name: c.name,
      slug: c.slug,
      color: c.color,
      summary: c.summary,
      degree: degree[c.id] ?? 0,
    })),
    edges: (links ?? []).map((l: any) => ({
      source: l.from_concept_id,
      target: l.to_concept_id,
    })),
  };
});
