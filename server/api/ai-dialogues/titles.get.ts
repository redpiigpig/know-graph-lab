export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { source = 'all' } = getQuery(event) as { source?: string }

  const tables = source === 'all'
    ? ['ai_dialogues_gemini', 'ai_dialogues_chatgpt']
    : [`ai_dialogues_${source}`]

  // Aggregate counts in memory (PostgREST has no native GROUP BY).
  // Page through 1000-row chunks to bypass PostgREST's row cap.
  const counts = new Map<string, { count: number; sources: Set<string> }>()

  for (const tableName of tables) {
    const tableSource = tableName === 'ai_dialogues_gemini' ? 'gemini' : 'chatgpt'
    let offset = 0
    while (true) {
      const { data, error } = await supabase
        .from(tableName)
        .select('title')
        .not('title', 'is', null)
        .range(offset, offset + 999)

      if (error) {
        // skip table if title column missing (e.g. pre-migration gemini)
        if (/title.*does not exist/i.test(error.message)) break
        throw createError({ statusCode: 500, message: error.message })
      }
      if (!data || data.length === 0) break

      for (const r of data) {
        const t = (r as any).title as string
        if (!t) continue
        const cur = counts.get(t) ?? { count: 0, sources: new Set<string>() }
        cur.count += 1
        cur.sources.add(tableSource)
        counts.set(t, cur)
      }

      if (data.length < 1000) break
      offset += 1000
    }
  }

  const titles = Array.from(counts.entries())
    .map(([title, v]) => ({ title, count: v.count, sources: Array.from(v.sources) }))
    .sort((a, b) => b.count - a.count)

  return { titles }
})
