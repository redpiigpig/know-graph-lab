// GET /api/apocrypha/document?slug=1-enoch
// Returns one document + all its sections grouped by order_index → byVersion map.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const slug = String(query.slug || '').toLowerCase()
  if (!slug) throw createError({ statusCode: 400, message: 'slug required' })

  const supabase = getAdminClient()

  const { data: doc, error: dErr } = await supabase
    .from('apocrypha_documents')
    .select('*')
    .eq('slug', slug)
    .maybeSingle()
  if (dErr) throw createError({ statusCode: 500, message: dErr.message })
  if (!doc) throw createError({ statusCode: 404, message: 'document not found' })

  // For now we only ship version='cct_zh' rows; once English/原文 land
  // they slot in automatically via the same query.
  const { data: sections, error: sErr } = await supabase
    .from('apocrypha_sections')
    .select('order_index, version_code, text, section_label, page_number, source_chunk_id')
    .eq('doc_slug', slug)
    .order('order_index', { ascending: true })
    .limit(5000)
  if (sErr) throw createError({ statusCode: 500, message: sErr.message })

  // Group: { order_index → { byVersion: { cct_zh: '...', charles_apot: '...' }, section_label, page_number } }
  const byOrder = new Map<number, {
    order_index: number
    section_label: string | null
    page_number: number | null
    byVersion: Record<string, string>
  }>()
  for (const row of (sections ?? []) as any[]) {
    if (!byOrder.has(row.order_index)) {
      byOrder.set(row.order_index, {
        order_index: row.order_index,
        section_label: row.section_label,
        page_number: row.page_number,
        byVersion: {},
      })
    }
    byOrder.get(row.order_index)!.byVersion[row.version_code] = row.text
  }

  const sectionsOut = Array.from(byOrder.values())
    .sort((a, b) => a.order_index - b.order_index)

  return {
    document: doc,
    sections: sectionsOut,
  }
})
