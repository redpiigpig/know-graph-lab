// GET /api/gnostic/documents
// All gnostic_documents + per-version section counts (so UI knows which docs
// have 英文 / 繁中 data).
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { data: docs, error } = await supabase
    .from('gnostic_documents')
    .select('*')
    .order('display_order', { ascending: true })
  if (error) throw createError({ statusCode: 500, message: error.message })

  // Per-(doc, version) counts via a DB-side aggregate view. Counting by fetching
  // every gnostic_sections row hit PostgREST's 1000-row cap once the corpus grew
  // past ~500 sections (only the first docs got tallied → most cards wrongly
  // showed 未轉錄). The view has one row per (doc_slug, version_code) — 268×2 ≈
  // 536 rows, comfortably under the cap.
  const { data: counts, error: cErr } = await supabase
    .from('gnostic_section_counts')
    .select('doc_slug, version_code, n')
  if (cErr) throw createError({ statusCode: 500, message: cErr.message })

  const tally = new Map<string, Record<string, number>>()
  for (const row of (counts ?? []) as { doc_slug: string; version_code: string; n: number }[]) {
    if (!tally.has(row.doc_slug)) tally.set(row.doc_slug, {})
    tally.get(row.doc_slug)![row.version_code] = row.n
  }

  return (docs ?? []).map((d: any) => ({
    ...d,
    section_counts: tally.get(d.slug) ?? {},
    total_sections: Object.values(tally.get(d.slug) ?? {}).reduce((a, b) => a + b, 0),
  }))
})
