// GET /api/canon-law/document?slug=cic-1983
// One document + all sections grouped by order_index (= 條號) → byVersion map.
// Carries book_label / chapter_label so the reader can build the 卷/題/章 tree.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const slug = String(query.slug || '').toLowerCase()
  if (!slug) throw createError({ statusCode: 400, message: 'slug required' })

  const supabase = getAdminClient()

  const { data: doc, error: dErr } = await supabase
    .from('canon_law_documents')
    .select('*')
    .eq('slug', slug)
    .maybeSingle()
  if (dErr) throw createError({ statusCode: 500, message: dErr.message })
  if (!doc) throw createError({ statusCode: 404, message: 'document not found' })

  const { data: sections, error: sErr } = await supabase
    .from('canon_law_sections')
    .select('order_index, version_code, text, section_label, book_label, chapter_label, is_heading')
    .eq('doc_slug', slug)
    .order('order_index', { ascending: true })
    .limit(20000)
  if (sErr) throw createError({ statusCode: 500, message: sErr.message })

  const byOrder = new Map<number, {
    order_index: number
    section_label: string | null
    book_label: string | null
    chapter_label: string | null
    is_heading: boolean
    byVersion: Record<string, string>
  }>()
  for (const row of (sections ?? []) as any[]) {
    if (!byOrder.has(row.order_index)) {
      byOrder.set(row.order_index, {
        order_index: row.order_index,
        section_label: row.section_label,
        book_label: row.book_label,
        chapter_label: row.chapter_label,
        is_heading: row.is_heading ?? false,
        byVersion: {},
      })
    }
    byOrder.get(row.order_index)!.byVersion[row.version_code] = row.text
  }
  const sectionsOut = Array.from(byOrder.values()).sort((a, b) => a.order_index - b.order_index)

  return { document: doc, sections: sectionsOut }
})
