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
      .select(`excerpt:excerpts(
        id, title, content, page_number, book_id, journal_article_id,
        books(id, title, author, publish_year),
        journal_articles(id, title, venue, author, publish_year)
      )`)
      .eq("concept_id", concept.id),
  ]);

  const excerpts = (excerptLinks ?? []).map((e: any) => e.excerpt).filter(Boolean);

  // Aggregate source books / journals referenced by this concept's excerpts.
  const bookMap = new Map<string, { id: string; title: string; author?: string; publish_year?: number; excerpt_count: number }>();
  const jaMap   = new Map<string, { id: string; title: string; venue?: string; author?: string; publish_year?: number; excerpt_count: number }>();
  for (const ex of excerpts) {
    if (ex.books) {
      const b = ex.books;
      const cur = bookMap.get(b.id) || { id: b.id, title: b.title, author: b.author, publish_year: b.publish_year, excerpt_count: 0 };
      cur.excerpt_count++;
      bookMap.set(b.id, cur);
    }
    if (ex.journal_articles) {
      const j = ex.journal_articles;
      const cur = jaMap.get(j.id) || { id: j.id, title: j.title, venue: j.venue, author: j.author, publish_year: j.publish_year, excerpt_count: 0 };
      cur.excerpt_count++;
      jaMap.set(j.id, cur);
    }
  }

  return {
    ...concept,
    outlinks:  (outLinks  ?? []).map((l: any) => ({ ...l.target, raw: l.raw_link_text, context: l.context })),
    backlinks: (backLinks ?? []).map((l: any) => ({ ...l.source, context: l.context })),
    excerpts,
    source_books:    Array.from(bookMap.values()).sort((a, b) => b.excerpt_count - a.excerpt_count),
    source_journals: Array.from(jaMap.values()).sort((a, b) => b.excerpt_count - a.excerpt_count),
  };
});
