// GET /api/lit-review/entries?slug=<project_slug>[&bookId=<book_id>]
// All literature-review bibliography entries for a 論文寫作 project, ordered.
// `bookId` scopes to one volume within a 叢書 project (創生哲學 卷, e.g. 'M1').
// `has_fulltext` marks entries that have aligned 原文/中譯 sections (reader-ready).
export default defineEventHandler(async (event) => {
  const slug = String(getQuery(event).slug || "");
  if (!slug) throw createError({ statusCode: 400, message: "slug required" });
  const bookId = String(getQuery(event).bookId || "");

  const supabase = getAdminClient();

  let query = supabase
    .from("lit_review_entries")
    .select(
      "id, ref_key, authors, year, title, venue, language, theme, dimension, stance, abstract_zh, fulltext_url, fulltext_status, display_order"
    )
    .eq("project_slug", slug);
  if (bookId) query = query.eq("book_id", bookId);
  const { data: entries, error } = await query
    .order("display_order", { ascending: true })
    .order("id", { ascending: true });
  if (error) throw createError({ statusCode: 500, message: error.message });

  const list = entries ?? [];
  // Which entries actually have translated sections on the page?
  const ids = list.map((e: any) => e.id);
  const withFulltext = new Set<number>();
  if (ids.length) {
    // Page through — PostgREST caps each response at max-rows (1000), and a single
    // whole-book entry (中國禪宗史 ~1224 段) can fill that, starving the rest.
    const PAGE = 1000;
    for (let from = 0; ; from += PAGE) {
      const { data: secs } = await supabase
        .from("lit_review_sections")
        .select("entry_id")
        .in("entry_id", ids)
        .eq("version_code", "zh")
        .order("entry_id", { ascending: true })
        .range(from, from + PAGE - 1);
      const rows = (secs ?? []) as any[];
      for (const r of rows) withFulltext.add(r.entry_id);
      if (rows.length < PAGE) break;
    }
  }

  return {
    entries: list.map((e: any) => ({ ...e, has_fulltext: withFulltext.has(e.id) })),
  };
});
