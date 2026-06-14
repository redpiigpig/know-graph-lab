// GET /api/scripture/canon-order  → all per-canon book orderings
// Returns { [canon]: [{ book_code, testament, sort_order, is_deutero, chapter_count }] }
// Canons absent here → index falls back to bible_books.display_order/testament.
export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const { data, error } = await supabase
    .from('bible_canon_books')
    .select('canon, book_code, testament, sort_order, is_deutero, chapter_count, name_override, abbr_override')
    .order('canon', { ascending: true })
    .order('sort_order', { ascending: true })
  if (error) throw createError({ statusCode: 500, message: error.message })

  const byCanon: Record<string, any[]> = {}
  for (const row of (data ?? []) as any[]) {
    ;(byCanon[row.canon] ||= []).push(row)
  }
  return byCanon
})
