// GET /api/apocrypha/document?slug=1-enoch&page=N
// Returns one document + all its sections grouped by order_index → byVersion map.
// If `page` query is given, returns only sections from that page_number.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const slug = String(query.slug || '').toLowerCase()
  const pageFilter = query.page ? Number(query.page) : null
  if (!slug) throw createError({ statusCode: 400, message: 'slug required' })

  const supabase = getAdminClient()

  const { data: doc, error: dErr } = await supabase
    .from('apocrypha_documents')
    .select('*')
    .eq('slug', slug)
    .maybeSingle()
  if (dErr) throw createError({ statusCode: 500, message: dErr.message })
  if (!doc) throw createError({ statusCode: 404, message: 'document not found' })

  let sectionsQuery = supabase
    .from('apocrypha_sections')
    .select('order_index, version_code, text, section_label, page_number, chapter, source_chunk_id, footnote_defs')
    .eq('doc_slug', slug)
    .order('order_index', { ascending: true })
  if (pageFilter !== null) sectionsQuery = sectionsQuery.eq('page_number', pageFilter)
  const { data: sections, error: sErr } = await sectionsQuery.limit(5000)
  if (sErr) throw createError({ statusCode: 500, message: sErr.message })

  // Group: { order_index → { byVersion, footnotesByVersion, section_label, page_number, chapter } }
  const byOrder = new Map<number, {
    order_index: number
    section_label: string | null
    page_number: number | null
    chapter: number | null
    byVersion: Record<string, string>
    footnotesByVersion: Record<string, Record<string, string>>
  }>()
  for (const row of (sections ?? []) as any[]) {
    if (!byOrder.has(row.order_index)) {
      byOrder.set(row.order_index, {
        order_index: row.order_index,
        section_label: row.section_label,
        page_number: row.page_number,
        chapter: row.chapter,
        byVersion: {},
        footnotesByVersion: {},
      })
    }
    const entry = byOrder.get(row.order_index)!
    entry.byVersion[row.version_code] = row.text
    if (row.footnote_defs && typeof row.footnote_defs === 'object') {
      entry.footnotesByVersion[row.version_code] = row.footnote_defs
    }
  }
  const sectionsOut = Array.from(byOrder.values())
    .sort((a, b) => a.order_index - b.order_index)

  // Compute page list (distinct page_numbers across all sections of this doc, NOT
  // limited by pageFilter — UI needs the full page strip even when viewing one page).
  const { data: allPagesRows, error: pErr } = await supabase
    .from('apocrypha_sections')
    .select('page_number, version_code')
    .eq('doc_slug', slug)
    .eq('version_code', 'cct_zh')
    .order('page_number', { ascending: true })
  if (pErr) throw createError({ statusCode: 500, message: pErr.message })
  const pages = Array.from(new Set(
    (allPagesRows ?? [])
      .map((r: any) => r.page_number)
      .filter((p: any) => p !== null && p !== undefined)
  )) as number[]

  return {
    document: doc,
    sections: sectionsOut,
    pages,
    currentPage: pageFilter,
  }
})
