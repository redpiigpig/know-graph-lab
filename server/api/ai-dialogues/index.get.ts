import { buildDialogueKeywordFilter } from '~/server/utils/dialogue-search'

const MAX_MERGED_KEYWORD_RESULTS = 1000

export default defineEventHandler(async (event) => {
  await requireAuth(event)
  const supabase = getAdminClient()

  const { month, date, category, uncategorized, source = 'all', q, page = '1', limit = '50' } = getQuery(event) as {
    month?: string
    date?: string
    category?: string
    uncategorized?: string
    source?: string
    q?: string
    page?: string
    limit?: string
  }

  const parsedPage = Number(page)
  const parsedLimit = Number(limit)
  const pageNum = Number.isInteger(parsedPage) && parsedPage >= 1 ? parsedPage : 1
  const limitNum = (month || date)
    ? 2000
    : Number.isInteger(parsedLimit) && parsedLimit >= 1
      ? Math.min(200, parsedLimit)
      : 50
  const offset   = (month || date) ? 0 : (pageNum - 1) * limitNum

  const keywordInput = String(q ?? '').trim()
  const keywordFilter = buildDialogueKeywordFilter(keywordInput)
  if (keywordInput && !keywordFilter) {
    return { data: [], count: 0, page: pageNum }
  }

  // Keep the source value from becoming part of a dynamic table name.
  const tables = source === 'gemini'
    ? ['ai_dialogues_gemini']
    : source === 'chatgpt'
      ? ['ai_dialogues_chatgpt']
      : ['ai_dialogues_gemini', 'ai_dialogues_chatgpt']

  // Keyword results must exclude categorized rows before range/count are
  // applied; filtering after pagination can produce empty or underfilled pages.
  const assignedIdsForKeywordSearch: string[] = []
  if (keywordFilter && uncategorized === '1') {
    const assigned = new Set<string>()
    let assignedOffset = 0
    while (true) {
      const { data, error } = await supabase
        .from('ai_dialogue_entry_categories')
        .select('dialogue_id')
        .range(assignedOffset, assignedOffset + 999)
      if (error) throw createError({ statusCode: 500, message: error.message })

      for (const row of data ?? []) {
        const id = String(row.dialogue_id ?? '')
        if (/^[\p{L}\p{N}-]+$/u.test(id)) assigned.add(id)
      }
      if (!data || data.length < 1000) break
      assignedOffset += 1000
    }
    assignedIdsForKeywordSearch.push(...assigned)
  }

  // Fetch from each table and combine results
  const allData: any[] = []
  let totalCount = 0

  for (const tableName of tables) {
    const tableSource = tableName === 'ai_dialogues_gemini' ? 'gemini' : 'chatgpt'
    let query = supabase
      .from(tableName)
      .select(`
        id, seq_label, dialogue_date, dialogue_time, prompt, response
      `, { count: 'exact' })
      .order('dialogue_date', { ascending: false })
      .order('dialogue_time', { ascending: false })
      .order('id', { ascending: false })

    if (date) {
      query = query.eq('dialogue_date', date)
    } else if (month) {
      query = query.gte('dialogue_date', `${month}-01`).lte('dialogue_date', `${month}-31`)
    }

    if (keywordFilter) {
      query = query.or(keywordFilter)
    }

    if (assignedIdsForKeywordSearch.length > 0) {
      query = query.not('id', 'in', `(${assignedIdsForKeywordSearch.join(',')})`)
    }

    if (category) {
      // Include child categories so filtering a parent aggregates all its sub-categories
      const { data: children } = await supabase
        .from('ai_dialogue_categories')
        .select('id')
        .eq('parent_id', category)
      const catIds = [category, ...((children ?? []).map((c: any) => c.id))]
      const { data: entryIds } = await supabase
        .from('ai_dialogue_entry_categories')
        .select('dialogue_id')
        .in('category_id', catIds)
      const ids = (entryIds ?? []).map((r: any) => r.dialogue_id)
      if (ids.length === 0) {
        // Skip this table if no matching entries
        continue
      }
      query = query.in('id', ids)
    }

    // Note: uncategorized filter will be applied after fetching data (in memory)

    if (!month && !date) {
      if (keywordFilter) {
        // A single source can page directly. Combined sources need an ordered
        // prefix from each table before their rows can be merged correctly.
        query = tables.length === 1
          ? query.range(offset, offset + limitNum - 1)
          : query.range(0, Math.min(offset + limitNum - 1, MAX_MERGED_KEYWORD_RESULTS - 1))
      } else if (tables.length === 1) {
        query = query.range(offset, offset + limitNum - 1)
      }
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
  if (uncategorized === '1' && !keywordFilter) {
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
    const timeComp = String(b.dialogue_time ?? '').localeCompare(String(a.dialogue_time ?? ''))
    if (timeComp !== 0) return timeComp
    const sourceComp = String(a.source).localeCompare(String(b.source))
    if (sourceComp !== 0) return sourceComp
    return String(b.id).localeCompare(String(a.id))
  })

  const paginatedData = (month || date)
    ? filteredData
    : (keywordFilter && tables.length === 1)
      ? filteredData
      : filteredData.slice(offset, offset + limitNum)

  const mergedSearchIsLimited = Boolean(
    keywordFilter
      && tables.length > 1
      && !month
      && !date
      && totalCount > MAX_MERGED_KEYWORD_RESULTS,
  )
  const resultCount = mergedSearchIsLimited ? MAX_MERGED_KEYWORD_RESULTS : totalCount

  return {
    data: paginatedData,
    count: resultCount,
    totalMatches: totalCount,
    limited: mergedSearchIsLimited,
    page: pageNum,
  }
})
