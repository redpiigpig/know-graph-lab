// GET /api/concepts/:slug — full body + outlinks + backlinks + excerpts
export default defineEventHandler(async (event) => {
  await requireAuth(event);
  const supabase = getAdminClient();
  const slug = getRouterParam(event, "slug")!;

  const { data: concept, error } = await supabase
    .from("concepts").select("*").eq("slug", slug).single();
  if (error || !concept) throw createError({ statusCode: 404, message: "concept not found" });

  const [{ data: outLinks }, { data: backLinks }, { data: excerptLinks }] = await Promise.all([
    supabase
      .from("concept_links")
      .select("to_concept_id, raw_link_text, context, target:concepts!concept_links_to_concept_id_fkey(id, name, slug, summary)")
      .eq("from_concept_id", concept.id),
    supabase
      .from("concept_links")
      .select("from_concept_id, context, source:concepts!concept_links_from_concept_id_fkey(id, name, slug, summary)")
      .eq("to_concept_id", concept.id),
    supabase
      .from("excerpt_concepts")
      .select("excerpt:excerpts(id, title, content, book_id, journal_article_id)")
      .eq("concept_id", concept.id),
  ]);

  return {
    ...concept,
    outlinks:  (outLinks  ?? []).map((l: any) => ({ ...l.target, raw: l.raw_link_text, context: l.context })),
    backlinks: (backLinks ?? []).map((l: any) => ({ ...l.source, context: l.context })),
    excerpts:  (excerptLinks ?? []).map((e: any) => e.excerpt).filter(Boolean),
  };
});
