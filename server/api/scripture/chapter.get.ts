// GET /api/scripture/chapter?book=gen&chapter=1
// Returns { book, chapter, verses: [{ verse, byVersion: { sblgnt: '...', wlc: '...', ... } }] }
// 經文本體 2026-07-08 起不在 DB（超量救援）：走 Drive/R2 gz JSON，見 server/utils/bible-verses.ts。
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const bookCode = String(query.book || '').toLowerCase()
  const chapter = Number(query.chapter || 0)
  if (!bookCode || !chapter) {
    throw createError({ statusCode: 400, message: 'book and chapter required' })
  }

  const supabase = getAdminClient()

  const { data: bookRow, error: bookErr } = await supabase
    .from('bible_books')
    .select('*')
    .eq('code', bookCode)
    .maybeSingle()
  if (bookErr) throw createError({ statusCode: 500, message: bookErr.message })
  if (!bookRow) throw createError({ statusCode: 404, message: 'book not found' })

  const doc = await loadBibleBook(bookCode)
  const entries = doc?.chapters?.[String(chapter)] ?? []

  return {
    book: bookRow,
    chapter,
    verses: entries.map((e) => ({ verse: e.v, byVersion: e.t })),
  }
})
