// GET /api/canon-law/documents
// All canon_law_documents + per-version section counts (so UI knows which docs
// have 拉丁/希臘 / 英文 / 繁中 data).
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data: docs, error } = await supabase
    .from('canon_law_documents')
    .select('*')
    .order('display_order', { ascending: true })
  if (error) throw createError({ statusCode: 500, message: error.message })

  const { data: counts, error: cErr } = await supabase
    .from('canon_law_sections')
    .select('doc_slug, version_code')
  if (cErr) throw createError({ statusCode: 500, message: cErr.message })

  const tally = new Map<string, Record<string, number>>()
  for (const row of (counts ?? []) as { doc_slug: string; version_code: string }[]) {
    if (!tally.has(row.doc_slug)) tally.set(row.doc_slug, {})
    const m = tally.get(row.doc_slug)!
    m[row.version_code] = (m[row.version_code] ?? 0) + 1
  }

  return (docs ?? []).map((d: any) => ({
    ...d,
    section_counts: tally.get(d.slug) ?? {},
    total_sections: Object.values(tally.get(d.slug) ?? {}).reduce((a, b) => a + b, 0),
  }))
})
