export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()
  const { source = 'all' } = getQuery(event) as { source?: string }

  const monthMap: Record<string, number> = {}
  const dateMap: Record<string, number> = {}

  // Determine which tables to query
  const tables = source === 'all' ? ['ai_dialogues_gemini', 'ai_dialogues_chatgpt'] : [`ai_dialogues_${source}`]

  // Query the appropriate tables with pagination to bypass 1000 row limit
  for (const tableName of tables) {
    let offset = 0
    let hasMore = true

    while (hasMore) {
      const { data, error } = await supabase
        .from(tableName)
        .select('dialogue_date')
        .range(offset, offset + 999)

      if (error) throw createError({ statusCode: 500, message: error.message })

      if (!data || data.length === 0) {
        hasMore = false
        break
      }

      for (const row of data) {
        const date = row.dialogue_date as string
        const month = date.substring(0, 7) // YYYY-MM
        monthMap[month] = (monthMap[month] ?? 0) + 1
        dateMap[date] = (dateMap[date] ?? 0) + 1
      }

      if (data.length < 1000) {
        hasMore = false
      } else {
        offset += 1000
      }
    }
  }

  return {
    months: Object.entries(monthMap)
      .map(([month, count]) => ({ month, count }))
      .sort((a, b) => b.month.localeCompare(a.month)),
    dates: Object.entries(dateMap)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => b.date.localeCompare(a.date)),
  }
})
