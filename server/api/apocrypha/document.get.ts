// GET /api/apocrypha/document?slug=1-enoch[&chapter=N]
// Returns one document + its sections grouped by order_index → byVersion map.
// Sections are now per-verse (order_index = chapter*1000 + verse). If `chapter`
// is given, only that chapter's verses are returned (lighter payload); the full
// chapter list is always returned for the navigator.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const slug = String(query.slug || '').toLowerCase()
  const chapterFilter = query.chapter != null && query.chapter !== '' ? Number(query.chapter) : null
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
    .select('order_index, version_code, text, section_label, page_number, chapter, verse, source_chunk_id, footnote_defs')
    .eq('doc_slug', slug)
    .order('order_index', { ascending: true })
  if (chapterFilter !== null) sectionsQuery = sectionsQuery.eq('chapter', chapterFilter)
  const { data: sections, error: sErr } = await sectionsQuery.limit(8000)
  if (sErr) throw createError({ statusCode: 500, message: sErr.message })

  // Group by order_index → { byVersion, footnotesByVersion, chapter, verse, ... }
  const byOrder = new Map<number, {
    order_index: number
    section_label: string | null
    page_number: number | null
    chapter: number | null
    verse: number | null
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
        verse: row.verse,
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
  const sectionsOut = Array.from(byOrder.values()).sort((a, b) => a.order_index - b.order_index)

  // Full chapter list (distinct chapters across all sections of this doc), with a
  // verse count per chapter, for the navigator. Uses cct_zh first, falls back to
  // any version so docs with only English still get a navigator.
  const { data: chapRows, error: cErr } = await supabase
    .from('apocrypha_sections')
    .select('chapter, verse, version_code')
    .eq('doc_slug', slug)
    .not('chapter', 'is', null)
    .order('chapter', { ascending: true })
    .limit(20000)
  if (cErr) throw createError({ statusCode: 500, message: cErr.message })
  const chapVerses = new Map<number, Set<number>>()
  for (const r of (chapRows ?? []) as any[]) {
    if (r.chapter == null) continue
    if (!chapVerses.has(r.chapter)) chapVerses.set(r.chapter, new Set())
    if (r.verse != null) chapVerses.get(r.chapter)!.add(r.verse)
  }
  const chapters = Array.from(chapVerses.entries())
    .map(([chapter, vs]) => ({ chapter, verses: vs.size }))
    .sort((a, b) => a.chapter - b.chapter)

  return {
    document: doc,
    sections: sectionsOut,
    chapters,
    currentChapter: chapterFilter,
  }
})
