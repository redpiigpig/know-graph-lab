// GET /api/canon-law/search?q=&doc=&version=&limit=
// ILIKE substring search across all 教會法規 sections.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const q = String(query.q || '').trim()
  const docFilter = query.doc ? String(query.doc) : null
  const versionFilter = query.version ? String(query.version) : null
  const limit = Math.min(Number(query.limit) || 100, 300)

  if (!q || q.length < 2) return { q, total: 0, results: [] }

  const supabase = getAdminClient()
  let sb = supabase
    .from('canon_law_sections')
    .select('doc_slug, version_code, order_index, section_label, book_label, text', { count: 'exact' })
    .ilike('text', `%${q}%`)
  if (docFilter) sb = sb.eq('doc_slug', docFilter)
  if (versionFilter) sb = sb.eq('version_code', versionFilter)

  const { data, error, count } = await sb
    .order('doc_slug', { ascending: true })
    .order('order_index', { ascending: true })
    .limit(limit)
  if (error) throw createError({ statusCode: 500, message: error.message })

  return { q, total: count || 0, results: data || [] }
})
