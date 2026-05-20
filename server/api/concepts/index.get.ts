// GET /api/concepts?q=...
// List concepts (optionally filtered by name/alias) with backlink + outlink counts.
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const { q } = getQuery(event) as { q?: string };

  let query = supabase
    .from("concepts")
    .select("id, name, slug, aliases, summary, color, created_at, updated_at")
    .order("updated_at", { ascending: false });

  if (q?.trim()) {
    const needle = `%${q.trim()}%`;
    query = query.or(`name.ilike.${needle},summary.ilike.${needle}`);
  }

  const { data: concepts, error } = await query;
  if (error) throw createError({ statusCode: 500, message: error.message });

  const { data: links } = await supabase
    .from("concept_links")
    .select("from_concept_id, to_concept_id");

  const outCount: Record<string, number> = {};
  const inCount: Record<string, number> = {};
  (links ?? []).forEach((l: any) => {
    outCount[l.from_concept_id] = (outCount[l.from_concept_id] ?? 0) + 1;
    inCount[l.to_concept_id] = (inCount[l.to_concept_id] ?? 0) + 1;
  });

  return (concepts ?? []).map((c) => ({
    ...c,
    out_count: outCount[c.id] ?? 0,
    in_count: inCount[c.id] ?? 0,
  }));
});
