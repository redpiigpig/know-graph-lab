// GET /api/scripture/search?q=創世&version=cuv2010&book=gen&limit=100
// Search verse text. Returns up to limit (default 100) matches.
// 經文本體 2026-07-08 起不在 DB（超量救援）：逐卷掃 Drive/R2 gz JSON。
// 冷掃全庫（80 卷）在 production 約數秒；指定 book/常用卷有 LRU 快取。
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const q = String(query.q || '').trim()
  const versionFilter = query.version ? String(query.version) : null
  const bookFilter = query.book ? String(query.book).toLowerCase() : null
  const limit = Math.min(Number(query.limit) || 100, 300)

  if (!q || q.length < 2) {
    return { q, total: 0, results: [] }
  }

  const supabase = getAdminClient()
  let bookCodes: string[]
  if (bookFilter) {
    bookCodes = [bookFilter]
  } else {
    const { data, error } = await supabase
      .from('bible_books')
      .select('code, sort_order')
      .order('sort_order', { ascending: true })
    if (error) throw createError({ statusCode: 500, message: error.message })
    bookCodes = (data ?? []).map((b: any) => b.code)
  }

  const needle = q.toLowerCase()
  const results: {
    book_code: string; chapter: number; verse: number; version_code: string; text: string
  }[] = []
  let total = 0

  for (const code of bookCodes) {
    const doc = bookFilter
      ? await loadBibleBook(code)
      : await loadBibleBookUncached(code) // 全庫掃描不洗閱讀快取
    if (!doc) continue
    for (const [ch, entries] of Object.entries(doc.chapters)) {
      for (const e of entries) {
        for (const [ver, text] of Object.entries(e.t)) {
          if (versionFilter && ver !== versionFilter) continue
          if (!text.toLowerCase().includes(needle)) continue
          total++
          if (results.length < limit) {
            results.push({
              book_code: code, chapter: Number(ch), verse: e.v,
              version_code: ver, text,
            })
          }
        }
      }
    }
  }

  return { q, total, results }
})
