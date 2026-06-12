// GET /api/scripture/commentary?book=gen&chapter=1
// Returns ACCS patristic commentary for a chapter, grouped into pericopes:
//   { book, chapter, available, pericopes: [
//       { verse_start, verse_end, entries: [
//           { section_kind, heading, father_name, work_title, body_zh }, ... ] }, ... ] }
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const query = getQuery(event)
  const bookCode = String(query.book || '').toLowerCase()
  const chapter = Number(query.chapter || 0)
  if (!bookCode || !chapter) {
    throw createError({ statusCode: 400, message: 'book and chapter required' })
  }

  const supabase = getAdminClient()
  const { data, error } = await supabase
    .from('accs_commentary')
    .select('verse_start, verse_end, pericope_order, entry_order, section_kind, heading, father_name, work_title, body_zh, source_vol')
    .eq('book_code', bookCode)
    .eq('chapter', chapter)
    .order('pericope_order', { ascending: true })
    .order('entry_order', { ascending: true })
  if (error) throw createError({ statusCode: 500, message: error.message })

  type Row = {
    verse_start: number; verse_end: number
    pericope_order: number; entry_order: number
    section_kind: string; heading: string | null
    father_name: string | null; work_title: string | null
    body_zh: string; source_vol: string
  }
  const rows = (data ?? []) as Row[]

  // Group by pericope_order → ordered list of pericopes
  const byPericope = new Map<number, {
    verse_start: number; verse_end: number
    entries: Pick<Row, 'section_kind' | 'heading' | 'father_name' | 'work_title' | 'body_zh'>[]
  }>()
  let sourceVol = ''
  for (const r of rows) {
    sourceVol = sourceVol || r.source_vol
    if (!byPericope.has(r.pericope_order)) {
      byPericope.set(r.pericope_order, {
        verse_start: r.verse_start,
        verse_end: r.verse_end,
        entries: [],
      })
    }
    byPericope.get(r.pericope_order)!.entries.push({
      section_kind: r.section_kind,
      heading: r.heading,
      father_name: r.father_name,
      work_title: r.work_title,
      body_zh: r.body_zh,
    })
  }

  const pericopes = Array.from(byPericope.entries())
    .sort((a, b) => a[0] - b[0])
    .map(([, p]) => p)

  return {
    book: bookCode,
    chapter,
    available: rows.length > 0,
    source_vol: sourceVol,
    pericopes,
  }
})
