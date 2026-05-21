// GET /api/scripture/chapter?book=gen&chapter=1
// Returns { book, chapter, verses: [{ verse, byVersion: { sblgnt: '...', wlc: '...', ... } }] }
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

  const { data: verses, error: verseErr } = await supabase
    .from('bible_verses')
    .select('verse, version_code, text')
    .eq('book_code', bookCode)
    .eq('chapter', chapter)
    .order('verse', { ascending: true })
  if (verseErr) throw createError({ statusCode: 500, message: verseErr.message })

  // Group by verse number → { [verse]: { [version_code]: text } }
  const byVerse = new Map<number, Record<string, string>>()
  for (const row of (verses ?? []) as { verse: number; version_code: string; text: string }[]) {
    if (!byVerse.has(row.verse)) byVerse.set(row.verse, {})
    byVerse.get(row.verse)![row.version_code] = row.text
  }

  const versesOut = Array.from(byVerse.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([verse, byVersion]) => ({ verse, byVersion }))

  return {
    book: bookRow,
    chapter,
    verses: versesOut,
  }
})
