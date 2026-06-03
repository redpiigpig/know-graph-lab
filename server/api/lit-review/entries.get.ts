// GET /api/lit-review/entries?slug=<project_slug>
// All literature-review bibliography entries for a 論文寫作 project, ordered.
// `has_fulltext` marks entries that have aligned 原文/中譯 sections (reader-ready).
export default defineEventHandler(async (event) => {
  const slug = String(getQuery(event).slug || "");
  if (!slug) throw createError({ statusCode: 400, message: "slug required" });

  const supabase = getAdminClient();

  const { data: entries, error } = await supabase
    .from("lit_review_entries")
    .select(
      "id, ref_key, authors, year, title, venue, language, theme, dimension, stance, abstract_zh, fulltext_url, fulltext_status, display_order"
    )
    .eq("project_slug", slug)
    .order("display_order", { ascending: true })
    .order("id", { ascending: true });
  if (error) throw createError({ statusCode: 500, message: error.message });

  const list = entries ?? [];
  // Which entries actually have translated sections on the page?
  const ids = list.map((e: any) => e.id);
  const withFulltext = new Set<number>();
  if (ids.length) {
    const { data: secs } = await supabase
      .from("lit_review_sections")
      .select("entry_id")
      .in("entry_id", ids)
      .eq("version_code", "zh")
      .limit(10000);
    for (const r of (secs ?? []) as any[]) withFulltext.add(r.entry_id);
  }

  return {
    entries: list.map((e: any) => ({ ...e, has_fulltext: withFulltext.has(e.id) })),
  };
});
