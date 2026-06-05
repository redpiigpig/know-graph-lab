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

  // Page through all sections — PostgREST caps each response at 1000 rows
  // (db-max-rows); a full doc (e.g. CIC ~5200 rows across 3 langs) needs several.
  const sections: any[] = []
  const PAGE = 1000
  for (let from = 0; ; from += PAGE) {
    const { data, error: sErr } = await supabase
      .from('canon_law_sections')
      .select('order_index, version_code, text, section_label, book_label, chapter_label, is_heading')
      .eq('doc_slug', slug)
      .order('order_index', { ascending: true })
      .order('version_code', { ascending: true })
      .range(from, from + PAGE - 1)
    if (sErr) throw createError({ statusCode: 500, message: sErr.message })
    if (data) sections.push(...data)
    if (!data || data.length < PAGE) break
  }

  // Label priority: prefer the 繁中 labels, then 拉丁, then 英文 — so the sidebar
  // tree is consistent (not a per-canon mix of '第一題' / 'TITULUS I').
  const LABEL_PRIORITY: Record<string, number> = { zh: 3, la: 2, grc: 2, en: 1 }
  const byOrder = new Map<number, {
    order_index: number
    section_label: string | null
    book_label: string | null
    chapter_label: string | null
    is_heading: boolean
    byVersion: Record<string, string>
    _labelPrio: number
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
        _labelPrio: -1,
      })
    }
    const entry = byOrder.get(row.order_index)!
    entry.byVersion[row.version_code] = row.text
    const prio = LABEL_PRIORITY[row.version_code] ?? 0
    if (prio > entry._labelPrio) {  // adopt the higher-priority language's labels
      entry._labelPrio = prio
      entry.section_label = row.section_label ?? entry.section_label
      entry.book_label = row.book_label ?? entry.book_label
      entry.chapter_label = row.chapter_label ?? entry.chapter_label
    }
  }
  const sectionsOut = Array.from(byOrder.values())
    .sort((a, b) => a.order_index - b.order_index)
    .map(({ _labelPrio, ...s }) => s)

  return { document: doc, sections: sectionsOut }
})
