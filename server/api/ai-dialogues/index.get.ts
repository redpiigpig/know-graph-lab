export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { month, date, category, uncategorized, source = 'all', page = '1', limit = '50' } = getQuery(event) as {
    month?: string
    date?: string
    category?: string
    uncategorized?: string
    source?: string
    page?: string
    limit?: string
  }

  const pageNum  = Math.max(1, parseInt(page))
  const limitNum = (month || date) ? 2000 : Math.min(200, parseInt(limit))
  const offset   = (month || date) ? 0 : (pageNum - 1) * limitNum

  // Determine which tables to query
  const tables = source === 'all' ? ['ai_dialogues_gemini', 'ai_dialogues_chatgpt'] : [`ai_dialogues_${source}`]

  // Fetch from each table and combine results
  const allData: any[] = []
  let totalCount = 0

  for (const tableName of tables) {
    const tableSource = tableName === 'ai_dialogues_gemini' ? 'gemini' : 'chatgpt'
    let query = supabase
      .from(tableName)
      .select(`
        id, dialogue_date, dialogue_time, prompt, response
      `, { count: 'exact' })
      .order('dialogue_date', { ascending: false })
      .order('dialogue_time', { ascending: false })

    if (date) {
      query = query.eq('dialogue_date', date)
    } else if (month) {
      query = query.gte('dialogue_date', `${month}-01`).lte('dialogue_date', `${month}-31`)
    }

    if (category) {
      const { data: entryIds } = await supabase
        .from('ai_dialogue_entry_categories')
        .select('dialogue_id')
        .eq('category_id', category)
      const ids = (entryIds ?? []).map((r: any) => r.dialogue_id)
      if (ids.length === 0) {
        // Skip this table if no matching entries
        continue
      }
      query = query.in('id', ids)
    }

    // Note: uncategorized filter will be applied after fetching data (in memory)

    // Only apply range when querying a single table (not combining)
    if (tables.length === 1 && !month && !date) {
      query = query.range(offset, offset + limitNum - 1)
    }

    const { data, error, count } = await query
    if (error) throw createError({ statusCode: 500, message: error.message })

    // Add source field to each entry
    const dataWithSource = (data ?? []).map((item: any) => ({ ...item, source: tableSource, ai_dialogue_entry_categories: [] }))
    allData.push(...dataWithSource)
    totalCount += (count ?? 0)
  }

  // Fetch categories separately for all entries (grouped by source to avoid ID conflicts)
  if (allData.length > 0) {
    const catMap: Record<string, any[]> = {}

    for (const tableSource of ['gemini', 'chatgpt']) {
      const idsForSource = allData
        .filter(e => e.source === tableSource)
        .map(e => e.id)

      if (idsForSource.length === 0) continue

      const { data: catData } = await supabase
        .from('ai_dialogue_entry_categories')
        .select(`
          dialogue_id,
          category_id,
          ai_dialogue_categories(id, name, color)
        `)
        .in('dialogue_id', idsForSource)

      if (catData) {
        for (const cat of catData) {
          const key = `${tableSource}:${cat.dialogue_id}`
          if (!catMap[key]) catMap[key] = []
          catMap[key].push({
            category_id: cat.category_id,
            ai_dialogue_categories: cat.ai_dialogue_categories
          })
        }
      }
    }

    for (const entry of allData) {
      const key = `${entry.source}:${entry.id}`
      entry.ai_dialogue_entry_categories = catMap[key] || []
    }
  }

  // Apply uncategorized filter in memory (if needed)
  let filteredData = allData
  if (uncategorized === '1') {
    const { data: catIds } = await supabase
      .from('ai_dialogue_entry_categories')
      .select('dialogue_id')
    const assigned = new Set((catIds ?? []).map((r: any) => r.dialogue_id))
    filteredData = allData.filter(item => !assigned.has(item.id))
  }

  // Sort combined results by date/time and apply pagination
  filteredData.sort((a, b) => {
    const dateComp = new Date(b.dialogue_date).getTime() - new Date(a.dialogue_date).getTime()
    if (dateComp !== 0) return dateComp
    return b.dialogue_time.localeCompare(a.dialogue_time)
  })

  const paginatedData = (month || date) ? filteredData : filteredData.slice(offset, offset + limitNum)

  return { data: paginatedData, count: totalCount, page: pageNum }
})
