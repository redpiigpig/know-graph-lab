// GET /api/gnostic/document?slug=gospel-of-thomas
// One document + all sections grouped by order_index → byVersion map.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const slug = String(query.slug || '').toLowerCase()
  if (!slug) throw createError({ statusCode: 400, message: 'slug required' })

  const supabase = getAdminClient()

  const { data: doc, error: dErr } = await supabase
    .from('gnostic_documents')
    .select('*')
    .eq('slug', slug)
    .maybeSingle()
  if (dErr) throw createError({ statusCode: 500, message: dErr.message })
  if (!doc) throw createError({ statusCode: 404, message: 'document not found' })

  const { data: sections, error: sErr } = await supabase
    .from('gnostic_sections')
    .select('order_index, version_code, text, section_label')
    .eq('doc_slug', slug)
    .order('order_index', { ascending: true })
    .limit(10000)
  if (sErr) throw createError({ statusCode: 500, message: sErr.message })

  const byOrder = new Map<number, {
    order_index: number
    section_label: string | null
    byVersion: Record<string, string>
  }>()
  for (const row of (sections ?? []) as any[]) {
    if (!byOrder.has(row.order_index)) {
      byOrder.set(row.order_index, { order_index: row.order_index, section_label: row.section_label, byVersion: {} })
    }
    byOrder.get(row.order_index)!.byVersion[row.version_code] = row.text
  }
  const sectionsOut = Array.from(byOrder.values()).sort((a, b) => a.order_index - b.order_index)

  return { document: doc, sections: sectionsOut }
})
