// GET /api/scripture/search?q=創世&version=cuv2010&book=gen&limit=100
// Search verse text. Default: ILIKE across all versions, all books.
// Returns up to limit (default 100) matches with snippet.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const q = String(query.q || '').trim()
  const versionFilter = query.version ? String(query.version) : null
  const bookFilter = query.book ? String(query.book) : null
  const limit = Math.min(Number(query.limit) || 100, 300)

  if (!q || q.length < 2) {
    return { q, total: 0, results: [] }
  }

  const supabase = getAdminClient()
  let sb = supabase
    .from('bible_verses')
    .select('book_code, chapter, verse, version_code, text', { count: 'exact' })
    .ilike('text', `%${q}%`)
  if (versionFilter) sb = sb.eq('version_code', versionFilter)
  if (bookFilter) sb = sb.eq('book_code', bookFilter)

  const { data, error, count } = await sb
    .order('book_code', { ascending: true })
    .order('chapter', { ascending: true })
    .order('verse', { ascending: true })
    .limit(limit)

  if (error) throw createError({ statusCode: 500, message: error.message })

  return {
    q,
    total: count || 0,
    results: data || [],
  }
})
