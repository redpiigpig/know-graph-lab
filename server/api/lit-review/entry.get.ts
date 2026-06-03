// GET /api/lit-review/entry?slug=<project_slug>&ref=<ref_key>
// One bibliography entry + its full-text sections grouped by order_index
// (byVersion: { orig, zh }) — the source for the 原文/中譯 two-column reader.
export default defineEventHandler(async (event) => {
  const q = getQuery(event);
  const slug = String(q.slug || "");
  const ref = String(q.ref || "");
  if (!slug || !ref) throw createError({ statusCode: 400, message: "slug and ref required" });

  const supabase = getAdminClient();

  const { data: entry, error: eErr } = await supabase
    .from("lit_review_entries")
    .select(
      "id, ref_key, authors, year, title, venue, language, theme, dimension, stance, abstract_zh, fulltext_url, fulltext_status"
    )
    .eq("project_slug", slug)
    .eq("ref_key", ref)
    .maybeSingle();
  if (eErr) throw createError({ statusCode: 500, message: eErr.message });
  if (!entry) throw createError({ statusCode: 404, message: "entry not found" });

  const { data: sections, error: sErr } = await supabase
    .from("lit_review_sections")
    .select("order_index, version_code, text")
    .eq("entry_id", (entry as any).id)
    .order("order_index", { ascending: true })
    .limit(20000);
  if (sErr) throw createError({ statusCode: 500, message: sErr.message });

  const byOrder = new Map<number, { order_index: number; byVersion: Record<string, string> }>();
  for (const row of (sections ?? []) as any[]) {
    if (!byOrder.has(row.order_index)) {
      byOrder.set(row.order_index, { order_index: row.order_index, byVersion: {} });
    }
    byOrder.get(row.order_index)!.byVersion[row.version_code] = row.text;
  }
  const sectionsOut = Array.from(byOrder.values()).sort((a, b) => a.order_index - b.order_index);

  return { entry, sections: sectionsOut };
});
